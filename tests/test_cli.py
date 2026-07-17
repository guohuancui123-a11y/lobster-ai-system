import json
from pathlib import Path

import pytest

from repair_loop.cli import RunResult, first_blocking_error, main, print_apply_result, repair_loop, run_command
from repair_loop.core.apply_engine import ApplyResult


def test_first_blocking_error_uses_exception_line():
    result = RunResult(
        command=["python"],
        returncode=1,
        stdout="",
        stderr='Traceback\nModuleNotFoundError: No module named \'x\'\n',
    )
    assert first_blocking_error(result) == "ModuleNotFoundError: No module named 'x'"


def test_first_blocking_error_none_when_ok():
    result = RunResult(command=["python"], returncode=0, stdout="ok", stderr="")
    assert first_blocking_error(result) is None


def test_repair_loop_rejects_invalid_iteration_count(capsys):
    code = repair_loop(["python", "-c", "print('should not run')"], apply=False, max_iterations=0)

    captured = capsys.readouterr()
    assert code == 2
    assert "--max-iterations must be at least 1" in captured.err
    assert "Traceback" not in captured.err


def test_print_apply_result_marks_dry_run_preview(capsys):
    result = ApplyResult(
        attempted=False,
        ok=False,
        command=None,
        stdout="",
        stderr="",
        reason="apply disabled; rerun with --apply to execute safe fix commands",
    )

    print_apply_result(result)

    captured = capsys.readouterr()
    assert "[PREVIEW] no changes were made" in captured.out


def test_run_command_reports_startup_errors_without_traceback():
    result = run_command(["definitely-not-a-real-command-for-RepairLoop-tests"])

    assert result.returncode == 127
    assert "Could not start command" in result.stderr


def test_run_json_report_outputs_machine_readable_payload(capsys):
    code = main(["run", "--json-report", "--", "python", "-c", "print('json-ok')"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert code == 0
    assert payload["ok"] is True
    assert payload["returncode"] == 0
    assert payload["stdout"].strip() == "json-ok"
    assert payload["tool"]["name"] == "RepairLoop"
    assert "github.com/guohuancui123-a11y/repairloop" in payload["tool"]["url"]


def test_human_output_includes_source_attribution(capsys):
    code = main(["run", "--", "python", "-c", "print('source-ok')"])

    captured = capsys.readouterr()
    assert code == 0
    assert "[SOURCE] Built with RepairLoop" in captured.out
    assert "github.com/guohuancui123-a11y/repairloop" in captured.out


def test_repair_json_report_preview_is_machine_readable(capsys, tmp_path):
    target = tmp_path / "missing_file_demo.py"
    missing_path = tmp_path / "generated" / "config.txt"
    target.write_text(
        "from pathlib import Path\n"
        f"print(Path({str(missing_path)!r}).read_text())\n",
        encoding="utf-8",
    )

    code = main(["repair", "--json-report", "--", "python", str(target)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert code != 0
    assert payload["ok"] is False
    assert payload["preview"] is True
    assert payload["iterations"][0]["run"]["suggestion"]["kind"] == "file_not_found"


def test_main_version_prints_package_version(capsys):
    with pytest.raises(SystemExit) as error:
        main(["--version"])

    captured = capsys.readouterr()
    assert error.value.code == 0
    assert "repair-loop" in captured.out
    assert "Traceback" not in captured.err


def test_main_help_mentions_safe_first_run(capsys):
    with pytest.raises(SystemExit) as error:
        main(["--help"])

    captured = capsys.readouterr()
    assert error.value.code == 0
    assert "repair-loop demo" in captured.out
    assert "https://github.com/guohuancui123-a11y/repairloop" in captured.out


def test_demo_preview_uses_temporary_project(capsys):
    code = main(["demo"])

    captured = capsys.readouterr()
    assert code != 0
    assert "[DEMO] temporary project:" in captured.out
    assert "[PREVIEW] no changes were made" in captured.out
    assert "[VERIFY] not rerun; preview mode only" in captured.out
