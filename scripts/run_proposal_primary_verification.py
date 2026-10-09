import argparse
import os
from pathlib import Path

from thesis_factory.domain.primary_source import (
    PrimaryVerificationRun,
)
from thesis_factory.domain.proposal_verification import (
    ProposalVerificationPlan,
    VerificationLane,
)
from thesis_factory.evidence.extraction import (
    EvidenceExtractor,
)
from thesis_factory.integrations.anthropic.client import (
    AnthropicStructuredReasoner,
)
from thesis_factory.integrations.anthropic.primary_source import (
    AnthropicPrimarySourceScout,
)
from thesis_factory.integrations.anthropic.web_research import (
    AnthropicWebResearcher,
)
from thesis_factory.integrations.voyage.client import (
    VoyageEmbeddingClient,
)
from thesis_factory.primary_source.evidence import (
    PrimaryDocumentEvidenceFinder,
)
from thesis_factory.primary_source.execution import (
    PrimarySourceExecutor,
)
from thesis_factory.primary_source.fetching import (
    PrimarySourceFetcher,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "plan",
        type=Path,
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "./proposal_primary_evidence.json"
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
        "--model",
        default=os.environ.get(
            "THESIS_FACTORY_RESEARCH_MODEL",
            "claude-sonnet-5-5",
        ),
    )

    parser.add_argument(
        "--max-search-uses",
        type=int,
        default=2,
    )

    parser.add_argument(
        "--max-documents",
        type=int,
        default=2,
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
        if task.lane
        in {
            VerificationLane
            .OFFICIAL_PRIMARY_WEB,
            VerificationLane
            .DATASET_PRIMARY,
        }
    )

    legal_count = sum(
        1
        for task in tasks
        if task.lane
        == VerificationLane
        .OFFICIAL_PRIMARY_WEB
    )

    dataset_count = (
        len(tasks)
        - legal_count
    )

    print(
        "primary tasks:",
        len(tasks),
    )
    print(
        "legal:",
        legal_count,
    )
    print(
        "dataset:",
        dataset_count,
    )

    existing = _load_existing(
        args.output,
        topic=plan.topic,
    )

    existing_by_id = {
        item.task_id: item
        for item
        in existing.task_results
    }

    pending = tuple(
        task
        for task in tasks
        if task.task_id
        not in existing_by_id
    )

    print(
        "already completed:",
        len(existing_by_id),
    )
    print(
        "pending:",
        len(pending),
    )

    missing = _missing_environment()

    if args.preflight:
        print(
            "mode: FREE / LOCAL preflight"
        )
        print(
            "external API calls: 0"
        )

        if missing:
            print(
                "missing environment:",
                ", ".join(missing),
            )
            raise SystemExit(2)

        if len(tasks) != 8:
            raise RuntimeError(
                "expected exactly 8 primary "
                "verification tasks"
            )

        print(
            "environment: ready"
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
            "primary task"
        )
    else:
        print(
            "mode: API RUN — resumable"
        )

    print(
        "uses: Anthropic web search + "
        "direct primary-source fetch + "
        "Voyage + Anthropic extraction"
    )

    researcher = AnthropicWebResearcher(
        model=args.model,
        max_tokens=2200,
        max_search_uses=(
            args.max_search_uses
        ),
        max_continuations=1,
    )

    scout = AnthropicPrimarySourceScout(
        researcher
    )

    fetcher = PrimarySourceFetcher()

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

    finder = (
        PrimaryDocumentEvidenceFinder(
            embedder=voyage,
            extractor=EvidenceExtractor(
                reasoner
            ),
        )
    )

    executor = PrimarySourceExecutor(
        scout=scout,
        fetcher=fetcher,
        evidence_finder=finder,
        max_documents=(
            args.max_documents
        ),
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
                f"\n=== PRIMARY "
                f"{index}/{len(pending)} ==="
            )
            print(
                task.task_id
            )
            print(
                "lane:",
                task.lane.value,
            )
            print(
                task.requirement.question
            )

            result = executor.execute(
                topic=plan.topic,
                task=task,
            )

            results_by_id[
                task.task_id
            ] = result

            ordered = tuple(
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
                results=ordered,
            )

            fetched = sum(
                1
                for source
                in result.sources
                if source.fetched
            )

            accepted = sum(
                1
                for source
                in result.sources
                if source.authority_accepted
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
                "authoritative candidates:",
                accepted,
            )
            print(
                "fetched primary documents:",
                fetched,
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

    print(
        "\nsaved checkpoint:",
        args.output,
    )


def _missing_environment() -> tuple[
    str,
    ...,
]:
    required = (
        "ANTHROPIC_API_KEY",
        "VOYAGE_API_KEY",
    )

    return tuple(
        item
        for item in required
        if not os.environ.get(
            item
        )
    )


def _load_existing(
    path: Path,
    *,
    topic: str,
) -> PrimaryVerificationRun:
    if not path.exists():
        return PrimaryVerificationRun(
            topic=topic,
        )

    run = (
        PrimaryVerificationRun
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
    run = PrimaryVerificationRun(
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
