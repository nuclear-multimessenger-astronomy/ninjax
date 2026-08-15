# Contributing

For full contributing guidelines, see [`CONTRIBUTING.md`](../../CONTRIBUTING.md) at the repository root.

## Quick Reference

```bash
# Run tests
uv run pytest tests/ -m "not slow"

# Type checking
uv run pyright src/ninjax/

# Pre-commit checks
uv run pre-commit run --all-files

# Build docs (strict mode)
uv run sphinx-build -W --keep-going docs docs/_build/html
```
