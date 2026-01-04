import streamlit as st
import pandas as pd
import os

# streamlit run 1_Home.py

st.set_page_config(
    page_title="FocusData Home",
    page_icon="🏠",
    layout="centered"
)

st.title("🏠 FocusData: Productivity Hub")
st.markdown("---")

# --- Validation of database ---
file_path = "productivity_database.csv"

if os.path.exists(file_path):
    try:
        df = pd.read_csv(file_path)
        st.toast("Database loaded successfully!", icon="✅")
        database_ready = True
    except Exception as e:
        st.error(f"Error loading database: {e}")
        database_ready = False
else:
    st.warning("Database file not found. Please register your first activity.")
    database_ready = False

st.write("### Choose your path:")

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("📝 Record_Activities")
        st.write("Record your daily activities.")
        st.caption("Inputs: English, Gym, Studies...")

with col2:
    with st.container(border=True):
        st.subheader("📊 Dashboard")
        st.write("Analyze your progress.")
        st.caption("Visuals: Charts & Metrics.")