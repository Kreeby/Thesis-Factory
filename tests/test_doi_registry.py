from thesis_factory.domain.source import SourceRecord
from thesis_factory.verification.doi_registry import (
    CompositeDoiRegistry,
)


class MissingProvider:
    def __init__(self) -> None:
        self.calls = 0

    def get_work_by_doi(
            self,
            doi: str,
    ) -> SourceRecord | None:
        self.calls += 1
        return None


class SuccessfulProvider:
    def __init__(self) -> None:
        self.calls = 0

    def get_work_by_doi(
            self,
            doi: str,
    ) -> SourceRecord | None:
        self.calls += 1

        return SourceRecord(
            title="Example",
            doi=doi,
            provider="datacite",
            provider_id=doi,
        )


def test_registry_falls_back_to_next_provider() -> None:
    first = MissingProvider()
    second = SuccessfulProvider()

    registry = CompositeDoiRegistry(
        first,
        second,
    )

    result = registry.get_work_by_doi(
        "10.1234/example"
    )

    assert result is not None
    assert result.provider == "datacite"

    assert first.calls == 1
    assert second.calls == 1