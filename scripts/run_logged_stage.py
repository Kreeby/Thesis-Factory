"""Run an existing CLI as a bounded, locally logged thesis stage.

Example: ./scripts/uv run python scripts/run_logged_stage.py --run-id r001
    --stage discovery --timeout-sec 1800 -- ./scripts/uv run python ...
"""

import argparse
import sys
from pathlib import Path

from thesis_factory.runtime.stage import run_stage


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--stage", required=True)
    parser.add_argument("--run-root", type=Path, default=Path(".thesis-runs"))
    parser.add_argument("--timeout-sec", type=int, default=1800)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    return run_stage(run_root=args.run_root, run_id=args.run_id,
                     stage=args.stage, command=command, timeout_sec=args.timeout_sec)


if __name__ == "__main__":
    sys.exit(main())
