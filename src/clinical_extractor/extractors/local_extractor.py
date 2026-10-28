"""Deterministic local clinical entity extraction engine using medical lexicons and regex patterns."""

import re
import time
from typing import List, Dict, Tuple, Optional

from .base import BaseExtractor
from ..models.entities import (
    Medication,
    Diagnosis,
    Investigation,
    Allergy,
    MedicationStatus,
    AssertionStatus,
    InvestigationCategory,
    InvestigationFlag,
    AllergySeverity,
    AllergyType,
    AllergyStatus,
)
from ..models.result import ClinicalExtractionResult, ExtractionMetadata
from ..pipeline.preprocessor import ClinicalPreprocessor, ProcessedClinicalText
from ..pipeline.assertion import AssertionAnalyzer
from ..pipeline.validator import EntityValidator


# Extensive dictionary of common medications (generic and brand)
COMMON_MEDICATIONS = [
    # Cardiovascular
    "lisinopril", "amlodipine", "atorvastatin", "metoprolol", "losartan",
    "hydrochlorothiazide", "hctz", "simvastatin", "furosemide", "carvedilol",
    "clopidogrel", "apixaban", "warfarin", "rivaroxaban", "spironolactone",
    "valsartan", "diltiazem", "atenolol", "digoxin", "hydralazine",
    # Endocrine / Diabetes
    "metformin", "glipizide", "insulin glargine", "insulin lispro", "insulin",
    "empagliflozin", "dapagliflozin", "semaglutide", "sitagliptin", "levothyroxine",
    # Gastrointestinal
    "omeprazole", "pantoprazole", "famotidine", "esomeprazole", "ondansetron",
    # Respiratory
    "albuterol", "fluticasone", "montelukast", "budesonide", "ipratropium",
    # Antimicrobials
    "amoxicillin", "azithromycin", "ciprofloxacin", "ceftriaxone", "vancomycin",
    "doxycycline", "cephalexin", "trimethoprim-sulfamethoxazole", "bactrim",
    "augmentin", "piperacillin-tazobactam", "zosyn", "meropenem", "metronidazole",
    # Analgesics & Anti-inflammatory
    "aspirin", "acetaminophen", "ibuprofen", "naproxen", "gabapentin",
    "tramadol", "prednisone", "methylprednisolone", "morphine", "oxycodone",
    # Neuro / Psych
    "sertraline", "escitalopram", "duloxetine", "fluoxetine", "trazodone",
    "lorazepam", "alprazolam", "clonazepam", "quetiapine", "haloperidol",
]

# Common diagnoses, symptoms, and conditions
COMMON_DIAGNOSES = [
    # Chronic conditions
    ("type 2 diabetes mellitus", "chronic"),
    ("type 2 diabetes", "chronic"),
    ("t2dm", "chronic"),
    ("type 1 diabetes", "chronic"),
    ("diabetes mellitus", "chronic"),
    ("essential hypertension", "chronic"),
    ("hypertension", "chronic"),
    ("htn", "chronic"),
    ("hyperlipidemia", "chronic"),
    ("dyslipidemia", "chronic"),
    ("coronary artery disease", "chronic"),
    ("cad", "chronic"),
    ("congestive heart failure", "chronic"),
    ("heart failure", "chronic"),
    ("chf", "chronic"),
    ("atrial fibrillation", "chronic"),
    ("afib", "chronic"),
    ("chronic kidney disease", "chronic"),
    ("ckd", "chronic"),
    ("chronic obstructive pulmonary disease", "chronic"),
    ("copd", "chronic"),
    ("asthma", "chronic"),
    ("gastroesophageal reflux disease", "chronic"),
    ("gerd", "chronic"),
    ("hypothyroidism", "chronic"),
    ("depression", "chronic"),
    ("major depressive disorder", "chronic"),
    ("generalized anxiety disorder", "chronic"),
    ("anxiety", "chronic"),
    ("osteoarthritis", "chronic"),
    ("rheumatoid arthritis", "chronic"),
    # Acute conditions & complications
    ("acute myocardial infarction", "acute"),
    ("myocardial infarction", "acute"),
    ("stemi", "acute"),
    ("nstemi", "acute"),
    ("pulmonary embolism", "acute"),
    ("deep vein thrombosis", "acute"),
    ("dvt", "acute"),
    ("acute kidney injury", "acute"),
    ("aki", "acute"),
    ("community-acquired pneumonia", "acute"),
    ("pneumonia", "acute"),
    ("sepsis", "acute"),
    ("urinary tract infection", "acute"),
    ("uti", "acute"),
    ("cellulitis", "acute"),
    ("ischemic stroke", "acute"),
    ("cerebrovascular accident", "acute"),
    ("cva", "acute"),
    ("transient ischemic attack", "acute"),
    ("tia", "acute"),
    ("diabetic ketoacidosis", "acute"),
    ("dka", "acute"),
    ("covid-19", "acute"),
    # Cardinal symptoms
    ("chest pain", "acute"),
    ("shortness of breath", "acute"),
    ("sob", "acute"),
    ("dyspnea", "acute"),
    ("cough", "acute"),
    ("fever", "acute"),
    ("chills", "acute"),
    ("headache", "acute"),
    ("nausea", "acute"),
    ("vomiting", "acute"),
    ("abdominal pain", "acute"),
    ("dizziness", "acute"),
    ("syncope", "acute"),
    ("palpitations", "acute"),
    ("edema", "chronic"),
]

# Lab tests and diagnostic parameters
COMMON_INVESTIGATIONS = [
    # Labs
    ("hemoglobin a1c", InvestigationCategory.LABORATORY, "%"),
    ("hba1c", InvestigationCategory.LABORATORY, "%"),
    ("hemoglobin", InvestigationCategory.LABORATORY, "g/dL"),
    ("hgb", InvestigationCategory.LABORATORY, "g/dL"),
    ("hematocrit", InvestigationCategory.LABORATORY, "%"),
    ("hct", InvestigationCategory.LABORATORY, "%"),
    ("wbc", InvestigationCategory.LABORATORY, "k/uL"),
    ("white blood cell count", InvestigationCategory.LABORATORY, "k/uL"),
    ("platelets", InvestigationCategory.LABORATORY, "k/uL"),
    ("creatinine", InvestigationCategory.LABORATORY, "mg/dL"),
    ("serum creatinine", InvestigationCategory.LABORATORY, "mg/dL"),
    ("bun", InvestigationCategory.LABORATORY, "mg/dL"),
    ("blood urea nitrogen", InvestigationCategory.LABORATORY, "mg/dL"),
    ("potassium", InvestigationCategory.LABORATORY, "mEq/L"),
    ("sodium", InvestigationCategory.LABORATORY, "mEq/L"),
    ("chloride", InvestigationCategory.LABORATORY, "mEq/L"),
    ("bicarbonate", InvestigationCategory.LABORATORY, "mEq/L"),
    ("glucose", InvestigationCategory.LABORATORY, "mg/dL"),
    ("blood glucose", InvestigationCategory.LABORATORY, "mg/dL"),
    ("fasting blood glucose", InvestigationCategory.LABORATORY, "mg/dL"),
    ("troponin i", InvestigationCategory.LABORATORY, "ng/mL"),
    ("troponin t", InvestigationCategory.LABORATORY, "ng/mL"),
    ("troponin", InvestigationCategory.LABORATORY, "ng/mL"),
    ("bnp", InvestigationCategory.LABORATORY, "pg/mL"),
    ("tsh", InvestigationCategory.LABORATORY, "uIU/mL"),
    ("alt", InvestigationCategory.LABORATORY, "U/L"),
    ("ast", InvestigationCategory.LABORATORY, "U/L"),
    ("total cholesterol", InvestigationCategory.LABORATORY, "mg/dL"),
    ("ldl", InvestigationCategory.LABORATORY, "mg/dL"),
    ("hdl", InvestigationCategory.LABORATORY, "mg/dL"),
    ("triglycerides", InvestigationCategory.LABORATORY, "mg/dL"),
    ("inr", InvestigationCategory.LABORATORY, ""),
    # Imaging
    ("chest x-ray", InvestigationCategory.IMAGING, ""),
    ("cxr", InvestigationCategory.IMAGING, ""),
    ("chest radiograph", InvestigationCategory.IMAGING, ""),
    ("ct chest", InvestigationCategory.IMAGING, ""),
    ("ct abdomen", InvestigationCategory.IMAGING, ""),
    ("ct head", InvestigationCategory.IMAGING, ""),
    ("mri brain", InvestigationCategory.IMAGING, ""),
    ("echocardiogram", InvestigationCategory.IMAGING, ""),
    ("echo", InvestigationCategory.IMAGING, ""),
    ("ultrasound", InvestigationCategory.IMAGING, ""),
    # Procedures / Tracings
    ("electrocardiogram", InvestigationCategory.PROCEDURE, ""),
    ("ecg", InvestigationCategory.PROCEDURE, ""),
    ("ekg", InvestigationCategory.PROCEDURE, ""),
    # Vitals
    ("blood pressure", InvestigationCategory.VITAL_SIGN, "mmHg"),
    ("bp", InvestigationCategory.VITAL_SIGN, "mmHg"),
    ("heart rate", InvestigationCategory.VITAL_SIGN, "bpm"),
    ("hr", InvestigationCategory.VITAL_SIGN, "bpm"),
    ("pulse", InvestigationCategory.VITAL_SIGN, "bpm"),
    ("respiratory rate", InvestigationCategory.VITAL_SIGN, "breaths/min"),
    ("rr", InvestigationCategory.VITAL_SIGN, "breaths/min"),
    ("spo2", InvestigationCategory.VITAL_SIGN, "%"),
    ("oxygen saturation", InvestigationCategory.VITAL_SIGN, "%"),
    ("temperature", InvestigationCategory.VITAL_SIGN, "F"),
]

# Known allergens
KNOWN_ALLERGENS = [
    "penicillin", "amoxicillin", "sulfa", "sulfonamides", "codeine",
    "morphine", "aspirin", "nsaids", "latex", "iodine", "contrast dye",
    "peanuts", "shellfish", "eggs", "dairy", "tree nuts", "ciprofloxacin",
]


class LocalClinicalExtractor(BaseExtractor):
    """Rule-based clinical extraction engine operating fully offline with zero dependencies."""

    def __init__(self):
        # Precompile medication dosage & SIG patterns
        self.dosage_pattern = re.compile(
            r"\b(\d+(?:\.\d+)?\s*(?:mg|mcg|g|ml|mEq|units?|puffs?|tablets?|caps?))\b",
            re.IGNORECASE,
        )
        self.freq_pattern = re.compile(
            r"\b(daily|once daily|twice daily|BID|b\.i\.d\.|three times daily|TID|t\.i\.d\.|QID|q\.i\.d\.|q\d+h|prn|as needed|at bedtime|qhs|qam|every \d+ hours)\b",
            re.IGNORECASE,
        )
        self.route_pattern = re.compile(
            r"\b(oral|PO|p\.o\.|IV|i\.v\.|IM|subcutaneous|subQ|topical|inhalation|sublingual)\b",
            re.IGNORECASE,
        )

    def extract(self, text: str) -> ClinicalExtractionResult:
        """Execute deterministic rule extraction across the text."""
        start_time = time.perf_counter()
        doc = ClinicalPreprocessor.process(text)

        medications = self._extract_medications(doc)
        diagnoses = self._extract_diagnoses(doc)
        investigations = self._extract_investigations(doc)
        allergies = self._extract_allergies(doc)

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        metadata = ExtractionMetadata(
            engine="local_rule_engine",
            model_name="regex_lexicon_v1",
            char_count=doc.char_count,
            word_count=doc.word_count,
            processing_time_ms=round(elapsed_ms, 2),
        )

        return ClinicalExtractionResult(
            medications=EntityValidator.deduplicate_medications(medications),
            diagnoses=EntityValidator.deduplicate_diagnoses(diagnoses),
            investigations=EntityValidator.deduplicate_investigations(investigations),
            allergies=EntityValidator.deduplicate_allergies(allergies),
            metadata=metadata,
        )

    def _extract_medications(self, doc: ProcessedClinicalText) -> List[Medication]:
        """Extract medications and parse dosage, frequency, and route."""
        results: List[Medication] = []
        text = doc.cleaned_text

        for drug in COMMON_MEDICATIONS:
            # Word boundary regex for drug name
            pattern = rf"\b({re.escape(drug)})\b"
            for match in re.finditer(pattern, text, re.IGNORECASE):
                # Isolate clause: look primarily forward from the drug name to the next delimiter (newline, comma, semicolon, " and ")
                before_text = text[:match.start()]
                after_text = text[match.end():]

                pre_delims = [before_text.rfind(d) for d in ["\n", ";"] if before_text.rfind(d) != -1]
                line_start = (max(pre_delims) + 1) if pre_delims else max(0, match.start() - 20)

                post_delims = [after_text.find(d) for d in ["\n", ";"] if after_text.find(d) != -1]
                line_end = (match.end() + min(post_delims)) if post_delims else min(len(text), match.end() + 100)

                # Clause following drug (stops at next item separator or newline)
                forward_delims = [after_text.find(d) for d in [",", "\n", ";", " and ", " or "] if after_text.find(d) != -1]
                clause_end = (match.end() + min(forward_delims)) if forward_delims else line_end
                target_window = text[match.start():clause_end]

                # Don't pick up medications inside the ALLERGIES section
                allergies_sec = doc.get_section_text("allergies")
                if allergies_sec and match.group(1).lower() in allergies_sec.lower():
                    for sec in doc.sections:
                        if sec.normalized_name == "allergies" and sec.start_char <= match.start() <= sec.end_char:
                            continue

                # Parse dosage (search forward clause first, fallback to line window)
                dosage_match = self.dosage_pattern.search(target_window) or self.dosage_pattern.search(text[line_start:line_end])
                dosage = dosage_match.group(1) if dosage_match else None

                # Parse frequency
                freq_match = self.freq_pattern.search(target_window) or self.freq_pattern.search(text[line_start:line_end])
                freq = freq_match.group(1) if freq_match else None

                # Parse route
                route_match = self.route_pattern.search(target_window) or self.route_pattern.search(text[line_start:line_end])
                route = route_match.group(1).upper() if route_match else None

                # Status
                status = MedicationStatus.ACTIVE
                # Check for discontinuation keywords within the same clause or line
                if re.search(r"\b(discontinue|discontinued|d/c|stopped|held|stop)\b", text[line_start:line_end], re.IGNORECASE):
                    status = MedicationStatus.DISCONTINUED
                elif freq and "prn" in freq.lower():
                    status = MedicationStatus.PRN

                # Evidence span
                evidence = target_window.strip()

                results.append(
                    Medication(
                        name=match.group(1).title(),
                        dosage=dosage,
                        frequency=freq,
                        route=route,
                        status=status,
                        evidence_span=evidence or match.group(1),
                        confidence=0.95,
                    )
                )

        return results

    def _extract_diagnoses(self, doc: ProcessedClinicalText) -> List[Diagnosis]:
        """Extract conditions and analyze assertion/negation status."""
        results: List[Diagnosis] = []
        text = doc.cleaned_text

        for condition, default_acuity in COMMON_DIAGNOSES:
            pattern = rf"\b({re.escape(condition)})\b"
            for match in re.finditer(pattern, text, re.IGNORECASE):
                matched_text = match.group(1)
                # Analyze assertion status
                assertion = AssertionAnalyzer.analyze_assertion(text, matched_text)

                # Contextual evidence span (surrounding 40 characters)
                span_start = max(0, match.start() - 25)
                span_end = min(len(text), match.end() + 25)
                evidence = text[span_start:span_end].strip()

                results.append(
                    Diagnosis(
                        condition_name=matched_text.title(),
                        assertion=assertion,
                        acuity=default_acuity,
                        evidence_span=evidence,
                        confidence=0.92,
                    )
                )

        return results

    def _extract_investigations(self, doc: ProcessedClinicalText) -> List[Investigation]:
        """Extract diagnostic tests, lab values, and vitals."""
        results: List[Investigation] = []
        text = doc.cleaned_text

        for test_name, category, default_unit in COMMON_INVESTIGATIONS:
            # Match test name followed optionally by 'was', 'is', ':', or spaces, then value
            pattern = rf"\b({re.escape(test_name)})\b(?:\s*[:=]|was|is)?\s*([<>]?\s*\d+(?:\.\d+)?(?:/\d+)?|\b(?:normal|unremarkable|clear|elevated|high|low|negative|positive)\b)?"
            for match in re.finditer(pattern, text, re.IGNORECASE):
                test_term = match.group(1)
                raw_val = match.group(2) if match.group(2) else None

                # Determine unit and flag
                flag = InvestigationFlag.UNKNOWN
                val_str = None
                unit_str = default_unit or None

                if raw_val:
                    lower_val = raw_val.lower().strip()
                    if lower_val in ("elevated", "high"):
                        flag = InvestigationFlag.HIGH
                        val_str = lower_val
                    elif lower_val in ("low",):
                        flag = InvestigationFlag.LOW
                        val_str = lower_val
                    elif lower_val in ("normal", "unremarkable", "clear", "negative"):
                        flag = InvestigationFlag.NORMAL
                        val_str = lower_val
                    elif lower_val in ("positive", "abnormal"):
                        flag = InvestigationFlag.ABNORMAL
                        val_str = lower_val
                    else:
                        val_str = raw_val.strip()

                # Extract surrounding evidence span
                span_start = match.start()
                span_end = min(len(text), match.end() + 20)
                evidence = text[span_start:span_end].strip()

                # Look for abnormality cues in evidence window
                if flag == InvestigationFlag.UNKNOWN:
                    if re.search(r"\b(high|elevated|critical)\b", evidence, re.IGNORECASE):
                        flag = InvestigationFlag.HIGH
                    elif re.search(r"\b(low|decreased)\b", evidence, re.IGNORECASE):
                        flag = InvestigationFlag.LOW
                    elif re.search(r"\b(normal|within\s+normal\s+limits|wnl)\b", evidence, re.IGNORECASE):
                        flag = InvestigationFlag.NORMAL

                results.append(
                    Investigation(
                        test_name=test_term.upper() if len(test_term) <= 4 else test_term.title(),
                        category=category,
                        value=val_str,
                        unit=unit_str,
                        flag=flag,
                        evidence_span=evidence,
                        confidence=0.90,
                    )
                )

        return results

    def _extract_allergies(self, doc: ProcessedClinicalText) -> List[Allergy]:
        """Extract documented allergies and check for NKDA."""
        results: List[Allergy] = []
        text = doc.cleaned_text

        # 1. Check for NKDA
        is_nkda, nkda_span = AssertionAnalyzer.check_nkda(text)
        if is_nkda:
            results.append(
                Allergy(
                    allergen="No Known Drug Allergies",
                    status=AllergyStatus.NKDA_REPORTED,
                    evidence_span=nkda_span,
                    confidence=1.0,
                )
            )

        # 2. Check for allergen mentions
        for allergen in KNOWN_ALLERGENS:
            pat = rf"\b({re.escape(allergen)})\b"
            for match in re.finditer(pat, text, re.IGNORECASE):
                before_text = text[:match.start()]
                after_text = text[match.end():]

                # Clause boundary isolation (commas, semicolons, periods, newlines)
                pre_delims = [before_text.rfind(d) for d in [",", ";", ".", "\n"] if before_text.rfind(d) != -1]
                clause_start = (max(pre_delims) + 1) if pre_delims else max(0, match.start() - 30)

                post_delims = [after_text.find(d) for d in [",", ";", ".", "\n"] if after_text.find(d) != -1]
                clause_end = (match.end() + min(post_delims)) if post_delims else min(len(text), match.end() + 50)

                window = text[clause_start:clause_end].strip()

                # Check if this occurrence is under allergies context
                is_allergy_context = False
                allergies_sec = doc.get_section_text("allergies")
                if allergies_sec and match.group(1).lower() in allergies_sec.lower():
                    is_allergy_context = True
                elif re.search(r"\b(?:allerg|adverse|reaction|hives|rash|anaphylaxis|swelling)\b", window, re.IGNORECASE):
                    is_allergy_context = True

                if not is_allergy_context:
                    continue

                # Detect reaction within this allergen's specific clause
                reaction = None
                severity = AllergySeverity.UNKNOWN
                if re.search(r"\b(anaphylaxis|throat\s+closing|angioedema)\b", window, re.IGNORECASE):
                    reaction = "anaphylaxis"
                    severity = AllergySeverity.SEVERE
                elif re.search(r"\b(hives|urticaria)\b", window, re.IGNORECASE):
                    reaction = "hives"
                    severity = AllergySeverity.MODERATE
                elif re.search(r"\b(rash)\b", window, re.IGNORECASE):
                    reaction = "rash"
                    severity = AllergySeverity.MODERATE
                elif re.search(r"\b(nausea|vomiting|gi\s+upset)\b", window, re.IGNORECASE):
                    reaction = "nausea/GI upset"
                    severity = AllergySeverity.MILD

                results.append(
                    Allergy(
                        allergen=match.group(1).title(),
                        reaction=reaction,
                        severity=severity,
                        allergy_type=AllergyType.DRUG,
                        status=AllergyStatus.ACTIVE,
                        evidence_span=window,
                        confidence=0.92,
                    )
                )

        return results
