"""Core facade for the Clinical NLP extraction engine."""

import os
from pathlib import Path
from typing import Optional, Union, Dict, Any, Callable

from .models.result import ClinicalExtractionResult
from .extractors.base import BaseExtractor
from .extractors.local_extractor import LocalClinicalExtractor
from .extractors.llm_extractor import LLMClinicalExtractor


class ClinicalNLP:
    """Unified entry point for clinical text entity extraction."""

    def __init__(
        self,
        engine: str = "auto",
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        api_type: str = "gemini",
        base_url: Optional[str] = None,
        client_fn: Optional[Callable[[str, str], str]] = None,
    ):
        """Initialize ClinicalNLP orchestrator.

        Args:
            engine: 'auto', 'local', 'llm', or 'hybrid'.
                    'auto' selects LLM if an API key is present, else falls back to 'local'.
            api_key: Optional API key for LLM.
            model_name: Model identifier (e.g. 'gemini-1.5-flash').
            api_type: 'gemini' or 'openai'.
            base_url: Optional custom endpoint URL.
            client_fn: Optional callable for mocking LLM in testing.
        """
        self.engine_mode = engine.lower()
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("OPENAI_API_KEY")
        self.model_name = model_name or ("gemini-1.5-flash" if api_type == "gemini" else "gpt-4o")
        self.api_type = api_type
        self.base_url = base_url
        self.client_fn = client_fn

        self.local_extractor = LocalClinicalExtractor()
        self.active_extractor = self._resolve_extractor()

    def _resolve_extractor(self) -> BaseExtractor:
        """Resolve the active extractor based on engine setting and environment."""
        if self.engine_mode == "local":
            return self.local_extractor

        if self.engine_mode == "llm":
            return LLMClinicalExtractor(
                api_key=self.api_key,
                model_name=self.model_name,
                api_type=self.api_type,
                base_url=self.base_url,
                client_fn=self.client_fn,
            )

        if self.engine_mode == "auto":
            # If client_fn is injected or an API key exists, use LLM; else local
            if self.client_fn or self.api_key:
                return LLMClinicalExtractor(
                    api_key=self.api_key,
                    model_name=self.model_name,
                    api_type=self.api_type,
                    base_url=self.base_url,
                    client_fn=self.client_fn,
                )
            return self.local_extractor

        raise ValueError(f"Unknown engine mode '{self.engine_mode}'. Choose 'auto', 'local', or 'llm'.")

    def extract(self, text: str) -> ClinicalExtractionResult:
        """Extract medications, diagnoses, investigations, and allergies from clinical text.

        Args:
            text: Unstructured clinical note, transcript, or summary.

        Returns:
            ClinicalExtractionResult containing extracted entities and metadata.
        """
        try:
            return self.active_extractor.extract(text)
        except Exception as e:
            # If LLM failed due to network / quota in auto mode, fallback to local engine
            if self.engine_mode == "auto" and not isinstance(self.active_extractor, LocalClinicalExtractor):
                res = self.local_extractor.extract(text)
                res.metadata.warnings.append(f"LLM extraction failed ({str(e)}). Fell back to local rule engine.")
                return res
            raise e

    def extract_file(self, file_path: Union[str, Path]) -> ClinicalExtractionResult:
        """Read a clinical note file (.txt, .json) and extract entities."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Clinical file not found at: {path}")

        content = path.read_text(encoding="utf-8")
        return self.extract(content)
