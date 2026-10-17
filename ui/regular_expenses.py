"""Recurring-expense tracking UI and a NON-TRANSACTING rent payment preview.

No wallet/API calls are made from this module.
"""
from datetime import date
import streamlit as st

PREVIEW_RENT = 250
PREVIEW_BALANCE = 1000
RECIPIENT = "landlord (demo wallet)"


def _due(raw):
    try:
        return date.fromisoformat(str(raw)).strftime("%d %b %Y")
    except ValueError:
        return str(raw)


def render_regular_expenses(expenses: list[dict], summary: dict):
    st.header("Regular Expenses")
    st.caption("Review planned expenses. Automatic recurrence is not configured in this prototype.")
    a, b = st.columns(2)
    a.metric("Planned expenses", len(expenses))
    b.metric("Reserved budget (EUR demo)", f"€{summary['mandatory_expenses']:,.2f}")
    st.info("EUR expense data is a budget demo. The STUSD rent payment below is a separate UI-only preview, not a currency conversion.")

    st.subheader("Upcoming bills and reserves")
    if not expenses:
        st.info("No planned expenses found.")
    for item in sorted(expenses, key=lambda e: str(e.get("due_date", ""))):
        with st.container(border=True):
            title_col, amount_col = st.columns([3, 1])
            title_col.markdown(f"**{item.get('name', 'Expense')}**")
            title_col.caption(f"Due {_due(item.get('due_date', ''))} · Planned")
            amount_col.markdown(f"**€{float(item['amount']):,.2f}**")
            if "rent" in str(item.get("name", "")).lower():
                st.caption("Rent is the only expense with an RGB payment UX preview.")
                if st.button("Review rent payment", key="regular_rent_review"):
                    st.session_state["regular_payment_step"] = "review"
                    st.rerun()
            else:
                st.caption("Tracking only — payment not connected")

    st.divider()
    st.subheader("RGB rent payment · UI preview")
    st.warning("No verified invoice, no real RGB connection, and no STUSD transfer. This is a local interface test.")
    x, y, z = st.columns(3)
    x.metric("Rent", f"{PREVIEW_RENT} STUSD")
    y.metric("Wallet (mock)", f"{PREVIEW_BALANCE} STUSD")
    z.metric("Projected after", f"{PREVIEW_BALANCE - PREVIEW_RENT} STUSD")

    if "regular_payment_step" not in st.session_state:
        st.session_state.regular_payment_step = "idle"
    step = st.session_state.regular_payment_step

    if step == "idle":
        st.markdown("**Step 1 of 3 — Prepare**")
        if st.button("Prepare payment preview", key="regular_prepare", type="primary"):
            st.session_state.regular_payment_step = "review"
            st.rerun()
    elif step == "review":
        st.markdown("**Step 2 of 3 — Review**")
        with st.container(border=True):
            st.write(f"**Recipient:** {RECIPIENT}")
            st.write(f"**Amount:** {PREVIEW_RENT} STUSD")
            st.write("**Network:** Bitcoin Signet (target)")
            st.write("**Invoice:** Not connected or verified")
        st.button("Confirm real RGB payment", disabled=True, help="Requires real invoice validation and wallet integration")
        left, right = st.columns(2)
        if left.button("Simulate approval (UI only)", key="regular_simulate"):
            st.session_state.regular_payment_step = "preview_approved"
            st.rerun()
        if right.button("Cancel", key="regular_cancel"):
            st.session_state.regular_payment_step = "idle"
            st.rerun()
    elif step == "preview_approved":
        st.markdown("**Step 3 of 3 — Preview finished**")
        st.info("Approval was simulated. No transaction was submitted. The real STUSD wallet balance is unchanged.")
        if st.button("Reset preview", key="regular_reset"):
            st.session_state.regular_payment_step = "idle"
            st.rerun()
    else:
        st.session_state.regular_payment_step = "idle"
        st.rerun()

    with st.expander("Interface expected from the RGB teammate"):
        st.code("get_wallet_snapshot()\nprepare_rent_payment()\nsend_prepared_payment()  # only after explicit approval\nget_payment_status()", language="python")
        st.caption("Pending does not mean confirmed; prevent duplicate sending on retries and Streamlit reruns.")
