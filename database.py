import pandas as pd
import streamlit as st
import os
import pygsheets
import json

# Use to reserve the local memory and to prevent the app from having to read code all the time.
@st.cache_resource

def get_worksheet():
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
        worksheet = gc.worksheet_by_title("database")

        return worksheet
    
    except Exception as e:
        st.error(f"Erro de Conexão: {e}")
        return None

def get_df():
    '''
    Conection usage for data load and tranform into a dataframe.
    '''
    sheet = get_worksheet()
    
    if sheet:
        # Transforms my records into a dataframe
        df = sheet.get_as_df()

        # If database is empty, create a visual database just to show what the model would look like.
        if df.empty:
             return pd.DataFrame(columns=["Date", "Time", "Category", "Notes", "Duration"])

        return df
    return None


def save_record(date, time, category, notes, duration):
    """
    Receive data and add a new row to the Google Sheets.
    """
    sheet = get_worksheet()

    if sheet:
        # Convert date to string (YYYY-MM-DD) for google sheets understand
        row = [str(date), time, category, notes, duration]
        
        # The function gets the list of [row], and inserts it without overwriting. This means it will paste into the next blank row.
        sheet.append_table([row], start='A1', dimension='ROWS', overwrite=False)
        return True
    return False

def update_record(row_index,date, time, category, notes, duration):
    """
    Update a record based on the pandas index
    """
    sheet = get_worksheet()

    if sheet:
        try:
            # Calculate real row of excel
            # (Pandas starts in 0, Excel starts in 1 + 1 from header = +2)
            google_row_number = row_index + 2
            
            # Prepare rows and your type of data (Exactly sequence)
            row_data = [str(date), str(time), str(category), str(notes), int(duration)]
            
            # Define the exact address (Range)
            # Ex: If the line is 10, the range will be "A10:D10"
            range_address = f"A{google_row_number}:E{google_row_number}"
            
            # Send the update command via range
            sheet.update_values(crange=range_address, values=[row_data])
            
            return True
            
        except Exception as e:
            st.error(f"Error to update row {range_address}: {e}")
            return False
                
    return False
