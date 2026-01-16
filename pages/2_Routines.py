import pandas as pd
import streamlit as st
from database import get_df

st.set_page_config(
    page_title="Routine Planner",
    page_icon="📋",
    layout="wide"

)
# Load data
df_books = get_df("books_library_d")

# --- SIDEBAR ---

st.sidebar.header("Navigation")

if not df_books.empty:

    unique_status = list(df_books["Status"].unique())
    status_all = ["All"] + unique_status

    selected_status = st.sidebar.selectbox("Status", status_all)

    if selected_status != "All":
        df_books = df_books[df_books["Status"] == selected_status]

else:
    st.warning("Any book found at library.")


st.write("📚 My books library")

st.dataframe(
    df_books,
    use_container_width=True,
    hide_index=True,
    column_config={"ID_Google": None}
)