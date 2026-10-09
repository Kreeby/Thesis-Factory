from thesis_factory.domain.evidence_acquisition import (
    EvidenceRequirement,
    EvidenceRequirementKind,
)
from thesis_factory.primary_source.evidence import (
    _retrieval_queries,
)


def test_primary_retrieval_uses_question_and_verification_need() -> None:
    requirement = EvidenceRequirement(
        requirement_id="req-1",
        kind=(
            EvidenceRequirementKind.DATASET
        ),
        question=(
            "Verify dataset size and features."
        ),
        why_needed=(
            "Confirm license, class balance, "
            "and corrected version."
        ),
    )

    assert _retrieval_queries(
        requirement
    ) == (
        "Verify dataset size and features.",
        (
            "Confirm license, class balance, "
            "and corrected version."
        ),
    )
