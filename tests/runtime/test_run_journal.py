import sys

import pytest

from thesis_factory.runtime.journal import append_event, create_run_directory, read_events
from thesis_factory.runtime.stage import run_stage


def test_journal_is_append_only_and_validates_event_types(tmp_path):
    run_dir = create_run_directory(tmp_path, "research-01")
    append_event(run_dir, "research-01", "discovery", "STAGE_STARTED",
                 metadata={"attempt": 1})
    append_event(run_dir, "research-01", "discovery", "STAGE_COMPLETED",
                 metadata={"exit_code": 0})
    events = read_events(run_dir, run_id="research-01")
    assert [e["event_type"] for e in events] == ["STAGE_STARTED", "STAGE_COMPLETED"]
    assert all(e["schema_version"] == 1 for e in events)
    with pytest.raises(ValueError):
        append_event(run_dir, "research-01", "discovery", "MADE_UP")


def test_logged_wrapper_persists_stdout_stderr_and_failure(tmp_path):
    command = [sys.executable, "-c", "import sys; print('ok'); print('err',file=sys.stderr); sys.exit(3)"]
    result = run_stage(run_root=tmp_path, run_id="research-02", stage="verify",
                       command=command, timeout_sec=4)
    assert result == 3
    run_dir = tmp_path / "research-02"
    assert (run_dir / "steps/verify-0001/stdout.log").read_text().strip() == "ok"
    assert (run_dir / "steps/verify-0001/stderr.log").read_text().strip() == "err"
    assert read_events(run_dir)[-1]["event_type"] == "STAGE_FAILED"


def test_logged_wrapper_timeout(tmp_path):
    result = run_stage(run_root=tmp_path, run_id="research-03", stage="slow",
                       command=[sys.executable, "-c", "import time; time.sleep(30)"],
                       timeout_sec=1)
    assert result == 124
    assert read_events(tmp_path / "research-03")[-1]["event_type"] == "STAGE_TIMED_OUT"


def test_run_id_blocks_traversal(tmp_path):
    with pytest.raises(ValueError):
        create_run_directory(tmp_path, "../../outside")


def test_model_usage_does_not_store_prompts(tmp_path):
    from thesis_factory.runtime.journal import record_model_usage
    run_dir = create_run_directory(tmp_path, "usage")
    record_model_usage(run_dir, "usage", "verify", provider="anthropic",
                       model="claude-example", input_tokens=12, output_tokens=7,
                       elapsed_ms=100)
    saved = (run_dir / "events.jsonl").read_text()
    assert '"MODEL_USAGE"' in saved
    assert "prompt" not in saved
    with pytest.raises(ValueError):
        record_model_usage(run_dir, "usage", "verify", provider="anthropic",
                           model="claude-example", input_tokens=-1,
                           output_tokens=1, elapsed_ms=100)
