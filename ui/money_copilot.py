"""Money Copilot chat. Python verifies the numbers; local QVAC phrases the answer.

Place this file at ui/money_copilot.py. Chat history lives in session_state,
so answers survive Streamlit reruns.
"""
import streamlit as st

from copilot_logic import answer_question


def render_money_copilot(summary: dict, expenses: list[dict], transactions: list[dict]):
    st.header("Ask Money Copilot")
    st.caption("Python calculates the numbers. Local QVAC writes the advice.")

    if "copilot_chat" not in st.session_state:
        st.session_state.copilot_chat = []

    for entry in st.session_state.copilot_chat:
        with st.chat_message(entry["role"]):
            st.write(entry["content"])
            if entry.get("caption"):
                st.caption(entry["caption"])

    question = st.chat_input(
        "Ask about your budget, e.g. Can I go out 3 times this week?",
        key="copilot_chat_input",
    )
    if question and question.strip():
        st.session_state.copilot_chat.append({"role": "user", "content": question.strip()})
        with st.spinner("QVAC is answering locally..."):
            result = answer_question(question.strip(), summary, expenses, transactions)
        st.session_state.copilot_chat.append(
            {"role": "assistant", "content": result["text"], "caption": result["caption"]}
        )
        st.rerun()

    if st.session_state.copilot_chat and st.button("Clear chat", key="copilot_clear"):
        st.session_state.copilot_chat = []
        st.rerun()
