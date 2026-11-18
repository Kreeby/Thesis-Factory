"""Deterministic candidate pool for deep reading, grouped by thesis facet.

Ranks included papers by how often other included papers cite them, within
facets defined by title patterns. The pool is reviewed by the orchestrator,
who selects the reading list; this script makes no relevance judgement.
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

from thesis_factory.corpus.screening import policy_included
from thesis_factory.corpus.store import CorpusStore

CREDIT = r"\b(credit|loans?|lending|lenders?|borrowers?|mortgages?|default prediction|scorecards?)\b"
XAI = r"(explainab|interpretab|\bXAI\b|\bSHAP\b|Shapley|\bLIME\b|counterfactual|recourse|explanation|attribution|saliency)"
LEGAL = r"(GDPR|right to (an )?explanation|AI Act|Artificial Intelligence Act|regulat|\blaw\b|legal|profiling|Article 22|automated decision|ECOA|Equal Credit|consumer protection|accountab|transparen)"
FAIR = r"(fair|discriminat|\bbias|disparate|redlining)"

# Facet: (title must match all patterns, max candidates). Order sets dedupe priority.
FACETS = {
    "xai_credit": ([CREDIT, XAI], None),
    "legal": ([LEGAL], 150),
    "fairness_lending": ([FAIR, CREDIT], 120),
    "xai_methods": ([XAI], 200),
    "credit_ml": ([CREDIT], 150),
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=Path(".thesis-corpus/corpus.sqlite"))
    parser.add_argument("--queries", type=Path, default=Path("config/corpus/credit_xai.json"))
    parser.add_argument("--model", default="qwen3:8b")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    config = json.loads(args.queries.read_text(encoding="utf-8"))
    store = CorpusStore(args.db)

    try:
        included, _, _ = policy_included(store, config, model=f"ollama:{args.model}")
        cited = Counter(b for a, b in store.citations() if a in included and b in included)
        papers = {p["paper_id"]: p for p in store.papers() if p["paper_id"] in included}
    finally:
        store.close()

    taken: set[str] = set()
    pool = {}

    for facet, (patterns, limit) in FACETS.items():
        regexes = [re.compile(p, re.I) for p in patterns]
        ids = [
            pid for pid, paper in papers.items()
            if pid not in taken and all(r.search(paper["title"]) for r in regexes)
        ]
        ids.sort(key=lambda pid: (-cited[pid], -(papers[pid]["citation_count"] or 0), pid))
        ids = ids[:limit]
        taken.update(ids)
        pool[facet] = [
            {
                "paper_id": pid,
                "title": papers[pid]["title"],
                "year": papers[pid]["year"],
                "venue": papers[pid]["venue"],
                "doi": papers[pid]["doi"],
                "citations": papers[pid]["citation_count"],
                "cited_in_library": cited[pid],
                "has_abstract": bool((papers[pid]["abstract"] or "").strip()),
            }
            for pid in ids
        ]

    args.out.write_text(json.dumps(pool, indent=1, ensure_ascii=False), encoding="utf-8")
    print({facet: len(items) for facet, items in pool.items()})
    return 0


if __name__ == "__main__":
    sys.exit(main())
