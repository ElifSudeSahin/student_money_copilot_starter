"""QVAC purchase explanation (the original feature, shown on the Dashboard tab)."""
import streamlit as st

from budget import evaluate_purchase, build_qvac_prompt
from qvac_client import get_qvac_recommendation


def render_qvac_purchase(balance: float, expenses) -> None:
    with st.expander("QVAC purchase explanation (existing feature)"):
        purchase = st.number_input(
            "Purchase amount for QVAC (EUR demo)",
            min_value=0.0,
            value=80.0,
            step=5.0,
            key="legacy_qvac_purchase",
        )
        if not st.button("Explain purchase with QVAC", key="legacy_qvac_check"):
            return

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