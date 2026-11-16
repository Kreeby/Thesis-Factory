import argparse
import json
import os
import sys
from pathlib import Path

from thesis_factory.corpus.build import (
    collect_query,
    enrich_embeddings,
    enrich_references,
)
from thesis_factory.corpus.store import CorpusStore
from thesis_factory.integrations.semantic_scholar.client import (
    SemanticScholarClient,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build or resume the local Semantic Scholar corpus.",
    )
    parser.add_argument("--db", type=Path, default=Path(".thesis-corpus/corpus.sqlite"))
    parser.add_argument("--queries", type=Path, required=True)
    parser.add_argument("--max-per-query", type=int)
    parser.add_argument("--year", help="S2 year filter, e.g. 2015-")
    parser.add_argument("--embeddings", type=int, default=0, help="max papers to embed")
    parser.add_argument("--references", type=int, default=0, help="max papers to fetch references for")
    args = parser.parse_args()

    config = json.loads(args.queries.read_text(encoding="utf-8"))
    max_papers = args.max_per_query or config["max_papers_per_query"]

    client = SemanticScholarClient(api_key=os.environ.get("S2_API_KEY"))
    store = CorpusStore(args.db)

    try:
        for query in config["queries"]:
            collect_query(client, store, query, max_papers=max_papers, year=args.year)

        if args.embeddings:
            enrich_embeddings(client, store, limit=args.embeddings)

        if args.references:
            enrich_references(client, store, limit=args.references)

        print(json.dumps(store.counts(), indent=2))
    finally:
        store.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
