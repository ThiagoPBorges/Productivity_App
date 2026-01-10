import streamlit as st
import pandas as pd
from database import get_df
from datetime import date
import calendar
import altair as alt

# Set page config

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

# Data processing
df["Date"] = pd.to_datetime(df["Date"])
df["Duration"] = pd.to_numeric(df["Duration"], errors='coerce').fillna(0).astype(int)
df["Duration"] = df["Duration"].fillna(0).astype(int)

today = date.today()
month_list = calendar.month_name[1:]

# ------------- SIDEBAR & FILTERS -------------

st.sidebar.header("Date filters")

selected_year = st.sidebar.number_input("Year", value=today.year)

default_index = today.month - 1

selected_month_name = st.sidebar.selectbox("Month", month_list, index=default_index)
selected_month_number = month_list.index(selected_month_name) + 1

df_monthly = df[(df["Date"].dt.month == selected_month_number) & (df["Date"].dt.year == selected_year)]
month_days = calendar.monthrange(selected_year, selected_month_number)[1]

st.sidebar.header("Topics filters")

# Create a option list for categories
categories_list = ["General"] + list(df["Category"].unique())

# Create a selection box on the sidebar
selected_category = st.sidebar.selectbox("Category", categories_list)
if selected_category != "General":
    df_monthly = df_monthly[df_monthly["Category"] == selected_category]


# ------------- METRICS & KPI's -------------
st.subheader(f"📅 Goals of {today.strftime('%B')}")

# Create 3 columns to bring Expected x Actual
cl1,cl2,cl3 = st.columns(3)

# Studies Goal
with cl1:
    with st.container(border=True):
        daily_study_goal = 60
        month_study_goal = daily_study_goal * month_days
        performed_study = df_monthly[df_monthly['Category'] == 'Studies']['Duration'].sum()
        study_progress = performed_study/month_study_goal
        st.metric(label="🧠 Studies (1h/day)", 
                  value=f"{round((performed_study/60),1)}h", 
                  delta=f"Goal: {round((month_study_goal/60),1)}h")
        st.progress(min(study_progress, 1.0))
        st.caption(f"{int(study_progress*100)}% completed")
# English Goal
with cl2:
    with st.container(border=True):
        daily_english_goal = 30
        month_english_goal = daily_english_goal * month_days
        performed_english = df_monthly[df_monthly['Category'] == 'English']['Duration'].sum()
        english_progress = performed_english/month_english_goal
        st.metric(label="🌍 English (30min/day)", 
                  value=f"{round((performed_english/60),1)}h", 
                  delta=f"Goal: {round((month_english_goal/60),1)}h")
        st.progress(min(english_progress, 1.0))
        st.caption(f"{int(english_progress*100)}% completed")
#Reading Goal
with cl3:
    with st.container(border=True):
        daily_reading_goal = 30
        month_reading_goal = daily_reading_goal * month_days
        performed_reading = df_monthly[df_monthly['Category'] == 'Read']['Duration'].sum()
        reading_progress = performed_reading/month_reading_goal
        st.metric(label="📖 Reading (30min/day)", 
                  value=f"{round((performed_reading/60),1)}h", 
                  delta=f"Goal: {round((month_reading_goal/60),1)}h")
        st.progress(min(reading_progress, 1.0))
        st.caption(f"{int(reading_progress*100)}% completed")



# Pacing Logic
days_passed = today.day
expected = (daily_study_goal + daily_english_goal + daily_reading_goal) * days_passed 
actual = df_monthly['Duration'].sum()

delta_pacing = actual - expected

if delta_pacing >= 0:
    st.success(f"🚀 You are **{int(delta_pacing/60)}h ahead** of your study schedule for today!")
else:
    st.warning(f"⚠️ You are **{abs(int(delta_pacing/60))}h behind** schedule. Time to focus!")



st.markdown("---")



c1, c2 = st.columns([2, 1])

# Groupy by date
with c1:
    st.subheader(f"📈 Daily Evolution - ({today.strftime('%B/%Y')})")
    daily_evolution = df_monthly.groupby(["Date", "Category"])["Duration"].sum().unstack(fill_value=0)

    start_date = f"{selected_year}-{selected_month_number:02d}-01"
    end_date = f"{selected_year}-{selected_month_number:02d}-{month_days}"
    all_days = pd.date_range(start=start_date, end=end_date, freq='D')

    daily_evolution = daily_evolution.reindex(all_days, fill_value=0)

    daily_evolution.index = daily_evolution.index.strftime("%d")

    st.bar_chart(daily_evolution)
# Groupy by category
with c2:
    st.subheader(f"📊 Time Distribution - ({today.strftime('%B/%Y')})")
    category_distribution = df_monthly.groupby("Category")["Duration"].sum().sort_values(ascending=False)
    st.bar_chart(category_distribution, horizontal=True,color="#0c3ac5")

st.markdown("---")

days_order = [
    "Monday", "Tuesday", "Wednesday", "Thursday", 
    "Friday", "Saturday", "Sunday"
]

df_monthly['day_of_week'] = pd.Categorical(
    df_monthly['Date'].dt.day_name(), 
    categories=days_order, 
    ordered=True
)

df_monthly['Hours'] = round((df_monthly['Duration'] / 60),2)
weekday_averages = df_monthly.groupby('day_of_week', observed=False)['Hours'].sum()
chart_data = weekday_averages.reset_index()
chart_data.columns = ['Day', 'Hours']

st.subheader("📅 Weekly Performance Pattern")
st.caption("Which is your most productive day?")

chart = alt.Chart(chart_data).mark_bar(color="#ffaa00").encode(
    x=alt.X('Day', sort=days_order, title='Day of Week'),
    y=alt.Y('Hours', title='Total Duration (hours)'),
    tooltip=['Day', 'Hours']
)

st.altair_chart(chart, use_container_width=True)

