"""Business-rule validation for extracted quote fields.

Runs after extraction and before comparison. Anything that fails here
should stop the quote from going straight into an auto-generated
recommendation — it needs a human to look at it first.
"""

from dataclasses import dataclass

from schema import FIELD_BY_KEY, QuoteRecord

LOW_CONFIDENCE_THRESHOLD = 0.5


@dataclass
class ValidationIssue:
    field_key: str
    message: str
    severity: str  # "error" | "warning"


def validate_quote(quote: QuoteRecord) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    for key, field_def in FIELD_BY_KEY.items():
        extracted = quote.get(key)

        if field_def.required and (extracted is None or extracted.value in (None, "")):
            issues.append(ValidationIssue(
                field_key=key,
                message=f"Required field '{field_def.label}' is missing.",
                severity="error",
            ))
            continue

        if extracted is None or extracted.value is None:
            continue

        if extracted.confidence < LOW_CONFIDENCE_THRESHOLD:
            issues.append(ValidationIssue(
                field_key=key,
                message=f"'{field_def.label}' has low extraction confidence "
                        f"({extracted.confidence:.0%}) — needs human review.",
                severity="warning",
            ))

    effective = quote.value("effective_date")
    expiration = quote.value("expiration_date")
    if effective and expiration and effective >= expiration:
        issues.append(ValidationIssue(
            field_key="effective_date",
            message="Effective date is not before expiration date.",
            severity="error",
        ))

    premium = quote.value("total_premium")
    if premium is not None and premium <= 0:
        issues.append(ValidationIssue(
            field_key="total_premium",
            message="Total premium must be a positive number.",
            severity="error",
        ))

    return issues


def has_blocking_errors(issues: list[ValidationIssue]) -> bool:
    return any(i.severity == "error" for i in issues)
