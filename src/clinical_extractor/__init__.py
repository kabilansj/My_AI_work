"""Clinical Text Extraction Package.

Extracts medications, diagnoses, investigations, and allergies from unstructured clinical notes.
"""

from .core import ClinicalNLP
from .models.entities import (
    AssertionStatus,
    MedicationStatus,
    InvestigationCategory,
    InvestigationFlag,
    AllergySeverity,
    AllergyType,
    AllergyStatus,
    ClinicalBaseEntity,
    Medication,
    Diagnosis,
    Investigation,
    Allergy,
)
from .models.result import ClinicalExtractionResult, ExtractionMetadata
from .extractors.base import BaseExtractor
from .extractors.local_extractor import LocalClinicalExtractor
from .extractors.llm_extractor import LLMClinicalExtractor

__version__ = "0.1.0"

__all__ = [
    "ClinicalNLP",
    "AssertionStatus",
    "MedicationStatus",
    "InvestigationCategory",
    "InvestigationFlag",
    "AllergySeverity",
    "AllergyType",
    "AllergyStatus",
    "ClinicalBaseEntity",
    "Medication",
    "Diagnosis",
    "Investigation",
    "Allergy",
    "ClinicalExtractionResult",
    "ExtractionMetadata",
    "BaseExtractor",
    "LocalClinicalExtractor",
    "LLMClinicalExtractor",
]
