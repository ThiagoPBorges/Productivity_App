import streamlit as st
import pandas as pd
import os
from datetime import date
from database import get_df
from database import save_record
from database import update_record
import time


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
    df["Date"] = pd.to_datetime(df["Date"], errors='coerce').dt.date
    df["Notes"] = df["Notes"].fillna("").astype(str)

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
        duration = st.number_input("Time Spent (minutes)", min_value=0, step=5)
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
            st.rerun()
    with c3:
        if st.form_submit_button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()
    



# --- LOGIC OF SAVE ---
if submitted:
    save = save_record(register_date, category, notes, duration)
    
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
                    width="stretch",
                    num_rows="fixed",
                    key="editor_table",
                    column_config={
                        # Configuração da Data (Já existia)
                        "Date": st.column_config.DateColumn(
                            "Date",
                            format="DD/MM/YYYY",
                            step=1,
                        ),
                        # --- NOVO: FORÇAR NOTES A SER TEXTO ---
                        "Notes": st.column_config.TextColumn(
                            "Notes",
                            help="Detalhes da atividade (Texto ou Números)",
                            default="", # Se criar nova linha, começa vazio
                        ),
                    }
                )

        changes = st.session_state["editor_table"]["edited_rows"]

        if len(changes) > 0:
            st.warning(f"You have changed {len(changes)} record(s). Do you want to save?")

        if st.button("💾 Save changes"):

            progress = st.progress(0)
            status_txt = st.empty()
            total_changes = len(changes)
            erros = 0

            i = 0

            for index_pandas, alterations in changes.items():
                i += 1
                progress.progress(i/total_changes)
                status_txt.text(f"Salvando {i}/{total_changes}... (Aguarde o Google)")

                time.sleep(1.5)

                complete_row = df_edited.loc[index_pandas]

                date_txt = str(complete_row["Date"])
                category_txt = str(complete_row["Category"])
                notes_txt = str(complete_row["Notes"]) if complete_row["Notes"] else ""
                try:
                    dur_int = int(complete_row["Duration"])
                except:
                    dur_int = 0

                register_data = update_record(
                    row_index=index_pandas,
                    date=date_txt,
                    category=category_txt,
                    notes=notes_txt,
                    duration=dur_int
                )
                if not register_data:
                    erros += 1
                    st.error(f"❌ Falha ao salvar linha {index_pandas}. Tente novamente.")
            
            # Finalização
            progress.empty() # Some com a barra
            status_txt.empty()
            
            if erros == 0:
                st.success("✅ Todas as alterações foram salvas!")
                import time
                time.sleep(1)
                st.cache_data.clear()
                st.rerun()
            else:
                st.warning(f"⚠️ Processo finalizado com {erros} erro(s). O sistema não irá recarregar para você ver o erro.")
else:
    st.dataframe(df, use_container_width=True)