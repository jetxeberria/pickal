# pickal — Architecture Documentation

## Overview

This document describes the architecture and design decisions for pickal.

## Architecture Overview

pickal follows a clean architecture pattern with separation of concerns:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLI/HTTP   │───▶│   API Layer  │───▶│  Domain     │
│   Interface   │    │   (REST/gRPC) │    │  Logic      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Core       │    │   Infrastructure│    │   External   │
│   (Config,   │    │   (Database,  │    │   Services   │
│   Logging)   │    │   APIs)       │    │              │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Core Components

### Configuration Management

- **Library**: Pydantic Settings
- **Strategy**: Schema-first hierarchical overrides
- **Precedence**: Environment variables > .env file > defaults
- **Fail-fast**: Application crashes on invalid configuration

### Error Handling

- **Base Error**: `BaseError` with code and details
- **Exit Codes**: Standardized exit codes for different error types
- **Logging**: Rich formatted error messages

### Logging

- **Library**: Rich logging with colorized output
- **Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Format**: Structured logging with timestamps

## Domain Layer

### Business Logic

- **Models**: Pydantic models for data validation
- **Services**: Business logic encapsulation
- **Repositories**: Data access abstraction
- **Events**: Domain events for decoupled communication

### Validation

- **Type Safety**: Strict type checking with mypy
- **Schema Validation**: Pydantic for data validation
- **Business Rules**: Custom validation logic

## API Layer

### CLI Interface

- **Library**: Cyclopts for command-line parsing
- **Features**: Verb-based commands, global options, JSON output
- **Commands**: Version, config, health, help

### REST API

- **Framework**: FastAPI (if implemented)
- **Features**: Automatic documentation, validation, async support
- **Security**: API keys, OAuth2, rate limiting

## Infrastructure

### Database

- **Abstraction**: Repository pattern
- **Support**: Multiple database backends
- **Transactions**: ACID compliance

### External Services

- **Clients**: HTTP clients with retry logic
- **Caching**: Redis or similar for performance
- **Monitoring**: Metrics and tracing

## Development Tools

### Testing

- **Framework**: pytest with coverage
- **Types**: Unit, integration, end-to-end tests
- **Fixtures**: Reusable test data

### Code Quality

- **Linting**: Ruff (replaces flake8, isort, pylint)
- **Formatting**: Ruff format
- **Type Checking**: mypy with strict mode

### CI/CD

- **Pipeline**: GitHub Actions
- **Quality Gates**: Linting, testing, type checking
- **Release**: Semantic release with automated versioning

## Distribution

### Packaging

- **Format**: Tarball with self-bootstrapping shim
- **Dependencies**: uv lockfile for reproducible builds
- **Execution**: User-space isolation without sudo

### Shim

- **Features**: Automatic uv installation, virtual environment setup
- **Execution**: Replaces bash process with isolated Python interpreter
- **Portability**: Works on any system with bash, curl, tar

## Configuration Management

### Hierarchy

1. **Environment Variables**: `PICKAL_VAR_NAME`
2. **Local Config**: `.env` file
3. **Defaults**: Hardcoded in configuration models

### Schema

- **Models**: Pydantic Settings for type safety
- **Validation**: Automatic validation on load
- **Documentation**: Auto-generated from schema

## Security Considerations

### Configuration

- **Secrets**: Never commit secrets to version control
- **Validation**: Strict validation of all inputs
- **Encryption**: Optional encryption for sensitive data

### API Security

- **Authentication**: API keys, OAuth2
- **Authorization**: Role-based access control
- **Rate Limiting**: Prevent abuse

## Performance

### Optimization

- **Caching**: Strategic caching of expensive operations
- **Async**: Asynchronous I/O for scalability
- **Profiling**: Performance monitoring and optimization

### Monitoring

- **Metrics**: Application metrics collection
- **Tracing**: Distributed tracing for debugging
- **Logging**: Structured logging for analysis

## Deployment

### Environment

- **Target**: Ubuntu/Linux systems
- **Isolation**: User-space virtual environments
- **Dependencies**: Minimal system requirements

### Updates

- **Template Updates**: `just update-template`
- **Configuration**: Hot-reload capable
- **Zero Downtime**: Graceful restarts

## Future Enhancements

### Planned Features

- **Plugin System**: Extensible architecture
- **Web UI**: Browser-based interface
- **Advanced Monitoring**: Prometheus integration
- **Multi-tenancy**: Support for multiple organizations

### Technical Debt

- **Documentation**: Comprehensive API documentation
- **Testing**: Higher test coverage
- **Performance**: Optimization of critical paths

## Decision Records

### ADR-001: Copier for Templating

**Context**: Static templates drift over time
**Decision**: Use Copier for template management
**Consequence**: Repositories can receive upstream updates

### ADR-002: uv for Package Management

**Context**: Python packaging is fragmented and slow
**Decision**: Standardize on uv
**Consequence**: Blazing fast CI times, unified lockfiles

### ADR-003: Pydantic Settings for Configuration

**Context**: Need robust configuration management
**Decision**: Pydantic Settings over Dynaconf
**Consequence**: Strict typing, IDE autocompletion

### ADR-004: just for Task Management

**Context**: Need cross-platform task runner
**Decision**: Use just over make
**Consequence**: Better Windows support, cleaner syntax

### ADR-005: Tarball + Shim Distribution

**Context**: Need local execution without system pollution
**Decision**: Build tarball with bash shim
**Consequence**: User-space isolation, no sudo required