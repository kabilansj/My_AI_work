"""Root result model encapsulating all extracted clinical categories and metadata."""

from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

from .entities import (
    Medication,
    Diagnosis,
    Investigation,
    Allergy,
    MedicationStatus,
    AssertionStatus,
    AllergyStatus,
)


class ExtractionMetadata(BaseModel):
    """Metadata tracking the execution context, model, and performance."""
    model_config = ConfigDict(extra="ignore")

    engine: str = Field(default="unknown", description="Extraction engine used (e.g. 'llm', 'local_rules').")
    model_name: Optional[str] = Field(default=None, description="Specific underlying model or version identifier.")
    extracted_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 UTC timestamp of extraction."
    )
    char_count: int = Field(default=0, description="Character length of input text.")
    word_count: int = Field(default=0, description="Word count of input text.")
    processing_time_ms: float = Field(default=0.0, description="Elapsed processing time in milliseconds.")
    warnings: List[str] = Field(default_factory=list, description="Any warnings or validation notices encountered.")


class ClinicalExtractionResult(BaseModel):
    """Structured extraction result containing the four core clinical entity categories."""
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    medications: List[Medication] = Field(
        default_factory=list,
        description="List of pharmaceutical agents, prescriptions, and over-the-counter treatments."
    )
    diagnoses: List[Diagnosis] = Field(
        default_factory=list,
        description="List of medical conditions, signs, symptoms, and diagnostic impressions."
    )
    investigations: List[Investigation] = Field(
        default_factory=list,
        description="List of lab tests, imaging studies, and diagnostic procedures with results."
    )
    allergies: List[Allergy] = Field(
        default_factory=list,
        description="List of allergies, adverse drug reactions, and NKDA affirmations."
    )
    metadata: ExtractionMetadata = Field(
        default_factory=ExtractionMetadata,
        description="Technical and document-level metadata."
    )

    # Convenient accessors / filters
    def active_medications(self) -> List[Medication]:
        """Return only active or PRN medications."""
        return [m for m in self.medications if m.status in (MedicationStatus.ACTIVE, MedicationStatus.PRN)]

    def confirmed_diagnoses(self) -> List[Diagnosis]:
        """Return only confirmed or active diagnoses (excluding ruled out / negated)."""
        return [d for d in self.diagnoses if d.assertion == AssertionStatus.CONFIRMED]

    def ruled_out_diagnoses(self) -> List[Diagnosis]:
        """Return diagnoses that were explicitly negated or ruled out."""
        return [d for d in self.diagnoses if d.assertion == AssertionStatus.RULED_OUT]

    def has_nkda(self) -> bool:
        """Check if 'No Known Drug Allergies' (NKDA) was explicitly documented."""
        return any(a.status == AllergyStatus.NKDA_REPORTED for a in self.allergies)

    def to_markdown_report(self) -> str:
        """Generate a clean, structured clinical summary in Markdown format."""
        lines = [
            "# Clinical Extraction Summary",
            f"**Engine**: `{self.metadata.engine}` | **Words**: {self.metadata.word_count} | **Time**: {self.metadata.processing_time_ms:.1f}ms",
            "",
            "## 1. Medications",
        ]
        if not self.medications:
            lines.append("_No medications identified._")
        else:
            lines.append("| Medication | Dosage | Frequency | Route | Status | Indication |")
            lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
            for m in self.medications:
                lines.append(
                    f"| **{m.name}** | {m.dosage or '-'} | {m.frequency or '-'} | {m.route or '-'} | {m.status.value} | {m.indication or '-'} |"
                )

        lines.extend(["", "## 2. Diagnoses & Conditions"])
        if not self.diagnoses:
            lines.append("_No diagnoses identified._")
        else:
            lines.append("| Condition | Assertion | Acuity | Evidence |")
            lines.append("| :--- | :--- | :--- | :--- |")
            for d in self.diagnoses:
                assertion_badge = f"`{d.assertion.value}`"
                lines.append(
                    f"| **{d.condition_name}** | {assertion_badge} | {d.acuity or '-'} | _{d.evidence_span or '-'}_ |"
                )

        lines.extend(["", "## 3. Investigations (Labs & Imaging)"])
        if not self.investigations:
            lines.append("_No investigations identified._")
        else:
            lines.append("| Test Name | Category | Result / Value | Flag | Evidence |")
            lines.append("| :--- | :--- | :--- | :--- | :--- |")
            for inv in self.investigations:
                flag_str = f"**{inv.flag.value.upper()}**" if inv.flag.value in ("high", "low", "abnormal") else inv.flag.value
                val_str = f"{inv.value or ''} {inv.unit or ''}".strip() or "-"
                lines.append(
                    f"| **{inv.test_name}** | {inv.category.value} | {val_str} | {flag_str} | _{inv.evidence_span or '-'}_ |"
                )

        lines.extend(["", "## 4. Allergies"])
        if not self.allergies:
            lines.append("_No allergies documented._")
        else:
            lines.append("| Allergen | Reaction | Severity | Status |")
            lines.append("| :--- | :--- | :--- | :--- |")
            for a in self.allergies:
                lines.append(
                    f"| **{a.allergen}** | {a.reaction or '-'} | {a.severity.value} | `{a.status.value}` |"
                )

        return "\n".join(lines)
