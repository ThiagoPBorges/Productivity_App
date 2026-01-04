import streamlit as st
import pandas as pd
import os
from database import get_df

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

st.title("📊 Performance Dashboard")

st.markdown("---")

# --- Functions (Backend) ---
with st.spinner("Loading data from cloud..."):
    df = get_df()

if df.empty:
    st.warning("No data found in Google Sheets. Add the first one!")
    st.stop()


df["Date"] = pd.to_datetime(df["Date"])
df["Duration"] = pd.to_numeric(df["Duration"], errors='coerce')
df["Duration"] = df["Duration"].fillna(0).astype(int)


# --- SIDEBAR & FILTERS ---
st.sidebar.header("Filters")

# Create a option list for categories
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
    if total_registers > 0:
        media = total_hours / total_registers
    else:
        media = 0
    st.metric("Mean per register", value=f"{media:.1f} h")

data_groups_graphic = df.groupby("Category")['Duration'].sum()
if df.shape[0] > 0:
    st.subheader("Time per Category")
    st.bar_chart(data_groups_graphic, use_container_width=True)


data_date_graphic = df.groupby(["Date", "Category"])['Duration'].sum().unstack().fillna(0)
data_date_graphic.index = data_date_graphic.index.astype(str)

if df.shape[0] > 0:
    st.subheader("Daily evolution")
    st.line_chart(data_date_graphic, use_container_width=True)