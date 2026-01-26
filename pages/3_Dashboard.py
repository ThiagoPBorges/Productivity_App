import streamlit as st
import pandas as pd
from database import get_df
from datetime import date,timedelta, datetime
import calendar
import altair as alt
import pytz

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

    br_timezone = pytz.timezone('America/Sao_Paulo')
    today = datetime.now(br_timezone).date()
    current_streak = 0
    check_date = today

    # Wait a range of one day to start analyze streak
    if not check_date in unique_days:
        check_date = check_date - timedelta(days=1)

    while check_date in unique_days:
        current_streak += 1
        check_date = check_date - timedelta(days=1)

    return current_streak

def create_kpi_card(icon, title, category, daily_goal, column):
    with column:
        with st.container(border=True):
            st.subheader(icon + " " + title)

            streak = calculate_streak(df_monthly, category)
            month_goal = daily_goal * month_days
            performed = df_monthly[df_monthly['Category'] == category]['Duration'].sum()

            kpi1, kpi2 = st.columns(2)

            with kpi1:
                st.metric(
                    label="🔥 Streak",
                    value = f"{streak} day" if streak <= 1 else f"{streak} days"
                )
                
            with kpi2:
                hours_done = round(performed/60, 1)
                hours_goal = round(month_goal/60, 1)
                delta_val = round(hours_done - hours_goal, 1)
                
                st.metric(
                    label="⏱️ Output", 
                    value=f"{hours_done}h",
                    help=f"Goal: {hours_goal}h per month"
                )
            
            progress = performed/month_goal
            st.progress(min(progress, 1.0))
            st.caption(f"{int(progress*100)}% completed")

# Create 3 columns to bring Expected x Actual
cl1,cl2,cl3,cl4,cl5 = st.columns(5)

# Create cards = icon, title, category, daily_goal, column
create_kpi_card("📚","Studies", "Studies", 60, cl1)
create_kpi_card("🌍","English", "English", 30, cl2)
create_kpi_card("📖","Reading", "Read", 30, cl3)
create_kpi_card("🛠️","Projects", "Personal projects", 30, cl4)
create_kpi_card("🏋️‍♂️","Workout", "Workout", 60, cl5)

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
    category_distribution = df_monthly.groupby("Category")["hours"].mean().round(2).sort_values(ascending=False)
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

weekday_averages = df_monthly.groupby('day_of_week', observed=False)['hours'].mean().round(2)
chart_data = weekday_averages.reset_index()
chart_data.columns = ['Day', 'hours']

st.subheader("📅 Weekly Performance Pattern")
st.caption("Which is your most productive day?")

chart = alt.Chart(chart_data).mark_bar(color="#0c3ac5").encode(
    x=alt.X('Day', sort=days_order, title='Day of Week'),
    y=alt.Y('hours', title='Total Duration (hours)'),
    tooltip=['Day', 'hours']
)

st.altair_chart(chart, use_container_width=True)




