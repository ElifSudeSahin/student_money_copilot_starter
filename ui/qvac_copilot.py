"""Money Copilot tab: Python-verified outing estimates plus local QVAC answers."""
import re

import streamlit as st

from qvac_client import get_qvac_recommendation
from spending_insights import estimate_outings, category_spending_summary
from ui.money_copilot import render_money_copilot

OUTING_PHRASES = ("go out", "going out", "outing", "outings")
OUTING_COUNT_PATTERN = r"\b(\d+)\s+(?:times?|outings?)\b"


# ---------------------------------------------------------------------------
# Outing questions ("Can I afford to go out 10 times?")
# ---------------------------------------------------------------------------

def _verified_outing_text(count, sample_size, average, total, available, affordable) -> str:
    """Python provides the verified financial facts."""
    intro = (
        f"Based on {sample_size} relevant past transaction(s), "
        f"your average transaction was €{average:.2f}. "
        f"At that rate, {count} outings would cost approximately "
    )
    if affordable:
        return (
            intro
            + f"€{total:.2f}, which fits your €{available:.2f} "
            "flexible budget under this estimate."
        )
    shortfall = max(0.0, total - available)
    return (
        intro
        + f"€{total:.2f}, exceeding your €{available:.2f} "
        f"flexible budget by €{shortfall:.2f}. "
        "You cannot afford this plan under this estimate."
    )


def _build_tip_prompt(question: str, affordable: bool, sample_size: int) -> str:
    decision = "WITHIN BUDGET" if affordable else "OVER BUDGET"
    return f"""
You are QVAC, a private AI budgeting copilot for students.

STUDENT QUESTION:
{question}

VERIFIED PYTHON DECISION:
{decision}

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


def _is_valid_tip(tip: str, affordable: bool) -> bool:
    """Basic sanity checks on QVAC's one-sentence tip."""
    tip_lower = tip.lower()

    relevant = any(
        word in tip_lower
        for word in ("outing", "go out", "activit", "event", "trip", "plan")
    )
    no_numbers = re.search(r"\d|€|\$", tip) is None
    no_contradiction = not (
        not affordable
        and any(
            phrase in tip_lower
            for phrase in ("can afford", "enough money", "within your budget")
        )
    )
    return bool(tip) and len(tip) < 240 and relevant and no_numbers and no_contradiction


def _get_outing_tip(question: str, affordable: bool, sample_size: int):
    """Returns (tip, came_from_qvac)."""
    fallback_tip = (
        "Consider fewer outings or lower-cost activities."
        if not affordable
        else "Consider setting a limit for each outing."
    )

    prompt = _build_tip_prompt(question, affordable, sample_size)
    with st.spinner("QVAC is generating a personalized recommendation..."):
        try:
            tip = get_qvac_recommendation(prompt).strip().strip('"')
            valid = _is_valid_tip(tip, affordable)
        except Exception:
            tip, valid = "", False

    return (tip, True) if valid else (fallback_tip, False)


def _answer_outing_question(question: str, count: int, transactions, available: float) -> None:
    if count == 0:
        st.info("Please choose at least one outing.")
        return

    insight = estimate_outings(transactions, count, available)
    sample_size = insight["sample_size"]

    if sample_size == 0:
        st.info(
            "I don't have relevant spending history yet. "
            "How much do you usually spend on a complete outing?"
        )
        return

    affordable = insight["affordable"]
    verified_text = _verified_outing_text(
        count, sample_size, insight["average"],
        insight["estimated_total"], available, affordable,
    )
    tip, from_qvac = _get_outing_tip(question, affordable, sample_size)

    # One combined answer, not two separate outputs.
    st.write(verified_text + " " + tip)

    if from_qvac:
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


# ---------------------------------------------------------------------------
# General questions
# ---------------------------------------------------------------------------

def _build_general_prompt(question, summary, available, expenses, transactions) -> str:
    expense_text = "\n".join(
        f"- {e['name']}: €{float(e['amount']):.2f} due {e['due_date']}"
        for e in expenses
    )
    transaction_text = "\n".join(
        f"- {t['merchant']}: €{float(t['amount']):.2f} ({t['category']})"
        for t in transactions
    )
    category_text = "\n".join(
        f"- {category}: "
        f"total spent €{data['total']:.2f}, "
        f"{data['count']} transactions, "
        f"average €{data['average']:.2f} per transaction"
        for category, data in category_spending_summary(transactions).items()
    )

    return f"""
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


def _answer_general_question(question, summary, available, expenses, transactions) -> None:
    prompt = _build_general_prompt(question, summary, available, expenses, transactions)

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


# ---------------------------------------------------------------------------
# Tab entry point
# ---------------------------------------------------------------------------

def render_qvac_copilot(summary, expenses, transactions) -> None:
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

            outing_question = any(phrase in text for phrase in OUTING_PHRASES)
            match = re.search(OUTING_COUNT_PATTERN, text)

            st.subheader("🤖 Money Copilot")

            if outing_question and match:
                _answer_outing_question(question, int(match.group(1)), transactions, available)
            else:
                _answer_general_question(question, summary, available, expenses, transactions)

    with st.expander("Preview-only chat interface (not connected to QVAC)"):
        render_money_copilot(summary, expenses, transactions)