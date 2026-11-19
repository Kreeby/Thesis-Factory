"""Graded deep-reading priority (0-100) for every corpus paper, included or not.

Scores included papers, papers the screen dropped and unscreened tail papers on
one scale, so a high-scoring dropped paper shows where screening may have lost
good material. Discovery artifact, not evidence; no LLM calls.
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np

from reading_pool import FACETS
from thesis_factory.corpus.build import SPECTER_V2
from thesis_factory.corpus.priority import WEIGHTS, priority_scores
from thesis_factory.corpus.screening import policy_included
from thesis_factory.corpus.store import CorpusStore


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=Path(".thesis-corpus/corpus.sqlite"))
    parser.add_argument("--queries", type=Path, default=Path("config/corpus/credit_xai.json"))
    parser.add_argument("--model", default="qwen3:8b")
    parser.add_argument("--reading-list", type=Path, default=Path("config/reading/credit_xai_reading_list_v1.json"))
    parser.add_argument("--year", type=int, default=2026)
    parser.add_argument("--out", type=Path, default=Path(".thesis-corpus/reading_priority.json"))
    args = parser.parse_args()

    config = json.loads(args.queries.read_text(encoding="utf-8"))
    store = CorpusStore(args.db)

    try:
        included, unscreened, _ = policy_included(store, config, model=f"ollama:{args.model}")
        papers = {p["paper_id"]: p for p in store.papers()}
        vectors = {p: np.frombuffer(v, dtype=np.float32) for p, v in store.embeddings(SPECTER_V2)}
        cited = Counter(b for a, b in store.citations() if a in included)
    finally:
        store.close()

    facets = {
        name: {
            p for p in included
            if all(re.search(pattern, papers[p]["title"], re.I) for pattern in patterns)
        }
        for name, (patterns, _) in FACETS.items()
    }
    scores = priority_scores(
        vectors, facets, cited, {p: papers[p]["year"] for p in vectors}, current_year=args.year,
    )
    status = lambda p: "included" if p in included else "unscreened" if p in unscreened else "dropped"

    out = {
        "method": f"weights {WEIGHTS}; percentiles over {len(scores)} papers with SPECTER2 vectors",
        "papers": {
            p: {**s, "status": status(p), "title": papers[p]["title"], "year": papers[p]["year"]}
            for p, s in sorted(scores.items(), key=lambda kv: -kv[1]["score"])
        },
        "unscored_included": sorted(included - set(scores)),
    }
    args.out.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")

    rows = list(out["papers"].items())
    print(f"scored {len(rows)}; included without vector (unscored) {len(out['unscored_included'])}")
    for name in ("included", "dropped", "unscreened"):
        values = [s["score"] for _, s in rows if s["status"] == name]
        print(f"{name:10} n={len(values):6} deciles", [int(np.percentile(values, q)) for q in range(10, 100, 10)])

    reading = json.loads(args.reading_list.read_text(encoding="utf-8"))
    listed = {p["paper_id"] for f in reading["facets"].values() for p in f["papers"]}
    rank = {p: i for i, (p, _) in enumerate(rows)}
    print("reading list v1 rank percentiles", [
        int(np.percentile([rank[p] / len(rows) * 100 for p in listed if p in rank], q)) for q in (10, 50, 90)
    ])
    top = rows[:500]
    print("top 500: status", Counter(s["status"] for _, s in top), "years", sorted(Counter(
        (s["year"] or 0) // 5 * 5 for _, s in top).items()))
    print("top dropped papers:")
    for p, s in [r for r in rows if r[1]["status"] == "dropped"][:15]:
        print(f"  {s['score']:5} rel {s['relevance']:5} {s['year']} {s['title'][:90]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
