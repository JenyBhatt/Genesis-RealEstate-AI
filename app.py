import streamlit as st
import requests
import pandas as pd
import base64
import io
from PIL import Image
import os

# 1. SETUP & PATHS
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Try to load data safely
try:
    df_loc = pd.read_csv("metadata.csv", usecols=['location'])
    all_locations = sorted(df_loc['location'].dropna().unique().tolist())
except:
    all_locations = ["Hebbal", "Whitefield"] # Fallback

# 2. PAGE CONFIG
st.set_page_config(page_title="Genesis Real Estate Dashboard", layout="wide", initial_sidebar_state="expanded")
API_URL = "http://127.0.0.1:8000"

# 3. CUSTOM CSS (For the "Calculator Card" look)
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #0e1117; border-radius: 4px; gap: 1px; color: white; font-weight: 600; padding: 10px;}
    .stTabs [aria-selected="true"] { background-color: #007bff; }
    
    /* Style the Right Panel */
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
        background-color: #f9f9f9;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #ddd;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("Genesis : Real Estate Investment Analyser")
st.caption("Hybrid System: AI Agent + Deterministic Data Engine")
st.caption("@JenyBhatt")

# ==================================================
# LEFT SIDEBAR (FILTERS ONLY)
# ==================================================
with st.sidebar:
    st.header("🎛️ Global Filters")
    selected_locations = st.multiselect("Select Locations", all_locations, default=all_locations[:1])
    decision_filter = st.selectbox("Investment Strategy", ["All", "BUY", "RENT"])
    price_range = st.slider("Price Range (₹ Cr)", 0.1, 10.0, (0.5, 5.0))
    st.divider()
    st.info(f"System Status: ● Online\n{len(selected_locations)} Areas Active")

# ==================================================
# MAIN LAYOUT: SPLIT SCREEN (Chat vs Tools)
# ==================================================
# Create 2 columns: Main App (70%) | Tools Panel (30%)
col_app, col_tools = st.columns([3, 1], gap="medium")

# --- RIGHT COLUMN: THE CALCULATOR WIDGET ---
with col_tools:
    st.markdown("### 🧮 Mortgage Calculator")
    with st.container(border=True): # Makes it look like a card
        home_price = st.number_input("Property Price (₹)", min_value=1000000, value=6500000, step=500000)
        down_payment_pct = st.slider("Down Payment (%)", 10, 80, 20)
        interest_rate = st.slider("Interest Rate (%)", 6.0, 12.0, 8.5)
        tenure_years = st.slider("Tenure (Years)", 5, 30, 20)
        
        # Calculation
        loan_amount = home_price * (1 - down_payment_pct/100)
        monthly_rate = interest_rate / 12 / 100
        months = tenure_years * 12
        if loan_amount > 0:
            emi = (loan_amount * monthly_rate * ((1 + monthly_rate) ** months)) / (((1 + monthly_rate) ** months) - 1)
        else:
            emi = 0
            
        st.divider()
        st.metric(label="Monthly EMI", value=f"₹{int(emi):,}")
        st.caption(f"Total Loan: ₹{int(loan_amount):,}")

# --- LEFT COLUMN: THE MAIN APP (TABS) ---
with col_app:
    tab_chat, tab_data = st.tabs(["🤖 AI Advisor", "🔍 Market Data"])

    # TAB 1: CHATBOT
    with tab_chat:
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if "chart" in msg:
                    st.image(msg["chart"])

        if prompt := st.chat_input("Ex: 'Compare ROI for Hebbal vs Whitefield'"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.spinner("Analyzing..."):
                try:
                    response = requests.post(f"{API_URL}/chat", json={"query": prompt})
                    res = response.json()
                    
                    with st.chat_message("assistant"):
                        st.markdown(res['answer'])
                        if res['chart_base64']:
                            img_bytes = base64.b64decode(res['chart_base64'])
                            img = Image.open(io.BytesIO(img_bytes))
                            st.image(img, caption="Wealth Projection")
                            
                            # Call to Action Button
                            st.divider()
                            c1, c2 = st.columns([1,2])
                            with c1:
                                if st.button("📞 Contact Agent", key=f"btn_{len(st.session_state.messages)}"):
                                    st.toast("Request Sent!", icon="✅")
                            
                            st.session_state.messages.append({"role": "assistant", "content": res['answer'], "chart": img})
                        else:
                            st.session_state.messages.append({"role": "assistant", "content": res['answer']})
                except Exception as e:
                    st.error(f"Connection Error: {e}")

    # TAB 2: DATA EXPLORER
    with tab_data:
        st.subheader("📊 Live Market Scanner")
        if st.button("Refresh Data Table", type="primary", use_container_width=True):
            try:
                min_p = price_range[0] * 10000000
                max_p = price_range[1] * 10000000
                payload = {
                    "locations": selected_locations,
                    "min_price": min_p,
                    "max_price": max_p,
                    "decision_type": decision_filter
                }
                response = requests.post(f"{API_URL}/filter", json=payload)
                data = response.json()
                
                if data:
                    df_res = pd.DataFrame(data)
                    st.dataframe(
                        df_res[['title', 'location', 'price_raw', 'monthly_emi', 'decision']],
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.warning("No properties found.")
            except Exception as e:
                st.error(f"Error: {e}")