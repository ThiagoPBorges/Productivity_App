import pandas as pd
import streamlit as st
from database import get_df

st.set_page_config(
    page_title="Routine Planner",
    page_icon="📋",
    layout="wide"

)

st.write("📚 My books library")
df_books = get_df("books_library_d")
st.dataframe(df_books)