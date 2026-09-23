import pytest

from thesis_factory.domain.document import (
    DocumentSectionKind,
    SectionHeadingRole,
)
from thesis_factory.domain.retrieval import (
    RetrievalUnit,
)
from thesis_factory.retrieval.semantic import (
    SemanticRetriever,
)


SHA256 = "a" * 64


def _unit(
        paragraph: int,
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
        section_ordinal=1,
        section_path=("Results",),
        section_kind=(
            DocumentSectionKind.BODY
        ),
        heading_role=(
            SectionHeadingRole.STANDARD
        ),
        paragraph_ordinal=paragraph,
        text=text,
    )


class FakeEmbedder:
    def embed_documents(
            self,
            texts: tuple[
                str,
                ...,
            ],
    ) -> tuple[
        tuple[
            float,
            ...,
        ],
        ...
    ]:
        assert texts == (
            "Results cats",
            "Results credit",
            "Results weather",
        )

        return (
            (
                1.0,
                0.0,
            ),
            (
                0.0,
                1.0,
            ),
            (
                -1.0,
                0.0,
            ),
        )

    def embed_query(
            self,
            text: str,
    ) -> tuple[
        float,
        ...,
    ]:
        assert text == (
            "borrower default risk"
        )

        return (
            0.0,
            1.0,
        )


def _retriever() -> SemanticRetriever:
    return SemanticRetriever(
        (
            _unit(
                1,
                "cats",
            ),
            _unit(
                2,
                "credit",
            ),
            _unit(
                3,
                "weather",
            ),
        ),
        embedder=FakeEmbedder(),
    )


def test_ranks_by_cosine_similarity() -> None:
    hits = _retriever().search(
        "borrower default risk"
    )

    assert (
            hits[0]
            .unit
            .paragraph_ordinal
            == 2
    )

    assert (
            hits[0].score
            == pytest.approx(
        1.0
    )
    )


def test_semantic_scores_may_be_negative() -> None:
    hits = _retriever().search(
        "borrower default risk"
    )

    assert (
            hits[-1].score
            <= 0
    )


def test_respects_top_k() -> None:
    hits = _retriever().search(
        "borrower default risk",
        top_k=1,
    )

    assert len(hits) == 1


def test_rejects_blank_query() -> None:
    retriever = _retriever()

    with pytest.raises(
            ValueError,
            match="query must not be empty",
    ):
        retriever.search(
            "   "
        )


def test_rejects_query_dimension_mismatch() -> None:
    class BadQueryEmbedder(
        FakeEmbedder
    ):
        def embed_query(
                self,
                text: str,
        ) -> tuple[
            float,
            ...,
        ]:
            return (
                1.0,
                2.0,
                3.0,
            )

    retriever = SemanticRetriever(
        (
            _unit(
                1,
                "cats",
            ),
            _unit(
                2,
                "credit",
            ),
            _unit(
                3,
                "weather",
            ),
        ),
        embedder=(
            BadQueryEmbedder()
        ),
    )

    with pytest.raises(
            ValueError,
            match="dimension",
    ):
        retriever.search(
            "borrower default risk"
        )


def test_rejects_zero_document_embedding() -> None:
    class ZeroEmbedder:
        def embed_documents(
                self,
                texts,
        ):
            return (
                (
                    0.0,
                    0.0,
                ),
            )

        def embed_query(
                self,
                text,
        ):
            return (
                1.0,
                0.0,
            )

    with pytest.raises(
            ValueError,
            match="zero vector",
    ):
        SemanticRetriever(
            (
                _unit(
                    1,
                    "credit",
                ),
            ),
            embedder=(
                ZeroEmbedder()
            ),
        )