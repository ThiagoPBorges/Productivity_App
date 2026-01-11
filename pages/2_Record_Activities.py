import streamlit as st
import pandas as pd
from datetime import date
from database import get_df
from database import save_record
from database import update_record
import time
from datetime import datetime
import pytz

# Set page config
st.set_page_config(
    page_title="Records",
    page_icon="📝",
    layout="wide"
)

# Set default state to hide the dataframe editor
if "show_editor" not in st.session_state:
    st.session_state["show_editor"] = False

# Main title of page
st.title("📝 Records")
st.markdown("---")

# Access control
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


# Variable to get df
df = get_df()

# ------- Settings to adjust Visualization & Data Settings -------
if not df.empty:
    df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
    df = df.dropna(subset=["Date"])

    df["Date"] = df["Date"].dt.date
    df["Notes"] = df["Notes"].fillna("").astype(str)
    df["Duration"] = df["Duration"].fillna(0).astype(int)
    
    if "ID_Google" in df.columns:
        df["ID_Google"] = pd.to_numeric(df["ID_Google"], errors='coerce').fillna(0).astype(int)

if df.empty:
    st.warning("No data found in Google Sheets. Add the first one!")
    st.stop()


# ----------------------- SIDEBAR & FILTERS -----------------------
st.sidebar.header("Filters")

# Create a option list for categories
categories_list = ["General"] + list(df["Category"].unique())
# Create a selection box on the sidebar
selected_category = st.sidebar.selectbox("Category", categories_list)
if selected_category != "General":
    df = df[df["Category"] == selected_category]



# ----------------------- INPUT FORM -----------------------
with st.form("form_register"):
    st.subheader("📝 New record")

    # Organizing them into columns to make them visual.
    col1, col2 = st.columns(2)

    with col1:
        register_date = st.date_input("Date", value=date.today(), format="DD/MM/YYYY")
        category = st.selectbox("Category", ["Studies", "English", "Read"])

    with col2:
        duration = st.number_input("Time Spent (minutes)", min_value=0, step=5)
        notes = st.text_input("Detail of the activity")

    # Organizing them into columns to make them visual.
    c1, c2, c3, c4 = st.columns([1.3,1.3,1.3,6.2])

    with c1:
            if is_admin:
                submitted = st.form_submit_button("💾 Save Register")
            else:
                submitted = st.form_submit_button("💾 Save Register", disabled=True)
                st.caption("🔒 Login to edit records.")
    with c2:
        if is_admin:
            # Editor button using the state to appear and hide editor mode
            editor_button = "❌ Close Editor" if st.session_state["show_editor"] else "✏️ Edit Register"
            editor_button_click = st.form_submit_button(editor_button)
        else:
            editor_button = "❌ Close Editor" if st.session_state["show_editor"] else "✏️ Edit Register"
            editor_button_click = st.form_submit_button(editor_button, disabled=True)
        
        # Change mode os state
        if editor_button_click:
            st.session_state["show_editor"] = not st.session_state["show_editor"]
            st.rerun()
    # Use to refresh data
    with c3:
        if is_admin:
            if st.form_submit_button("🔄 Refresh Data"):
                st.cache_data.clear()
                st.rerun()
        else:
            st.form_submit_button("🔄 Refresh Data", disabled=True)
    


# ----------------------- LOGIC OF SAVE -----------------------
if is_admin and submitted:

    br_time = pytz.timezone('America/Sao_Paulo')
    time_now = datetime.now(br_time).strftime("%H:%M:%S")

    save = save_record(register_date, time_now, category, notes, duration)
    
    if save:
        st.success("✅ Record saved successfully in Database!")
        # Visual efect after save
        st.balloons()
    else:
        st.error("❌ Error saving record in Database.")

# If state of page on to edit, show the editor dataframe
if st.session_state["show_editor"]:
    with st.container(border=True):
        if is_admin:
            st.subheader("✏️ Editor of records")
            st.caption("Edit directly in table below and press Enter.")

            df_visual = df.sort_values(by='Date', ascending=False)
            df_visual["ID_Google"] = df_visual["ID_Google"].astype(int)

            df_edited = st.data_editor(
                        df_visual,
                        width="stretch",
                        num_rows="fixed",
                        key="editor_table",
                        column_config={
                            "ID_Google": st.column_config.NumberColumn("ID Excel", disabled=True),
                            "Date": st.column_config.DateColumn(
                                "Date", format="DD/MM/YYYY", step=1
                            ),
                            "Time": st.column_config.TextColumn("Time"),
                            "Category": st.column_config.SelectboxColumn(
                                "Category", ["Studies", "English", "Read"]
                            ),
                            "Duration": st.column_config.NumberColumn("Duration (min)"),
                            "Notes": st.column_config.TextColumn("Notes"),
                        },
                        hide_index=True
                    )
            # Variable to store changes in the df
            changes = st.session_state["editor_table"]["edited_rows"]

            # If there is change, show quantity of them
            if len(changes) > 0:
                st.warning(f"You have changed {len(changes)} record(s). Do you want to save?")

            if st.button("💾 Save changes"):
                progress = st.progress(0)
                status_txt = st.empty()
                total_changes = len(changes)
                erros = 0
                i = 0

                # Aqui 'index_pandas' é o número interno do Pandas (ex: 55), não o ID do Google
                for index_pandas, alterations in changes.items():
                    i += 1
                    progress.progress(i/total_changes)

                    try:
                        # 1. Buscamos a linha no DataFrame Visual usando o índice do Pandas
                        # O .loc[index_pandas] acha a linha original mesmo se estiver ordenada
                        if index_pandas in df_visual.index:
                            complete_row = df_visual.loc[index_pandas]
                            
                            # 2. AGORA sim pegamos o ID do Google de dentro da coluna
                            real_id = int(complete_row["ID_Google"])

                            status_txt.markdown(f"💾 Saving Row... **Category:** {complete_row['Category']} | **ID:** {real_id}")
                            time.sleep(0.5)

                            # 3. Mescla os dados originais com o que você alterou
                            # (Se alterou só Duration, mantemos as Notas antigas, etc)
                            current_data = complete_row.to_dict()
                            # Atualiza com as alterações vindas do editor
                            current_data.update(alterations)

                            # Prepara envio
                            # Nota: dataframe usa Timestamp, convertemos para string
                            date_val = current_data["Date"]
                            if hasattr(date_val, 'strftime'):
                                date_txt = date_val.strftime("%Y-%m-%d")
                            else:
                                date_txt = str(date_val)

                            category_txt = str(current_data["Category"])
                            notes_txt = str(current_data["Notes"]) if pd.notna(current_data["Notes"]) else ""
                            time_txt = str(current_data["Time"]) if pd.notna(current_data["Time"]) else ""

                            try:
                                dur_int = int(current_data["Duration"])
                            except:
                                dur_int = 0

                            # Envia
                            register_data = update_record(
                                real_row_id=real_id,
                                date=date_txt,
                                time=time_txt,
                                category=category_txt,
                                notes=notes_txt,
                                duration=dur_int
                            )
                            
                            if not register_data:
                                erros += 1
                                st.error(f"❌ Error saving ID {real_id}.")
                        else:
                            st.warning(f"⚠️ Could not locate row index {index_pandas} in current view.")
                            erros += 1

                    except Exception as e:
                        st.error(f"⚠️ Error processing row: {e}")
                        erros += 1
                
                progress.empty()
                status_txt.empty()
                
                if erros == 0:
                    st.success("✅ All records updated successfully!")
                    time.sleep(1)
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.warning(f"⚠️ Process finished with {erros} error(s).")
        else:
            st.warning("🔒 You are in View Mode.")
            st.dataframe(df.sort_values(by='Date', ascending=True), use_container_width=True)

if not st.session_state["show_editor"]:
    st.dataframe(
        df.sort_values(by='Date', ascending=False),
        use_container_width=True,
        hide_index=True,
        column_config={"ID_Google": None}
    )