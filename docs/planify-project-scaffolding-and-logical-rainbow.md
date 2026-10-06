# pickal — Project Roadmap (high-level work packages)

## Context

[docs/Pic2Calendar.md](docs/Pic2Calendar.md) is a complete Master Design Document for **pickal**, a
personal CLI that extracts calendar events from a timetable/schedule photo using a multimodal LLM and
writes them to a calendar service, built on a Hexagonal (Ports & Adapters) architecture.

The repo currently holds only config scaffolding (the prior source tree was deleted). On disk:
[pyproject.toml](pyproject.toml), [justfile](justfile), [.gitignore](.gitignore),
[.editorconfig](.editorconfig), [.envrc](.envrc), plus the new design doc. The previous source files
(`src/pickal/**`, tests, docs) are tracked-but-deleted and will be recreated fresh.

This document is a **roadmap only**: it breaks the whole build into bounded work packages (WPs) with
clear interfaces between them. Each WP gets its own detailed planning + implementation round later — so
the goal here is correct decomposition and crisp boundaries, not implementation detail.

## Decisions locked in for this roadmap

- **Stack** (from the doc): Python 3.13+, `uv`, `cyclopts` v3, `pydantic` v2 + `pydantic-settings` v2
  (TOML config per ADR-005), `ruff`, `mypy --strict`, `just`, `pytest`. Keep `rich` for table output
  (Cyclopts already pulls it). Build backend stays `hatchling`.
- **Repo branch stays `master`** (the working branch). Doc references to `main` are normalized to `master`.
- **Vision provider default = Google Gemini free tier** (your "best free model for low usage" answer),
  via the `google-genai` SDK. This **supersedes ADR-002** (paid Claude) but *not* the design's intent:
  the `VisionProvider` port (ADR-008) keeps Claude / local Ollama / Groq as drop-in alternatives. Gemini
  free tier gives ~1,500 req/day on Flash, full vision, and native JSON-schema structured output; it also
  unifies the tool under Google (calendar side is already Google). Default model: a current free Flash
  model (e.g. `gemini-2.5-flash`), pinned during WP3's detailed round; configurable via `PICKAL_MODEL`.

## Corrections to the design doc (apply during the relevant WP)

- **Structured outputs is GA** — drop the `betas=["structured-outputs-2025-11-13"]` and `response_model`
  wording from ADR-002. Gemini uses `response_schema` / `response_mime_type="application/json"`.
- **`ExtractedEvent.confidence: float = Field(ge=0, le=1)`** is fine — provider SDKs that constrain output
  schemas strip unsupported numeric bounds and Pydantic validates client-side.
- **Add `all_day: bool`** to `ExtractedEvent` (Gap 3) so the calendar adapter can emit `date` vs `dateTime`.
- Config keys realign to the provider: `PICKAL_GEMINI_API_KEY`, `provider.vision = "gemini"`,
  `provider.calendar = "google"`. The doc's `PICKAL_ANTHROPIC_API_KEY` becomes provider-specific.

## Work packages

The central contract is **WP1 (domain models + ports)** — every adapter and the CLI depend only on those
types, never on each other. That is what lets each WP be planned and built independently.

### WP0 — Repo & tooling baseline (scaffolding)
- **Scope:** Rewrite [pyproject.toml](pyproject.toml) (deps: `cyclopts`, `pydantic-settings[toml]`,
  `rich`, `google-genai`, `google-api-python-client`, `google-auth-oauthlib`, `google-auth-httplib2`,
  `python-dateutil`; drop `pyyaml`; dev: `pytest`, `pytest-cov`, `ruff`, `mypy`; entry point
  `pickal = "pickal.cli:main"`; remove stray `semantic_release`/`pre-commit` blocks). Rewrite
  [justfile](justfile) to the doc's recipe contract (`setup`/`fmt`/`lint`/`test`/`test-unit`/`build`/
  `clean`/`auth-setup`; remove the duplicate `run`). Add `google_credentials.json`/`google_token.json` to
  [.gitignore](.gitignore) and fix `*.lock` so `uv.lock` isn't ignored. Add `.pre-commit-config.yaml`;
  declutter [.envrc](.envrc) (drop Flask/DB cruft). Create the empty `src/pickal/` package tree.
- **Boundary / output:** an installable package + working `just` dev loop (`just lint`/`just test` green
  on an empty skeleton). Everything else is built *inside* this.
- **Depends on:** nothing.

### WP1 — Domain core: models + ports  *(keystone)*
- **Scope:** `core/models.py` (`ExtractedEvent` + `all_day`, `ExtractedEvents`, `CalendarEvent`);
  `ports/vision.py` (`VisionProvider` ABC: `extract(image, media_type, context) -> ExtractedEvents`);
  `ports/calendar.py` (`CalendarProvider` ABC: `create_event`, `list_calendars`); `core/orchestrator.py`
  (`ExtractionOrchestrator` — confidence filtering, `ExtractedEvent → CalendarEvent` mapping incl. tz
  resolution + end-time defaulting, ports injected); `core/errors.py` + exit-code constants (CLI §5).
- **Boundary / output:** the typed contracts (ports + domain models) that all other WPs import. Fully
  unit-tested with fake providers — **no network, no SDKs imported here** (the dependency rule, §4.2).
- **Depends on:** WP0.

### WP2 — Configuration & logging
- **Scope:** `pydantic-settings` `Settings` (TOML file + `PICKAL_*` env + CLI precedence; `SecretStr` for
  API keys; `extra="forbid"`; tz validated against `zoneinfo`; fail-fast at startup). Log-redaction
  `logging.Filter` (§5) and logging setup.
- **Boundary / output:** a validated `Settings` object + configured logging, consumed by the CLI and
  adapters. Independent of any adapter.
- **Depends on:** WP0 (can run in parallel with WP1).

### WP3 — Vision adapter: Gemini (default)
- **Scope:** `adapters/gemini_vision.py` implementing `VisionProvider` via `google-genai`
  (`response_schema=ExtractedEvents`, today's-date + default-tz + confidence-gating injected into the
  prompt per ADR-007). `adapters/registry.py` `VISION_ADAPTERS = {"gemini": ..., "claude": <future>}`.
- **Boundary / output:** satisfies the `VisionProvider` port only. Swappable — a later round can add Claude
  or local-Ollama adapters without touching core/CLI. Integration test gated behind `PICKAL_GEMINI_API_KEY`.
- **Depends on:** WP1 (+ WP2 for config).

### WP4 — Calendar adapter: Google Calendar + auth
- **Scope:** `adapters/google_calendar.py` implementing `CalendarProvider` via `google-api-python-client`;
  OAuth2 InstalledApp flow (ADR-006), token at `~/.config/pickal/google_token.json` with `chmod 600`,
  refresh-error handling (→ exit 3), `create_event` (all-day `date` vs timed `dateTime`, tz), credential
  permission check. `CALENDAR_ADAPTERS = {"google": ...}`.
- **Boundary / output:** satisfies the `CalendarProvider` port + provides the auth flow used by the `auth`
  command. The one area only smoke-testable without your real OAuth credentials. Integration test gated
  behind a stored token.
- **Depends on:** WP1, WP2.

### WP5 — CLI composition (import / auth / calendars)
- **Scope:** `cli.py` (`cyclopts` App + `main()`) and `__main__.py`. Global options (`-v/-q/--json/--config`),
  the three commands, the composition root (build `Settings`, resolve adapters via registries, inject into
  `ExtractionOrchestrator`), image validation (size/format → exit 2), output rendering (rich table in human
  mode, strict JSON when `--json`/piped, stdout=data / stderr=logs), and exception→exit-code mapping
  (Gap 2 + §5).
- **Boundary / output:** the top-level wiring; end-to-end runnable (`pickal import … --dry-run` works once
  WP3 lands). Depends on every prior WP only through their public interfaces.
- **Depends on:** WP1–WP4.

### WP6 — Distribution & CI
- **Scope:** bootstrap shim `bin/pickal`, `just build`/`dist` (wheel + `requirements.lock` export + tarball),
  `.github/workflows` (lint + `test-unit` on PR), README + first-run OAuth/Gemini-key setup docs.
- **Boundary / output:** packaging around a finished app; no app-logic changes.
- **Depends on:** WP5.

## Ordering & dependencies

```
WP0 ──▶ WP1 ──┬──▶ WP3 ─┐
        │     ├──▶ WP4 ─┼──▶ WP5 ──▶ WP6
WP0 ──▶ WP2 ──┘         ┘
```
Critical path: **WP0 → WP1 → (WP3 ‖ WP4) → WP5 → WP6**. WP2 parallels WP1. A first runnable slice
(`import --dry-run`, vision only) is reachable after WP0→WP1→WP2→WP3→WP5, before WP4.

## Verification (per WP, detailed in each round)

- WP0: `just lint && just test` green on the empty skeleton; `uv sync` resolves.
- WP1: `pytest tests/unit` covering orchestrator filtering/mapping with fake ports (no network).
- WP2: unit tests for precedence, `extra="forbid"`, tz validation, and secret redaction.
- WP3: unit test prompt assembly with a stubbed client; opt-in integration test with `PICKAL_GEMINI_API_KEY`
  against a sample timetable image.
- WP4: unit test event-payload mapping with a stubbed Google client; opt-in integration test with a token.
- WP5: `pickal import sample.jpg --dry-run [--json]` end-to-end; exit-code assertions per scenario.
- WP6: build the tarball, install the shim into a clean dir, run `pickal --help`.

## Next step

Per your instruction, this stays high-level. The next round picks one work package (recommended start:
**WP0 then WP1**) and produces its detailed implementation plan + code.
