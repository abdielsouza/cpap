# Dataset limpo — Matriz Elétrica Brasileira

Fonte principal: Empresa de Pesquisa Energética (EPE), BEN — séries históricas.
Arquivos de origem: Capítulo 8 / Dados_8.8 e Anexo I / Tabela I.1.

## Arquivos

- `geracao_nacional_2011_2025.csv` — geração anual no Brasil por fonte, em GWh.
- `geracao_estadual_2011_2025.csv` — geração anual por região, estado e fonte, em GWh.
- `capacidade_instalada_1974_2025.csv` — capacidade instalada anual por fonte, em MW.
- `matriz_eletrica_2011_2025.csv` — geração + capacidade no período comum.

## Fontes agregadas

- Hidráulica
- Eólica
- Solar fotovoltaica
- Nuclear
- Térmica

`Térmica` usa o registro oficial `Termo Total` da Tabela 8.8. As fontes térmicas detalhadas não são somadas novamente, evitando dupla contagem.

## Tratamento

- Cabeçalhos, notas e linhas não tabulares foram removidos.
- Nomes de colunas e fontes foram padronizados.
- Anos e valores foram convertidos para tipos numéricos.
- Registros agregados `Total` foram excluídos da dimensão de fontes.
- Foram calculadas participação anual, crescimento anual e indicador `renovavel`.
- A geração de 2025 foi validada contra o total oficial da Tabela 8.8; a diferença foi inferior a 0,000001 GWh.

## Observação metodológica

Neste dataset, `renovavel = True` para Hidráulica, Eólica e Solar fotovoltaica. Nuclear permanece separada e não é classificada como renovável.

`crescimento_anual_pct` é nulo no primeiro ano de cada série, pois não existe ano anterior para comparação.
