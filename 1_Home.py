import streamlit as st

# Code to run the app
# streamlit run 1_Home.py

# Set page config
st.set_page_config(
    page_title="FocusData Home",
    page_icon="🏠",
    layout="wide"
)

# Main title of page
st.title("🏠 FocusData: Productivity Hub")
st.markdown("---")

# Subtitle of How to Proceed in the app
st.subheader("Choose your action:")

# Create two columns of page
col1, col2 = st.columns(2)

# Created container to split register menu and link
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
# Created container to split dashboard menu and link
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