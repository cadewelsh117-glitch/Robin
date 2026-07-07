"""Text extraction and field parsing for commercial property quote documents.

Pipeline: PDF/text -> raw text -> per-field regex extraction -> typed value
with a confidence score. Fields that can't be found are left blank with
confidence 0.0 so they get flagged for human review instead of silently
dropped.
"""

import re
from typing import IO, Optional, Union

import pdfplumber

from schema import FIELD_DEFS, ExtractedField, QuoteRecord

# One or more regex patterns per field. Patterns use a named group "val"
# for the value to capture. First pattern to match wins.
FIELD_PATTERNS: dict[str, list[str]] = {
    "carrier_name": [
        r"Carrier(?:\s*Name)?\s*[:\-]\s*(?P<val>.+)",
        r"Insurance Company\s*[:\-]\s*(?P<val>.+)",
    ],
    "quote_number": [
        r"Quote\s*(?:Number|#|No\.?)\s*[:\-]\s*(?P<val>\S+)",
    ],
    "named_insured": [
        r"Named Insured\s*[:\-]\s*(?P<val>.+)",
        r"Insured\s*[:\-]\s*(?P<val>.+)",
    ],
    "effective_date": [
        r"Effective Date\s*[:\-]\s*(?P<val>[A-Za-z0-9,/\-\s]+?)(?:\n|$)",
    ],
    "expiration_date": [
        r"Expiration Date\s*[:\-]\s*(?P<val>[A-Za-z0-9,/\-\s]+?)(?:\n|$)",
    ],
    "total_premium": [
        r"Total Premium\s*[:\-]\s*\$?(?P<val>[\d,]+(?:\.\d{2})?)",
        r"Annual Premium\s*[:\-]\s*\$?(?P<val>[\d,]+(?:\.\d{2})?)",
    ],
    "taxes_fees": [
        r"Taxes\s*(?:&|and)\s*Fees\s*[:\-]\s*\$?(?P<val>[\d,]+(?:\.\d{2})?)",
    ],
    "building_limit": [
        r"Building Limit\s*[:\-]\s*\$?(?P<val>[\d,]+(?:\.\d{2})?)",
    ],
    "bpp_limit": [
        r"(?:Business Personal Property|BPP) Limit\s*[:\-]\s*\$?(?P<val>[\d,]+(?:\.\d{2})?)",
    ],
    "business_income_limit": [
        r"Business Income(?:\s*/\s*EE)? Limit\s*[:\-]\s*\$?(?P<val>[\d,]+(?:\.\d{2})?)",
    ],
    "aop_deductible": [
        r"(?:AOP|All Other Perils) Deductible\s*[:\-]\s*\$?(?P<val>[\d,]+(?:\.\d{2})?)",
    ],
    "wind_hail_deductible": [
        r"Wind\s*/?\s*Hail Deductible\s*[:\-]\s*(?P<val>.+)",
    ],
    "flood_coverage": [
        r"Flood Coverage\s*[:\-]\s*(?P<val>.+)",
    ],
    "earthquake_coverage": [
        r"Earthquake Coverage\s*[:\-]\s*(?P<val>.+)",
    ],
    "coinsurance_pct": [
        r"Coinsurance\s*[:\-]\s*(?P<val>[\d.]+)\s*%",
    ],
    "valuation": [
        r"Valuation\s*[:\-]\s*(?P<val>.+)",
    ],
    "covered_locations": [
        r"Covered Location(?:s)?\s*[:\-]\s*(?P<val>.+)",
    ],
    "construction_type": [
        r"Construction(?:\s*Type)?\s*[:\-]\s*(?P<val>.+)",
    ],
    "protection_class": [
        r"Protection Class\s*[:\-]\s*(?P<val>.+)",
    ],
    "sprinklered": [
        r"Sprinklered\s*[:\-]\s*(?P<val>.+)",
    ],
    "exclusions": [
        r"Exclusions\s*[:\-]\s*(?P<val>.+)",
    ],
    "endorsements": [
        r"Endorsements\s*[:\-]\s*(?P<val>.+)",
    ],
    "ordinance_or_law": [
        r"Ordinance or Law(?:\s*Coverage)?\s*[:\-]\s*(?P<val>.+)",
    ],
    "equipment_breakdown": [
        r"Equipment Breakdown(?:\s*Coverage)?\s*[:\-]\s*(?P<val>.+)",
    ],
    "payment_plan": [
        r"Payment Plan\s*[:\-]\s*(?P<val>.+)",
    ],
}


def extract_text_from_pdf(file: Union[str, IO[bytes]]) -> str:
    """Read all text from a digital (non-scanned) PDF."""
    chunks = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            chunks.append(text)
    return "\n".join(chunks)


def _find_field(text: str, field_key: str) -> Optional[re.Match]:
    for pattern in FIELD_PATTERNS.get(field_key, []):
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match
    return None


def extract_fields(text: str, source_filename: str = "") -> QuoteRecord:
    """Parse raw quote text into a QuoteRecord of typed, confidence-scored fields."""
    record = QuoteRecord(source_filename=source_filename)

    for field_def in FIELD_DEFS:
        match = _find_field(text, field_def.key)
        if not match:
            record.fields[field_def.key] = ExtractedField(
                raw_text=None, value=None, confidence=0.0,
                error="Field not found in document",
            )
            continue

        raw_val = match.group("val").strip()
        try:
            parsed = field_def.parser(raw_val)
            record.fields[field_def.key] = ExtractedField(
                raw_text=raw_val,
                value=parsed,
                confidence=0.9,
                source_snippet=match.group(0).strip(),
            )
        except (ValueError, TypeError) as exc:
            record.fields[field_def.key] = ExtractedField(
                raw_text=raw_val,
                value=None,
                confidence=0.2,
                source_snippet=match.group(0).strip(),
                error=f"Could not parse value: {exc}",
            )

    return record


def extract_from_pdf(file: Union[str, IO[bytes]], source_filename: str = "") -> QuoteRecord:
    text = extract_text_from_pdf(file)
    return extract_fields(text, source_filename=source_filename or (file if isinstance(file, str) else "uploaded.pdf"))
