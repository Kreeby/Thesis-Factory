import pytest
from pydantic import ValidationError

from thesis_factory.domain.evidence_acquisition import (
    EvidenceExtractionProposal,
    EvidenceQuery,
    EvidenceQueryPlan,
    EvidenceQuoteProposal,
    EvidenceRequirement,
    EvidenceRequirementKind,
    EvidenceSupportStatus,
)


def _requirement() -> EvidenceRequirement:
    return EvidenceRequirement(
        requirement_id="dataset-suitability",
        kind=EvidenceRequirementKind.DATASET,
        question=(
            "What dataset properties are required "
            "to evaluate the approved topic?"
        ),
        why_needed=(
            "Dataset selection must be justified "
            "before experiment design."
        ),
    )


def test_requirement_normalizes_text() -> None:
    requirement = EvidenceRequirement(
        requirement_id="dataset-suitability",
        kind=EvidenceRequirementKind.DATASET,
        question="  What   data are needed? ",
        why_needed="  Needed   for evaluation. ",
    )

    assert (
        requirement.question
        == "What data are needed?"
    )
    assert (
        requirement.why_needed
        == "Needed for evaluation."
    )


def test_query_plan_is_bounded() -> None:
    with pytest.raises(ValidationError):
        EvidenceQueryPlan(
            requirement_id="dataset-suitability",
            queries=tuple(
                EvidenceQuery(
                    query=f"query {index}"
                )
                for index in range(5)
            ),
        )


def test_query_plan_rejects_duplicates() -> None:
    with pytest.raises(
        ValidationError,
        match="queries must be unique",
    ):
        EvidenceQueryPlan(
            requirement_id="dataset-suitability",
            queries=(
                EvidenceQuery(
                    query="credit scoring dataset"
                ),
                EvidenceQuery(
                    query="Credit Scoring Dataset"
                ),
            ),
        )


def test_supported_proposal_requires_quote() -> None:
    with pytest.raises(
        ValidationError,
        match="requires at least one quote",
    ):
        EvidenceExtractionProposal(
            requirement_id="dataset-suitability",
            status=EvidenceSupportStatus.SUPPORTED,
            rationale="The source supports it.",
        )


def test_insufficient_proposal_rejects_quotes() -> None:
    with pytest.raises(
        ValidationError,
        match="must not contain quotes",
    ):
        EvidenceExtractionProposal(
            requirement_id="dataset-suitability",
            status=(
                EvidenceSupportStatus
                .INSUFFICIENT_EVIDENCE
            ),
            rationale="The context is insufficient.",
            quotes=(
                EvidenceQuoteProposal(
                    paragraph_ordinal=1,
                    exact_quote="Some text.",
                ),
            ),
        )


def test_valid_supported_proposal() -> None:
    proposal = EvidenceExtractionProposal(
        requirement_id="dataset-suitability",
        status=EvidenceSupportStatus.SUPPORTED,
        rationale="The source states the property.",
        quotes=(
            EvidenceQuoteProposal(
                paragraph_ordinal=3,
                exact_quote=(
                    "The dataset contains "
                    "10,000 observations."
                ),
            ),
        ),
    )

    assert len(proposal.quotes) == 1
