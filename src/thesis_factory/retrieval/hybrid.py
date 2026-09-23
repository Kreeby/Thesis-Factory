from typing import Protocol

from thesis_factory.domain.retrieval import (
    RetrievalHit,
    RetrievalUnit,
    RetrievalUnitId,
)


class RankedRetriever(Protocol):
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


class HybridRetriever:
    def __init__(
            self,
            *,
            lexical_retriever: RankedRetriever,
            semantic_retriever: RankedRetriever,
            candidate_k: int = 20,
            rrf_constant: float = 60.0,
    ) -> None:
        if candidate_k < 1:
            raise ValueError(
                "candidate_k must be positive"
            )

        if rrf_constant <= 0:
            raise ValueError(
                "rrf_constant must be positive"
            )

        self._lexical_retriever = (
            lexical_retriever
        )

        self._semantic_retriever = (
            semantic_retriever
        )

        self._candidate_k = (
            candidate_k
        )

        self._rrf_constant = (
            rrf_constant
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
        normalized_query = (
            query.strip()
        )

        if not normalized_query:
            raise ValueError(
                "query must not be empty"
            )

        if top_k < 1:
            raise ValueError(
                "top_k must be positive"
            )

        candidate_depth = max(
            self._candidate_k,
            top_k,
        )

        lexical_hits = (
            self._lexical_retriever
            .search(
                normalized_query,
                top_k=candidate_depth,
            )
        )

        semantic_hits = (
            self._semantic_retriever
            .search(
                normalized_query,
                top_k=candidate_depth,
            )
        )

        _validate_unique_hits(
            lexical_hits
        )

        _validate_unique_hits(
            semantic_hits
        )

        units: dict[
            RetrievalUnitId,
            RetrievalUnit,
        ] = {}

        scores: dict[
            RetrievalUnitId,
            float,
        ] = {}

        for hits in (
                lexical_hits,
                semantic_hits,
        ):
            for rank, hit in enumerate(
                    hits,
                    start=1,
            ):
                identity = (
                    hit.unit.identity
                )

                existing = units.get(
                    identity
                )

                if (
                        existing is not None
                        and existing != hit.unit
                ):
                    raise ValueError(
                        "retrievers returned "
                        "conflicting units for "
                        "the same identity"
                    )

                units[
                    identity
                ] = hit.unit

                contribution = (
                        1.0
                        / (
                                self._rrf_constant
                                + rank
                        )
                )

                scores[
                    identity
                ] = (
                        scores.get(
                            identity,
                            0.0,
                        )
                        + contribution
                )

        ranked_identities = sorted(
            scores,
            key=lambda identity: (
                -scores[identity],
                identity.artifact_sha256,
                identity.normalization_version,
                identity.paragraph_ordinal,
            ),
        )

        return tuple(
            RetrievalHit(
                unit=units[identity],
                score=scores[identity],
            )
            for identity
            in ranked_identities[:top_k]
        )


def _validate_unique_hits(
        hits: tuple[
            RetrievalHit,
            ...,
        ],
) -> None:
    identities = [
        hit.unit.identity
        for hit in hits
    ]

    if (
            len(identities)
            != len(set(identities))
    ):
        raise ValueError(
            "child retriever returned "
            "duplicate unit identities"
        )