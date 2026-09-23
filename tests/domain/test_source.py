import pytest
from pydantic import ValidationError

from thesis_factory.domain.source import SourceRecord


def test_source_record_accepts_valid_source() -> None:
    source = SourceRecord(
        title="Machine Learning in Credit Risk Assessment",
        authors=("Alice Smith", "Bob Jones"),
        publication_year=2025,
        doi="10.1234/example",
        abstract="An example abstract.",
        venue="Example Journal",
        provider="openalex",
        provider_id="W123456789",
    )

    assert source.title == "Machine Learning in Credit Risk Assessment"
    assert source.provider == "openalex"
    assert source.provider_id == "W123456789"


def test_source_record_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        SourceRecord(
            title="Example",
            provider="openalex",
            provider_id="W123",
            hallucinated_field="should not exist",
        )

def test_source_record_normalizes_doi_url() -> None:
    source = SourceRecord(
        title="Example",
        provider="openalex",
        provider_id="W123",
        doi="https://doi.org/10.1234/example",
    )

    assert source.doi == "10.1234/example"

def test_source_record_decodes_html_entities() -> None:
    source = SourceRecord(
        title="Example",
        venue="Journal of Banking &amp; Finance",
        provider="crossref",
        provider_id="10.1234/example",
    )

    assert source.venue == "Journal of Banking & Finance"