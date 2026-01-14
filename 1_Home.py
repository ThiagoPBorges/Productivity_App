import streamlit as st
from datetime import datetime
import pytz

# Code to run the app
# streamlit run 1_Home.py

# Set page config
st.set_page_config(
    page_title="FocusData Home",
    page_icon="🏠",
    layout="wide"
)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("**Developer:** Thiago Prochnow Borges")
    col1, col2 = st.columns(2)
    with col1:
        st.link_button("💼 Linkedin", "https://www.linkedin.com/in/thiagopborges/")
    with col2:
        st.link_button("💻 Github", "https://github.com/thiagopborges")
    st.write("")
    st.markdown("**Disclaimer:**")
    st.info("This app connects to Google Sheets to track my productivity metrics in real-time.")
    st.write("")
    st.markdown("**Version:** 1.0.0")

# --- MAIN CONTENT ---
st.title("🎯 FocusData: Productivity Hub")

br_timezone = pytz.timezone('America/Sao_Paulo')
now_in_brazil = datetime.now(br_timezone)
today = datetime.now(br_timezone).strftime("%A, %d %B %Y")
st.markdown(f"*{today}*")

st.write("")

# Greetings logic
current_hour = now_in_brazil.hour
if 5 <= current_hour < 12:
    greeting_msg = "🌅 Good Morning! Ready to produce?"
elif 12 <= current_hour < 18:
    greeting_msg = "☀️ Good Afternoon! Let's stay focused?"
else:
    greeting_msg = "🌙 Good Evening! Let's finish the day focused!"
st.success(greeting_msg)

st.write("")

with st.container(border=True):
    st.markdown("""
    ### Welcome to my Personal Growth Tracker!
    This application was built to manage time, track habits, and analyze performance across different areas of life.
    """)

    st.write("")

    st.markdown("###### 🛠️ Tech Stack used in this project:")
    st.markdown("""
    ![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
    ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=Streamlit&logoColor=white)
    ![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white)
    ![Google Sheets](https://img.shields.io/badge/Google_Sheets-34A853?style=flat&logo=google-sheets&logoColor=white)
    """)

st.markdown("---")

# --- NAVIGATION CARDS ---

# Subtitle of How to Proceed in the app
st.subheader("Choose your action:")

# Create two columns of page
col1, col2 = st.columns(2)

# Container Register
with col1:
    with st.container(border=True):
        st.subheader("📝 Record_Activities")
        st.write("Record your daily activities.")
        st.caption("Inputs Routines: English, Reading, Studies, Workout...")
        st.page_link(
            "pages/2_Record_Activities.py", 
            label="Go to Register", 
            icon="➡️",
            use_container_width=True 
        )
# Container Dashboard
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

# --- FOOTER ---
for i in range(3):
    st.write("")


st.caption("© 2026 FocusData Project. Developed for practical work and personal purposes.")