"""Planned EUR expenses, without payment controls.

RGB payment review and approval live in ui/transactions.py.
"""
from datetime import date
import streamlit as st


def _due(raw):
    try:
        return date.fromisoformat(str(raw)).strftime("%d %b %Y")
    except ValueError:
        return str(raw)


def render_regular_expenses(expenses: list[dict], summary: dict):
    st.header("Regular Expenses")
    st.caption("Keep track of upcoming bills and money set aside for essentials.")

    count_col, reserve_col = st.columns(2)
    count_col.metric("Planned expenses", len(expenses))
    reserve_col.metric("Reserved budget (EUR demo)", f"€{summary['mandatory_expenses']:,.2f}")

    st.info("These EUR figures are sample budget data, not your on-chain STUSD balance.")
    st.subheader("Upcoming bills and reserves")

    if not expenses:
        st.info("No planned expenses found.")
        return

    for item in sorted(expenses, key=lambda e: str(e.get("due_date", ""))):
        with st.container(border=True):
            name_col, amount_col = st.columns([3, 1])
            name_col.markdown(f"**{item.get('name', 'Expense')}**")
            name_col.caption(f"Due {_due(item.get('due_date', ''))} · Planned")
            amount_col.markdown(f"**€{float(item['amount']):,.2f}**")

    st.caption("To review the demo rent payment, open the Transactions tab. No automatic payments are enabled.")
