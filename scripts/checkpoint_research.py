"""Make a local content-addressed proposal research checkpoint; no API calls.

Specify --artifact ROLE=PATH for each source JSON. See README in runbook.
"""

import argparse
import sys
from pathlib import Path

from thesis_factory.runtime.checkpoint import ROLES, create_research_checkpoint


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run-id", required=True)
    p.add_argument("--run-root", type=Path, default=Path(".thesis-runs"))
    p.add_argument("--artifact", action="append", required=True,
                   metavar="ROLE=PATH", help="one of: " + ", ".join(ROLES))
    args = p.parse_args()
    selected = {}
    for item in args.artifact:
        role, sep, path = item.partition("=")
        if not sep or role not in ROLES or not path or role in selected:
            p.error("expected unique ROLE=PATH; valid roles: " + ", ".join(ROLES))
        selected[role] = Path(path)
    result = create_research_checkpoint(root=args.run_root,
                                        run_id=args.run_id, artifacts=selected)
    print("Checkpoint created:", args.run_id)
    print("Validation:", result["validation"])
    print("Artifact SHA-256:")
    for role, entry in result["artifacts"].items():
        print(f"  {role}: {entry['sha256']}")
    print("Evidence summary:", result["research_summary"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
