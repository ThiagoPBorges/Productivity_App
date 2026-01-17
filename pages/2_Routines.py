import pandas as pd
import streamlit as st
from database import get_df
from database import save_book
import numpy as np


# Set page config
st.set_page_config(
    page_title="Routine Planner",
    page_icon="📋",
    layout="wide"
)

# --- LOAD ALL DATA REQUIRED ---
df_books = get_df("books_library_d")
df_database = get_df()

# --- CONFIGURATION : SESSION STATES ---
# Set default state to hide the dataframe editor
if "show_book_editor" not in st.session_state:
    st.session_state["show_book_editor"] = False


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

    if selected_status != "All":
        df_books = df_books[df_books["Status"] == selected_status]

else:
    st.warning("Any book found at library.")


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
        if not is_admin:
            st.button("✏️ Edit book library", disabled=True)
        else:
            st.session_state["show_book_editor"] = True
            st.button("✏️ Edit book library")  

    with c3:
        if not is_admin:
            st.button("🔄 Refresh Data", disabled=True)
        else:
            st.button("🔄 Refresh Data")


df_readings = df_database[df_database["Category"] == "Read"].copy()
total_pages_read = df_readings.groupby("Notes")["Pages"].sum()
df_books["Pages_Read"] = df_books["Name_book"].map(total_pages_read).fillna(0)
df_books["Total_pages"] = df_books["Total_pages"].astype(int)


df_books["Status"] = np.where(
    df_books["Pages_Read"] >= df_books["Total_pages"], 
    "Finished", 
    df_books["Status"]
)


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
    st.dataframe(
        df_books,
        use_container_width=True,
        hide_index=True,
        column_config={"ID_Google": None}
    )