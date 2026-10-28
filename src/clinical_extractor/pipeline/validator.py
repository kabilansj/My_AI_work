"""Validation and deduplication utilities for clinical entities."""

import re
from typing import List, Dict, Any, TypeVar
from ..models.entities import (
    Medication,
    Diagnosis,
    Investigation,
    Allergy,
    ClinicalBaseEntity,
)

T = TypeVar("T", bound=ClinicalBaseEntity)


class EntityValidator:
    """Validates evidence grounding and deduplicates extracted clinical entities."""

    @staticmethod
    def verify_evidence_span(source_text: str, evidence: str) -> bool:
        """Verify that the evidence span exists in the original source note."""
        if not source_text or not evidence:
            return False

        # Clean whitespace for comparison
        clean_source = re.sub(r"\s+", " ", source_text).lower()
        clean_evidence = re.sub(r"\s+", " ", evidence).lower()
        return clean_evidence in clean_source

    @staticmethod
    def deduplicate_medications(meds: List[Medication]) -> List[Medication]:
        """Merge identical medication mentions, keeping the most detailed entry."""
        merged: Dict[str, Medication] = {}
        for m in meds:
            key = m.name.strip().lower()
            if key not in merged:
                merged[key] = m
            else:
                existing = merged[key]
                # If current has dosage/frequency while existing doesn't, update
                if not existing.dosage and m.dosage:
                    existing.dosage = m.dosage
                if not existing.frequency and m.frequency:
                    existing.frequency = m.frequency
                if not existing.route and m.route:
                    existing.route = m.route
                if not existing.indication and m.indication:
                    existing.indication = m.indication
                if len(m.evidence_span or "") > len(existing.evidence_span or ""):
                    existing.evidence_span = m.evidence_span
        return list(merged.values())

    @staticmethod
    def deduplicate_diagnoses(dxs: List[Diagnosis]) -> List[Diagnosis]:
        """Deduplicate diagnoses by condition and assertion status, suppressing substring duplicates."""
        # First sort by length of condition_name descending so longer, more specific names come first
        sorted_dxs = sorted(dxs, key=lambda d: len(d.condition_name), reverse=True)
        filtered: List[Diagnosis] = []

        for d in sorted_dxs:
            d_norm = d.condition_name.strip().lower()
            # Check if this shorter condition is already subsumed by an existing condition with the same assertion
            is_subsumed = False
            for existing in filtered:
                ex_norm = existing.condition_name.strip().lower()
                if d.assertion == existing.assertion and d_norm in ex_norm:
                    is_subsumed = True
                    if not existing.acuity and d.acuity:
                        existing.acuity = d.acuity
                    if not existing.icd10_hint and d.icd10_hint:
                        existing.icd10_hint = d.icd10_hint
                    if len(d.evidence_span or "") > len(existing.evidence_span or ""):
                        existing.evidence_span = d.evidence_span
                    break
            if not is_subsumed:
                filtered.append(d)

        return filtered

    @staticmethod
    def deduplicate_investigations(invs: List[Investigation]) -> List[Investigation]:
        """Deduplicate investigations by test name, keeping the one with values and more specific name."""
        sorted_invs = sorted(invs, key=lambda i: len(i.test_name), reverse=True)
        filtered: List[Investigation] = []

        for inv in sorted_invs:
            inv_norm = inv.test_name.strip().lower()
            is_subsumed = False
            for existing in filtered:
                ex_norm = existing.test_name.strip().lower()
                if inv_norm in ex_norm or ex_norm in inv_norm:
                    is_subsumed = True
                    # If current has value but existing didn't, adopt value
                    if not existing.value and inv.value:
                        existing.value = inv.value
                        existing.unit = inv.unit
                        existing.flag = inv.flag
                    break
            if not is_subsumed:
                filtered.append(inv)

        return filtered

    @staticmethod
    def deduplicate_allergies(allergies: List[Allergy]) -> List[Allergy]:
        """Deduplicate allergy entries by allergen name."""
        merged: Dict[str, Allergy] = {}
        for a in allergies:
            key = a.allergen.strip().lower()
            if key not in merged:
                merged[key] = a
            else:
                existing = merged[key]
                if not existing.reaction and a.reaction:
                    existing.reaction = a.reaction
                if existing.severity.value == "unknown" and a.severity.value != "unknown":
                    existing.severity = a.severity
        return list(merged.values())
