
"""Estimate outing costs from historical transactions."""

def estimate_outings(
    transactions: list[dict],
    count: int,
    safe_to_spend: float,
) -> dict:
    if count <= 0:
        raise ValueError("Outing count must be positive.")

    outing_categories = {"food", "restaurants", "entertainment", "cafes"}
    grocery_merchants = {"carrefour", "lidl", "aldi", "esselunga"}

    relevant = [
        float(tx["amount"])
        for tx in transactions
        if tx.get("category", "").strip().lower() in outing_categories
        and tx.get("merchant", "").strip().lower() not in grocery_merchants
        and float(tx["amount"]) > 0
    ]

    if not relevant:
        return {
            "count": count,
            "sample_size": 0,
            "average": None,
            "estimated_total": None,
            "affordable": None,
            "message": "No relevant outing transactions were found.",
        }

    average = sum(relevant) / len(relevant)
    estimated_total = average * count

    return {
        "count": count,
        "sample_size": len(relevant),
        "average": round(average, 2),
        "estimated_total": round(estimated_total, 2),
        "affordable": estimated_total <= safe_to_spend,
        "message": (
            "Limited historical data; this is an indicative estimate."
            if len(relevant) < 3
            else "Estimate based on historical spending."
        ),
    }

def category_spending_summary(transactions: list[dict]) -> dict:
    """Calculate spending statistics for each category."""

    categories = {}

    for transaction in transactions:
        category = transaction["category"]
        amount = float(transaction["amount"])

        if amount <= 0:
            continue

        if category not in categories:
            categories[category] = {
                "total": 0.0,
                "count": 0,
            }

        categories[category]["total"] += amount
        categories[category]["count"] += 1

    for category, data in categories.items():
        data["average"] = round(
            data["total"] / data["count"], 2
        )
        data["total"] = round(data["total"], 2)

    return categories
