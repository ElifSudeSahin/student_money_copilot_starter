"""Chat UI preview. Intentionally makes no QVAC calls until integration is ready."""
import streamlit as st


def render_money_copilot(summary: dict, expenses: list[dict], transactions: list[dict]):
    st.header("Ask Money Copilot")
    st.caption("Local QVAC integration will be connected by the AI teammate. This is a frontend-only chat preview.")
    st.info("Chat messages are displayed locally. No QVAC response is generated in this preview.")

    if "preview_chat" not in st.session_state:
        st.session_state.preview_chat = []

    for entry in st.session_state.preview_chat:
        with st.chat_message(entry["role"]):
            st.write(entry["content"])

    question = st.chat_input("Ask about your budget, for example: Should I pay my rent?")
    if question and question.strip():
        st.session_state.preview_chat.append({"role": "user", "content": question.strip()})
        st.session_state.preview_chat.append({"role": "assistant", "content": "UI preview only: QVAC is not connected here yet. No financial recommendation or payment was generated."})
        st.rerun()

    if st.button("Clear preview chat"):
        st.session_state.preview_chat = []
        st.rerun()
