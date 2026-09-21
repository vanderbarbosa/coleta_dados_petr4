# 04 · Imai et al. (2024) — *Concept drift* e ajuste fino periódico

> **Os autores são do nosso programa.** Alceu de Souza Britto Jr. e Jean Paul Barddal são
> professores do PPGIa da PUCPR; Alessandro Koerich é da ÉTS/Canadá, ex-PUCPR.
>
> **É o trabalho mais incômodo da lista.** A crítica que eles fazem a Santos — não respeitar a
> ordem temporal — **aplica-se hoje, literalmente, à nossa dissertação**. Se a banca ler este
> artigo, a pergunta vem pronta.
>
> ⚠️ **Limitação desta ficha.** O texto completo está atrás do *paywall* do IEEE Xplore. Este
> resumo foi montado a partir do *abstract* integral, do contexto de citação obtido na API do
> Semantic Scholar e da página de publicações do Prof. Barddal. **Recomenda-se baixar o PDF pelo
> Portal de Periódicos da CAPES via PUCPR** antes da versão final da dissertação — é a única
> ficha deste conjunto montada sem o texto integral, junto com a de Reichert e Perlin.

---

## 1. Ficha bibliográfica

| Campo | Valor |
|---|---|
| **Referência** | IMAI, B. Y. L.; GARCIA, C. M.; ROCHA, M. V.; KOERICH, A. L.; BRITTO JR., A. S.; BARDDAL, J. P. Is it fine to tune? Evaluating SentenceBERT fine-tuning for Brazilian Portuguese text stream classification. In: **IEEE INTERNATIONAL CONFERENCE ON BIG DATA (IEEE Big Data)**, 2024. |
| **DOI** | 10.1109/BigData62323.2024.10825456 |
| **Data** | 15/12/2024 |
| **Instituições** | **PUCPR (PPGIa)** e ÉTS/Canadá |
| **Acesso** | ❌ *Paywall* IEEE Xplore |
| **Código-fonte** | Não localizado (verificado na página do Prof. Barddal, 04/08/2026) |

---

## 2. Objetivo e pergunta de pesquisa

**Problema.** Modelos de linguagem pré-treinados são frequentemente usados **de forma estática
ao longo do tempo**, o que os expõe a dois fenômenos:

| Fenômeno | Definição |
|---|---|
| ***Concept drift*** | Mudança na distribuição dos dados |
| ***Semantic shift*** | Mudança no significado das palavras |

Ambos ficam mais evidentes quando **novos textos se tornam gradualmente disponíveis** — que é
exatamente a situação de um corpus de notícias.

**Pergunta.** Vale a pena atualizar periodicamente um modelo de linguagem pré-treinado, em vez
de mantê-lo estático? E a que custo computacional?

---

## 3. Dados

| Item | Valor |
|---|---|
| **Domínio** | *Posts* de notícias brasileiras |
| **Paradigma** | ***Text stream*** — respeitando a **ordem temporal** |
| **Granularidade de atualização** | **Anual** |
| **Amostra de atualização** | "número reduzido de *posts* recentes" |

> 💡 O paradigma de fluxo textual respeitando ordem temporal é o que distingue este trabalho.
> Diferentemente da validação cruzada aleatória — que Santos usa e nós também —, aqui **nenhum
> dado do futuro pode influenciar a avaliação do passado**.

---

## 4. Tecnologias e encoders

| Componente | Papel |
|---|---|
| **SentenceBERT (SBERT)** | Modelo de linguagem que gera as representações; atualizado anualmente |
| **Adaptive Random Forest (ARF)** | Classificador em fluxo, com adaptação a *drift* |
| **F1-macro** | Métrica de desempenho |
| **Tempo decorrido** | Métrica de custo |

> 💡 **SBERT é diferente do que usamos.** Produz *embeddings* de sentença otimizados para
> similaridade, e não classificação direta. O desenho é: SBERT gera vetores → ARF classifica.
> Isso permite **atualizar o modelo de linguagem sem retreinar o classificador**, e é uma
> arquitetura que valeria considerar se quiséssemos separar as duas etapas.
>
> **Adaptive Random Forest** é a peça que faz a ligação com *drift*: é uma floresta aleatória
> com detectores de mudança que substituem árvores quando a distribuição muda. Está disponível
> em `river` (antigo `scikit-multiflow`).

---

## 5. Método

```
Ano N:  [SBERT_N-1] --(fine-tune com amostra reduzida de posts do ano N)--> [SBERT_N]
             │                                                                   │
             └──> embeddings ──> Adaptive Random Forest ──> classificação ───────┘

Cenário de comparação: SBERT estático (nunca atualizado) sobre os mesmos anos
```

Comparam-se, ano a ano, o **modelo atualizado periodicamente** contra o **modelo estático**,
medindo F1-macro e tempo decorrido.

---

## 6. Resultados

Do *abstract* integral:

> *"The experimental results show that **regularly leveraging sampled texts from the recent past
> for fine-tuning LMs can improve performance metrics over time, reaching better results than
> using static LMs in most years analyzed**. We also evaluated the run times, which suggests that
> fine-tuning LMs over time provides **a good trade-off between performance and run time**."*

| Achado | Conteúdo |
|---|---|
| **Desempenho** | O ajuste fino periódico supera o modelo estático **na maioria dos anos analisados** |
| **Custo** | Bom compromisso entre desempenho e tempo de execução |
| **Volume necessário** | Basta uma **amostra reduzida** de textos recentes — não é preciso retreinar do zero |

> ⚠️ Os números exatos por ano estão no texto integral, inacessível. **Ao citar, restringir-se à
> afirmação qualitativa** — "supera o modelo estático na maioria dos anos analisados" — que está
> literalmente no *abstract* e é, portanto, citável com segurança.

---

## 7. Código

❌ Não localizado. O grupo publica alguns PDFs em `ppgia.pucpr.br/~jean.barddal/assets/pdf/`,
mas não este.

**Como reproduzir a ideia com o que temos:** o experimento mínimo (nível 2 do gap G4) não exige
o código deles. Está gravado em
[`../_codigos/avaliacao_temporal_drift.py`](../_codigos/avaliacao_temporal_drift.py). Núcleo:

```python
# Particionar o conjunto-ouro por ANO da notícia e medir a acurácia do
# FinBERT-PT-BR (congelado em 02/2024) em cada partição.
# Se houver drift, a acurácia cai nos anos posteriores ao congelamento.
for ano, grupo in gabarito.groupby(gabarito["data"].dt.year):
    acc = accuracy_score(grupo["rotulo_humano"], grupo["pred_finbert"])
    kappa = cohen_kappa_score(grupo["rotulo_humano"], grupo["pred_finbert"])
    print(f"{ano}: n={len(grupo):3d}  acc={acc:.3f}  κ={kappa:.3f}")
```

E um segundo diagnóstico, este **sem gabarito nenhum** — mede *drift* de vocabulário por
perplexidade, aproveitando o modelo do gap G3:

```python
# Perplexidade do modelo por ano do corpus completo (~205 mil notícias).
# Se subir nos anos recentes, há semantic shift mesmo sem rótulo humano.
for ano in range(2018, 2027):
    ppl = perplexidade(modelo, corpus[corpus.ano == ano])
```

---

## 8. Leitura crítica

### 8.1 Como o trabalho cita Santos — e por que isso nos atinge

> *"Even though we acknowledge the existence of similar works, such as **Santos et al. [24]**,
> their approach differs from ours in the following aspects: **(a) our approach considers the
> text stream paradigm, respecting the temporal order**; (b) although the authors used BERTimbau
> as a base LM, they fine-tuned…"* *(trecho truncado na base do Semantic Scholar)*

**A crítica é dirigida a Santos, mas descreve exatamente a nossa situação:**

| Aspecto | Santos (2023) | **Nossa dissertação** |
|---|---|---|
| Modelo | FinBERT-PT-BR, treinado com dados até 2022 | **FinBERT-PT-BR congelado em 13/02/2024** |
| Corpus classificado | 2006–2022 | **2018–2026** |
| Respeita ordem temporal na validação? | Não — CV aleatória 5-*fold* | **Não — CV aleatória** |
| Trata *drift*? | Não | **Não** |

**O problema concreto:** as notícias de 2025 e 2026 sobre a Petrobras contêm vocabulário e
enquadramento que o modelo nunca viu — mudanças na política de preços, novo ciclo de dividendos,
discussão sobre a **Margem Equatorial**, o novo plano estratégico. Um modelo congelado em
fevereiro de 2024 classifica esse material com o vocabulário de 2022.

> 💡 **Há, porém, uma atenuante que vale registrar.** O nosso Script 02c faz o *split*
> treino/validação/teste de forma **temporal** (60/15/25, `definicao_split_temporal.csv`), e o
> Script 05 usa **walk-forward**. Ou seja: **a modelagem preditiva respeita a ordem temporal**;
> o que não a respeita é a **etapa de sentimento**, em que um modelo estático é aplicado a todo
> o período. É uma distinção importante e que devemos fazer explicitamente — evita que a crítica
> pareça mais ampla do que é.

### 8.2 O que aproveitar

| # | O que | Como | Gap |
|---|---|---|---|
| 1 | **A fundamentação teórica de *concept drift* e *semantic shift*** | Declarar a limitação com respaldo, em vez de esperar que a banca a levante | **G4** |
| 2 | **O achado de que ajuste fino periódico supera o estático** | Justificar a proposta de adaptação incremental por ano | G4 |
| 3 | **O achado de que basta amostra reduzida** | Torna o experimento viável — não é preciso retreinar sobre 205 mil textos por ano | G4 |
| 4 | **A distinção *text stream* × validação aleatória** | Fortalece a defesa do nosso *split* temporal e do walk-forward | — |
| 5 | **`Adaptive Random Forest`** (`river`) | Alternativa a considerar para o Script 04, se quisermos modelagem adaptativa | — |
| 6 | **A ponte institucional** | Consultar Barddal e Britto Jr. — colaboração interna, custo zero | — |

### 8.3 O que **não** aproveitar

| Item | Por quê |
|---|---|
| **Migrar para SentenceBERT** | Arquitetura diferente (*embeddings* + classificador externo). Trocar agora refaria todo o Script 03 sem ganho claro para a nossa pergunta. |
| **Adotar o paradigma de fluxo integralmente** | Nossa base é finita e fechada (2018–2026), não um fluxo aberto. O que importa é o *diagnóstico* de *drift*, não a arquitetura de fluxo. |

### 8.4 Os três níveis de resposta ao gap G4

| Nível | O que fazer | Custo | Quando |
|---|---|---|---|
| **1 — Mínimo, obrigatório** | Declarar a limitação no capítulo de método, citando Imai et al. (2024). Registrar a atenuante do *split* temporal (Seção 8.1). | **1 parágrafo** | Antes de 10/08 |
| **2 — Recomendado** | Medir a acurácia do FinBERT-PT-BR **por subperíodo** contra o conjunto-ouro. Se cair nos anos recentes, **isso é um resultado**. Infra já existe (`resultados_subperiodo_petr4.csv`). | ~2 h | Antes de 10/08 |
| **3 — Ambicioso** | Adaptação de domínio incremental por ano, medida por perplexidade. Combina com G3 e **não consome rótulo**. | Colab, ~1 dia | Pós-10/08 |

> ⚠️ **Ressalva estatística sobre o nível 2.** Com 300 manchetes distribuídas em 9 anos, cada
> ano tem ~33 itens. **Isso é pouco para conclusão robusta.** Reportar com intervalo de
> confiança por *bootstrap* e ser explícito sobre o poder estatístico limitado — ou agrupar em
> dois blocos (até 2023 × 2024–2026), o que dá ~150 itens cada e é defensável.

### 8.5 Como citar

> *"O uso de modelos de linguagem de forma estática ao longo do tempo expõe-nos a concept drift
> e semantic shift (IMAI et al., 2024). Os autores demonstram, em fluxo de notícias brasileiras,
> que o ajuste fino periódico com amostra reduzida de textos recentes supera o modelo estático
> na maioria dos anos analisados, com bom compromisso entre desempenho e tempo de execução.
> Reconhecemos essa limitação: o modelo de sentimento aqui empregado foi congelado em fevereiro
> de 2024 e aplicado a um corpus que se estende até 2026. Ressalva-se, contudo, que a modelagem
> preditiva subsequente respeita a ordem temporal, tanto no split treino/teste quanto na
> validação walk-forward."*

---

## Anexo — quadro-resumo

| | |
|---|---|
| **Objetivo** | Avaliar se atualizar periodicamente um LM supera mantê-lo estático, em fluxo de notícias PT-BR |
| **Autores** | **Barddal e Britto Jr. são do PPGIa/PUCPR** |
| **Corpus** | *Posts* de notícias brasileiras, em paradigma de fluxo temporal |
| **Modelos** | **SentenceBERT** (atualizado anualmente) + **Adaptive Random Forest** |
| **Métricas** | F1-macro e tempo decorrido |
| **Resultado** | Ajuste fino periódico **supera o estático na maioria dos anos**; bom *trade-off* de tempo |
| **Citação a Santos** | Só para se diferenciar: *"our approach considers the text stream paradigm, respecting the temporal order"* |
| **Código** | ❌ Não localizado |
| **Ameaça à nossa pesquisa** | **Direta** — modelo congelado em 02/2024 sobre corpus 2018–2026 |
| **Atenuante nossa** | O *split* e o walk-forward **já** respeitam ordem temporal; o problema é só na etapa de sentimento |
