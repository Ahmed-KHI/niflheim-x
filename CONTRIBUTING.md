# Contributing to Niflheim_x

We welcome contributions to Niflheim_x! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

### Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Ahmed-KHI/niflheim-x.git
   cd niflheim-x
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```

## 🧪 Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=niflheim_x

# Run specific test file
pytest tests/test_agent.py

# Run tests in watch mode
pytest-watch
```

### Code Formatting

We use Black for code formatting and Ruff for linting:

```bash
# Format code
black niflheim_x/ tests/ examples/

# Check linting
ruff check niflheim_x/ tests/ examples/

# Fix auto-fixable linting issues
ruff check --fix niflheim_x/ tests/ examples/
```

### Type Checking

```bash
# Run type checking
mypy niflheim_x/
```

## 📝 Contribution Guidelines

### Code Style

- Follow PEP 8 style guidelines
- Use type hints for all functions and methods
- Write comprehensive docstrings for all public APIs
- Keep line length to 88 characters (Black default)
- Use meaningful variable and function names

### Documentation

- Document all public classes, methods, and functions
- Include examples in docstrings where helpful
- Update README.md if adding new features
- Add type hints to all function signatures

### Testing

- Write tests for all new functionality
- Aim for >90% test coverage
- Include both unit tests and integration tests
- Test error conditions and edge cases
- Use meaningful test names that describe what is being tested

### Commit Messages

Follow conventional commit format:

```
type(scope): description

feat(agent): add streaming response support
fix(memory): resolve SQLite connection issue
docs(readme): update installation instructions
test(tools): add tests for async tool execution
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `style`: Code style changes
- `perf`: Performance improvements
- `chore`: Build process or auxiliary tool changes

## 🛠️ Types of Contributions

### Bug Reports

When reporting bugs, please include:

- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Python version and OS
- Minimal code example
- Error messages and stack traces

### Feature Requests

For new features:

- Describe the use case and motivation
- Provide examples of how it would be used
- Consider backwards compatibility
- Discuss implementation approach

### Code Contributions

1. **Fork the repository**
2. **Create a feature branch:** `git checkout -b feature/your-feature-name`
3. **Make your changes** following the guidelines above
4. **Add tests** for your changes
5. **Update documentation** if needed
6. **Run the test suite** to ensure everything passes
7. **Commit your changes** with a clear commit message
8. **Push to your fork** and create a pull request

### Pull Request Process

1. Ensure all tests pass and code is properly formatted
2. Update documentation for any API changes
3. Add entries to CHANGELOG.md for significant changes
4. Request review from maintainers
5. Address any feedback from code review
6. Maintain a clean commit history (squash if needed)

## 🏗️ Architecture Guidelines

### Core Principles

- **Minimal dependencies:** Keep the core lightweight
- **Composability:** Components should work well together
- **Type safety:** Use type hints throughout
- **Async-first:** Design for async/await patterns
- **Extensibility:** Make it easy to add new adapters and backends

### Adding New LLM Adapters

1. Inherit from `LLMAdapter` base class
2. Implement all abstract methods
3. Handle streaming and non-streaming responses
4. Add comprehensive error handling
5. Include adapter-specific configuration options
6. Write tests for all functionality
7. Add documentation and examples

### Adding New Memory Backends

1. Inherit from `MemoryBackend` base class
2. Implement all abstract methods
3. Handle session management properly
4. Consider performance for large message histories
5. Add configuration options
6. Include migration utilities if needed
7. Write thorough tests
8. Document usage patterns

### Adding New Tools

1. Use the `@tool` decorator for simple functions
2. Create `Tool` objects for complex tools
3. Include proper type hints and docstrings
4. Handle errors gracefully
5. Consider timeout and async execution
6. Add comprehensive tests
7. Include usage examples

## 🔍 Code Review Guidelines

### For Contributors

- Keep pull requests focused and reasonably sized
- Write clear descriptions of changes
- Respond promptly to review feedback
- Test your changes thoroughly
- Be open to suggestions and improvements

### For Reviewers

- Be constructive and helpful in feedback
- Focus on code quality, maintainability, and correctness
- Check for proper testing and documentation
- Verify backwards compatibility
- Approve when changes meet project standards

## 📋 Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md with release notes
3. Create release branch: `git checkout -b release/v0.x.0`
4. Run full test suite
5. Create pull request for release branch
6. After merge, tag release: `git tag v0.x.0`
7. Publish to PyPI
8. Create GitHub release with notes

## 🤝 Community Guidelines

- Be respectful and inclusive
- Help newcomers get started
- Share knowledge and best practices
- Provide constructive feedback
- Follow the code of conduct

## 💡 Getting Help

- **Documentation:** Check our docs and examples first
- **Issues:** Search existing issues before creating new ones
- **Discussions:** Use GitHub Discussions for questions and ideas
- **Discord:** Join our community chat (link in README)

## 🏆 Recognition

Contributors will be recognized in:

- CONTRIBUTORS.md file
- Release notes for significant contributions
- Annual contributor highlights
- Project documentation credits

Thank you for contributing to Niflheim_x! 🌟
