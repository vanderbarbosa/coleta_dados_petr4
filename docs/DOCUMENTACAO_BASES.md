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

## 2. Base TRATADA (derivada — filtragem LEVE)

- **Arquivo:** `Mestrado_PETR4/base_textual_petr4_tratada.csv`
- **Filtragem leve (limpeza de qualidade):** remove apenas notícias degeneradas —
  título vazio, com menos de 15 caracteres, ou marcadores de remoção.
  **Não** há filtro temático: todas as 7 categorias são preservadas.
- **Total após limpeza:** 205697 (100.0% da base original)
- **Coluna adicional:** `conjunto` (treino / validacao / teste).

### Notícias por categoria (original → tratada)
| Categoria | Original | Tratada |
|-----------|----------|---------|
| CAT1_Empresa | 64886 | 64882 |
| CAT2_Mercado_Petroleo | 55915 | 55910 |
| CAT3_Geopolitica | 46414 | 46412 |
| CAT7_Macro_Energia | 26412 | 26407 |
| CAT6_Governanca | 6122 | 6121 |
| CAT5_Sancoes_Navegacao | 3620 | 3619 |
| CAT4_Infraestrutura | 2347 | 2346 |

> ✅ A filtragem leve preserva a amplitude temática (incl. geopolítica e macro),
> mantendo a base adequada para a análise de ablação por categoria. O sinal de
> relevância vem do termo da taxonomia usado na captura (Script 02b).

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
| treino | 123030 | 59.8% |
| validacao | 30796 | 15.0% |
| teste | 51871 | 25.2% |

### Notícias por ano × conjunto (confirma todos os anos nos 3 conjuntos)
| Ano | Treino | Validação | Teste |
|-----|--------|-----------|-------|
| 2018 | 17921 | 10715 | 2658 | 4546 |
| 2019 | 20575 | 12324 | 3079 | 5171 |
| 2020 | 19984 | 11961 | 3017 | 5001 |
| 2021 | 23332 | 13964 | 3484 | 5883 |
| 2022 | 36008 | 21466 | 5460 | 9081 |
| 2023 | 28984 | 17349 | 4338 | 7295 |
| 2024 | 26835 | 16039 | 4010 | 6781 |
| 2025 | 32077 | 19212 | 4750 | 8113 |
