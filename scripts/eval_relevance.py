import json
import os
import sys
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from thesis_factory.domain.source import SourceRecord
from thesis_factory.integrations.anthropic.client import (
    AnthropicStructuredReasoner,
)
from thesis_factory.research.relevance import (
    RelevanceAgent,
    RelevanceStatus,
)


class RelevanceEvalCase(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    id: str
    topic: str
    title: str
    abstract: str | None
    expected_status: RelevanceStatus


def load_cases() -> tuple[RelevanceEvalCase, ...]:
    path = Path("evals/relevance/cases.json")

    payload = json.loads(
        path.read_text(encoding="utf-8")
    )

    return tuple(
        RelevanceEvalCase.model_validate(item)
        for item in payload
    )


def main() -> int:
    reasoner = AnthropicStructuredReasoner(
        model=os.environ["THESIS_FACTORY_CLAUDE_MODEL"],
    )

    agent = RelevanceAgent(reasoner)

    cases = load_cases()

    passed = 0

    for case in cases:
        source = SourceRecord(
            title=case.title,
            abstract=case.abstract,
            provider="eval",
            provider_id=case.id,
        )

        result = agent.assess(
            topic=case.topic,
            source=source,
        )

        success = result.status == case.expected_status

        print("=" * 80)
        print(case.id)
        print("EXPECTED:", case.expected_status)
        print("ACTUAL:  ", result.status)
        print("RESULT:  ", "PASS" if success else "FAIL")
        print("RATIONALE:", result.rationale)

        if success:
            passed += 1

    failed = len(cases) - passed

    print("=" * 80)
    print(
        f"SUMMARY: {passed}/{len(cases)} passed, "
        f"{failed} failed"
    )

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())