import json
import os
from pathlib import Path
from typing import Protocol

import httpx

from thesis_factory.artifacts.fetching import (
    ArtifactFetcher,
    select_preferred_text_location,
)
from thesis_factory.domain.retrieval import (
    RetrievalHit,
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
from thesis_factory.retrieval.hybrid import (
    HybridRetriever,
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

HYBRID_CANDIDATE_K = 20
RRF_CONSTANT = 60.0


class RankedRetriever(Protocol):
    def search(
            self,
            query: str,
            *,
            top_k: int = 10,
    ) -> tuple[
        RetrievalHit,
        ...
    ]:
        ...


class PrefetchingRetriever:
    """
    Diagnostic-only wrapper.

    The first search for a query asks the underlying retriever
    for at least prefetch_k results and caches that ranking.

    Later requests at a shallower depth reuse the same ranking.
    This prevents the hybrid benchmark from making duplicate
    Voyage query-embedding calls.
    """

    def __init__(
            self,
            retriever: RankedRetriever,
            *,
            prefetch_k: int,
    ) -> None:
        if prefetch_k < 1:
            raise ValueError(
                "prefetch_k must be positive"
            )

        self._retriever = retriever
        self._prefetch_k = prefetch_k

        self._cache: dict[
            str,
            tuple[
                RetrievalHit,
                ...
            ],
        ] = {}

        self._cache_depth: dict[
            str,
            int,
        ] = {}

    def search(
            self,
            query: str,
            *,
            top_k: int = 10,
    ) -> tuple[
        RetrievalHit,
        ...
    ]:
        if top_k < 1:
            raise ValueError(
                "top_k must be positive"
            )

        normalized_query = (
            query.strip()
        )

        if not normalized_query:
            raise ValueError(
                "query must not be empty"
            )

        required_depth = max(
            self._prefetch_k,
            top_k,
        )

        cached_depth = (
            self._cache_depth.get(
                normalized_query,
                0,
            )
        )

        if cached_depth < required_depth:
            hits = (
                self._retriever.search(
                    normalized_query,
                    top_k=required_depth,
                )
            )

            self._cache[
                normalized_query
            ] = hits

            self._cache_depth[
                normalized_query
            ] = required_depth

        return self._cache[
            normalized_query
        ][:top_k]


def print_three_way_comparison(
        label: str,
        *,
        bm25: RetrievalEvalMetrics,
        semantic: RetrievalEvalMetrics,
        hybrid: RetrievalEvalMetrics,
        top_k: int,
) -> None:
    print(label)

    print(
        f"  {'METRIC':<24}"
        f"{'BM25':>10}"
        f"{'VOYAGE':>10}"
        f"{'HYBRID':>10}"
        f"{'H-BM25':>10}"
        f"{'H-VOY':>10}"
    )

    rows = (
        (
            f"Hit@{top_k}",
            bm25.hit_rate_at_k,
            semantic.hit_rate_at_k,
            hybrid.hit_rate_at_k,
        ),
        (
            f"Complete@{top_k}",
            bm25.complete_rate_at_k,
            semantic.complete_rate_at_k,
            hybrid.complete_rate_at_k,
        ),
        (
            f"Target Coverage@{top_k}",
            bm25.mean_target_coverage_at_k,
            semantic.mean_target_coverage_at_k,
            hybrid.mean_target_coverage_at_k,
        ),
        (
            "MRR",
            bm25.mean_reciprocal_rank,
            semantic.mean_reciprocal_rank,
            hybrid.mean_reciprocal_rank,
        ),
    )

    for (
            metric_name,
            bm25_value,
            semantic_value,
            hybrid_value,
    ) in rows:
        print(
            f"  {metric_name:<24}"
            f"{bm25_value:>10.4f}"
            f"{semantic_value:>10.4f}"
            f"{hybrid_value:>10.4f}"
            f"{hybrid_value - bm25_value:>+10.4f}"
            f"{hybrid_value - semantic_value:>+10.4f}"
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
        hybrid_report,
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

    hybrid_by_case = {
        result.case_id: result
        for result
        in hybrid_report.results
    }

    print()
    print("=" * 110)
    print("CASE COMPARISON")

    for case in cases:
        bm25 = bm25_by_case[
            case.id
        ]

        semantic = semantic_by_case[
            case.id
        ]

        hybrid = hybrid_by_case[
            case.id
        ]

        print()
        print("-" * 110)

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
            f"  {'SYSTEM':<12}"
            f"{'HIT':>8}"
            f"{'COMPLETE':>12}"
            f"{'COVERAGE':>12}"
            f"{'RR':>10}"
            f"  SATISFIED"
        )

        for (
                label,
                result,
        ) in (
                (
                        "BM25",
                        bm25,
                ),
                (
                        "VOYAGE",
                        semantic,
                ),
                (
                        "HYBRID",
                        hybrid,
                ),
        ):
            satisfied = (
                    ", ".join(
                        result.satisfied_target_ids
                    )
                    or "-"
            )

            print(
                f"  {label:<12}"
                f"{str(result.hit_at_k):>8}"
                f"{str(result.complete_at_k):>12}"
                f"{result.target_coverage_at_k:>12.4f}"
                f"{result.reciprocal_rank:>10.4f}"
                f"  {satisfied}"
            )

        print()
        print(
            "HYBRID TOP RESULTS:"
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
            hybrid.retrieved_units,
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

    print("=" * 110)

    print(
        "RETRIEVAL COMPARISON:",
        benchmark["name"],
    )

    print(
        "HYBRID:",
        (
            "RRF("
            f"candidate_k={HYBRID_CANDIDATE_K}, "
            f"constant={RRF_CONSTANT:g}"
            ")"
        ),
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
        raw_semantic_retriever = (
            SemanticRetriever(
                corpus,
                embedder=voyage,
            )
        )

        semantic_retriever = (
            PrefetchingRetriever(
                raw_semantic_retriever,
                prefetch_k=(
                    HYBRID_CANDIDATE_K
                ),
            )
        )

        hybrid_retriever = (
            HybridRetriever(
                lexical_retriever=(
                    bm25_retriever
                ),
                semantic_retriever=(
                    semantic_retriever
                ),
                candidate_k=(
                    HYBRID_CANDIDATE_K
                ),
                rrf_constant=(
                    RRF_CONSTANT
                ),
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

        print(
            "Running Hybrid RRF evaluation..."
        )

        hybrid_report = (
            evaluate_retriever(
                hybrid_retriever,
                cases,
                top_k=top_k,
            )
        )

    finally:
        voyage.close()

    print()
    print("=" * 110)
    print("OVERALL COMPARISON")

    print_three_way_comparison(
        "ALL CASES",
        bm25=(
            bm25_report.overall
        ),
        semantic=(
            semantic_report.overall
        ),
        hybrid=(
            hybrid_report.overall
        ),
        top_k=top_k,
    )

    print()
    print("=" * 110)
    print("BY QUERY STYLE")

    for style in (
            RetrievalQueryStyle
    ):
        print()

        print_three_way_comparison(
            style.value,
            bm25=subset_metrics(
                bm25_report.results,
                query_style=style,
            ),
            semantic=subset_metrics(
                semantic_report.results,
                query_style=style,
            ),
            hybrid=subset_metrics(
                hybrid_report.results,
                query_style=style,
            ),
            top_k=top_k,
        )

    print()
    print("=" * 110)
    print("BY SCOPE")

    for scope in (
            RetrievalEvalScope
    ):
        print()

        print_three_way_comparison(
            scope.value,
            bm25=subset_metrics(
                bm25_report.results,
                scope=scope,
            ),
            semantic=subset_metrics(
                semantic_report.results,
                scope=scope,
            ),
            hybrid=subset_metrics(
                hybrid_report.results,
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
        hybrid_report=(
            hybrid_report
        ),
        corpus=corpus,
    )

    print()
    print("=" * 110)

    print(
        "* = acceptable evidence anchor "
        "for at least one benchmark target"
    )


if __name__ == "__main__":
    main()