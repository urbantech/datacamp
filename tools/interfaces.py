"""Base interfaces for BoomScraper tools."""
from abc import ABC, abstractmethod
from typing import Any, Dict


class ToolInterface(ABC):
    """Base interface for all Langflow-compatible tools."""

    @abstractmethod
    def __init__(self, **kwargs: Dict[str, Any]) -> None:
        """Initialize the tool with configuration parameters."""
        pass

    @abstractmethod
    def run(self, **kwargs: Dict[str, Any]) -> Any:
        """Execute the tool's main functionality."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the tool's name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Return the tool's description."""
        pass

    @property
    @abstractmethod
    def input_types(self) -> Dict[str, Any]:
        """Return the tool's input parameter types."""
        pass

    @property
    @abstractmethod
    def output_type(self) -> Any:
        """Return the tool's output type."""
        pass
