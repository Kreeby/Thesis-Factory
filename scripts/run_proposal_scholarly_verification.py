import argparse
import os
from pathlib import Path

from thesis_factory.artifacts.fetching import (
    ArtifactFetcher,
)
from thesis_factory.domain.evidence_acquisition import (
    EvidenceSupportStatus,
)
from thesis_factory.domain.proposal_verification import (
    ProposalVerificationPlan,
    VerificationLane,
)
from thesis_factory.domain.scholarly_verification import (
    ScholarlyVerificationRun,
)
from thesis_factory.evidence.extraction import (
    EvidenceExtractor,
)
from thesis_factory.integrations.anthropic.client import (
    AnthropicStructuredReasoner,
)
from thesis_factory.integrations.crossref.client import (
    CrossrefClient,
)
from thesis_factory.integrations.datacite.client import (
    DataCiteClient,
)
from thesis_factory.integrations.openalex.client import (
    OpenAlexClient,
    OpenAlexSearchMode,
)
from thesis_factory.integrations.voyage.client import (
    VoyageEmbeddingClient,
)
from thesis_factory.parsing.grobid import (
    GrobidTeiParser,
)
from thesis_factory.research.scholarly_document_evidence import (
    VoyageDocumentEvidenceFinder,
)
from thesis_factory.research.scholarly_documents import (
    OpenAlexVerifiedDocumentProvider,
)
from thesis_factory.research.scholarly_evidence_execution import (
    ScholarlyEvidenceExecutor,
)
from thesis_factory.research.scholarly_seeds import (
    load_scholarly_seed_queries,
)
from thesis_factory.verification.doi_registry import (
    CompositeDoiRegistry,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "plan",
        type=Path,
    )

    parser.add_argument(
        "--discovery",
        type=Path,
        default=Path(
            "./proposal_discovery.json"
        ),
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "./proposal_scholarly_evidence.json"
        ),
    )

    parser.add_argument(
        "--preflight",
        action="store_true",
    )

    parser.add_argument(
        "--probe",
        action="store_true",
    )

    parser.add_argument(
        "--retry-insufficient",
        action="store_true",
    )

    parser.add_argument(
        "--search-limit",
        type=int,
        default=5,
    )

    parser.add_argument(
        "--max-search-queries",
        type=int,
        default=4,
    )

    parser.add_argument(
        "--max-documents",
        type=int,
        default=3,
    )

    parser.add_argument(
        "--bm25-candidates",
        type=int,
        default=24,
    )

    parser.add_argument(
        "--semantic-hits",
        type=int,
        default=4,
    )

    parser.add_argument(
        "--extraction-hits",
        type=int,
        default=2,
    )

    parser.add_argument(
        "--model",
        default=os.environ.get(
            "THESIS_FACTORY_RESEARCH_MODEL",
            "claude-sonnet-5-5",
        ),
    )

    parser.add_argument(
        "--voyage-model",
        default="voyage-4",
    )

    parser.add_argument(
        "--voyage-min-request-interval",
        type=float,
        default=21.0,
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    plan = (
        ProposalVerificationPlan
        .model_validate_json(
            args.plan.read_text(
                encoding="utf-8"
            )
        )
    )

    tasks = tuple(
        task
        for task in plan.tasks
        if (
            task.lane
            == VerificationLane
            .SCHOLARLY_FULLTEXT
        )
    )

    seed_queries = (
        load_scholarly_seed_queries(
            args.discovery,
            plan=plan,
        )
    )

    print(
        "scholarly tasks:",
        len(tasks),
    )
    print(
        "seeded requirements:",
        sum(
            1
            for task in tasks
            if seed_queries.get(
                task.requirement
                .requirement_id
            )
        ),
    )

    existing = _load_existing(
        args.output,
        topic=plan.topic,
    )

    existing_by_id = {
        result.task_id: result
        for result
        in existing.task_results
    }

    pending = tuple(
        task
        for task in tasks
        if _should_run(
            task.task_id,
            existing_by_id=(
                existing_by_id
            ),
            retry_insufficient=(
                args.retry_insufficient
            ),
        )
    )

    print(
        "existing results:",
        len(existing_by_id),
    )
    print(
        "pending:",
        len(pending),
    )

    missing = (
        _missing_environment()
    )

    if args.preflight:
        print(
            "mode: FREE / LOCAL preflight"
        )
        print(
            "external API calls: 0"
        )

        if not args.discovery.exists():
            print(
                "missing discovery artifact:",
                args.discovery,
            )
            raise SystemExit(2)

        if missing:
            print(
                "missing environment:",
                ", ".join(missing),
            )
            raise SystemExit(2)

        print(
            "environment: ready"
        )
        print(
            "OpenAlex content auth: ready"
        )
        return

    if missing:
        raise RuntimeError(
            "missing required environment: "
            + ", ".join(missing)
        )

    if not pending:
        print(
            "nothing to do"
        )
        return

    if args.probe:
        pending = pending[:1]
        print(
            "mode: API PROBE — one pending "
            "scholarly task"
        )
    else:
        print(
            "mode: API RUN — resumable"
        )

    print(
        "uses: OpenAlex + Crossref/DataCite "
        "+ Voyage + Anthropic"
    )

    openalex_key = os.environ[
        "OPENALEX_API_KEY"
    ]

    # Exact discovery-citation titles are now
    # searched lexically. The previous semantic
    # search over a long requirement sentence
    # returned broad topical papers instead of
    # the already-discovered target sources.
    openalex = OpenAlexClient(
        api_key=openalex_key,
        search_mode=(
            OpenAlexSearchMode.LEXICAL
        ),
    )

    crossref = CrossrefClient(
        mailto=os.environ.get(
            "CROSSREF_MAILTO"
        )
    )

    datacite = DataCiteClient()

    fetcher = ArtifactFetcher(
        openalex_api_key=(
            openalex_key
        )
    )

    voyage = VoyageEmbeddingClient(
        api_key=os.environ[
            "VOYAGE_API_KEY"
        ],
        model=args.voyage_model,
        min_request_interval_seconds=(
            args.voyage_min_request_interval
        ),
    )

    reasoner = AnthropicStructuredReasoner(
        model=args.model,
        max_tokens=1800,
    )

    provider = (
        OpenAlexVerifiedDocumentProvider(
            searcher=openalex,
            registry=CompositeDoiRegistry(
                crossref,
                datacite,
            ),
            fetcher=fetcher,
            parser=GrobidTeiParser(),
            seed_queries_by_requirement_id=(
                seed_queries
            ),
            search_limit=(
                args.search_limit
            ),
            max_search_queries=(
                args.max_search_queries
            ),
            max_documents=(
                args.max_documents
            ),
        )
    )

    finder = (
        VoyageDocumentEvidenceFinder(
            embedder=voyage,
            extractor=EvidenceExtractor(
                reasoner
            ),
            bm25_candidates=(
                args.bm25_candidates
            ),
            semantic_hits=(
                args.semantic_hits
            ),
            extraction_hits=(
                args.extraction_hits
            ),
        )
    )

    executor = ScholarlyEvidenceExecutor(
        document_provider=provider,
        evidence_finder=finder,
    )

    results_by_id = dict(
        existing_by_id
    )

    try:
        for index, task in enumerate(
            pending,
            start=1,
        ):
            print(
                f"\n=== SCHOLARLY "
                f"{index}/{len(pending)} ==="
            )
            print(
                task.task_id
            )
            print(
                task.requirement.question
            )

            seeds = seed_queries.get(
                task.requirement
                .requirement_id,
                (),
            )

            if seeds:
                print(
                    "seed queries:",
                    len(seeds),
                )
                for seed in seeds[:3]:
                    print(
                        "  -",
                        seed,
                    )

            result = executor.execute(
                task=task
            )

            results_by_id[
                task.task_id
            ] = result

            ordered_results = tuple(
                results_by_id[
                    plan_task.task_id
                ]
                for plan_task in tasks
                if plan_task.task_id
                in results_by_id
            )

            _write_checkpoint(
                args.output,
                topic=plan.topic,
                results=ordered_results,
            )

            usable = sum(
                1
                for source
                in result.sources
                if source.usable_fulltext
            )

            print(
                "status:",
                result.evidence_result
                .status.value,
            )
            print(
                "verified spans:",
                len(
                    result.evidence_result
                    .evidence
                ),
            )
            print(
                "usable full texts:",
                usable,
            )
            print(
                "source audits:",
                len(
                    result.sources
                ),
            )
            print(
                "errors:",
                len(
                    result.errors
                ),
            )

            if result.errors:
                for error in (
                    result.errors[:3]
                ):
                    print(
                        "  warning:",
                        error,
                    )

    finally:
        voyage.close()
        fetcher.close()
        datacite.close()
        crossref.close()
        openalex.close()

    print(
        "\nsaved checkpoint:",
        args.output,
    )


def _should_run(
    task_id: str,
    *,
    existing_by_id,
    retry_insufficient: bool,
) -> bool:
    existing = existing_by_id.get(
        task_id
    )

    if existing is None:
        return True

    if (
            retry_insufficient
            and existing.evidence_result.status
            == EvidenceSupportStatus
            .INSUFFICIENT_EVIDENCE
    ):
        return True

    return False


def _missing_environment() -> tuple[
    str,
    ...,
]:
    required = (
        "ANTHROPIC_API_KEY",
        "VOYAGE_API_KEY",
        "OPENALEX_API_KEY",
    )

    return tuple(
        name
        for name in required
        if not os.environ.get(
            name
        )
    )


def _load_existing(
    path: Path,
    *,
    topic: str,
) -> ScholarlyVerificationRun:
    if not path.exists():
        return ScholarlyVerificationRun(
            topic=topic,
        )

    run = (
        ScholarlyVerificationRun
        .model_validate_json(
            path.read_text(
                encoding="utf-8"
            )
        )
    )

    if run.topic != topic:
        raise ValueError(
            "existing checkpoint topic "
            "does not match plan topic"
        )

    return run


def _write_checkpoint(
    path: Path,
    *,
    topic: str,
    results,
) -> None:
    run = ScholarlyVerificationRun(
        topic=topic,
        task_results=tuple(
            results
        ),
    )

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temp = path.with_suffix(
        path.suffix + ".tmp"
    )

    temp.write_text(
        run.model_dump_json(
            indent=2,
        ),
        encoding="utf-8",
    )

    temp.replace(
        path
    )


if __name__ == "__main__":
    main()
