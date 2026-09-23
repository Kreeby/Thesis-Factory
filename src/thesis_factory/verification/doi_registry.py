from typing import Protocol

from thesis_factory.domain.source import SourceRecord


class DoiMetadataProvider(Protocol):
    def get_work_by_doi(
            self,
            doi: str,
    ) -> SourceRecord | None:
        ...


class CompositeDoiRegistry:
    def __init__(
            self,
            *providers: DoiMetadataProvider,
    ) -> None:
        if not providers:
            raise ValueError(
                "at least one DOI metadata provider is required"
            )

        self._providers = providers

    def get_work_by_doi(
            self,
            doi: str,
    ) -> SourceRecord | None:
        for provider in self._providers:
            source = provider.get_work_by_doi(
                doi
            )

            if source is not None:
                return source

        return None