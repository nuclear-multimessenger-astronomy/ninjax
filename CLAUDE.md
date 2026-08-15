# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## IMPORTANT GUIDELINES

**Contributing guide**: `CONTRIBUTING.md` at the repo root is the authoritative reference for development workflow and PR requirements. Always consult it when working on new features or before opening a PR.

**Testing Philosophy**: When tests fail, investigate root causes rather than modifying tests to pass.

**Documentation Style**: Write clear, concise documentation in full sentences as if by a human researcher. Avoid LLM-like verbosity.

**Sphinx warnings are errors**: CI runs `sphinx-build -W --keep-going`, which turns every Sphinx warning into a build failure that blocks merging. Always verify locally before committing.

**Math Formatting in Docstrings**: All mathematical expressions in docstrings must use Sphinx/reStructuredText formatting:
- Use `:math:` role for inline math: `:math:`\Gamma(x)``
- Use `.. math::` directive for display equations
- Always use raw strings (`r"""`) for docstrings containing LaTeX

**File Operations**: Use proper tools (Write, Edit, Read) instead of bash heredocs or cat redirection.

---

## Project Overview

**package_name** is a Python package for [DESCRIBE YOUR PACKAGE].

### Core Modules

**src/package_name/** - Main package source
- Add description of your modules here

---

## Development Commands

### Always Use `uv`
```bash
# Run Python commands
uv run <command>

# Install dependencies
uv pip install <package>
```

### Code Quality
```bash
# Run tests
uv run pytest -v tests/

# Run pyright
uv run pyright

# Run pre-commit
uv run pre-commit run --all-files
```

### Documentation
```bash
# Build docs locally
uv pip install -e ".[dev]"
uv run sphinx-build docs docs/_build/html
open docs/_build/html/index.html

# Strict mode (same as CI)
uv run sphinx-build -W --keep-going docs docs/_build/html
```

## Code Quality Standards

**All new code MUST include comprehensive type hints.**

```python
# Standard library types (Python 3.10+ syntax)
def process_data(values: list[float], threshold: float | None = None) -> dict[str, float]:
    ...
```

**Type checking**: `uv run pyright src/package_name/`
