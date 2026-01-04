import streamlit as st
import pandas as pd
import os
import pygsheets

# streamlit run 1_Home.py

st.set_page_config(
    page_title="FocusData Home",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 FocusData: Productivity Hub")
st.markdown("---")

st.subheader("Choose your action:")

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("📝 Record_Activities")
        st.write("Record your daily activities.")
        st.caption("Inputs Routines: English, Reading, Studies, Gym...")
        st.page_link(
            "pages/2_Record_Activities.py", 
            label="Go to Register", 
            icon="➡️",
            use_container_width=True 
        )

with col2:
    with st.container(border=True):
        st.subheader("📊 Dashboard")
        st.write("Analyze your progress.")
        st.caption("Visuals: Charts & Metrics.")
        st.page_link(
            "pages/3_Dashboard.py", 
            label="Go to Dashboard", 
            icon="➡️",
            use_container_width=True
        )