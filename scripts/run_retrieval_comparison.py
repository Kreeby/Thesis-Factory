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
from thesis_factory.integrations.voyage.client import (
    VoyageEmbeddingClient,
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
from thesis_factory.retrieval.semantic import (
    SemanticRetriever,
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
        *,
        top_k: int,
) -> None:
    print(label)

    print(
        f"  HIT@{top_k}:",
        f"{metrics.hit_rate_at_k:.4f}",
    )

    print(
        f"  COMPLETE@{top_k}:",
        f"{metrics.complete_rate_at_k:.4f}",
    )

    print(
        f"  TARGET COVERAGE@{top_k}:",
        f"{metrics.mean_target_coverage_at_k:.4f}",
    )

    print(
        "  MRR:",
        f"{metrics.mean_reciprocal_rank:.4f}",
    )


def print_comparison(
        label: str,
        *,
        bm25: RetrievalEvalMetrics,
        semantic: RetrievalEvalMetrics,
        top_k: int,
) -> None:
    print(label)

    print(
        f"  {'METRIC':<24}"
        f"{'BM25':>10}"
        f"{'VOYAGE':>10}"
        f"{'DELTA':>10}"
    )

    rows = (
        (
            f"Hit@{top_k}",
            bm25.hit_rate_at_k,
            semantic.hit_rate_at_k,
        ),
        (
            f"Complete@{top_k}",
            bm25.complete_rate_at_k,
            semantic.complete_rate_at_k,
        ),
        (
            f"Target Coverage@{top_k}",
            bm25.mean_target_coverage_at_k,
            semantic.mean_target_coverage_at_k,
        ),
        (
            "MRR",
            bm25.mean_reciprocal_rank,
            semantic.mean_reciprocal_rank,
        ),
    )

    for (
            metric_name,
            bm25_value,
            semantic_value,
    ) in rows:
        delta = (
                semantic_value
                - bm25_value
        )

        print(
            f"  {metric_name:<24}"
            f"{bm25_value:>10.4f}"
            f"{semantic_value:>10.4f}"
            f"{delta:>+10.4f}"
        )


def subset_metrics(
        results,
        *,
        query_style=None,
        scope=None,
) -> RetrievalEvalMetrics:
    selected = tuple(
        result
        for result in results
        if (
                (
                        query_style is None
                        or result.query_style
                        == query_style
                )
                and (
                        scope is None
                        or result.scope
                        == scope
                )
        )
    )

    return summarize_eval_results(
        selected
    )


def load_documents(
        *,
        benchmark: dict,
        openalex_api_key: str,
) -> tuple:
    openalex = OpenAlexClient(
        api_key=openalex_api_key,
    )

    content_client = httpx.Client(
        timeout=30.0,
        follow_redirects=True,
        params={
            "api_key": openalex_api_key,
        },
    )

    fetcher = ArtifactFetcher(
        http_client=content_client,
    )

    try:
        documents = []

        for spec in benchmark[
            "documents"
        ]:
            source = SourceRecord(
                title=spec["title"],
                doi=spec["doi"],
                provider=spec["provider"],
                provider_id=(
                    spec["provider_id"]
                ),
            )

            locations = (
                openalex
                .get_text_locations(
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

            print(
                "DOCUMENT:",
                document.title,
            )

            print(
                "ARTIFACT:",
                document.artifact_sha256,
            )

            print()

        return tuple(
            documents
        )

    finally:
        openalex.close()
        content_client.close()


def validate_benchmark_units(
        cases,
        corpus,
) -> None:
    corpus_ids = {
        unit.identity
        for unit in corpus
    }

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


def print_case_comparison(
        *,
        cases,
        bm25_report,
        semantic_report,
        corpus,
) -> None:
    corpus_by_id = {
        unit.identity: unit
        for unit in corpus
    }

    bm25_by_case = {
        result.case_id: result
        for result
        in bm25_report.results
    }

    semantic_by_case = {
        result.case_id: result
        for result
        in semantic_report.results
    }

    print()
    print("=" * 100)
    print("CASE COMPARISON")

    for case in cases:
        bm25 = bm25_by_case[
            case.id
        ]

        semantic = semantic_by_case[
            case.id
        ]

        print()
        print("-" * 100)

        print(
            "CASE:",
            case.id,
        )

        print(
            "STYLE:",
            case.query_style.value,
        )

        print(
            "SCOPE:",
            case.scope.value,
        )

        print(
            "QUERY:",
            case.query,
        )

        print()

        print(
            "BM25:"
        )

        print(
            "  HIT:",
            bm25.hit_at_k,
        )

        print(
            "  COMPLETE:",
            bm25.complete_at_k,
        )

        print(
            "  TARGET COVERAGE:",
            f"{bm25.target_coverage_at_k:.4f}",
        )

        print(
            "  RR:",
            f"{bm25.reciprocal_rank:.4f}",
        )

        print(
            "  SATISFIED:",
            (
                    ", ".join(
                        bm25.satisfied_target_ids
                    )
                    or "-"
            ),
        )

        print()

        print(
            "VOYAGE:"
        )

        print(
            "  HIT:",
            semantic.hit_at_k,
        )

        print(
            "  COMPLETE:",
            semantic.complete_at_k,
        )

        print(
            "  TARGET COVERAGE:",
            f"{semantic.target_coverage_at_k:.4f}",
        )

        print(
            "  RR:",
            f"{semantic.reciprocal_rank:.4f}",
        )

        print(
            "  SATISFIED:",
            (
                    ", ".join(
                        semantic.satisfied_target_ids
                    )
                    or "-"
            ),
        )

        print()

        print(
            "VOYAGE TOP RESULTS:"
        )

        acceptable_units = {
            unit_id
            for target in case.targets
            for unit_id
            in target.acceptable_units
        }

        for (
                rank,
                unit_id,
        ) in enumerate(
            semantic.retrieved_units,
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


def main() -> None:
    openalex_api_key = (
        os.environ[
            "OPENALEX_API_KEY"
        ]
    )

    voyage_api_key = (
        os.environ[
            "VOYAGE_API_KEY"
        ]
    )

    benchmark = json.loads(
        BENCHMARK_PATH.read_text(
            encoding="utf-8"
        )
    )

    top_k = int(
        benchmark[
            "top_k"
        ]
    )

    cases = tuple(
        RetrievalEvalCase
        .model_validate(
            raw_case
        )
        for raw_case
        in benchmark["cases"]
    )

    print("=" * 100)

    print(
        "RETRIEVAL COMPARISON:",
        benchmark["name"],
    )

    print()

    documents = load_documents(
        benchmark=benchmark,
        openalex_api_key=(
            openalex_api_key
        ),
    )

    corpus = (
        build_retrieval_corpus(
            documents
        )
    )

    print(
        "DOCUMENTS:",
        len(documents),
    )

    print(
        "RETRIEVAL UNITS:",
        len(corpus),
    )

    print()

    validate_benchmark_units(
        cases,
        corpus,
    )

    print(
        "Building BM25 index..."
    )

    bm25_retriever = (
        BM25Retriever(
            corpus
        )
    )

    print(
        "Building Voyage semantic index..."
    )

    voyage = (
        VoyageEmbeddingClient(
            api_key=voyage_api_key,
            model="voyage-4",
        )
    )

    try:
        semantic_retriever = (
            SemanticRetriever(
                corpus,
                embedder=voyage,
            )
        )

        print(
            "Running BM25 evaluation..."
        )

        bm25_report = (
            evaluate_retriever(
                bm25_retriever,
                cases,
                top_k=top_k,
            )
        )

        print(
            "Running Voyage evaluation..."
        )

        semantic_report = (
            evaluate_retriever(
                semantic_retriever,
                cases,
                top_k=top_k,
            )
        )

    finally:
        voyage.close()

    print()
    print("=" * 100)
    print("OVERALL COMPARISON")

    print_comparison(
        "ALL CASES",
        bm25=(
            bm25_report.overall
        ),
        semantic=(
            semantic_report.overall
        ),
        top_k=top_k,
    )

    print()
    print("=" * 100)
    print("BY QUERY STYLE")

    for style in (
            RetrievalQueryStyle
    ):
        print()

        print_comparison(
            style.value,
            bm25=subset_metrics(
                bm25_report.results,
                query_style=style,
            ),
            semantic=subset_metrics(
                semantic_report.results,
                query_style=style,
            ),
            top_k=top_k,
        )

    print()
    print("=" * 100)
    print("BY SCOPE")

    for scope in (
            RetrievalEvalScope
    ):
        print()

        print_comparison(
            scope.value,
            bm25=subset_metrics(
                bm25_report.results,
                scope=scope,
            ),
            semantic=subset_metrics(
                semantic_report.results,
                scope=scope,
            ),
            top_k=top_k,
        )

    print_case_comparison(
        cases=cases,
        bm25_report=bm25_report,
        semantic_report=(
            semantic_report
        ),
        corpus=corpus,
    )

    print()
    print("=" * 100)

    print(
        "* = acceptable evidence anchor "
        "for at least one benchmark target"
    )


if __name__ == "__main__":
    main()