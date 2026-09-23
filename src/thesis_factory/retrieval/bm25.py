import math
import re
from collections import Counter

from thesis_factory.domain.retrieval import (
    RetrievalHit,
    RetrievalUnit,
)


_TOKEN_PATTERN = re.compile(
    r"\w+",
    flags=re.UNICODE,
)


class BM25Retriever:
    def __init__(
            self,
            units: tuple[
                RetrievalUnit,
                ...,
            ],
            *,
            k1: float = 1.5,
            b: float = 0.75,
    ) -> None:
        if not units:
            raise ValueError(
                "retrieval corpus must not be empty"
            )

        if k1 <= 0:
            raise ValueError(
                "k1 must be positive"
            )

        if not 0 <= b <= 1:
            raise ValueError(
                "b must be between 0 and 1"
            )

        _validate_unique_units(
            units
        )

        self._units = units
        self._k1 = k1
        self._b = b

        self._documents = tuple(
            _tokenize(
                _index_text(unit)
            )
            for unit in units
        )

        self._term_frequencies = tuple(
            Counter(document)
            for document in self._documents
        )

        self._document_lengths = tuple(
            len(document)
            for document in self._documents
        )

        self._average_document_length = (
                sum(
                    self._document_lengths
                )
                / len(
            self._document_lengths
        )
        )

        document_frequency: Counter[
            str
        ] = Counter()

        for document in self._documents:
            document_frequency.update(
                set(document)
            )

        self._document_frequency = (
            document_frequency
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

        query_terms = tuple(
            dict.fromkeys(
                _tokenize(
                    normalized_query
                )
            )
        )

        if not query_terms:
            raise ValueError(
                "query must contain "
                "searchable terms"
            )

        scored: list[
            tuple[
                int,
                float,
            ]
        ] = []

        for index in range(
                len(self._units)
        ):
            score = self._score_document(
                index,
                query_terms,
            )

            if score <= 0:
                continue

            scored.append(
                (
                    index,
                    score,
                )
            )

        scored.sort(
            key=lambda item: (
                -item[1],
                item[0],
            )
        )

        return tuple(
            RetrievalHit(
                unit=self._units[index],
                score=score,
            )
            for index, score
            in scored[:top_k]
        )

    def _score_document(
            self,
            index: int,
            query_terms: tuple[
                str,
                ...,
            ],
    ) -> float:
        frequencies = (
            self._term_frequencies[
                index
            ]
        )

        document_length = (
            self._document_lengths[
                index
            ]
        )

        score = 0.0

        for term in query_terms:
            frequency = (
                frequencies.get(
                    term,
                    0,
                )
            )

            if frequency == 0:
                continue

            document_frequency = (
                self
                ._document_frequency
                .get(
                    term,
                    0,
                )
            )

            inverse_document_frequency = (
                math.log(
                    1
                    + (
                            (
                                    len(self._units)
                                    - document_frequency
                                    + 0.5
                            )
                            / (
                                    document_frequency
                                    + 0.5
                            )
                    )
                )
            )

            length_normalization = (
                    frequency
                    + self._k1
                    * (
                            1
                            - self._b
                            + self._b
                            * (
                                    document_length
                                    / self
                                    ._average_document_length
                            )
                    )
            )

            score += (
                    inverse_document_frequency
                    * (
                            frequency
                            * (
                                    self._k1
                                    + 1
                            )
                    )
                    / length_normalization
            )

        return score


def _index_text(
        unit: RetrievalUnit,
) -> str:
    return " ".join(
        (
            *unit.section_path,
            unit.text,
        )
    )


def _tokenize(
        text: str,
) -> tuple[
    str,
    ...
]:
    return tuple(
        match.group(0).casefold()
        for match
        in _TOKEN_PATTERN.finditer(
            text
        )
    )


def _validate_unique_units(
        units: tuple[
            RetrievalUnit,
            ...,
        ],
) -> None:
    identities = [
        (
            unit.artifact_sha256,
            unit.normalization_version,
            unit.paragraph_ordinal,
        )
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