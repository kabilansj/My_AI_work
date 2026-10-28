"""Abstract base extractor interface."""

from abc import ABC, abstractmethod
from ..models.result import ClinicalExtractionResult


class BaseExtractor(ABC):
    """Abstract base class for all clinical entity extraction engines."""

    @abstractmethod
    def extract(self, text: str) -> ClinicalExtractionResult:
        """Extract medications, diagnoses, investigations, and allergies from clinical text.

        Args:
            text: Raw or preprocessed clinical note.

        Returns:
            ClinicalExtractionResult containing lists of validated entities.
        """
        pass
