import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import sqlite3
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import time


# Função para carregar dados do SQLite
def load_data():
    # Conecta ao banco SQLite
    conn = sqlite3.connect('violencia_dm.db')

    # Lê os dados da tabela 'violencia_domestica' para um DataFrame
    violencia_dm = pd.read_sql_query("SELECT * FROM violencia_domestica", conn)

    # Fecha a conexão com o banco
    conn.close()

    # Retorna o DataFrame
    return violencia_dm


# Função para predição com regressão linear
def preditor_linear(data, group_col, target_col):
    resultados = {}
    anos = sorted(data['ANO'].unique())
    anos_futuros = np.arange(max(anos) + 1, max(anos) + 6)  # Próximos 5 anos

    for group, subset in data.groupby(group_col):
        X = subset['ANO'].values.reshape(-1, 1)
        y = subset[target_col].values
        model = LinearRegression()
        model.fit(X, y)
        previsoes = model.predict(anos_futuros.reshape(-1, 1))
        resultados[group] = {ano: max(int(pred), 0) for ano, pred in zip(anos_futuros, previsoes)}
    return resultados


# Função principal para o app
def predition():
    st.title('Análise e Predição de Crimes')
    with st.spinner("Aguarde processando os dados e criando as predições..."):
        time.sleep(5)

    violencia_dm = load_data()
    violencia_dm['ANO'] = pd.to_numeric(violencia_dm['ANO'], errors='coerce')

    st.sidebar.header('Selecione a Análise:')
    analysis = st.sidebar.selectbox(
        '',
        [
            'Predição de Crimes Temporal',
            'Predição dos Crimes com Maiores Incidências',
            # 'Evolução das Cidades com Maior Incidência de Crimes',
            'Evolução do Total de Crimes por Região Geográfica',
        ]
    )

    if analysis == 'Predição de Crimes Temporal':
        df_ano = violencia_dm.groupby('ANO')['TOTAL'].sum().reset_index()
        df_ano.columns = ['ANO', 'TOTAL']

        X = df_ano[['ANO']]
        y = df_ano['TOTAL']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = LinearRegression()
        model.fit(X_train, y_train)

        anos_futuros = pd.DataFrame({'ANO': np.arange(df_ano['ANO'].max() + 1, df_ano['ANO'].max() + 6)})
        predicoes = model.predict(anos_futuros)

        st.subheader('Previsão do Número de Crimes para os Próximos Anos')
        fig = px.line(
            x=df_ano['ANO'].tolist() + anos_futuros['ANO'].tolist(),
            y=df_ano['TOTAL'].tolist() + predicoes.tolist(),
            title='Evolução e Previsão do Número de Crimes',
            labels={'x': 'Ano', 'y': 'Número de Crimes'}
        )
        st.plotly_chart(fig)

    elif analysis == 'Predição dos Crimes com Maiores Incidências':
        crime_data = violencia_dm.groupby(['ANO', 'NATUREZA'], as_index=False)['TOTAL'].sum()
        previsoes_crime = preditor_linear(crime_data, 'NATUREZA', 'TOTAL')

        st.subheader('Predição de Crimes por Natureza')
        rows_crime = []
        for crime, anos in previsoes_crime.items():
            for ano, total in anos.items():
                rows_crime.append({'Natureza': crime, 'Ano': ano, 'Total': total})
        df_crime = pd.DataFrame(rows_crime)

        fig = px.line(
            df_crime,
            x='Ano',
            y='Total',
            color='Natureza',
            title='Predição de Crimes por Natureza',
            labels={'Ano': 'Ano', 'Total': 'Total de Ocorrências'}
        )
        st.plotly_chart(fig)

    # elif analysis == 'Evolução das Cidades com Maior Incidência de Crimes':
    #     cidade_data = violencia_dm.groupby(['ANO', 'MUNICIPIO'], as_index=False)['TOTAL'].sum()
    #     previsoes_cidade = preditor_linear(cidade_data, 'MUNICIPIO', 'TOTAL')
    #
    #     st.subheader('Predição de Cidades com Maior Incidência de Crimes')
    #     rows_cidade = []
    #     for cidade, anos in previsoes_cidade.items():
    #         for ano, total in anos.items():
    #             rows_cidade.append({'Cidade': cidade, 'Ano': ano, 'Total': total})
    #     df_cidade = pd.DataFrame(rows_cidade)
    #
    #     fig = px.line(
    #         df_cidade,
    #         x='Ano',
    #         y='Total',
    #         color='Cidade',
    #         title='Predição de Cidades com Maior Incidência de Crimes',
    #         labels={'Ano': 'Ano', 'Total': 'Total de Ocorrências'}
    #     )
    #     st.plotly_chart(fig)

    elif analysis == 'Evolução do Total de Crimes por Região Geográfica':
        regiao_data = violencia_dm.groupby(['ANO', 'REGIAO_GEOGRAFICA'], as_index=False)['TOTAL'].sum()
        previsoes_regiao = preditor_linear(regiao_data, 'REGIAO_GEOGRAFICA', 'TOTAL')

        st.subheader('Predição de Crimes por Região Geográfica')
        rows_regiao = []
        for regiao, anos in previsoes_regiao.items():
            for ano, total in anos.items():
                rows_regiao.append({'Região Geográfica': regiao, 'Ano': ano, 'Total': total})
        df_regiao = pd.DataFrame(rows_regiao)

        fig = px.line(
            df_regiao,
            x='Ano',
            y='Total',
            color='Região Geográfica',
            title='Predição de Crimes por Região Geográfica',
            labels={'Ano': 'Ano', 'Total': 'Total de Ocorrências'}
        )
        st.plotly_chart(fig)


if __name__ == '__main__':
    predition()