import json

import pytest

from thesis_factory.runtime.checkpoint import CheckpointError, create_research_checkpoint
from thesis_factory.runtime.journal import read_events


def _research_json(topic="Topic"):
    return {
        "approved_topic": topic,
        "findings": [{
            "finding_id": "gap-1", "dimension": "RESEARCH_GAP",
            "statement": "The gap is currently unknown.",
            "rationale": "No adequate comparison has been verified.",
            "state": "UNKNOWN", "supporting_requirement_ids": [],
        }],
    }


def test_research_checkpoint_is_content_addressed(tmp_path):
    source = tmp_path / "proposal_research_draft.json"
    source.write_text(json.dumps(_research_json()))
    manifest = create_research_checkpoint(root=tmp_path / "runs", run_id="r01",
                                          artifacts={"research_draft": source})
    entry = manifest["artifacts"]["research_draft"]
    stored = tmp_path / "runs" / "r01" / entry["stored_filename"]
    assert stored.read_bytes() == source.read_bytes()
    assert manifest["research_summary"]["research_findings"] == 1
    assert manifest["validation"] == "LOCAL_SCHEMA_AND_IDENTITY_ONLY"
    assert manifest["research_summary"]["research_links"] == "DEFERRED"
    assert read_events(tmp_path / "runs/r01")[-1]["event_type"] == "CHECKPOINT_CREATED"
    again = create_research_checkpoint(root=tmp_path / "runs", run_id="r01",
                                       artifacts={"research_draft": source})
    assert again["artifacts"]["research_draft"]["sha256"] == entry["sha256"]
    assert len(list((tmp_path / "runs/r01/checkpoints").glob("*.json"))) == 2


def test_invalid_json_creates_no_checkpoint(tmp_path):
    source = tmp_path / "invalid.json"
    source.write_text('{"approved_topic":"Topic", "findings":[] }')
    with pytest.raises(ValueError):
        create_research_checkpoint(root=tmp_path / "runs", run_id="r02",
                                   artifacts={"research_draft": source})
    assert not (tmp_path / "runs/r02").exists()


def test_unknown_artifact_role_fails(tmp_path):
    with pytest.raises(CheckpointError):
        create_research_checkpoint(root=tmp_path, run_id="r01",
                                   artifacts={"unknown": tmp_path / "file.json"})
