# 📷 Dashboard de Imagens de Produtos

Dashboard para acompanhamento da cobertura de imagens dos produtos por fornecedor.

O sistema lê o relatório:

`RelatorioGeralImagens.xls`

gerado pela rotina 860 do WinThor.

## Funcionalidades

- Total de produtos
- Total de produtos ativos
- Produtos com foto
- Produtos sem foto
- Percentual de cobertura
- Percentual sem foto
- Comparativo por fornecedor
- Filtro por fornecedor
- Gráfico de cobertura
- Gráfico com foto x sem foto
- Exportação dos dados filtrados
- Atualização através de novo arquivo Excel

## Estrutura

```text
DashboardImagens/
│
├── app.py
├── requirements.txt
├── iniciar_dashboard.bat
├── README.md
├── .gitignore
│
└── data/
    └── RelatorioGeralImagens.xls