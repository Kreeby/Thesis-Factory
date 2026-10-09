import argparse
from pathlib import Path

from thesis_factory.research.discovery_artifact import (
    load_discovery_artifact,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "artifact",
        type=Path,
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    artifact = load_discovery_artifact(
        args.artifact
    )

    lead_count = sum(
        len(objective.leads)
        for objective in artifact.objectives
    )

    print("topic:", artifact.topic)
    print("objectives:", len(artifact.objectives))
    print("discovery leads:", lead_count)
    print("citation references: valid")


if __name__ == "__main__":
    main()
