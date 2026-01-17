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
df_database = get_df()

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

    st.button(
        label="Save new Book",
        on_click=None,
        key="save_new_book",
        help="Include a new book to read in library."
    )



st.write("📚 My books library")

total_pages_read = df_database.groupby("Notes")["Pages"].sum()
df_books["Pages_Read"] = df_books["Name_book"].map(total_pages_read).fillna(0)

st.dataframe(
    df_books,
    use_container_width=True,
    hide_index=True,
    column_config={"ID_Google": None}
)

st.header("Database")
st.dataframe(
    df_database,
    use_container_width=True,
    hide_index=True
)