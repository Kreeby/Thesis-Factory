import pytest
from pydantic import (
    ValidationError,
)

from thesis_factory.domain.evidence import (
    EvidenceAddress,
)


SHA256 = "a" * 64


def test_evidence_address_accepts_valid_range() -> None:
    address = EvidenceAddress(
        artifact_sha256=SHA256,
        normalization_version=(
            "grobid-tei-v1"
        ),
        paragraph_ordinal=7,
        start_char=10,
        end_char=20,
    )

    assert (
            address.paragraph_ordinal
            == 7
    )

    assert (
            address.start_char
            == 10
    )

    assert (
            address.end_char
            == 20
    )


def test_evidence_address_rejects_empty_range() -> None:
    with pytest.raises(
            ValidationError,
    ):
        EvidenceAddress(
            artifact_sha256=SHA256,
            normalization_version=(
                "grobid-tei-v1"
            ),
            paragraph_ordinal=1,
            start_char=10,
            end_char=10,
        )


def test_evidence_address_rejects_reversed_range() -> None:
    with pytest.raises(
            ValidationError,
    ):
        EvidenceAddress(
            artifact_sha256=SHA256,
            normalization_version=(
                "grobid-tei-v1"
            ),
            paragraph_ordinal=1,
            start_char=20,
            end_char=10,
        )


def test_evidence_address_is_immutable() -> None:
    address = EvidenceAddress(
        artifact_sha256=SHA256,
        normalization_version=(
            "grobid-tei-v1"
        ),
        paragraph_ordinal=1,
        start_char=0,
        end_char=5,
    )

    with pytest.raises(
            ValidationError,
    ):
        address.start_char = 1