import streamlit as st

from budget import (
    load_data,
    calculate_budget,
    spending_by_category,
    evaluate_purchase,
    build_qvac_prompt,
)
from qvac_client import get_qvac_recommendation


st.set_page_config(
    page_title="Student Money Copilot",
    page_icon="💸",
)

st.title("💸 Student Money Copilot")
st.caption(
    "Hackathon MVP — local QVAC budgeting assistant with RGB integration in progress"
)


transactions, expenses = load_data()

balance = st.number_input(
    "Wallet balance",
    min_value=0.0,
    value=534.0,
    step=10.0,
)

summary = calculate_budget(balance, expenses)


# -----------------------------
# DASHBOARD
# -----------------------------

col1, col2 = st.columns(2)

col1.metric(
    "Balance",
    f"€{summary['balance']:.2f}",
)

col2.metric(
    "Safe to spend",
    f"€{summary['safe_to_spend']:.2f}",
)


st.subheader("Upcoming expenses")

for expense in expenses:
    st.write(
        f"**{expense['name']}** — "
        f"€{expense['amount']:.2f} — "
        f"due {expense['due_date']}"
    )


st.subheader("Recent spending")

for transaction in transactions:
    st.write(
        f"{transaction['date']} · "
        f"{transaction['merchant']} · "
        f"€{transaction['amount']:.2f} · "
        f"{transaction['category']}"
    )


# -----------------------------
# PURCHASE CHECKER
# -----------------------------

st.divider()

st.subheader("🛍️ Can I afford this?")

purchase = st.number_input(
    "Purchase amount",
    min_value=0.0,
    value=80.0,
    step=5.0,
)

if st.button("Check purchase"):

    result = evaluate_purchase(
        balance,
        expenses,
        purchase,
    )

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

    prompt = build_qvac_prompt(
        result,
        expenses,
    )

    with st.spinner(
        "Money Copilot is thinking locally..."
    ):
        try:
            recommendation = get_qvac_recommendation(
                prompt
            )

            st.subheader("🤖 Money Copilot")
            st.write(recommendation)

            st.caption(
                "Generated locally with QVAC"
            )

        except Exception as error:
            st.error(
                "QVAC could not generate a recommendation."
            )
            st.code(str(error))

    with st.expander(
        "See the data sent to QVAC"
    ):
        st.code(prompt)


# -----------------------------
# FREE-FORM MONEY COPILOT
# -----------------------------

st.divider()

st.subheader("💬 Ask Money Copilot")

question = st.text_input(
    "Ask something about your budget",
    placeholder=(
        "Can I afford to go out twice this weekend?"
    ),
)

if st.button("Ask Money Copilot"):

    if question.strip():

        summary = calculate_budget(
            balance,
            expenses,
        )

        expense_text = "\n".join(
            (
                f"- {expense['name']}: "
                f"€{expense['amount']:.2f} "
                f"due {expense['due_date']}"
            )
            for expense in expenses
        )

        transaction_text = "\n".join(
            (
                f"- {transaction['date']} | "
                f"{transaction['merchant']} | "
                f"€{transaction['amount']:.2f} | "
                f"{transaction['category']}"
            )
            for transaction in transactions
        )

        prompt = f"""
You are a private student budgeting assistant.

IMPORTANT:
- Do not invent numbers.
- Do not perform new calculations yourself.
- Use only the financial facts provided below.
- Give a short and practical answer.
- Do not give investment advice.

CURRENT FINANCIAL DATA

Current balance:
€{summary['balance']:.2f}

Upcoming mandatory expenses:
{expense_text}

Total upcoming mandatory expenses:
€{summary['mandatory_expenses']:.2f}

Current safe-to-spend amount:
€{summary['safe_to_spend']:.2f}

Recent transactions:
{transaction_text}

STUDENT QUESTION:
{question}

Answer the student directly in 2-4 sentences.
"""

        with st.spinner(
            "Money Copilot is thinking locally..."
        ):
            try:
                answer = get_qvac_recommendation(
                    prompt
                )

                st.subheader("🤖 Money Copilot")
                st.write(answer)

                st.caption(
                    "Generated locally with QVAC"
                )

            except Exception as error:
                st.error(
                    "QVAC could not answer the question."
                )
                st.code(str(error))

    else:
        st.warning(
            "Please enter a question first."
        )


# -----------------------------
# RGB STATUS
# -----------------------------

st.divider()

st.subheader("₿ RGB Integration")

st.info(
    "RGB wallet integration is currently in progress. "
    "The pre-hackathon prototype already has a working "
    "RGB node, test Bitcoin wallet, RGB-capable UTXOs, "
    "and an issued STUSD test asset."
)