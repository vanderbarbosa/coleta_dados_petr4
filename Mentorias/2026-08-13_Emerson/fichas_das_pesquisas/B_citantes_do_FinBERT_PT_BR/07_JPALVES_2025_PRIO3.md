# 07 · jp-alves (2025) — Sentiment-Driven Returns: PRIO3 (PetroRio) 2015–2024

> ⚠️ **Não é trabalho acadêmico nem cita Santos.** É um repositório público de GitHub.
> Está incluído por uma razão simples: **é o pipeline público mais parecido com o nosso** —
> notícias de petróleo em português, ação brasileira do setor, FinBERT-PT-BR, estudo de evento,
> causalidade de Granger — e **o código está inteiro disponível**, o que nenhum dos trabalhos
> acadêmicos oferece.
>
> Também é o trabalho cujos **achados mais convergem com os nossos**, o que é uma forma
> independente de validação.
>
> Fonte: repositório clonado e código lido integralmente em 04/08/2026.

---

## 1. Ficha

| Campo | Valor |
|---|---|
| **Título** | Sentiment-Driven Returns: PRIO3 (PetroRio) 2015–2024 |
| **Autor** | `jp-alves` (GitHub) |
| **Repositório** | https://github.com/jp-alves/prio3-sentiment |
| **Data** | Criado e publicado em **27/06/2025** |
| **Licença** | Declarada no repositório (`LICENSE`) |
| **Natureza** | Projeto pessoal / portfólio — **não revisado por pares** |
| **Ativo** | **PRIO3** (PetroRio) — petroleira independente brasileira |
| **Período** | 2015–2024 |
| **Código local** | `../_codigos/prio3_*.py` (8 arquivos baixados) |

> ⚠️ **Como usar isto na dissertação.** Não é fonte citável como literatura revisada por pares.
> Pode ser mencionado como **referência de implementação** ou em nota de rodapé, ou simplesmente
> usado internamente como validação de decisões técnicas. **Não construir argumento sobre ele.**

---

## 2. Objetivo

Pergunta declarada no README:

> *"Brazil's independent oil producer PetroRio S.A. (ticker PRIO3) moved from penny-stock to
> Ibovespa heavyweight in less than a decade. During that climb its newsflow exploded — earnings
> beats, field acquisitions, OPEC shocks, regulatory twists. **Can the tone of those headlines
> help explain (or even predict) the stock's price action?**"*

**É, palavra por palavra, uma variante da nossa pergunta de pesquisa**, com PRIO3 no lugar de
PETR4.

---

## 3. Dados

| Item | Valor |
|---|---|
| **Notícias** | Coletadas via **GNews** (`gnews`), consulta `'PetroRio OR PRIO3'`, `language='pt'`, `country='BR'` |
| **Estratégia de coleta** | **Iteração mês a mês** ao longo de 10 anos, com `time.sleep(2)` entre requisições para evitar bloqueio |
| **Preços** | **`yfinance`** — fechamento e abertura da B3 |
| **Período** | 2015-01-01 a 2024-12-31 |
| **Unidade de análise** | **Manchete** (`title`) — igual à nossa |

### 3.1 Limpeza de notícias — diretamente comparável à nossa

```python
# Remove o sufixo "- Publisher" ou "| Publisher" das manchetes do Google News
df["title"] = df["title"].str.replace(
    r"\s*[-|]\s*[A-Za-zÀ-ÿ0-9&.\- ]+$", "", regex=True, flags=re.I)

# Filtro por palavras-chave do contexto de E&P de petróleo brasileiro
PRIO_WORDS = [
    "petro ?rio", "prior3", "prio3", "produção", "barris", "campo",
    "licen[çc]a", "fpsos?", "manati", "polo", r"\banp\b",
    "reservas?", "lifting cost", "regula[çc][aã]o", "combustível",
    "petr[oó]leo", "gasolina", "leil[aã]o", "investimento"
]
df = df[df["title"].str.contains(pattern) | df["description"].str.contains(pattern, na=False)]

# Deduplicação por hash MD5 da URL
df["url_hash"] = df["url"].apply(lambda u: hashlib.md5(str(u).encode()).hexdigest())
df = df.drop_duplicates(subset="url_hash")
```

> 💡 **Compare com a nossa `src/comum/taxonomia.py`**, que tem **152 termos em 7 categorias**.
> A deles tem 18 termos, sem categorização. **A nossa é substancialmente mais elaborada** — e
> isso é um ponto forte que vale explicitar na dissertação, não deixar implícito.
>
> Vale, porém, **conferir se termos deles estão faltando na nossa**: `lifting cost`, `FPSO`,
> `barris`, `leilão`, `ANP`, `reservas` são vocabulário de E&P que pode aparecer em notícias de
> PETR4 e escapar da nossa taxonomia.

### 3.2 Deduplicação por URL — uma técnica simples que não temos

O `hashlib.md5` sobre a URL é uma forma barata de eliminar republicações. **Vale verificar se
a nossa base tem duplicatas** — o Script 02b coleta de 5 portais via WordPress REST API, e
republicações de agência (Reuters, Estadão Conteúdo) são comuns.

---

## 4. Tecnologias e bibliotecas

Do `environment.yaml`:

| Categoria | Pacotes |
|---|---|
| **Core** | Python 3.11, pandas 2.2, numpy 2.3, **pyarrow**, **duckdb**, **yfinance** |
| **PLN / ML** | **spaCy 3.7** (`pt_core_news_sm`), **transformers 4.41**, **PyTorch 2.4 (CPU)**, NLTK |
| **Estatística e visualização** | scipy, **statsmodels**, matplotlib, seaborn, tqdm |
| **Coleta** | `gnews` |

**Modelo de sentimento:** `lucas-leme/FinBERT-PT-BR` — o mesmo nosso.

> 💡 **Duas escolhas técnicas que valem imitar:**
> 1. **Parquet + pyarrow** em vez de CSV para os dados intermediários. Nossa pasta
>    `Mestrado_PETR4/` é toda CSV. Parquet é tipado, comprimido e muito mais rápido — e
>    preserva `datetime` com fuso, o que CSV não faz.
> 2. **`environment.yaml` com versões fixadas.** O nosso `requirements.txt` existe, mas o
>    ambiente local está quebrado (PyTorch com falha de DLL). Um ambiente conda reproduzível
>    resolveria isso — e vale notar que eles fixam **PyTorch CPU**, que é suficiente para
>    inferência de sentimento e evita todo o inferno de CUDA.

---

## 5. Método

### 5.1 Pontuação de sentimento

```python
_pt_pipeline = pipeline(task="text-classification",
                        model="lucas-leme/FinBERT-PT-BR",
                        tokenizer="lucas-leme/FinBERT-PT-BR",
                        truncation=True, max_length=512)

LABEL2COMP = {"POSITIVE": 0.5, "NEGATIVE": -0.5, "NEUTRAL": 0.0}

# Heurística de idioma: se a manchete tem acentos → português → FinBERT-PT-BR;
# senão → VADER (inglês) como fallback
_pt_regex = re.compile(r"[áàâãéèêíìîóòôõúùüç]")
```

> ⚠️ **Duas fragilidades relevantes aqui:**
>
> 1. **O `compound` descarta a confiança do modelo.** Eles mapeiam a classe para
>    `{−0,5; 0; +0,5}`, jogando fora a probabilidade. **O nosso ISM usa `polaridade × confiança
>    ∈ [−1, +1]`**, que é estritamente mais informativo. Isso é uma **vantagem nossa**, e o
>    contraste vale ser registrado no gap G11.
> 2. **A heurística de idioma por acentuação é frágil.** *"Petrobras beats Q3 estimates"* não
>    tem acento e cairia no VADER; *"Oil prices fall"* também. Como classificam manchetes
>    coletadas do Google News em `language='pt'`, o impacto é pequeno — mas é o tipo de atalho
>    que não devemos replicar.

### 5.2 Agregação diária

```python
daily_sent = (news.groupby(pd.Grouper(freq="D"))
    .agg(compound_mean=("compound", "mean"),      # média do dia
         compound_mag =("compound", max_magnitude), # o de MAIOR magnitude absoluta
         art_count    =("compound", "size")))      # volume de notícias
```

> 💡 **`compound_mag` é uma ideia que não temos e que vale testar.** Em vez da média, pega o
> sentimento **de maior magnitude absoluta** do dia — a lógica é que **uma notícia muito
> negativa move o mercado mais do que dez notícias neutras a diluem**. É uma hipótese
> plausível e barata de testar, e entra diretamente no **gap G11** (comparação de formulações
> do índice).
>
> Eles próprios reportam que `compound_mean ≈ compound_mag` (Pearson ρ ≈ 0,94) no caso deles,
> mas isso pode ser específico do volume de notícias da PRIO3.

**Tratamento de fuso horário** — detalhe que importa:

```python
LOCAL_TZ = "America/Sao_Paulo"
def to_local_midnight(idx):
    local = idx.tz_convert(LOCAL_TZ)
    return pd.to_datetime(local.date)
```

> 💡 Converter para meia-noite local **antes** de juntar notícia e preço é exatamente o cuidado
> que sustenta o nosso recorte de "notícias após as 17h". **Vale conferir se o nosso Script 02b
> faz a conversão de fuso explicitamente** ou se está assumindo que a API já devolve em horário
> local — é fonte clássica de erro de um dia.

### 5.3 Retornos futuros e janelas

```python
merged["pct_d0"] = (merged["price_close"] - merged["price_open"]) / merged["price_open"]
for d in (1, 3, 5, 7, 15, 30, 60, 80, 90):
    merged[f"pct_d{d}"] = (series.shift(-d) - series) / series
```

**Nove horizontes**, de D+1 a D+90, mais o retorno intradiário D0.

> 💡 **Nós olhamos principalmente D+1.** Esta é uma limitação nossa que vale reconhecer: o
> efeito do sentimento pode ser **lento**, e eles encontram justamente isso (Seção 6). Ampliar
> os horizontes é barato — os dados já estão na base — e pode reposicionar o resultado da
> direção.

### 5.4 Análises aplicadas

Curvas de estudo de evento · gráficos de barras por horizonte · distribuições em violino ·
matrizes de correlação · **causalidade de Granger** · testes de diferença de médias
(**Welch-t** e **Mann-Whitney**).

---

## 6. Resultados — e a convergência com os nossos

| Achado | Evidência declarada |
|---|---|
| **Impacto intradiário desprezível** | Mediana de `pct_d0` ≈ 0% para todas as classes de sentimento |
| ***Drift* de médio prazo aparece** | Dias neutros e positivos superam os negativos em **15–30 pp em D+15/D+30** |
| **Poder estatístico fraco** | Welch-t e Mann-Whitney em horizontes ≤ 7 dias **não significativos (p > 0,05)** |
| `compound_mean` ≈ `compound_mag` | Pearson ρ ≈ 0,94 |
| **Relação não linear e defasada** | Pearson/Spearman ≈ 0 no curto prazo; efeito só após 5+ dias |

**Conclusão do autor:**

> *"headline tone doesn't move PRIO3 intraday, yet there is early evidence of bullish drift 5–30
> days after non-negative headlines — worth deeper back-testing with more data."*

### 6.1 Por que isso importa para nós

**Estes achados convergem com os nossos**, obtidos de forma independente, em outro ativo do
mesmo setor, por outro autor, com outro pipeline:

| Nosso achado | Achado deles |
|---|---|
| Direção ≈ acaso | *"headline tone doesn't move PRIO3 intraday"* |
| Sinal fraco em horizonte curto | *"Pearson/Spearman ≈ 0 in short run"* |
| Ganho está na volatilidade, não na direção | *"effect shows only after 5+ days"* — efeito lento, compatível com propagação por incerteza |

> **Isso é uma forma de validação externa do nosso resultado negativo na direção.** Não é
> literatura citável, mas é uma verificação independente de que **o problema não é o nosso
> pipeline** — é a natureza do fenômeno. Reforça o argumento do gap **G1**: migrar o eixo da
> dissertação para volatilidade não é conveniência, é o que os dados do setor indicam.

### 6.2 O que eles não fizeram e nós fazemos

| Dimensão | jp-alves | **Nós** |
|---|---|---|
| **Gabarito humano** | ❌ Nenhum — sentimento nunca validado | ✅ 300 manchetes anotadas |
| **Modelo de volatilidade** | ❌ | ✅ GARCH(1,1), Mincer-Zarnowitz, QLIKE, regressão quantílica |
| **Fusão com ML** | ❌ | ✅ SVM, XGBoost, *stacking*, ablação |
| **Taxonomia de categorias** | 18 termos, sem categoria | ✅ 152 termos, 7 categorias |
| ***Split* temporal e walk-forward** | ❌ | ✅ |
| **Confiança do modelo no índice** | ❌ descarta (usa ±0,5) | ✅ polaridade × confiança |
| **Testes de significância** | ✅ Welch-t, Mann-Whitney | ✅ binomial, McNemar, Granger |

**Em quase todas as dimensões o nosso trabalho é mais completo.** O que eles têm e nós não:
**múltiplos horizontes** (D+1 a D+90), **Parquet**, **deduplicação por hash de URL** e
**`compound_mag`**.

---

## 7. Código — arquivos baixados

| Arquivo local | Original | Conteúdo |
|---|---|---|
| `prio3_README.md` | `README.md` | Objetivo, achados, passos de reprodução |
| `prio3_environment.yaml` | `environment.yaml` | Ambiente conda com versões fixadas |
| `prio3_src_collect_scrap_news.py` | `src/collect/scrap_news.py` | Coleta GNews mês a mês |
| `prio3_src_clean_clean_news.py` | `src/clean/clean_news.py` | Limpeza, filtro por palavras-chave, dedup por hash |
| `prio3_src_nlp_sentiment.py` | `src/nlp/sentiment.py` | FinBERT-PT-BR + fallback VADER |
| `prio3_src_nlp_apply_sentiment.py` | `src/nlp/apply_sentiment.py` | Aplicação em lote |
| `prio3_src_nlp_text_preprocess.py` | `src/nlp/text_preprocess.py` | Lematização com spaCy `pt_core_news_sm` |
| `prio3_analysis_merge.py` | `analysis/merge.py` | Agregação diária, fuso, retornos futuros D0–D90 |

O repositório também traz `notebooks/main_analysis.ipynb` (não baixado — é o que gera as figuras)
e os dados intermediários em Parquet.

---

## 8. Leitura crítica

### 8.1 O que aproveitar

| # | O que | Como | Gap |
|---|---|---|---|
| 1 | **Múltiplos horizontes (D+1 a D+90)** | Nosso foco está em D+1; ampliar é barato e pode reposicionar o resultado da direção | **G1** |
| 2 | **`compound_mag`** (sentimento de maior magnitude do dia) | Quarta variante na comparação de formulações do índice | **G11** |
| 3 | **Deduplicação por hash MD5 da URL** | Verificar duplicatas nos 5 portais que coletamos | — |
| 4 | **Conversão explícita de fuso antes do *join*** | Auditar o Script 02b — fonte clássica de erro de um dia | — |
| 5 | **Termos de E&P ausentes na nossa taxonomia** | `lifting cost`, `FPSO`, `barris`, `leilão`, `ANP`, `reservas` | — |
| 6 | **Parquet + pyarrow** para dados intermediários | Substituir CSV — tipado, comprimido, preserva fuso | — |
| 7 | **`environment.yaml` com PyTorch CPU fixado** | Resolveria o nosso ambiente quebrado | — |
| 8 | **Convergência dos achados** | Validação externa independente do nosso resultado na direção | **G1** |

### 8.2 O que **não** aproveitar

| Item | Por quê |
|---|---|
| **`compound ∈ {−0,5; 0; +0,5}`** | Descarta a confiança do modelo. O nosso `polaridade × confiança` é estritamente melhor. |
| **Heurística de idioma por acentuação** | Frágil. Manchetes em português sem acento cairiam no VADER. |
| **Ausência de gabarito** | O sentimento nunca é validado contra humano. É a maior fragilidade do projeto — e o nosso maior diferencial. |
| **GNews como fonte primária** | O `gnews` devolve manchetes agregadas, com metadados pobres e sem hora exata. O nosso Script 02b, via WordPress REST API, captura **hora exata** — que é o que viabiliza o recorte "após as 17h". |

### 8.3 Ação imediata sugerida

Três verificações baratas na nossa base, motivadas por este repositório:

```python
# 1. Duplicatas por URL — o Script 02b coleta de 5 portais; republicações de
#    agência (Reuters, Estadão Conteúdo) são comuns
import hashlib
base["url_hash"] = base["link"].map(lambda u: hashlib.md5(str(u).encode()).hexdigest())
print("Duplicatas por URL:", base.duplicated("url_hash").sum())

# 2. Duplicatas por título normalizado (republicação com URL diferente)
print("Duplicatas por título:", base["titulo"].str.lower().str.strip().duplicated().sum())

# 3. Termos de E&P que podem estar faltando na taxonomia
faltantes = {"lifting cost", "fpso", "barris", "leilão", "anp", "reservas", "campo"}
from src.comum.taxonomia import TERMOS   # 152 termos, 7 categorias
print("Ausentes da taxonomia:", faltantes - {t.lower() for t in TERMOS})
```

---

## Anexo — quadro-resumo

| | |
|---|---|
| **Natureza** | Repositório GitHub — **não é publicação acadêmica**, não cita Santos |
| **Ativo / período** | **PRIO3** (PetroRio), 2015–2024 |
| **Coleta** | `gnews` mês a mês (`'PetroRio OR PRIO3'`, pt-BR) + `yfinance` |
| **Modelo** | **`lucas-leme/FinBERT-PT-BR`**, com fallback VADER para inglês |
| **Índice** | `compound ∈ {−0,5; 0; +0,5}`; agregação diária por média, magnitude máxima e contagem |
| **Análises** | Estudo de evento, D0 a D+90, Granger, Welch-t, Mann-Whitney |
| **Bibliotecas** | pandas, pyarrow, duckdb, yfinance, spaCy, transformers 4.41, PyTorch 2.4 CPU, statsmodels |
| **Achados** | Impacto intradiário ≈ 0; *drift* de 15–30 pp em D+15/D+30; p > 0,05 em horizontes curtos |
| **Código** | ✅ **Completo e público** |
| **Valor para nós** | **Alto como referência de implementação e validação externa; nulo como citação** |
