import json
import os
from pathlib import Path

from thesis_factory.integrations.voyage.client import (
    VoyageEmbeddingClient,
)
from thesis_factory.retrieval.bm25 import (
    BM25Retriever,
)
from thesis_factory.retrieval.corpus import (
    build_retrieval_corpus,
)
from thesis_factory.retrieval.evaluation import (
    RetrievalEvalCase,
    RetrievalEvalScope,
    RetrievalQueryStyle,
    evaluate_retriever,
)
from thesis_factory.retrieval.hybrid import (
    HybridRetriever,
)
from thesis_factory.retrieval.semantic import (
    SemanticRetriever,
)

from run_retrieval_comparison import (
    HYBRID_CANDIDATE_K,
    RRF_CONSTANT,
    PrefetchingRetriever,
    load_documents,
    print_case_comparison,
    print_three_way_comparison,
    subset_metrics,
    validate_benchmark_units,
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
        / "held_out_v1.json"
)

FROZEN_BENCHMARK_COMMIT = (
    "61e2c82"
)


def main() -> None:
    openalex_api_key = os.environ[
        "OPENALEX_API_KEY"
    ]

    voyage_api_key = os.environ[
        "VOYAGE_API_KEY"
    ]

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
        "HELD-OUT RETRIEVAL COMPARISON:",
        benchmark["name"],
    )

    print(
        "FROZEN BENCHMARK COMMIT:",
        FROZEN_BENCHMARK_COMMIT,
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

    print(
        "IMPORTANT:"
    )

    print(
        "  This benchmark was frozen before "
        "BM25, Voyage, or RRF evaluation."
    )

    print(
        "  Its queries, targets, and acceptable "
        "anchors must not be changed in response "
        "to these results."
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

    print(
        "CASES:",
        len(cases),
    )

    print(
        "TARGETS:",
        sum(
            len(case.targets)
            for case in cases
        ),
    )

    print()

    validate_benchmark_units(
        cases,
        corpus,
    )

    print(
        "Frozen evidence anchors "
        "validated against corpus."
    )

    print()

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
            "Running BM25 held-out evaluation..."
        )

        bm25_report = (
            evaluate_retriever(
                bm25_retriever,
                cases,
                top_k=top_k,
            )
        )

        print(
            "Running Voyage held-out evaluation..."
        )

        semantic_report = (
            evaluate_retriever(
                semantic_retriever,
                cases,
                top_k=top_k,
            )
        )

        print(
            "Running frozen RRF held-out "
            "evaluation..."
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
    print(
        "HELD-OUT OVERALL COMPARISON"
    )

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
    print(
        "HELD-OUT BY QUERY STYLE"
    )

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
    print(
        "HELD-OUT BY SCOPE"
    )

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
        bm25_report=(
            bm25_report
        ),
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
        "* = frozen acceptable evidence "
        "anchor for at least one target"
    )

    print()

    print(
        "BENCHMARK REMAINS FROZEN AT:",
        FROZEN_BENCHMARK_COMMIT,
    )


if __name__ == "__main__":
    main()