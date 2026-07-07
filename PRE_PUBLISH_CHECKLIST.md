# Pre-Publish Checklist

Use this before the first GitHub push.

## Required Before Publishing

- Confirm the final GitHub repository owner/name.
- Add a CI badge and repository URLs after the remote exists, if desired.
- Review README wording and screenshots/demo plan.
- Run `python -m pytest -q`.
- Run `python -m pip install -e .`.
- Run `repair-loop --help`.

## Suggested First Commit

```powershell
git add .
git commit -m "Release v0.1.0 local-first repair prototype"
```

## Suggested GitHub Setup

```powershell
git branch -M main
git remote add origin <repo-url>
git push -u origin main
```

Do not run the GitHub setup until the final repo URL is confirmed.
