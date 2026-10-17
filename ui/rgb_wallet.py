"""RGB wallet UI for Student Money Copilot.

Shows the STUSD wallet balance and handles the rent payment flow.
Imported by app.py and rendered inside the Transactions tab.

Place this file at: ui/rgb_wallet.py
"""
import streamlit as st

from rgb_client import get_stusd_balance, send_stusd_payment


def _render_balance() -> None:
    """Show settled / future / spendable STUSD balances."""
    try:
        rgb_balance = get_stusd_balance()
        settled = int(rgb_balance.get("settled", 0))
        future = int(rgb_balance.get("future", 0))
        spendable = int(rgb_balance.get("spendable", 0))

        col1, col2, col3 = st.columns(3)
        col1.metric("Settled", f"{settled} STUSD")
        col2.metric("Future", f"{future} STUSD")
        col3.metric("Spendable", f"{spendable} STUSD")

        if settled != future:
            st.info(
                "An RGB transfer is pending. "
                f"The wallet currently projects {future} STUSD after pending transfers."
            )
        else:
            st.success("RGB wallet is synced.")

    except Exception as error:
        st.error(
            "Could not read the RGB wallet. Make sure Docker, studentcopilot, "
            "and landlord2 are running and unlocked."
        )
        st.code(str(error))


def _render_rent_payment(expenses) -> None:
    """Rent payment flow: prepare -> confirm -> send."""
    st.subheader("🏠 Send rent with RGB")

    rent = next(
        (
            expense
            for expense in expenses
            if str(expense.get("name", "")).lower() == "rent"
        ),
        None,
    )

    default_rent = int(float(rent["amount"])) if rent else 250

    rent_amount = st.number_input(
        "Rent payment (STUSD)",
        min_value=1,
        value=default_rent,
        step=1,
        key="rgb_rent_amount",
    )

    st.caption(
        "This sends a real test-network RGB transaction from studentcopilot "
        "to landlord2."
    )

    if "rgb_payment_prepared" not in st.session_state:
        st.session_state["rgb_payment_prepared"] = False

    if st.button("Prepare RGB payment", key="prepare_rgb_payment"):
        st.session_state["rgb_payment_prepared"] = True

    if st.session_state["rgb_payment_prepared"]:
        st.warning(
            f"You are about to send {rent_amount} STUSD on the RGB test network."
        )

        confirm = st.checkbox(
            "I understand this creates a real test-network RGB transaction.",
            key="rgb_confirm_checkbox",
        )

        col_cancel, col_send = st.columns(2)

        with col_cancel:
            if st.button("Cancel", key="cancel_rgb_payment"):
                st.session_state["rgb_payment_prepared"] = False
                st.rerun()

        with col_send:
            if st.button(
                "Confirm & Send",
                key="confirm_rgb_payment",
                disabled=not confirm,
            ):
                with st.spinner("Creating landlord invoice and sending STUSD..."):
                    try:
                        result = send_stusd_payment(int(rent_amount))
                        txid = result.get("txid", "Transaction created")

                        st.success("✅ RGB payment created successfully.")
                        st.write("Transaction ID")
                        st.code(txid)

                        st.session_state["rgb_payment_prepared"] = False
                        st.session_state["last_rgb_txid"] = txid

                    except Exception as error:
                        st.error("RGB payment failed.")
                        st.code(str(error))

    if st.session_state.get("last_rgb_txid"):
        st.caption("Most recent RGB transaction")
        st.code(st.session_state["last_rgb_txid"])


def render_rgb_wallet(expenses) -> None:
    """Entry point used by app.py."""
    st.subheader("₿ RGB Wallet")
    _render_balance()
    st.divider()
    _render_rent_payment(expenses)