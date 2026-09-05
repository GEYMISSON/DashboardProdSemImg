from pathlib import Path
from datetime import datetime
import math

import pandas as pd
import streamlit as st

from utils.data_utils import (
    localizar_arquivo,
    ler_excel,
    limpar_colunas,
    validar_relatorio_unificado,
    preparar_dados,
    construir_resumo_fornecedores,
    construir_produtos_sem_imagem,
    possui_detalhe,
    calcular_kpis,
    classificacao_cobertura,
    validar_consistencia,
    exportar_csv,
)
from utils.ui import aplicar_estilo, metric_card, status_badge

# Linha acrescentada para carregar relatório do MongoDB Atlas
from utils.mongodb import carregar_relatorio_mongodb

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

st.set_page_config(
    page_title="Dashboard de Imagens",
    page_icon="📷",
    layout="wide",
    initial_sidebar_state="expanded",
)

aplicar_estilo()

st.markdown('<div class="titulo">📷 Painel de Produtos sem Imagens</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitulo">Acompanhamento da cobertura de imagens por fornecedor</div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Controle")
    meta = st.number_input("Meta de cobertura (%)", min_value=0.0, max_value=100.0, value=95.0, step=0.5)
    st.divider()
    st.subheader("Importar relatório")
    upload = st.file_uploader("Relatório unificado (.xls ou .xlsx)", type=["xls", "xlsx"])

    if upload is not None and st.button("🔄 Atualizar Dashboard", use_container_width=True):
        try:
            destino = DATA_DIR / "RelatorioGeralImagens.xls"
            destino.write_bytes(upload.getbuffer())
            st.success("Relatório atualizado com sucesso.")
            st.rerun()
        except Exception as erro:
            st.error(f"Erro ao salvar o relatório: {erro}")

    st.divider()
    st.caption("O relatório deve ser gerado pela query unificada disponível em sql/.")

try:
    df, report_id = carregar_relatorio_mongodb()

    faltantes = validar_relatorio_unificado(df)

    if faltantes:
        st.error("O relatório do MongoDB não possui as colunas obrigatórias:")
        st.write(faltantes)
        st.stop()

except Exception as erro:
    st.error(f"Não foi possível carregar o relatório do MongoDB: {erro}")
    st.stop()

st.caption(
    f"📊 Fonte: MongoDB Atlas | "
    f"Report ID: {report_id} | "
    f"Registros: {len(df):,}".replace(",", ".")
)

resumo = construir_resumo_fornecedores(df, meta)
produtos_sem = construir_produtos_sem_imagem(df)

# Filtros
fornecedores = resumo[["CODFORNEC", "NOME_FORNECEDOR"]].drop_duplicates().sort_values("NOME_FORNECEDOR")
fornecedores["OPCAO"] = fornecedores["CODFORNEC"].astype(int).astype(str) + " - " + fornecedores["NOME_FORNECEDOR"].astype(str)

c1, c2, c3 = st.columns([2, 2, 1])
with c1:
    opcoes = ["TODOS"] + fornecedores["OPCAO"].tolist()
    filtro_fornecedor = st.selectbox("🏢 Fornecedor", opcoes)
with c2:
    filtro_status = st.selectbox("🚦 Status", ["TODOS", "EXCELENTE", "ATENÇÃO", "CRÍTICO"])
with c3:
    ordenar_por = st.selectbox("↕️ Ordenar", ["Menor cobertura", "Maior sem foto", "Maior cobertura", "Maior ativos"])

resumo_filtrado = resumo.copy()
if filtro_fornecedor != "TODOS":
    cod = int(filtro_fornecedor.split(" - ")[0])
    resumo_filtrado = resumo_filtrado[resumo_filtrado["CODFORNEC"] == cod]
if filtro_status != "TODOS":
    resumo_filtrado = resumo_filtrado[resumo_filtrado["STATUS"] == filtro_status]

# KPIs
kpis = calcular_kpis(resumo_filtrado, meta)
col1, col2, col3, col4, col5, col6 = st.columns(6)
metric_card(col1, "Total Produtos", kpis["total_produtos"], "blue")
metric_card(col2, "Produtos Ativos", kpis["total_ativos"], "blue")
metric_card(col3, "Com Foto", kpis["com_foto"], "green")
metric_card(col4, "Sem Foto", kpis["sem_foto"], "red")
metric_card(col5, "Cobertura", kpis["cobertura"], "green" if kpis["cobertura"] >= meta else "orange", percentual=True)
metric_card(col6, f"Faltam p/ {meta:.1f}%", kpis["faltam_meta"], "orange" if kpis["faltam_meta"] > 0 else "green")

st.write("")

# Status geral
classe = classificacao_cobertura(kpis["cobertura"], meta)
diferenca = kpis["cobertura"] - meta
st.markdown(
    f'<div class="info-box">{status_badge(classe)} &nbsp; Cobertura atual: <b>{kpis["cobertura"]:.2f}%</b> &nbsp; | &nbsp; Meta: <b>{meta:.2f}%</b> &nbsp; | &nbsp; Diferença: <b>{diferenca:+.2f} p.p.</b></div>',
    unsafe_allow_html=True,
)

consistencia = validar_consistencia(resumo_filtrado)
if consistencia["ok"]:
    st.success("✓ Dados consistentes: ativos = com foto + sem foto.")
else:
    st.warning(consistencia["mensagem"])

# Gráficos
import plotly.express as px
import plotly.graph_objects as go

g1, g2 = st.columns(2)
with g1:
    graf = resumo_filtrado.copy()
    if not graf.empty:
        graf = graf.sort_values("COBERTURA", ascending=True)
        fig = px.bar(graf, x="COBERTURA", y="NOME_FORNECEDOR", orientation="h", text="COBERTURA", title="Cobertura por fornecedor")
        fig.add_vline(x=meta, line_dash="dash", annotation_text=f"Meta {meta:.0f}%")
        fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
        fig.update_layout(height=520, xaxis_title="Cobertura (%)", yaxis_title="", xaxis_range=[0, 105], margin=dict(l=10,r=30,t=60,b=20))
        st.plotly_chart(fig, use_container_width=True)

with g2:
    pie = pd.DataFrame({"Status": ["Com Foto", "Sem Foto"], "Quantidade": [kpis["com_foto"], kpis["sem_foto"]]})
    fig = px.pie(pie, names="Status", values="Quantidade", hole=0.62, title="Produtos ativos: com foto x sem foto", color="Status", color_discrete_map={"Com Foto": "#16a34a", "Sem Foto": "#dc2626"})
    fig.update_traces(textinfo="percent+value")
    fig.update_layout(height=520, margin=dict(l=10,r=10,t=60,b=20), legend_title="")
    st.plotly_chart(fig, use_container_width=True)

# Ranking
st.subheader("📊 Ranking de Fornecedores")
tabela = resumo_filtrado.copy()
if ordenar_por == "Menor cobertura":
    tabela = tabela.sort_values("COBERTURA")
elif ordenar_por == "Maior sem foto":
    tabela = tabela.sort_values("PRODUTOS_SEM_FOTOS", ascending=False)
elif ordenar_por == "Maior cobertura":
    tabela = tabela.sort_values("COBERTURA", ascending=False)
else:
    tabela = tabela.sort_values("TOTAL_ATIVOS", ascending=False)

tabela_exibicao = tabela[["CODFORNEC", "NOME_FORNECEDOR", "TOTAL_PRODUTOS", "TOTAL_ATIVOS", "PRODUTOS_COM_FOTOS", "PRODUTOS_SEM_FOTOS", "COBERTURA", "STATUS", "FALTAM_META"]].copy()
tabela_exibicao.columns = ["Código", "Fornecedor", "Total Produtos", "Ativos", "Com Foto", "Sem Foto", "Cobertura %", "Status", "Faltam p/ Meta"]
st.dataframe(tabela_exibicao, use_container_width=True, hide_index=True, column_config={"Cobertura %": st.column_config.NumberColumn(format="%.2f%%")})

# Produtos sem imagem
st.subheader("🔎 Produtos sem imagem")
if not possui_detalhe(df):
    st.info("O arquivo atual é um relatório de resumo. Para habilitar a lista detalhada de produtos sem imagem, gere o relatório pela query unificada em sql/RelatorioImagens_Unificado.sql.")
    ps = pd.DataFrame(columns=["CODPROD", "CODFAB", "DESCRICAO", "CODAUXILIAR", "CODAUXILIAR2", "CODFORNEC", "NOME_FORNECEDOR"])
else:
    ps = produtos_sem.copy()
if filtro_fornecedor != "TODOS":
    ps = ps[ps["CODFORNEC"] == int(filtro_fornecedor.split(" - ")[0])]

busca = st.text_input("Pesquisar por código, fabricante, descrição ou EAN", placeholder="Digite para filtrar...")
if busca.strip():
    termo = busca.strip().lower()
    mascara = ps.astype(str).apply(lambda col: col.str.lower().str.contains(termo, na=False)).any(axis=1)
    ps = ps[mascara]

st.caption(f"{len(ps):,} produto(s) sem imagem encontrado(s).".replace(",", "."))
ps_exibicao = ps[["CODPROD", "CODFAB", "DESCRICAO", "CODAUXILIAR", "CODAUXILIAR2", "CODFORNEC", "NOME_FORNECEDOR"]].copy()
ps_exibicao.columns = ["Código Produto", "Código Fabricante", "Descrição", "EAN", "EAN 2", "Código Fornecedor", "Fornecedor"]
st.dataframe(ps_exibicao, use_container_width=True, hide_index=True, height=420)

# Exportações
st.subheader("📥 Exportar")
e1, e2 = st.columns(2)
with e1:
    st.download_button("⬇️ Exportar resumo por fornecedor", data=exportar_csv(tabela), file_name="resumo_imagens_fornecedores.csv", mime="text/csv", use_container_width=True)
with e2:
    st.download_button("⬇️ Exportar produtos sem imagem", data=exportar_csv(ps), file_name="produtos_sem_imagem.csv", mime="text/csv", use_container_width=True)

st.divider()
st.caption("Dashboard de Imagens de Produtos | Relatório unificado")
