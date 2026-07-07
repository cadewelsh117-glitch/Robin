"""Insurance Quote Comparison — MVP.

Single-user Streamlit app. Upload 2-5 commercial property quote PDFs,
extract structured fields, validate them, compare side by side, and
draft a recommendation. No login, no database — everything lives in the
Streamlit session for this MVP.
"""

import pandas as pd
import streamlit as st

from comparison import build_comparison_table, detect_risk_flags, generate_recommendation
from extraction import extract_from_pdf
from schema import QuoteRecord
from validation import validate_quote

st.set_page_config(page_title="Insurance Quote Comparison", layout="wide")

st.title("Commercial Property Quote Comparison")
st.caption(
    "Upload 2-5 commercial property quote PDFs to get a side-by-side comparison, "
    "risk flags, and a draft recommendation. Always review before sending to a client."
)

uploaded_files = st.file_uploader(
    "Upload quote PDFs", type=["pdf"], accept_multiple_files=True,
)

if uploaded_files and len(uploaded_files) > 5:
    st.error("Please upload at most 5 quotes at a time.")
    st.stop()

if uploaded_files and len(uploaded_files) < 2:
    st.info("Upload at least 2 quotes to run a comparison.")

if uploaded_files and len(uploaded_files) >= 2:
    quotes: list[QuoteRecord] = []
    for uploaded in uploaded_files:
        record = extract_from_pdf(uploaded, source_filename=uploaded.name)
        quotes.append(record)

    st.header("1. Validation")
    any_blocking = False
    for quote in quotes:
        issues = validate_quote(quote)
        errors = [i for i in issues if i.severity == "error"]
        warnings = [i for i in issues if i.severity == "warning"]
        with st.expander(
            f"{quote.source_filename} — {len(errors)} error(s), {len(warnings)} warning(s)",
            expanded=bool(errors),
        ):
            if not issues:
                st.success("No validation issues.")
            for issue in errors:
                st.error(issue.message)
                any_blocking = True
            for issue in warnings:
                st.warning(issue.message)

    st.header("2. Side-by-Side Comparison")
    table_rows = build_comparison_table(quotes)
    df = pd.DataFrame(table_rows).set_index("field")
    st.dataframe(df, use_container_width=True)

    with st.expander("View extraction source & confidence for each field"):
        for quote in quotes:
            st.subheader(quote.source_filename)
            detail_rows = []
            for key, extracted in quote.fields.items():
                detail_rows.append({
                    "field": key,
                    "value": extracted.value,
                    "confidence": f"{extracted.confidence:.0%}",
                    "source snippet": extracted.source_snippet or "—",
                    "note": extracted.error or "",
                })
            st.dataframe(pd.DataFrame(detail_rows), use_container_width=True, hide_index=True)

    st.header("3. Risk Flags")
    flags = detect_risk_flags(quotes)
    if not flags:
        st.info("No risk flags detected.")
    for flag_item in flags:
        if flag_item.severity == "warning":
            st.warning(flag_item.message)
        else:
            st.info(flag_item.message)

    st.header("4. Draft Recommendation")
    if any_blocking:
        st.error(
            "One or more quotes have blocking validation errors (missing required fields, "
            "bad dates, etc.). Fix or manually review those quotes before relying on this "
            "recommendation."
        )
    recommendation = generate_recommendation(quotes, flags)
    st.markdown(recommendation)
    st.caption("This is a draft. A human agent must review before sending to the client.")
