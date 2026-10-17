"""Dashboard UI only: budget calculations stay in budget.py."""
from datetime import date
from html import escape

import streamlit as st

from budget import evaluate_purchase, spending_by_category, build_qvac_prompt


def _eur(value):
    return f"€{float(value):,.2f}"


def _due(raw):
    try:
        return date.fromisoformat(str(raw)).strftime("%d %b %Y")
    except ValueError:
        return str(raw)


def render_dashboard(balance: float, summary: dict, expenses: list[dict], transactions: list[dict]):
    """Render the budget overview with demo EUR data, independent of RGB/QVAC."""
    st.markdown('<div class="smc-label">Your financial snapshot</div>', unsafe_allow_html=True)
    st.header("Your money, at a glance")
    st.caption("EUR sample data only. These figures are not your on-chain STUSD wallet balance.")

    safe = float(summary["safe_to_spend"])
    cards = [
        ("Current budget balance", _eur(summary["balance"]), "Demo budget · EUR", "hero"),
        ("Safe to spend", _eur(safe), "After setting money aside for planned expenses", "positive" if safe >= 0 else ""),
        ("Upcoming obligations", _eur(summary["mandatory_expenses"]), f"{len(expenses)} planned expenses", ""),
    ]
    html = '<div class="smc-overview">'
    for label, value, note, cls in cards:
        html += (f'<div class="smc-stat {cls}"><div class="name">{escape(label)}</div>'
                 f'<div class="value">{escape(value)}</div><div class="hint">{escape(note)}</div></div>')
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

    if safe < 0:
        st.warning("Upcoming expenses exceed the demo balance. Review your budget before new purchases.")

    st.subheader("📅 Upcoming expenses")
    st.caption("Expenses reserved when Python calculates your safe-to-spend amount.")
    if not expenses:
        st.info("No upcoming expenses.")
    for expense in sorted(expenses, key=lambda item: str(item.get("due_date", ""))):
        name = escape(str(expense.get("name", "Expense")))
        due = escape(_due(expense.get("due_date", "")))
        amount = escape(_eur(expense["amount"]))
        st.markdown(f'<div class="smc-expense"><div><div class="title">{name}</div>'
                    f'<div class="date">Due {due}</div></div><div class="amount">{amount}</div></div>',
                    unsafe_allow_html=True)

    st.subheader("🧾 Spending insights")
    left, right = st.columns([1.65, 1], gap="large")
    with left:
        st.markdown("**Recent transactions**")
        if transactions:
            rows = [{"Date": str(tx.get("date", "")),
                     "Merchant": str(tx.get("merchant", tx.get("description", "Transaction"))),
                     "Category": str(tx.get("category", "Other")),
                     "Amount": float(tx["amount"])}
                    for tx in sorted(transactions, key=lambda row: str(row.get("date", "")), reverse=True)]
            st.dataframe(rows, hide_index=True, use_container_width=True, height=250,
                         column_config={"Amount": st.column_config.NumberColumn("Amount (€)", format="€%.2f")})
        else:
            st.info("No recent transactions.")
    with right:
        st.markdown("**Spending by category**")
        totals = spending_by_category(transactions)
        total_spend = sum(max(float(v), 0) for v in totals.values())
        if total_spend:
            for cat, amount in sorted(totals.items(), key=lambda row: row[1], reverse=True):
                share = max(0.0, min(1.0, float(amount) / total_spend))
                st.progress(share, text=f"{cat} · {_eur(amount)}")
        else:
            st.caption("No spending data available.")

    st.divider()
    st.subheader("🛍️ Can I afford this?")
    st.caption("Python calculates purchase affordability. Local QVAC can explain it after integration.")
    purchase = st.number_input("Purchase amount (EUR demo)", min_value=0.0, value=80.0, step=5.0, key="preview_purchase")
    if st.button("Check purchase", key="preview_check_purchase", type="primary"):
        result = evaluate_purchase(balance, expenses, purchase)
        if result["status"] == "okay":
            st.success(result["reason"])
        elif result["status"] == "risky":
            st.warning(result["reason"])
        else:
            st.error(result["reason"])
        st.write(f"Flexible money after purchase: **{_eur(result['flexible_after_purchase'])}**")
        st.caption("QVAC explanation is intentionally disabled in the independent frontend preview.")
        with st.expander("See facts prepared for QVAC"):
            st.code(build_qvac_prompt(result, expenses))
