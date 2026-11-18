"""Build verified-claim cards for fetched full texts with a local model (resumable)."""

import argparse
import json
import sys
import time
from pathlib import Path

from thesis_factory.artifacts.fetching import ArtifactFormat, FetchedArtifact
from thesis_factory.domain.source_text import SourceTextLocation, SourceTextLocationKind
from thesis_factory.integrations.ollama.client import OllamaStructuredReasoner
from thesis_factory.parsing.grobid import GrobidTeiParser
from thesis_factory.reading.cards import build_card


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fulltext", type=Path, default=Path(".thesis-corpus/fulltext"))
    parser.add_argument("--out", type=Path, default=Path(".thesis-corpus/cards"))
    parser.add_argument("--model", default="qwen3:8b")
    parser.add_argument("--num-ctx", type=int, default=8192)
    parser.add_argument("--max-chars", type=int, default=6000, help="paragraph text per model call")
    parser.add_argument("--limit", type=int, default=1_000_000)
    parser.add_argument("--pause", type=float, default=0.0, help="seconds idle between papers")
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    index = json.loads((args.fulltext / "index.json").read_text(encoding="utf-8"))
    reasoner = OllamaStructuredReasoner(model=args.model, num_ctx=args.num_ctx)
    done = 0

    for paper_id, entry in index.items():
        card_path = args.out / f"{paper_id}.json"
        if entry.get("status") != "fetched" or card_path.exists():
            continue
        if done >= args.limit:
            break

        content = (args.fulltext / f"{entry['sha256']}.tei.xml").read_bytes()
        artifact = FetchedArtifact(
            location=SourceTextLocation(
                kind=SourceTextLocationKind.OPENALEX_GROBID_XML,
                url=entry["grobid_url"],
                provider="openalex",
                provider_work_id=entry["work_id"],
                is_open_access=True,
            ),
            format=ArtifactFormat.GROBID_XML,
            content=content,
            sha256=entry["sha256"],
            content_length=len(content),
        )

        started = time.monotonic()
        try:
            document = GrobidTeiParser().parse(artifact)
        except ValueError as error:
            print(f"parse failed {paper_id}: {error}", file=sys.stderr, flush=True)
            continue

        card = build_card(
            reasoner, document, paper_id=paper_id,
            artifact_sha256=entry["sha256"], max_chars=args.max_chars,
        )
        card["model"] = f"ollama:{args.model}"
        card["seconds"] = round(time.monotonic() - started, 1)
        tmp = card_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(card, indent=1, ensure_ascii=False), encoding="utf-8")
        tmp.replace(card_path)
        done += 1
        print(f"{done} {paper_id} {card['stats']} {card['seconds']}s", flush=True)
        time.sleep(args.pause)

    return 0


if __name__ == "__main__":
    sys.exit(main())
