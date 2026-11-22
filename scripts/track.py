"""Run any command and publish its live status to the progress pane.

Usage: ./scripts/uv run python scripts/track.py --name "Codex labelling" -- <cmd...>
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

TASKS = Path(".thesis-runs/tasks")


def _write(path: Path, payload: dict) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload), encoding="utf-8")
    tmp.replace(path)  # atomic: the pane never reads a half-written file


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command

    if not command:
        parser.error("command is required after --")

    TASKS.mkdir(parents=True, exist_ok=True)
    path = TASKS / (re.sub(r"[^a-z0-9]+", "-", args.name.lower()).strip("-") + ".json")
    task = {"name": args.name, "status": "running", "started": time.time(), "pid": os.getpid()}
    _write(path, task)

    try:
        code = subprocess.call(command)
    except KeyboardInterrupt:
        code = 130

    _write(path, {**task, "status": "done" if code == 0 else f"failed ({code})", "ended": time.time()})
    return code


if __name__ == "__main__":
    sys.exit(main())
