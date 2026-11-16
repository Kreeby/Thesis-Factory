import argparse
import json
import sys
from pathlib import Path

from thesis_factory.corpus.field_map import build_field_map, render_markdown
from thesis_factory.corpus.store import CorpusStore


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic field map of the corpus.")
    parser.add_argument("--db", type=Path, default=Path(".thesis-corpus/corpus.sqlite"))
    parser.add_argument("--out", type=Path, default=Path(".thesis-corpus/field_map"))
    parser.add_argument("--clusters", type=int)
    args = parser.parse_args()

    store = CorpusStore(args.db)

    try:
        field_map = build_field_map(store, clusters=args.clusters)
    finally:
        store.close()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.with_suffix(".json").write_text(json.dumps(field_map, indent=2), encoding="utf-8")
    args.out.with_suffix(".md").write_text(render_markdown(field_map), encoding="utf-8")
    print(f"{field_map['papers_mapped']} papers, {len(field_map['clusters'])} clusters -> {args.out}.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
