"""Bounded subprocess stage executor with append-only local journaling.

Importable runtime logic is separate from its CLI so tests do not depend on
repository-root package import resolution.
"""

import os
import signal
import subprocess
import time
from pathlib import Path

from thesis_factory.runtime.journal import (
    append_event, create_run_directory, read_events, validate_id,
)


def _git_sha() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "UNKNOWN"


def _next_attempt(run_dir: Path, stage: str) -> int:
    return sum(
        item["event_type"] == "STAGE_STARTED" and item["stage"] == stage
        for item in read_events(run_dir)
    ) + 1


def _terminate_group(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=3)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait()


def run_stage(*, run_root: Path, run_id: str, stage: str,
              command: list[str], timeout_sec: int) -> int:
    validate_id(run_id, "run_id")
    validate_id(stage, "stage")
    if not command:
        raise ValueError("stage command required")
    if timeout_sec < 1 or timeout_sec > 36000:
        raise ValueError("timeout_sec must be between 1 and 36000")
    run_dir = create_run_directory(run_root, run_id)
    attempt = _next_attempt(run_dir, stage)
    step_dir = run_dir / "steps" / f"{stage}-{attempt:04d}"
    step_dir.mkdir(parents=True, exist_ok=False, mode=0o700)
    stdout_path, stderr_path = step_dir / "stdout.log", step_dir / "stderr.log"
    # Secrets may appear in subprocess output: logs are private and gitignored.
    append_event(run_dir, run_id, stage, "STAGE_STARTED", metadata={
        "attempt": attempt, "git_sha": _git_sha(), "timeout_sec": timeout_sec,
    })
    started = time.monotonic()
    status, exit_code = "STAGE_FAILED", 1
    with stdout_path.open("wb") as out, stderr_path.open("wb") as err:
        stdout_path.chmod(0o600)
        stderr_path.chmod(0o600)
        process = None
        try:
            process = subprocess.Popen(command, stdout=out, stderr=err,
                                       start_new_session=True)
            try:
                exit_code = process.wait(timeout=timeout_sec)
                status = "STAGE_COMPLETED" if exit_code == 0 else "STAGE_FAILED"
            except subprocess.TimeoutExpired:
                _terminate_group(process)
                status, exit_code = "STAGE_TIMED_OUT", 124
        except BaseException:
            if process is not None:
                _terminate_group(process)
            status, exit_code = "STAGE_FAILED", 1
            raise
        finally:
            append_event(run_dir, run_id, stage, status, metadata={
                "attempt": attempt,
                "exit_code": exit_code,
                "elapsed_ms": round((time.monotonic() - started) * 1000),
            })
    print(f"{stage}: {status} (exit={exit_code}); logs: {step_dir}")
    return exit_code
