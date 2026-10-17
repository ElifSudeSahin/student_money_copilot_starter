import streamlit as st


# ==========================================
# STUDENT MONEY COPILOT
# CALM FINANCE DESIGN SYSTEM
# ==========================================

# COLOR PALETTE
COLORS = {
    "background": "#F7F9F6",
    "surface": "#FFFFFF",
    "surface_soft": "#F1F5F0",

    "primary": "#50816A",
    "primary_light": "#E6F1E9",
    "primary_hover": "#3F6D56",

    "lavender": "#EDEFF8",
    "lavender_dark": "#767CAC",

    "text": "#283A34",
    "text_secondary": "#718078",
    "text_muted": "#87958D",

    "border": "#E5EBE5",

    "success": "#2E6851",
    "warning": "#A47740",
    "danger": "#B65B5B",
}


def apply_styles():
    """Apply the Calm Finance design system."""

    st.markdown(
        """
        <style>

        /* ==================================
           1. GLOBAL APP
        ================================== */

        .stApp {
            background-color: #F7F9F6;
            color: #283A34;
        }

        .block-container {
            max-width: 1200px;
            padding-top: 2rem;
            padding-bottom: 4rem;
        }

        html, body {
            font-family: 'Inter', sans-serif;
        }

        h1, h2, h3, h4 {
            color: #283A34 !important;
            font-weight: 650;
            letter-spacing: -0.025em;
        }

        p {
            line-height: 1.65;
        }


        /* ==================================
           2. SIDEBAR
        ================================== */

        section[data-testid="stSidebar"] {
            background-color: #F1F5F0;
            border-right: 1px solid #E5EBE5;
        }


        /* ==================================
           3. TABS
        ================================== */

        .stTabs [data-baseweb="tab-list"] {
            gap: 12px;
            background: transparent;
            border-bottom: 1px solid #E5EBE5;
        }

        .stTabs [data-baseweb="tab"] {
            color: #718078;
            font-weight: 550;
            padding: 12px 18px;
            border-radius: 12px 12px 0 0;
        }

        .stTabs [aria-selected="true"] {
            color: #50816A !important;
            background-color: #E6F1E9;
        }


        /* ==================================
           4. OVERVIEW CARDS
        ================================== */

        .smc-overview {
            display: grid;
            grid-template-columns: 1.4fr 1fr 1fr;
            gap: 16px;
            margin: 20px 0 32px;
        }

        .smc-stat {
            background: #FFFFFF;
            border: 1px solid #E5EBE5;
            border-radius: 20px;
            padding: 24px;
            min-height: 155px;

            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }

        .smc-stat--hero {
            background: #E6F1E9;
            border-color: #D4E7D9;
        }

        .smc-stat--positive {
            background: #FFFFFF;
        }

        .smc-stat-label {
            font-size: 0.9rem;
            font-weight: 550;
            color: #718078;
        }

        .smc-stat-value {
            font-size: 2rem;
            font-weight: 700;
            letter-spacing: -0.04em;
            color: #283A34;
            margin: 12px 0;
        }

        .smc-stat--positive .smc-stat-value {
            color: #2E6851;
        }

        .smc-stat-foot {
            font-size: 0.79rem;
            color: #718078;
            line-height: 1.5;
        }


        /* ==================================
           5. EXPENSE CARDS
        ================================== */

        .smc-expense {
            background: #FFFFFF;
            border: 1px solid #E5EBE5;
            border-radius: 16px;

            padding: 18px 22px;
            margin-bottom: 12px;

            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 16px;
        }

        .smc-expense-title {
            font-size: 0.98rem;
            font-weight: 650;
            color: #283A34;
        }

        .smc-expense-due {
            font-size: 0.8rem;
            color: #87958D;
            margin-top: 5px;
        }

        .smc-expense-amount {
            font-weight: 650;
            color: #283A34;
            white-space: nowrap;
        }


        /* ==================================
           6. SECTION HEADINGS
        ================================== */

        .smc-section-eyebrow {
            color: #50816A;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            margin-bottom: 8px;
        }

        .smc-section-title {
            font-size: 1.4rem;
            font-weight: 700;
            color: #283A34;
            margin: 24px 0 8px;
        }

        .smc-mini-note {
            color: #718078;
            font-size: 0.86rem;
            margin: 0 0 18px;
        }


        /* ==================================
           7. BUTTONS
        ================================== */

        .stButton > button {
            border-radius: 12px;
            border: 1px solid #DCE6DD;
            background-color: #FFFFFF;
            color: #283A34;
            font-weight: 600;
            padding: 0.6rem 1.2rem;
            transition: background-color 0.2s ease;
        }

        .stButton > button:hover {
            border-color: #50816A;
            background-color: #E6F1E9;
            color: #2E6851;
        }

        .stButton > button[kind="primary"] {
            background-color: #50816A;
            color: #FFFFFF;
            border-color: #50816A;
        }

        .stButton > button[kind="primary"]:hover {
            background-color: #3F6D56;
            color: #FFFFFF;
        }

        .stButton > button:focus-visible {
            outline: 3px solid #A4CDB5;
            outline-offset: 2px;
        }


        /* ==================================
           8. INPUT FIELDS
        ================================== */

        .stTextInput input,
        .stNumberInput input,
        .stChatInput textarea {
            background-color: #FFFFFF;
            color: #283A34;
            border-radius: 12px;
        }


        /* ==================================
           9. CHAT MESSAGES
        ================================== */

        [data-testid="stChatMessage"] {
            border-radius: 18px;
            padding: 16px;
            margin-bottom: 12px;
            background-color: #FFFFFF;
            border: 1px solid #E5EBE5;
        }

        [data-testid="stChatMessage"]:has(
            [data-testid="stChatMessageAvatarAssistant"]
        ) {
            background-color: #EDEFF8;
        }


        /* ==================================
           10. TABLES
        ================================== */

        [data-testid="stDataFrame"] {
            border-radius: 14px;
            overflow: hidden;
            border: 1px solid #E5EBE5;
        }


        /* ==================================
           11. RESPONSIVE DESIGN
        ================================== */

        @media (max-width: 900px) {

            .smc-overview {
                grid-template-columns: 1fr 1fr;
            }

            .smc-stat--hero {
                grid-column: 1 / -1;
            }

        }

        @media (max-width: 600px) {

            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }

            .smc-overview {
                grid-template-columns: 1fr;
            }

            .smc-stat--hero {
                grid-column: auto;
            }

            .smc-stat {
                min-height: 130px;
                padding: 18px;
            }

            .smc-expense {
                padding: 16px;
            }

        }

        </style>
        """,
        unsafe_allow_html=True,
    )


inject_styles = apply_styles