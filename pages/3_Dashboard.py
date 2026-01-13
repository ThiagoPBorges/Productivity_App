import streamlit as st
import pandas as pd
from database import get_df
from datetime import date,timedelta
import calendar
import altair as alt

# Set page config

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
today = date.today()
st.title(f"📊 Performance Dashboard")

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
st.subheader("📅 Metrics & KPI's")

def calculate_streak(df, category):

    if df.empty:
        return 0

    # --- Day Streak metrics ---

    df_category = df[df["Category"] == category].copy()

    # Convert to datetime, without time
    df_category["Date"] = pd.to_datetime(df_category["Date"]).dt.date
    # Set function convert column to unique list
    unique_days = set(df_category["Date"])

    today = date.today()
    current_streak = 0
    check_date = today

    # Wait a range of one day to start analyze streak
    if not check_date in unique_days:
        check_date = check_date - timedelta(days=1)
    else:
        while check_date in unique_days:
            current_streak += 1
            check_date = check_date - timedelta(days=1)

        return current_streak

# Create 3 columns to bring Expected x Actual
cl1,cl2,cl3,cl4 = st.columns(4)

# Studies Goal
with cl1:
    with st.container(border=True):

        st.subheader("📚 Studies")

        streak = calculate_streak(df_monthly, 'Studies')
        daily_study_goal = 90
        month_study_goal = daily_study_goal * month_days
        performed_study = df_monthly[df_monthly['Category'] == 'Studies']['Duration'].sum()

        kpi1, kpi2 = st.columns(2)

        with kpi1:
            st.metric(
                label="🔥 Streak",
                value=f"{streak} days"
            )
            
        with kpi2:
            hours_done = round(performed_study/60, 1)
            hours_goal = round(month_study_goal/60, 1)
            delta_val = round(hours_done - hours_goal, 1)
            
            st.metric(
                label="⏱️ Performance", 
                value=f"{hours_done}h",
                help=f"Goal: {hours_goal}h per month"
            )
            
        study_progress = performed_study/month_study_goal
        st.progress(min(study_progress, 1.0))
        st.caption(f"{int(study_progress*100)}% completed")

# English Goal
with cl2:
    with st.container(border=True):
        
        st.subheader("🌍 English")

        streak = calculate_streak(df_monthly, 'English') 
        daily_english_goal = 30
        month_english_goal = daily_english_goal * month_days
        performed_english = df_monthly[df_monthly['Category'] == 'English']['Duration'].sum()

        kpi1, kpi2 = st.columns(2)

        with kpi1:
            st.metric(
                label="🔥 Streak",
                value=f"{streak} days"
            )
            
        with kpi2:
            hours_done = round(performed_english/60, 1)
            hours_goal = round(month_english_goal/60, 1)
            delta_val = round(hours_done - hours_goal, 1)
            
            st.metric(
                label="⏱️ Performance", 
                value=f"{hours_done}h",
                help=f"Goal: {hours_goal}h per month"
            )

        english_progress = performed_english/month_english_goal
        st.progress(min(english_progress, 1.0))
        st.caption(f"{int(english_progress*100)}% completed")

# Reading Goal
with cl3:
    with st.container(border=True):
        
        st.subheader("📖 Reading")

        streak = calculate_streak(df_monthly, 'Read') 

        daily_reading_goal = 30
        month_reading_goal = daily_reading_goal * month_days
        performed_reading = df_monthly[df_monthly['Category'] == 'Read']['Duration'].sum()

        kpi1, kpi2 = st.columns(2)

        with kpi1:
            st.metric(
                label="🔥 Streak",
                value=f"{streak} days"
            )
            
        with kpi2:
            hours_done = round(performed_reading/60, 1)
            hours_goal = round(month_reading_goal/60, 1)
            delta_val = round(hours_done - hours_goal, 1)
            
            st.metric(
                label="⏱️ Performance", 
                value=f"{hours_done}h",
                help=f"Goal: {hours_goal}h per month"
            )

        reading_progress = performed_reading / month_reading_goal
        st.progress(min(reading_progress, 1.0))
        st.caption(f"{int(reading_progress*100)}% completed")

# Personal projects goal
with cl4:
    with st.container(border=True):
        
        st.subheader("📖 Personal projects")

        streak = calculate_streak(df_monthly, 'Personal projects') 

        daily_projects_goal = 30
        month_projects_goal = daily_projects_goal * month_days
        performed_projects = df_monthly[df_monthly['Category'] == 'Personal projects']['Duration'].sum()

        kpi1, kpi2 = st.columns(2)

        with kpi1:
            st.metric(
                label="🔥 Streak",
                value=f"{streak} days"
            )
            
        with kpi2:
            hours_done = round(performed_projects/60, 1)
            hours_goal = round(month_projects_goal/60, 1)
            delta_val = round(hours_done - hours_goal, 1)
            
            st.metric(
                label="⏱️ Performance", 
                value=f"{hours_done}h",
                help=f"Goal: {hours_goal}h per month"
            )

        projects_progress = performed_projects / month_projects_goal
        st.progress(min(projects_progress, 1.0))
        st.caption(f"{int(projects_progress*100)}% completed")

st.write("")

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
    st.subheader(f"📈 Daily Evolution")

    df_monthly["hours"] = round((df_monthly["Duration"] / 60), 1)

    daily_evolution = df_monthly.groupby(["Date", "Category"])["hours"].sum().unstack(fill_value=0)

    start_date = f"{selected_year}-{selected_month_number:02d}-01"
    end_date = f"{selected_year}-{selected_month_number:02d}-{month_days}"
    all_days = pd.date_range(start=start_date, end=end_date, freq='D')

    daily_evolution = daily_evolution.reindex(all_days, fill_value=0)

    daily_evolution.index = daily_evolution.index.strftime("%d")

    st.bar_chart(daily_evolution, y_label="Hours", x_label="Days")

# Groupy by category
with c2:
    st.subheader(f"📊 Time Distribution")
    category_distribution = df_monthly.groupby("Category")["hours"].sum().sort_values(ascending=False)
    st.bar_chart(category_distribution, horizontal=True,color="#0c3ac5",
                 x_label="Hours", y_label="Category")

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

weekday_averages = df_monthly.groupby('day_of_week', observed=False)['hours'].sum()
chart_data = weekday_averages.reset_index()
chart_data.columns = ['Day', 'hours']

st.subheader("📅 Weekly Performance Pattern")
st.caption("Which is your most productive day?")

chart = alt.Chart(chart_data).mark_bar(color="#ffaa00").encode(
    x=alt.X('Day', sort=days_order, title='Day of Week'),
    y=alt.Y('hours', title='Total Duration (hours)'),
    tooltip=['Day', 'hours']
)

st.altair_chart(chart, use_container_width=True)




