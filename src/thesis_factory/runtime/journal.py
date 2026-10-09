"""Append-only, local-first run journal for bounded stage execution.

The journal stores only explicitly supplied metadata. Never put model prompts,
secrets, URLs with tokens, evidence text or command arguments into events.
Raw stdout/stderr are retained locally (0600) and must not be published.
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]{0,79}$")
EVENT_TYPES = frozenset({
    "STAGE_STARTED", "STAGE_COMPLETED", "STAGE_FAILED", "STAGE_TIMED_OUT",
    "ARTIFACT_SNAPSHOTTED", "CHECKPOINT_CREATED", "PR_PREPARED",
    "PR_CREATED", "HUMAN_REVIEW_REQUIRED", "MODEL_USAGE",
})


def validate_id(value: str, label: str = "identifier") -> str:
    if not _ID.fullmatch(value):
        raise ValueError(f"invalid {label}: use 1-80 ASCII letters, digits, _ or -")
    return value


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def create_run_directory(root: Path, run_id: str) -> Path:
    validate_id(run_id, "run_id")
    run_dir = root.resolve() / run_id
    run_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    if run_dir.is_symlink():
        raise ValueError("run directory must not be a symlink")
    try:
        run_dir.chmod(0o700)
    except OSError:
        pass
    return run_dir


def append_event(run_dir: Path, run_id: str, stage: str, event_type: str,
                 *, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    validate_id(run_id, "run_id")
    validate_id(stage, "stage")
    if event_type not in EVENT_TYPES:
        raise ValueError("unknown event type")
    # Metadata must be strictly structured and bounded: no free-form log lines.
    metadata = metadata or {}
    if any(not isinstance(k, str) or not _ID.fullmatch(k) for k in metadata):
        raise ValueError("invalid metadata key")
    event = {
        "schema_version": 1,
        "run_id": run_id,
        "stage": stage,
        "event_type": event_type,
        "timestamp_utc": utc_now(),
        "metadata": metadata,
    }
    line = json.dumps(event, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    if len(line) > 8192:
        raise ValueError("journal event too large")
    path = run_dir / "events.jsonl"
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    try:
        os.write(descriptor, (line + "\n").encode("utf-8"))
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    return event


def read_events(run_dir: Path, *, run_id: str | None = None) -> list[dict[str, Any]]:
    path = run_dir / "events.jsonl"
    if not path.is_file():
        return []
    events: list[dict[str, Any]] = []
    for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        item = json.loads(line)
        if not isinstance(item, dict) or item.get("schema_version") != 1:
            raise ValueError(f"invalid journal event at line {index}")
        if run_id is not None and item.get("run_id") != run_id:
            raise ValueError(f"foreign run_id at line {index}")
        if item.get("event_type") not in EVENT_TYPES:
            raise ValueError(f"unknown journal event at line {index}")
        events.append(item)
    return events


def write_json_atomically(path: Path, document: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    encoded = (json.dumps(document, indent=2, sort_keys=True) + "\n").encode("utf-8")
    temp = path.with_name(path.name + ".tmp-" + str(os.getpid()))
    fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(encoded)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def record_model_usage(run_dir: Path, run_id: str, stage: str, *,
                       provider: str, model: str, input_tokens: int,
                       output_tokens: int, elapsed_ms: int) -> dict[str, Any]:
    """Record aggregate provider usage without prompts, responses or keys.

    Call explicitly from a model integration when actual usage is returned.
    This helper does not infer charges or instrument existing adapters.
    """
    if any(v < 0 for v in (input_tokens, output_tokens, elapsed_ms)):
        raise ValueError("usage counts must be nonnegative")
    if not provider or not model or len(provider) > 40 or len(model) > 100:
        raise ValueError("invalid provider/model")
    if not all(c.isalnum() or c in "-._" for c in provider + model):
        raise ValueError("provider/model contains unsupported characters")
    return append_event(run_dir, run_id, stage, "MODEL_USAGE", metadata={
        "provider": provider, "model": model,
        "input_tokens": input_tokens, "output_tokens": output_tokens,
        "elapsed_ms": elapsed_ms,
    })
