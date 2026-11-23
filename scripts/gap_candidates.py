"""Stage 3: group verified OPEN_QUESTION claims from all cards into recurrence-ranked clusters.

Usage: ./scripts/uv run python scripts/gap_candidates.py [--distance 0.3]
Needs a local Ollama embedding model (default qwen3-embedding:0.6b). Embeddings are cached by
quote text, so re-running with another --distance does not re-embed.
Writes .thesis-corpus/gaps/open_question_clusters.json (input for review and refutation).
"""

import argparse
import json
import sys
from pathlib import Path

from thesis_factory.integrations.ollama.client import OllamaEmbedder
from thesis_factory.reading.gaps import build_clusters, cluster_vectors, collect_open_questions


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cards", type=Path, default=Path(".thesis-corpus/cards"))
    parser.add_argument("--out-dir", type=Path, default=Path(".thesis-corpus/gaps"))
    parser.add_argument("--model", default="qwen3-embedding:0.6b")
    parser.add_argument("--distance", type=float, default=0.3, help="cosine distance threshold (average linkage)")
    args = parser.parse_args()

    cards = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(args.cards.glob("*.json"))]
    items = collect_open_questions(cards)
    quotes = [i["quote"] for i in items]

    args.out_dir.mkdir(parents=True, exist_ok=True)
    cache_path = args.out_dir / f"embeddings-{args.model.replace(':', '_')}.json"
    cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
    missing = sorted({q for q in quotes if q not in cache})
    if missing:
        cache.update(zip(missing, OllamaEmbedder(model=args.model).embed(missing)))
        cache_path.write_text(json.dumps(cache), encoding="utf-8")

    clusters = build_clusters(items, cluster_vectors([cache[q] for q in quotes], args.distance))
    payload = {
        "method": f"{args.model} embeddings of verified quotes; agglomerative clustering, cosine, "
                  f"average linkage, distance threshold {args.distance}",
        "cards": len(cards), "open_questions": len(items), "clusters": clusters,
    }
    out = args.out_dir / "open_question_clusters.json"
    tmp = out.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, indent=1, ensure_ascii=False), encoding="utf-8")
    tmp.replace(out)

    recurring = [c for c in clusters if c["papers"] >= 3]
    print(f"{len(cards)} cards, {len(items)} open questions, {len(clusters)} clusters, {len(recurring)} in >=3 papers")
    for c in clusters[:25]:
        print(f"{c['id']} papers={c['papers']} claims={c['claims']} | {c['members'][0]['quote'][:110]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
