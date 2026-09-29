"""Common contract for stateless LLM providers."""

from abc import ABC, abstractmethod


class ILLM(ABC):
    """Interface implemented by every model provider."""

    @abstractmethod
    def list_models(self) -> tuple[list[str], str | None]:
        """Return available model identifiers and an optional error."""

    @abstractmethod
    def call(self, model: str, prompt: str) -> tuple[str | None, str | None]:
        """Call one selected model and return (response, error)."""
