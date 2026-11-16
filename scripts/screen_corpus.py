import argparse
import sys
from collections import Counter
from pathlib import Path

from thesis_factory.corpus.store import CorpusStore
from thesis_factory.domain.source import SourceRecord
from thesis_factory.integrations.ollama.client import OllamaStructuredReasoner
from thesis_factory.research.relevance import RelevanceAgent


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Screen corpus abstracts with a local model (resumable).",
    )
    parser.add_argument("--db", type=Path, default=Path(".thesis-corpus/corpus.sqlite"))
    parser.add_argument("--topic", required=True)
    parser.add_argument("--model", default="qwen3:8b")
    parser.add_argument("--limit", type=int, required=True, help="max papers this run")
    args = parser.parse_args()

    store = CorpusStore(args.db)
    agent = RelevanceAgent(OllamaStructuredReasoner(model=args.model))
    model_id = f"ollama:{args.model}"

    try:
        pending = sorted(
            store.unscreened_papers(args.topic, model_id),
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
                result = agent.assess(topic=args.topic, source=source)
            except Exception as error:  # one bad response must not stop a long run
                print(f"error {paper['paper_id']}: {error}", file=sys.stderr)
                continue

            store.put_screening(
                paper["paper_id"],
                topic=args.topic,
                model=model_id,
                status=result.status,
                rationale=result.rationale,
            )
            statuses[result.status] += 1

            if done % 50 == 0:
                print(f"{done}/{len(pending)} {dict(statuses)}", flush=True)

        print(f"screened {sum(statuses.values())}: {dict(statuses)}")
    finally:
        store.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
