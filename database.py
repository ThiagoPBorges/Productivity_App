import pandas as pd
import streamlit as st
import os
import pygsheets
import json
import time

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
                st.error("Arquivo credentials.json não encontrado e Secrets não configurados.")
                return None

        url = "https://docs.google.com/spreadsheets/d/1ADvnbbl6a3AzkguJ_Qeua3PoV0n0hxJgxrvDITsCa7k/edit?gid=0#gid=0"

        # Via my credentials, get my google sheets
        gc = credentials.open_by_url(url)

        worksheet = gc.worksheet_by_title("database")

        return worksheet
    
    except Exception as e:
        # Se der erro, não fazemos cache para tentar conectar de novo na próxima
        st.error(f"Erro de Conexão: {e}")
        return None

    except Exception as e:
        st.error(f"Conection error: {e}")
        return None

def get_df():
    '''
    Conection usage for data load and tranform into a dataframe.
    '''
    sheet = get_worksheet()
    
    if sheet:
        # Transforms my records into a dataframe
        df = sheet.get_as_df()

        if df.empty:
             return pd.DataFrame(columns=["Date", "Category", "Notes", "Duration"])

        return df
    return None


def save_record(date, category, notes, duration):
    """
    Receive data and add a new row to the Google Sheets.
    """
    sheet = get_worksheet()

    if sheet:
        # Convert date to string (YYYY-MM-DD) for google sheets understand
        row = [str(date), category, notes, duration]
        
        # The function gets the list of [row], and inserts it without overwriting. This means it will paste into the next blank row.
        sheet.append_table([row], start='A1', dimension='ROWS', overwrite=False)
        return True
    return False

def update_record(row_index,date, category, notes, duration):
    """
    Update a record based on the pandas index
    """
    sheet = get_worksheet()

    if sheet:
        try:
            # 1. Calcula a linha real no Excel
            # (Pandas começa em 0, Excel começa em 1 + 1 do cabeçalho = +2)
            google_row_number = row_index + 2
            
            # 2. Prepara os dados
            # A ordem da lista deve ser IGUAL às colunas da planilha:
            # Coluna A (Date), B (Category), C (Notes), D (Duration)
            row_data = [str(date), str(category), str(notes), int(duration)]
            
            # 3. Define o endereço exato (Range)
            # Ex: Se linha for 10, o range será "A10:D10"
            range_address = f"A{google_row_number}:D{google_row_number}"
            
            # 4. Envia o comando de atualização por Range
            # values deve ser uma lista de listas -> [[dados]]
            sheet.update_values(crange=range_address, values=[row_data])
            
            return True
            
        except Exception as e:
            st.error(f"Erro ao atualizar linha {google_row_number}: {e}")
            return False
                
    return False
