import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st

# --- CONFIGURAÇÃO ---
# Define o escopo (o que o robô pode acessar: Drive e Planilhas)
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# --- ATENÇÃO: Substitua a função antiga por esta no database.py ---

def conectar_google_sheets():
    """
    Função que autentica e retorna a aba da planilha.
    Tenta ler primeiro dos Secrets (Nuvem), se falhar, tenta ler do arquivo local (PC).
    """
    try:
        # TENTA LER DOS SEGREDOS (Para quando estiver na Nuvem)
        # O Streamlit guarda segredos num dicionário chamado st.secrets
        if "gcp_service_account" in st.secrets:
            creds_dict = st.secrets["gcp_service_account"]
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
        
        # TENTA LER DO ARQUIVO (Para quando você estiver rodando local no VS Code)
        else:
            creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", SCOPE)

        client = gspread.authorize(creds)
        sheet = client.open("FocusData_DB").sheet1 
        return sheet
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return None

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