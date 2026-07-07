# Security Policy

## Supported Versions

RepairLoop is currently a v0.x prototype. Security fixes target the latest `main` branch until the first stable release.

## Safety Model

RepairLoop is local-first and does not require external AI APIs or API keys. The base repair engine runs on your machine and uses explicit, rule-based suggestions.

Automatic changes are opt-in:

- `repair` without `--apply` only observes and suggests fixes.
- `repair --apply` may create local files/directories, patch narrow syntax patterns, update local SQLite fixtures, or run the first suggested command.
- Rollback metadata for file edits is written under `.repairloop/rollback/`.

Only run RepairLoop against projects you trust. Runtime repair tools execute target commands and may run package manager commands when `--apply` is enabled.

## Reporting Issues

Please open a GitHub issue with:

- RepairLoop version or commit hash.
- Operating system and Python version.
- The exact command you ran.
- Sanitized stderr/stdout or a minimal reproduction.

Do not include secrets, API keys, private source code, or production database files in reports.
