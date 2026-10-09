import json

from thesis_factory.domain.proposal_research import (
    CritiqueVerdict,
    ProposalCritique,
    ProposalDocumentDraft,
    ProposalParagraphKind,
    ProposalResearchDraft,
    ResearchFindingState,
)
from thesis_factory.llm.structured import (
    StructuredReasoner,
)


class ProposalWritingError(
    ValueError
):
    pass


class ProposalWriter:
    def __init__(
        self,
        reasoner: StructuredReasoner,
    ) -> None:
        self._reasoner = reasoner

    def write(
        self,
        *,
        research: ProposalResearchDraft,
        critique: ProposalCritique,
    ) -> ProposalDocumentDraft:
        if (
            critique.verdict
            != CritiqueVerdict.PASS
        ):
            raise ProposalWritingError(
                "proposal cannot be written "
                "before critique passes"
            )

        return self._reasoner.generate(
            system=(
                "You are the academic proposal writer. "
                "Write a concise MSc project proposal using "
                "only the supplied audited research findings. "
                "Do not perform new research. "
                "Do not introduce new datasets, methods, "
                "metrics, legal claims, results, citations, "
                "or contribution claims. "
                "Evidence-backed factual prose must use "
                "EVIDENCE_BACKED paragraphs and cite the "
                "finding ids it is based on. "
                "Design choices that the project proposes to "
                "do must use PROPOSED paragraphs. "
                "Limitations must use LIMITATION paragraphs. "
                "Do not present ASSUMPTION or UNKNOWN findings "
                "as established facts. "
                "Prefer precise, conservative language over "
                "marketing language. "
                "The proposal should be concrete enough to "
                "guide implementation but must not claim that "
                "experiments have already been run."
            ),
            prompt=(
                "<approved_research>\n"
                f"{research.model_dump_json()}\n"
                "</approved_research>\n"
                "<critique>"
                f"{critique.model_dump_json()}"
                "</critique>"
            ),
            output_model=(
                ProposalDocumentDraft
            ),
        )


def validate_proposal_document(
    document: ProposalDocumentDraft,
    *,
    research: ProposalResearchDraft,
) -> None:
    findings = {
        finding.finding_id: finding
        for finding in research.findings
    }

    for section in document.sections:
        for paragraph in section.paragraphs:
            for finding_id in (
                paragraph.finding_ids
            ):
                if finding_id not in findings:
                    raise ProposalWritingError(
                        "proposal paragraph references "
                        "unknown finding"
                    )

            if (
                paragraph.kind
                == ProposalParagraphKind.EVIDENCE_BACKED
            ):
                for finding_id in (
                    paragraph.finding_ids
                ):
                    state = (
                        findings[
                            finding_id
                        ].state
                    )

                    if (
                        state
                        not in {
                            ResearchFindingState.SUPPORTED,
                            ResearchFindingState.DERIVED,
                        }
                    ):
                        raise ProposalWritingError(
                            "evidence-backed paragraph "
                            "references unsupported finding"
                        )
