# Análise da Matriz Energética Brasileira

## O que é este projeto?

Este projeto é uma análise exploratória que apresenta um estudo analítico sobre a transformação da matriz energética brasileira ao longo dos anos (2011 - 2025). O estudo busca explorar a evolução das principais fontes de geração de energia elétrica pelo Brasil, quantificando a participação de cada uma na produção de energia no Brasil ao longo dos anos e explicando seus impactos.

## Como executar a EDA?

Para executar o projeto do zero, você deverá instalar as dependências contidas em `pyproject.toml` e executar o script python em `src/eda.py`, que produzirá os resultados da análise na pasta `outputs`.

## Estrutura do projeto

- **data:**
    - **article:** Os arquivos finais do artigo da análise.
    - **processed:** Os datasets já separados, processados, limpos e convertidos em CSV.
- **datasets:** Os datasets originais com os dados brutos.
- **outputs:**
    - **figures:** As figuras produzidas pelo script.
    - **tables:** As tabelas produzidas pelo script.
- **src**: Os scripts Python que contém a lógica da análise.