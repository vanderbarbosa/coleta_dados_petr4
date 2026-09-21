# 01 · Santos, Bianchi e Costa (2023) — FinBERT-PT-BR

> **É o modelo que a nossa pesquisa usa.** Este é o documento mais detalhado do conjunto,
> porque é a única pesquisa da lista que precisamos conhecer *integralmente* — não apenas para
> citar, mas para replicar, estender e criticar.
>
> Fonte deste resumo: leitura integral do **artigo do BWAIF** (12 páginas) e da **monografia de
> 2022** (61 páginas), que é substancialmente mais detalhada e contém material ausente do artigo.

---

## 1. Ficha bibliográfica

| Campo | Valor |
|---|---|
| **Referência (artigo)** | SANTOS, L. L.; BIANCHI, R. A. C.; COSTA, A. H. R. FinBERT-PT-BR: Análise de Sentimentos de Textos em Português do Mercado Financeiro. In: BRAZILIAN WORKSHOP ON ARTIFICIAL INTELLIGENCE IN FINANCE (BWAIF), 2., 2023. **Anais** [...]. Porto Alegre: SBC, 2023. p. 144-155. |
| **DOI** | 10.5753/bwaif.2023.231151 |
| **Referência (monografia)** | SANTOS, L. L. **FinBERT-PT-BR: análise de sentimentos de textos em português referentes ao mercado financeiro**. 2022. TCC (Engenharia de Computação) — Escola Politécnica, USP, São Paulo. Orientadora: Anna Helena Reali Costa. 61 f. |
| **Afiliações** | Escola Politécnica da USP (Santos e Costa); Centro Universitário FEI (Bianchi) |
| **Fomento** | CNPq, processo n. 310085/2020-9 |
| **Colaboradores citados nos agradecimentos** | Julia Pocciotti, Kevin Ujiie, Thomas Ferraz, Vinícius Carmo, Prof. Dr. Fábio Levy — todos ligados ao grupo **Turing USP** |
| **Modelo publicado** | https://huggingface.co/lucas-leme/FinBERT-PT-BR · licença **Apache 2.0** · última modificação **13/02/2024** · **177.384 downloads/mês** · 30 *likes* · 7 discussões |
| **Código-fonte do treinamento** | ⚠️ **NÃO PUBLICADO** — ver Seção 7.1 |
| **Dados de treinamento** | ⚠️ **NÃO PUBLICADOS** — nem o corpus de 1,4 milhão, nem os 503 textos rotulados |

---

## 2. Objetivo e pergunta de pesquisa

**Objetivo declarado.** Apresentar um modelo de linguagem do estado da arte para o mercado
financeiro em português do Brasil (**FinBERT-PT-BR**) e, a partir dele, um classificador de
sentimento (**SentFinBERT-PT-BR**), demonstrando que este viabiliza a construção de sinais para
análise e estratégias de investimento.

**Premissa teórica.** Ancorada na **hipótese de mercados adaptativos** de Lo (2004): os preços
dos ativos refletem informações *e emoções* da população e são adaptativos. Se os mercados
fossem perfeitamente eficientes, o sentimento de notícias não teria conteúdo informacional —
é essa premissa que legitima toda a linha de pesquisa, inclusive a nossa.

**Premissa técnica.** Herdada de Araci (2019): modelos genéricos erram em texto financeiro
porque o vocabulário do domínio inverte polaridades. A solução é o pré-treino de domínio.

### ⚠️ Nota terminológica que gera confusão prática

O trabalho define **dois artefatos distintos**:

| Nome | O que é | Publicado? |
|---|---|---|
| **FinBERT-PT-BR** | O **modelo de linguagem** adaptado ao domínio financeiro (só MLM) | ❌ **Não** |
| **SentFinBERT-PT-BR** | O **classificador de sentimento** derivado dele (3 classes) | ✅ Sim — mas sob o nome do primeiro |

O repositório HuggingFace publica **um único artefato**, chamado `FinBERT-PT-BR`, que é na
verdade o **SentFinBERT-PT-BR**: a arquitetura declarada no `config.json` é
`BertForSequenceClassification`, com três rótulos.

**Consequência direta para nós:** ao continuar o pré-treinamento MLM a partir de
`lucas-leme/FinBERT-PT-BR` (nosso gap G3), estaremos partindo de um modelo **que já passou por
ajuste fino supervisionado**, e não do modelo de linguagem puro. É viável, mas é metodologicamente
menos limpo — daí a recomendação de rodar as duas variantes (ver Seção 8.3).

---

## 3. Dados

### 3.1 Etapa 1 — corpus para o modelo de linguagem

| Item | Valor |
|---|---|
| **Fontes** | Valor Econômico, Exame, InfoMoney |
| **Período** | 2006 a 2022 |
| **Coleta** | *Web scraping* com **Scrapy** |
| **Metadados capturados** | título, subtítulo, data de publicação, data de atualização, nome e página do autor, *links* |
| **Volume bruto** | **2,7 milhões** de sentenças · **130 milhões** de palavras |
| **Após limpeza (regex)** | 1,6 milhão de sentenças |
| **Após filtro de ≤ 512 tokens** | **1.428.867 sentenças** — o número final de treino |
| **Holdout de avaliação** | 100 mil sentenças não usadas no treino |

Distribuição por veículo:

| Veículo | Textos |
|---|---|
| Valor Econômico | 1,23 milhão |
| Exame | 1,01 milhão |
| InfoMoney | 0,46 milhão |

**Limpeza declarada:** expressões regulares que identificaram padrões de texto irrelevantes —
textos malformados com caracteres especiais e código-fonte. *O artigo não publica as regex.*

### 3.2 Etapa 2 — base rotulada para o classificador

| Item | Valor |
|---|---|
| **Textos anotados** | 1.000 |
| **Descartados** | **497 (49,7%)** — classificados como "não se aplica" **ou** sem concordância |
| **Base final** | **503 textos** |
| **Distribuição** | 160 positivos · 203 negativos · 140 neutros |
| **Anotadores** | 3 pessoas — **duas de engenharia e uma de linguística** |
| **Cobertura** | cada texto anotado por **ao menos duas** pessoas |
| **Divisão** | 70% treino (com validação cruzada 5-*fold*) · 30% teste |

**Instrução de anotação, literal:**

> *"Classifique a notícia considerando se o texto implicaria em uma rentabilidade **Positiva,
> Negativa ou Neutra**. **'Não se aplica'** para textos não relacionados a finanças, de políticos
> ou sem sentido."*

**Concordância entre anotadores:**

| Métrica | Valor |
|---|---|
| Percentual de concordância | **90,4%** |
| *Krippendorff's alpha* (α) | **0,88** |

> 💡 **Ponto crítico para nós.** O que dá validade a esse gabarito não é a formação dos
> anotadores — nenhum é especialista em finanças. São três coisas: a **definição operacional
> ancorada em rentabilidade** (não em emoção), a **dupla anotação com descarte agressivo** de
> quase metade dos casos, e a **medição formal de concordância**. O nosso conjunto-ouro tem
> anotador único e, portanto, não tem nenhuma das três.

### 3.3 Protocolo de anotação em 6 etapas (monografia, Seção 2.3.1)

Baseado em Hovy e Lavid (2010). É o protocolo a adotar quando a rotulagem for retomada:

1. Seleção de textos representativos
2. Definição clara sobre as classes a serem classificadas
3. Anotação inicial **coletiva** de uma amostra da base
4. Avaliação do nível de concordância dos avaliadores
   - se insuficiente → **voltar à etapa 2** (redefinir as classes)
   - se suficiente → seguir para a etapa 5
5. Anotação do corpus inteiro, com análises de concordância **contínuas**
6. Treinamento do modelo com validação cruzada para avaliar a base

**Etapa 1 tem uma técnica associada** (monografia, Seção 2.3.1.1): **modelagem de tópicos** para
pré-selecionar textos representativos e sugerir classe ao anotador. Santos cita
Poursabzi-Sangdeh e Boyd-Graber (2015) para o ganho de eficiência, e aponta dois modelos de
*zero-shot*: **XLM-R** (Goyal et al., 2021) e **ZeroBERTo** (Alcoforado et al., 2022), este
último desenhado para línguas de poucos recursos. **É a resposta técnica direta à objeção do
Prof. Emerson sobre a falta de especialização em finanças.**

---

## 4. Tecnologias, bibliotecas e encoders

### 4.1 Stack completo (monografia, Seção 4.1)

| Tecnologia | Função no projeto |
|---|---|
| **Python** | Linguagem base |
| **Scrapy** | *Web crawling* dos portais financeiros |
| **Hugging Face `transformers`** | Modelos, *tokenizers* e `Trainer` |
| **PyTorch** | *Backend* de treinamento |
| **Kedro** | **Orquestração do pipeline de dados** — organiza a sequência coleta → limpeza → treino |
| **Kaggle** | Ambiente de execução (GPU gratuita) |
| **Weights & Biases (`wandb`)** | Rastreamento de experimentos e curvas de convergência |
| **scikit-learn** | Linha de base Random Forest + TF-IDF (Pedregosa et al., 2011) |

> 💡 **Kedro é o elemento que mais nos falta.** O nosso pipeline é uma sequência de scripts
> numerados (`01_`, `02b_`, `03_`, `04_`…) executados manualmente e na ordem certa. Kedro
> formaliza isso em um DAG com catálogo de dados versionado. Não é obrigatório, mas é o que
> transformaria a nossa reprodutibilidade de "documentada no README" em "garantida pelo código".

### 4.2 Encoders envolvidos

| Encoder | Papel |
|---|---|
| **BERTimbau base** (`neuralmind/bert-base-portuguese-cased`) | **Ponto de partida** — pesos iniciais |
| **FinBERT-PT-BR** | Resultado da Etapa 1 (não publicado) |
| **SentFinBERT-PT-BR** | Resultado da Etapa 2 (publicado como `lucas-leme/FinBERT-PT-BR`) |
| **FinBERT (EN)** (Araci, 2019) | Linha de base, sobre texto **traduzido** |
| **M2M-100 do Facebook** (Fan et al., 2021) | Tradutor multilíngue usado para gerar a linha de base acima |
| **Random Forest + TF-IDF** | Linha de base clássica |

### 4.3 Infraestrutura declarada

| Item | Valor |
|---|---|
| Ambiente | Kaggle |
| RAM | 30 GB |
| GPU | **2× Nvidia T4** (30 GB total) |
| Restrição imposta | *batch size* limitado a 16; necessidade de **alocação dinâmica de memória** (textos carregados do disco → RAM → GPU ao longo do treino, e não todos de uma vez) |
| Tempo | **2 épocas em 11 horas** |

---

## 5. Método passo a passo, com todos os hiperparâmetros

### 5.1 Etapa 1 — modelo de linguagem (*domain-adaptive pretraining*)

```
BERTimbau base  →  [MLM sobre 1.428.867 sentenças financeiras]  →  FinBERT-PT-BR
```

| Hiperparâmetro | Valor | Origem declarada |
|---|---|---|
| Pesos iniciais | BERTimbau base | Souza, Nogueira e Lotufo (2020) |
| Objetivo | *Masked Language Modeling* | Devlin et al. (2018) |
| **Probabilidade de máscara** | **15%** | Devlin et al. (2018) |
| **Taxa de aprendizado** | **2e-5** | Sun et al. (2019) |
| ***Batch size*** | **16** | Limitação de GPU |
| **Épocas** | **2** | — |
| Limite de tokens | 512 | Arquitetura BERT |
| Métrica | **Perplexidade** | Chen, Beeferman e Rosenfeld (1998) |

**Resultado:**

| Modelo | Perplexidade |
|---|---|
| BERTimbau (original) | 1,51 |
| **FinBERT-PT-BR** | **1,24** |

> 💡 Ganho de **~18%** em perplexidade com apenas 2 épocas. É a etapa de melhor relação
> custo-benefício de todo o trabalho — e **é a que nós ainda não fizemos**.

### 5.2 Etapa 2 — classificador de sentimento

```
FinBERT-PT-BR  →  [+ camada de classificação, transfer learning]  →  SentFinBERT-PT-BR
```

| Hiperparâmetro | Valor | Observação |
|---|---|---|
| Cabeça de classificação | Sobre a **primeira dimensão de saída** do BERT (token `[CLS]`) | Conforme Devlin et al. (2018) |
| Classes | 3 — positivo, negativo, neutro | |
| **Técnica antiesquecimento** | ***Gradual Unfreezing*** | Descongelamento gradativo das camadas de *encoder* |
| Camadas descongeladas gradualmente | **11 camadas de *encoder*** | O texto diz 11; o `config.json` publicado declara 12 (`num_hidden_layers: 12`) |
| **Taxa de aprendizado** | **5e-6** | Uma ordem de grandeza abaixo do usual, para evitar esquecimento catastrófico |
| **Épocas** | **11** | |
| Validação | **Validação cruzada 5-*fold*** sobre 70% da base | Modelo escolhido: o de menor função de custo na validação |
| Teste | 30% da base, não vistos | |

> ⚠️ **Comparação direta com o que fizemos.** Nossos experimentos de encoder usaram
> **3 épocas, sem *gradual unfreezing*, sem adaptação de domínio prévia e com 300 exemplos**.
> Santos usou **11 épocas, com *gradual unfreezing*, sobre um LM já adaptado, com 503 exemplos**.
> Não é de espantar que os nossos concorrentes tenham colapsado para a classe majoritária.

### 5.3 Etapa 3 — índice de sentimento

Série temporal construída a partir das classificações, seguindo Hiew et al. (2019):

$$\text{Índice}_{t-k,\,t} = \frac{Pos_{t-k,t} - Neg_{t-k,t}}{Pos_{t-k,t} + Neu_{t-k,t} + Neg_{t-k,t}}$$

onde *Pos*, *Neg* e *Neu* são as **contagens** de notícias de cada classe no intervalo
[t − k, t].

> 💡 **Diferença em relação ao nosso ISM.** Nós usamos `polaridade × confiança ∈ [−1, +1]`, o
> que é uma **variante não documentada na literatura** — mais informativa (aproveita a
> probabilidade da classe), porém não comparável diretamente com Santos e Hiew. Isso precisa
> estar declarado no capítulo de método, e é o conteúdo do gap G11.

### 5.4 Etapa 4 — validação qualitativa contra eventos

O índice foi confrontado com **oito eventos** da economia brasileira, com narrativa para cada:

| # | Evento | Data | Comportamento do índice |
|---|---|---|---|
| 1 | Manifestações (alta do transporte público) | jun/2013 | Grande variação **negativa**; reversão positiva em ago/2013 |
| 2 | Início da Operação Lava Jato | mar/2014 | Tendência de **queda de médio prazo**; mínimo em mar/2015 (prisão de executivos) |
| 3 | Início do *impeachment* de Dilma Rousseff | fim de 2015 | Variação **positiva** (expectativa de resolução), seguida de queda |
| 4 | *Joesley Day* | 17/05/2017 | Grande variação **negativa**; amenizada quando o presidente não foi destituído |
| 5 | Eleição presidencial | 2018 | Leve **aumento** pós-eleição; retorno a negativo após a posse |
| 6 | Reforma da previdência | 2019 | Sequências de **alta** |
| 7 | Pandemia de COVID-19 | 2020 | **Poucas variações** — o autor atribui à incerteza (veículos divulgavam narrativas opostas) |
| 8 | Vacinas e estímulos econômicos | fim de 2020 | **Pico** do índice |
| 9 | Invasão da Ucrânia pela Rússia | 2022 | **"De longe, o fato que mais impactou o sentimento"** — grande variação negativa |

> 💡 O item 9 é diretamente comparável ao nosso `grafico_petr4_guerra.png`. Vale replicar o
> rigor narrativo da Figura 3 dele.

### 5.5 Etapa 5 — estratégia "apostando contra o sentimento"

**Racional declarado:** investidores pessimistas vendem ações influenciados por notícias
negativas, mas os fundamentos das empresas não são necessariamente afetados por notícias
negativas *de todo o mercado*. Quando esses investidores vendem, **aumenta o prêmio de risco**
dessas ações.

**Operacionalização:** base de preços de fechamento da B3 obtida do **Yahoo Finance**,
2014–2022. Para cada ação, calcula-se a correlação entre o índice de sentimento e os retornos
históricos; **selecionam-se mensalmente as ações com alta correlação negativa** com o índice.

| Resultado | Valor |
|---|---|
| Retorno acumulado da estratégia (8 anos) | **683%** |
| Retorno acumulado do Ibovespa no mesmo período | **254%** |
| Razão | **2,7×** |

> ⚠️ **Ressalva metodológica que o próprio artigo não faz.** Não há relato de custos de
> transação, de *slippage*, de restrições de liquidez, nem de teste de robustez fora da amostra.
> Um retorno de 683% em 8 anos sem esses controles deve ser lido com cautela. **Não recomendo
> citar esse número sem a ressalva** — e não recomendo estender essa linha (é finanças de
> carteira, não previsão de ativo; ver a lista de "não perseguir" em `CITACOES_E_GAPS`).

### 5.6 Etapa 6 — relação com dados macroeconômicos (só na monografia)

Presente apenas na monografia (Seção 4.3.2, Figura 18): **correlação entre o índice de
sentimento e a inflação**. Há também uma **regressão linear** com o índice de mercado como
variável dependente e fatores de investimento como independentes (Tabela 5).

---

## 6. Resultados completos

### 6.1 Modelo de linguagem

| Métrica | BERTimbau | FinBERT-PT-BR |
|---|---|---|
| Perplexidade | 1,51 | **1,24** |

### 6.2 Classificador de sentimento

**Tabela do artigo (Tabela 3) — a versão revisada por pares:**

| Modelo | Acurácia | F1-Score |
|---|---|---|
| Sent-BERTimbau | 0,67 | 0,63 |
| **SentFinBERT-PT-BR** | **0,76** | **0,73** |

**Tabela da monografia (Tabela 4) — mais completa, com as quatro linhas de base:**

| Modelo | Acurácia | F1-Score |
|---|---|---|
| Random Forest + TF-IDF | 0,45 | 0,35 |
| FinBERT (EN) sobre texto traduzido | 0,67 | 0,67 |
| BERTimbau | 0,69 | 0,63 |
| **FinBERT PT BR** | **0,76** | **0,73** |

> ⚠️ **Divergência entre as duas versões.** A monografia atribui **0,69** de acurácia ao
> BERTimbau; o artigo atribui **0,67**. É divergência do próprio autor entre as duas versões do
> trabalho. **Citar a versão do artigo**, que é a revisada por pares — e, se a diferença for
> relevante para algum argumento, mencionar as duas.

### 6.3 Validação estatística (só na monografia, Seção 4.2.4)

Esta é a parte **ausente do artigo** e mais valiosa para nós:

1. **Bootstrapping** (Efron, 1992) — reamostragem com reposição do conjunto de teste, para
   estimar intervalos de confiança de acurácia e F1 (Figuras 15 e 16).
2. **Resultado:** com intervalo de confiança de **80%**, os intervalos do FinBERT-PT-BR
   **não se sobrepõem** aos dos concorrentes.
3. **Teste de hipótese** — construído sobre a distribuição empírica reamostrada. Como as
   estatísticas tendem à gaussiana pelo teorema do limite central, aplicou-se um **teste Z**:
   - H₀: não existe diferença estatística entre as métricas dos modelos
   - H₁: existe diferença
   - **Resultado: p-valor numericamente igual a 0** → rejeita-se H₀

> 💡 **É exatamente o que a nossa tabela `resultado_encoders_petr4.csv` não tem** (gap G12).
> Com n = 300 e desvios-padrão de 2,7 a 8,4 pontos, a nossa diferença de −1,67 pp para o
> BERTimbau large é quase certamente indistinguível de zero.

---

## 7. Código

### 7.1 Situação: o código de treinamento não foi publicado

Verificação feita em 04/08/2026:

| Onde procurei | Resultado |
|---|---|
| GitHub pessoal `github.com/lucas-leme` (22 repositórios) | ❌ Nenhum repositório de FinBERT ou PLN financeiro |
| Organização `github.com/turing-usp` (81 repositórios) | ❌ Nenhum repositório do FinBERT-PT-BR |
| Repositório HuggingFace (10 arquivos) | ❌ Só pesos e *tokenizer* — sem `training_args.bin`, sem *notebooks*, sem dados |
| Busca no GitHub por "finbert-pt-br" | Só repositórios de **terceiros** que **consomem** o modelo |

**Consequência:** a replicação exata é impossível. O que segue é (a) o código oficial de
**inferência**, publicado no *model card*, e (b) uma **reconstrução fiel do treinamento**, escrita
a partir dos hiperparâmetros documentados no artigo e na monografia.

### 7.2 Código oficial de inferência (do *model card*)

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification

tokenizer = AutoTokenizer.from_pretrained("lucas-leme/FinBERT-PT-BR")
model = AutoModelForSequenceClassification.from_pretrained(
    "lucas-leme/FinBERT-PT-BR", device_map="auto")
```

Ou, na forma de *pipeline*:

```python
from transformers import pipeline

pipe = pipeline("text-classification", model="lucas-leme/FinBERT-PT-BR")
pipe("O Ibovespa fecha em alta puxado pelas ações da Petrobras")
# → [{'label': 'POSITIVE', 'score': 0.9...}]
```

### 7.3 ⚠️ Armadilha do mapeamento de rótulos

O `config.json` publicado contém:

```json
"id2label": { "0": "POSITIVE", "1": "NEGATIVE", "2": "NEUTRAL" },
"label2id": { "LABEL_0": 0, "LABEL_1": 1, "LABEL_2": 2 }
```

Dois problemas:

1. **A ordem é contraintuitiva.** Quase todos os modelos de sentimento de 3 classes usam
   `0 = negativo, 1 = neutro, 2 = positivo`. **Aqui é o oposto.**
2. **O `label2id` está quebrado** — não é o inverso do `id2label`. Mapeia `LABEL_0 → 0` em vez
   de `POSITIVE → 0`.

Na prática a `pipeline` usa o `id2label`, que está correto, e por isso o nosso Script 03
funciona. Mas o *fallback* `LABEL_*` do nosso código está **invertido**
([`03_analise_sentimento_bertimbau_petr4.py:312-317`](../../src/sentimento/03_analise_sentimento_bertimbau_petr4.py#L312-L317)):
se um dia esse caminho for acionado, **o sinal do ISM se inverte em silêncio, sem erro**.

**Verificação defensiva recomendada, a rodar uma vez no início do Script 03:**

```python
esperado = {0: "POSITIVE", 1: "NEGATIVE", 2: "NEUTRAL"}
obtido = {int(k): v for k, v in modelo.config.id2label.items()}
assert obtido == esperado, f"Mapeamento de rótulos mudou: {obtido}"
```

### 7.4 Reconstrução — Etapa 1: adaptação de domínio por MLM

> **Este é o script do gap G3**, a nossa frente técnica prioritária. Está gravado em
> [`../_codigos/reconstrucao_santos_etapa1_mlm.py`](../_codigos/reconstrucao_santos_etapa1_mlm.py),
> já adaptado ao nosso corpus de ~205 mil notícias.

Núcleo do método:

```python
from transformers import (AutoTokenizer, AutoModelForMaskedLM,
                          DataCollatorForLanguageModeling,
                          Trainer, TrainingArguments)

MODELO_BASE = "neuralmind/bert-base-portuguese-cased"   # ou lucas-leme/FinBERT-PT-BR

tokenizer = AutoTokenizer.from_pretrained(MODELO_BASE)
model     = AutoModelForMaskedLM.from_pretrained(MODELO_BASE)

# Máscara de 15% — Devlin et al. (2018), replicado por Santos
collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer, mlm=True, mlm_probability=0.15)

args = TrainingArguments(
    learning_rate=2e-5,              # Sun et al. (2019), usado por Santos
    per_device_train_batch_size=16,  # limitação de GPU, como no Kaggle 2×T4
    num_train_epochs=2,              # Santos: 2 épocas em 11 h
    ...
)
```

E a métrica de avaliação, que é o que torna este experimento **independente de gabarito humano**:

```python
import math
perplexidade = math.exp(trainer.evaluate()["eval_loss"])
# Alvo: bater a perplexidade do modelo de partida.
# Referência de Santos: BERTimbau 1,51 → FinBERT-PT-BR 1,24
```

> ⚠️ **Detalhe de implementação que Santos precisou resolver e nós também precisaremos.**
> Com 1,4 milhão de textos e 30 GB de RAM, ele implementou **alocação dinâmica de memória**:
> os textos são carregados do disco para a memória e depois para a GPU ao longo do treino, e
> não todos de uma vez. Em `datasets`, isso se resolve com `streaming=True` ou
> `load_dataset(..., keep_in_memory=False)`. O script reconstruído já contempla isso.

### 7.5 Reconstrução — Etapa 2: classificação com *gradual unfreezing*

> Gravado em [`../_codigos/reconstrucao_santos_etapa2_sentimento.py`](../_codigos/reconstrucao_santos_etapa2_sentimento.py).

O elemento que faltou nos nossos experimentos e que provavelmente explica o colapso do
Albertina é este:

```python
def congelar_tudo(model):
    """Congela embeddings e todas as camadas de encoder; só a cabeça treina."""
    for p in model.bert.embeddings.parameters():
        p.requires_grad = False
    for layer in model.bert.encoder.layer:
        for p in layer.parameters():
            p.requires_grad = False

def descongelar_ate(model, n):
    """Descongela as n camadas superiores do encoder (gradual unfreezing)."""
    camadas = model.bert.encoder.layer
    for layer in camadas[len(camadas) - n:]:
        for p in layer.parameters():
            p.requires_grad = True

# Santos: 11 épocas, uma camada liberada por época, lr = 5e-6
for epoca in range(11):
    descongelar_ate(model, n=epoca + 1)
    treinar_uma_epoca(model, lr=5e-6)
```

**Por que isso importa tanto.** Sem *gradual unfreezing*, ajustar um encoder de 100–900 milhões
de parâmetros sobre ~240 exemplos por *fold* faz o modelo esquecer o que aprendeu no pré-treino
e colapsar para a classe majoritária. É exatamente a assinatura do nosso
`log_albertina.txt`: **κ = 0,000 em 3 dos 5 folds** e F1-macro de 25–29%.

### 7.6 Reconstrução — validação estatística por *bootstrap*

> Gravado em [`../_codigos/reconstrucao_santos_bootstrap.py`](../_codigos/reconstrucao_santos_bootstrap.py).
> **É o gap G12**, e roda em ~2 horas sobre a nossa tabela atual.

```python
def bootstrap_metrica(y_true, y_pred, metrica, n_reamostras=10_000, seed=42):
    """Distribuição empírica da métrica por reamostragem com reposição (Efron, 1992)."""
    rng = np.random.default_rng(seed)
    n = len(y_true)
    return np.array([
        metrica(y_true[idx], y_pred[idx])
        for idx in (rng.integers(0, n, n) for _ in range(n_reamostras))
    ])

# Intervalo de confiança de 80%, como Santos
ic_inf, ic_sup = np.percentile(dist, [10, 90])

# Teste Z entre dois modelos sobre as distribuições empíricas
z = (dist_a.mean() - dist_b.mean()) / np.sqrt(dist_a.var() + dist_b.var())
```

---

## 8. Leitura crítica

### 8.1 O que aproveitar — em ordem de valor

| # | O que | Onde aplicar | Gap |
|---|---|---|---|
| 1 | **Receita de adaptação de domínio** (MLM, máscara 15%, lr 2e-5, ≤512 tokens, perplexidade) | Novo experimento sobre as ~205 mil notícias | **G3** |
| 2 | **Protocolo de ajuste fino** (*gradual unfreezing*, lr 5e-6, 11 épocas, CV 5-*fold*) | Refazer os experimentos de encoder, hoje inconclusivos | G3 |
| 3 | **Protocolo de anotação em 6 etapas** + definição operacional literal | Refundar o conjunto-ouro | **G5** |
| 4 | **Categoria "não se aplica" + descarte por discordância** | Nosso gabarito registra relevância, mas não descarta | G5 |
| 5 | ***Krippendorff's alpha*** e percentual de concordância | Métrica que hoje não temos | G5 |
| 6 | ***Bootstrap* + teste Z** | Dar significância à tabela de encoders | **G12** |
| 7 | **Modelagem de tópicos / *zero-shot* para pré-seleção** | Reduzir custo e dependência de especialista na rotulagem | G5 |
| 8 | **Fórmula do índice** | Comparar formalmente com o nosso ISM | G11 |
| 9 | **Validação qualitativa contra eventos** | Replicar o rigor da Figura 3 | — |
| 10 | **Kedro** para orquestração | Reprodutibilidade do pipeline | — |
| 11 | **Benchmark 0,76 / 0,73** | Contraste explícito com os nossos 58% | **G2** |

### 8.2 O que **não** aproveitar

| Item | Por quê |
|---|---|
| **Estratégia "apostando contra o sentimento"** | É finanças de carteira, não previsão de ativo. Descaracteriza o objeto e abre um flanco em que não temos competência declarada. Além disso, os 683% são reportados **sem custos de transação, sem *slippage* e sem teste fora da amostra**. |
| **Relação índice × inflação** | É trabalho futuro do próprio Santos e pertence à macroeconomia. Só faria sentido no doutorado. |
| **Números da monografia quando divergem do artigo** | Citar sempre a versão revisada por pares. |

### 8.3 Gaps e melhorias que podemos sanar

| Fragilidade de Santos | Como podemos sanar | Gap |
|---|---|---|
| **Não publicou dados nem código** | Publicar o nosso conjunto-ouro com DOI, dupla anotação e α — contribuição de artefato durável | **G5** |
| **Não testou em ativo específico** | É o nosso objeto. A degradação de 0,76 → 0,58 é **resultado**, não limitação | **G2** |
| **Não previu volatilidade** | É a nossa contribuição principal | **G1** |
| **Não respeitou ordem temporal** (crítica levantada por Imai et al., 2024) | Avaliação por subperíodo + adaptação incremental | **G4** |
| **Deixou a adaptação setorial como trabalho futuro** | *"aplicar a metodologia para setores específicos da bolsa"* — passados 3 anos, ninguém fez | **G3** |
| **Só 503 rótulos** | Não é problema em si (a adaptação de domínio compensa), mas limita a comparação de encoders | G5 |
| **Não filtrou relevância por ativo** | Nosso dado: só 37% das manchetes são relevantes à PETR4 | **G10** |
| **Não comparou granularidades textuais** | Ablação manchete × subtítulo × corpo | **G9** |
| **Publicou só `pytorch_model.bin`, sem `safetensors`** | Declarar como limitação de reprodutibilidade | — |
| **`label2id` quebrado no `config.json`** | Verificação defensiva no Script 03 (Seção 7.3) | — |

### 8.4 Trabalhos futuros que o próprio autor listou

Vale reproduzir, porque **todos apontam para o que estamos fazendo** — é o argumento mais
econômico de justificativa da dissertação:

1. Base **maior e mais específica** de textos financeiros para o modelo de linguagem → **G3**
2. **Mais textos rotulados**, mantendo altas métricas de concordância → **G5**
3. Aprimorar a **forma de cálculo do índice** de sentimento → **G11**
4. **Aplicar a metodologia a setores específicos da bolsa** → **G3 / nosso objeto**
5. Expandir a análise para **dados macroeconômicos** (inflação, PIB, desemprego) → *não perseguir*

### 8.5 Como citar em banca

> *"Adotamos o FinBERT-PT-BR (SANTOS; BIANCHI; COSTA, 2023) por ser o único modelo de linguagem
> adaptado ao domínio financeiro em português brasileiro com validação publicada — acurácia de
> 0,76 e F1 de 0,73 em três classes, superando o BERTimbau (0,67 / 0,63) com significância
> estatística verificada por bootstrap. Estendemos o trabalho em três direções que os próprios
> autores apontam como pendentes: a adaptação a um setor específico da bolsa, a validação contra
> gabarito humano em um ativo individual, e a previsão de volatilidade — dimensão que nenhum dos
> trabalhos correlatos aborda."*

---

## Anexo — quadro-resumo de uma página

| | |
|---|---|
| **Objetivo** | Modelo de linguagem e classificador de sentimento financeiro para PT-BR |
| **Encoder base** | BERTimbau base (110M) |
| **Corpus (LM)** | 1.428.867 sentenças · Valor, Exame, InfoMoney · 2006–2022 |
| **Corpus (sentimento)** | 503 textos (de 1.000; 49,7% descartados) · 3 anotadores · α = 0,88 |
| **Etapa 1** | MLM · máscara 15% · lr 2e-5 · batch 16 · 2 épocas · 11 h · 2× T4 |
| **Etapa 2** | *Gradual unfreezing* · lr 5e-6 · 11 épocas · CV 5-*fold* · 70/30 |
| **Bibliotecas** | Python, Scrapy, transformers, PyTorch, **Kedro**, Kaggle, **wandb**, scikit-learn |
| **Resultado (LM)** | Perplexidade 1,51 → **1,24** |
| **Resultado (sentimento)** | Acurácia **0,76** · F1 **0,73** (vs. BERTimbau 0,67 / 0,63) |
| **Validação estatística** | *Bootstrap* + IC 80% + teste Z · p ≈ 0 |
| **Aplicações** | Índice de sentimento · 8 eventos econômicos · estratégia contra o sentimento (683% × 254%) |
| **Código** | ❌ Não publicado · reconstruções em `../_codigos/` |
| **Licença do modelo** | Apache 2.0 — permite uso, modificação e **redistribuição de um `FinBERT-PETR4`** |
