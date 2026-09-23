from enum import StrEnum
from typing import Protocol, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

from thesis_factory.domain.retrieval import (
    RetrievalHit,
    RetrievalUnitId,
)


class RetrievalQueryStyle(StrEnum):
    LEXICAL = "LEXICAL"
    PARAPHRASE = "PARAPHRASE"


class RetrievalEvalScope(StrEnum):
    SINGLE_DOCUMENT = "SINGLE_DOCUMENT"
    SOURCE_SELECTION = "SOURCE_SELECTION"
    CROSS_DOCUMENT = "CROSS_DOCUMENT"


class RetrievalTarget(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    id: str = Field(
        min_length=1,
    )

    acceptable_units: tuple[
        RetrievalUnitId,
        ...,
    ] = Field(
        min_length=1,
    )

    @model_validator(
        mode="after",
    )
    def validate_acceptable_units(
            self,
    ) -> Self:
        if (
                len(self.acceptable_units)
                != len(
            set(self.acceptable_units)
        )
        ):
            raise ValueError(
                "acceptable units must be unique"
            )

        return self


class RetrievalEvalCase(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    id: str = Field(
        min_length=1,
    )

    query_style: RetrievalQueryStyle

    scope: RetrievalEvalScope

    query: str = Field(
        min_length=1,
    )

    targets: tuple[
        RetrievalTarget,
        ...,
    ] = Field(
        min_length=1,
    )

    @model_validator(
        mode="after",
    )
    def validate_targets(
            self,
    ) -> Self:
        target_ids = [
            target.id
            for target in self.targets
        ]

        if (
                len(target_ids)
                != len(set(target_ids))
        ):
            raise ValueError(
                "target ids must be unique"
            )

        return self


class RetrievalEvalResult(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    case_id: str

    query_style: RetrievalQueryStyle

    scope: RetrievalEvalScope

    query: str

    top_k: int = Field(
        ge=1,
    )

    retrieved_units: tuple[
        RetrievalUnitId,
        ...,
    ]

    satisfied_target_ids: tuple[
        str,
        ...,
    ]

    hit_at_k: bool

    complete_at_k: bool

    target_coverage_at_k: float = Field(
        ge=0,
        le=1,
    )

    reciprocal_rank: float = Field(
        ge=0,
        le=1,
    )


class RetrievalEvalMetrics(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    case_count: int = Field(
        ge=1,
    )

    hit_rate_at_k: float = Field(
        ge=0,
        le=1,
    )

    complete_rate_at_k: float = Field(
        ge=0,
        le=1,
    )

    mean_target_coverage_at_k: float = Field(
        ge=0,
        le=1,
    )

    mean_reciprocal_rank: float = Field(
        ge=0,
        le=1,
    )


class RetrievalEvalReport(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    top_k: int = Field(
        ge=1,
    )

    results: tuple[
        RetrievalEvalResult,
        ...,
    ] = Field(
        min_length=1,
    )

    overall: RetrievalEvalMetrics


class Retriever(Protocol):
    def search(
            self,
            query: str,
            *,
            top_k: int = 10,
    ) -> tuple[
        RetrievalHit,
        ...
    ]:
        ...


def evaluate_retriever(
        retriever: Retriever,
        cases: tuple[
            RetrievalEvalCase,
            ...,
        ],
        *,
        top_k: int = 5,
) -> RetrievalEvalReport:
    if not cases:
        raise ValueError(
            "evaluation cases must not be empty"
        )

    if top_k < 1:
        raise ValueError(
            "top_k must be positive"
        )

    results = tuple(
        _evaluate_case(
            retriever,
            case,
            top_k=top_k,
        )
        for case in cases
    )

    return RetrievalEvalReport(
        top_k=top_k,
        results=results,
        overall=(
            summarize_eval_results(
                results
            )
        ),
    )


def summarize_eval_results(
        results: tuple[
            RetrievalEvalResult,
            ...,
        ],
) -> RetrievalEvalMetrics:
    if not results:
        raise ValueError(
            "evaluation results must not be empty"
        )

    count = len(results)

    return RetrievalEvalMetrics(
        case_count=count,
        hit_rate_at_k=(
                sum(
                    1
                    for result in results
                    if result.hit_at_k
                )
                / count
        ),
        complete_rate_at_k=(
                sum(
                    1
                    for result in results
                    if result.complete_at_k
                )
                / count
        ),
        mean_target_coverage_at_k=(
                sum(
                    result.target_coverage_at_k
                    for result in results
                )
                / count
        ),
        mean_reciprocal_rank=(
                sum(
                    result.reciprocal_rank
                    for result in results
                )
                / count
        ),
    )


def _evaluate_case(
        retriever: Retriever,
        case: RetrievalEvalCase,
        *,
        top_k: int,
) -> RetrievalEvalResult:
    hits = retriever.search(
        case.query,
        top_k=top_k,
    )

    retrieved = tuple(
        hit.unit.identity
        for hit in hits
    )

    if (
            len(retrieved)
            != len(set(retrieved))
    ):
        raise ValueError(
            "retriever returned duplicate units"
        )

    retrieved_set = set(
        retrieved
    )

    satisfied_targets = tuple(
        target.id
        for target in case.targets
        if (
                retrieved_set
                & set(target.acceptable_units)
        )
    )

    all_acceptable_units = set(
        unit
        for target in case.targets
        for unit in target.acceptable_units
    )

    reciprocal_rank = 0.0

    for rank, unit_id in enumerate(
            retrieved,
            start=1,
    ):
        if (
                unit_id
                in all_acceptable_units
        ):
            reciprocal_rank = (
                    1.0 / rank
            )
            break

    target_count = len(
        case.targets
    )

    coverage = (
            len(satisfied_targets)
            / target_count
    )

    return RetrievalEvalResult(
        case_id=case.id,
        query_style=case.query_style,
        scope=case.scope,
        query=case.query,
        top_k=top_k,
        retrieved_units=retrieved,
        satisfied_target_ids=(
            satisfied_targets
        ),
        hit_at_k=bool(
            satisfied_targets
        ),
        complete_at_k=(
                len(satisfied_targets)
                == target_count
        ),
        target_coverage_at_k=coverage,
        reciprocal_rank=(
            reciprocal_rank
        ),
    )