# 📷 Dashboard de Imagens de Produtos

Dashboard em Streamlit para acompanhar a cobertura de imagens dos produtos por fornecedor e identificar os produtos ativos que estão sem foto.

## 1. Relatório unificado

O projeto usa uma única query Oracle, localizada em:

`sql/RelatorioImagens_Unificado.sql`

Ela reúne em uma mesma saída:

- resumo por fornecedor;
- total de produtos;
- total de produtos ativos;
- produtos com foto;
- produtos sem foto;
- percentuais;
- dados individuais dos produtos;
- situação do produto: INATIVO, COM FOTO ou SEM FOTO.

### Por que a query retorna uma linha por produto?

SQL normalmente retorna um único conjunto tabular. Para manter o resumo e o detalhe no mesmo relatório, os totais do fornecedor são repetidos nas linhas dos produtos daquele fornecedor. O Dashboard remove as duplicidades para montar os KPIs e usa as linhas de produto para a lista de itens sem imagem.

## 2. Como gerar o relatório

Execute `sql/RelatorioImagens_Unificado.sql` no ambiente Oracle/WinThor e exporte o resultado para:

`data/RelatorioGeralImagens.xls`

Também é aceito `.xlsx`.

## 3. Como executar

No Windows, dê duplo clique em:

`iniciar_dashboard.bat`

Ou manualmente:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## 4. Funcionalidades

- KPIs gerais;
- meta de cobertura configurável;
- quantidade de produtos que faltam para atingir a meta;
- classificação Excelente / Atenção / Crítico;
- ranking de fornecedores;
- cobertura por fornecedor;
- com foto x sem foto;
- filtro por fornecedor;
- filtro por status;
- pesquisa de produtos sem imagem;
- exportação do resumo;
- exportação dos produtos sem imagem;
- validação de consistência: ativos = com foto + sem foto.

## 5. Observação sobre o arquivo XLS

Para `.xls`, o projeto usa `xlrd`. Para `.xlsx`, usa `openpyxl`.

## 6. GitHub

Não envie `.venv/`, relatórios da empresa ou arquivos de exportação. O `.gitignore` já está preparado para isso.
