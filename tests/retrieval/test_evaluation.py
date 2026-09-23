import pytest

from thesis_factory.domain.document import (
    DocumentSectionKind,
    SectionHeadingRole,
)
from thesis_factory.domain.retrieval import (
    RetrievalHit,
    RetrievalUnit,
    RetrievalUnitId,
)
from thesis_factory.retrieval.evaluation import (
    RetrievalEvalCase,
    RetrievalEvalScope,
    RetrievalQueryStyle,
    RetrievalTarget,
    evaluate_retriever,
)


def _unit(
        artifact: str,
        paragraph: int,
) -> RetrievalUnit:
    return RetrievalUnit(
        artifact_sha256=artifact,
        normalization_version=(
            "grobid-tei-v1"
        ),
        source_provider="openalex",
        source_provider_id=(
            f"work-{artifact[0]}"
        ),
        section_ordinal=1,
        section_path=("Results",),
        section_kind=(
            DocumentSectionKind.BODY
        ),
        heading_role=(
            SectionHeadingRole.STANDARD
        ),
        paragraph_ordinal=paragraph,
        text=f"Paragraph {paragraph}",
    )


class FakeRetriever:
    def __init__(
            self,
            units: tuple[
                RetrievalUnit,
                ...,
            ],
    ) -> None:
        self._units = units

    def search(
            self,
            query: str,
            *,
            top_k: int = 10,
    ) -> tuple[
        RetrievalHit,
        ...
    ]:
        return tuple(
            RetrievalHit(
                unit=unit,
                score=float(
                    len(self._units)
                    - index
                ),
            )
            for index, unit
            in enumerate(
                self._units[:top_k]
            )
        )


def _id(
        artifact: str,
        paragraph: int,
) -> RetrievalUnitId:
    return RetrievalUnitId(
        artifact_sha256=artifact,
        normalization_version=(
            "grobid-tei-v1"
        ),
        paragraph_ordinal=paragraph,
    )


def _target(
        target_id: str,
        *units: RetrievalUnitId,
) -> RetrievalTarget:
    return RetrievalTarget(
        id=target_id,
        acceptable_units=units,
    )


def _case(
        *targets: RetrievalTarget,
) -> RetrievalEvalCase:
    return RetrievalEvalCase(
        id="case-1",
        query_style=(
            RetrievalQueryStyle.PARAPHRASE
        ),
        scope=(
            RetrievalEvalScope
            .SINGLE_DOCUMENT
        ),
        query="example",
        targets=targets,
    )


def test_identity_distinguishes_documents() -> None:
    first = _unit(
        "a" * 64,
        1,
        )

    second = _unit(
        "b" * 64,
        1,
        )

    assert (
            first.identity
            != second.identity
    )


def test_evaluates_hit_and_reciprocal_rank() -> None:
    retriever = FakeRetriever(
        (
            _unit(
                "a" * 64,
                1,
                ),
            _unit(
                "a" * 64,
                2,
                ),
            _unit(
                "a" * 64,
                3,
                ),
        )
    )

    report = evaluate_retriever(
        retriever,
        (
            _case(
                _target(
                    "answer",
                    _id(
                        "a" * 64,
                        2,
                        ),
                ),
            ),
        ),
        top_k=3,
    )

    result = report.results[0]

    assert result.hit_at_k is True
    assert result.complete_at_k is True

    assert (
            result.target_coverage_at_k
            == 1.0
    )

    assert (
            result.reciprocal_rank
            == 0.5
    )


def test_one_passage_can_satisfy_target() -> None:
    retriever = FakeRetriever(
        (
            _unit(
                "a" * 64,
                2,
                ),
        )
    )

    result = evaluate_retriever(
        retriever,
        (
            _case(
                _target(
                    "answer",
                    _id(
                        "a" * 64,
                        1,
                        ),
                    _id(
                        "a" * 64,
                        2,
                        ),
                ),
            ),
        ),
    ).results[0]

    assert result.hit_at_k is True
    assert result.complete_at_k is True

    assert (
            result.target_coverage_at_k
            == 1.0
    )


def test_evaluates_partial_target_coverage() -> None:
    retriever = FakeRetriever(
        (
            _unit(
                "a" * 64,
                1,
                ),
            _unit(
                "a" * 64,
                9,
                ),
        )
    )

    case = _case(
        _target(
            "first",
            _id(
                "a" * 64,
                1,
                ),
        ),
        _target(
            "second",
            _id(
                "b" * 64,
                2,
                ),
        ),
    )

    result = evaluate_retriever(
        retriever,
        (case,),
    ).results[0]

    assert result.hit_at_k is True
    assert result.complete_at_k is False

    assert (
            result.target_coverage_at_k
            == 0.5
    )

    assert (
            result.satisfied_target_ids
            == ("first",)
    )


def test_evaluates_no_hit() -> None:
    retriever = FakeRetriever(
        (
            _unit(
                "a" * 64,
                1,
                ),
        )
    )

    result = evaluate_retriever(
        retriever,
        (
            _case(
                _target(
                    "answer",
                    _id(
                        "b" * 64,
                        9,
                        ),
                ),
            ),
        ),
    ).results[0]

    assert result.hit_at_k is False
    assert result.complete_at_k is False

    assert (
            result.target_coverage_at_k
            == 0.0
    )

    assert (
            result.reciprocal_rank
            == 0.0
    )


def test_report_aggregates_metrics() -> None:
    retriever = FakeRetriever(
        (
            _unit(
                "a" * 64,
                1,
                ),
        )
    )

    cases = (
        _case(
            _target(
                "one",
                _id(
                    "a" * 64,
                    1,
                    ),
            ),
        ),
        RetrievalEvalCase(
            id="case-2",
            query_style=(
                RetrievalQueryStyle.PARAPHRASE
            ),
            scope=(
                RetrievalEvalScope
                .CROSS_DOCUMENT
            ),
            query="two",
            targets=(
                _target(
                    "a",
                    _id(
                        "a" * 64,
                        1,
                        ),
                ),
                _target(
                    "b",
                    _id(
                        "b" * 64,
                        1,
                        ),
                ),
            ),
        ),
    )

    report = evaluate_retriever(
        retriever,
        cases,
    )

    assert (
            report.overall.case_count
            == 2
    )

    assert (
            report.overall.hit_rate_at_k
            == 1.0
    )

    assert (
            report.overall.complete_rate_at_k
            == 0.5
    )

    assert (
            report.overall
            .mean_target_coverage_at_k
            == 0.75
    )

    assert (
            report.overall.mean_reciprocal_rank
            == 1.0
    )


def test_target_rejects_duplicate_acceptable_units() -> None:
    unit_id = _id(
        "a" * 64,
        1,
        )

    with pytest.raises(
            ValueError,
            match=(
                    "acceptable units "
                    "must be unique"
            ),
    ):
        RetrievalTarget(
            id="target",
            acceptable_units=(
                unit_id,
                unit_id,
            ),
        )


def test_case_rejects_duplicate_target_ids() -> None:
    first = _target(
        "same",
        _id(
            "a" * 64,
            1,
            ),
    )

    second = _target(
        "same",
        _id(
            "b" * 64,
            1,
            ),
    )

    with pytest.raises(
            ValueError,
            match="target ids must be unique",
    ):
        _case(
            first,
            second,
        )


def test_evaluation_rejects_empty_cases() -> None:
    retriever = FakeRetriever(
        (
            _unit(
                "a" * 64,
                1,
                ),
        )
    )

    with pytest.raises(
            ValueError,
            match=(
                    "evaluation cases "
                    "must not be empty"
            ),
    ):
        evaluate_retriever(
            retriever,
            (),
        )