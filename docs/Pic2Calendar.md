# Master Design Document: pickal

**Version:** 1.0 | **Date:** 2026-06-28 | **Status:** Draft

---

## Preamble

**pickal** is a personal-use CLI tool that accepts a timetable or schedule photograph and autonomously extracts structured events — titles, dates, times, and locations — from it using a multimodal LLM, then creates those events in the user's calendar service.

The system is designed around a **Ports & Adapters (Hexagonal)** architecture so that: (a) the calendar backend (Google Calendar, CalDAV, Microsoft Graph, etc.) and (b) the vision AI provider (Claude, GPT-4o Vision, Gemini Vision, etc.) are both interchangeable without touching domain logic.

### Selected Atoms

| Atom | Rationale |
| :---- | :---- |
| Core Architecture & Patterns | Multi-component system with external I/O on both ends |
| Configuration Management | Multiple secrets \+ user-tunable parameters |
| CLI Spec | Primary interface; no GUI or API surface required |
| DX & Repository Structure | Standard modern Python project |
| Distribution & Runtime Provisioning | Single-user portable CLI tool, no root required |

### Pending Atoms / Known Gaps

The following atoms are not yet available in the portfolio. Critical design decisions for each are recorded in the Gap Register below, but full specs are deferred.

| Gap | Scope Impact | Interim Mitigation in This MDD |
| :---- | :---- | :---- |
| **Security & Auth** | OAuth2 token lifecycle, credential file permissions | ADR-006 \+ Config §5 |
| **Error Handling & Recovery** | API failures, extraction failures, partial results | Architecture §4.2, Exit codes §CLI-5 |
| **Data Model & Persistence** | Event schema, normalization pipeline, no DB needed | Core Models §Architecture-7 |
| **API Surface** | Not applicable — CLI-only tool | Excluded by design |

---

## ADR Log (Cross-Cutting Decisions)

| ID | Date | Decision Title | Status | Context & Consequence |
| :---- | :---- | :---- | :---- | :---- |
| ADR-001 | 2026-06-28 | Runtime: Python 3.13+ | Accepted | **Context:** Language choice propagates to all atoms. **Decision:** Python 3.13+. **Why:** Free-threaded mode (PEP 703, GA in 3.13), improved `typing` with `PEP 696` defaults, `uv` toolchain maturity. Rejected Go — insufficient LLM SDK ecosystem. Rejected Rust — over-engineered for a personal automation CLI. |
| ADR-002 | 2026-06-28 | Vision AI: Anthropic Claude Vision \+ Native Structured Outputs | Accepted | **Context:** Images arrive in arbitrary languages and layouts. OCR+NLP pipeline (Tesseract \+ spaCy) requires layout understanding that rule-based approaches cannot generalize. **Decision:** Anthropic `claude-sonnet-4-6` via `client.messages.parse()` with `betas=["structured-outputs-2025-11-13"]` and a Pydantic `response_model`. **Why:** Constrained decoding guarantees schema compliance on the first call — eliminates retry logic. Native multilingual and multi-layout understanding removes the need for OCR preprocessing. Vision is a core language-reasoning capability in Claude, not bolted-on. Alternatives rejected: (1) Tesseract+spaCy — cannot handle arbitrary layouts or multilingual documents without per-language fine-tuning; (2) GPT-4o Vision — viable alternative but requires separate SDK, no meaningful quality delta for this task on Claude Sonnet. The `VisionProvider` port makes provider substitution trivial if needed. |
| ADR-003 | 2026-06-28 | Architectural Pattern: Hexagonal / Ports & Adapters | Accepted | **Context:** Must support multiple calendar backends (now: Google, future: CalDAV, Outlook) and potentially multiple vision providers. **Decision:** Hexagonal architecture with abstract `VisionProvider` and `CalendarProvider` ports; adapters implement them. Domain core holds no references to any specific API SDK. **Why:** Direct import of `google-api-python-client` into orchestration logic would make adding a second backend require forking. Hexagonal enforces the boundary at the type-system level. |
| ADR-004 | 2026-06-28 | CLI Framework: Cyclopts | Accepted | **Context:** CLI framework choice propagates to argument parsing, help generation, and type coercion. Typer (established, 2019-era API), Click (foundational, imperative), argparse (stdlib, verbose). **Decision:** Cyclopts v3.x. **Why:** Native Pydantic model support for argument groups (no proxy defaults), docstring-driven help, Union/Literal type support, 38% less boilerplate vs Typer on equivalent CLIs. Actively maintained with 3.x in 2025\. The project already depends on Pydantic for domain models; Cyclopts shares that dependency with zero friction. Rejected Typer — proxy-default API is a known ergonomics regression vs. modern Python typing. Rejected argparse — verbosity and lack of type integration are not justified for a new project. |
| ADR-005 | 2026-06-28 | Config Library: Pydantic Settings v2 | Accepted | **Context:** Multiple config sources (env vars, TOML file, CLI flags). **Decision:** `pydantic-settings` v2 with `BaseSettings`. **Why:** Single library covers env var parsing, TOML loading (via `pydantic-settings[toml]`), type coercion, and validation. Integrates directly with existing Pydantic domain models. No additional dependency vs. plain `pydantic`. Rejected Dynaconf — heavier, no Pydantic-native integration. Rejected python-dotenv alone — no type validation. |
| ADR-006 | 2026-06-28 | Google Calendar Auth: OAuth2 InstalledApp Flow | Accepted | **Context:** Personal-use tool accessing the user's own Google Calendar. Service account requires Workspace domain. **Decision:** `google-auth-oauthlib` InstalledApp flow with offline access. Refresh token stored in `~/.config/pickal/google_token.json` (permissions: 600). **Why:** Personal accounts cannot use service accounts without Workspace. InstalledApp with refresh token provides a one-time browser login, then headless operation. Token file permissions enforced at write time. Rejected service account — not applicable to personal Gmail accounts. |
| ADR-007 | 2026-06-28 | Date Normalization: LLM-Direct ISO 8601 with Today-Context Injection | Accepted | **Context:** Input images contain dates in arbitrary formats and languages ("lunes 3 julio", "3rd July", "07/03", "下午三点"). Post-processing with `dateutil` cannot handle ambiguous relative references. **Decision:** Prompt Claude to output all dates as ISO 8601 (`YYYY-MM-DDThh:mm:ssZ`) with the current date (`today`) injected into the system prompt. Claude resolves "next Monday", "mañana", etc. relative to the injected date. **Why:** Centralizes all parsing intelligence in the same LLM call that extracts the events. Avoids a second normalization pass. Confidence field in the schema gates uncertain dates for human review before calendar write. Rejected dateutil post-processing — cannot resolve language-dependent relative references. |
| ADR-008 | 2026-06-28 | Extensibility Contract: Typed ABCs as Provider Ports | Accepted | **Context:** Architecture must support future calendar backends without core changes. **Decision:** `VisionProvider(ABC)` and `CalendarProvider(ABC)` in `src/pickal/ports/`. Each adapter is a concrete class in `src/pickal/adapters/`. Provider selection at runtime via config key `provider.calendar = "google"`. **Why:** Python's `abc.ABC` \+ `@abstractmethod` enforces the contract at import time. A registry dict maps string keys to adapter classes, allowing zero-friction addition of new adapters. |

---

## Core Architecture & Patterns

**Status:** DRAFT | **Date:** 2026-06-28 | **System:** pickal

### 1\. System Context (Level 1\)

- **Primary Actor:** User (invokes `pickal` CLI with a local image path)  
- **External Dependencies:**  
  - **Anthropic API** (`api.anthropic.com`): Vision inference \+ structured output extraction  
  - **Google Calendar API v3** (`googleapis.com/calendar/v3`): Event creation; authenticated via OAuth2

**Context Description:**  
The user provides a timetable image to `pickal`. The system sends the image to the Anthropic Claude Vision API and receives a structured list of calendar events (`ExtractedEvent[]`). Events passing the confidence threshold are written to the configured Google Calendar via the Google Calendar API. Events below threshold are surfaced on stdout for user review.

### 2\. Container/Component Architecture (Level 2\)

| Component | Responsibility | Deployment Unit |
| :---- | :---- | :---- |
| **CLI Layer** | Parse arguments, load config, invoke orchestrator, render output | `pickal` binary (Cyclopts) |
| **Core Domain** | `ExtractionOrchestrator` coordinates vision extraction and calendar write; pure business logic with no external SDK imports | Python module `pickal.core` |
| **Vision Port \+ ClaudeVisionAdapter** | Abstract `VisionProvider` port; concrete `ClaudeVisionAdapter` calls Anthropic API | Python module `pickal.adapters.claude_vision` |
| **Calendar Port \+ GoogleCalendarAdapter** | Abstract `CalendarProvider` port; concrete `GoogleCalendarAdapter` calls Google API | Python module `pickal.adapters.google_calendar` |
| **Config Layer** | Loads and validates all configuration; validates secrets at startup | `pydantic-settings` `Settings` singleton |

**Communication Strategy:**

- **Internal:** Direct synchronous function calls. No event bus. Dependency injection: adapters are instantiated in `cli.py` and passed into `ExtractionOrchestrator.__init__()`. The domain core never imports from `adapters` or `infrastructure`.  
- **External:** HTTPS REST over `httpx` (Anthropic SDK) and `googleapiclient` (Google SDK).

### 3\. Technology Selection & Trend Analysis

#### 3.1. SOTA Check

- **Vision AI:** As of 2026-Q2, multimodal LLMs with structured output (constrained decoding) are the dominant approach for document information extraction from arbitrary images. Rule-based OCR \+ NLP pipelines are relegated to high-volume, fixed-layout use cases. References: [Virtido, April 2026](https://virtido.com/blog/document-intelligence-llm-extraction-guide), [Anthropic Structured Outputs GA](https://platform.claude.com/docs/en/build-with-claude/structured-outputs).  
- **Python CLI framework:** Cyclopts v3 (2025) has emerged as a cleaner alternative to Typer, with native Pydantic support and superior type hint handling. Reference: [Cyclopts docs](https://cyclopts.readthedocs.io/en/latest/vs_typer/README.html).  
- **Config:** Pydantic Settings v2 is the current community standard for typed multi-source config in Python.

#### 3.2. Selected Stack

| Concern | Selected | Version | Justification |
| :---- | :---- | :---- | :---- |
| Language | Python | 3.13+ | Free-threaded mode, mature `uv` toolchain, LLM SDK ecosystem |
| Vision AI | `anthropic` SDK | latest | Claude Vision \+ `messages.parse()` structured outputs |
| Structured output contract | `pydantic` | v2 | `response_model` for extraction; `BaseSettings` for config |
| CLI | `cyclopts` | v3.x | Native Pydantic, docstring-driven help, clean type-hint API |
| Google Calendar | `google-api-python-client`, `google-auth-oauthlib` | latest | Official Google SDK; no viable alternative |
| Date/time | `python-dateutil`, `zoneinfo` (stdlib) | \- | Fallback parsing; `zoneinfo` replaces `pytz` as of Python 3.9 |
| HTTP | Anthropic SDK wraps `httpx`; Google SDK wraps `httplib2` | \- | Managed by respective SDKs |

### 4\. Key Architectural Patterns

#### 4.1. Architectural Style

- **Selected Style:** Hexagonal (Ports & Adapters)  
- **Rationale:** Two external systems (vision AI, calendar backend) must be independently swappable without modifying core orchestration logic. Hexagonal enforces this at the type level via ABCs.

#### 4.2. Data Flow & Constraints

\[Image bytes\] → ClaudeVisionAdapter.extract(image) → \[ExtractedEvent\[\]\]

    → ExtractionOrchestrator.filter(confidence\_threshold) → \[CalendarEvent\[\]\]

    → GoogleCalendarAdapter.create\_event(calendar\_id, event) → \[EventId\[\]\]

    → CLI renders result table or JSON

**Dependency Rule:** `core/` MUST NOT import from `adapters/` or the Anthropic/Google SDKs. Domain models (`ExtractedEvent`, `CalendarEvent`) live in `core/models.py`. Adapters translate between domain models and SDK-specific types.

#### 4.3. Domain Models (Data Model Gap Mitigation)

\# src/pickal/core/models.py

from pydantic import BaseModel, Field

from datetime import datetime

from typing import Optional

class ExtractedEvent(BaseModel):

    """Output of VisionProvider.extract(). All dates as ISO 8601."""

    title: str

    start: datetime                      \# ISO 8601, tz-aware if possible

    end: Optional\[datetime\] \= None       \# None → single-point event, end \= start \+ 1h

    location: Optional\[str\] \= None

    description: Optional\[str\] \= None

    confidence: float \= Field(ge=0.0, le=1.0)

class ExtractedEvents(BaseModel):

    """Root structured-output schema sent to Claude."""

    events: list\[ExtractedEvent\]

    notes: Optional\[str\] \= None         \# Claude's remarks (e.g., "date year ambiguous")

class CalendarEvent(BaseModel):

    """Canonical event as submitted to any CalendarProvider."""

    title: str

    start: datetime

    end: datetime

    location: Optional\[str\] \= None

    description: Optional\[str\] \= None

    timezone: str                        \# IANA tz name, e.g. "Europe/Madrid"

### 5\. Operational Characteristics

- **Concurrency Model:** Single-threaded synchronous. Volume is 1–N images per invocation; no concurrency primitive justified. Async would add complexity without benefit.  
- **State Management:** Stateless between invocations. The only persistent state is the OAuth2 `google_token.json` refresh token, managed outside the domain core.  
- **Scalability Strategy:** Not applicable — personal-use tool. If batch processing of many images becomes a use case, a future `--batch` flag with `asyncio` gather can be added without architectural change.

### 6\. Provider Extensibility Registry

Future calendar providers (CalDAV, Microsoft Graph) are registered in `src/pickal/adapters/registry.py`:

from pickal.ports.calendar import CalendarProvider

from pickal.adapters.google\_calendar import GoogleCalendarAdapter

CALENDAR\_ADAPTERS: dict\[str, type\[CalendarProvider\]\] \= {

    "google": GoogleCalendarAdapter,

    \# "caldav": CalDAVAdapter,       \# future

    \# "outlook": OutlookAdapter,     \# future

}

VISION\_ADAPTERS: dict\[str, type\] \= {

    "claude": None,   \# import-resolved at runtime to avoid circular deps

}

### 7\. Code Organization Blueprint

pickal/

├── src/

│   └── pickal/

│       ├── \_\_init\_\_.py

│       ├── cli.py                  \# Cyclopts entrypoint; instantiates adapters \+ orchestrator

│       ├── core/

│       │   ├── \_\_init\_\_.py

│       │   ├── models.py           \# ExtractedEvent, CalendarEvent, ExtractedEvents

│       │   └── orchestrator.py     \# ExtractionOrchestrator (pure domain logic)

│       ├── ports/

│       │   ├── \_\_init\_\_.py

│       │   ├── vision.py           \# VisionProvider ABC

│       │   └── calendar.py         \# CalendarProvider ABC

│       └── adapters/

│           ├── \_\_init\_\_.py

│           ├── registry.py         \# CALENDAR\_ADAPTERS, VISION\_ADAPTERS dicts

│           ├── claude\_vision.py    \# ClaudeVisionAdapter

│           └── google\_calendar.py  \# GoogleCalendarAdapter

├── tests/

│   ├── unit/

│   │   ├── test\_models.py

│   │   └── test\_orchestrator.py

│   └── integration/

│       ├── test\_claude\_vision.py   \# Requires ANTHROPIC\_API\_KEY

│       └── test\_google\_calendar.py \# Requires GOOGLE\_TOKEN

├── docs/

│   └── architecture.md

├── pyproject.toml

├── Justfile

├── .editorconfig

└── .pre-commit-config.yaml

---

## Configuration Management

**Status:** DRAFT | **Date:** 2026-06-28 | **System:** pickal

### 1\. Philosophy & Precedence Strategy

- **Strategy:** Hierarchical Merge (12-Factor compliant)  
- **Precedence Order (Highest to Lowest):**  
  1. CLI Flags (e.g., `--provider google`, `--calendar primary`)  
  2. Environment Variables (`PICKAL_*`)  
  3. User Config File (`~/.config/pickal/config.toml`)  
  4. Base defaults (encoded in `Settings` model defaults)  
- **Strict Policy:** No hardcoded values in domain logic. All defaults live in `Settings`.

### 2\. Technology Selection

- **Library:** `pydantic-settings` v2 with `BaseSettings`  
- **File Format:** TOML (via `pydantic-settings[toml]`)  
- **Justification:** Pydantic Settings v2 is SOTA for typed multi-source config in Python 2025\. Shares Pydantic v2 dependency already required for domain models and structured outputs. TOML preferred over YAML: simpler type system, less ambiguous parsing (e.g., no implicit string-to-bool conversion).

### 3\. Environment Variables Specification

- **Global Prefix:** `PICKAL_`  
- **Separator:** `__` for nested (e.g., `PICKAL_GOOGLE__TOKEN_PATH`)

#### Critical Variables Table

| Variable | Maps To | Required? | Default | Description |
| :---- | :---- | :---- | :---- | :---- |
| `PICKAL_ANTHROPIC_API_KEY` | `settings.anthropic.api_key` | Yes | — | Anthropic API key |
| `PICKAL_GOOGLE__CREDENTIALS_PATH` | `settings.google.credentials_path` | Yes (Google provider) | `~/.config/pickal/google_credentials.json` | OAuth2 client credentials file |
| `PICKAL_GOOGLE__TOKEN_PATH` | `settings.google.token_path` | No | `~/.config/pickal/google_token.json` | Stored OAuth2 refresh token |
| `PICKAL_DEFAULT_CALENDAR_ID` | `settings.default_calendar_id` | No | `primary` | Target Google Calendar ID |
| `PICKAL_MODEL` | `settings.model` | No | `claude-sonnet-4-6` | Anthropic model identifier |
| `PICKAL_CONFIDENCE_THRESHOLD` | `settings.confidence_threshold` | No | `0.75` | Min extraction confidence to auto-create event |
| `PICKAL_PROVIDER` | `settings.provider` | No | `google` | Calendar adapter key (registry lookup) |
| `PICKAL_LOG_LEVEL` | `settings.log_level` | No | `WARNING` | Verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |

### 4\. Configuration Files & Discovery

- **Standard:** XDG Base Directory Specification  
- **Loading Strategy:** Pydantic Settings merges env vars over file values at instantiation  
- **Discovery Paths:**  
  1. **Base (Mandatory):** `Settings` class defaults  
  2. **User (Optional):** `~/.config/pickal/config.toml`  
  3. **Dev (Optional):** `.env` in CWD (enabled only in dev mode, never in dist artifact)

#### Configuration Structure (Schema)

\# \~/.config/pickal/config.toml

\[anthropic\]

model \= "claude-sonnet-4-6"

\[google\]

credentials\_path \= "\~/.config/pickal/google\_credentials.json"

token\_path \= "\~/.config/pickal/google\_token.json"

default\_calendar\_id \= "primary"

\[extraction\]

confidence\_threshold \= 0.75

timezone \= "Europe/Madrid"    \# IANA tz; used for events with no explicit tz

### 5\. Secrets Management

- **Storage Policy:** `PICKAL_ANTHROPIC_API_KEY` never written to disk by the application. Must be injected via env var or exported in shell profile. `google_token.json` is written by `google-auth-oauthlib` after first auth. The app enforces `chmod 600` on write.  
- **Injection Method:** Environment variables only for API keys. Refresh token via file (standard OAuth2 pattern for installed apps).  
- **Leaking Prevention:** `pydantic-settings` `SecretStr` type for `api_key`; `.get_secret_value()` is called only at the Anthropic SDK call site. Log redaction: any log record containing the substrings `api_key`, `token`, or `credentials` is intercepted by a custom `logging.Filter` that replaces values with `***REDACTED***`.

### 6\. Validation & Fail-Fast Policy

- **Validation Time:** Startup (import of `Settings` singleton in `cli.py`)  
- **Schema Enforcement:** Strict Pydantic types. `api_key: SecretStr` (non-empty), `confidence_threshold: float` (0.0–1.0), `model: str` (non-empty), `timezone: str` (validated against `zoneinfo.available_timezones()`).  
- **Unknown Keys Policy:** `model_config = SettingsConfigDict(extra="forbid")` — unknown keys raise `ValidationError` at startup with a clear message identifying the offending key.

---

## CLI Specification

**Status:** DRAFT | **Date:** 2026-06-28 | **System:** pickal

### 1\. Invocation & Philosophy

- **Binary Name:** `pickal`  
- **Invocation Pattern:** `pickal [GLOBAL_OPTIONS] COMMAND [ARGS] [OPTIONS]`  
- **Interpreter:** Python 3.13+ (via bootstrap shim)  
- **Standard:** POSIX / GNU

#### Core Principles

1. **Silence is Golden:** Successful execution outputs only the event summary table.  
2. **Dry Run:** `import` command supports `--dry-run`. Events are extracted and displayed but not written to calendar.  
3. **Machine Readable:** `--json` flag emits strict JSON on stdout.

### 2\. Global Options

| Short | Long | Type | Default | Description |
| :---- | :---- | :---- | :---- | :---- |
| `-h` | `--help` | Bool | False | Show help and exit 0 |
| `-v` | `--verbose` | Count | 0 | Increase log verbosity (`-v`\=INFO, `-vv`\=DEBUG) |
| `-q` | `--quiet` | Bool | False | Suppress stdout; only stderr |
|  | `--json` | Bool | False | Force JSON output on stdout |
|  | `--config` | Path | `~/.config/pickal/config.toml` | Path to config file |

### 3\. Command Hierarchy

#### 3.1. Command: `import`

**Purpose:** Extract events from an image and create them in the configured calendar.

| Position | Name | Required | Type | Description |
| :---- | :---- | :---- | :---- | :---- |
| 1 | `image` | Yes | Path | Local path to image file (JPEG/PNG/WebP/GIF; max 20 MB) |

| Flag | Description | Default |
| :---- | :---- | :---- |
| `--provider` | Calendar adapter key (`google`, etc.) | `google` |
| `--calendar` | Target calendar ID | `primary` |
| `--dry-run` | Extract events, print, do not write to calendar | False |
| `--force` | Create all events including those below confidence threshold | False |
| `--timezone` | Override default IANA timezone for events missing tz info | Config value |

\# Dry-run extraction of a timetable photo

pickal import ./timetable.jpg \--dry-run

\# Extract and create events, targeting a specific calendar

pickal import ./schedule.png \--calendar "work@example.com" \--provider google

\# Machine-readable output

pickal import ./program.jpg \--json | jq '.events\[\] | select(.created \== true)'

**Output (human mode — stdout):**

Extracted 4 events (3 above confidence threshold 0.75):

  STATUS  TITLE                      START                  END                    LOCATION

  \------  \-------------------------  \---------------------  \---------------------  \--------

  \[OK\]    Team standup               2026-07-02 09:00 CEST  2026-07-02 09:30 CEST  Room A

  \[OK\]    Sprint review              2026-07-02 14:00 CEST  2026-07-02 15:00 CEST  \-

  \[OK\]    1:1 with manager           2026-07-03 10:00 CEST  2026-07-03 10:30 CEST  \-

  \[SKIP\]  "July training" (conf=0.6) 2026-07-?? ??:??       \-                      \-

3 events created. 1 skipped (confidence \< 0.75). Use \--force to create skipped events.

**Output (JSON mode — stdout):**

{

  "events": \[

    {

      "title": "Team standup",

      "start": "2026-07-02T09:00:00+02:00",

      "end": "2026-07-02T09:30:00+02:00",

      "location": "Room A",

      "confidence": 0.92,

      "created": true,

      "event\_id": "abc123xyz"

    }

  \],

  "summary": { "total": 4, "created": 3, "skipped": 1 }

}

#### 3.2. Command: `auth`

**Purpose:** Perform interactive OAuth2 authorization for a calendar provider. Opens browser.

| Flag | Description | Default |
| :---- | :---- | :---- |
| `--provider` | Calendar adapter key | `google` |
| `--revoke` | Revoke stored token and remove token file | False |

\# First-time setup (opens browser)

pickal auth \--provider google

\# Revoke and re-authorize

pickal auth \--provider google \--revoke

#### 3.3. Command: `calendars`

**Purpose:** List available calendars for the configured provider.

pickal calendars

pickal calendars \--provider google \--json

### 4\. I/O Specifications

#### 4.1. Standard Output (stdout)

- **Human Mode (TTY detected):** ASCII table, ANSI colors (Green=created, Yellow=skipped, Red=error). Progress spinner for operations \>1s (suppressed if not TTY).  
- **Machine Mode (`--json` or piped):** Strict JSON, no preamble. Schema: `{"events": [...], "summary": {...}}`.

#### 4.2. Standard Error (stderr)

All logs, warnings, errors, and spinner output go to stderr. stdout is strictly for event data. Enables clean piping: `pickal import img.jpg --json | jq .events`.

### 5\. Exit Codes

| Code | Constant | Meaning |
| :---- | :---- | :---- |
| 0 | `EXIT_SUCCESS` | All events created successfully (or dry-run complete) |
| 1 | `EXIT_FAILURE` | Generic runtime error (API failure, network error) |
| 2 | `EXIT_USAGE` | Bad arguments or invalid flags |
| 3 | `EXIT_AUTH` | Auth token missing or expired; run `pickal auth` |
| 4 | `EXIT_EXTRACTION_EMPTY` | No events extracted from image |
| 5 | `EXIT_ALL_SKIPPED` | All extracted events below confidence threshold |
| 130 | `EXIT_SIGINT` | Ctrl+C |

### 6\. Environment Variables (CLI Override)

| Env Variable | Mapping | Description |
| :---- | :---- | :---- |
| `PICKAL_ANTHROPIC_API_KEY` | Loaded via Settings | Anthropic API key |
| `PICKAL_DEBUG` | `-vv` verbose flag | Set to `1` for debug logs |
| `PICKAL_NO_COLOR` | Disables ANSI | Honor the [no-color.org](https://no-color.org/) standard |

---

## Developer Experience & Repository Structure

**Status:** DRAFT | **Date:** 2026-06-28 | **System:** pickal

### 1\. DX Philosophy & Onboarding

- **Time-to-First-Run:** Clone \+ `just setup` \+ `just test` in under 3 minutes on a machine with `uv` installed.  
- **Single Source of Truth:** All build/lint/test commands live in `Justfile`. CI and git hooks call the same `just` recipes as the developer.  
- **Local-CI Symmetry:** `.pre-commit-config.yaml` and CI pipeline both invoke `just lint` and `just test`. No hidden logic.

### 2\. Technology Selection

#### 2.1. SOTA Check

- **Command Runner:** `just` v1.x is SOTA for cross-platform shell-agnostic task runners in Python projects. GNU Make is designed for C compilation; its tab-whitespace rules and implicit targets are error-prone in Python contexts.  
- **Formatter/Linter:** `ruff` v0.6+ consolidates `black`, `flake8`, `isort`, and more into a single Rust-speed binary. No credible challenger as of 2026\.  
- **Dependency Manager:** `uv` v0.4+ is the current community standard for Python dependency management, replacing `pip + venv + pip-tools` entirely. Faster than `poetry` with better lock file semantics.  
- **Config Centralization:** `pyproject.toml` is the unambiguous standard (`PEP 517/518/621`). Fragmented dotfiles (`.flake8`, `pytest.ini`, `setup.cfg`) are deprecated.

#### 2.2. Selected Stack

| Tool | Selected | Justification |
| :---- | :---- | :---- |
| Project Scaffolding | `copier` | Template-based, re-sync support |
| Command Runner | `just` | Shell-agnostic, documented, SOTA for Python 2025 |
| Dependency & Env Manager | `uv` | Fastest Python dep manager, lock-file native |
| Git Hook Manager | `pre-commit` | Ecosystem standard; Cyclopts-/ruff-aware hooks available |
| Central Config Hub | `pyproject.toml` | PEP 621; `ruff`, `pytest`, `mypy` all read from it |
| Type Checker | `mypy` (strict mode) | Required given the ABC-heavy port/adapter pattern |

### 3\. Justfile Contract

| Recipe | Responsibility | Behavior |
| :---- | :---- | :---- |
| `just setup` | Environment provision | `uv venv`, `uv sync`, `pre-commit install` |
| `just fmt` | Format code | `ruff format .` \+ `taplo fmt pyproject.toml` |
| `just lint` | Static analysis | `ruff check .` \+ `mypy src/` — exits \>0 on failure |
| `just test` | Unit \+ integration tests | `pytest tests/unit/` (no network); `pytest tests/integration/` with markers |
| `just test-unit` | Unit tests only | `pytest tests/unit/ -x` |
| `just build` | Artifact generation | `uv build` → `dist/pickal-*.whl` |
| `just clean` | Workspace reset | Removes `.venv`, `dist/`, `__pycache__/`, `.pytest_cache/` |
| `just auth-setup` | Google OAuth first-run | `pickal auth --provider google` via installed shim |

### 4\. Code Quality & Configuration Centralization

#### 4.1. Zero-Clutter Policy

All tool configuration in `pyproject.toml` under `[tool.<name>]`. Forbidden: `.ruff.toml`, `pytest.ini`, `setup.cfg`, `mypy.ini`. Exception: `.pre-commit-config.yaml` and `.editorconfig` at root (neither supports `pyproject.toml` as config source).

#### 4.2. Universal Formatting

- **Python:** `ruff format` \+ `ruff check --fix`  
- **TOML:** `taplo fmt`  
- **Markdown:** `prettier`  
- **Shell/Bash:** `shfmt` (bootstrap shim)  
- **Enforcement:** All via `pre-commit` hooks calling `just lint` / `just fmt`

### 5\. Version Control & CI/CD DX

- **Commit Semantics:** Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`). Enforced via `commitlint` in `commit-msg` pre-commit hook.  
- **Branching Strategy:** Trunk-based development. `main` is always release-ready. Features on short-lived branches, PRs via GitHub/GitLab.  
- **CI Requirements:** `just lint` \+ `just test-unit` on every PR. `just test` (integration) on merge to main if secrets available.  
- **mypy Strict Mode:** `--strict` flag required. The port/adapter boundary is only as strong as the type checker enforces it.

---

## Distribution & Runtime Provisioning

**Status:** DRAFT | **Date:** 2026-06-28 | **System:** pickal

### 1\. Distribution Philosophy

- **The Artifact:** `pickal-linux-x64.tar.gz` — a self-contained directory extractable anywhere.  
- **Content Constraints:** No `pyproject.toml`, no source tree, no dev configs in artifact. Contains: bootstrap shim \+ `.whl` \+ `requirements.lock`.  
- **Zero-Assumption:** Runs on bare Linux with only `bash`, `curl`, `tar`. Python is bootstrapped by the shim via `uv` if not present.

### 2\. Technology Selection

- **Build Tool:** `uv build` (produces PEP 517 wheel)  
- **Dependency Lock:** `uv export --frozen > requirements.lock` (platform-locked for Linux x64)  
- **Runtime Bootstrap:** Bash shim (lazy initialization)  
- **Distribution Format:** Portable tarball

**Rejected alternatives:**

- `shiv/pex` ZipApps: require pre-installed Python at target; not zero-assumption.  
- `.deb` package: requires root for system-wide install; over-engineered for personal tool.  
- Docker image: heavy overhead for a personal CLI; contradicts zero-assumption on bare system.

### 3\. Build Process (Artifact Generation)

just build

Executes:

1. `uv build` → `dist/pickal-x.y.z-py3-none-any.whl`  
2. `uv export --frozen --no-dev > dist/pickal/conf/requirements.lock`  
3. Assemble:  
     
   dist/pickal/  
     
   ├── bin/  
     
   │   └── pickal          \# Bash bootstrap shim (executable)  
     
   ├── lib/  
     
   │   └── pickal-x.y.z-py3-none-any.whl  
     
   └── conf/  
     
       └── requirements.lock  
     
4. `tar -czf pickal-linux-x64.tar.gz dist/pickal/`

### 4\. Installation Experience

tar \-xzf pickal-linux-x64.tar.gz

ln \-s "$(pwd)/pickal/bin/pickal" \~/.local/bin/pickal

pickal \--help

On first run if shim detects it is not in `$PATH`, it prompts:

pickal is not in your PATH. Add symlink to \~/.local/bin? \[y/N\]

### 5\. Bootstrap Shim Specification

**Location:** `dist/pickal/bin/pickal` (`chmod 755`)

**Logic:**

\#\!/usr/bin/env bash

set \-euo pipefail

INSTALL\_DIR="$(dirname "$(realpath "$0")")/.."

\# Step 1: Ensure uv is available

if \! command \-v uv &\>/dev/null; then

    echo "\[pickal\] uv not found. Installing uv..." \>&2

    curl \-LsSf https://astral.sh/uv/install.sh | sh \>&2

fi

\# Step 2: Bootstrap venv on first run

if \[\[ \! \-d "$INSTALL\_DIR/.venv" \]\]; then

    uv venv "$INSTALL\_DIR/.venv" \--python 3.13 \>&2

    uv pip sync \--python "$INSTALL\_DIR/.venv" "$INSTALL\_DIR/conf/requirements.lock" \>&2

fi

\# Step 3: Install wheel if not already installed

uv pip install \--python "$INSTALL\_DIR/.venv" \\

    "$INSTALL\_DIR/lib/"pickal-\*.whl \--quiet \>&2

\# Step 4: Execute (replace process)

exec "$INSTALL\_DIR/.venv/bin/python" \-m pickal "$@"

### 6\. Portability & Cleanup

- **Isolation:** All files (`.venv`, logs) remain inside `$INSTALL_DIR` or XDG state dir.  
- **Uninstall:**  
    
  rm \-rf \~/.local/share/pickal && rm \~/.local/bin/pickal

### 7\. OAuth2 Credential Bootstrap (First Use)

Google OAuth2 credentials are not bundled in the artifact. On `pickal auth`:

1. User downloads `google_credentials.json` from Google Cloud Console.  
2. Places it at the path configured in `settings.google.credentials_path`.  
3. Runs `pickal auth --provider google` — opens browser for consent.  
4. Token stored at `settings.google.token_path` with `chmod 600`.

This step is documented in `README.md`. It is a one-time operation per machine.

---

## Gap Register (Pending Atoms)

The following concerns require implementation attention but lack a formal atom template. Decisions are recorded here as interim ADRs.

### Gap 1: Security & Auth (Pending Atom)

| Concern | Decision |
| :---- | :---- |
| OAuth2 token storage | `~/.config/pickal/google_token.json`; `chmod 600` enforced on write by `GoogleCalendarAdapter._save_token()` |
| Credential file permissions | `google_credentials.json` must be `600`; validated at `pickal auth` time with explicit error if not |
| API key logging prevention | `SecretStr` in Pydantic Settings; custom `logging.Filter` redacts substrings matching `api_key|token|credentials|secret` |
| Token refresh | `google-auth-oauthlib` auto-refreshes. On `google.auth.exceptions.RefreshError` → exit code 3 with message: "Token expired. Run `pickal auth --provider google`." |
| No credential git leakage | `.gitignore` includes `google_credentials.json`, `google_token.json`, `.env` |

### Gap 2: Error Handling & Recovery (Pending Atom)

| Error Condition | Behavior |
| :---- | :---- |
| Anthropic API `429 RateLimitError` | Exponential backoff: 1s, 2s, 4s (max 3 retries), then exit 1 |
| Anthropic API `5xx` | Immediate exit 1 with message to stderr |
| Zero events extracted | Exit 4 with message: "No events found in image. Verify image clarity." |
| All events below confidence | Exit 5 with table of skipped events; suggest `--force` |
| Image too large (\>20 MB) | Validated before API call. Exit 2 with message: "Image exceeds 20 MB limit." |
| Unsupported image format | Validated via `imghdr` / `magic` bytes. Exit 2 with supported formats listed |
| Google Calendar `403` | Exit 1: "Calendar write denied. Check calendar ID and scopes." |
| Google Calendar `409` conflict | Log warning to stderr, continue with remaining events. Reported in summary as `[CONFLICT]` |
| `FileNotFoundError` on image path | Exit 2: "Image file not found: " |
| Network timeout | 30s timeout on all requests. Exit 1 with "Request timed out." |

### Gap 3: Data Model Detail (Pending Atom)

| Concern | Decision |
| :---- | :---- |
| Event deduplication | Not implemented in v1.0. Future: hash `(title, start_iso)` → compare against existing events via `calendars.events.list` |
| Multi-day events | `ExtractedEvent.end.date() > ExtractedEvent.start.date()` → `GoogleCalendarAdapter` sets `end.dateTime` accordingly |
| All-day events | If `start_time` absent in extraction, Claude is prompted to flag as `all_day: bool`. Google API uses `date` instead of `dateTime` |
| Timezone resolution | Priority: (1) explicit tz in image text; (2) `--timezone` flag; (3) `settings.extraction.timezone`; (4) system local timezone |
| Extraction prompt | System prompt includes: today's ISO date, default timezone, instruction to output all datetimes as ISO 8601 with UTC offset, instruction to set `confidence < 0.75` for any ambiguous date |

