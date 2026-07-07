# Contributing

Thanks for helping improve RepairLoop.

## Development Setup

```powershell
python -m pip install -e .[dev]
python -m pytest -q
```

## Project Principles

- Keep the base engine local-first and offline-capable.
- Prefer small, explainable rule-based repairs over broad rewrites.
- Never require an external AI API key for core functionality.
- Keep automatic fixes opt-in behind `--apply`.
- Add tests for every new repair rule.

## Adding a Repair Rule

1. Add classification/suggestion logic in `repair_loop/core/fix_engine.py`.
2. Add apply logic in `repair_loop/core/apply_engine.py` only if the fix is narrow and safe.
3. Add unit tests under `tests/`.
4. Update `README.md` and `RELEASE_NOTES.md` if user-facing behavior changes.

## Before Opening a PR

```powershell
python -m pytest -q
```

Keep PRs focused. A single repair rule with tests is better than a large mixed change.
