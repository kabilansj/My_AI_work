"""Clinical text preprocessor and clinical section segmenter."""

import re
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ClinicalSection(BaseModel):
    """Identified section in a clinical note."""
    header: str
    normalized_name: str
    text: str
    start_char: int
    end_char: int


class ProcessedClinicalText(BaseModel):
    """Processed clinical document with normalized sections."""
    raw_text: str
    cleaned_text: str
    sections: List[ClinicalSection] = Field(default_factory=list)
    char_count: int = 0
    word_count: int = 0

    def get_section_text(self, section_name: str) -> Optional[str]:
        """Retrieve text from a specific normalized section name if present."""
        for sec in self.sections:
            if sec.normalized_name.lower() == section_name.lower():
                return sec.text
        return None


# Standard clinical section header regex patterns
SECTION_PATTERNS = [
    (r"(?i)\b(CHIEF\s+COMPLAINT|REASON\s+FOR\s+VISIT)\s*:", "chief_complaint"),
    (r"(?i)\b(HISTORY\s+OF\s+PRESENT\s+ILLNESS|HPI)\s*:", "history_of_present_illness"),
    (r"(?i)\b(PAST\s+MEDICAL\s+HISTORY|PMH|MEDICAL\s+HISTORY)\s*:", "past_medical_history"),
    (r"(?i)\b(PAST\s+SURGICAL\s+HISTORY|PSH)\s*:", "past_surgical_history"),
    (r"(?i)\b(MEDICATIONS|CURRENT\s+MEDICATIONS|MEDS|HOME\s+MEDICATIONS)\s*:", "medications"),
    (r"(?i)\b(ALLERGIES|ALLERGIC\s+HISTORY|ADVERSE\s+REACTIONS)\s*:", "allergies"),
    (r"(?i)\b(FAMILY\s+HISTORY|FH)\s*:", "family_history"),
    (r"(?i)\b(SOCIAL\s+HISTORY|SH)\s*:", "social_history"),
    (r"(?i)\b(REVIEW\s+OF\s+SYSTEMS|ROS)\s*:", "review_of_systems"),
    (r"(?i)\b(PHYSICAL\s+EXAMINATION|PHYSICAL\s+EXAM|PE|OBJECTIVE)\s*:", "physical_exam"),
    (r"(?i)\b(LABORATORY\s+DATA|LABS|LABORATORIES|DIAGNOSTIC\s+STUDIES|INVESTIGATIONS)\s*:", "investigations"),
    (r"(?i)\b(ASSESSMENT\s+AND\s+PLAN|ASSESSMENT|PLAN|IMPRESSION|A/P|IMPRESSION\s+AND\s+PLAN)\s*:", "assessment_and_plan"),
]


class ClinicalPreprocessor:
    """Cleans, normalizes, and segments clinical text into standard medical sections."""

    @staticmethod
    def clean(text: str) -> str:
        """Normalize line breaks and trailing whitespaces while preserving structural cues."""
        if not text:
            return ""
        # Replace carriage returns and excessive empty lines
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    @classmethod
    def process(cls, text: str) -> ProcessedClinicalText:
        """Parse raw clinical text into sections."""
        cleaned = cls.clean(text)
        words = len(cleaned.split()) if cleaned else 0
        chars = len(cleaned)

        if not cleaned:
            return ProcessedClinicalText(
                raw_text=text or "",
                cleaned_text="",
                sections=[],
                char_count=0,
                word_count=0
            )

        # Find all section header matches
        header_matches = []
        for regex, norm_name in SECTION_PATTERNS:
            for match in re.finditer(regex, cleaned):
                header_matches.append({
                    "start": match.start(),
                    "end": match.end(),
                    "raw_header": match.group(1),
                    "normalized": norm_name,
                })

        # Sort matches by start position
        header_matches.sort(key=lambda x: x["start"])

        sections: List[ClinicalSection] = []
        for i, h in enumerate(header_matches):
            header_end = h["end"]
            # Section text runs up to next header start, or end of document
            next_start = header_matches[i + 1]["start"] if i + 1 < len(header_matches) else len(cleaned)
            sec_text = cleaned[header_end:next_start].strip()

            sections.append(
                ClinicalSection(
                    header=h["raw_header"],
                    normalized_name=h["normalized"],
                    text=sec_text,
                    start_char=h["start"],
                    end_char=next_start,
                )
            )

        return ProcessedClinicalText(
            raw_text=text,
            cleaned_text=cleaned,
            sections=sections,
            char_count=chars,
            word_count=words
        )
