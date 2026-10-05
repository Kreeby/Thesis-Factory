import argparse
from pathlib import Path

from thesis_factory.research.discovery_artifact import (
    load_discovery_artifact,
)
from thesis_factory.research.proposal_verification_planning import (
    DeterministicProposalVerificationPlanner,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "artifact",
        type=Path,
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("./proposal_verification_plan.json"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    artifact = load_discovery_artifact(
        args.artifact
    )
    plan = (
        DeterministicProposalVerificationPlanner()
        .plan(artifact=artifact)
    )

    args.output.write_text(
        plan.model_dump_json(indent=2),
        encoding="utf-8",
    )

    print("planning mode: deterministic/local")
    print("external API calls: 0")
    print("verification tasks:", len(plan.tasks))
    print("deferred leads:", len(plan.deferred_lead_ids))

    for task in plan.tasks:
        print(
            f"- [{task.priority.value}] "
            f"[{task.lane.value}] "
            f"{task.task_id}: "
            f"{task.requirement.question}"
        )

    print("saved:", args.output)


if __name__ == "__main__":
    main()
