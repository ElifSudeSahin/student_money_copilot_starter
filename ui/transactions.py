"""Transaction history and UI-only RGB rent-payment preview.

Does NOT initiate wallet, invoice, or on-chain actions. Demonstration approval
is kept separate from transaction history and does not change wallet balances.
"""
from datetime import date
import streamlit as st

PREVIEW_RENT = 250
PREVIEW_BALANCE = 1000
RECIPIENT = "landlord (demo wallet)"


def render_transactions(expenses: list[dict], transactions: list[dict]):
    st.header("Transactions")
    st.caption("Review payment details and browse your recorded spending.")
    st.info(
        "Payment preview only: no verified RGB invoice or wallet connection. "
        "EUR history is sample budget data; STUSD amounts are a separate demo."
    )

    st.subheader("Make a payment · RGB preview")
    rent_item = next(
        (item for item in expenses if "rent" in str(item.get("name", "")).lower()),
        None,
    )
    if rent_item is None:
        st.info("No rent expense is configured. Payment preview is unavailable.")
    else:
        st.caption(
            f"Planned rent: €{float(rent_item['amount']):,.2f} (EUR budget demo). "
            f"The separate mock payment amount is {PREVIEW_RENT} STUSD; "
            "no exchange rate is assumed."
        )
        balance_col, rent_col, after_col = st.columns(3)
        balance_col.metric("Mock STUSD wallet", f"{PREVIEW_BALANCE} STUSD")
        rent_col.metric("Demo payment", f"{PREVIEW_RENT} STUSD")
        after_col.metric("Projected only", f"{PREVIEW_BALANCE - PREVIEW_RENT} STUSD")

        key = "transactions_payment_step"
        if key not in st.session_state:
            st.session_state[key] = "idle"
        step = st.session_state[key]

        if step == "idle":
            st.markdown("**Step 1 of 3 — Prepare**")
            if st.button("Review demo rent payment", type="primary", key="transactions_prepare"):
                st.session_state[key] = "review"
                st.rerun()

        elif step == "review":
            st.markdown("**Step 2 of 3 — Review**")
            with st.container(border=True):
                st.write(f"**Recipient:** {RECIPIENT}")
                st.write(f"**Amount:** {PREVIEW_RENT} STUSD")
                st.write("**Network:** Bitcoin Signet (target)")
                st.write("**Invoice:** Not provided or verified")
            st.button(
                "Confirm real RGB payment",
                disabled=True,
                help="Requires a verified invoice, wallet integration, and explicit approval.",
                key="transactions_real_send_disabled",
            )
            left, right = st.columns(2)
            if left.button("Simulate approval (no transfer)", key="transactions_simulate"):
                st.session_state[key] = "preview_approved"
                st.rerun()
            if right.button("Cancel", key="transactions_cancel"):
                st.session_state[key] = "idle"
                st.rerun()

        elif step == "preview_approved":
            st.markdown("**Step 3 of 3 — Preview complete**")
            st.info(
                "Approval was simulated locally. No transfer was sent, "
                "no transaction was created, and the real wallet balance did not change."
            )
            if st.button("Reset preview", key="transactions_reset"):
                st.session_state[key] = "idle"
                st.rerun()
        else:
            st.session_state[key] = "idle"
            st.rerun()

        with st.expander("RGB teammate integration contract"):
            st.code(
                "get_wallet_snapshot()\n"
                "prepare_rent_payment()\n"
                "send_prepared_payment()  # after explicit approval only\n"
                "get_payment_status()",
                language="python",
            )
            st.caption("Pending does not mean confirmed; retries must not send twice.")

    st.divider()
    st.subheader("Transaction history · EUR demo")
    st.caption("These entries come from the existing sample transactions file, not from the RGB blockchain.")
    if not transactions:
        st.info("No recorded spending yet.")
        return

    rows = []
    for tx in sorted(transactions, key=lambda t: str(t.get("date", "")), reverse=True):
        rows.append({
            "Date": str(tx.get("date", "")),
            "Merchant": str(tx.get("merchant", tx.get("name", "—"))),
            "Category": str(tx.get("category", "Other")),
            "Amount (EUR)": f"€{float(tx.get('amount', 0)):,.2f}",
        })
    st.dataframe(rows, hide_index=True, width="stretch")
