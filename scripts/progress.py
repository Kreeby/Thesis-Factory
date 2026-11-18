"""Print corpus pipeline progress as JSON (read-only; used by the progress pane)."""

import json
import os
import sqlite3
import time
import sys
from pathlib import Path

from thesis_factory.corpus.screening import needs_screening

DB = Path(".thesis-corpus/corpus.sqlite")
CONFIG = Path("config/corpus/credit_xai.json")
TASKS = Path(".thesis-runs/tasks")
PLAN = Path(".thesis-corpus/screening_priority_plan.json")
RESCUED = Path(".thesis-corpus/rescued.json")  # written by map_corpus.py --included


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def tracked_tasks() -> list[dict]:
    """Tasks started via scripts/track.py; a dead 'running' task reads as stopped."""

    tasks = []
    for path in sorted(TASKS.glob("*.json")) if TASKS.exists() else []:
        task = json.loads(path.read_text(encoding="utf-8"))
        if task["status"] == "running" and not _alive(task["pid"]):
            task["status"] = "stopped"
        end = task.get("ended") or time.time()
        tasks.append({"name": task["name"], "status": task["status"], "elapsed_s": int(end - task["started"])})
    return tasks


def main() -> int:
    if not DB.exists():
        print(json.dumps({"stages": [], "tasks": tracked_tasks()}))
        return 0

    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    broad = set(config["broad_queries"])
    # Read-only connection so polling never contends with writers.
    db = sqlite3.connect(f"file:{DB}?mode=ro", uri=True, timeout=5)
    count = lambda sql: db.execute(sql).fetchone()[0]

    papers = count("SELECT COUNT(*) FROM papers")
    hits: dict[str, set[str]] = {}
    for query, paper_id in db.execute("SELECT query, paper_id FROM query_hits"):
        hits.setdefault(paper_id, set()).add(query)
    broad_only = {p for p, qs in hits.items() if needs_screening(qs, broad)}
    verdicts = dict(db.execute(
        "SELECT paper_id, status FROM screenings WHERE topic = ?",
        (config["screening_topic"],),
    ).fetchall())
    screened = set(verdicts)
    broad_verdicts = [verdicts[p] for p in broad_only & screened]
    screening = [{"name": "Screening (qwen3, broad-only)", "done": len(broad_only & screened), "total": len(broad_only)}]
    tail_left = None

    if PLAN.exists():
        groups = json.loads(PLAN.read_text(encoding="utf-8"))["groups"]
        top = set(groups["no_abstract"]) | set(groups["no_embedding"]) | set(groups["top"])
        audit = set(groups["audit"])
        planned = top | audit
        screening = [
            {"name": "Screening: top-ranked", "done": len(top & screened), "total": len(top)},
            {"name": "Screening: tail audit", "done": len(audit & screened), "total": len(audit)},
        ]
        tail_left = len(broad_only - screened - planned)

    print(json.dumps({
        "stages": [
            {"name": "Embeddings (SPECTER2)", "done": count("SELECT COUNT(*) FROM embeddings"), "total": papers},
            {"name": "Citation graph", "done": count("SELECT COUNT(*) FROM references_fetched"), "total": papers},
            *screening,
        ],
        "tasks": tracked_tasks(),
        "facts": {
            "papers": papers,
            "citation_edges": count("SELECT COUNT(*) FROM citations"),
            "core_kept": len(hits) - len(broad_only),
            "broad_relevant": broad_verdicts.count("RELEVANT"),
            "broad_kept": sum(v != "NOT_RELEVANT" for v in broad_verdicts),
            "broad_dropped": broad_verdicts.count("NOT_RELEVANT"),
            **({"tail_unscreened": tail_left} if tail_left is not None else {}),
            **({"citation_rescued": len(json.loads(RESCUED.read_text(encoding="utf-8")))} if RESCUED.exists() else {}),
        },
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
