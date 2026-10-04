import pytest

from thesis_factory.domain.proposal_research import (
    CritiqueIssue,
    CritiqueSeverity,
    CritiqueVerdict,
    ProposalCritique,
    ProposalDocumentDraft,
    ProposalParagraph,
    ProposalParagraphKind,
    ProposalResearchDraft,
    ProposalSection,
    ProposalSectionKind,
    ResearchDimension,
    ResearchFinding,
    ResearchFindingState,
)
from thesis_factory.research.proposal_writing import (
    ProposalWriter,
    ProposalWritingError,
    validate_proposal_document,
)


def _research(
    *,
    state=ResearchFindingState.SUPPORTED,
) -> ProposalResearchDraft:
    support = (
        ("req-1",)
        if state
        in {
            ResearchFindingState.SUPPORTED,
            ResearchFindingState.DERIVED,
        }
        else ()
    )

    return ProposalResearchDraft(
        approved_topic="Topic",
        findings=(
            ResearchFinding(
                finding_id="finding-1",
                dimension=ResearchDimension.PROBLEM,
                statement="Problem statement.",
                rationale="Research rationale.",
                state=state,
                supporting_requirement_ids=support,
            ),
        ),
    )


def _document() -> ProposalDocumentDraft:
    return ProposalDocumentDraft(
        title="Proposal",
        sections=(
            ProposalSection(
                kind=(
                    ProposalSectionKind
                    .BACKGROUND_PROBLEM
                ),
                heading="Background and problem",
                paragraphs=(
                    ProposalParagraph(
                        kind=(
                            ProposalParagraphKind
                            .EVIDENCE_BACKED
                        ),
                        text="Supported problem.",
                        finding_ids=(
                            "finding-1",
                        ),
                    ),
                ),
            ),
        ),
    )


class FakeReasoner:
    def __init__(self, result):
        self.result = result

    def generate(self, **kwargs):
        return self.result


def test_writer_requires_passing_critique() -> None:
    writer = ProposalWriter(
        FakeReasoner(
            _document()
        )
    )

    critique = ProposalCritique(
        verdict=CritiqueVerdict.REVISE,
        issues=(
            CritiqueIssue(
                issue_id="issue-1",
                severity=CritiqueSeverity.MAJOR,
                problem="Needs revision.",
                required_action="Revise it.",
            ),
        ),
        summary="Revision required.",
    )

    with pytest.raises(
        ProposalWritingError,
        match="critique passes",
    ):
        writer.write(
            research=_research(),
            critique=critique,
        )


def test_validates_evidence_backed_paragraph() -> None:
    validate_proposal_document(
        _document(),
        research=_research(),
    )


def test_rejects_unknown_finding() -> None:
    document = _document().model_copy(
        update={
            "sections": (
                ProposalSection(
                    kind=(
                        ProposalSectionKind
                        .BACKGROUND_PROBLEM
                    ),
                    heading="Background",
                    paragraphs=(
                        ProposalParagraph(
                            kind=(
                                ProposalParagraphKind
                                .EVIDENCE_BACKED
                            ),
                            text="Text.",
                            finding_ids=("missing",),
                        ),
                    ),
                ),
            )
        }
    )

    with pytest.raises(
        ProposalWritingError,
        match="unknown finding",
    ):
        validate_proposal_document(
            document,
            research=_research(),
        )


def test_rejects_assumption_as_evidence() -> None:
    with pytest.raises(
        ProposalWritingError,
        match="unsupported finding",
    ):
        validate_proposal_document(
            _document(),
            research=_research(
                state=(
                    ResearchFindingState
                    .ASSUMPTION
                )
            ),
        )
