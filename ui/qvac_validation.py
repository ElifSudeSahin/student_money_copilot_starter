"""Helpers for checking QVAC answers against Python-verified figures.

Currently not called anywhere; kept here so app.py stays clean.
"""
import re
from decimal import Decimal


def euro_amounts(text: str) -> set[Decimal]:
    """Recognize €450 and €450.00 as the same amount."""
    matches = re.findall(r"€\s*([0-9]+(?:[.,][0-9]{1,2})?)", text)
    return {Decimal(value.replace(",", ".")) for value in matches}


def valid_outing_answer(answer: str, average: float, total: float,
                        available: float, affordable: bool) -> bool:
    """Reject obvious QVAC contradictions; not a guarantee of full accuracy."""
    amounts = euro_amounts(answer)
    expected = {Decimal(str(value)) for value in (average, total, available)}
    if not expected.issubset(amounts):
        return False

    normalized = answer.lower().replace("’", "'")
    negative_terms = (
        "cannot afford", "can't afford", "not affordable", "not enough",
        "insufficient", "exceeds", "exceed your", "over budget",
        "falls short", "shortfall", "does not fit", "doesn't fit",
        "more than your", "higher than your", "beyond your budget",
    )
    positive_terms = (
        "you can afford", "you could afford", "sufficient to cover",
        "enough to cover", "fits within", "within your budget",
        "within the budget", "can cover the cost", "can comfortably afford",
    )

    if affordable:
        # Must positively recognize the verified affordable estimate.
        return (
            any(term in normalized for term in positive_terms)
            and not any(term in normalized for term in negative_terms)
        )

    # The verified plan is over budget. Reject explicit opposite claims.
    return (
        any(term in normalized for term in negative_terms)
        and not any(term in normalized for term in positive_terms)
        and "=" not in answer  # disallow QVAC's invented arithmetic
    )