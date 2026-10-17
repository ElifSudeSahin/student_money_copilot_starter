"""Frontend-only preview; does not replace or modify the team's app.py."""
import streamlit as st

from budget import load_data, calculate_budget
from ui.styles import apply_styles
from ui.dashboard import render_dashboard
from ui.regular_expenses import render_regular_expenses
from ui.money_copilot import render_money_copilot

st.set_page_config(page_title="Student Money Copilot — UI Preview", page_icon="💸", layout="wide")
apply_styles()

st.title("💸 Student Money Copilot")
st.caption("Frontend preview · Dashboard · Regular Expenses · Money Copilot")
st.info("All EUR budget figures are demo values. The STUSD wallet and chat are UI previews; no real payment or QVAC inference takes place here.")

try:
    transactions, expenses = load_data()
except (OSError, ValueError) as error:
    st.error("Could not read demo JSON files from data/.")
    st.code(str(error))
    st.stop()

with st.sidebar:
    st.header("Budget settings")
    balance = st.number_input("EUR budget balance (demo)", min_value=0.0, value=534.0, step=10.0)
    st.caption("Separate from the RGB STUSD test wallet")

summary = calculate_budget(balance, expenses)
tab_dashboard, tab_expenses, tab_copilot = st.tabs(["📊 Dashboard", "🗓️ Regular Expenses", "💬 Money Copilot"])
with tab_dashboard:
    render_dashboard(balance, summary, expenses, transactions)
with tab_expenses:
    render_regular_expenses(expenses, summary)
with tab_copilot:
    render_money_copilot(summary, expenses, transactions)

