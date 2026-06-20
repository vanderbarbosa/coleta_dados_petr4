# Documentação das Bases de Dados — Corpus PETR4

*Gerado automaticamente pelo `02c_preparar_base_treino_teste_validacao.py`.*

## 1. Base ORIGINAL (intacta)

- **Arquivo:** `Mestrado_PETR4/base_textual_petr4_wordpress_2018_2025.csv`
- **Total de notícias:** 205716
- **Período:** 2018–2025
- **Timestamp:** 100% das notícias têm hora exata de publicação (horário de Brasília).
- **Lead-Lag:** 26.4% das notícias foram publicadas após o fechamento da B3 (≥17h) e são realocadas ao pregão seguinte.
- **Coleta:** Script 02b (WordPress REST API) de 5 portais (InfoMoney, Exame, Money Times, Petronotícias, Poder360), taxonomia de 7 categorias.
- **Status:** NUNCA é modificada. Todas as bases abaixo são derivadas dela.

### Distribuição por ano (base original)
| Ano | Notícias |
|-----|----------|
| 2018 | 17921 |
| 2019 | 20575 |
| 2020 | 19984 |
| 2021 | 23332 |
| 2022 | 36008 |
| 2023 | 28984 |
| 2024 | 26835 |
| 2025 | 32077 |

## 2. Base FILTRADA (derivada)

- **Arquivo:** `Mestrado_PETR4/base_textual_petr4_filtrada.csv`
- **Filtro:** mantém notícias cujo título ou resumo contém termos de relevância
  (petrobras, petr4, petr3, petroleira, petróleo, petroleo, brent, wti…).
- **Total após filtro:** 41635 (20.2% da base original)
- **Coluna adicional:** `conjunto` (treino / validacao / teste).

### Impacto do filtro por categoria (original → filtrada)
| Categoria | Original | Filtrada |
|-----------|----------|----------|
| CAT1_Empresa | 64886 | 29523 |
| CAT2_Mercado_Petroleo | 55915 | 9551 |
| CAT3_Geopolitica | 46414 | 470 |
| CAT7_Macro_Energia | 26412 | 870 |
| CAT6_Governanca | 6122 | 229 |
| CAT5_Sancoes_Navegacao | 3620 | 356 |
| CAT4_Infraestrutura | 2347 | 636 |

> ⚠️ O filtro reduz fortemente as categorias exógenas (geopolítica, macro), pois
> essas notícias raramente citam "petróleo/Petrobras" no título. Para a análise
> de ablação por categoria, considere usar também a base original (não filtrada).

## 3. Split Temporal Treino / Validação / Teste

- **Proporção:** 60% treino / 15% validação / 25% teste.
- **Estratégia:** estratificado por ano e cronológico dentro do ano. Em cada ano,
  os primeiros 60% dos dias vão para treino, os 15% seguintes para validação
  e os 25% finais (mais recentes) para teste. Um dia inteiro nunca é dividido
  entre conjuntos — garante ausência de *data leakage* e representação de todos
  os anos (regimes de mercado) nos três conjuntos.
- **Mapa de datas:** `Mestrado_PETR4/definicao_split_temporal.csv` (Data → conjunto),
  aplicável aos dias de pregão no Script 04 para manter consistência.

### Distribuição global
| Conjunto | Notícias | % |
|----------|----------|---|
| treino | 24909 | 59.8% |
| validacao | 6230 | 15.0% |
| teste | 10496 | 25.2% |

### Notícias por ano × conjunto (confirma todos os anos nos 3 conjuntos)
| Ano | Treino | Validação | Teste |
|-----|--------|-----------|-------|
| 2018 | 17921 | 2774 | 705 | 1164 |
| 2019 | 20575 | 2780 | 692 | 1186 |
| 2020 | 19984 | 2731 | 680 | 1143 |
| 2021 | 23332 | 3091 | 776 | 1309 |
| 2022 | 36008 | 4435 | 1104 | 1859 |
| 2023 | 28984 | 3532 | 875 | 1484 |
| 2024 | 26835 | 2890 | 710 | 1221 |
| 2025 | 32077 | 2676 | 688 | 1130 |
