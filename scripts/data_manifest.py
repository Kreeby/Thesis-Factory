"""Hash manifest of the local, gitignored research data in .thesis-corpus/ (for copying between machines).

Usage:
  ./scripts/uv run python scripts/data_manifest.py --write docs/runbooks/data-manifest.json
  ./scripts/uv run python scripts/data_manifest.py --check docs/runbooks/data-manifest.json
Directory entries use one combined hash: sha256 over sorted lines "<relative path> <file sha256>".
"""

import argparse
import hashlib
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(".thesis-corpus")
FILES = ["corpus.sqlite", "reading_priority.json", "fulltext/index.json", "gaps/review.json",
         "gaps/refutation_verdicts.json", "gaps/open_question_clusters.json"]
DIRS = ["cards", "fulltext", "gaps", "datasets"]


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def tree(d):
    files = sorted(p for p in (ROOT / d).rglob("*") if p.is_file())
    h = hashlib.sha256()
    for p in files:
        h.update(f"{p.relative_to(ROOT).as_posix()} {sha(p)}\n".encode())
    return {"files": len(files), "bytes": sum(p.stat().st_size for p in files), "combined_sha256": h.hexdigest()}


def build():
    return {"generated": date.today().isoformat(),
            "single_files": {p: {"bytes": (ROOT / p).stat().st_size, "sha256": sha(ROOT / p)}
                             for p in FILES if (ROOT / p).exists()},
            "directories": {d: tree(d) for d in DIRS if (ROOT / d).exists()}}


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--write", type=Path)
    g.add_argument("--check", type=Path)
    a = ap.parse_args()
    now = build()
    if a.write:
        a.write.write_text(json.dumps(now, indent=1) + "\n", encoding="utf-8")
        print(f"wrote {a.write}")
        return 0
    ref = json.loads(a.check.read_text(encoding="utf-8"))
    bad = 0
    for kind in ("single_files", "directories"):
        for name, want in ref[kind].items():
            got = now[kind].get(name)
            ok = got is not None and all(got[k] == v for k, v in want.items())
            bad += not ok
            print(("OK   " if ok else "DIFF ") + f"{'file' if kind == 'single_files' else 'dir '} {name}" + ("" if ok else f"  expected {want}, got {got}"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
