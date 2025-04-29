# Contributing to IoT Device Controller

Thank you for your interest in contributing to the IoT Device Controller project! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please read and follow it to ensure a positive experience for everyone.

## How Can I Contribute?

### Reporting Bugs

Before reporting a bug, please search existing issues to see if it has already been reported. If not, create a new issue with the following information:

- A clear, descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Screenshots or code samples if applicable
- Your environment (OS, browser, etc.)

### Suggesting Enhancements

Enhancement suggestions are welcome! When suggesting an enhancement:

- Use a clear, descriptive title
- Provide a detailed description of the proposed enhancement
- Explain why this enhancement would be useful
- Include example code or mockups if possible

### Pull Requests

We actively welcome pull requests. To submit a PR:

1. Fork the repository
2. Create a new branch from `develop`: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Run tests to ensure they pass: `pytest`
5. Format your code with appropriate tools
6. Commit your changes following our commit message guidelines
7. Push to your fork and submit a pull request to the `develop` branch

For detailed instructions, please refer to the [Development Guide](docs/development.md).

## Development Process

### Setting Up Development Environment

See the [Development Guide](docs/development.md) for detailed instructions on setting up your development environment.

### Coding Standards

We follow specific coding standards to ensure code quality and consistency. Please refer to the [Development Guide](docs/development.md) for details on:

- Python style guide
- JavaScript style guide
- HTML/CSS style guide
- Code documentation requirements

### Commit Message Format

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>: <description>

[optional body]

[optional footer]
```

Types include:

- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring without changing functionality
- `test`: Adding or updating tests
- `chore`: Routine tasks, maintenance, etc.

### Testing

All new code should include appropriate tests:

- Unit tests for individual functions and classes
- Integration tests for component interactions
- Functional tests for API endpoints

See the [Development Guide](docs/development.md) for more details on testing.

## Review Process

All submissions require review. The review process ensures code quality and consistency:

1. Automated CI checks must pass (tests, linting, etc.)
2. At least one project maintainer must approve the changes
3. Changes may require revisions before acceptance

## Community

Connect with other contributors:

- GitHub Discussions
- Issue tracker

## License

By contributing to IoT Device Controller, you agree that your contributions will be licensed under the project's MIT License.

## Questions?

If you have any questions about contributing, please open an issue or contact the project maintainers.

---

Thank you for helping improve the IoT Device Controller project!

© 2024 Mahmoud Ashraf (SNO7E). All rights reserved. 