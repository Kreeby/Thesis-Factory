import pytest

from thesis_factory.domain.evidence import (
    EvidenceAddress,
    EvidenceSpan,
)
from thesis_factory.domain.evidence_acquisition import (
    EvidenceRequirement,
    EvidenceRequirementKind,
    EvidenceSupportStatus,
    VerifiedEvidenceResult,
)
from thesis_factory.domain.proposal_research import (
    ProposalResearchDraft,
    ResearchDimension,
    ResearchFinding,
    ResearchFindingState,
)
from thesis_factory.research.proposal_research import (
    ProposalResearchError,
    ProposalResearchSynthesizer,
    validate_research_draft,
)


SHA256 = "a" * 64


def _span() -> EvidenceSpan:
    return EvidenceSpan(
        address=EvidenceAddress(
            artifact_sha256=SHA256,
            normalization_version="grobid-tei-v1",
            paragraph_ordinal=1,
            start_char=0,
            end_char=18,
        ),
        text="Dataset has labels",
        source_provider="openalex",
        source_provider_id="W1",
        section_ordinal=1,
        section_path=("Data",),
    )


def _requirement() -> EvidenceRequirement:
    return EvidenceRequirement(
        requirement_id="dataset-evidence",
        kind=EvidenceRequirementKind.DATASET,
        question="What data properties are available?",
        why_needed="Dataset selection requires evidence.",
    )


def _result(
    status=EvidenceSupportStatus.SUPPORTED,
):
    evidence = (
        (_span(),)
        if status
        in {
            EvidenceSupportStatus.SUPPORTED,
            EvidenceSupportStatus.PARTIAL,
        }
        else ()
    )

    return VerifiedEvidenceResult(
        requirement_id="dataset-evidence",
        status=status,
        rationale="Evidence status.",
        evidence=evidence,
    )


def _draft() -> ProposalResearchDraft:
    return ProposalResearchDraft(
        approved_topic="Approved topic",
        findings=(
            ResearchFinding(
                finding_id="dataset-finding",
                dimension=ResearchDimension.DATASET,
                statement="A labelled dataset is available.",
                rationale="The evidence states labels exist.",
                state=ResearchFindingState.SUPPORTED,
                supporting_requirement_ids=(
                    "dataset-evidence",
                ),
            ),
        ),
    )


class FakeReasoner:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def generate(
        self,
        *,
        system,
        prompt,
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


def test_synthesizer_uses_verified_evidence_only() -> None:
    reasoner = FakeReasoner(
        _draft()
    )

    synthesizer = (
        ProposalResearchSynthesizer(
            reasoner
        )
    )

    result = synthesizer.synthesize(
        approved_topic="Approved topic",
        requirements=(_requirement(),),
        evidence_results=(_result(),),
    )

    assert result == _draft()
    assert len(reasoner.calls) == 1
    assert (
        "Do not perform new research"
        in reasoner.calls[0]["system"]
    )


def test_validates_supported_finding() -> None:
    validate_research_draft(
        _draft(),
        evidence_results=(
            _result(),
        ),
    )


def test_rejects_reference_to_insufficient_evidence() -> None:
    with pytest.raises(
        ProposalResearchError,
        match="does not support",
    ):
        validate_research_draft(
            _draft(),
            evidence_results=(
                _result(
                    EvidenceSupportStatus
                    .INSUFFICIENT_EVIDENCE
                ),
            ),
        )


def test_rejects_unknown_requirement_reference() -> None:
    with pytest.raises(
        ProposalResearchError,
        match="unknown evidence requirement",
    ):
        validate_research_draft(
            _draft(),
            evidence_results=(),
        )
