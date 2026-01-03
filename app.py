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
st.write("Record and analyze your Studies, Training and Personal Pojects.")


# --- Functions (Backend) ---
def load_data ():
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

df = load_data()


st.markdown("---")
st.subheader("📊 History of Records")


# --- SIDEBAR & FILTERS ---
st.sidebar.header("Filters")

# Create a lista of options for categories
categories_list = ["General"] + list(df["Category"].unique())
# Create a selection box on the sidebar
selected_category = st.sidebar.selectbox("Category", categories_list)
if selected_category != "General":
    df = df[df["Category"] == selected_category]


# METRICS & KPI's

total_hours = df['Duration'].sum() / 60
total_registers = df.shape[0]

c1, c2, c3 = st.columns(3)

with c1:
    st.metric("Total registers", value=total_registers)
with c2:
    st.metric("Total Hours", value=f"{total_hours:.1f} h")
with c3:
    st.metric("Mean per register", value=f"{total_hours/total_registers:.1f} h")

data_groups_graphic = df.groupby("Category")['Duration'].sum()

if df.shape[0] > 0:
    st.subheader("Time per Category")
    st.bar_chart(data_groups_graphic, use_container_width=True)




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
    # Create a new row of data
    new_row = pd.DataFrame({
        "Date": [register_date],
        "Category": [category],
        "Activity": [activity],
        "Duration": [time],
        "Notes": [notes]
    })
    
    # Add in exist dataframe
    df = pd.concat([df, new_row], ignore_index=True)

    try:
        df.to_csv("productivity_database.csv", index=False)
        st.success("Register saved successfully!")
        # Rerun forces the page to reload to display the updated table
        st.rerun()
    except PermissionError:
            st.error("⚠️ ERROR: Close the Excel file and try again!")



# Display the dataframe on the screen (If it's empty, will show only the headers)
st.dataframe(df,use_container_width=True)
if df.empty:
    st.info("No record found. Your excel file has been create and is ready to use")