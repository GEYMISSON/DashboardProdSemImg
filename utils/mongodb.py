import os

import pandas as pd
from pymongo import MongoClient
from pymongo.server_api import ServerApi


BANCO = "DashboardProd"
COLLECTION = "relatorios"


def obter_uri_mongodb():
    """
    Obtém a URI do MongoDB Atlas através da variável de ambiente MONGO_URI.
    """
    uri = os.getenv("MONGO_URI")

    if not uri:
        raise RuntimeError(
            "A variável de ambiente MONGO_URI não foi encontrada."
        )

    return uri


def conectar_mongodb():
    """
    Cria e retorna uma conexão com o MongoDB Atlas.
    """
    uri = obter_uri_mongodb()

    client = MongoClient(
        uri,
        server_api=ServerApi("1"),
    )

    # Testa a conexão
    client.admin.command("ping")

    return client


def obter_collection():
    """
    Retorna a collection 'relatorios' do banco 'DashboardProd'.
    """
    client = conectar_mongodb()

    db = client[BANCO]
    collection = db[COLLECTION]

    return client, collection


def obter_report_id_mais_recente(collection):
    """
    Localiza o report_id da importação mais recente.
    """

    documento = collection.find_one(
        {},
        {
            "_id": 0,
            "report_id": 1,
            "importacao.data": 1,
        },
        sort=[("importacao.data", -1)],
    )

    if documento is None:
        raise RuntimeError(
            "Nenhum relatório encontrado na collection 'relatorios'."
        )

    report_id = documento.get("report_id")

    if not report_id:
        raise RuntimeError(
            "Não foi possível identificar o report_id do relatório."
        )

    return report_id


def carregar_relatorio_mongodb(report_id=None):
    """
    Carrega o relatório do MongoDB Atlas e devolve um DataFrame
    com as mesmas colunas utilizadas atualmente pelo dashboard.
    """

    client = None

    try:
        client, collection = obter_collection()

        if report_id is None:
            report_id = obter_report_id_mais_recente(collection)

        documentos = collection.find(
            {"report_id": report_id},
            {
                "_id": 0,
                "fornecedor": 1,
                "resumo_fornecedor": 1,
                "produto": 1,
                "report_id": 1,
                "importacao": 1,
            },
        )

        registros = []

        for documento in documentos:

            fornecedor = documento.get("fornecedor", {})
            resumo = documento.get("resumo_fornecedor", {})
            produto = documento.get("produto", {})

            registros.append(
                {
                    "CODPROD": produto.get("codigo"),
                    "CODFAB": produto.get("codigo_fabricante"),
                    "DESCRICAO": produto.get("descricao"),
                    "CODAUXILIAR": produto.get("codigo_auxiliar"),
                    "CODAUXILIAR2": produto.get("codigo_auxiliar_2"),
                    "CODFORNEC": fornecedor.get("codigo"),
                    "NOME_FORNECEDOR": fornecedor.get("nome"),
                    "TOTAL_PRODUTOS": resumo.get("total_produtos"),
                    "TOTAL_ATIVOS": resumo.get("total_ativos"),
                    "PRODUTOS_COM_FOTOS": resumo.get("produtos_com_fotos"),
                    "PRODUTOS_SEM_FOTOS": resumo.get("produtos_sem_fotos"),
                    "PERC_COM_FOTOS": resumo.get("perc_com_fotos"),
                    "PERC_SEM_FOTOS": resumo.get("perc_sem_fotos"),
                    "ATIVO": produto.get("ativo"),
                    "STATUS_IMAGEM": produto.get("status_imagem"),
                }
            )

        df = pd.DataFrame(registros)

        if df.empty:
            raise RuntimeError(
                f"Nenhum registro encontrado para o report_id: {report_id}"
            )

        return df, report_id

    finally:
        if client is not None:
            client.close()


def contar_registros_mongodb(report_id=None):
    """
    Retorna a quantidade de documentos do relatório.
    """

    client = None

    try:
        client, collection = obter_collection()

        if report_id is None:
            report_id = obter_report_id_mais_recente(collection)

        quantidade = collection.count_documents(
            {"report_id": report_id}
        )

        return quantidade, report_id

    finally:
        if client is not None:
            client.close()