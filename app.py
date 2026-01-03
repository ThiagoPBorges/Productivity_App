import streamlit as st
import pandas as pd
import os
from datetime import date

# streamlit run app.py

# Page Setup
st.set_page_config(
    page_title="Productivity App",
    page_icon="🎯",
    layout="wide"
)

# Main Header
st.title("🎯 FocusData: Productivity Dashboard")
st.write("Record and analyze your studies, Training and projects.")

# Sidebar (Left Menu)
st.sidebar.header("Configuration")
st.sidebar.info("Version 1.0 - Dev: Thiago Prochnow Borges")




# --- Functions (Backend) ---
def carregar_dados ():
    filename = 'productivity_database.csv'

    # If not exist create
    if not os.path.exists(filename):
        df = pd.DataFrame(columns=["Date", "Category", "Activity", "Duration", "Notes"])
        # Save the physical file
        df.to_csv(filename, index=False)
        return df
    else:
        # If exist try read
        try:
            df = pd.read_csv(filename)
            # Ensures that the Date column is interpreted as a date.
            df['Date'] = pd.to_datetime(df['Date']).dt.date
            return df
        except Exception as e:
            st.error(f"Error reading Excel file: {e}")
            return pd.DataFrame() # Returns empty to not crashing the app

df = carregar_dados()


st.markdown("---")

st.subheader("📊 History of Records")
# Display the dataframe on the screen (If it's empty, will show only the headers)
st.dataframe(df,use_container_width=True)
if df.empty:
    st.info("No record found. Your excel file has been create and is ready to use")