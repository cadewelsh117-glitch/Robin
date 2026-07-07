"""Field schema for commercial property insurance quotes.

Defines the 25 fields the extraction engine looks for, which ones are
required, and how each field's raw text should be parsed into a typed
Python value for comparison.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Callable, Optional


def _parse_money(raw: str) -> float:
    cleaned = raw.replace("$", "").replace(",", "").strip()
    return float(cleaned)


def _parse_percent(raw: str) -> float:
    return float(raw.replace("%", "").strip())


def _parse_date(raw: str) -> date:
    raw = raw.strip()
    for fmt in ("%m/%d/%Y", "%m-%d-%Y", "%B %d, %Y", "%b %d, %Y", "%Y-%m-%d"):
        try:
            from datetime import datetime

            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unrecognized date format: {raw!r}")


def _identity(raw: str) -> str:
    return raw.strip()


@dataclass(frozen=True)
class FieldDef:
    key: str
    label: str
    required: bool
    parser: Callable[[str], Any] = _identity


FIELD_DEFS: list[FieldDef] = [
    FieldDef("carrier_name", "Carrier", required=True),
    FieldDef("quote_number", "Quote #", required=False),
    FieldDef("named_insured", "Named Insured", required=True),
    FieldDef("effective_date", "Effective Date", required=True, parser=_parse_date),
    FieldDef("expiration_date", "Expiration Date", required=True, parser=_parse_date),
    FieldDef("total_premium", "Total Premium", required=True, parser=_parse_money),
    FieldDef("taxes_fees", "Taxes & Fees", required=False, parser=_parse_money),
    FieldDef("building_limit", "Building Limit", required=True, parser=_parse_money),
    FieldDef("bpp_limit", "Business Personal Property Limit", required=False, parser=_parse_money),
    FieldDef("business_income_limit", "Business Income / EE Limit", required=False, parser=_parse_money),
    FieldDef("aop_deductible", "AOP Deductible", required=True, parser=_parse_money),
    FieldDef("wind_hail_deductible", "Wind/Hail Deductible", required=False),
    FieldDef("flood_coverage", "Flood Coverage", required=False),
    FieldDef("earthquake_coverage", "Earthquake Coverage", required=False),
    FieldDef("coinsurance_pct", "Coinsurance %", required=False, parser=_parse_percent),
    FieldDef("valuation", "Valuation (RC/ACV)", required=False),
    FieldDef("covered_locations", "Covered Locations", required=True),
    FieldDef("construction_type", "Construction Type", required=False),
    FieldDef("protection_class", "Protection Class", required=False),
    FieldDef("sprinklered", "Sprinklered", required=False),
    FieldDef("exclusions", "Exclusions", required=False),
    FieldDef("endorsements", "Endorsements", required=False),
    FieldDef("ordinance_or_law", "Ordinance or Law Coverage", required=False),
    FieldDef("equipment_breakdown", "Equipment Breakdown Coverage", required=False),
    FieldDef("payment_plan", "Payment Plan", required=False),
]

FIELD_KEYS = [f.key for f in FIELD_DEFS]
FIELD_BY_KEY = {f.key: f for f in FIELD_DEFS}


@dataclass
class ExtractedField:
    raw_text: Optional[str]
    value: Any
    confidence: float  # 0.0-1.0
    source_snippet: Optional[str] = None
    error: Optional[str] = None


@dataclass
class QuoteRecord:
    source_filename: str
    fields: dict[str, ExtractedField] = field(default_factory=dict)

    def get(self, key: str) -> Optional[ExtractedField]:
        return self.fields.get(key)

    def value(self, key: str) -> Any:
        f = self.fields.get(key)
        return f.value if f else None
