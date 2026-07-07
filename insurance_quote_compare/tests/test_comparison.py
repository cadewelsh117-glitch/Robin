import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from comparison import build_comparison_table, detect_risk_flags, generate_recommendation
from extraction import extract_fields

CHEAP_BASIC = """
Carrier: Cheap Basic Co
Named Insured: Test LLC
Effective Date: 08/01/2026
Expiration Date: 08/01/2027
Total Premium: $5,000.00
Building Limit: $1,000,000
AOP Deductible: $10,000
Covered Locations: 1 Test St
Endorsements: Equipment Breakdown
"""

PRICEY_BROAD = """
Carrier: Pricey Broad Co
Named Insured: Test LLC
Effective Date: 08/01/2026
Expiration Date: 08/01/2027
Total Premium: $8,000.00
Building Limit: $1,000,000
AOP Deductible: $2,500
Wind/Hail Deductible: 2%
Flood Coverage: $500,000
Covered Locations: 1 Test St
Endorsements: Equipment Breakdown, Ordinance or Law, Flood Buyback
"""


def _quotes():
    a = extract_fields(CHEAP_BASIC, source_filename="Cheap Basic Co")
    b = extract_fields(PRICEY_BROAD, source_filename="Pricey Broad Co")
    return [a, b]


def test_comparison_table_has_one_row_per_field_and_column_per_carrier():
    rows = build_comparison_table(_quotes())
    assert len(rows) == 25  # matches FIELD_DEFS count
    row = rows[0]
    assert "Cheap Basic Co" in row
    assert "Pricey Broad Co" in row


def test_risk_flags_catch_premium_spread_and_deductible_gap():
    flags = detect_risk_flags(_quotes())
    messages = [f.message for f in flags]
    assert any("cheaper" in m for m in messages)
    assert any("higher AOP deductible" in m for m in messages)


def test_recommendation_names_cheapest_and_broadest():
    quotes = _quotes()
    flags = detect_risk_flags(quotes)
    rec = generate_recommendation(quotes, flags)
    assert "Cheap Basic Co" in rec
    assert "Pricey Broad Co" in rec
    assert "Recommended option" in rec
