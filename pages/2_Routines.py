import pandas as pd
import streamlit as st
from database import get_df
from database import save_book
import numpy as np
from datetime import date, datetime as dt
from database import save_planner
import pytz

# Set page config
st.set_page_config(
    page_title="Routine Planner",
    page_icon="📋",
    layout="wide"
)

# --- LOAD ALL DATA REQUIRED ---
df_books = get_df("books_library_d")
df_database = get_df()
df_weekly_planner = get_df("weekly_planner")

# --- CONFIGURATION : SESSION STATES ---
# Set default state to hide the dataframe editor
if "show_book_editor" not in st.session_state:
    st.session_state["show_book_editor"] = False


# --- CALCULATIONS ---

df_readings = df_database[df_database["Category"] == "Read"].copy()
total_pages_read = df_readings.groupby("Notes")["Pages"].sum()
df_books["Pages_Read"] = df_books["Name_book"].map(total_pages_read).fillna(0)
df_books["Total_pages"] = df_books["Total_pages"].astype(int)




last_read_date = df_database.groupby("Notes")["Date"].max()
df_books["Last_Activity"] = df_books["Name_book"].map(last_read_date).fillna("")
df_books["Status_Display"] = np.where(
    df_books["Pages_Read"] >= df_books["Total_pages"],
    "✅ Finished (" + df_books["Last_Activity"] + ")",
    "📖 Reading" 
)

df_books["Status"] = np.where(
    df_books["Pages_Read"] >= df_books["Total_pages"], 
    "Finished", 
    df_books["Status"]
)


# ---------------- SIDEBAR ----------------

# --- ACCESS CONTROL ---
st.sidebar.header("🔐 Admin Area")
input_pass = st.sidebar.text_input("Admin Password", type="password")
# Verify if the password is right, the same of secrets on streamlit folder
is_admin = False
if "admin_password" in st.secrets:
    if input_pass.strip() == st.secrets["admin_password"]:
        is_admin = True
        st.sidebar.success("Unlocked! 🔓")
    elif input_pass:
        st.sidebar.error("Wrong password 🔒")

# --- NAVIGATION ---
st.sidebar.header("Navigation")

if not df_books.empty:

    unique_status = list(df_books["Status"].unique())
    status_all = ["All"] + unique_status

    selected_status = st.sidebar.selectbox("Status", status_all)

    df_view = df_weekly_planner.copy()
    
    if selected_status != "All":
        df_view = df_view[df_view["Status"] == selected_status]

else:
    st.warning("Any book found at library.")

# --- DAYS OF WEEK ---

if not df_weekly_planner.empty:

    days_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    days_week_list = ["All"] + days_week

    br_timezone = pytz.timezone('America/Sao_Paulo')
    today_num = dt.now(br_timezone).weekday()
    
    default_index = today_num + 1

    selected_day_filter = st.sidebar.selectbox(
        "Days Week",
        days_week_list,
        index=default_index
    )

# ---------------- BOOK LIBRARY ----------------

with st.container(border=True):

    st.subheader("Include a new book to read")

    col1,col2,col3 = st.columns(3)

    with col1:
        book = st.text_input(
            label="Book title",
            placeholder="Title",
            on_change=None,
            key="new_book"
        )
    with col2:
        Author = st.text_input(
            label="Author",
            placeholder="Author",
            on_change=None,
            key="new_author"
        )
    with col3:
        Pages = st.number_input(
            label="Total Pages",
            placeholder="Total number of Pages",
            on_change=None,
            key="new_pages",
            min_value=1,
            step=1
        )

    c1, c2, c3, c4 = st.columns([1.4,1.5,1.5,6.5])

    with c1:
        if not is_admin:
            st.button("💾 Save new Book", disabled=True)
            st.caption("🔒 Login to edit records.")
        else:
            if st.button(label="💾 Save new Book"):
                if book and Author and Pages:
                    save_book(book, Author, Pages, "Reading")
                    st.success("✅ Book saved successfully!")
                    st.rerun()   

    with c2:
        btn_txt = "❌ Close Editor" if st.session_state["show_book_editor"] else "✏️ Edit Library"
        
        if not is_admin:
            st.button(btn_txt, disabled=True)
        else:
            if st.button(btn_txt):
                st.session_state["show_book_editor"] = not st.session_state["show_book_editor"]
                st.rerun() 

    with c3:
        if st.button("🔄 Refresh Data", disabled=not is_admin):
            st.rerun()


df_books = df_books.sort_values(by='Last_Activity', ascending=False)


if  st.session_state["show_book_editor"] == True:
    st.subheader("✏️ Editor of records")
    st.caption("Edit directly in table below and press Enter.")
    df_visual = df_books.sort_values(by='Name_book', ascending=True)
    df_visual = df_visual.reset_index(drop=True)
    df_visual["ID_Google"] = df_visual["ID_Google"].astype(int)
    st.data_editor(
        df_visual,
        width="stretch",
        num_rows="fixed",
        key="editor_table"
    )
    
elif st.session_state["show_book_editor"] == False:

    df_books["Percentage"] = ((df_books["Pages_Read"] / df_books["Total_pages"]) * 100).fillna(0)

    st.dataframe(
        df_books,
        use_container_width=True,
        hide_index=True,
        column_config={
            "ID_Google" : None,
            "Last_Activity" : None,
            "Status" : None,
            "Percentage": st.column_config.ProgressColumn(
                "Progress",
                help="Reading progress",
                format="%.0f%%",
                min_value=0,
                max_value=100,
                width="small"
            ),
        },    
    )

# ---------------- WEEKLY PLANNER ----------------

st.divider()
st.header("📅 Weekly Master Plan")

# 1. ÁREA DE VISUALIZAÇÃO (Aqui usamos o filtro da Sidebar com segurança)
if selected_day_filter != "All":
    st.info(f"Visualizing Focus: **{selected_day_filter}**")
    # Criamos uma cópia temporária só para mostrar
    df_focus = df_weekly_planner[df_weekly_planner["Day"] == selected_day_filter]
    st.dataframe(df_focus, use_container_width=True, hide_index=True)
    edit_button = st.button("Edit data", disabled=not is_admin)
else:
    if is_admin == True:
        if st.button("Edit data", disabled=not is_admin):

            # 2. ÁREA DE EDIÇÃO (Sempre mostra TUDO para garantir salvamento seguro)
            st.subheader("📝 Edit Full Plan")
            st.caption("⚠️ The editor below always shows the full week to prevent data loss.")

            edited_planner = st.data_editor(
                df_weekly_planner.reset_index(drop=True),
                column_config={
                    'ID_Google' : None,
                    "Day": st.column_config.SelectboxColumn(
                        "Day of week",
                        options=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                        required=True
                    ),
                    "Activity": st.column_config.SelectboxColumn(
                        "Activity",
                        options=[
                            "🐍 Python", 
                            "🗄️ SQL", 
                            "📊 Power BI", 
                            "🤖 AI", 
                            "🛠️ Personal Project", 
                            "⚙️ Automation", 
                            "🪁 Free to choose"
                        ],
                        required=True
                    ),
                    "Time": st.column_config.SelectboxColumn(
                        "Time",
                        options=[60, 45, 30, 15, 5],
                        required=True
                    )
                },
                num_rows="dynamic",
                hide_index=True
            )

            if st.button("💾 Save changes"):

                saved = save_planner(edited_planner)
                
                if saved:
                    st.success("Updated Planner!")