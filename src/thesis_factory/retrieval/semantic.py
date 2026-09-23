import math
from typing import Protocol

from thesis_factory.domain.retrieval import (
    RetrievalHit,
    RetrievalUnit,
)


EmbeddingVector = tuple[
    float,
    ...
]


class TextEmbedder(Protocol):
    def embed_documents(
            self,
            texts: tuple[
                str,
                ...,
            ],
    ) -> tuple[
        EmbeddingVector,
        ...
    ]:
        ...

    def embed_query(
            self,
            text: str,
    ) -> EmbeddingVector:
        ...


class SemanticRetriever:
    def __init__(
            self,
            units: tuple[
                RetrievalUnit,
                ...,
            ],
            *,
            embedder: TextEmbedder,
    ) -> None:
        if not units:
            raise ValueError(
                "retrieval corpus must not be empty"
            )

        _validate_unique_units(
            units
        )

        self._units = units
        self._embedder = embedder

        texts = tuple(
            _embedding_text(
                unit
            )
            for unit in units
        )

        embeddings = (
            embedder.embed_documents(
                texts
            )
        )

        if (
                len(embeddings)
                != len(units)
        ):
            raise ValueError(
                "embedder returned an unexpected "
                "number of document embeddings"
            )

        dimension = _validate_embeddings(
            embeddings
        )

        self._dimension = dimension
        self._document_embeddings = (
            embeddings
        )

    def search(
            self,
            query: str,
            *,
            top_k: int = 10,
    ) -> tuple[
        RetrievalHit,
        ...
    ]:
        if top_k < 1:
            raise ValueError(
                "top_k must be positive"
            )

        normalized_query = (
            query.strip()
        )

        if not normalized_query:
            raise ValueError(
                "query must not be empty"
            )

        query_embedding = (
            self._embedder
            .embed_query(
                normalized_query
            )
        )

        _validate_embedding(
            query_embedding
        )

        if (
                len(query_embedding)
                != self._dimension
        ):
            raise ValueError(
                "query embedding dimension "
                "does not match document embeddings"
            )

        scored = tuple(
            (
                index,
                _cosine_similarity(
                    query_embedding,
                    document_embedding,
                ),
            )
            for index, document_embedding
            in enumerate(
                self._document_embeddings
            )
        )

        ranked = sorted(
            scored,
            key=lambda item: (
                -item[1],
                item[0],
            ),
        )

        return tuple(
            RetrievalHit(
                unit=self._units[index],
                score=score,
            )
            for index, score
            in ranked[:top_k]
        )


def _embedding_text(
        unit: RetrievalUnit,
) -> str:
    return " ".join(
        (
            *unit.section_path,
            unit.text,
        )
    )


def _validate_embeddings(
        embeddings: tuple[
            EmbeddingVector,
            ...,
        ],
) -> int:
    if not embeddings:
        raise ValueError(
            "document embeddings must not be empty"
        )

    dimensions = {
        len(embedding)
        for embedding in embeddings
    }

    if (
            len(dimensions)
            != 1
    ):
        raise ValueError(
            "document embedding dimensions "
            "must be consistent"
        )

    for embedding in embeddings:
        _validate_embedding(
            embedding
        )

    return len(
        embeddings[0]
    )


def _validate_embedding(
        embedding: EmbeddingVector,
) -> None:
    if not embedding:
        raise ValueError(
            "embedding must not be empty"
        )

    if not all(
            math.isfinite(value)
            for value in embedding
    ):
        raise ValueError(
            "embedding values must be finite"
        )

    magnitude_squared = sum(
        value * value
        for value in embedding
    )

    if magnitude_squared == 0:
        raise ValueError(
            "embedding must not be a zero vector"
        )


def _cosine_similarity(
        left: EmbeddingVector,
        right: EmbeddingVector,
) -> float:
    if (
            len(left)
            != len(right)
    ):
        raise ValueError(
            "embedding dimensions do not match"
        )

    numerator = sum(
        left_value * right_value
        for left_value, right_value
        in zip(
            left,
            right,
            strict=True,
        )
    )

    left_norm = math.sqrt(
        sum(
            value * value
            for value in left
        )
    )

    right_norm = math.sqrt(
        sum(
            value * value
            for value in right
        )
    )

    return (
            numerator
            / (
                    left_norm
                    * right_norm
            )
    )


def _validate_unique_units(
        units: tuple[
            RetrievalUnit,
            ...,
        ],
) -> None:
    identities = [
        unit.identity
        for unit in units
    ]

    if (
            len(identities)
            != len(set(identities))
    ):
        raise ValueError(
            "retrieval corpus contains "
            "duplicate unit identities"
        )