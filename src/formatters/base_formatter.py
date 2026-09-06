import abc
from typing import Dict, Any


class BaseFormatter(abc.ABC):
    """
    Abstract base class for all output formatters.
    Enforces a strict contract for any future format plugins (e.g. CSV, HTML).
    """

    @abc.abstractmethod
    def name(self) -> str:
        """Returns the format name used in the CLI (e.g., 'json', 'markdown')."""
        pass

    @abc.abstractmethod
    def format(self, data: Dict[str, Any]) -> str:
        """Takes the final enriched dictionary and returns a formatted string."""
        pass
