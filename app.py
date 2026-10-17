"""Student Money Copilot - Streamlit application with modular UI.

Python calculates the budget, local QVAC explains it. RGB payment is UI preview only.
"""
import streamlit as st

from budget import load_data, calculate_budget, evaluate_purchase, build_qvac_prompt
from qvac_client import get_qvac_recommendation
from ui.styles import apply_styles
from ui.dashboard import render_dashboard
from ui.regular_expenses import render_regular_expenses
from ui.transactions import render_transactions
from ui.money_copilot import render_money_copilot

st.set_page_config(page_title="Student Money Copilot", page_icon="💸", layout="wide")
apply_styles()
st.title("💸 Student Money Copilot")
st.caption("Student budgeting · Python calculations · local QVAC · RGB integration in progress")

try:
    transactions, expenses = load_data()
except (OSError, ValueError) as error:
    st.error("Cannot read demo expense and transaction files.")
    st.code(str(error))
    st.stop()

with st.sidebar:
    st.header("Budget settings")
    balance = st.number_input("EUR budget balance (demo)", min_value=0.0, value=534.0, step=10.0)
    st.caption("EUR demo figures are separate from the RGB STUSD wallet.")

summary = calculate_budget(balance, expenses)

tab_dashboard, tab_expenses, tab_transactions, tab_copilot = st.tabs([
    "📊 Dashboard", "🗓️ Regular Expenses", "💳 Transactions", "💬 Money Copilot"
])

with tab_dashboard:
    render_dashboard(balance, summary, expenses, transactions)
    # Existing QVAC purchase explanation, kept separate from the UI purchase check.
    with st.expander("QVAC purchase explanation (existing feature)"):
        purchase = st.number_input(
            "Purchase amount for QVAC (EUR demo)",
            min_value=0.0, value=80.0, step=5.0, key="legacy_qvac_purchase",
        )
        if st.button("Explain purchase with QVAC", key="legacy_qvac_check"):
            result = evaluate_purchase(balance, expenses, purchase)
            if result["status"] == "okay":
                st.success(result["reason"])
            elif result["status"] == "risky":
                st.warning(result["reason"])
            else:
                st.error(result["reason"])

            st.write(
                "Flexible money after purchase: "
                f"**€{result['flexible_after_purchase']:.2f}**"
            )
            prompt = build_qvac_prompt(result, expenses)
            with st.spinner("Money Copilot is thinking locally..."):
                try:
                    recommendation = get_qvac_recommendation(prompt)
                    st.subheader("🤖 Money Copilot")
                    st.write(recommendation)
                    st.caption("Generated locally with QVAC; verified figures are shown above")
                except Exception as error:
                    st.error("QVAC could not generate a recommendation.")
                    st.code(str(error))
            st.caption("Data sent to QVAC:")
            st.code(prompt)

with tab_expenses:
    render_regular_expenses(expenses, summary)

with tab_transactions:
    render_transactions(expenses, transactions)

with tab_copilot:
    render_money_copilot(summary, expenses, transactions)

st.caption("RGB: on-chain STUSD sending is not connected here. Payment controls are demo-only.")