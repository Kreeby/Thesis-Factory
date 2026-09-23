from typing import Protocol, TypeVar

from pydantic import BaseModel


T = TypeVar("T", bound=BaseModel)


class StructuredReasoner(Protocol):
    def generate(
            self,
            *,
            system: str,
            prompt: str,
            output_model: type[T],
    ) -> T:
        ...