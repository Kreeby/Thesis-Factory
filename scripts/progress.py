"""Print corpus pipeline progress as JSON (read-only; used by the progress pane)."""

import json
import sqlite3
import sys
from pathlib import Path

from thesis_factory.corpus.screening import needs_screening

DB = Path(".thesis-corpus/corpus.sqlite")
CONFIG = Path("config/corpus/credit_xai.json")


def main() -> int:
    if not DB.exists():
        print(json.dumps({"stages": []}))
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
    screened = {
        p for (p,) in db.execute(
            "SELECT paper_id FROM screenings WHERE topic = ?",
            (config["screening_topic"],),
        )
    }

    print(json.dumps({
        "stages": [
            {"name": "Embeddings (SPECTER2)", "done": count("SELECT COUNT(*) FROM embeddings"), "total": papers},
            {"name": "Citation graph", "done": count("SELECT COUNT(*) FROM references_fetched"), "total": papers},
            {"name": "Screening (qwen3, broad-only)", "done": len(broad_only & screened), "total": len(broad_only)},
        ],
        "facts": {
            "papers": papers,
            "citation_edges": count("SELECT COUNT(*) FROM citations"),
        },
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
