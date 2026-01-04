import streamlit as st
import pandas as pd
import os
from datetime import date
from database import get_df
from database import save_record
from database import update_record


st.set_page_config(
    page_title="Records",
    page_icon="📝",
    layout="wide"
)

if "show_editor" not in st.session_state:
    st.session_state["show_editor"] = False

st.title("📝 Records")
st.markdown("---")

df = get_df()

if not df.empty:
    df["Date"] = pd.to_datetime(df["Date"]).dt.date

# --- SIDEBAR & FILTERS ---
st.sidebar.header("Filters")

# Create a option list for categories
categories_list = ["General"] + list(df["Category"].unique())
# Create a selection box on the sidebar
selected_category = st.sidebar.selectbox("Category", categories_list)
if selected_category != "General":
    df = df[df["Category"] == selected_category]

if df.empty:
    st.warning("No data found in Google Sheets. Add the first one!")



# --- INPUT FORM ---
with st.form("form_register"):
    st.subheader("📝 New record")

    # Organizing them into columns to make them visual.
    col1, col2 = st.columns(2)

    with col1:
        register_date = st.date_input("Date", value=date.today(), format="DD/MM/YYYY")
        category = st.selectbox("Category", ["Studies", "Work", "Read", "Exercise", "English", "Other"])

    with col2:
        time = st.number_input("Time Spent (minutes)", min_value=0, step=5)
        notes = st.text_input("Detail of the activity")

    # Organizing them into columns to make them visual.
    c1, c2, c3, c4 = st.columns([1,1,1,6])

    with c1:
        # Send button
        submitted = st.form_submit_button("💾 Save Register")
    with c2:
        # Editor button
        editor_button = "❌ Close Editor" if st.session_state["show_editor"] else "✏️ Edit Register"
        editor_button_click = st.form_submit_button(editor_button)
        
        if editor_button_click:
            st.session_state["show_editor"] = not st.session_state["show_editor"]
            st.rerun() # Recarrega a página para atualizar o ícone do botão imediatamente
    with c3:
        if st.form_submit_button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()
    



# --- LOGIC OF SAVE ---
if submitted:
    save = save_record(register_date, category, notes, time)
    
    if save:
        st.success("✅ Record saved successfully in Database!")
        st.balloons() # Visual efect after save
    else:
        st.error("❌ Error saving record in Database.")


if st.session_state["show_editor"]:
    with st.container(border=True):

        st.subheader("✏️ Editor of records")
        st.caption("Edit directly in table below and press Enter.")

        df_edited = st.data_editor(
            df.sort_values(by='Date', ascending=False),
            use_container_width=True,
            num_rows="fixed",
            key="editor_table",
            column_config={
                "Date": st.column_config.DateColumn(
                    "Date",
                    format="DD/MM/YYYY",  # Força o formato visual brasileiro
                    step=1,
                ),
            }
        )

        changes = st.session_state["editor_table"]["edited_rows"]

        if len(changes) > 0:
            st.warning(f"You have changed {len(changes)} record(s). Do you want to save?")

        if st.button("💾 Save changes"):
            for index_pandas, alterations in changes.items():

                complete_row = df_edited.iloc[index_pandas]
                complete_row["Date"] = pd.to_datetime(complete_row["Date"])
                register_data = update_record(
                    row_index=index_pandas,
                    date=complete_row['Date'],
                    category=complete_row['Category'],
                    notes=complete_row['Notes'],
                    duration=complete_row['Duration']
                )
                if register_data:
                        st.toast(f"Row {index_pandas} updated successfully!", icon="✅")
            
            st.cache_data.clear()
            st.rerun()