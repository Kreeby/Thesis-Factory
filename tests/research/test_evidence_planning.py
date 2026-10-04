import pytest
from pydantic import ValidationError

from thesis_factory.domain.evidence_acquisition import (
    EvidenceQuery,
    EvidenceQueryPlan,
    EvidenceRequirement,
    EvidenceRequirementKind,
)
from thesis_factory.research.evidence_planning import (
    EvidenceQueryPlanner,
    EvidenceRequirementPlanner,
    EvidenceRequirementSet,
)


class FakeReasoner:
    def __init__(
        self,
        result,
    ) -> None:
        self.result = result
        self.calls: list[
            dict[str, object]
        ] = []

    def generate(
        self,
        *,
        system: str,
        prompt: str,
        output_model,
    ):
        self.calls.append(
            {
                "system": system,
                "prompt": prompt,
                "output_model": output_model,
            }
        )

        return self.result


def _requirement() -> EvidenceRequirement:
    return EvidenceRequirement(
        requirement_id="dataset-needs",
        kind=EvidenceRequirementKind.DATASET,
        question=(
            "What dataset properties are required "
            "for this empirical evaluation?"
        ),
        why_needed=(
            "The experiment needs a defensible "
            "dataset selection."
        ),
    )


def test_requirement_planner_is_bounded() -> None:
    result = EvidenceRequirementSet(
        requirements=(
            _requirement(),
        )
    )

    reasoner = FakeReasoner(
        result
    )

    planner = EvidenceRequirementPlanner(
        reasoner
    )

    planned = planner.plan(
        topic=(
            "Explainable AI for "
            "consumer credit scoring"
        ),
        objective=(
            "Prepare an evidence-backed "
            "MSc project proposal"
        ),
    )

    assert planned == result
    assert len(reasoner.calls) == 1

    call = reasoner.calls[0]

    assert (
        "Do not answer the requirements."
        in call["system"]
    )

    assert (
        "<approved_topic>"
        in call["prompt"]
    )


def test_requirement_set_rejects_duplicate_ids() -> None:
    with pytest.raises(
        ValidationError,
        match="must be unique",
    ):
        EvidenceRequirementSet(
            requirements=(
                _requirement(),
                _requirement(),
            )
        )


def test_requirement_planner_rejects_blank_input() -> None:
    reasoner = FakeReasoner(
        EvidenceRequirementSet(
            requirements=(
                _requirement(),
            )
        )
    )

    planner = EvidenceRequirementPlanner(
        reasoner
    )

    with pytest.raises(
        ValueError,
        match="topic must not be empty",
    ):
        planner.plan(
            topic="   ",
            objective="proposal",
        )

    assert reasoner.calls == []


def test_query_planner_preserves_requirement_id() -> None:
    plan = EvidenceQueryPlan(
        requirement_id="dataset-needs",
        queries=(
            EvidenceQuery(
                query=(
                    "consumer credit scoring "
                    "dataset explainable AI"
                ),
            ),
        ),
    )

    reasoner = FakeReasoner(
        plan
    )

    planner = EvidenceQueryPlanner(
        reasoner
    )

    result = planner.plan(
        requirement=_requirement()
    )

    assert result == plan
    assert len(result.queries) == 1

    call = reasoner.calls[0]

    assert (
        "returned requirement_id "
        "must exactly match"
        in call["system"]
    )
