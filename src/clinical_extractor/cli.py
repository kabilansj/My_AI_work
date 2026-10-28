"""Command-line interface for the clinical text extraction application."""

import sys
import argparse
import json
from pathlib import Path
from typing import Optional

from .core import ClinicalNLP
from .models.result import ClinicalExtractionResult

SAMPLE_CLINICAL_NOTE = """CHIEF COMPLAINT:
Follow-up for type 2 diabetes mellitus and hypertension.

HISTORY OF PRESENT ILLNESS:
Patient is a 58-year-old male presenting for routine clinical review.
He reports good compliance with home medications. Patient denies chest pain, denies shortness of breath, and denies palpitations.
No fever, cough, or nausea.

PAST MEDICAL HISTORY:
1. Type 2 Diabetes Mellitus - diagnosed 6 years ago.
2. Essential Hypertension.
3. History of resolved childhood asthma.
4. Family history of coronary artery disease (father had MI at age 52).

CURRENT MEDICATIONS:
1. Metformin 1000 mg BID PO
2. Lisinopril 20 mg daily PO
3. Atorvastatin 40 mg PO at bedtime
4. Albuterol inhaler 2 puffs PRN (has not used in past year)

ALLERGIES:
Penicillin (hives and facial swelling). Sulfa drugs (anaphylaxis).

INVESTIGATIONS:
- Blood pressure: 128/82 mmHg
- Heart rate: 72 bpm
- HbA1c: 7.2% (down from 8.5% 6 months ago)
- Serum Creatinine: 1.0 mg/dL (normal)
- Potassium: 4.3 mEq/L
- CXR: Clear lung fields, normal cardiothoracic ratio

ASSESSMENT & PLAN:
1. Type 2 Diabetes Mellitus - improved glycemic control on Metformin.
2. Hypertension - well-controlled on Lisinopril.
3. Continue current medication regimen. Recheck labs in 6 months.
"""


def format_terminal_summary(result: ClinicalExtractionResult) -> str:
    """Generate a clean, colorized terminal summary."""
    lines = [
        "=" * 60,
        " CLINICAL ENTITY EXTRACTION RESULTS",
        f" Engine: {result.metadata.engine} ({result.metadata.model_name or 'N/A'})",
        f" Processed: {result.metadata.word_count} words in {result.metadata.processing_time_ms:.1f}ms",
        "=" * 60,
        "",
        "💊 MEDICATIONS EXTRACTED:",
    ]
    if not result.medications:
        lines.append("  (None identified)")
    else:
        for m in result.medications:
            sig_parts = [m.dosage, m.frequency, m.route]
            sig = " ".join([p for p in sig_parts if p])
            lines.append(f"  • {m.name}" + (f" [{sig}]" if sig else "") + f" - Status: {m.status.value}")

    lines.extend(["", "🩺 DIAGNOSES & CONDITIONS:"])
    if not result.diagnoses:
        lines.append("  (None identified)")
    else:
        for d in result.diagnoses:
            assertion_tag = f"[{d.assertion.value.upper()}]"
            lines.append(f"  • {assertion_tag:<14} {d.condition_name}" + (f" ({d.acuity})" if d.acuity else ""))

    lines.extend(["", "🔬 INVESTIGATIONS (LABS & IMAGING):"])
    if not result.investigations:
        lines.append("  (None identified)")
    else:
        for inv in result.investigations:
            val_str = f"{inv.value or ''} {inv.unit or ''}".strip()
            flag_str = f"[{inv.flag.value.upper()}]" if inv.flag.value != "unknown" else ""
            lines.append(f"  • {inv.test_name:<20} {val_str:<18} {flag_str}")

    lines.extend(["", "⚠️ ALLERGIES & ADVERSE REACTIONS:"])
    if not result.allergies:
        lines.append("  (None identified)")
    else:
        for a in result.allergies:
            react = f" - Reaction: {a.reaction}" if a.reaction else ""
            sev = f" ({a.severity.value})" if a.severity.value != "unknown" else ""
            lines.append(f"  • {a.allergen}{react}{sev} [{a.status.value}]")

    lines.append("")
    lines.append("=" * 60)
    return "\n".join(lines)


def parse_args(args=None):
    parser = argparse.ArgumentParser(
        prog="clinical-extract",
        description="Extract medications, diagnoses, investigations, and allergies from clinical text.",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-f", "--file", type=str, help="Path to clinical note text file.")
    group.add_argument("-t", "--text", type=str, help="Raw clinical note string to process.")
    group.add_argument("--sample", action="store_true", help="Run extraction on a realistic built-in clinical note.")

    parser.add_argument(
        "-e", "--engine",
        choices=["auto", "local", "llm"],
        default="auto",
        help="Extraction engine (default: auto).",
    )
    parser.add_argument(
        "--format",
        choices=["summary", "json", "markdown"],
        default="summary",
        help="Output format (default: summary).",
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Optional destination file path to write results.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gemini-1.5-flash",
        help="Model identifier when using LLM engine (default: gemini-1.5-flash).",
    )

    return parser.parse_args(args)


def main(args=None):
    parsed = parse_args(args)

    # Determine input text
    clinical_text: Optional[str] = None

    if parsed.sample:
        clinical_text = SAMPLE_CLINICAL_NOTE
    elif parsed.file:
        file_path = Path(parsed.file)
        if not file_path.exists():
            sys.stderr.write(f"Error: File not found: {parsed.file}\n")
            sys.exit(1)
        clinical_text = file_path.read_text(encoding="utf-8")
    elif parsed.text:
        clinical_text = parsed.text
    elif not sys.stdin.isatty():
        # Read from piped stdin
        clinical_text = sys.stdin.read()
    else:
        sys.stderr.write("Error: Please provide clinical text via --file, --text, --sample, or standard input.\n")
        sys.exit(1)

    # Initialize extraction engine
    nlp = ClinicalNLP(engine=parsed.engine, model_name=parsed.model)
    result = nlp.extract(clinical_text)

    # Format output
    if parsed.format == "json":
        output_str = result.model_dump_json(indent=2)
    elif parsed.format == "markdown":
        output_str = result.to_markdown_report()
    else:
        output_str = format_terminal_summary(result)

    # Write output to file or stdout
    if parsed.output:
        out_path = Path(parsed.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output_str, encoding="utf-8")
        print(f"Results successfully saved to: {parsed.output}")
    else:
        print(output_str)


if __name__ == "__main__":
    main()
