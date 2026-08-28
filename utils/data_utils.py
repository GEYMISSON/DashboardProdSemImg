from pathlib import Path
import math
import pandas as pd

OBRIGATORIAS_RESUMO = [
    "CODFORNEC", "NOME_FORNECEDOR", "TOTAL_PRODUTOS", "TOTAL_ATIVOS",
    "PRODUTOS_COM_FOTOS", "PRODUTOS_SEM_FOTOS", "PERC_COM_FOTOS",
    "PERC_SEM_FOTOS"
]

OBRIGATORIAS_DETALHE = [
    "CODPROD", "CODFAB", "DESCRICAO", "CODAUXILIAR", "CODAUXILIAR2",
    "ATIVO", "STATUS_IMAGEM"
]

NUMERICAS = [
    "CODFORNEC", "TOTAL_PRODUTOS", "TOTAL_ATIVOS", "PRODUTOS_COM_FOTOS",
    "PRODUTOS_SEM_FOTOS", "PERC_COM_FOTOS", "PERC_SEM_FOTOS", "CODPROD",
    "CODAUXILIAR", "CODAUXILIAR2"
]


def localizar_arquivo(data_dir: Path):
    arquivos = list(data_dir.glob("*.xls")) + list(data_dir.glob("*.xlsx"))
    if not arquivos:
        return None
    for nome in ["RelatorioGeralImagens.xls", "RelatorioGeralImagens.xlsx"]:
        for arquivo in arquivos:
            if arquivo.name.lower() == nome.lower():
                return arquivo
    return max(arquivos, key=lambda p: p.stat().st_mtime)


def ler_excel(caminho: Path):
    engine = "xlrd" if caminho.suffix.lower() == ".xls" else "openpyxl"
    return pd.read_excel(caminho, engine=engine)


def limpar_colunas(df):
    df = df.copy()
    df.columns = df.columns.astype(str).str.strip().str.upper()
    return df


def validar_relatorio_unificado(df):
    return [c for c in OBRIGATORIAS_RESUMO if c not in df.columns]

def possui_detalhe(df):
    return all(c in df.columns for c in OBRIGATORIAS_DETALHE)


def preparar_dados(df):
    df = df.copy()
    for coluna in NUMERICAS:
        if coluna in df.columns:
            df[coluna] = pd.to_numeric(df[coluna], errors="coerce").fillna(0)
    if "NOME_FORNECEDOR" in df.columns:
        df["NOME_FORNECEDOR"] = df["NOME_FORNECEDOR"].fillna("SEM FORNECEDOR").astype(str).str.strip()
    if "DESCRICAO" in df.columns:
        df["DESCRICAO"] = df["DESCRICAO"].fillna("").astype(str).str.strip()
    return df


def construir_resumo_fornecedores(df, meta=95.0):
    cols = ["CODFORNEC", "NOME_FORNECEDOR", "TOTAL_PRODUTOS", "TOTAL_ATIVOS", "PRODUTOS_COM_FOTOS", "PRODUTOS_SEM_FOTOS", "PERC_COM_FOTOS", "PERC_SEM_FOTOS"]
    resumo = df[cols].drop_duplicates(subset=["CODFORNEC"]).copy()
    resumo["COBERTURA"] = resumo["PRODUTOS_COM_FOTOS"].div(resumo["TOTAL_ATIVOS"].replace(0, pd.NA)).mul(100).fillna(0)
    resumo["PERC_SEM_FOTOS_CALCULADO"] = resumo["PRODUTOS_SEM_FOTOS"].div(resumo["TOTAL_ATIVOS"].replace(0, pd.NA)).mul(100).fillna(0)

    # Campos derivados usados pela interface. Eles são calculados aqui para
    # que o Dashboard funcione tanto com o relatório unificado quanto com
    # relatórios de resumo que não tragam esses campos prontos.
    resumo["STATUS"] = resumo["COBERTURA"].apply(lambda valor: classificacao_cobertura(valor, meta))
    alvo = (resumo["TOTAL_ATIVOS"] * float(meta) / 100).apply(math.ceil)
    resumo["FALTAM_META"] = (alvo - resumo["PRODUTOS_COM_FOTOS"]).clip(lower=0).astype(int)

    return resumo


def construir_produtos_sem_imagem(df):
    if not possui_detalhe(df):
        return pd.DataFrame(columns=["CODPROD", "CODFAB", "DESCRICAO", "CODAUXILIAR", "CODAUXILIAR2", "CODFORNEC", "NOME_FORNECEDOR"])
    ativo = pd.to_numeric(df["ATIVO"], errors="coerce").fillna(0).eq(1)
    sem_foto = df["STATUS_IMAGEM"].astype(str).str.upper().eq("SEM FOTO")
    return df[ativo & sem_foto].copy()


def calcular_kpis(resumo, meta):
    total_produtos = int(resumo["TOTAL_PRODUTOS"].sum())
    total_ativos = int(resumo["TOTAL_ATIVOS"].sum())
    com_foto = int(resumo["PRODUTOS_COM_FOTOS"].sum())
    sem_foto = int(resumo["PRODUTOS_SEM_FOTOS"].sum())
    cobertura = (com_foto / total_ativos * 100) if total_ativos else 0
    alvo = math.ceil(total_ativos * meta / 100) if total_ativos else 0
    faltam = max(0, alvo - com_foto)
    return {"total_produtos": total_produtos, "total_ativos": total_ativos, "com_foto": com_foto, "sem_foto": sem_foto, "cobertura": cobertura, "faltam_meta": faltam}


def classificacao_cobertura(valor, meta=95):
    if valor >= meta:
        return "EXCELENTE"
    if valor >= max(0, meta - 15):
        return "ATENÇÃO"
    return "CRÍTICO"


def validar_consistencia(resumo):
    ativos = int(resumo["TOTAL_ATIVOS"].sum())
    soma = int(resumo["PRODUTOS_COM_FOTOS"].sum() + resumo["PRODUTOS_SEM_FOTOS"].sum())
    if ativos == soma:
        return {"ok": True, "mensagem": "Dados consistentes."}
    return {"ok": False, "mensagem": f"⚠️ Inconsistência: ativos={ativos:,} e com foto + sem foto={soma:,}.".replace(",", ".")}


def exportar_csv(df):
    return df.to_csv(index=False, sep=";", encoding="utf-8-sig")
