"""Student Money Copilot - Streamlit application with modular UI.

Keeps the existing QVAC spending analysis intact. RGB payment is UI preview only.
"""
import re
from decimal import Decimal
import streamlit as st

from budget import load_data, calculate_budget, evaluate_purchase, build_qvac_prompt
from qvac_client import get_qvac_recommendation
from spending_insights import estimate_outings, category_spending_summary
from ui.styles import apply_styles
from ui.dashboard import render_dashboard
from ui.regular_expenses import render_regular_expenses
from ui.transactions import render_transactions
from ui.money_copilot import render_money_copilot

def euro_amounts(text: str) -> set[Decimal]:
    """Recognize €450 and €450.00 as the same amount."""
    matches = re.findall(r"€\s*([0-9]+(?:[.,][0-9]{1,2})?)", text)
    return {Decimal(value.replace(",", ".")) for value in matches}


def valid_outing_answer(answer: str, average: float, total: float,
                        available: float, affordable: bool) -> bool:
    """Reject obvious QVAC contradictions; not a guarantee of full accuracy."""
    amounts = euro_amounts(answer)
    expected = {Decimal(str(value)) for value in (average, total, available)}
    if not expected.issubset(amounts):
        return False

    normalized = answer.lower().replace("’", "'")
    negative_terms = (
        "cannot afford", "can't afford", "not affordable", "not enough",
        "insufficient", "exceeds", "exceed your", "over budget",
        "falls short", "shortfall", "does not fit", "doesn't fit",
        "more than your", "higher than your", "beyond your budget",
    )
    positive_terms = (
        "you can afford", "you could afford", "sufficient to cover",
        "enough to cover", "fits within", "within your budget",
        "within the budget", "can cover the cost", "can comfortably afford",
    )

    if affordable:
        # Must positively recognize the verified affordable estimate.
        return (
            any(term in normalized for term in positive_terms)
            and not any(term in normalized for term in negative_terms)
        )

    # The verified plan is over budget. Reject explicit opposite claims.
    return (
        any(term in normalized for term in negative_terms)
        and not any(term in normalized for term in positive_terms)
        and "=" not in answer  # disallow QVAC's invented arithmetic
    )


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
    # Existing QVAC purchase explanation is kept separately from the new UI purchase check.
    with st.expander("QVAC purchase explanation (existing feature)"):
        purchase = st.number_input("Purchase amount for QVAC (EUR demo)", min_value=0.0, value=80.0, step=5.0, key="legacy_qvac_purchase")
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
    st.subheader("Ask Money Copilot · QVAC")
    st.caption("Existing Python-verified QVAC analysis. Local QVAC model required for AI responses.")
    question = st.text_input(
        "Ask something about your budget",
        placeholder="Can I afford to go out 100 times in a week?",
    )

    if st.button("Ask Money Copilot"):
        if not question.strip():
            st.warning("Please enter a question first.")
        else:
            available = summary["safe_to_spend"]
            text = question.lower()

            outing_question = any(
                phrase in text
                for phrase in ("go out", "going out", "outing", "outings")
            )

            match = re.search(
                r"\b(\d+)\s+(?:times?|outings?)\b", text
            )

            st.subheader("🤖 Money Copilot")

            if outing_question and match:
                count = int(match.group(1))

                if count == 0:
                    st.info("Please choose at least one outing.")

                else:
                    insight = estimate_outings(
                        transactions, count, available
                    )

                    if insight["sample_size"] == 0:
                        st.info(
                            "I don't have relevant spending history yet. "
                            "How much do you usually spend on a complete outing?"
                        )

                    else:
                        average = insight["average"]
                        total = insight["estimated_total"]
                        sample_size = insight["sample_size"]
                        affordable = insight["affordable"]

                        shortfall = max(0.0, total - available)

                        # Python provides verified financial facts.
                        if affordable:
                            verified_text = (
                                f"Based on {sample_size} relevant past transaction(s), "
                                f"your average transaction was €{average:.2f}. "
                                f"At that rate, {count} outings would cost approximately "
                                f"€{total:.2f}, which fits your €{available:.2f} "
                                "flexible budget under this estimate."
                            )
                        else:
                            verified_text = (
                                f"Based on {sample_size} relevant past transaction(s), "
                                f"your average transaction was €{average:.2f}. "
                                f"At that rate, {count} outings would cost approximately "
                                f"€{total:.2f}, exceeding your €{available:.2f} "
                                f"flexible budget by €{shortfall:.2f}. "
                                "You cannot afford this plan under this estimate."
                            )

                        # QVAC generates the personalized recommendation.
                        tip_prompt = f"""
    You are QVAC, a private AI budgeting copilot for students.

    STUDENT QUESTION:
    {question}

    VERIFIED PYTHON DECISION:
    {"OVER BUDGET" if not affordable else "WITHIN BUDGET"}

    Historical evidence:
    Only {sample_size} relevant transaction(s) are available.

    YOUR TASK:
    Suggest one specific, practical change to the student's
    outing plans based on the verified decision.

    RULES:
    - Write exactly ONE short English sentence.
    - Address the student directly.
    - Do not include any numbers or money amounts.
    - Do not perform calculations.
    - Do not contradict the verified decision.
    - Focus on outings, not generic budget management.
    - Do not discuss unrelated bills or investments.
    - Output only the recommendation.
    """

                        fallback_tip = (
                            "Consider fewer outings or lower-cost activities."
                            if not affordable
                            else "Consider setting a limit for each outing."
                        )

                        with st.spinner(
                            "QVAC is generating a personalized recommendation..."
                        ):
                            try:
                                tip = get_qvac_recommendation(
                                    tip_prompt
                                ).strip().strip('"')

                                tip_lower = tip.lower()

                                relevant = any(
                                    word in tip_lower
                                    for word in (
                                        "outing", "go out", "activit",
                                        "event", "trip", "plan"
                                    )
                                )

                                no_numbers = re.search(
                                    r"\d|€|\$", tip
                                ) is None

                                no_contradiction = not (
                                    not affordable
                                    and any(
                                        phrase in tip_lower
                                        for phrase in (
                                            "can afford",
                                            "enough money",
                                            "within your budget",
                                        )
                                    )
                                )

                                valid_tip = (
                                    bool(tip)
                                    and len(tip) < 240
                                    and relevant
                                    and no_numbers
                                    and no_contradiction
                                )

                            except Exception:
                                valid_tip = False
                                tip = ""

                        final_tip = tip if valid_tip else fallback_tip

                        # One combined answer, not two separate outputs.
                        st.write(verified_text + " " + final_tip)

                        if valid_tip:
                            st.caption(
                                "Budget calculations verified by Python. "
                                "Personalized recommendation generated locally by QVAC. "
                                f"Estimate based on {sample_size} transaction(s); "
                                "a transaction may not represent a complete outing."
                            )
                        else:
                            st.caption(
                                "QVAC was called, but its recommendation did not "
                                "pass basic checks. A rule-based tip was used. "
                                "Budget calculations are verified by Python."
                            )

            else:
                # General questions still use QVAC directly.
                expense_text = "\n".join(
                    f"- {e['name']}: €{float(e['amount']):.2f} "
                    f"due {e['due_date']}"
                    for e in expenses
                )

                transaction_text = "\n".join(
                    f"- {t['merchant']}: €{float(t['amount']):.2f} "
                    f"({t['category']})"
                    for t in transactions
                )
                category_stats = category_spending_summary(transactions)

                category_text = "\n".join(
                    f"- {category}: "
                    f"total spent €{data['total']:.2f}, "
                    f"{data['count']} transactions, "
                    f"average €{data['average']:.2f} per transaction"
                    for category, data in category_stats.items()
                )
                prompt = f"""
    You are QVAC, a private student budgeting assistant.

    USER QUESTION:
    {question}

    VERIFIED FINANCIAL FACTS:
    Wallet balance: €{summary['balance']:.2f}
    Reserved mandatory expenses: €{summary['mandatory_expenses']:.2f}
    Flexible budget: €{available:.2f}

    Upcoming expenses:
    {expense_text}

    Past transactions (already spent):
    {transaction_text}

    VERIFIED SPENDING STATISTICS:
    {category_text}

    IMPORTANT:
    - Category totals and averages were calculated by Python.
    - Use these figures when answering questions about spending habits.
    - A category average is per transaction, not necessarily per outing.
    - Do not invent or recalculate financial figures.

    Answer the user's actual question in 2-3 sentences.
    Do not invent prices or income.
    Do not calculate new balances.
    Reserved expenses are NOT incoming money.
    If required information is missing, ask for it.
    """

                with st.spinner("QVAC is answering locally..."):
                    try:
                        answer = get_qvac_recommendation(prompt).strip()

                        if answer:
                            st.write(answer)
                            st.caption(
                                "Generated locally with QVAC. "
                                "Financial claims in general answers "
                                "are not independently verified."
                            )
                        else:
                            st.warning("QVAC returned an empty response.")

                    except Exception as error:
                        st.error("QVAC could not answer the question.")
                        st.code(str(error))



    with st.expander("Preview-only chat interface (not connected to QVAC)"):
        render_money_copilot(summary, expenses, transactions)

st.caption("RGB: on-chain STUSD sending is not connected here. Payment controls are demo-only.")
