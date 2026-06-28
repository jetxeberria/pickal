# pickal — Development Guide

## Prerequisites

- Python 3.13 or higher
- uv (Python package manager)
- Git

## Installation

### From Source

```bash
# Clone the repository
git clone 
cd pickal

# Install development dependencies
just setup
```

### Development Environment

#### Using direnv

```bash
# Install direnv
# (Follow instructions for your OS)

# Allow direnv in the project
direnv allow
```

#### Manual Setup

```bash
# Create virtual environment
uv venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
uv pip install -e .[dev]
```

## Development Workflow

### Code Quality

```bash
# Run linting
just lint

# Format code
just fmt

# Run type checking
just check
```

### Testing

```bash
# Run all tests
just test

# Run tests with coverage
just coverage

# Run specific test file
just test tests/unit/test_config.py
```

### Building

```bash
# Build the package
just build

# Create distribution
just release
```

## Project Structure

```
src/pickal/
├── core/           # Core functionality (config, logging, errors)
├── domain/         # Business logic
├── api/            # API layer (CLI, REST, gRPC)
└── cli.py          # CLI entrypoint

tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
└── conftest.py     # Test configuration

conf/
└── defaults.yaml   # Default configuration

docs/                 # Documentation
```

## Configuration

Configuration can be set via:

1. Environment variables: `PICKAL_VAR_NAME`
2. Local config file: `.env`
3. Default values in code

## Debugging

### Logging

Set the log level using the `LOG_LEVEL` environment variable:

```bash
export LOG_LEVEL=DEBUG
```

### Debugging with PDB

```bash
# Run with debugger
python -m pdb -m pickal
```

## Common Tasks

### Adding a New Command

1. Create a new function in `cli.py`
2. Decorate with `@app.command()`
3. Add documentation
4. Add tests

### Adding a New Configuration Option

1. Add to `config_schema.py`
2. Add default value to `defaults.yaml`
3. Add validation if needed
4. Update documentation

### Adding a New API Endpoint

1. Create new module in `api/`
2. Implement the endpoint
3. Add routing
4. Add tests
5. Update documentation

## Testing Guidelines

- Write unit tests for all business logic
- Write integration tests for API endpoints
- Use fixtures for test data
- Aim for >80% code coverage
- Test error conditions

## Code Style

- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for all public functions
- Use meaningful variable names
- Keep functions small and focused

## Git Workflow

1. Create feature branch: `git checkout -b feature-name`
2. Make changes and commit
3. Run tests: `just test`
4. Create pull request
5. Address review comments
6. Merge to main

## Release Process

1. Ensure all tests pass: `just test`
2. Update version: `just tag`
3. Build distribution: `just build`
4. Create release: `just release`
5. Verify release on GitHub