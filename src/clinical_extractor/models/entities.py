"""Clinical entity domain models with strict validation and assertion tracking."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class AssertionStatus(str, Enum):
    """Clinical assertion / certainty status for diagnoses and findings."""
    CONFIRMED = "confirmed"
    SUSPECTED = "suspected"
    RULED_OUT = "ruled_out"
    HISTORICAL = "historical"
    FAMILY_HISTORY = "family_history"


class MedicationStatus(str, Enum):
    """Status of medication prescription/usage."""
    ACTIVE = "active"
    DISCONTINUED = "discontinued"
    PRN = "prn"  # As needed (pro re nata)
    HISTORICAL = "historical"
    UNKNOWN = "unknown"


class InvestigationCategory(str, Enum):
    """Category of diagnostic test or measurement."""
    LABORATORY = "laboratory"
    IMAGING = "imaging"
    PROCEDURE = "procedure"
    VITAL_SIGN = "vital_sign"
    OTHER = "other"


class InvestigationFlag(str, Enum):
    """Interpretive flag for diagnostic result."""
    NORMAL = "normal"
    HIGH = "high"
    LOW = "low"
    ABNORMAL = "abnormal"
    PENDING = "pending"
    UNKNOWN = "unknown"


class AllergySeverity(str, Enum):
    """Severity classification of allergic reactions."""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    LIFE_THREATENING = "life_threatening"
    UNKNOWN = "unknown"


class AllergyType(str, Enum):
    """Classification of the allergen source."""
    DRUG = "drug"
    FOOD = "food"
    ENVIRONMENTAL = "environmental"
    OTHER = "other"


class AllergyStatus(str, Enum):
    """Clinical allergy assertion status."""
    ACTIVE = "active"
    RESOLVED = "resolved"
    NKDA_REPORTED = "nkda_reported"  # No Known Drug Allergies
    UNKNOWN = "unknown"


class ClinicalBaseEntity(BaseModel):
    """Base model for clinical entities with source grounding and confidence."""
    model_config = ConfigDict(populate_by_name=True, extra="ignore", str_strip_whitespace=True)

    evidence_span: Optional[str] = Field(
        default=None,
        description="Exact quote or phrase from the clinical note supporting this extraction."
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence score for this extraction between 0.0 and 1.0."
    )


class Medication(ClinicalBaseEntity):
    """Extracted pharmaceutical agent or treatment."""
    name: str = Field(..., description="Name of medication (generic or brand).")
    dosage: Optional[str] = Field(default=None, description="Dose amount and unit, e.g., '500 mg', '10 mL'.")
    frequency: Optional[str] = Field(default=None, description="Dosing schedule, e.g., 'BID', 'daily', 'q8h prn'.")
    route: Optional[str] = Field(default=None, description="Route of administration, e.g., 'PO', 'IV', 'subcutaneous'.")
    status: MedicationStatus = Field(default=MedicationStatus.ACTIVE, description="Medication active or past status.")
    indication: Optional[str] = Field(default=None, description="Reason or diagnosis medication was prescribed for.")


class Diagnosis(ClinicalBaseEntity):
    """Extracted medical condition, symptom, or diagnosis."""
    condition_name: str = Field(..., description="Name of the diagnosis, syndrome, or symptom.")
    assertion: AssertionStatus = Field(
        default=AssertionStatus.CONFIRMED,
        description="Assertion status (e.g. confirmed, ruled out / negated, suspected, historical)."
    )
    acuity: Optional[str] = Field(default=None, description="Acuity of condition (e.g. acute, chronic, recurrent).")
    icd10_hint: Optional[str] = Field(default=None, description="Optional suggested ICD-10 code or category.")


class Investigation(ClinicalBaseEntity):
    """Extracted diagnostic test, lab panel, imaging, or vital observation."""
    test_name: str = Field(..., description="Name of the investigation or diagnostic test.")
    category: InvestigationCategory = Field(
        default=InvestigationCategory.LABORATORY,
        description="Type of test (laboratory, imaging, procedure, vitals)."
    )
    value: Optional[str] = Field(default=None, description="Observed result or qualitative interpretation.")
    unit: Optional[str] = Field(default=None, description="Measurement unit, e.g., 'mg/dL', 'mmol/L', '%'.")
    reference_range: Optional[str] = Field(default=None, description="Normal reference interval if documented.")
    flag: InvestigationFlag = Field(default=InvestigationFlag.UNKNOWN, description="Abnormality flag.")


class Allergy(ClinicalBaseEntity):
    """Extracted allergy, intolerance, or explicit NKDA assertion."""
    allergen: str = Field(..., description="Causative substance, medication class, or food.")
    reaction: Optional[str] = Field(default=None, description="Reported manifestation, e.g., 'hives', 'anaphylaxis', 'rash'.")
    severity: AllergySeverity = Field(default=AllergySeverity.UNKNOWN, description="Severity of reaction.")
    allergy_type: AllergyType = Field(default=AllergyType.DRUG, description="Type of allergen.")
    status: AllergyStatus = Field(default=AllergyStatus.ACTIVE, description="Status of the allergy or NKDA indicator.")
