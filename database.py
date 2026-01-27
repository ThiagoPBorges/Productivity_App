import pandas as pd
import streamlit as st
import os
import pygsheets
import json

'''
# Use to reserve the local memory and to prevent the app from having to read code all the time.
@st.cache_resource
'''

def get_worksheet(sheet_name):
    """
    Function:
    Check if 'credentials.json' exists (Local Use on PC).
    It connects to my Google Sheets file via the Google Cloud API.
    Open and get all records of my database (file).
    """
    try:
        # STRATEGY 1: (Local Use on PC)
        if os.path.exists("credentials.json"):
            credentials = pygsheets.authorize(service_file="credentials.json")
        # STRATEGY 1: (Cloud Mode - Streamlit CLoud) - Use st.secrets
        else:
            # Pygsheets needs a JSON string, so we converted the secrets dictionary.
            if "gcp_service_account" in st.secrets:
                service_account_info = st.secrets["gcp_service_account"]
                # Convert the dictionary back to a JSON text
                json_creds = json.dumps(dict(service_account_info))
                credentials = pygsheets.authorize(service_account_json=json_creds)
            else:
                st.error("Credentials.json file not found and secrets not previous config.")
                return None

        url = "https://docs.google.com/spreadsheets/d/1ADvnbbl6a3AzkguJ_Qeua3PoV0n0hxJgxrvDITsCa7k/edit?gid=0#gid=0"

        # Via my credentials, get my google sheets
        gc = credentials.open_by_url(url)

        # Get my database from specific sheet
        worksheet = gc.worksheet_by_title(sheet_name)

        return worksheet
    
    except Exception as e:
        st.error(f"Erro de Conexão na aba {sheet_name}: {e}")
        return None

def get_df(sheet_name="database"):
    '''
    Conection usage for data load and tranform into a dataframe.
    '''
    sheet = get_worksheet(sheet_name)
    
    if sheet:
        # Transforms my records into a dataframe
        df = sheet.get_as_df(has_header=True)

        # If database is empty, create a visual database just to show what the model would look like.
        if df.empty:
            if sheet_name == "books_library_d":
                return pd.DataFrame(columns=["Name_book", "Author", "Total_pages", "Status"])
            elif sheet_name == "weekly_planner":
                return pd.DataFrame(columns=["Day", "Activity", "Notes", "Time"])
            else:
                return pd.DataFrame(columns=["Date", "Time", "Category", "Notes", "Duration", "Pages"])
        
        df['ID_Google'] = df.index + 2

        return df
    return None


def save_record(date, time, category, notes, duration, pages=0):
    """
    Receive data and add a new row to the Google Sheets.
    """
    sheet = get_worksheet("database")

    if sheet:
        # Convert date to string (YYYY-MM-DD) for google sheets understand
        row = [str(date), str(time), str(category), str(notes), int(duration), int(pages)]
        
        # The function gets the list of [row], and inserts it without overwriting. This means it will paste into the next blank row.
        sheet.append_table([row], start='A2', dimension='ROWS', overwrite=False)
        return True
    return False

def save_book(Name_book, Author, Total_pages, Status):
    """
    Receive data and add a new row to the Google Sheets.
    """
    sheet = get_worksheet("books_library_d")

    if sheet:
        # Convert date to string (YYYY-MM-DD) for google sheets understand
        row = [str(Name_book), str(Author), str(Total_pages), str(Status)]
        
        # The function gets the list of [row], and inserts it without overwriting. This means it will paste into the next blank row.
        sheet.append_table([row], start='A2', dimension='ROWS', overwrite=False)
        return True
    return False

def update_record(real_row_id,date, time, category, notes, duration, pages=0):
    """
    Update a record based on the pandas index
    """
    sheet = get_worksheet("database")

    if sheet:
        try:
            # Calculate real row of excel
            # (Pandas starts in 0, Excel starts in 1 + 1 from header = +2)
            google_row_number = real_row_id
            
            # Prepare rows and your type of data (Exactly sequence)
            row_data = [
                str(date), 
                str(time), 
                str(category), 
                str(notes), 
                int(duration),
                int(pages)
            ]
            
            # Define the exact address (Range)
            # Ex: If the line is 10, the range will be "A10:D10"
            range_address = f"A{google_row_number}:F{google_row_number}"
            
            st.toast(f"💾 Changing row {google_row_number}")
            # Send the update command via range
            sheet.update_values(crange=range_address, values=[row_data])
            
            return True
            
        except Exception as e:
            st.error(f"Error to update {range_address}: {e}")
            return False
                
    return False

def update_book(real_row_id,Name_book, Author, Total_pages, Status):
    """
    Update a record based on the pandas index
    """
    sheet = get_worksheet("books_library_d")

    if sheet:
        try:
            # Calculate real row of excel
            # (Pandas starts in 0, Excel starts in 1 + 1 from header = +2)
            google_row_number = real_row_id
            
            # Prepare rows and your type of data (Exactly sequence)
            row_data = [
                str(Name_book), 
                str(Author), 
                str(Total_pages), 
                str(Status)
            ]
            
            # Define the exact address (Range)
            # Ex: If the line is 10, the range will be "A10:D10"
            range_address = f"A{google_row_number}:F{google_row_number}"
            
            st.toast(f"💾 Changing row {google_row_number}")
            # Send the update command via range
            sheet.update_values(crange=range_address, values=[row_data])
            
            return True
            
        except Exception as e:
            st.error(f"Error to update {range_address}: {e}")
            return False
                
    return False

def save_planner(df):
    """
    Clean the sheet and overwrite with a new planner
    """
    try:
        planner = get_worksheet("weekly_planner")

        planner.clear()

        df_clean = df.fillna("")

        planner.set_dataframe(df_clean, (1,1))

    except Exception as e:
        st.error(f"Erro ao salvar Planner: {e}")
        return False
