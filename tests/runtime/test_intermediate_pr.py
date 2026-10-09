import pytest

from thesis_factory.runtime.journal import append_event, create_run_directory, read_events
from thesis_factory.runtime.pr_checkpoint import prepare_pr_body


def test_pr_body_excludes_logs_and_keeps_review_gate(tmp_path):
    run_dir = create_run_directory(tmp_path, "run1")
    append_event(run_dir, "run1", "research", "STAGE_STARTED", metadata={"attempt": 1})
    append_event(run_dir, "run1", "research", "STAGE_COMPLETED",
                 metadata={"exit_code": 0})
    (run_dir / "secret.txt").write_text("PRIVATE_RESEARCH_CONTENT")
    path, safe = prepare_pr_body(root=tmp_path, run_id="run1", title="Research checkpoint",
                                 stage="research", git_sha="123abc")
    assert safe
    result = path.read_text()
    assert "PRIVATE_RESEARCH_CONTENT" not in result
    assert "Do not merge automatically" in result
    assert "STAGE_COMPLETED" in result
    assert read_events(run_dir)[-1]["event_type"] == "PR_PREPARED"


def test_failed_stage_blocks_automatic_pr(tmp_path):
    run_dir = create_run_directory(tmp_path, "run2")
    append_event(run_dir, "run2", "verify", "STAGE_FAILED",
                 metadata={"exit_code": 9})
    path, safe = prepare_pr_body(root=tmp_path, run_id="run2", title="Verification",
                                 stage="verify", git_sha="456def")
    assert not safe
    assert "incomplete, failed, or timed out" in path.read_text()


def test_empty_run_cannot_claim_progress(tmp_path):
    with pytest.raises(ValueError):
        prepare_pr_body(root=tmp_path, run_id="empty", title="Empty",
                        stage="none", git_sha="none")


def test_started_stage_blocks_automatic_pr(tmp_path):
    run_dir = create_run_directory(tmp_path, "run3")
    append_event(run_dir, "run3", "search", "STAGE_STARTED",
                 metadata={"attempt": 1})
    body, safe = prepare_pr_body(root=tmp_path, run_id="run3", title="Pending",
                                 stage="search", git_sha="567abc")
    assert not safe
    assert "STAGE_STARTED" in body.read_text()
