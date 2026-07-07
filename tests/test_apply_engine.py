import sqlite3
import subprocess

from repair_loop.core.apply_engine import apply_suggestion
from repair_loop.core.fix_engine import ErrorKind, FixSuggestion


def test_apply_disabled_does_not_attempt_command():
    suggestion = FixSuggestion(
        kind=ErrorKind.MODULE_NOT_FOUND,
        summary="missing",
        commands=["python -m pip install example"],
        notes=[],
    )
    result = apply_suggestion(suggestion, enabled=False)
    assert result.attempted is False
    assert result.ok is False
    assert result.command is None


def test_apply_runs_first_command_when_enabled():
    calls = []

    def fake_runner(command, **kwargs):
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(command, 0, stdout="installed", stderr="")

    suggestion = FixSuggestion(
        kind=ErrorKind.MODULE_NOT_FOUND,
        summary="missing",
        commands=["python -m pip install example"],
        notes=[],
    )
    result = apply_suggestion(suggestion, enabled=True, runner=fake_runner)
    assert result.attempted is True
    assert result.ok is True
    assert result.command == "python -m pip install example"
    assert result.stdout == "installed"
    assert calls[0][0] == "python -m pip install example"


def test_apply_create_path_action_creates_file(tmp_path):
    target = tmp_path / "config" / "settings.txt"
    suggestion = FixSuggestion(
        kind=ErrorKind.FILE_NOT_FOUND,
        summary="missing file",
        commands=[],
        notes=[],
        actions=[f"create_path:{target}"],
    )
    result = apply_suggestion(suggestion, enabled=True)
    assert result.ok is True
    assert target.exists()
    assert target.is_file()


def test_apply_append_missing_colon_creates_backup_and_patch(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    target = tmp_path / "broken.py"
    target.write_text("def main()\n    pass\n", encoding="utf-8")
    suggestion = FixSuggestion(
        kind=ErrorKind.SYNTAX_ERROR,
        summary="missing colon",
        commands=[],
        notes=[],
        actions=[f"append_missing_colon:{target}:1"],
    )
    result = apply_suggestion(suggestion, enabled=True)
    assert result.ok is True
    assert target.read_text(encoding="utf-8").splitlines()[0] == "def main():"
    backups = list((tmp_path / ".repairloop" / "rollback").glob("broken.py.*.bak"))
    assert backups
    assert (tmp_path / ".repairloop" / "rollback" / "records.jsonl").exists()


def test_apply_sqlite_create_users_table_uses_config_db_path(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "config.py").write_text(
        "from pathlib import Path\nDB_PATH = str(Path('data') / 'app.db')\n",
        encoding="utf-8",
    )
    suggestion = FixSuggestion(
        kind=ErrorKind.SQLITE_MISSING_TABLE,
        summary="missing users",
        commands=[],
        notes=[],
        actions=["sqlite_create_users_table"],
    )
    result = apply_suggestion(suggestion, enabled=True)
    assert result.ok is True
    conn = sqlite3.connect(tmp_path / "data" / "app.db")
    try:
        row = conn.execute("SELECT name FROM users WHERE id = 1").fetchone()
    finally:
        conn.close()
    assert row == ("Local User",)
