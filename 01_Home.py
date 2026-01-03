import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="FocusData Home",
    page_icon="🏠",
    layout="centered"
)

st.title("🏠 Welcome to the Home Page of FocusData")
st.markdown("---")

st.write("""
### Your hub of personal productivity.
Use the sidebar to navigate:

- **📝 Register:** To record your activities.
- **📊 Dashboard:** To analyze your progress.
""")

# Mostra uma prévia rápida (opcional)
st.info("Database conected and ready to use.")