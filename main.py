import pandas as pd
import sqlite3
import streamlit as st
from visualizacao import *
from predicao import *
from about import *

# Função para tratamento de dados
def tratamento_data():
    # Conectar ao banco SQLite
    conn = sqlite3.connect('violencia_dm.db', check_same_thread=False)

    # Verificar se a tabela já existe e contém dados
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name='violencia_domestica';
        """)
        tabela_existe = cursor.fetchone()
    
        if tabela_existe:
            # Verificar se a tabela contém dados
            cursor.execute("SELECT COUNT(*) FROM violencia_domestica;")
            registros = cursor.fetchone()[0]
            if registros > 0:
                st.info("Os dados já estão salvos no banco SQLite. Pulando carregamento do Excel.")
                conn.close()
                return  # Não fazer nada se os dados já estiverem no banco

        # Caso contrário, carregar do Excel e salvar no SQLite
        violencia_dm = pd.read_excel('MICRODADOS_DE_VIOLÊNCIA_DOMÉSTICA_JAN_2015_A_AGO_2024.xlsx')
        pd.set_option('display.max_columns', 100)
        violencia_dm = violencia_dm.rename(columns={
            'MUNICÍPIO DO FATO': 'MUNICIPIO',
            'REGIAO GEOGRÁFICA': 'REGIAO_GEOGRAFICA',
            'DATA DO FATO': 'DATA_FATO',
            'IDADE SENASP': 'FAIXA_IDADE',
            'TOTAL DE ENVOLVIDOS': 'TOTAL'
        })
    
        # Remover o índice numérico seguido de ')'
        violencia_dm['FAIXA_IDADE'] = violencia_dm['FAIXA_IDADE'].str.replace(r'^\d+\)\s*', '', regex=True)
        violencia_dm['FAIXA_IDADE'] = violencia_dm['FAIXA_IDADE'].str.replace('(vazio)', 'não informado')
    
        # Salvar no SQLite
        violencia_dm.to_sql('violencia_domestica', conn, if_exists='replace', index=False)

    finally:
        # Certifique-se de fechar o cursor e a conexão
        cursor.close()
        conn.close()

    # st.success("Dados carregados do Excel e salvos no banco SQLite com sucesso.")

# Carregar dados para tratamento inicial
tratamento_data()

# Configuração principal do Streamlit
# st.title("Estudo sobre Microdados de Violência Doméstica em Pernambuco")
st.sidebar.title("Microdados de Violência Doméstica em Pernambuco")
tab = st.sidebar.radio("Selecione a análise:", ["About", "Dados de Violência Doméstica", "Probabilidades Futuras"])

# Exibir o conteúdo com base na aba selecionada
if tab == "About":
    about()
# Exibir o conteúdo com base na aba selecionada
elif tab == "Dados de Violência Doméstica":
    # st.subheader("Visualização de Dados de Violência Doméstica")
    visualizacao()
elif tab == "Probabilidades Futuras":
    # st.subheader("Predições de Probabilidades Futuras")
    predition()
