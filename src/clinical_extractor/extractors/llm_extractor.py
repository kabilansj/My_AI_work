"""LLM-powered clinical extraction engine using structured JSON outputs."""

import json
import os
import re
import time
from typing import Optional, Dict, Any, Callable

import requests

from .base import BaseExtractor
from .prompts import CLINICAL_SYSTEM_PROMPT, CLINICAL_USER_PROMPT_TEMPLATE
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
from ..pipeline.preprocessor import ClinicalPreprocessor
from ..pipeline.validator import EntityValidator


class LLMClinicalExtractor(BaseExtractor):
    """Clinical extractor powered by Large Language Models (Gemini / OpenAI compatible API)."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gemini-1.5-flash",
        api_type: str = "gemini",  # "gemini" or "openai"
        base_url: Optional[str] = None,
        client_fn: Optional[Callable[[str, str], str]] = None,
    ):
        """Initialize the LLM extractor.

        Args:
            api_key: API key. If None, checks GEMINI_API_KEY or OPENAI_API_KEY env vars.
            model_name: Model identifier (e.g. 'gemini-1.5-flash', 'gemini-2.0-flash', 'gpt-4o').
            api_type: 'gemini' or 'openai'.
            base_url: Custom API endpoint URL if needed.
            client_fn: Custom callable for testing/mocking `(system_prompt, user_prompt) -> json_str`.
        """
        self.api_type = api_type.lower()
        self.model_name = model_name
        self.client_fn = client_fn

        if self.api_type == "gemini":
            self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        else:
            self.api_key = api_key or os.environ.get("OPENAI_API_KEY")

        self.base_url = base_url

    def extract(self, text: str) -> ClinicalExtractionResult:
        """Execute LLM extraction and parse into validated domain models."""
        start_time = time.perf_counter()
        doc = ClinicalPreprocessor.process(text)

        if not text.strip():
            return ClinicalExtractionResult(
                metadata=ExtractionMetadata(
                    engine="llm",
                    model_name=self.model_name,
                    char_count=0,
                    word_count=0,
                    processing_time_ms=0.0,
                )
            )

        # Generate response text via client_fn or HTTP API
        raw_response = self._invoke_llm(
            system_prompt=CLINICAL_SYSTEM_PROMPT,
            user_prompt=CLINICAL_USER_PROMPT_TEMPLATE.format(clinical_text=doc.cleaned_text),
        )

        parsed_json = self._parse_json_from_response(raw_response)
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        # Construct entities with Pydantic validation
        medications = self._parse_medications(parsed_json.get("medications", []))
        diagnoses = self._parse_diagnoses(parsed_json.get("diagnoses", []))
        investigations = self._parse_investigations(parsed_json.get("investigations", []))
        allergies = self._parse_allergies(parsed_json.get("allergies", []))

        # Check grounding against original text
        warnings = []
        for category_name, entity_list in [
            ("medication", medications),
            ("diagnosis", diagnoses),
            ("investigation", investigations),
            ("allergy", allergies),
        ]:
            for ent in entity_list:
                if ent.evidence_span:
                    if not EntityValidator.verify_evidence_span(doc.cleaned_text, ent.evidence_span):
                        ent.confidence = 0.5
                        warnings.append(f"Ungrounded span for {category_name}: '{ent.evidence_span}'")

        metadata = ExtractionMetadata(
            engine="llm",
            model_name=self.model_name,
            char_count=doc.char_count,
            word_count=doc.word_count,
            processing_time_ms=round(elapsed_ms, 2),
            warnings=warnings,
        )

        return ClinicalExtractionResult(
            medications=EntityValidator.deduplicate_medications(medications),
            diagnoses=EntityValidator.deduplicate_diagnoses(diagnoses),
            investigations=EntityValidator.deduplicate_investigations(investigations),
            allergies=EntityValidator.deduplicate_allergies(allergies),
            metadata=metadata,
        )

    def _invoke_llm(self, system_prompt: str, user_prompt: str) -> str:
        """Call LLM API or test client function."""
        if self.client_fn:
            return self.client_fn(system_prompt, user_prompt)

        if not self.api_key:
            raise ValueError(
                f"Missing API key for {self.api_type}. Set GEMINI_API_KEY / OPENAI_API_KEY environment variable "
                f"or initialize ClinicalNLP(engine='local') to use the offline engine."
            )

        if self.api_type == "gemini":
            return self._call_gemini_api(system_prompt, user_prompt)
        elif self.api_type == "openai":
            return self._call_openai_api(system_prompt, user_prompt)
        else:
            raise ValueError(f"Unsupported api_type: {self.api_type}")

    def _call_gemini_api(self, system_prompt: str, user_prompt: str) -> str:
        """Invoke Google Gemini REST API using generateContent with JSON response schema."""
        endpoint = (
            self.base_url
            or f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        )

        payload = {
            "system_instruction": {
                "parts": [{"text": system_prompt}]
            },
            "contents": [
                {
                    "parts": [{"text": user_prompt}]
                }
            ],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.1,
            },
        }

        resp = requests.post(endpoint, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        candidates = data.get("candidates", [])
        if not candidates:
            raise RuntimeError("Gemini API returned no response candidates.")
        return candidates[0]["content"]["parts"][0]["text"]

    def _call_openai_api(self, system_prompt: str, user_prompt: str) -> str:
        """Invoke OpenAI-compatible chat completions endpoint with json_object response format."""
        endpoint = self.base_url or "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.1,
        }

        resp = requests.post(endpoint, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    def _parse_json_from_response(self, text: str) -> Dict[str, Any]:
        """Safely parse JSON response from LLM, handling optional markdown formatting."""
        text = text.strip()
        # Strip ```json ... ``` wrapper if present
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if json_match:
            text = json_match.group(1).strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Failed to parse LLM response into valid JSON: {exc}\nResponse was:\n{text}")

    def _parse_medications(self, items: list) -> list:
        results = []
        for item in items:
            try:
                # Normalize status enum
                status_val = str(item.get("status", "active")).lower()
                try:
                    status = MedicationStatus(status_val)
                except ValueError:
                    status = MedicationStatus.ACTIVE

                results.append(
                    Medication(
                        name=item.get("name", "Unknown"),
                        dosage=item.get("dosage"),
                        frequency=item.get("frequency"),
                        route=item.get("route"),
                        status=status,
                        indication=item.get("indication"),
                        evidence_span=item.get("evidence_span"),
                    )
                )
            except Exception:
                continue
        return results

    def _parse_diagnoses(self, items: list) -> list:
        results = []
        for item in items:
            try:
                # Normalize assertion enum
                assert_val = str(item.get("assertion", "confirmed")).lower()
                try:
                    assertion = AssertionStatus(assert_val)
                except ValueError:
                    assertion = AssertionStatus.CONFIRMED

                results.append(
                    Diagnosis(
                        condition_name=item.get("condition_name", "Unknown"),
                        assertion=assertion,
                        acuity=item.get("acuity"),
                        icd10_hint=item.get("icd10_hint"),
                        evidence_span=item.get("evidence_span"),
                    )
                )
            except Exception:
                continue
        return results

    def _parse_investigations(self, items: list) -> list:
        results = []
        for item in items:
            try:
                cat_val = str(item.get("category", "laboratory")).lower()
                try:
                    category = InvestigationCategory(cat_val)
                except ValueError:
                    category = InvestigationCategory.LABORATORY

                flag_val = str(item.get("flag", "unknown")).lower()
                try:
                    flag = InvestigationFlag(flag_val)
                except ValueError:
                    flag = InvestigationFlag.UNKNOWN

                results.append(
                    Investigation(
                        test_name=item.get("test_name", "Unknown"),
                        category=category,
                        value=str(item.get("value")) if item.get("value") is not None else None,
                        unit=item.get("unit"),
                        reference_range=item.get("reference_range"),
                        flag=flag,
                        evidence_span=item.get("evidence_span"),
                    )
                )
            except Exception:
                continue
        return results

    def _parse_allergies(self, items: list) -> list:
        results = []
        for item in items:
            try:
                sev_val = str(item.get("severity", "unknown")).lower()
                try:
                    severity = AllergySeverity(sev_val)
                except ValueError:
                    severity = AllergySeverity.UNKNOWN

                type_val = str(item.get("allergy_type", "drug")).lower()
                try:
                    allergy_type = AllergyType(type_val)
                except ValueError:
                    allergy_type = AllergyType.DRUG

                stat_val = str(item.get("status", "active")).lower()
                try:
                    status = AllergyStatus(stat_val)
                except ValueError:
                    status = AllergyStatus.ACTIVE

                results.append(
                    Allergy(
                        allergen=item.get("allergen", "Unknown"),
                        reaction=item.get("reaction"),
                        severity=severity,
                        allergy_type=allergy_type,
                        status=status,
                        evidence_span=item.get("evidence_span"),
                    )
                )
            except Exception:
                continue
        return results
