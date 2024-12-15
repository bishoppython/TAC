import pandas as pd
import sqlite3
import streamlit as st
from visualizacao import *
from predicao import *
from about import *

# Função para criar conexões temporárias
def get_data_from_sqlite(query):
    with sqlite3.connect('violencia_dm.db', check_same_thread=False) as conn:
        return pd.read_sql_query(query, conn)

# Função para tratamento de dados
def tratamento_data():
    conn = sqlite3.connect('violencia_dm.db', check_same_thread=False)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name='violencia_domestica';
        """)
        tabela_existe = cursor.fetchone()

        if tabela_existe:
            cursor.execute("SELECT COUNT(*) FROM violencia_domestica;")
            registros = cursor.fetchone()[0]
            if registros > 0:
                st.info("Os dados já estão salvos no banco SQLite. Pulando carregamento do Excel.")
                return

        violencia_dm = pd.read_excel('MICRODADOS_DE_VIOLÊNCIA_DOMÉSTICA_JAN_2015_A_AGO_2024.xlsx')
        violencia_dm = violencia_dm.rename(columns={
            'MUNICÍPIO DO FATO': 'MUNICIPIO',
            'REGIAO GEOGRÁFICA': 'REGIAO_GEOGRAFICA',
            'DATA DO FATO': 'DATA_FATO',
            'IDADE SENASP': 'FAIXA_IDADE',
            'TOTAL DE ENVOLVIDOS': 'TOTAL'
        })
        violencia_dm.to_sql('violencia_domestica', conn, if_exists='replace', index=False)
        st.success("Dados carregados e salvos no SQLite com sucesso!")
    finally:
        cursor.close()
        conn.close()

# Carregar dados para tratamento inicial
tratamento_data()

# Configuração principal do Streamlit
st.sidebar.title("Microdados de Violência Doméstica em Pernambuco")
tab = st.sidebar.radio("Selecione a análise:", ["About", "Dados de Violência Doméstica", "Probabilidades Futuras"])

# Exibir o conteúdo com base na aba selecionada
if tab == "About":
    about()
elif tab == "Dados de Violência Doméstica":
    violencia_dm = get_data_from_sqlite("SELECT * FROM violencia_domestica")
    st.subheader("Dados de Violência Doméstica")
    st.dataframe(violencia_dm.head(10))
elif tab == "Probabilidades Futuras":
    predition()
