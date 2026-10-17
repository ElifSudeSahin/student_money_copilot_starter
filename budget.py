import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

def load_data():
    transactions = json.loads((DATA_DIR / "transactions.json").read_text())
    expenses = json.loads((DATA_DIR / "expenses.json").read_text())
    return transactions, expenses

def calculate_budget(balance: float, expenses: list[dict]) -> dict:
    mandatory = sum(float(item["amount"]) for item in expenses)
    safe_to_spend = balance - mandatory
    return {
        "balance": balance,
        "mandatory_expenses": mandatory,
        "safe_to_spend": safe_to_spend,
    }

def spending_by_category(transactions: list[dict]) -> dict:
    totals = {}
    for tx in transactions:
        category = tx["category"]
        totals[category] = totals.get(category, 0) + float(tx["amount"])
    return totals

def evaluate_purchase(balance: float, expenses: list[dict], purchase_amount: float) -> dict:
    summary = calculate_budget(balance, expenses)
    after_purchase = summary["safe_to_spend"] - purchase_amount

    if after_purchase < 0:
        status = "not_recommended"
        reason = "This purchase would use money needed for upcoming expenses."
    elif after_purchase < 50:
        status = "risky"
        reason = "You can technically afford it, but your remaining flexible money would be low."
    else:
        status = "okay"
        reason = "This purchase fits inside your current flexible budget."

    return {
        **summary,
        "purchase_amount": purchase_amount,
        "flexible_after_purchase": after_purchase,
        "status": status,
        "reason": reason,
    }

def build_qvac_prompt(result: dict, expenses: list[dict]) -> str:
    upcoming = "\n".join(
        f"- {e['name']}: €{e['amount']:.2f} due {e['due_date']}"
        for e in expenses
    )
    return f"""You are a concise student budgeting copilot.

Current balance: €{result['balance']:.2f}
Upcoming expenses:
{upcoming}

Safe-to-spend before purchase: €{result['safe_to_spend']:.2f}
Proposed purchase: €{result['purchase_amount']:.2f}
Flexible money after purchase: €{result['flexible_after_purchase']:.2f}
Rule-based status: {result['status']}
Reason: {result['reason']}

Give the student a short recommendation in 2-3 sentences.
Do not invent numbers and do not give investment advice."""
