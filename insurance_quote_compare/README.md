# Insurance Quote Comparison (MVP)

Narrow, single-purpose tool for one workflow: an independent P&C agent
uploads 2–5 **commercial property** quote PDFs and gets a side-by-side
comparison, risk flags, and a draft recommendation.

## What this is (and isn't)

Built as a narrow workflow machine, not a platform. It does one job:

```
documents in -> data extracted -> rules checked -> quotes compared -> recommendation out
```

Explicitly **not** in scope for this version: login/accounts, a CRM, a
full quoting engine, carrier system integrations, claims workflows, or a
customer self-service portal. Single-user, no auth, no database — each
session is stateless.

## Scope: commercial property, 25 fields

`schema.py` defines the field schema extraction targets:

Carrier, Quote #, Named Insured, Effective/Expiration Date, Total
Premium, Taxes & Fees, Building Limit, BPP Limit, Business Income Limit,
AOP Deductible, Wind/Hail Deductible, Flood Coverage, Earthquake
Coverage, Coinsurance %, Valuation, Covered Locations, Construction
Type, Protection Class, Sprinklered, Exclusions, Endorsements, Ordinance
or Law Coverage, Equipment Breakdown Coverage, Payment Plan.

## Pipeline

1. **Intake** (`extraction.py`) — `pdfplumber` pulls text from digital
   (non-scanned) PDFs.
2. **Extraction** — regex-based field extraction maps raw text to typed
   values (money, dates, percentages) with a confidence score per field.
   Fields that can't be found are left blank at 0% confidence rather
   than guessed, so they surface for review instead of silently failing.
3. **Validation** (`validation.py`) — required fields must be present,
   premium must be a positive number, effective date must precede
   expiration date, and any field under 50% confidence is flagged as a
   warning for human review.
4. **Comparison** (`comparison.py`) — builds a field-by-carrier table,
   flags material differences (premium spread >15%, deductible gaps,
   missing endorsements/wind-hail terms), and drafts a plain-English
   recommendation naming the cheapest and broadest-coverage options.
5. **UI** (`app.py`) — Streamlit app: upload, validation summary,
   comparison table, per-field source/confidence drill-down, risk
   flags, and the draft recommendation. Always labeled as a draft for
   human review before it goes to a client.

## Running it

```bash
pip install -r requirements.txt
streamlit run app.py
```

Upload 2–5 commercial property quote PDFs. Three synthetic sample
quotes are included for a quick test:

```bash
streamlit run app.py
# then upload the files in sample_quotes/*.pdf
```

(Sample PDFs were generated with `sample_quotes/generate_samples.py`,
which needs `reportlab` — a dev-only dependency, not required to run
the app itself.)

## Tests

```bash
pip install pytest
pytest tests/
```

Covers field extraction (including from a real PDF), validation rules,
and the comparison/recommendation logic.

## Known limitations (by design, for v1)

- Digital PDFs only — no OCR for scanned documents yet.
- Field extraction is regex/pattern-based, tuned to common quote layouts.
  Carriers with very different formatting will need broader field
  extraction and lower confidence scores until patterns are added.
- No persistence: nothing is saved between sessions. Add document
  storage and an audit trail (upload time, extracted values, edits,
  exports) before using this for real client work.
