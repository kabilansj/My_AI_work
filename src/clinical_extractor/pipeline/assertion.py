"""Clinical assertion, negation, and certainty analysis."""

import re
from typing import Tuple
from ..models.entities import AssertionStatus, AllergyStatus


# Preceding negation triggers
PRE_NEGATION_PATTERNS = [
    r"\b(?:no|not|denies|denied|denying|without|never|negative\s+for|rules\s+out|ruled\s+out|no\s+evidence\s+of|absence\s+of|free\s+of|unlikely)\b",
    r"\b(?:patient\s+denies|patient\s+reports\s+no|states\s+no|reports\s+no)\b",
]

# Following negation triggers
POST_NEGATION_PATTERNS = [
    r"\b(?:is\s+ruled\s+out|was\s+ruled\s+out|is\s+negative|was\s+negative|unremarkable|absent|not\s+seen)\b",
]

# Suspected / Uncertainty triggers
SUSPECTED_PATTERNS = [
    r"\b(?:suspect|suspected|possible|probable|likely|evaluate\s+for|eval\s+for|rule\s+out|r/o|differential|concern\s+for|borderline)\b",
]

# Historical / Resolved triggers
HISTORICAL_PATTERNS = [
    r"\b(?:history\s+of\s+resolved|resolved|in\s+childhood|childhood\s+history|prior\s+history\s+of|previous\s+history\s+of|past\s+hx\s+of)\b",
]

# Family history triggers
FAMILY_PATTERNS = [
    r"\b(?:family\s+history|fhx|father\s+had|mother\s+had|brother\s+with|sister\s+with|maternal|paternal)\b",
]

# NKDA (No Known Drug Allergies) triggers
NKDA_PATTERNS = [
    r"\b(?:NKDA|N\.K\.D\.A\.|NKA|no\s+known\s+drug\s+allergies|no\s+known\s+allergies|no\s+allergies|denies\s+allergies|allergic\s+history\s+negative)\b",
]


class AssertionAnalyzer:
    """Analyzes clinical context surrounding an entity to determine assertion status."""

    @classmethod
    def analyze_assertion(cls, full_text: str, entity_span: str, window_words: int = 6) -> AssertionStatus:
        """Examine the context window within sentence boundaries."""
        if not full_text or not entity_span:
            return AssertionStatus.CONFIRMED

        # Locate entity in text (case-insensitive)
        pattern = re.escape(entity_span)
        match = re.search(pattern, full_text, flags=re.IGNORECASE)
        if not match:
            return AssertionStatus.CONFIRMED

        start, end = match.span()

        # Isolate the sentence/clause containing the entity
        # Split on sentence boundaries (., ;, \n)
        before_text = full_text[:start]
        after_text = full_text[end:]

        # Find closest preceding sentence boundary
        pre_boundary = max(
            before_text.rfind("."),
            before_text.rfind(";"),
            before_text.rfind("\n"),
        )
        clause_before = before_text[pre_boundary + 1:] if pre_boundary != -1 else before_text

        # Find closest following sentence boundary
        post_boundaries = [pos for pos in [after_text.find("."), after_text.find(";"), after_text.find("\n")] if pos != -1]
        post_boundary = min(post_boundaries) if post_boundaries else len(after_text)
        clause_after = after_text[:post_boundary]

        pre_tokens = clause_before.split()[-window_words:]
        post_tokens = clause_after.split()[:window_words]

        pre_window = " ".join(pre_tokens).lower()
        post_window = " ".join(post_tokens).lower()

        # 1. Family history check
        for pat in FAMILY_PATTERNS:
            if re.search(pat, pre_window, re.IGNORECASE):
                return AssertionStatus.FAMILY_HISTORY

        # 2. Negation check (Pre & Post) - highest clinical priority in current sentence
        for pat in PRE_NEGATION_PATTERNS:
            if re.search(pat, pre_window, re.IGNORECASE):
                return AssertionStatus.RULED_OUT

        for pat in POST_NEGATION_PATTERNS:
            if re.search(pat, post_window, re.IGNORECASE):
                return AssertionStatus.RULED_OUT

        # 3. Suspected / Uncertainty check
        for pat in SUSPECTED_PATTERNS:
            if re.search(pat, pre_window, re.IGNORECASE):
                return AssertionStatus.SUSPECTED

        # 4. Historical / resolved check
        for pat in HISTORICAL_PATTERNS:
            if re.search(pat, pre_window, re.IGNORECASE) or re.search(pat, post_window, re.IGNORECASE):
                return AssertionStatus.HISTORICAL

        return AssertionStatus.CONFIRMED

    @classmethod
    def check_nkda(cls, text: str) -> Tuple[bool, str]:
        """Detect explicit No Known Drug Allergies (NKDA) statements."""
        for pat in NKDA_PATTERNS:
            match = re.search(pat, text, flags=re.IGNORECASE)
            if match:
                return True, match.group(0)
        return False, ""
