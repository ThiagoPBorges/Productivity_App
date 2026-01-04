import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st
import os

# --- CONFIGURAÇÃO ---
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def conectar_google_sheets():
    """
    Função Híbrida:
    1. Verifica se existe 'credentials.json' (Uso Local no PC).
    2. Se não existir, tenta ler de st.secrets (Uso na Nuvem).
    """
    try:
        # ESTRATÉGIA 1: Modo Local (PC)
        # Verifica fisicamente se o arquivo existe na pasta
        if os.path.exists("credentials.json"):
            creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", SCOPE)
        
        # ESTRATÉGIA 2: Modo Nuvem (Streamlit Cloud)
        # Se o arquivo não existe, assumimos que estamos na nuvem e buscamos no cofre
        else:
            # Esse bloco só roda se não tiver o arquivo json, evitando o erro no seu PC
            creds_dict = st.secrets["gcp_service_account"]
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)

        # Autentica e abre a planilha
        client = gspread.authorize(creds)
        sheet = client.open("FocusData_DB").sheet1 
        return sheet

    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return None

# ... (O resto das funções carregar_dados e salvar_registro continuam iguais)

def carregar_dados():
    """
    Lê os dados da nuvem e transforma em DataFrame do Pandas.
    """
    sheet = conectar_google_sheets()
    if sheet:
        # Pega todos os registros como lista de dicionários
        dados = sheet.get_all_records()
        
        # Se a planilha estiver vazia (só cabeçalho), retorna DF vazio com colunas certas
        if not dados:
             return pd.DataFrame(columns=["Date", "Category", "Activity", "Duration", "Notes"])
             
        df = pd.DataFrame(dados)
        
        # Garante que a data seja interpretada corretamente
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.date
            
        return df
    return pd.DataFrame()

def salvar_registro(data, categoria, atividade, tempo, notas):
    """
    Recebe os dados e adiciona uma nova linha lá no Google Sheets.
    """
    sheet = conectar_google_sheets()
    if sheet:
        # O gspread espera os dados como uma lista simples: [col1, col2, col3...]
        # Convertemos a data para string (YYYY-MM-DD) para o Sheets entender
        linha = [str(data), categoria, atividade, tempo, notas]
        
        # O append_row adiciona na primeira linha vazia disponível
        sheet.append_row(linha)
        return True
    return False