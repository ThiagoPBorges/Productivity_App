import streamlit as st
import pandas as pd
import os
from datetime import date
from database import salvar_registro

st.set_page_config(
    page_title="Register",
    page_icon="📝",
    layout="centered"
)

st.title("📝 Register")
st.markdown("---")


# --- INPUT FORM ---
with st.form("form_register"):
    st.subheader("📝 New registration")

    # Organizing them into columns to make them visual.
    col1, col2 = st.columns(2)

    with col1:
        register_date = st.date_input("Date", value=date.today(), format="DD/MM/YYYY")
        category = st.selectbox("Category", ["Studies", "Work", "Read", "Exercise", "English", "Other"])

    with col2:
        time = st.number_input("Time Spent (minutes)", min_value=0, step=5)
        activity = st.text_input("Detail of the activity")
    notes = st.text_input("Observation / Insights", placeholder= "What you learn today?")

    # Send button
    submitted = st.form_submit_button("💾 Save Register")

# --- LOGIC OF SAVE ---
if submitted:
    # Chama a função que criamos no database.py
    sucesso = salvar_registro(register_date, category, activity, time, notes)
    
    if sucesso:
        st.success("✅ Registro salvo no Google Sheets com sucesso!")
        st.balloons() # Um efeito visual de comemoração
    else:
        st.error("❌ Erro ao salvar. Verifique sua conexão.")