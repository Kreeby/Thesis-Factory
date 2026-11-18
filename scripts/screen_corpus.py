import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path

from thesis_factory.corpus.build import SPECTER_V2
from thesis_factory.corpus.screening import needs_screening, policy_included, priority_plan
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
    parser.add_argument("--pause", type=float, default=0.0, help="seconds idle between papers (cooler, quieter)")
    parser.add_argument("--priority-plan", type=Path, help="screen in predicted-relevance order; write/reuse the plan here")
    parser.add_argument("--top-fraction", type=float, default=0.4)
    parser.add_argument("--audit", type=int, default=300, help="random tail papers screened to measure the cut")
    parser.add_argument("--title-only", action="store_true", help="screen no-abstract papers by title (recall-first)")
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
        )

        if args.title_only:
            # Papers the abstract screen could not judge; verdicts kept under a separate model key.
            screened = store.screenings(topic, model_id)
            done_ids = set(store.screenings(topic, f"{model_id}:title-only"))
            pending = [
                paper
                for paper in store.papers()
                if screened.get(paper["paper_id"]) == "INSUFFICIENT_EVIDENCE"
                and paper["paper_id"] not in done_ids
            ]

        if args.priority_plan and not args.title_only:
            # Reuse a saved plan on restart so the order and audit sample stay fixed.
            if args.priority_plan.exists():
                plan = json.loads(args.priority_plan.read_text(encoding="utf-8"))
            else:
                plan = priority_plan(
                    store, pending, topic=topic, model=model_id,
                    embedding_model=SPECTER_V2,
                    top_fraction=args.top_fraction, audit_size=args.audit,
                )
                args.priority_plan.write_text(json.dumps(plan, indent=1), encoding="utf-8")
            by_id = {paper["paper_id"]: paper for paper in pending}
            pending = [
                by_id[paper_id]
                for group in ("no_abstract", "no_embedding", "top", "audit")
                for paper_id in plan["groups"][group]
                if paper_id in by_id
            ]
            print(f"priority plan: cv AUC {plan['cv_auc']}, cv recall {plan['cv_recall_at_top_fraction']}, "
                  f"{len(pending)} to screen, {plan['tail_unscreened']} tail left unscreened", flush=True)

        pending = pending[:args.limit]
        statuses = Counter()

        for done, paper in enumerate(pending, start=1):
            source = SourceRecord(
                title=paper["title"],
                abstract=paper["abstract"],
                provider="semantic_scholar",
                provider_id=paper["paper_id"],
            )

            try:
                result = (
                    agent.assess_title_only(topic=topic, title=paper["title"])
                    if args.title_only
                    else agent.assess(topic=topic, source=source)
                )
            except Exception as error:  # one bad response must not stop a long run
                print(f"error {paper['paper_id']}: {error}", file=sys.stderr)
                continue

            store.put_screening(
                paper["paper_id"],
                topic=topic,
                model=f"{model_id}:title-only" if args.title_only else model_id,
                status=result.status,
                rationale=result.rationale,
            )
            statuses[result.status] += 1

            # Papers without an abstract are decided without an LLM call; no need to cool down.
            if args.title_only or (paper["abstract"] or "").strip():
                time.sleep(args.pause)

            if done % 50 == 0:
                print(f"{done}/{len(pending)} {dict(statuses)}", flush=True)

        included, unscreened, rescued = policy_included(store, config, model=model_id)
        print(f"screened this run {sum(statuses.values())}: {dict(statuses)}")
        print(f"included {len(included)} (citation-rescued {len(rescued)}), broad-only still unscreened {len(unscreened)}")
    finally:
        store.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
