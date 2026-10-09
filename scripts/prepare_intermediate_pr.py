"""Prepare an intermediary review PR (local by default; --create uses gh).

Does NOT stage, commit, push or merge anything. --create requires that the
working branch exists on origin and that an authorized gh user is logged in.
"""

import argparse
import subprocess
import sys
from pathlib import Path

from thesis_factory.runtime.journal import append_event
from thesis_factory.runtime.pr_checkpoint import prepare_pr_body


def _git(*args: str) -> str:
    value = subprocess.run(["git", *args], check=True, capture_output=True, text=True)
    return value.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--stage", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--run-root", type=Path, default=Path(".thesis-runs"))
    parser.add_argument("--base", default="main")
    parser.add_argument("--create", action="store_true", help="explicitly call gh pr create")
    args = parser.parse_args()
    sha = _git("rev-parse", "HEAD")
    head = _git("branch", "--show-current")
    if not head or head in {"main", args.base}:
        parser.error("must be on a dedicated feature branch")
    body, safe = prepare_pr_body(root=args.run_root, run_id=args.run_id,
                                 title=args.title, stage=args.stage, git_sha=sha)
    print("Prepared local PR body:", body)
    if not args.create:
        print("Dry run. To open a PR, push the branch and repeat with --create.")
        return 0
    if not safe:
        parser.error("failed/timed-out stages need human review before PR creation")
    if _git("status", "--porcelain"):
        parser.error("working tree must be clean before creating PR")
    # GitHub CLI owns credentials; never copy tokens to the journal.
    result = subprocess.run([
        "gh", "pr", "create", "--base", args.base, "--head", head,
        "--title", args.title, "--body-file", str(body),
    ], capture_output=True, text=True, check=False)
    if result.returncode != 0:
        print("gh pr create failed; check gh authentication and pushed branch", file=sys.stderr)
        return result.returncode
    append_event(args.run_root / args.run_id, args.run_id, args.stage,
                 "PR_CREATED", metadata={"git_sha": sha, "head": head})
    print(result.stdout.strip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
