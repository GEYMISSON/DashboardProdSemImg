import os
import shutil
from pathlib import Path
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# CONFIGURAÇÕES
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ARQUIVO_PADRAO = DATA_DIR / "RelatorioGeralImagens.xls"

DATA_DIR.mkdir(exist_ok=True)


# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================
st.set_page_config(
    page_title="Dashboard de Imagens",
    page_icon="📷",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .main {
        background-color: #f5f7fa;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    .titulo {
        font-size: 32px;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0px;
    }

    .subtitulo {
        font-size: 15px;
        color: #6b7280;
        margin-bottom: 20px;
    }

    .card {
        background-color: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border: 1px solid #e5e7eb;
        min-height: 120px;
    }

    .card-title {
        color: #6b7280;
        font-size: 14px;
        font-weight: 600;
        text-transform: uppercase;
    }

    .card-value {
        color: #111827;
        font-size: 30px;
        font-weight: 700;
        margin-top: 8px;
    }

    .card-green {
        border-left: 5px solid #16a34a;
    }

    .card-red {
        border-left: 5px solid #dc2626;
    }

    .card-blue {
        border-left: 5px solid #2563eb;
    }

    .card-orange {
        border-left: 5px solid #f59e0b;
    }

    .status-excelente {
        color: #15803d;
        font-weight: 700;
    }

    .status-atencao {
        color: #ca8a04;
        font-weight: 700;
    }

    .status-critico {
        color: #dc2626;
        font-weight: 700;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# FUNÇÕES
# ============================================================

def localizar_arquivo():
    """
    Localiza o arquivo RelatorioGeralImagens.xls.
    Também aceita .xlsx.
    """

    arquivos = list(DATA_DIR.glob("*.xls")) + list(DATA_DIR.glob("*.xlsx"))

    if not arquivos:
        return None

    # Prioriza o nome padrão
    for arquivo in arquivos:
        if arquivo.name.lower() == "relatoriogeralimagens.xls":
            return arquivo

    # Caso não exista, pega o arquivo mais recente
    arquivos.sort(key=lambda x: x.stat().st_mtime, reverse=True)

    return arquivos[0]


def ler_excel(caminho):
    """
    Lê arquivos XLS ou XLSX.
    """

    extensao = caminho.suffix.lower()

    if extensao == ".xls":
        df = pd.read_excel(caminho, engine="xlrd")
    else:
        df = pd.read_excel(caminho, engine="openpyxl")

    return df


def limpar_colunas(df):
    """
    Padroniza os nomes das colunas.
    """

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.upper()
    )

    return df


def preparar_dados(df):
    """
    Converte os campos numéricos para o formato correto.
    """

    colunas_numericas = [
        "CODFORNEC",
        "TOTAL_PRODUTOS",
        "TOTAL_ATIVOS",
        "PRODUTOS_COM_FOTOS",
        "PRODUTOS_SEM_FOTOS",
        "PERC_COM_FOTOS",
        "PERC_SEM_FOTOS"
    ]

    for coluna in colunas_numericas:

        if coluna in df.columns:
            df[coluna] = pd.to_numeric(
                df[coluna],
                errors="coerce"
            ).fillna(0)

    return df


def validar_planilha(df):
    """
    Verifica se as colunas necessárias existem.
    """

    obrigatorias = [
        "CODFORNEC",
        "NOME_FORNECEDOR",
        "TOTAL_PRODUTOS",
        "TOTAL_ATIVOS",
        "PRODUTOS_COM_FOTOS",
        "PRODUTOS_SEM_FOTOS",
        "PERC_COM_FOTOS",
        "PERC_SEM_FOTOS"
    ]

    faltantes = [
        coluna
        for coluna in obrigatorias
        if coluna not in df.columns
    ]

    return faltantes


def formatar_numero(valor):
    """
    Formata números no padrão brasileiro.
    """

    return f"{valor:,.0f}".replace(",", ".")


def formatar_percentual(valor):
    """
    Formata percentual.
    """

    return f"{valor:.2f}%".replace(".", ",")


def classificacao_cobertura(valor):

    if valor >= 95:
        return "EXCELENTE"

    if valor >= 80:
        return "ATENÇÃO"

    return "CRÍTICO"


def salvar_upload(arquivo):

    """
    Substitui os arquivos anteriores e salva somente
    o relatório atual.
    """

    # Remove XLS/XLSX antigos
    for arquivo_antigo in DATA_DIR.glob("*.xls"):
        arquivo_antigo.unlink()

    for arquivo_antigo in DATA_DIR.glob("*.xlsx"):
        arquivo_antigo.unlink()

    destino = DATA_DIR / "RelatorioGeralImagens.xls"

    with open(destino, "wb") as f:
        f.write(arquivo.getbuffer())

    return destino


# ============================================================
# TÍTULO
# ============================================================

st.markdown(
    '<div class="titulo">📷 Dashboard de Imagens de Produtos</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitulo">'
    'Acompanhamento de cobertura de imagens por fornecedor'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ Controle")

    st.subheader("Importar relatório")

    arquivo_upload = st.file_uploader(
        "Envie o RelatorioGeralImagens.xls",
        type=["xls", "xlsx"]
    )

    if arquivo_upload is not None:

        if st.button(
            "🔄 Atualizar Dashboard",
            use_container_width=True
        ):

            try:

                caminho = salvar_upload(arquivo_upload)

                st.success(
                    f"Arquivo atualizado:\n{caminho.name}"
                )

                st.rerun()

            except Exception as erro:

                st.error(
                    f"Erro ao salvar arquivo: {erro}"
                )


# ============================================================
# LOCALIZA ARQUIVO
# ============================================================

arquivo = localizar_arquivo()

if arquivo is None:

    st.warning(
        "Nenhum relatório encontrado."
    )

    st.info(
        "Coloque o arquivo RelatorioGeralImagens.xls "
        "dentro da pasta 'data' ou faça o upload pelo menu lateral."
    )

    st.stop()


# ============================================================
# LEITURA
# ============================================================

try:

    df = ler_excel(arquivo)

    df = limpar_colunas(df)

    faltantes = validar_planilha(df)

    if faltantes:

        st.error(
            "O relatório não possui as seguintes colunas:"
        )

        for coluna in faltantes:
            st.write(f"- {coluna}")

        st.stop()

    df = preparar_dados(df)

except Exception as erro:

    st.error(
        f"Não foi possível ler o arquivo Excel: {erro}"
    )

    st.stop()


# ============================================================
# DATA DE ATUALIZAÇÃO
# ============================================================

data_atualizacao = datetime.fromtimestamp(
    arquivo.stat().st_mtime
)

st.caption(
    f"📄 Arquivo: {arquivo.name} | "
    f"Atualizado em: {data_atualizacao.strftime('%d/%m/%Y %H:%M')}"
)


# ============================================================
# FILTRO DE FORNECEDOR
# ============================================================

fornecedores = df[
    ["CODFORNEC", "NOME_FORNECEDOR"]
].drop_duplicates()

fornecedores["DESCRICAO"] = (
    fornecedores["CODFORNEC"].astype(int).astype(str)
    + " - "
    + fornecedores["NOME_FORNECEDOR"].astype(str)
)

opcoes = ["TODOS"] + fornecedores["DESCRICAO"].tolist()

filtro = st.selectbox(
    "🏢 Fornecedor",
    opcoes
)


if filtro != "TODOS":

    codigo_selecionado = int(
        filtro.split(" - ")[0]
    )

    dados = df[
        df["CODFORNEC"] == codigo_selecionado
    ].copy()

else:

    dados = df.copy()


# ============================================================
# CÁLCULOS DOS KPIs
# ============================================================

total_produtos = dados["TOTAL_PRODUTOS"].sum()

total_ativos = dados["TOTAL_ATIVOS"].sum()

produtos_com_fotos = dados["PRODUTOS_COM_FOTOS"].sum()

produtos_sem_fotos = dados["PRODUTOS_SEM_FOTOS"].sum()


if total_ativos > 0:

    cobertura = (
        produtos_com_fotos
        / total_ativos
        * 100
    )

    percentual_sem_foto = (
        produtos_sem_fotos
        / total_ativos
        * 100
    )

else:

    cobertura = 0
    percentual_sem_foto = 0


# ============================================================
# CARDS
# ============================================================

col1, col2, col3, col4, col5 = st.columns(5)


with col1:

    st.markdown(
        f"""
        <div class="card card-blue">
            <div class="card-title">
                Total Produtos
            </div>
            <div class="card-value">
                {formatar_numero(total_produtos)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col2:

    st.markdown(
        f"""
        <div class="card card-blue">
            <div class="card-title">
                Produtos Ativos
            </div>
            <div class="card-value">
                {formatar_numero(total_ativos)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col3:

    st.markdown(
        f"""
        <div class="card card-green">
            <div class="card-title">
                Com Foto
            </div>
            <div class="card-value">
                {formatar_numero(produtos_com_fotos)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col4:

    st.markdown(
        f"""
        <div class="card card-red">
            <div class="card-title">
                Sem Foto
            </div>
            <div class="card-value">
                {formatar_numero(produtos_sem_fotos)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col5:

    classe = classificacao_cobertura(cobertura)

    if classe == "EXCELENTE":
        cor = "#16a34a"
    elif classe == "ATENÇÃO":
        cor = "#f59e0b"
    else:
        cor = "#dc2626"

    st.markdown(
        f"""
        <div class="card card-orange">
            <div class="card-title">
                Cobertura
            </div>
            <div class="card-value" style="color:{cor}">
                {formatar_percentual(cobertura)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


st.write("")


# ============================================================
# GRÁFICOS
# ============================================================

col_grafico1, col_grafico2 = st.columns(2)


# ------------------------------------------------------------
# GRÁFICO DE COBERTURA
# ------------------------------------------------------------

with col_grafico1:

    if filtro == "TODOS":

        grafico = dados.copy()

        grafico["COBERTURA"] = (
            grafico["PRODUTOS_COM_FOTOS"]
            / grafico["TOTAL_ATIVOS"]
            * 100
        )

        grafico = grafico.sort_values(
            "COBERTURA",
            ascending=True
        )

        fig = px.bar(
            grafico,
            x="COBERTURA",
            y="NOME_FORNECEDOR",
            orientation="h",
            text="COBERTURA",
            title="Cobertura de Imagens por Fornecedor",
            color="COBERTURA",
            color_continuous_scale=[
                "#dc2626",
                "#f59e0b",
                "#16a34a"
            ]
        )

        fig.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="outside"
        )

        fig.update_layout(
            height=650,
            xaxis_title="Cobertura (%)",
            yaxis_title="",
            coloraxis_showscale=False,
            margin=dict(l=20, r=30, t=60, b=20)
        )

        fig.update_xaxes(
            range=[0, 105]
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info(
            "Selecione 'TODOS' para visualizar "
            "o comparativo entre fornecedores."
        )


# ------------------------------------------------------------
# GRÁFICO COM FOTO X SEM FOTO
# ------------------------------------------------------------

with col_grafico2:

    valores = pd.DataFrame({
        "Status": [
            "Com Foto",
            "Sem Foto"
        ],
        "Quantidade": [
            produtos_com_fotos,
            produtos_sem_fotos
        ]
    })

    fig_pizza = px.pie(
        valores,
        names="Status",
        values="Quantidade",
        hole=0.60,
        color="Status",
        color_discrete_map={
            "Com Foto": "#16a34a",
            "Sem Foto": "#dc2626"
        },
        title="Produtos com Foto x Sem Foto"
    )

    fig_pizza.update_traces(
        textinfo="percent+value",
        textfont_size=14
    )

    fig_pizza.update_layout(
        height=500,
        margin=dict(l=20, r=20, t=60, b=20),
        legend_title=""
    )

    st.plotly_chart(
        fig_pizza,
        use_container_width=True
    )


# ============================================================
# TABELA DE FORNECEDORES
# ============================================================

if filtro == "TODOS":

    st.subheader(
        "📊 Resumo por Fornecedor"
    )

    tabela = dados.copy()

    tabela["COBERTURA"] = (
        tabela["PRODUTOS_COM_FOTOS"]
        / tabela["TOTAL_ATIVOS"]
        * 100
    )

    tabela["STATUS"] = tabela["COBERTURA"].apply(
        classificacao_cobertura
    )

    tabela = tabela[
        [
            "CODFORNEC",
            "NOME_FORNECEDOR",
            "TOTAL_PRODUTOS",
            "TOTAL_ATIVOS",
            "PRODUTOS_COM_FOTOS",
            "PRODUTOS_SEM_FOTOS",
            "COBERTURA",
            "STATUS"
        ]
    ].copy()

    tabela.columns = [
        "Código",
        "Fornecedor",
        "Total Produtos",
        "Ativos",
        "Com Foto",
        "Sem Foto",
        "Cobertura %",
        "Status"
    ]

    st.dataframe(
        tabela,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Cobertura %": st.column_config.NumberColumn(
                format="%.2f%%"
            )
        }
    )


# ============================================================
# FORNECEDOR SELECIONADO
# ============================================================

else:

    st.subheader(
        f"🏢 Detalhes - {filtro}"
    )

    registro = dados.iloc[0]

    cobertura_fornecedor = (
        registro["PRODUTOS_COM_FOTOS"]
        / registro["TOTAL_ATIVOS"]
        * 100
        if registro["TOTAL_ATIVOS"] > 0
        else 0
    )

    col_a, col_b, col_c = st.columns(3)

    with col_a:

        st.metric(
            "Produtos Ativos",
            formatar_numero(
                registro["TOTAL_ATIVOS"]
            )
        )

    with col_b:

        st.metric(
            "Produtos Sem Foto",
            formatar_numero(
                registro["PRODUTOS_SEM_FOTOS"]
            )
        )

    with col_c:

        st.metric(
            "Cobertura",
            formatar_percentual(
                cobertura_fornecedor
            )
        )


# ============================================================
# DOWNLOAD DO RELATÓRIO ATUAL
# ============================================================

st.subheader(
    "📥 Exportar dados"
)

csv = dados.to_csv(
    index=False,
    sep=";",
    encoding="utf-8-sig"
)

st.download_button(
    label="⬇️ Baixar dados filtrados",
    data=csv,
    file_name="dashboard_imagens.csv",
    mime="text/csv"
)


# ============================================================
# RODAPÉ
# ============================================================

st.divider()

st.caption(
    "Dashboard de Imagens de Produtos | "
    "Fonte: RelatorioGeralImagens.xls"
)