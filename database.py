import pandas as pd
import streamlit as st
import os
import pygsheets
import json


def get_worksheet():
    """
    Function:
    Check if 'credentials.json' exists (Local Use on PC).
    It connects to my Google Sheets file via the Google Cloud API.
    Open and get all records of my database (file).
    """
    try:
        if os.path.exists("credentials.json"):
            credentials = pygsheets.authorize(service_file="credentials.json")
        else:
            # O pygsheets pede uma string JSON, então convertemos o dicionário de secrets
            if "gcp_service_account" in st.secrets:
                service_account_info = st.secrets["gcp_service_account"]
                json_creds = json.dumps(dict(service_account_info))
                credentials = pygsheets.authorize(service_account_json=json_creds)
            else:
                st.error("Arquivo credentials.json não encontrado e Secrets não configurados.")
                return None

        url = "https://docs.google.com/spreadsheets/d/1ADvnbbl6a3AzkguJ_Qeua3PoV0n0hxJgxrvDITsCa7k/edit?gid=0#gid=0"
        # Via my credentials, open my google sheets
        worksheet = credentials.open_by_url(url)

        return worksheet

    except Exception as e:
        st.error(f"Conection error: {e}")
        return None

def load_data():
    '''
    Conection usage for data load and tranform into a dataframe.
    '''
    sheet = get_worksheet()
    
    if sheet:
        # Get my records by my name sheet
        sheet = sheet.worksheet_by_title("database")
        # Transforms my records into a dataframe
        df = sheet.get_as_df()

        if df.empty:
             return pd.DataFrame(columns=["Date", "Category", "Notes", "Duration"])

        return df
    return pd.DataFrame()


def save_record(date, category, notes, duration):
    """
    Receive data and add a new row to the Google Sheets.
    """
    df = load_data()
    if df:
        # Convert date to string (YYYY-MM-DD) for google sheets understand
        row = [str(date), category, notes, duration]
        
        # The function append_now add a new row on the next available empty line
        df.append_row(row)
        return True
    return False