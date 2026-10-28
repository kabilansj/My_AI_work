"""Clinical document parser using PyMuPDF and pdfplumber."""

import json
from pathlib import Path
from typing import Dict, Any, Tuple
import fitz  # PyMuPDF
import pdfplumber


class DocumentParser:
    """Extracts text, layout metadata, and tables from clinical documents."""

    @classmethod
    def parse_file(cls, file_path: str, filename: str) -> Tuple[str, Dict[str, Any]]:
        """Extract clean text and layout structure from PDF or text file."""
        path = Path(file_path)
        lower_name = filename.lower()

        if lower_name.endswith(".pdf"):
            return cls._parse_pdf(str(path))
        else:
            # Standard text file
            text = path.read_text(encoding="utf-8", errors="replace")
            meta = {
                "file_type": "text",
                "page_count": 1,
                "character_count": len(text),
                "tables_found": 0,
            }
            return text, meta

    @classmethod
    def _parse_pdf(cls, pdf_path: str) -> Tuple[str, Dict[str, Any]]:
        """Extract text with PyMuPDF, supplemented with tables via pdfplumber."""
        page_texts = []
        page_boxes = []

        # 1. PyMuPDF extraction for text and coordinate blocks
        with fitz.open(pdf_path) as doc:
            page_count = len(doc)
            for page_num in range(page_count):
                page = doc[page_num]
                text = page.get_text("text")
                page_texts.append(text)

                # Extract word/line bounding boxes for evidence grounding
                blocks = page.get_text("blocks")
                page_boxes.append([
                    {
                        "page": page_num + 1,
                        "bbox": block[:4],
                        "text": block[4].strip(),
                    }
                    for block in blocks if block[4].strip()
                ])

        full_text = "\n\n--- Page Break ---\n\n".join(page_texts)

        # 2. pdfplumber for table extraction
        tables_data = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for idx, p in enumerate(pdf.pages):
                    extracted_tables = p.extract_tables()
                    for t in extracted_tables:
                        if t and len(t) > 1:
                            tables_data.append({"page": idx + 1, "rows": t})
        except Exception:
            pass

        metadata = {
            "file_type": "pdf",
            "page_count": len(page_texts),
            "character_count": len(full_text),
            "tables_found": len(tables_data),
            "blocks": page_boxes,
            "tables": tables_data,
        }

        return full_text, metadata
