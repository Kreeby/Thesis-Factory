import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from thesis_factory.corpus.screening import included_papers, needs_screening
from thesis_factory.corpus.store import CorpusStore
from thesis_factory.domain.source import SourceRecord
from thesis_factory.integrations.ollama.client import OllamaStructuredReasoner
from thesis_factory.research.relevance import RelevanceAgent


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Screen broad-query-only papers with a local model (resumable).",
    )
    parser.add_argument("--db", type=Path, default=Path(".thesis-corpus/corpus.sqlite"))
    parser.add_argument("--queries", type=Path, required=True)
    parser.add_argument("--model", default="qwen3:8b")
    parser.add_argument("--limit", type=int, required=True, help="max papers this run")
    args = parser.parse_args()

    config = json.loads(args.queries.read_text(encoding="utf-8"))
    topic = config["screening_topic"]
    broad = set(config["broad_queries"])
    model_id = f"ollama:{args.model}"

    store = CorpusStore(args.db)
    agent = RelevanceAgent(OllamaStructuredReasoner(model=args.model))

    try:
        hits = store.paper_queries()
        pending = sorted(
            (
                paper
                for paper in store.unscreened_papers(topic, model_id)
                if needs_screening(hits.get(paper["paper_id"], set()), broad)
            ),
            key=lambda p: (-(p["citation_count"] or 0), p["paper_id"]),
        )[:args.limit]
        statuses = Counter()

        for done, paper in enumerate(pending, start=1):
            source = SourceRecord(
                title=paper["title"],
                abstract=paper["abstract"],
                provider="semantic_scholar",
                provider_id=paper["paper_id"],
            )

            try:
                result = agent.assess(topic=topic, source=source)
            except Exception as error:  # one bad response must not stop a long run
                print(f"error {paper['paper_id']}: {error}", file=sys.stderr)
                continue

            store.put_screening(
                paper["paper_id"],
                topic=topic,
                model=model_id,
                status=result.status,
                rationale=result.rationale,
            )
            statuses[result.status] += 1

            if done % 50 == 0:
                print(f"{done}/{len(pending)} {dict(statuses)}", flush=True)

        included, unscreened = included_papers(
            store, broad_queries=broad, topic=topic, model=model_id,
        )
        print(f"screened this run {sum(statuses.values())}: {dict(statuses)}")
        print(f"included {len(included)}, broad-only still unscreened {len(unscreened)}")
    finally:
        store.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
