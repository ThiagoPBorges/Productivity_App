import streamlit as st
import pandas as pd
from datetime import date
from database import get_df
from database import save_record
from database import update_record
import time
from datetime import datetime
import pytz
import time

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


# ----------------------- STOPWATCH -----------------------

@st.fragment(run_every=1)
def stopwatch():
    if "running" not in st.session_state:
        st.session_state.running = False
    if "start_time" not in st.session_state:
        st.session_state.start_time = None
    if "elapsed_total" not in st.session_state:
        st.session_state.elapsed_total = 0

    with st.container(border=True):
            
            c1, c2, c3 = st.columns([2, 1, 1])

            with c1:
                st.caption("⏱️ Activity Timer")

                if st.session_state.running:
                    # If it's working, calculate the real time
                    current_total = time.time() - st.session_state.start_time
                    minutes = int(current_total // 60)
                    seconds = int(current_total % 60)
                else:
                    # If stopped, show the last saved value
                    minutes = int(st.session_state.elapsed_total // 60)
                    seconds = int(st.session_state.elapsed_total % 60)
                st.markdown(f"## {minutes:02d}:{seconds:02d}")

            with c2:
                st.write("")
                if not st.session_state.running:
                    if st.session_state.elapsed_total < 1:
                        if st.button("▶️ Start"):
                            st.session_state.running = True
                            st.session_state.start_time = time.time()
                            st.rerun()
                    else:
                        st.success("✅ Done!")

                else:
                    if st.button("⏹️ Stop"):
                        # If stop, calculate the minute total and save
                        st.session_state.elapsed_total = time.time() - st.session_state.start_time
                        st.session_state.running = False
                        st.rerun()
            
            with c3:
                st.write("")
                if st.button("🔄 Reset"):
                    st.session_state.elapsed_total = 0
                    st.session_state.running = False
                    st.rerun()

stopwatch()


# ----------------------- INPUT FORM -----------------------
with st.container(border=True):
    st.subheader("📝 New record")

    br_timezone = pytz.timezone('America/Sao_Paulo')
    today_br = datetime.now(br_timezone).date()

    # Organizing them into columns to make them visual.
    col1, col2 = st.columns(2)

    with col1:
        register_date = st.date_input("Date", value=today_br, format="DD/MM/YYYY")
        category = st.selectbox("Category", ["Studies", "English", "Read", "Personal projects", "Workout"])

    with col2:
        if category == "Read":
            pages = st.number_input("Pages of book", min_value=1, step=2)
        else:
            pages = 0
        duration = st.number_input("Time Spent (minutes)", min_value=1, step=5)
        notes = st.text_input("Detail of the activity")

    # Organizing them into columns to make them visual.
    c1, c2, c3, c4 = st.columns([1.3,1.3,1.3,6.2])

    with c1:
            if is_admin:
                submitted = st.button("💾 Save Register")
            else:
                submitted = st.button("💾 Save Register", disabled=True)
                st.caption("🔒 Login to edit records.")
    with c2:
        if is_admin:
            # Editor button using the state to appear and hide editor mode
            editor_button = "❌ Close Editor" if st.session_state["show_editor"] else "✏️ Edit Register"
            editor_button_click = st.button(editor_button)
        else:
            editor_button = "❌ Close Editor" if st.session_state["show_editor"] else "✏️ Edit Register"
            editor_button_click = st.button(editor_button, disabled=True)
        
        # Change mode os state
        if editor_button_click:
            st.session_state["show_editor"] = not st.session_state["show_editor"]
            st.rerun()
    # Use to refresh data
    with c3:
        if is_admin:
            if st.button("🔄 Refresh Data"):
                st.cache_data.clear()
                st.rerun()
        else:
            st.button("🔄 Refresh Data", disabled=True)
    


# ----------------------- LOGIC OF SAVE -----------------------
if is_admin and submitted:

    br_time = pytz.timezone('America/Sao_Paulo')
    time_now = datetime.now(br_time).strftime("%H:%M:%S")

    save = save_record(register_date, time_now, category, notes, duration, pages)
    
    if save:
        st.success("✅ Record saved successfully in Database!")
        # Visual efect after save
        st.balloons()
        time.sleep(1)
        st.cache_data.clear()
        st.rerun()
    else:
        st.error("❌ Error saving record in Database.")


# ----------------------- EDITOR LOGIC -----------------------
if st.session_state["show_editor"]:
    with st.container(border=True):
        if is_admin:
            st.subheader("✏️ Editor of records")
            st.caption("Edit directly in table below and press Enter.")

            df_visual = df.sort_values(by='Date', ascending=False)

            df_visual = df_visual.reset_index(drop=True)
            df_visual["ID_Google"] = df_visual["ID_Google"].astype(int)

            df_edited = st.data_editor(
                        df_visual,
                        width="stretch",
                        num_rows="fixed",
                        key="editor_table",
                        column_config={
                            "ID_Google": None,
                            "Date": st.column_config.DateColumn("Date", format="DD/MM/YYYY", step=1),
                            "Time": st.column_config.TextColumn("Time"),
                            "Category": st.column_config.TextColumn("Category"),
                            "Notes": st.column_config.TextColumn("Notes"),
                            "Duration": st.column_config.NumberColumn("Duration (min)"),
                            "Pages": st.column_config.NumberColumn("Pages")
                        },
                        hide_index=True
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

                for index_visual, alterations in changes.items():
                    i += 1
                    progress.progress(i/total_changes)

                    try:
                        current_row = df_visual.iloc[index_visual]
                        real_id = int(current_row["ID_Google"])

                        status_txt.markdown(f"💾 Saving Row... **Category:** {current_row['Category']} | **ID:** {real_id}")
                        time.sleep(1)

                        # --- MISTURA DADOS ANTIGOS + NOVOS ---
                        current_data = current_row.to_dict()
                        current_data.update(alterations)

                        # Prepara dados para envio
                        date_val = current_data["Date"]
                        # Garante formato de string YYYY-MM-DD
                        if hasattr(date_val, 'strftime'):
                            date_txt = date_val.strftime("%Y-%m-%d")
                        else:
                            date_txt = str(date_val)

                        category_txt = str(current_data["Category"])
                        notes_txt = str(current_data["Notes"]) if pd.notna(current_data["Notes"]) else ""
                        time_txt = str(current_data["Time"]) if pd.notna(current_data["Time"]) else ""
                        page_txt = str(current_data["Pages"]) if pd.notna(current_data["Pages"]) else ""


                        try:
                            dur_int = int(current_data["Duration"])
                        except:
                            dur_int = 0

                        # ENVIA PARA O GOOGLE SHEETS
                        register_data = update_record(
                            real_row_id=real_id,
                            date=date_txt,
                            time=time_txt,
                            category=category_txt,
                            notes=notes_txt,
                            duration=dur_int,
                            pages=page_txt
                        )
                        
                        if not register_data:
                            erros += 1
                            st.error(f"❌ Error saving ID {real_id}.")

                    except Exception as e:
                        st.error(f"⚠️ Unexpected error on ID {index_visual}: {e}")
                        erros += 1
                
                progress.empty()
                status_txt.empty()
                
                if erros == 0:
                    st.success("✅ All records updated successfully!")
                    time.sleep(1)
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.warning(f"⚠️ Finished with {erros} error(s).")
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