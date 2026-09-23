import pytest

from thesis_factory.domain.document import (
    DocumentSectionKind,
    SectionHeadingRole,
)
from thesis_factory.domain.retrieval import (
    RetrievalUnit,
)
from thesis_factory.retrieval.bm25 import (
    BM25Retriever,
)


SHA256 = "a" * 64


def _unit(
        paragraph_ordinal: int,
        *,
        section: str,
        text: str,
) -> RetrievalUnit:
    return RetrievalUnit(
        artifact_sha256=SHA256,
        normalization_version=(
            "grobid-tei-v1"
        ),
        source_provider="openalex",
        source_provider_id=(
            "https://openalex.org/W123"
        ),
        section_ordinal=(
            paragraph_ordinal
        ),
        section_path=(
            section,
        ),
        section_kind=(
            DocumentSectionKind.BODY
        ),
        heading_role=(
            SectionHeadingRole.STANDARD
        ),
        paragraph_ordinal=(
            paragraph_ordinal
        ),
        text=text,
    )


def _units() -> tuple[
    RetrievalUnit,
    ...
]:
    return (
        _unit(
            1,
            section="Introduction",
            text=(
                "Credit risk modelling "
                "is important for banks."
            ),
        ),
        _unit(
            2,
            section=(
                "Machine Learning Models"
            ),
            text=(
                "Random forests and "
                "gradient boosted trees "
                "are evaluated."
            ),
        ),
        _unit(
            3,
            section="Backtesting",
            text=(
                "Predicted probabilities "
                "are compared with "
                "realized defaults."
            ),
        ),
        _unit(
            4,
            section="Credit Allocation",
            text=(
                "Safer borrowers receive "
                "credit before riskier "
                "borrowers."
            ),
        ),
    )


def test_ranks_matching_paragraph_first() -> None:
    retriever = BM25Retriever(
        _units()
    )

    hits = retriever.search(
        "random forest gradient boosted"
    )

    assert (
            hits[0].unit.paragraph_ordinal
            == 2
    )


def test_section_heading_is_searchable() -> None:
    retriever = BM25Retriever(
        _units()
    )

    hits = retriever.search(
        "backtesting"
    )

    assert (
            hits[0].unit.paragraph_ordinal
            == 3
    )


def test_search_is_case_insensitive() -> None:
    retriever = BM25Retriever(
        _units()
    )

    lower = retriever.search(
        "credit allocation"
    )

    upper = retriever.search(
        "CREDIT ALLOCATION"
    )

    assert lower == upper


def test_returns_only_positive_matches() -> None:
    retriever = BM25Retriever(
        _units()
    )

    hits = retriever.search(
        "quantum blockchain"
    )

    assert hits == ()


def test_respects_top_k() -> None:
    retriever = BM25Retriever(
        _units()
    )

    hits = retriever.search(
        "credit risk borrowers",
        top_k=1,
    )

    assert len(hits) == 1


def test_rejects_blank_query() -> None:
    retriever = BM25Retriever(
        _units()
    )

    with pytest.raises(
            ValueError,
            match="query must not be empty",
    ):
        retriever.search(
            "   "
        )


def test_rejects_duplicate_unit_identity() -> None:
    unit = _unit(
        1,
        section="Methods",
        text="Example.",
    )

    with pytest.raises(
            ValueError,
            match="duplicate unit identities",
    ):
        BM25Retriever(
            (
                unit,
                unit,
            )
        )