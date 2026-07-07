"""Generates 3 synthetic commercial property quote PDFs for demo/testing.

Not part of the app itself — run this once (`python generate_samples.py`)
to populate this folder with sample_carrier_a.pdf / b.pdf / c.pdf. Requires
reportlab (dev-only dependency, not in requirements.txt).
"""

import os

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

QUOTES = {
    "sample_carrier_a.pdf": """
Carrier: Acme Mutual Insurance
Quote Number: A-10021
Named Insured: Riverside Retail LLC
Effective Date: 08/01/2026
Expiration Date: 08/01/2027
Total Premium: $8,450.00
Taxes & Fees: $310.00
Building Limit: $1,200,000
Business Personal Property Limit: $250,000
Business Income Limit: $150,000
AOP Deductible: $2,500
Wind/Hail Deductible: 2% of building limit
Flood Coverage: Excluded
Earthquake Coverage: Excluded
Coinsurance: 80%
Valuation: Replacement Cost
Covered Locations: 400 Main St, Riverside, CA
Construction Type: Masonry Non-Combustible
Protection Class: 3
Sprinklered: Yes
Exclusions: Flood, Earthquake, Mold
Endorsements: Ordinance or Law, Equipment Breakdown
Ordinance or Law Coverage: Included, $100,000 limit
Equipment Breakdown Coverage: Included
Payment Plan: Annual
""",
    "sample_carrier_b.pdf": """
Carrier: Beacon Property & Casualty
Quote Number: B-55210
Named Insured: Riverside Retail LLC
Effective Date: 08/01/2026
Expiration Date: 08/01/2027
Total Premium: $9,900.00
Taxes & Fees: $340.00
Building Limit: $1,200,000
Business Personal Property Limit: $300,000
Business Income Limit: $200,000
AOP Deductible: $2,500
Wind/Hail Deductible: 2% of building limit
Flood Coverage: $500,000 sublimit
Earthquake Coverage: Excluded
Coinsurance: 80%
Valuation: Replacement Cost
Covered Locations: 400 Main St, Riverside, CA
Construction Type: Masonry Non-Combustible
Protection Class: 3
Sprinklered: Yes
Exclusions: Earthquake, Mold
Endorsements: Ordinance or Law, Equipment Breakdown, Flood Buyback
Ordinance or Law Coverage: Included, $150,000 limit
Equipment Breakdown Coverage: Included
Payment Plan: Quarterly
""",
    "sample_carrier_c.pdf": """
Carrier: Continental Guard Insurance
Quote Number: C-88342
Named Insured: Riverside Retail LLC
Effective Date: 08/01/2026
Expiration Date: 08/01/2027
Total Premium: $7,600.00
Taxes & Fees: $290.00
Building Limit: $1,200,000
Business Personal Property Limit: $250,000
Business Income Limit: $150,000
AOP Deductible: $5,000
Wind/Hail Deductible: 3% of building limit
Flood Coverage: Excluded
Earthquake Coverage: Excluded
Coinsurance: 90%
Valuation: Actual Cash Value
Covered Locations: 400 Main St, Riverside, CA
Construction Type: Masonry Non-Combustible
Protection Class: 3
Sprinklered: Yes
Exclusions: Flood, Earthquake, Mold, Ordinance or Law
Endorsements: Equipment Breakdown
Ordinance or Law Coverage: Excluded
Equipment Breakdown Coverage: Included
Payment Plan: Annual
""",
}


def main() -> None:
    out_dir = os.path.dirname(os.path.abspath(__file__))
    for filename, content in QUOTES.items():
        path = os.path.join(out_dir, filename)
        c = canvas.Canvas(path, pagesize=letter)
        text_obj = c.beginText(50, 740)
        text_obj.setFont("Helvetica", 10)
        for line in content.strip("\n").split("\n"):
            text_obj.textLine(line)
        c.drawText(text_obj)
        c.save()
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
