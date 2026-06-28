# pickal — Contributing Guidelines

## Overview

This document outlines the contribution guidelines for pickal.

## Getting Started

### Prerequisites

- Python 3.13 or higher
- uv (Python package manager)
- Git
- Basic understanding of Python development

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
# Clone the repository
git clone 
cd pickal

# Install development dependencies
just setup
```

## Contribution Workflow

### Before You Start

1. **Check existing issues**: Search for existing issues or features
2. **Discuss your idea**: Open an issue to discuss your proposal
3. **Fork the repository**: Create a fork of the main repository
4. **Create a branch**: Use a descriptive branch name

### Making Changes

1. **Make your changes**: Implement your feature or fix
2. **Add tests**: Include tests for your changes
3. **Update documentation**: Update relevant documentation
4. **Run quality checks**: Ensure all quality gates pass

### Quality Gates

Before submitting a pull request, ensure:

```bash
# Run all quality checks
just check

# Run tests
just test

# Run linting
just lint

# Format code
just fmt

# Build package
just build
```

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for all public functions
- Use meaningful variable names
- Keep functions small and focused

### Testing

- Write unit tests for all business logic
- Write integration tests for API endpoints
- Use fixtures for test data
- Aim for >80% code coverage
- Test error conditions

## Pull Request Process

### Before Submitting

1. **Ensure quality gates pass**: Run `just check`
2. **Update documentation**: Update relevant docs
3. **Add tests**: Include tests for new functionality
4. **Check formatting**: Run `just fmt`
5. **Self-review**: Review your own code

### Pull Request Template

```markdown
## Description

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update
- [ ] Refactoring

## Checklist

- [ ] I have read the CONTRIBUTING.md document
- [ ] I have run the test suite locally
- [ ] I have added tests for my changes
- [ ] I have updated the documentation
- [ ] I have formatted my code
- [ ] I have ensured all quality gates pass

## Testing

- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Coverage >80%

## Breaking Changes

- [ ] This change introduces breaking changes
- [ ] I have updated the documentation
- [ ] I have communicated the changes to users

## Additional Information

```

### Review Process

1. **Initial review**: Maintainer reviews the pull request
2. **Feedback**: Feedback provided if needed
3. **Revisions**: Address any feedback
4. **Approval**: Pull request approved
5. **Merge**: Pull request merged

## Development Guidelines

### Architecture

- Follow the existing architecture patterns
- Use the established coding conventions
- Maintain separation of concerns
- Use dependency injection where appropriate

### Error Handling

- Use the established error hierarchy
- Provide meaningful error messages
- Log errors appropriately
- Handle exceptions gracefully

### Configuration

- Use the established configuration system
- Follow the configuration hierarchy
- Validate configuration inputs
- Provide sensible defaults

### Testing

- Write tests for all new functionality
- Use fixtures for test data
- Mock external dependencies
- Test both success and failure cases

## Release Process

### Versioning

We use semantic versioning:

- **Major**: Breaking changes
- **Minor**: New features (backward compatible)
- **Patch**: Bug fixes (backward compatible)

### Release Checklist

1. **Ensure quality gates pass**: `just check`
2. **Update version**: `just tag`
3. **Build package**: `just build`
4. **Create release**: `just release`
5. **Verify release**: Test the release package

## Community Guidelines

### Communication

- Be respectful and constructive
- Ask questions if you need help
- Provide clear and detailed information
- Respond to feedback in a timely manner

### Code of Conduct

We expect all contributors to follow our code of conduct:

- Be respectful to others
- Avoid harassment and discrimination
- Respect privacy and confidentiality
- Be inclusive and welcoming

## Support

### Getting Help

- **Issues**: Open an issue for bugs or questions
- **Discussions**: Use discussions for general questions
- **Documentation**: Check the documentation first
- **Community**: Engage with the community

### Reporting Issues

When reporting issues, please include:

- **Description**: Clear description of the issue
- **Steps to reproduce**: Steps to reproduce the issue
- **Expected behavior**: What you expected to happen
- **Actual behavior**: What actually happened
- **Environment**: Python version, OS, etc.
- **Logs**: Relevant log output

## License

By contributing to pickal, you agree that your contributions will be licensed under the project's license.

## Acknowledgments

Thank you for contributing to pickal! Your contributions help make this project better for everyone.