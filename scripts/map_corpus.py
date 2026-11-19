import argparse
import json
import sys
from pathlib import Path

from thesis_factory.corpus.field_map import build_field_map, render_markdown
from thesis_factory.corpus.screening import policy_included
from thesis_factory.corpus.store import CorpusStore


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic field map of the corpus.")
    parser.add_argument("--db", type=Path, default=Path(".thesis-corpus/corpus.sqlite"))
    parser.add_argument("--out", type=Path, default=Path(".thesis-corpus/field_map"))
    parser.add_argument("--clusters", type=int)
    parser.add_argument("--included", type=Path, metavar="QUERIES_JSON", help="map only papers the screening policy includes")
    parser.add_argument("--model", default="qwen3:8b")
    args = parser.parse_args()

    store = CorpusStore(args.db)

    try:
        only = None

        if args.included:
            config = json.loads(args.included.read_text(encoding="utf-8"))
            only, _, rescued = policy_included(store, config, model=f"ollama:{args.model}")
            # Kept for the progress pane; the rule is in policy_included().
            args.out.with_name("rescued.json").write_text(json.dumps(sorted(rescued)), encoding="utf-8")

        field_map = build_field_map(store, clusters=args.clusters, only=only)
    finally:
        store.close()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.with_suffix(".json").write_text(json.dumps(field_map, indent=2), encoding="utf-8")
    args.out.with_suffix(".md").write_text(render_markdown(field_map), encoding="utf-8")
    print(f"{field_map['papers_mapped']} papers, {len(field_map['clusters'])} clusters -> {args.out}.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
