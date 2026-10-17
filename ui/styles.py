"""Shared Streamlit presentation styles for the frontend preview."""
import streamlit as st


def apply_styles():
    st.markdown("""
    <style>
    .block-container { max-width: 1220px; padding-top: 2rem; padding-bottom: 3rem; }
    .smc-label { color: #9db1c9; font-size: .78rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; }
    .smc-overview { display: grid; grid-template-columns: 1.3fr 1fr 1fr; gap: 14px; margin: 16px 0 24px; }
    .smc-stat { background: #192334; border: 1px solid #30415a; border-radius: 16px; padding: 22px; min-height: 145px; }
    .smc-stat.hero { background: linear-gradient(120deg,#143351,#1b2f4c); border-color: #376a90; }
    .smc-stat .name { color: #bdd0e5; font-size: .87rem; }
    .smc-stat .value { color: #fff; font-size: clamp(1.55rem, 2.6vw, 2.2rem); font-weight: 750; margin: 14px 0 7px; }
    .smc-stat.positive .value { color: #83ecc1; }
    .smc-stat .hint { color: #adbed3; font-size: .78rem; }
    .smc-expense { border: 1px solid #303a4d; border-radius: 13px; padding: 16px 18px; margin-bottom: 10px; display: flex; align-items: center; justify-content: space-between; gap: 15px; }
    .smc-expense .title { font-size: .98rem; font-weight: 700; }
    .smc-expense .date { font-size: .79rem; color: #a4b6d0; margin-top: 5px; }
    .smc-expense .amount { white-space: nowrap; font-weight: 750; }
    @media(max-width: 900px) { .smc-overview {grid-template-columns: repeat(2, 1fr);} .smc-stat.hero {grid-column: 1/-1;} }
    @media(max-width: 560px) { .smc-overview {grid-template-columns: 1fr;} .smc-stat.hero {grid-column: auto;} }
    </style>
    """, unsafe_allow_html=True)
