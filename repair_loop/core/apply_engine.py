from __future__ import annotations

import importlib.util
import json
import shutil
import sqlite3
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from .fix_engine import FixSuggestion


@dataclass(slots=True)
class ApplyResult:
    attempted: bool
    ok: bool
    command: str | None
    stdout: str
    stderr: str
    reason: str | None = None


def _rollback_dir() -> Path:
    path = Path(".repairloop") / "rollback"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _write_rollback_record(action: str, target: Path, backup: Path | None) -> None:
    record = {
        "time": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "target": str(target),
        "backup": str(backup) if backup else None,
    }
    record_path = _rollback_dir() / "records.jsonl"
    with record_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def _backup_file(path: Path) -> Path:
    rollback = _rollback_dir()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    backup = rollback / f"{path.name}.{stamp}.bak"
    shutil.copy2(path, backup)
    return backup


def _apply_create_path(raw_path: str) -> ApplyResult:
    if not raw_path or raw_path == "<path>":
        return ApplyResult(True, False, None, "", "", "missing path was not parsed")
    path = Path(raw_path)
    if path.exists():
        return ApplyResult(True, True, None, f"path already exists: {path}", "")
    if path.suffix:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch(exist_ok=True)
        _write_rollback_record("create_file", path, None)
        return ApplyResult(True, True, None, f"created file: {path}", "")
    path.mkdir(parents=True, exist_ok=True)
    _write_rollback_record("create_directory", path, None)
    return ApplyResult(True, True, None, f"created directory: {path}", "")


def _apply_append_missing_colon(payload: str) -> ApplyResult:
    try:
        raw_path, raw_line = payload.rsplit(":", 1)
        line_number = int(raw_line)
    except ValueError:
        return ApplyResult(True, False, None, "", "", "invalid append_missing_colon action payload")

    path = Path(raw_path)
    if not path.exists() or not path.is_file():
        return ApplyResult(True, False, None, "", "", f"target file does not exist: {path}")

    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    index = line_number - 1
    if index < 0 or index >= len(lines):
        return ApplyResult(True, False, None, "", "", f"line out of range: {line_number}")

    line = lines[index]
    newline = "\n" if line.endswith("\n") else ""
    body = line[:-1] if newline else line
    if body.rstrip().endswith(":"):
        return ApplyResult(True, True, None, f"line already has colon: {path}:{line_number}", "")

    backup = _backup_file(path)
    trailing = body[len(body.rstrip()):]
    lines[index] = body.rstrip() + ":" + trailing + newline
    path.write_text("".join(lines), encoding="utf-8")
    _write_rollback_record("append_missing_colon", path, backup)
    return ApplyResult(True, True, None, f"appended missing colon: {path}:{line_number}", "")


def _load_db_path() -> Path:
    config_path = Path("config.py")
    if config_path.exists():
        spec = importlib.util.spec_from_file_location("RepairLoop_target_config", config_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            db_path = getattr(module, "DB_PATH", None)
            if db_path:
                return Path(db_path)
    return Path("data") / "app.db"


def _apply_sqlite_create_users_table() -> ApplyResult:
    db_path = _load_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    existed = db_path.exists()
    backup = _backup_file(db_path) if existed else None
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT NOT NULL)")
        conn.execute("INSERT OR IGNORE INTO users (id, name) VALUES (?, ?)", (1, "Local User"))
        conn.commit()
    finally:
        conn.close()
    _write_rollback_record("sqlite_create_users_table", db_path, backup)
    return ApplyResult(True, True, None, f"created/verified users table: {db_path}", "")


def _apply_action(action: str) -> ApplyResult:
    if action.startswith("create_path:"):
        return _apply_create_path(action.removeprefix("create_path:").strip())
    if action.startswith("append_missing_colon:"):
        return _apply_append_missing_colon(action.removeprefix("append_missing_colon:").strip())
    if action == "sqlite_create_users_table":
        return _apply_sqlite_create_users_table()
    return ApplyResult(True, False, None, "", "", f"unsupported action: {action}")


def apply_suggestion(
    suggestion: FixSuggestion,
    *,
    enabled: bool,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> ApplyResult:
    if not enabled:
        return ApplyResult(
            attempted=False,
            ok=False,
            command=None,
            stdout="",
            stderr="",
            reason="apply disabled; rerun with --apply to execute safe fix commands",
        )

    if suggestion.actions:
        return _apply_action(suggestion.actions[0])

    if not suggestion.commands:
        return ApplyResult(
            attempted=False,
            ok=False,
            command=None,
            stdout="",
            stderr="",
            reason="no automatic command available for this fix",
        )

    command = suggestion.commands[0]
    completed = runner(
        command,
        shell=True,
        text=True,
        capture_output=True,
        check=False,
    )
    return ApplyResult(
        attempted=True,
        ok=completed.returncode == 0,
        command=command,
        stdout=completed.stdout,
        stderr=completed.stderr,
        reason=None if completed.returncode == 0 else f"fix command exited with code {completed.returncode}",
    )
