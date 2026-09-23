import json
import os
from pathlib import Path

import httpx

from thesis_factory.artifacts.fetching import (
    ArtifactFetcher,
    select_preferred_text_location,
)
from thesis_factory.domain.source import (
    SourceRecord,
)
from thesis_factory.integrations.openalex.client import (
    OpenAlexClient,
)
from thesis_factory.parsing.grobid import (
    GrobidTeiParser,
)
from thesis_factory.retrieval.bm25 import (
    BM25Retriever,
)
from thesis_factory.retrieval.corpus import (
    build_retrieval_corpus,
)
from thesis_factory.retrieval.evaluation import (
    RetrievalEvalCase,
    RetrievalEvalMetrics,
    RetrievalEvalScope,
    RetrievalQueryStyle,
    evaluate_retriever,
    summarize_eval_results,
)


ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

BENCHMARK_PATH = (
        ROOT
        / "evals"
        / "retrieval"
        / "baseline_v2.json"
)


def print_metrics(
        label: str,
        metrics: RetrievalEvalMetrics,
) -> None:
    print(label)

    print(
        "  CASES:",
        metrics.case_count,
    )

    print(
        "  HIT@5:",
        f"{metrics.hit_rate_at_k:.4f}",
    )

    print(
        "  COMPLETE@5:",
        f"{metrics.complete_rate_at_k:.4f}",
    )

    print(
        "  TARGET COVERAGE@5:",
        (
            f"{metrics.mean_target_coverage_at_k:.4f}"
        ),
    )

    print(
        "  MRR:",
        f"{metrics.mean_reciprocal_rank:.4f}",
    )


def main() -> None:
    api_key = os.environ[
        "OPENALEX_API_KEY"
    ]

    raw = json.loads(
        BENCHMARK_PATH.read_text(
            encoding="utf-8"
        )
    )

    top_k = int(
        raw["top_k"]
    )

    cases = tuple(
        RetrievalEvalCase.model_validate(
            case
        )
        for case in raw["cases"]
    )

    openalex = OpenAlexClient(
        api_key=api_key,
    )

    content_client = httpx.Client(
        timeout=30.0,
        follow_redirects=True,
        params={
            "api_key": api_key,
        },
    )

    fetcher = ArtifactFetcher(
        http_client=content_client,
    )

    try:
        documents = []

        print("=" * 100)
        print(
            "RETRIEVAL BENCHMARK:",
            raw["name"],
        )

        for spec in raw["documents"]:
            source = SourceRecord(
                title=spec["title"],
                doi=spec["doi"],
                provider=spec["provider"],
                provider_id=(
                    spec["provider_id"]
                ),
            )

            locations = (
                openalex.get_text_locations(
                    source
                )
            )

            preferred = (
                select_preferred_text_location(
                    locations
                )
            )

            if preferred is None:
                raise RuntimeError(
                    "No downloadable full text "
                    f"for {source.title}"
                )

            artifact = fetcher.fetch(
                preferred
            )

            expected_hash = (
                spec[
                    "expected_artifact_sha256"
                ]
            )

            if (
                    artifact.sha256
                    != expected_hash
            ):
                raise RuntimeError(
                    "benchmark artifact changed "
                    f"for {source.provider_id}: "
                    f"expected {expected_hash}, "
                    f"got {artifact.sha256}"
                )

            document = (
                GrobidTeiParser()
                .parse(
                    artifact
                )
            )

            documents.append(
                document
            )

            print()
            print(
                "DOCUMENT:",
                document.title,
            )
            print(
                "ARTIFACT:",
                document.artifact_sha256,
            )

        corpus = build_retrieval_corpus(
            tuple(documents)
        )

        corpus_by_id = {
            unit.identity: unit
            for unit in corpus
        }

        corpus_ids = set(
            corpus_by_id
        )

        for case in cases:
            for target in case.targets:
                missing = (
                        set(
                            target.acceptable_units
                        )
                        - corpus_ids
                )

                if missing:
                    raise RuntimeError(
                        "benchmark contains "
                        "missing retrieval units "
                        f"for case {case.id}, "
                        f"target {target.id}: "
                        f"{missing}"
                    )

        retriever = BM25Retriever(
            corpus
        )

        report = evaluate_retriever(
            retriever,
            cases,
            top_k=top_k,
        )

        print()
        print("=" * 100)
        print("OVERALL")
        print_metrics(
            "BM25",
            report.overall,
        )

        print()
        print("=" * 100)
        print("BY QUERY STYLE")

        for style in RetrievalQueryStyle:
            results = tuple(
                result
                for result in report.results
                if (
                        result.query_style
                        == style
                )
            )

            if not results:
                continue

            print_metrics(
                style.value,
                summarize_eval_results(
                    results
                ),
            )

        print()
        print("=" * 100)
        print("BY SCOPE")

        for scope in RetrievalEvalScope:
            results = tuple(
                result
                for result in report.results
                if (
                        result.scope
                        == scope
                )
            )

            if not results:
                continue

            print_metrics(
                scope.value,
                summarize_eval_results(
                    results
                ),
            )

        cases_by_id = {
            case.id: case
            for case in cases
        }

        print()
        print("=" * 100)
        print("CASE DETAILS")

        for result in report.results:
            case = cases_by_id[
                result.case_id
            ]

            acceptable_units = set(
                unit
                for target in case.targets
                for unit
                in target.acceptable_units
            )

            print()
            print("-" * 100)

            print(
                "CASE:",
                result.case_id,
            )

            print(
                "STYLE:",
                result.query_style.value,
            )

            print(
                "SCOPE:",
                result.scope.value,
            )

            print(
                "QUERY:",
                result.query,
            )

            print(
                "HIT:",
                result.hit_at_k,
            )

            print(
                "COMPLETE:",
                result.complete_at_k,
            )

            print(
                "TARGET COVERAGE:",
                (
                    f"{result.target_coverage_at_k:.4f}"
                ),
            )

            print(
                "SATISFIED TARGETS:",
                (
                        ", ".join(
                            result.satisfied_target_ids
                        )
                        or "-"
                ),
            )

            print(
                "RR:",
                f"{result.reciprocal_rank:.4f}",
            )

            print("TOP RESULTS:")

            for rank, unit_id in enumerate(
                    result.retrieved_units,
                    start=1,
            ):
                unit = corpus_by_id[
                    unit_id
                ]

                marker = (
                    "*"
                    if unit_id
                       in acceptable_units
                    else " "
                )

                print(
                    f"  {marker} #{rank}",
                    unit.source_provider_id,
                    f"P{unit.paragraph_ordinal}",
                    " > ".join(
                        unit.section_path
                    ),
                )

        print()
        print("=" * 100)
        print(
            "* = acceptable evidence anchor "
            "for at least one target"
        )

    finally:
        openalex.close()
        content_client.close()


if __name__ == "__main__":
    main()