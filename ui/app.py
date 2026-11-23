# ==============================================================================
# File: ui/app.py
# Project: SuryaGharSathi (सूर्याघर साथी)
# Description: Day 10 - Streamlit Interactive Web Application for SuryaGharSathi.
#              Connects to FastAPI (/agent and /ask), renders grounded citations,
#              interactive 10-year solar payback charts, and persists user feedback.
# ==============================================================================

import json
import logging
import os
import sys
from datetime import datetime
from typing import Any

import pandas as pd
import requests
import streamlit as st

# Ensure project root is available for direct imports if API service is offline
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from app.graph import langgraph_agent
    from app.tools import solar_cfa_calculator
except Exception:
    pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ui")

# Backend API Configuration
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
FEEDBACK_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "feedback.json")

# ------------------------------------------------------------------------------
# Streamlit Page Setup
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="SuryaGharSathi (सूर्याघर साथी) - AI Solar Advisory",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #e65100;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #555555;
        margin-bottom: 15px;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 12px;
        border-left: 4px solid #ff9800;
    }
    .citation-box {
        background-color: #f1f8e9;
        border-radius: 6px;
        padding: 8px 12px;
        border-left: 3px solid #4caf50;
        font-size: 0.88rem;
        margin-top: 8px;
    }
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------------------------
def save_feedback(question: str, rating: str, answer_snippet: str):
    """Persist user thumbs up / thumbs down feedback to data/feedback.json."""
    records = []
    if os.path.exists(FEEDBACK_FILE):
        try:
            with open(FEEDBACK_FILE, encoding="utf-8") as f:
                records = json.load(f)
        except Exception:
            records = []

    feedback_entry = {
        "id": len(records) + 1,
        "timestamp": datetime.now().isoformat(),
        "rating": rating,
        "question": question,
        "answer_snippet": answer_snippet[:150]
    }
    records.append(feedback_entry)

    os.makedirs(os.path.dirname(FEEDBACK_FILE), exist_ok=True)
    with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)


def call_backend_agent(
    question: str,
    user_name: str,
    bill: float,
    terrace: float,
    approved: bool = False
) -> dict[str, Any]:
    """Call FastAPI /agent endpoint with fallback to direct in-memory invocation."""
    payload = {
        "question": question,
        "user_name": user_name,
        "monthly_bill": bill,
        "terrace_sqm": terrace,
        "approved": approved,
        "thread_id": f"session_{user_name.lower().replace(' ', '_')}"
    }
    try:
        resp = requests.post(f"{API_URL}/agent", json=payload, timeout=10.0)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        logger.info(f"FastAPI service unreachable at {API_URL} ({e}). Using direct agent engine.")

    # In-memory execution fallback
    try:
        return langgraph_agent.run(
            question=question,
            user_name=user_name,
            monthly_bill=bill,
            terrace_sqm=terrace,
            approved=approved,
            thread_id=payload["thread_id"]
        )
    except Exception as ex:
        return {
            "question": question,
            "answer": f"⚠️ Advisory error: {ex!s}",
            "steps": ["Fallback error handler"],
            "calculation": None,
            "citations": [],
            "requires_approval": False
        }


def generate_payback_dataframe(net_cost: float, annual_savings: float) -> pd.DataFrame:
    """Compute cumulative savings vs net investment trajectory over 10 years."""
    years = list(range(11))
    cumulative_savings = [round(y * annual_savings, 2) for y in years]
    investment_line = [round(net_cost, 2)] * len(years)

    return pd.DataFrame({
        "Year": [f"Year {y}" for y in years],
        "Cumulative Savings (₹)": cumulative_savings,
        "Net Capital Cost (₹)": investment_line
    }).set_index("Year")


# ------------------------------------------------------------------------------
# Sidebar - Homeowner Profile & Controls
# ------------------------------------------------------------------------------
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Emblem_of_India.svg/200px-Emblem_of_India.svg.png", width=65)
    st.title("🏡 Homeowner Profile")
    st.caption("PM Surya Ghar: Muft Bijli Yojana")

    user_name = st.text_input("Homeowner Name", value="Abhishek Dighe")
    user_city = st.text_input("Location / City", value="Kopargaon, Maharashtra")

    st.divider()
    st.subheader("⚡ Electricity & Rooftop")
    monthly_bill = st.slider("Monthly MSEDCL Bill (₹)", min_value=500, max_value=10000, value=2000, step=100)
    terrace_sqm = st.slider("Shadow-Free Terrace Area (sq m)", min_value=10, max_value=150, value=40, step=5)

    st.divider()
    st.subheader("⚙️ System Presets")
    preset_choice = st.selectbox(
        "Quick Sizing Evaluation",
        ["Custom Query", "2 kW System (Kopargaon)", "3 kW System (Recommended)", "5 kW System (Higher Usage)"]
    )

    if st.button("🧹 Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.caption("SuryaGharSathi v1.0 • CSE AI & ML, Sanjivani")


# ------------------------------------------------------------------------------
# Main Application Header
# ------------------------------------------------------------------------------
st.markdown('<div class="main-header">☀️ SuryaGharSathi (सूर्याघर साथी)</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">AI-Powered Grounded Advisory for PM Surya Ghar: Muft Bijli Yojana | Target: Kopargaon Homeowners</div>',
    unsafe_allow_html=True
)

# Quick Metrics Row (Live Sizing Preview)
preview_calc = solar_cfa_calculator(
    capacity_kw=3.0 if "3 kW" in preset_choice else 2.0 if "2 kW" in preset_choice else 3.0,
    monthly_bill=float(monthly_bill),
    available_terrace_sqm=float(terrace_sqm)
)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(
        label="Eligible Central Subsidy (CFA)",
        value=f"₹{preview_calc['eligible_subsidy_inr']:,}",
        delta="Capped at ₹78,000" if preview_calc['capacity_kw'] >= 3 else "₹30,000/kW"
    )
with col2:
    st.metric(
        label="Net Installation Outlay",
        value=f"₹{preview_calc['net_cost_to_consumer_inr']:,}",
        delta=f"Total: ₹{preview_calc['estimated_total_cost_inr']:,}",
        delta_color="inverse"
    )
with col3:
    status_text = "Feasible ✅" if preview_calc['is_area_sufficient'] else "Area Shortage ⚠️"
    st.metric(
        label="Rooftop Area Status",
        value=f"{preview_calc['required_terrace_sqm']} / {preview_calc['available_terrace_sqm']} sq m",
        delta=status_text
    )
with col4:
    st.metric(
        label="Estimated Payback Period",
        value=f"{preview_calc['payback_period_years']} Years",
        delta=f"~₹{preview_calc['estimated_annual_savings_inr']:,}/yr savings"
    )

st.divider()

# ------------------------------------------------------------------------------
# Chat History Management
# ------------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                f"Namaste {user_name}! I am **SuryaGharSathi**, your official AI solar assistant for Kopargaon. "
                f"I can calculate your PM Surya Ghar central subsidy, assess whether your {terrace_sqm} sq m terrace "
                f"is sufficient, estimate your electricity savings against your ₹{monthly_bill:,} MSEDCL bill, "
                f"and answer questions on warranties and net metering rules with verified MNRE citations.\n\n"
                f"How can I assist you with your rooftop solar installation today?"
            ),
            "citations": ["PM Surya Ghar Operational Guidelines (June 2024) - Clause 4 (CFA Component)"],
            "calculation": preview_calc
        }
    ]

# Render existing chat conversation
for idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        # Display Calculation & Payback Chart if present in assistant response
        calc_data = msg.get("calculation")
        if calc_data and msg["role"] == "assistant":
            with st.expander("📈 View 10-Year Solar Payback & Economics Chart", expanded=False):
                df_payback = generate_payback_dataframe(
                    net_cost=calc_data["net_cost_to_consumer_inr"],
                    annual_savings=calc_data["estimated_annual_savings_inr"]
                )
                st.line_chart(df_payback, color=["#2e7d32", "#c62828"])
                st.caption(
                    f"🟢 Green Line: Cumulative Electricity Bill Savings | 🔴 Red Line: Net Capital Investment (₹{calc_data['net_cost_to_consumer_inr']:,}). "
                    f"The lines cross at Year {calc_data['payback_period_years']} (Break-even Payback Point)."
                )

        # Display Citations
        cits = msg.get("citations", [])
        if cits and msg["role"] == "assistant":
            with st.expander("📜 Official Source Citations", expanded=False):
                for c in cits:
                    st.markdown(f"- 🏛️ `{c}`")

        # Feedback buttons for assistant responses
        if msg["role"] == "assistant" and idx > 0:
            fb_col1, fb_col2, _ = st.columns([1, 1, 10])
            with fb_col1:
                if st.button("👍", key=f"up_{idx}", help="Helpful and accurate"):
                    save_feedback(st.session_state.messages[idx - 1]["content"], "up", msg["content"])
                    st.toast("Thank you for your feedback! 👍")
            with fb_col2:
                if st.button("👎", key=f"down_{idx}", help="Needs improvement"):
                    save_feedback(st.session_state.messages[idx - 1]["content"], "down", msg["content"])
                    st.toast("Feedback recorded for model tuning. 👎")


# ------------------------------------------------------------------------------
# Chat Input & User Prompt Handling
# ------------------------------------------------------------------------------
user_query = st.chat_input("Ask about subsidies, rooftop area, savings, warranties, or application steps...")

# Handle Preset Click
preset_prompt = None
if preset_choice == "2 kW System (Kopargaon)":
    preset_prompt = "What is the total subsidy, required terrace area, and estimated savings for a 2 kW solar system in Kopargaon?"
elif preset_choice == "3 kW System (Recommended)":
    preset_prompt = "Can I install a 3 kW solar plant on my 40 sq m roof in Kopargaon with Rs 2000 bill, and what warranty is provided?"
elif preset_choice == "5 kW System (Higher Usage)":
    preset_prompt = "How much subsidy and terrace area do I need for a 5 kW solar plant?"

active_input = user_query or (preset_prompt if st.session_state.get("last_preset") != preset_choice and preset_choice != "Custom Query" else None)

if active_input:
    st.session_state["last_preset"] = preset_choice

    # Append user question to chat history
    st.session_state.messages.append({"role": "user", "content": active_input})
    with st.chat_message("user"):
        st.markdown(active_input)

    # Invoke LangGraph Agent / Backend Service
    with st.chat_message("assistant"):
        with st.spinner("Analyzing rules & calculating solar financials..."):
            agent_result = call_backend_agent(
                question=active_input,
                user_name=user_name,
                bill=float(monthly_bill),
                terrace=float(terrace_sqm)
            )

        answer_text = agent_result.get("answer", "Unable to complete advisory analysis.")
        st.markdown(answer_text)

        calc = agent_result.get("calculation")
        if calc:
            with st.expander("📈 View 10-Year Solar Payback & Economics Chart", expanded=True):
                df_payback = generate_payback_dataframe(
                    net_cost=calc["net_cost_to_consumer_inr"],
                    annual_savings=calc["estimated_annual_savings_inr"]
                )
                st.line_chart(df_payback, color=["#2e7d32", "#c62828"])
                st.caption(
                    f"🟢 Cumulative Savings crosses Net Outlay (₹{calc['net_cost_to_consumer_inr']:,}) "
                    f"at Year {calc['payback_period_years']} (Break-even Point)."
                )

        citations = agent_result.get("citations", [])
        if citations:
            with st.expander("📜 Official Source Citations", expanded=False):
                for c in citations:
                    st.markdown(f"- 🏛️ `{c}`")

        # Record assistant response in session_state
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer_text,
            "citations": citations,
            "calculation": calc
        })
