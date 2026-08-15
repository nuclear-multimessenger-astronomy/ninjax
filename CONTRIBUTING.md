# Contributing to package_name

Thank you for your interest in contributing to package_name! This guide will help you get started with development.

## Quick Start

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/YOUR_ORG/package_name
cd package_name

# Install with development dependencies
uv sync --extra dev
```

### Running Tests

```bash
# Run all tests (excluding slow tests, while developing)
uv run pytest tests/ -m "not slow"

# Run all tests (including slow ones)
uv run pytest tests/

# Run specific test file
uv run pytest tests/test_example.py -v

# Run type checking
uv run pyright src/package_name/

# Run pre-commit checks
uv run pre-commit run --all-files
```

### Building Documentation

```bash
# Build docs locally
uv run sphinx-build docs docs/_build/html

# Build in strict mode (same as CI) — ALWAYS run this before opening a PR
uv run sphinx-build -W --keep-going docs docs/_build/html

# Open in browser
open docs/_build/html/index.html  # macOS
```

One can also use `sphinx-autobuild` to automatically rebuild on edits:
```bash
uv run sphinx-autobuild docs docs/_build/html
```

> **Sphinx warnings are treated as errors in CI.** The `-W` flag used by the CI pipeline turns every Sphinx warning into a hard build failure. Always run the strict-mode build locally before pushing.

## General Contribution Requirements

### Code Quality

- **Type hints** - Include type annotations in your code
  ```python
  def my_function(x: float, y: list[int]) -> dict[str, float]:
      ...
  ```

- **Docstrings** - Use proper math formatting where needed
  ```python
  def gamma_function(x: float) -> float:
      r"""Compute the gamma function.

      The gamma function is defined as :math:`\Gamma(x) = \int_0^\infty t^{x-1} e^{-t} dt`.

      Args:
          x: Input value where :math:`x > 0`

      Returns:
          Gamma function value
      """
  ```

### Testing

- **Unit tests** - Test individual components in isolation
- **Integration tests** - Test interactions between components
- **Comprehensive coverage** - Test edge cases and error handling

### Documentation

- **Docstrings** - All public functions and classes
- **API reference** - Auto-generated from docstrings
- **User guide** - Add page to `docs/` explaining the feature

## Pull Request Process

1. **Create a feature branch** from `main`:
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Make your changes** following the guidelines above

3. **Run the test suite**:
   ```bash
   uv run pytest tests/ -m "not slow"
   uv run pyright src/package_name/
   uv run pre-commit run --all-files
   ```

4. **Build documentation** (strict mode):
   ```bash
   uv run sphinx-build -W --keep-going docs docs/_build/html
   ```

5. **Commit with descriptive messages**:
   ```bash
   git add .
   git commit -m "Add new feature: brief description"
   ```

6. **Push and create PR**:
   ```bash
   git push origin feature/my-new-feature
   ```
   Then open a pull request on GitHub.

## Development Philosophy

> **Testing Philosophy**: When tests fail, investigate root causes rather than modifying tests to pass.

> **Documentation Style**: Write clear, concise documentation in full sentences as if by a human researcher. Avoid LLM-like verbosity.

## Getting Help

- **Documentation**: https://YOUR_ORG.github.io/package_name/
- **Issues**: https://github.com/YOUR_ORG/package_name/issues
- **Discussions**: https://github.com/YOUR_ORG/package_name/discussions

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please be respectful and professional in all interactions.
