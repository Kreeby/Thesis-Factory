import pytest

from thesis_factory.domain.document import (
    DocumentSectionKind,
    NormalizedDocument,
    NormalizedParagraph,
    NormalizedSection,
)
from thesis_factory.domain.evidence_acquisition import (
    EvidenceContext,
    EvidenceExtractionProposal,
    EvidenceQuoteProposal,
    EvidenceRequirement,
    EvidenceRequirementKind,
    EvidenceSupportStatus,
)
from thesis_factory.domain.retrieval import (
    RetrievalUnit,
)
from thesis_factory.evidence.extraction import (
    EvidenceExtractionError,
    EvidenceExtractor,
    verify_extraction_proposal,
)


SHA256 = "a" * 64


def _document() -> NormalizedDocument:
    return NormalizedDocument(
        artifact_sha256=SHA256,
        source_provider="openalex",
        source_provider_id="W1",
        sections=(
            NormalizedSection(
                ordinal=1,
                kind=DocumentSectionKind.BODY,
                path=("Results",),
                paragraphs=(
                    NormalizedParagraph(
                        ordinal=1,
                        text=(
                            "The dataset contains "
                            "10,000 observations and "
                            "23 input features."
                        ),
                    ),
                    NormalizedParagraph(
                        ordinal=2,
                        text=(
                            "Evaluation uses a "
                            "held-out test set."
                        ),
                    ),
                ),
            ),
        ),
    )


def _unit(
    paragraph_ordinal: int,
    text: str,
) -> RetrievalUnit:
    return RetrievalUnit(
        artifact_sha256=SHA256,
        normalization_version="grobid-tei-v1",
        source_provider="openalex",
        source_provider_id="W1",
        section_ordinal=1,
        section_path=("Results",),
        section_kind=DocumentSectionKind.BODY,
        heading_role="STANDARD",
        paragraph_ordinal=paragraph_ordinal,
        text=text,
    )


def _context() -> EvidenceContext:
    first = _unit(
        1,
        (
            "The dataset contains "
            "10,000 observations and "
            "23 input features."
        ),
    )

    second = _unit(
        2,
        "Evaluation uses a held-out test set.",
    )

    return EvidenceContext(
        hit_identity=first.identity,
        units=(first, second),
    )


def _requirement() -> EvidenceRequirement:
    return EvidenceRequirement(
        requirement_id="dataset-size",
        kind=EvidenceRequirementKind.DATASET,
        question=(
            "How many observations "
            "does the dataset contain?"
        ),
        why_needed=(
            "Dataset scale affects "
            "experimental feasibility."
        ),
    )


class FakeReasoner:
    def __init__(
        self,
        result: EvidenceExtractionProposal,
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


def test_extractor_supplies_only_bounded_context() -> None:
    proposal = EvidenceExtractionProposal(
        requirement_id="dataset-size",
        status=EvidenceSupportStatus.SUPPORTED,
        rationale="The paragraph states the size.",
        quotes=(
            EvidenceQuoteProposal(
                paragraph_ordinal=1,
                exact_quote=(
                    "The dataset contains "
                    "10,000 observations"
                ),
            ),
        ),
    )

    reasoner = FakeReasoner(
        proposal
    )

    extractor = EvidenceExtractor(
        reasoner
    )

    result = extractor.propose(
        requirement=_requirement(),
        context=_context(),
    )

    assert result == proposal
    assert len(reasoner.calls) == 1

    prompt = reasoner.calls[0][
        "prompt"
    ]

    assert "[P1]" in prompt
    assert "[P2]" in prompt


def test_verifies_exact_quote_and_builds_span() -> None:
    proposal = EvidenceExtractionProposal(
        requirement_id="dataset-size",
        status=EvidenceSupportStatus.SUPPORTED,
        rationale="The paragraph states the size.",
        quotes=(
            EvidenceQuoteProposal(
                paragraph_ordinal=1,
                exact_quote=(
                    "10,000 observations"
                ),
            ),
        ),
    )

    result = verify_extraction_proposal(
        document=_document(),
        context=_context(),
        requirement=_requirement(),
        proposal=proposal,
    )

    assert len(result.evidence) == 1

    evidence = result.evidence[0]

    assert evidence.text == (
        "10,000 observations"
    )

    assert (
        evidence.address.paragraph_ordinal
        == 1
    )

    paragraph_text = (
        _document()
        .sections[0]
        .paragraphs[0]
        .text
    )

    assert (
        paragraph_text[
            evidence.address.start_char:
            evidence.address.end_char
        ]
        == "10,000 observations"
    )


def test_rejects_paraphrased_quote() -> None:
    proposal = EvidenceExtractionProposal(
        requirement_id="dataset-size",
        status=EvidenceSupportStatus.SUPPORTED,
        rationale="The source gives the size.",
        quotes=(
            EvidenceQuoteProposal(
                paragraph_ordinal=1,
                exact_quote=(
                    "There are about "
                    "ten thousand rows."
                ),
            ),
        ),
    )

    with pytest.raises(
        EvidenceExtractionError,
        match="not an exact substring",
    ):
        verify_extraction_proposal(
            document=_document(),
            context=_context(),
            requirement=_requirement(),
            proposal=proposal,
        )


def test_rejects_quote_outside_context() -> None:
    proposal = EvidenceExtractionProposal(
        requirement_id="dataset-size",
        status=EvidenceSupportStatus.SUPPORTED,
        rationale="The source gives the size.",
        quotes=(
            EvidenceQuoteProposal(
                paragraph_ordinal=999,
                exact_quote="anything",
            ),
        ),
    )

    with pytest.raises(
        EvidenceExtractionError,
        match="outside supplied context",
    ):
        verify_extraction_proposal(
            document=_document(),
            context=_context(),
            requirement=_requirement(),
            proposal=proposal,
        )


def test_rejects_wrong_requirement_id() -> None:
    proposal = EvidenceExtractionProposal(
        requirement_id="wrong-requirement",
        status=(
            EvidenceSupportStatus
            .INSUFFICIENT_EVIDENCE
        ),
        rationale="Not enough evidence.",
    )

    with pytest.raises(
        EvidenceExtractionError,
        match="different requirement",
    ):
        verify_extraction_proposal(
            document=_document(),
            context=_context(),
            requirement=_requirement(),
            proposal=proposal,
        )


def test_preserves_insufficient_evidence() -> None:
    proposal = EvidenceExtractionProposal(
        requirement_id="dataset-size",
        status=(
            EvidenceSupportStatus
            .INSUFFICIENT_EVIDENCE
        ),
        rationale=(
            "The supplied context does not "
            "state the dataset size."
        ),
    )

    result = verify_extraction_proposal(
        document=_document(),
        context=_context(),
        requirement=_requirement(),
        proposal=proposal,
    )

    assert (
        result.status
        == EvidenceSupportStatus
        .INSUFFICIENT_EVIDENCE
    )
    assert result.evidence == ()
