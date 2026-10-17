"""Student Money Copilot - main entry point.

Python calculates the budget, local QVAC explains it, RGB handles STUSD payments.
All feature logic lives in separate modules; this file only wires them together.
"""
import streamlit as st

from budget import load_data, calculate_budget
from ui.styles import apply_styles
from ui.dashboard import render_dashboard
from ui.qvac_purchase import render_qvac_purchase
from ui.regular_expenses import render_regular_expenses
from ui.transactions import render_transactions
from ui.rgb_wallet import render_rgb_wallet
from ui.qvac_copilot import render_qvac_copilot


def setup_page() -> None:
    st.set_page_config(page_title="Student Money Copilot", page_icon="💸", layout="wide")
    apply_styles()
    st.title("💸 Student Money Copilot")
    st.caption("Student budgeting · Python calculations · local QVAC · live RGB wallet payments")


def load_or_stop():
    try:
        return load_data()
    except (OSError, ValueError) as error:
        st.error("Cannot read demo expense and transaction files.")
        st.code(str(error))
        st.stop()


def render_sidebar() -> float:
    with st.sidebar:
        st.header("Budget settings")
        balance = st.number_input(
            "EUR budget balance (demo)", min_value=0.0, value=534.0, step=10.0
        )
        st.caption("EUR demo figures are separate from the RGB STUSD wallet.")
    return balance


def main() -> None:
    setup_page()
    transactions, expenses = load_or_stop()
    balance = render_sidebar()
    summary = calculate_budget(balance, expenses)

    tab_dashboard, tab_expenses, tab_transactions, tab_copilot = st.tabs([
        "📊 Dashboard",
        "🗓️ Regular Expenses",
        "💳 Transactions",
        "💬 Money Copilot",
    ])

    with tab_dashboard:
        render_dashboard(balance, summary, expenses, transactions)
        render_qvac_purchase(balance, expenses)

    with tab_expenses:
        render_regular_expenses(expenses, summary)

    with tab_transactions:
        render_transactions(expenses, transactions)
        st.divider()
        render_rgb_wallet(expenses)

    with tab_copilot:
        render_qvac_copilot(summary, expenses, transactions)

    st.caption(
        "Budget figures are demo EUR values. RGB wallet balances and sends use the "
        "live local STUSD test-network setup."
    )


main()