import pytest

from thesis_factory.domain.document import (
    DocumentSectionKind,
    SectionHeadingRole,
)
from thesis_factory.domain.retrieval import (
    RetrievalHit,
    RetrievalUnit,
)
from thesis_factory.retrieval.hybrid import (
    HybridRetriever,
)


SHA256 = "a" * 64


def _unit(
        paragraph: int,
        *,
        text: str | None = None,
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
        section_ordinal=1,
        section_path=("Results",),
        section_kind=(
            DocumentSectionKind.BODY
        ),
        heading_role=(
            SectionHeadingRole.STANDARD
        ),
        paragraph_ordinal=paragraph,
        text=(
                text
                or f"Paragraph {paragraph}"
        ),
    )


def _hit(
        paragraph: int,
        *,
        score: float,
        text: str | None = None,
) -> RetrievalHit:
    return RetrievalHit(
        unit=_unit(
            paragraph,
            text=text,
        ),
        score=score,
    )


class FakeRetriever:
    def __init__(
            self,
            hits: tuple[
                RetrievalHit,
                ...,
            ],
    ) -> None:
        self._hits = hits

        self.requested_top_k: list[
            int
        ] = []

    def search(
            self,
            query: str,
            *,
            top_k: int = 10,
    ) -> tuple[
        RetrievalHit,
        ...
    ]:
        self.requested_top_k.append(
            top_k
        )

        return self._hits[
            :top_k
        ]


def test_consensus_result_ranks_first() -> None:
    lexical = FakeRetriever(
        (
            _hit(
                1,
                score=100.0,
            ),
            _hit(
                2,
                score=90.0,
            ),
            _hit(
                3,
                score=80.0,
            ),
        )
    )

    semantic = FakeRetriever(
        (
            _hit(
                2,
                score=0.9,
            ),
            _hit(
                4,
                score=0.8,
            ),
            _hit(
                5,
                score=0.7,
            ),
        )
    )

    retriever = HybridRetriever(
        lexical_retriever=lexical,
        semantic_retriever=semantic,
    )

    hits = retriever.search(
        "credit risk",
        top_k=5,
    )

    assert (
            hits[0]
            .unit
            .paragraph_ordinal
            == 2
    )


def test_preserves_candidates_from_both_retrievers() -> None:
    lexical = FakeRetriever(
        (
            _hit(
                1,
                score=2.0,
            ),
            _hit(
                2,
                score=1.0,
            ),
        )
    )

    semantic = FakeRetriever(
        (
            _hit(
                3,
                score=0.9,
            ),
            _hit(
                4,
                score=0.8,
            ),
        )
    )

    retriever = HybridRetriever(
        lexical_retriever=lexical,
        semantic_retriever=semantic,
    )

    hits = retriever.search(
        "example",
        top_k=4,
    )

    assert {
               hit.unit.paragraph_ordinal
               for hit in hits
           } == {
               1,
               2,
               3,
               4,
           }


def test_requests_candidate_depth_before_final_cutoff() -> None:
    lexical = FakeRetriever(
        tuple(
            _hit(
                paragraph,
                score=float(
                    10 - paragraph
                ),
            )
            for paragraph
            in range(
                1,
                6,
            )
        )
    )

    semantic = FakeRetriever(
        tuple(
            _hit(
                paragraph,
                score=(
                        1.0
                        / paragraph
                ),
            )
            for paragraph
            in range(
                1,
                6,
            )
        )
    )

    retriever = HybridRetriever(
        lexical_retriever=lexical,
        semantic_retriever=semantic,
        candidate_k=4,
    )

    hits = retriever.search(
        "example",
        top_k=2,
    )

    assert (
            lexical.requested_top_k
            == [4]
    )

    assert (
            semantic.requested_top_k
            == [4]
    )

    assert len(hits) == 2


def test_raw_score_scale_does_not_change_fusion() -> None:
    first = HybridRetriever(
        lexical_retriever=(
            FakeRetriever(
                (
                    _hit(
                        1,
                        score=1000000.0,
                    ),
                    _hit(
                        2,
                        score=1.0,
                    ),
                )
            )
        ),
        semantic_retriever=(
            FakeRetriever(
                (
                    _hit(
                        2,
                        score=0.99,
                    ),
                    _hit(
                        1,
                        score=0.01,
                    ),
                )
            )
        ),
    )

    second = HybridRetriever(
        lexical_retriever=(
            FakeRetriever(
                (
                    _hit(
                        1,
                        score=0.00001,
                    ),
                    _hit(
                        2,
                        score=0.000001,
                    ),
                )
            )
        ),
        semantic_retriever=(
            FakeRetriever(
                (
                    _hit(
                        2,
                        score=999999.0,
                    ),
                    _hit(
                        1,
                        score=999998.0,
                    ),
                )
            )
        ),
    )

    first_ids = tuple(
        hit.unit.identity
        for hit
        in first.search(
            "example",
            top_k=2,
        )
    )

    second_ids = tuple(
        hit.unit.identity
        for hit
        in second.search(
            "example",
            top_k=2,
        )
    )

    assert (
            first_ids
            == second_ids
    )


def test_ties_are_deterministic() -> None:
    lexical = FakeRetriever(
        (
            _hit(
                1,
                score=10.0,
            ),
        )
    )

    semantic = FakeRetriever(
        (
            _hit(
                2,
                score=0.9,
            ),
        )
    )

    retriever = HybridRetriever(
        lexical_retriever=lexical,
        semantic_retriever=semantic,
    )

    hits = retriever.search(
        "example",
        top_k=2,
    )

    assert [
               hit.unit.paragraph_ordinal
               for hit in hits
           ] == [
               1,
               2,
           ]


def test_rejects_duplicate_units_from_child_retriever() -> None:
    duplicate = _hit(
        1,
        score=1.0,
    )

    retriever = HybridRetriever(
        lexical_retriever=(
            FakeRetriever(
                (
                    duplicate,
                    duplicate,
                )
            )
        ),
        semantic_retriever=(
            FakeRetriever(())
        ),
    )

    with pytest.raises(
            ValueError,
            match="duplicate unit identities",
    ):
        retriever.search(
            "example"
        )


def test_rejects_conflicting_units_for_same_identity() -> None:
    lexical = FakeRetriever(
        (
            _hit(
                1,
                score=10.0,
                text="First representation.",
            ),
        )
    )

    semantic = FakeRetriever(
        (
            _hit(
                1,
                score=0.9,
                text="Different representation.",
            ),
        )
    )

    retriever = HybridRetriever(
        lexical_retriever=lexical,
        semantic_retriever=semantic,
    )

    with pytest.raises(
            ValueError,
            match="conflicting units",
    ):
        retriever.search(
            "example"
        )


def test_rejects_invalid_configuration_and_query() -> None:
    empty = FakeRetriever(())

    with pytest.raises(
            ValueError,
            match="candidate_k",
    ):
        HybridRetriever(
            lexical_retriever=empty,
            semantic_retriever=empty,
            candidate_k=0,
        )

    with pytest.raises(
            ValueError,
            match="rrf_constant",
    ):
        HybridRetriever(
            lexical_retriever=empty,
            semantic_retriever=empty,
            rrf_constant=0,
        )

    retriever = HybridRetriever(
        lexical_retriever=empty,
        semantic_retriever=empty,
    )

    with pytest.raises(
            ValueError,
            match="query must not be empty",
    ):
        retriever.search(
            "   "
        )

    with pytest.raises(
            ValueError,
            match="top_k",
    ):
        retriever.search(
            "example",
            top_k=0,
        )