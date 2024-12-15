import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import sqlite3


# Função para carregar dados do SQLite
def load_data():
    # Conecta ao banco SQLite
    conn = sqlite3.connect('violencia_dm.db')

    # Lê os dados da tabela 'violencia_domestica' para um DataFrame
    violencia_dm = pd.read_sql_query("SELECT * FROM violencia_domestica", conn)

    # Fecha a conexão com o banco
    conn.close()

    # Retorna apenas as 10 primeiras linhas do DataFrame
    return violencia_dm.head(10)


# Função principal para exibir os dados
def about():
    st.title("Exibição de Dados - Violência Doméstica")

    with st.spinner("Carregando dados..."):
        data = load_data()

    st.subheader("Dados de Referência")
    st.dataframe(data)  # Exibe os dados em formato de tabela no Streamlit


if __name__ == '__main__':
    about()
