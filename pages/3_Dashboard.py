import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

st.title("📊 Performance Dashboard")

st.markdown("---")

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

if df.empty:
    st.info("No record found... Your excel file has been create and is ready to use")
    st.stop()


# --- SIDEBAR & FILTERS ---
st.sidebar.header("Filters")

# Create a lista of options for categories
categories_list = ["General"] + list(df["Category"].unique())
# Create a selection box on the sidebar
selected_category = st.sidebar.selectbox("Category", categories_list)
if selected_category != "General":
    df = df[df["Category"] == selected_category]


# --- METRICS & KPI's ---
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


data_date_graphic = df.groupby(["Date", "Category"])['Duration'].sum().unstack().fillna(0)
data_date_graphic.index = data_date_graphic.index.astype(str)

if df.shape[0] > 0:
    st.subheader("Daily evolution")
    st.line_chart(data_date_graphic, use_container_width=True)