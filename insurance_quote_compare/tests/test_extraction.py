import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extraction import extract_fields, extract_from_pdf

SAMPLE_TEXT = """
Carrier: Acme Mutual Insurance
Quote Number: A-10021
Named Insured: Riverside Retail LLC
Effective Date: 08/01/2026
Expiration Date: 08/01/2027
Total Premium: $8,450.00
Building Limit: $1,200,000
AOP Deductible: $2,500
Coinsurance: 80%
Covered Locations: 400 Main St, Riverside, CA
Endorsements: Ordinance or Law, Equipment Breakdown
"""


def test_extracts_required_fields_with_high_confidence():
    record = extract_fields(SAMPLE_TEXT, source_filename="test.pdf")

    assert record.value("carrier_name") == "Acme Mutual Insurance"
    assert record.value("total_premium") == 8450.00
    assert record.value("building_limit") == 1200000.0
    assert record.value("aop_deductible") == 2500.0
    assert record.value("coinsurance_pct") == 80.0
    assert record.value("effective_date") == date(2026, 8, 1)
    assert record.value("expiration_date") == date(2027, 8, 1)

    assert record.get("total_premium").confidence >= 0.9


def test_missing_field_gets_zero_confidence_and_no_value():
    record = extract_fields("Carrier: Acme Mutual Insurance\n", source_filename="test.pdf")

    missing = record.get("wind_hail_deductible")
    assert missing.value is None
    assert missing.confidence == 0.0
    assert missing.error is not None


def test_unparsable_value_gets_low_confidence():
    text = "Carrier: Acme Mutual Insurance\nTotal Premium: not-a-number\n"
    record = extract_fields(text, source_filename="test.pdf")

    field = record.get("total_premium")
    assert field.value is None
    assert field.confidence < 0.5
    assert field.error is not None


def test_extract_from_real_pdf():
    pdf_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "sample_quotes", "sample_carrier_a.pdf",
    )
    if not os.path.exists(pdf_path):
        import pytest
        pytest.skip("sample PDF not generated; run sample_quotes/generate_samples.py first")

    record = extract_from_pdf(pdf_path, source_filename="sample_carrier_a.pdf")
    assert record.value("carrier_name") == "Acme Mutual Insurance"
    assert record.value("total_premium") == 8450.00
