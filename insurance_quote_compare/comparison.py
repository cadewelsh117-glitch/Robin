"""Side-by-side comparison, risk flagging, and recommendation drafting.

Takes 2-5 validated QuoteRecords and produces:
  - a comparison table (rows = fields, columns = carriers)
  - a list of risk flags (material differences worth calling out)
  - a plain-English recommendation
"""

from dataclasses import dataclass

from schema import FIELD_DEFS, QuoteRecord


@dataclass
class RiskFlag:
    message: str
    severity: str  # "info" | "warning"


def build_comparison_table(quotes: list[QuoteRecord]) -> list[dict]:
    """Return one row per field: {"field": label, "<carrier>": display_value, ...}."""
    rows = []
    for field_def in FIELD_DEFS:
        row = {"field": field_def.label}
        for quote in quotes:
            extracted = quote.get(field_def.key)
            if extracted is None or extracted.value in (None, ""):
                row[quote.source_filename] = "⚠ missing"
            else:
                row[quote.source_filename] = extracted.value
        rows.append(row)
    return rows


def _cheapest(quotes: list[QuoteRecord]) -> QuoteRecord | None:
    priced = [q for q in quotes if q.value("total_premium") is not None]
    if not priced:
        return None
    return min(priced, key=lambda q: q.value("total_premium"))


def detect_risk_flags(quotes: list[QuoteRecord]) -> list[RiskFlag]:
    flags: list[RiskFlag] = []
    cheapest = _cheapest(quotes)

    premiums = {q.source_filename: q.value("total_premium") for q in quotes if q.value("total_premium") is not None}
    if len(premiums) >= 2:
        spread = max(premiums.values()) - min(premiums.values())
        if spread > 0.15 * min(premiums.values()):
            cheap_name = min(premiums, key=premiums.get)
            flags.append(RiskFlag(
                message=f"{cheap_name} is more than 15% cheaper than the next lowest quote — "
                        f"confirm coverage wasn't reduced to hit that price.",
                severity="warning",
            ))

    deductibles = {q.source_filename: q.value("aop_deductible") for q in quotes if q.value("aop_deductible") is not None}
    if len(deductibles) >= 2:
        highest_ded_name = max(deductibles, key=deductibles.get)
        if deductibles[highest_ded_name] > 1.5 * min(deductibles.values()):
            flags.append(RiskFlag(
                message=f"{highest_ded_name} carries a materially higher AOP deductible "
                        f"(${deductibles[highest_ded_name]:,.0f}) than the other quotes.",
                severity="warning",
            ))

    wind_hail = {q.source_filename: q.value("wind_hail_deductible") for q in quotes}
    missing_wind_hail = [name for name, val in wind_hail.items() if not val]
    if 0 < len(missing_wind_hail) < len(quotes):
        flags.append(RiskFlag(
            message=f"No wind/hail deductible found for: {', '.join(missing_wind_hail)}. "
                     "Confirm whether wind/hail is excluded, bundled into AOP, or simply not quoted.",
            severity="warning",
        ))

    endorsement_sets = {q.source_filename: set(_split_list(q.value("endorsements"))) for q in quotes}
    all_endorsements = set().union(*endorsement_sets.values()) if endorsement_sets else set()
    for name, endorsements in endorsement_sets.items():
        missing = all_endorsements - endorsements
        if missing and all_endorsements:
            flags.append(RiskFlag(
                message=f"{name} is missing endorsement(s) present in other quotes: {', '.join(sorted(missing))}.",
                severity="info",
            ))

    if cheapest:
        flags.append(RiskFlag(
            message=f"{cheapest.source_filename} has the lowest total premium "
                    f"(${cheapest.value('total_premium'):,.2f}).",
            severity="info",
        ))

    return flags


def _split_list(raw) -> list[str]:
    if not raw:
        return []
    return [item.strip() for item in str(raw).split(",") if item.strip()]


def _broadest_coverage(quotes: list[QuoteRecord]) -> QuoteRecord | None:
    def coverage_score(q: QuoteRecord) -> int:
        score = 0
        for key in ("flood_coverage", "earthquake_coverage", "ordinance_or_law", "equipment_breakdown"):
            val = q.value(key)
            if val and str(val).strip().lower() not in ("no", "none", "excluded", "n/a"):
                score += 1
        score += len(_split_list(q.value("endorsements")))
        return score

    scored = [(coverage_score(q), q) for q in quotes]
    if not scored:
        return None
    return max(scored, key=lambda pair: pair[0])[1]


def generate_recommendation(quotes: list[QuoteRecord], flags: list[RiskFlag]) -> str:
    if not quotes:
        return "No quotes to compare."

    cheapest = _cheapest(quotes)
    broadest = _broadest_coverage(quotes)

    lines = []
    if cheapest:
        lines.append(f"- **{cheapest.source_filename}** is the cheapest option at "
                      f"${cheapest.value('total_premium'):,.2f} total premium.")
    if broadest and broadest is not cheapest:
        lines.append(f"- **{broadest.source_filename}** offers the broadest coverage "
                      f"(most included endorsements and optional coverages).")

    warnings = [f for f in flags if f.severity == "warning"]
    for w in warnings:
        lines.append(f"- ⚠ {w.message}")

    if cheapest and broadest and cheapest.source_filename == broadest.source_filename:
        recommended = cheapest.source_filename
        rationale = "lowest premium and broadest coverage among the options presented"
    elif broadest:
        recommended = broadest.source_filename
        rationale = "best balance of price and coverage breadth"
    elif cheapest:
        recommended = cheapest.source_filename
        rationale = "lowest premium among the options presented"
    else:
        recommended = None
        rationale = None

    summary = "\n".join(lines) if lines else "No material differences detected."

    if recommended:
        summary += f"\n\n**Recommended option: {recommended}** — {rationale}. " \
                    "Review before sending to the client."
    return summary
