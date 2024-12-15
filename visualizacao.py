import json

import pandas as pd
import sqlite3
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go


# Função para carregar dados do banco SQLite
def load_data():
    # Conecta ao banco SQLite
    conn = sqlite3.connect('violencia_dm.db')
    # Lê os dados da tabela 'violencia_domestica' para um DataFrame
    violencia_dm = pd.read_sql_query("SELECT * FROM violencia_domestica", conn)
    # Fecha a conexão com o banco
    conn.close()
    return violencia_dm

# Verificar se o banco de dados está disponível
def check_database():
    conn = sqlite3.connect('violencia_dm.db')
    cursor = conn.cursor()

    # Verifica se a tabela existe
    cursor.execute("""
        SELECT name FROM sqlite_master WHERE type='table' AND name='violencia_domestica';
    """)
    tabela_existe = cursor.fetchone()

    if not tabela_existe:
        st.error("Os dados não estão no banco SQLite. Por favor, carregue os dados primeiro.")
        conn.close()
        st.stop()

    # Fecha a conexão
    conn.close()

# Função principal para o app
def visualizacao():
    st.title('Análise Interativa sobre Crimes Domésticos em Pernambuco')

    # Carregar dados do banco
    violencia_dm = load_data()
    violencia_dm['ANO'] = pd.to_numeric(violencia_dm['ANO'], errors='coerce')

    # Barra lateral para seleção de visualização
    st.sidebar.header('Selecione a Visualização:')
    analysis = st.sidebar.selectbox('', [
        'Distribuição de Crimes - Região Geográfica',
        'Total de Casos em Pernambuco',
        'Total de Casos por Região Geográfica',
        'Crime com Maior Incidência',
        'Top 10 Crimes com maior Relevância',
        'Crimes Domésticos Por Sexo e Natureza',
        'Mapa de Crimes por Município'
    ])

    # Análise 1: Distribuição de Crimes por Sexo ao Longo dos Anos'
    if analysis == 'Distribuição de Crimes - Região Geográfica':
        st.subheader('Análise Temporal de Crimes - Região Geográfica')

        # Criar a tabela pivot para agrupar os dados por ANO e REGIAO_GEOGRAFICA
        violenciaPivot_df = violencia_dm.pivot_table(
            values='TOTAL',
            index='ANO',
            columns='REGIAO_GEOGRAFICA',
            aggfunc='sum'
        )

        # Criar a figura
        fig = go.Figure()

        # Adicionar uma linha para cada região geográfica
        for regiao in violenciaPivot_df.columns:
            fig.add_trace(
                go.Scatter(
                    x=violenciaPivot_df.index,
                    y=violenciaPivot_df[regiao],
                    mode='lines+markers',
                    name=regiao
                )
            )

        # Ajustar o layout
        fig.update_layout(
            title='Comparação Temporal de Ocorrências por Ano e Região Geográfica',
            xaxis_title='Ano',
            yaxis_title='Total de Ocorrências',
            legend_title='Região Geográfica',
            template='plotly_white'
        )

        # Exibir o gráfico no Streamlit
        st.plotly_chart(fig)

    # Análise 3: Top 10 Cidades com Mais Crimes
    elif analysis == 'Total de Casos em Pernambuco':
        st.subheader("Total de Casos em Pernambuco - ANO")

        # Agrupar os dados para contar o número de casos por ano
        df_ano = violencia_dm['ANO'].value_counts().reset_index()
        df_ano.columns = ['ANO', 'Número de Casos']
        df_ano = df_ano.sort_values('ANO')  # Ordenar os anos para manter a sequência

        # Gráfico de barras
        fig = px.bar(
            df_ano,
            x="ANO",
            y="Número de Casos",
            title="Total de Violência Doméstica em Pernambuco - ANO",
            labels={"ANO": "Ano", "Número de Casos": "Número de Casos"},
            color_discrete_sequence=["#1f77b4"]  # Cor única para todas as barras
        )

        # Ajustes de layout
        fig.update_layout(
            xaxis=dict(
                tickmode="linear",  # Garantir que todos os anos apareçam no eixo X
                tick0=df_ano["ANO"].min(),
                dtick=1
            ),
            xaxis_title="Ano",
            yaxis_title="Número de Casos",
            title=dict(
                text="Total de Violência Doméstica em Pernambuco - ANO",
                x=0  # Centralizar o título
            ),
            template="plotly_white"  # Tema visual mais limpo
        )

        # Exibir o gráfico no Streamlit
        st.plotly_chart(fig)

    # Análise 4: Incidência de Crimes por Ano
    elif analysis == 'Total de Casos por Região Geográfica':
        st.subheader("Total de Casos por Região Geográfica")

        violencia_dm['TOTAL'] = pd.to_numeric(violencia_dm['TOTAL'], errors='coerce')

        # Agrupar os dados por Região Geográfica e Sexo
        violencia_dm_sexo = violencia_dm.groupby(['REGIAO_GEOGRAFICA', 'SEXO'], as_index=False)['TOTAL'].sum()

        # Gráfico de Barras Empilhadas
        fig = px.bar(
            violencia_dm_sexo,
            x='REGIAO_GEOGRAFICA',
            y='TOTAL',
            color='SEXO',
            title='Total de Casos por Região Geográfica',
            labels={'TOTAL': 'Total de Casos', 'REGIAO_GEOGRAFICA': 'Região Geográfica'},
            barmode='stack',  # Configura as barras para serem empilhadas
            color_discrete_sequence=px.colors.qualitative.Dark24  # Paleta predefinida
        )

        # Exibir o gráfico no Streamlit
        st.plotly_chart(fig)

    # Análise 4: Incidência de Crimes por Ano
    elif analysis == 'Crime com Maior Incidência':
        # Subtítulo no Streamlit
        st.subheader("Crime com Maior Incidência por Região Geográfica")

        # Agrupar por REGIAO_GEOGRAFICA e NATUREZA, somando os totais
        regiao_natureza = violencia_dm.groupby(['REGIAO_GEOGRAFICA', 'NATUREZA'], as_index=False)['TOTAL'].sum()

        # Identificar o crime mais frequente por região
        crime_mais_frequente = regiao_natureza.loc[
            regiao_natureza.groupby('REGIAO_GEOGRAFICA')['TOTAL'].idxmax()
        ]

        # Criar o gráfico de barras
        fig = px.bar(
            crime_mais_frequente,
            x='REGIAO_GEOGRAFICA',
            y='TOTAL',
            color='NATUREZA',
            title='Crime com Maior Incidência por Região Geográfica',
            labels={
                'REGIAO_GEOGRAFICA': 'Região Geográfica',
                'TOTAL': 'Total de Ocorrências',
                'NATUREZA': 'Natureza do Crime'
            },
            color_discrete_sequence=px.colors.qualitative.Bold  # Paleta de cores para diferenciar crimes
        )

        # Ajustar layout
        fig.update_layout(
            xaxis_title='Região Geográfica',
            yaxis_title='Total de Ocorrências',
            title_x=0,  # Centralizar o título
            template='plotly_white'
        )

        # Exibir o gráfico no Streamlit
        st.plotly_chart(fig)

    # Análise 5: Incidência de Crimes por Ano
    elif analysis == 'Top 10 Crimes com maior Relevância':

        # Subtítulo no Streamlit
        st.subheader("10 Crimes Mais Relevantes por Região Geográfica")

        # Agrupar por REGIAO_GEOGRAFICA e NATUREZA, somando os totais
        regiao_natureza = violencia_dm.groupby(['REGIAO_GEOGRAFICA', 'NATUREZA'], as_index=False)['TOTAL'].sum()

        # Selecionar os 10 crimes mais relevantes por região
        top_10_crimes_por_regiao = (
            regiao_natureza.sort_values(['REGIAO_GEOGRAFICA', 'TOTAL'], ascending=[True, False])
            .groupby('REGIAO_GEOGRAFICA')
            .head(10)
        )

        # Criar o gráfico de barras
        fig = px.bar(
            top_10_crimes_por_regiao,
            x='REGIAO_GEOGRAFICA',
            y='TOTAL',
            color='NATUREZA',
            title='10 Crimes Mais Relevantes por Região Geográfica',
            labels={
                'REGIAO_GEOGRAFICA': 'Região Geográfica',
                'TOTAL': 'Total de Ocorrências',
                'NATUREZA': 'Natureza do Crime'
            },
            barmode='group',  # Barras agrupadas por região
            color_discrete_sequence=px.colors.qualitative.Bold  # Paleta de cores
        )

        # Ajustar layout
        fig.update_layout(
            xaxis_title='Região Geográfica',
            yaxis_title='Total de Ocorrências',
            title_x=0,  # Centralizar o título
            template='plotly_white'
        )

        # Exibir o gráfico no Streamlit
        st.plotly_chart(fig)

    # Análise 6: Crimes Por Sexo e Natureza
    elif analysis == 'Crimes Domésticos Por Sexo e Natureza':

        # Subtítulo no Streamlit
        st.subheader("Crimes Domésticos por Sexo e Natureza")

        # Agrupar por SEXO e NATUREZA, somando os totais
        regiao_natureza = violencia_dm.groupby(['SEXO', 'NATUREZA'], as_index=False)['TOTAL'].sum()

        # Ordenar os dados (apenas organiza, mas sem limitar a quantidade)
        regiao_natureza = regiao_natureza.sort_values(['SEXO', 'TOTAL'], ascending=[True, False])

        # Criar o gráfico de barras
        fig = px.bar(
            regiao_natureza,
            x='SEXO',
            y='TOTAL',
            color='NATUREZA',
            title='Crimes por Sexo e Natureza',
            labels={
                'SEXO': 'Sexo',
                'TOTAL': 'Total de Ocorrências',
                'NATUREZA': 'Natureza do Crime'
            },
            barmode='group',  # Barras agrupadas por região
            color_discrete_sequence=px.colors.qualitative.Bold  # Paleta de cores
        )

        # Ajustar layout
        fig.update_layout(
            xaxis_title='Sexo',
            yaxis_title='Total de Ocorrências',
            title_x=0.5,  # Centralizar o título
            template='plotly_white'
        )

        # Exibir o gráfico no Streamlit
        st.plotly_chart(fig)

    # Análise 7: Crimes Por Sexo e Natureza
    elif analysis == 'Mapa de Crimes por Município':
        # Subtítulo no Streamlit
        st.subheader("Mapa de Calor dos Crimes Domésticos em Pernambuco")

        # Carregar o arquivo GeoJSON do mapa de Pernambuco
        with open('pernambuco_municipios.json', 'r') as file:
            geojson_pernambuco = json.load(file)

        # Agrupar os dados por município (ou região)
        dados_agrupados = violencia_dm.groupby('MUNICIPIO', as_index=False).agg({'TOTAL': 'sum'})

        # Adicionar uma coluna com a chave de identificação do GeoJSON (caso necessário)
        # Certifique-se de que os nomes dos municípios no GeoJSON correspondem à coluna MUNICIPIO do DataFrame
        dados_agrupados['MUNICIPIO'] = dados_agrupados[
            'MUNICIPIO'].str.title()  # Normalizar nomes para evitar discrepâncias

        # Criar o mapa utilizando choropleth
        fig = px.choropleth(
            dados_agrupados,
            geojson=geojson_pernambuco,
            locations='MUNICIPIO',  # Nome do município no DataFrame
            featureidkey='properties.name',  # Nome do município no GeoJSON (ajuste conforme necessário)
            color='TOTAL',  # Total de ocorrências
            color_continuous_scale='Viridis',  # Paleta de cores
            title='Mapa de Calor dos Crimes Domésticos',
            labels={'TOTAL': 'Total de Ocorrências'}
        )

        # Ajustar layout do mapa
        fig.update_geos(
            fitbounds="locations",  # Ajustar o zoom ao mapa
            visible=False  # Ocultar linhas de grade
        )

        # Ajustar o layout para ocupar toda a tela
        fig.update_layout(
            title_x=0,  # Centralizar o título
            template='plotly_white',
            margin={"r": 0, "t": 50, "l": 0, "b": 0}  # Reduzir margens externas
        )

        # Exibir o gráfico no Streamlit ocupando toda a largura do container
        st.plotly_chart(fig, use_container_width=True)


# Executar o aplicativo
if __name__ == '__main__':
    check_database()
    visualizacao()