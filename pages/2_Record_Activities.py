import streamlit as st
import pandas as pd
import os
from datetime import date
from database import save_record
from database import load_data

df = load_data()

if df.empty:
    st.warning("No data found in Google Sheets. Add the first one!")
    st.stop()


st.set_page_config(
    page_title="Records",
    page_icon="📝",
    layout="centered"
)

st.title("📝 Records")
st.markdown("---")


# --- INPUT FORM ---
with st.form("form_register"):
    st.subheader("📝 New record")

    # Organizing them into columns to make them visual.
    col1, col2 = st.columns(2)

    with col1:
        register_date = st.date_input("Date", value=date.today(), format="DD/MM/YYYY")
        category = st.selectbox("Category", ["Studies", "Work", "Read", "Exercise", "English", "Other"])

    with col2:
        time = st.number_input("Time Spent (minutes)", min_value=0, step=5)
        notes = st.text_input("Detail of the activity")

    # Send button
    submitted = st.form_submit_button("💾 Save Register")

# --- LOGIC OF SAVE ---
if submitted:
    save = save_record(register_date, category, notes, time)
    
    if save:
        st.success("✅ Record saved successfully in Database!")
        st.balloons() # Visual efect after save
    else:
        st.error("❌ Error saving record in Database.")

st.dataframe(df)