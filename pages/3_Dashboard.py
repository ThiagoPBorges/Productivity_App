import streamlit as st
import pandas as pd
import os
from database import get_df

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

st.title("📊 Performance Dashboard")

st.markdown("---")

df= get_df()

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


cl1,cl2,cl3 = st.columns(3)


with cl1:
    with st.container(border=True):
        goal_study = 60
        performed_study = df[df['Category'] == 'Studies']['Duration'].sum()
        progress = performed_study/goal_study
        st.write(f"Studies Goal: {int(progress*100)}%")
        st.progress(min(progress, 1.0))
with cl2:
    with st.container(border=True):
        goal_english = 60
        performed_english = df[df['Category'] == 'English']['Duration'].sum()
        progress = performed_english/goal_english
        st.write(f"English Goal: {int(progress*100)}%")
        st.progress(min(progress, 1.0))
with cl3:
    with st.container(border=True):
        goal_read = 60
        performed_read = df[df['Category'] == 'Read']['Duration'].sum()
        progress = performed_read/goal_read
        st.write(f"Reading Goal: {int(progress*100)}%")
        st.progress(min(progress, 1.0))


st.markdown("---")


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