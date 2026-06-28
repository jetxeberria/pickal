# pickal

> Identify events in a picture and save them to calendar

## Installation

Download the latest release tarball from the [Releases](../../releases) page:

```bash
# Extract to ~/.local/share
tar xf pickal-*-linux-x64.tar.gz -C ~/.local/share/
ln -s ~/.local/share/pickal-*/bin/pickal ~/.local/bin/pickal
```

On first run, the bootstrap shim will automatically:
1. Detect/download `uv` if needed
2. Create an isolated virtual environment
3. Install all dependencies from the locked requirements

```bash
pickal --help
```

## Usage

```
pickal [OPTIONS] COMMAND [ARGS]

Options:
  -v, --verbose    Increase verbosity (use -vv for DEBUG)
  -q, --quiet      Suppress stdout; only show errors
  --json           Force JSON output (machine-readable mode)
  --config PATH    Path to custom config file
  -h, --help       Show help and exit

Commands:
  run              TODO: describe your main command
  version          Print version and exit
```

## API

### CLI Commands

- `pickal version` - Show version
- `pickal config` - Show configuration
- `pickal health` - Check health
- `pickal help` - Show help

## Configuration

Config is resolved in this order (highest → lowest priority):

1. CLI flags
2. Environment variables (`PICKAL_*`)
3. User config: `~/.config/pickal/config.yaml`
4. System config: `/etc/pickal/config.yaml`
5. Bundled defaults: `conf/defaults.yaml`

## Configuration Options

| Option | Environment Variable | Default | Description |
|--------|---------------------|---------|-------------|
| debug | `PICKAL_DEBUG` | `false` | Enable debug mode |
| log_level | `PICKAL_LOG_LEVEL` | `INFO` | Logging level |
| host | `PICKAL_HOST` | `127.0.0.1` | Server host |
| port | `PICKAL_PORT` | `8080` | Server port |

## Development

```bash
# Install development dependencies
just setup

# Run tests
just test

# Run linting
just lint

# Format code
just fmt

# Build distribution
just build
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Run the test suite: `just test`
6. Submit a pull request

## License

MIT — see [LICENSE](LICENSE).
