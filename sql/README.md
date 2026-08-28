# Query unificada

Use `RelatorioImagens_Unificado.sql` no Oracle/WinThor.

A query foi desenhada para entregar **um único relatório tabular**. Ela mantém os dados do produto em cada linha e repete os totais do respectivo fornecedor. Isso permite que o Streamlit reconstrua:

- resumo por fornecedor, sem somar várias vezes os mesmos totais;
- KPIs gerais;
- lista de produtos ativos sem imagem.

Não é recomendado simplesmente fazer `UNION ALL` entre as duas queries originais, porque elas possuem estruturas e granularidades diferentes e isso dificultaria o consumo pelo Dashboard.
