import argparse
import json
import os
from pathlib import Path

from thesis_factory.integrations.anthropic.client import (
    AnthropicStructuredReasoner,
)
from thesis_factory.integrations.anthropic.web_research import (
    AnthropicWebResearcher,
)
from thesis_factory.research.web_leads import (
    WebResearchLeadExtractor,
)


DEFAULT_TOPIC = (
    "A Legally Grounded Empirical Evaluation "
    "of Explainable AI for Consumer Credit Scoring"
)

DEFAULT_OBJECTIVES = (
    (
        "Establish the current problem context, "
        "relevant legal or regulatory explanation "
        "requirements, and evidence for a research gap."
    ),
    (
        "Discover candidate datasets and the properties "
        "that would make them suitable or unsuitable "
        "for the proposed empirical study."
    ),
    (
        "Discover relevant predictive baselines, "
        "interpretable model families, post-hoc or "
        "recourse explanation approaches, and the "
        "evidence needed to justify their comparison."
    ),
    (
        "Discover evaluation dimensions and metrics "
        "used to assess predictive models and "
        "explanations in this research area."
    ),
    (
        "Assess empirical feasibility, likely thesis "
        "contribution opportunities, limitations, "
        "and important competing approaches."
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--topic",
        default=DEFAULT_TOPIC,
    )

    parser.add_argument(
        "--model",
        default=(
            os.environ.get(
                "THESIS_FACTORY_RESEARCH_MODEL",
                "claude-sonnet-5-5",
            )
        ),
    )

    parser.add_argument(
        "--max-search-uses",
        type=int,
        default=4,
    )

    parser.add_argument(
        "--structured-max-tokens",
        type=int,
        default=8000,
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "/tmp/"
            "thesis_factory_proposal_discovery.json"
        ),
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    web_researcher = (
        AnthropicWebResearcher(
            model=args.model,
            max_search_uses=(
                args.max_search_uses
            ),
        )
    )

    reasoner = (
        AnthropicStructuredReasoner(
            model=args.model,
            max_tokens=(
                args.structured_max_tokens
            ),
        )
    )

    lead_extractor = (
        WebResearchLeadExtractor(
            reasoner
        )
    )

    packets = []
    lead_sets = []

    for index, objective in enumerate(
        DEFAULT_OBJECTIVES,
        start=1,
    ):
        print(
            f"\n=== OBJECTIVE {index}/"
            f"{len(DEFAULT_OBJECTIVES)} ==="
        )
        print(
            objective
        )

        packet = web_researcher.research(
            approved_topic=args.topic,
            objective=objective,
        )

        leads = lead_extractor.extract(
            packet=packet
        )

        packets.append(
            packet.model_dump(
                mode="json"
            )
        )
        lead_sets.append(
            leads.model_dump(
                mode="json"
            )
        )

        print(
            "citations:",
            len(
                packet.citations
            ),
        )
        print(
            "research leads:",
            len(
                leads.leads
            ),
        )

        for lead in leads.leads:
            print(
                f"- [{lead.dimension.value}] "
                f"{lead.candidate_statement}"
            )

    artifact = {
        "topic": args.topic,
        "model": args.model,
        "packets": packets,
        "lead_sets": lead_sets,
    }

    args.output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    args.output.write_text(
        json.dumps(
            artifact,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        "\nSaved discovery artifact to:",
        args.output,
    )


if __name__ == "__main__":
    main()
