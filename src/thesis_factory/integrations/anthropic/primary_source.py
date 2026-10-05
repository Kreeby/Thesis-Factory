from thesis_factory.domain.primary_source import (
    PrimarySourceCandidate,
)
from thesis_factory.domain.proposal_verification import (
    ProposalVerificationTask,
)
from thesis_factory.integrations.anthropic.web_research import (
    AnthropicWebResearcher,
)
from thesis_factory.primary_source.dataset_candidates import (
    deterministic_dataset_candidates,
)
from thesis_factory.primary_source.legal_candidates import (
    deterministic_legal_candidates,
)
from thesis_factory.primary_source.policy import (
    authority_hint,
)


_MAX_OBJECTIVE_CHARS = 1000


class AnthropicPrimarySourceScout:
    def __init__(
        self,
        researcher: AnthropicWebResearcher,
    ) -> None:
        self._researcher = researcher

    def discover(
        self,
        *,
        topic: str,
        task: ProposalVerificationTask,
    ) -> tuple[
        PrimarySourceCandidate,
        ...,
    ]:
        deterministic = (
            deterministic_legal_candidates(
                task
            )
        )

        if deterministic:
            return deterministic

        deterministic = (
            deterministic_dataset_candidates(
                task
            )
        )

        if deterministic:
            return deterministic

        objective = _build_bounded_objective(
            task
        )

        packet = (
            self._researcher.research(
                approved_topic=topic,
                objective=objective,
            )
        )

        return tuple(
            PrimarySourceCandidate(
                url=str(
                    citation.url
                ),
                title=citation.title,
                cited_text=(
                    citation.cited_text
                ),
            )
            for citation
            in packet.citations
        )


def _build_bounded_objective(
    task: ProposalVerificationTask,
) -> str:
    prefix = (
        "Locate the authoritative primary source "
        "needed to verify this requirement. "
        f"{authority_hint(task)} "
        "Return and cite the official page itself, "
        "not commentary. Prefer HTML containing the "
        "operative text or official dataset metadata. "
        "Requirement: "
    )

    suffix = " Verification need: "

    budget = (
        _MAX_OBJECTIVE_CHARS
        - len(prefix)
        - len(suffix)
    )

    if budget < 2:
        raise ValueError(
            "primary-source objective prefix "
            "exceeds configured objective limit"
        )

    question = " ".join(
        task.requirement.question.split()
    )

    need = " ".join(
        task.requirement.why_needed.split()
    )

    question_budget = min(
        len(question),
        max(
            1,
            int(
                budget * 0.62
            ),
        ),
    )

    bounded_question = _clip(
        question,
        question_budget,
    )

    remaining = (
        budget
        - len(bounded_question)
    )

    bounded_need = _clip(
        need,
        max(
            1,
            remaining,
        ),
    )

    objective = (
        prefix
        + bounded_question
        + suffix
        + bounded_need
    )

    if len(objective) > _MAX_OBJECTIVE_CHARS:
        objective = objective[
            :_MAX_OBJECTIVE_CHARS
        ]

    return objective


def _clip(
    value: str,
    limit: int,
) -> str:
    if len(value) <= limit:
        return value

    if limit <= 1:
        return value[:limit]

    return (
        value[
            :limit - 1
        ].rstrip()
        + "…"
    )
