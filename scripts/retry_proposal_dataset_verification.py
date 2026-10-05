import argparse
import os
from pathlib import Path

from thesis_factory.domain.evidence_acquisition import (
    EvidenceSupportStatus,
)
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
        "evidence",
        type=Path,
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

    run = (
        PrimaryVerificationRun
        .model_validate_json(
            args.evidence.read_text(
                encoding="utf-8"
            )
        )
    )

    if run.topic != plan.topic:
        raise ValueError(
            "evidence topic does not match plan"
        )

    tasks = tuple(
        task
        for task in plan.tasks
        if (
            task.lane
            == VerificationLane.DATASET_PRIMARY
        )
    )

    existing_by_id = {
        item.task_id: item
        for item in run.task_results
    }

    pending = tuple(
        task
        for task in tasks
        if (
            task.task_id
            not in existing_by_id
            or (
                existing_by_id[
                    task.task_id
                ]
                .evidence_result.status
                == EvidenceSupportStatus
                .INSUFFICIENT_EVIDENCE
            )
        )
    )

    print(
        "dataset tasks:",
        len(tasks),
    )
    print(
        "retry candidates:",
        len(pending),
    )
    print(
        "mode:",
        (
            "API PROBE — one dataset task"
            if args.probe
            else "API RUN — dataset retries"
        ),
    )
    print(
        "source discovery: deterministic "
        "canonical dataset routes"
    )
    print(
        "uses: direct fetch + Voyage + "
        "Anthropic extraction"
    )

    if not pending:
        print(
            "nothing to retry"
        )
        return

    if args.probe:
        pending = pending[:1]

    researcher = AnthropicWebResearcher(
        model=args.model,
        max_tokens=1800,
        max_search_uses=1,
        max_continuations=0,
    )

    scout = AnthropicPrimarySourceScout(
        researcher
    )

    fetcher = PrimarySourceFetcher()

    voyage = VoyageEmbeddingClient(
        api_key=os.environ[
            "VOYAGE_API_KEY"
        ],
        model="voyage-4",
        min_request_interval_seconds=21.0,
    )

    reasoner = AnthropicStructuredReasoner(
        model=args.model,
        max_tokens=1800,
    )

    finder = PrimaryDocumentEvidenceFinder(
        embedder=voyage,
        extractor=EvidenceExtractor(
            reasoner
        ),
        extraction_hits=4,
    )

    executor = PrimarySourceExecutor(
        scout=scout,
        fetcher=fetcher,
        evidence_finder=finder,
        max_documents=2,
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
                f"\n=== DATASET "
                f"{index}/{len(pending)} ==="
            )
            print(
                task.task_id
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
                for plan_task in plan.tasks
                if (
                    plan_task.lane
                    in {
                        VerificationLane
                        .OFFICIAL_PRIMARY_WEB,
                        VerificationLane
                        .DATASET_PRIMARY,
                    }
                    and plan_task.task_id
                    in results_by_id
                )
            )

            checkpoint = (
                PrimaryVerificationRun(
                    topic=plan.topic,
                    task_results=ordered,
                )
            )

            temp = args.evidence.with_suffix(
                args.evidence.suffix
                + ".tmp"
            )

            temp.write_text(
                checkpoint.model_dump_json(
                    indent=2,
                ),
                encoding="utf-8",
            )

            temp.replace(
                args.evidence
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
                "fetched documents:",
                sum(
                    1
                    for source
                    in result.sources
                    if source.fetched
                ),
            )
            print(
                "errors:",
                len(
                    result.errors
                ),
            )

    finally:
        voyage.close()
        fetcher.close()

    print(
        "\nupdated:",
        args.evidence,
    )


if __name__ == "__main__":
    main()
