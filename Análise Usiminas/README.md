# Usiminas — recuperação operacional e financeira

Projeto de análise de dados baseado na planilha **Base de Dados para Modelagem 2T26.xlsx**.

## Pergunta de pesquisa

> Quais fatores operacionais e financeiros acompanharam a recuperação da rentabilidade da Usiminas entre o 3T25 e o 2T26?

## O que foi entregue

- ETL reproduzível em `src/etl.py`;
- dados tratados em CSV/long format em `data/processed/`;
- análise focada em 1T25–2T26;
- gráficos em `outputs/figures/`;
- relatório final em `reports/relatorio_usiminas.pdf`;
- dashboard Streamlit em `app/app.py`;
- consulta DuckDB em `sql/recovery.sql`;
- testes automatizados em `tests/`;
- dicionário de dados em `data/processed/DATA_DICTIONARY.md`.

## Como testar

### 1. Criar ambiente

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

No Windows, use `.venv\\Scripts\\activate`.

### 2. Reproduzir o ETL

```bash
python -m src
```

Isso recria os CSVs derivados da planilha original.

### 3. Rodar os testes

```bash
pytest
```

### 4. Abrir o dashboard

```bash
streamlit run app/app.py
```

## Estrutura

```text
usiminas-analysis/
├── data/raw/                 # fonte original
├── data/processed/           # dados normalizados
├── src/                      # ETL e análise
├── sql/                      # consultas
├── app/                      # dashboard
├── tests/                    # testes
├── outputs/figures/          # gráficos
└── reports/                  # relatório PDF
```

## Escopo metodológico

O estudo é **descritivo e exploratório**. Não há afirmação de causalidade. A correlação calculada na janela de seis trimestres serve apenas para orientar hipóteses futuras.

## Próximos passos sugeridos

1. incorporar preços de aço e câmbio;
2. decompor preço × volume × mix;
3. construir uma série histórica maior para regressões simples;
4. comparar a Usiminas com outras siderúrgicas;
5. investigar especificamente o evento do 3T25;
6. adicionar dados de produção/capacidade ao dashboard.
