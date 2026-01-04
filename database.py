import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st
import os
from google.oauth2 import service_account

# --- CONFIGURATIONS ---
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def connect_google_sheets():
    """
    Hybrid Function:
    1. Check if 'credentials.json' exists (Local Use on PC)
    2. If it doesn't exist, try reading from st.secrets (Cloud Usage)
    """
    try:
        # 1.
        if os.path.exists("credentials.json"):
            creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", SCOPE)
        # 2.
        else:
            creds_dict = st.secrets["gcp_service_account"]
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)

        # Authenticates and opens the spreadsheet
        client = gspread.authorize(creds)
        sheet = client.open("FocusData_DB").sheet1 
        return sheet

    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return None


def carregar_dados():
    """
    Read data from cloud and transform into a Pandas Dataframe
    """
    sheet = connect_google_sheets()
    if sheet:
        # Get all records as a dictionary list
        dados = sheet.get_all_records()
        
        # If the spreadsheet is empty (Only the Header), returns empty DF with correct columns
        if not dados:
             return pd.DataFrame(columns=["Date", "Category", "Activity", "Duration", "Notes"])
             
        df = pd.DataFrame(dados)
        
        # Ensures the date is interpreted correctly
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.date
            
        return df
    return pd.DataFrame()

def salvar_registro(data, categoria, atividade, tempo, notas):
    """
    Receive data and add a new row to the Google Sheets.
    """
    sheet = connect_google_sheets()
    if sheet:
        # Convert date to string (YYYY-MM-DD) for google sheets understand
        linha = [str(data), categoria, atividade, tempo, notas]
        
        # The function append_now add a new row on the next available empty line
        sheet.append_row(linha)
        return True
    return False