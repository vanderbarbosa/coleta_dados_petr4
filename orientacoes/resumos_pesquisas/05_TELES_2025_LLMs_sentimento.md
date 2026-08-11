# 05 · Teles e Figueiredo (2025) — LLMs × modelos clássicos em sentimento financeiro

> **É o trabalho que define o nosso experimento G6** — e, ao mesmo tempo, o exemplo mais nítido
> da lacuna que a dissertação explora: um artigo brasileiro, de análise de sentimento, de
> notícias, de mercado financeiro, que cita Santos duas vezes e **não inclui o FinBERT-PT-BR
> entre os nove modelos avaliados**, testando tudo sobre corpora em inglês.
>
> Fonte: leitura integral do PDF (10 páginas, arXiv).

---

## 1. Ficha bibliográfica

| Campo | Valor |
|---|---|
| **Referência** | TELES, L. E. P.; FIGUEIREDO, C. M. S. Comparing LLMs for sentiment analysis in financial market news. **arXiv:2510.15929**, 3 out. 2025. |
| **Instituição** | Universidade do Estado do Amazonas (UEA) — Manaus |
| **Fomento** | **FAPEAM**; Laboratório de Sistemas Inteligentes (LSI) |
| **Data** | 03/10/2025 — é o trabalho citante **mais recente** com texto integral disponível |
| **Código-fonte** | ❌ Não publicado |
| **Arquivo local** | `../_teles2025.pdf` · `../_teles2025.txt` |

---

## 2. Objetivo e pergunta de pesquisa

Estudo comparativo entre **LLMs** e **modelos clássicos** na tarefa de análise de sentimento de
notícias do mercado financeiro. Objetivo declarado: *"analisar a diferença de desempenho desses
modelos nesta importante tarefa de PLN no contexto de finanças"*, permitindo **quantificar os
benefícios de cada modelo ou abordagem**.

Três contribuições declaradas:

1. Coleta de conjuntos de dados de tipos e formatos distintos no mercado financeiro
2. Pesquisa de técnicas de LLM para extração eficiente de informação para classificação
3. Avaliação e comparação dos resultados

**Continuidade declarada.** Os autores citam trabalho anterior próprio — Teles e Figueiredo
(2024) — sobre previsão de preços de seis ações com janelas de 5, 15, 25 e 35 dias. O
sentimento entra como *feature* adicional a preços. **Isto é, o grupo caminha na mesma direção
que nós.**

---

## 3. Dados — três conjuntos, todos em inglês

| Conjunto | Registros | Classes | Origem |
|---|---|---|---|
| **Financial Phrase Bank (FPB)** | 4.845 | positivo, neutro, negativo | Malo et al. (2014) — notícias financeiras gerais. **Contém coluna `text_pt` com tradução para o português**, mas os autores usaram a coluna em inglês |
| **StockEmotions** | 10.000 (8.000 treino / 1.000 val / 1.000 teste) | *bullish* (positivo), *bearish* (negativo) | Lee et al. (2023) — coletado do **StockTwits**; contém emojis já processados |
| **Tweet Financial News (TFN)** | 2.486 (só o conjunto de validação) | 0 negativo, 1 neutro, 2 positivo | Manchetes de notícias financeiras em inglês |

> ⚠️ **O ponto crítico.** O FPB **tem uma coluna em português** (`text_pt`), e os autores optaram
> por usar o inglês. Isso significa que a comparação **poderia** ter sido feita em português —
> e com o FinBERT-PT-BR — e não foi. **É literalmente o vão que a nossa dissertação preenche.**

### 3.1 Pré-processamento (só para os modelos clássicos)

Os autores registram que LLMs dispensam pré-processamento específico e usam o texto original;
os clássicos precisam de:

| Etapa | Detalhe |
|---|---|
| Limpeza inicial | Remoção de *links*, espaços extras e pontuação; conversão para minúsculas |
| *Stopwords* | Removidas com **NLTK** (inglês) |
| Normalização de rótulos | StockEmotions (*bullish*/*bearish*) e TFN (0/1/2) mapeados ao padrão |
| **Balanceamento** | ***Undersampling*** pela classe minoritária |
| Divisão | 80% treino (dos quais 20% validação) / 20% teste |
| **Vetorização** | **TF-IDF** (`TfidfVectorizer` do scikit-learn) |
| **Redução de dimensionalidade** | **SVD para 500 colunas** |

**Efeito do balanceamento:**

| Conjunto | Antes (neutro / positivo / negativo) | Depois (cada classe) |
|---|---|---|
| FPB | 2.878 / 1.363 / 604 | **604** |
| TFN | 1.566 / 475 / 347 | **347** |

Divisões finais: FPB → 1.159 treino / 290 validação / 363 teste · TFN → 665 / 167 / 209.

Vocabulários TF-IDF: FPB 5.342 · StockEmotions 8.000 · TFN 2.000.

> ⚠️ **Escolha discutível.** O *undersampling* pela classe minoritária descartou ~79% do FPB
> (de 4.845 para ~1.812). Os próprios autores reconhecem o efeito: *"com a abordagem de
> undersampling usada, bons registros que poderiam identificar melhor esse rótulo podem ter
> ficado de fora"*. **Não replicar.** No nosso caso, com apenas 300 itens, *undersampling* seria
> destrutivo — preferir ponderação de classe (`class_weight='balanced'`).
>
> A redução por SVD para 500 colunas também foi motivada por limitação de recursos: com 250 os
> resultados foram "muito inferiores" e com 1.000 o tempo de treino estourou a memória do
> ambiente.

---

## 4. Tecnologias, bibliotecas e modelos

### 4.1 Modelos clássicos

| Modelo | Biblioteca | Hiperparâmetros testados | Melhor configuração |
|---|---|---|---|
| **Random Forest** | scikit-learn | `n_estimators` ∈ {100…500}; `criterion` ∈ {gini, entropy, log_loss}; `max_features` ∈ {sqrt, log2, None} | FPB: 300/entropy/None · StockEmotions: 400/entropy/sqrt · TFN: 400/gini/sqrt |
| **SVM** (`SVC`) | scikit-learn | `C`, `degree`, `gamma`, `kernel` | FPB: C=1,2/deg 2/scale/**rbf** · StockEmotions: C=1,1/2/scale/**rbf** · TFN: C=0,7/2/scale/**sigmoid** |
| **MLP** | Keras | neurônios, ativação, épocas, *dropout*; *batch* fixo em 32 | FPB: (200,100)/(relu,selu)/13 ép./(0.1, 0) · StockEmotions: (250)/relu/15/0.1 · TFN: (50)/elu/16/0.3 |

**Monitoramento do MLP** (Keras): `EarlyStopping` (paciência de 10 épocas), `ModelCheckpoint`,
`ReduceLROnPlateau` (reduz a taxa pela metade a cada 5 épocas sem melhora). Máximo de 200
épocas configurado, mas **nenhum treino passou de 20**.

**Custo declarado:** *grid search* do Random Forest levou **quase 4 horas**, mesmo com GPU do
Colab.

### 4.2 LLMs e *transformers*

| Modelo | Versão | Modo de uso |
|---|---|---|
| **Gemma** | `gemma-2-2b-it` (Google) | *Prompt*: *"Classify the text as positive, neutral, or negative. The sentiment of the text is:"* |
| **DeBERTa** | He et al. (2021) | Classificação; treinado em >1 milhão de avaliações da Amazon + 4 conjuntos |
| **DeBERTaV3** | He et al. (2023) | *Zero-shot* com a lista `['negative','neutral','positive']` |
| **XLM-RoBERTa** | Conneau et al. (2020) | *Zero-shot*, ajustado em dados de NLI em 15 línguas |
| **BART** | — | *Zero-shot text classification* (0Shot-TC) |
| **Gemini** | **2.0-flash** (Google) | *Prompt*: *"Classify the text as positive, neutral, or negative:"* |

> 💡 **O *prompt* é notavelmente simples** — uma frase, sem exemplos, sem instrução de domínio,
> sem definição operacional de rótulo. **Isso é uma oportunidade para nós.** No gap G6 vamos
> usar a **instrução literal de Santos** — *"Classifique a notícia considerando se o texto
> implicaria em uma rentabilidade Positiva, Negativa ou Neutra"* —, que é ancorada em
> consequência econômica e não em emoção genérica. Se o resultado melhorar, o ganho é
> **atribuível ao prompt**, e isso é um achado.

Para o StockEmotions (binário), o *prompt* foi ajustado removendo "neutral".

---

## 5. Resultados completos

### 5.1 Financial Phrase Bank — precisão, *recall* e F1 por classe

| Modelo | P-Pos | P-Neu | P-Neg | R-Pos | R-Neu | R-Neg | F1-Pos | F1-Neu | F1-Neg |
|---|---|---|---|---|---|---|---|---|---|
| SVM | 0,71 | 0,58 | 0,77 | 0,46 | 0,81 | 0,72 | 0,56 | 0,68 | 0,74 |
| Random Forest | 0,63 | 0,53 | 0,53 | 0,19 | 0,78 | 0,68 | 0,29 | 0,63 | 0,60 |
| MLP | 0,69 | 0,61 | 0,69 | 0,55 | 0,70 | 0,75 | 0,61 | 0,65 | 0,72 |
| Gemma | 0,44 | 0,67 | 0,95 | 0,98 | **0,02** | 0,64 | 0,61 | **0,03** | 0,77 |
| **DeBERTa** | **1,00** | 0,72 | **1,00** | 1,00 | 1,00 | 0,53 | **1,00** | **0,84** | 0,70 |
| DeBERTaV3 | 0,57 | 0,92 | 0,77 | 0,95 | **0,09** | 0,98 | 0,71 | **0,17** | 0,86 |
| XLM-RoBERTa | 0,48 | 0,67 | 0,82 | 0,93 | **0,06** | 0,79 | 0,63 | **0,11** | 0,81 |
| BART | 0,58 | 0,86 | 0,75 | 0,96 | **0,05** | 1,00 | 0,72 | **0,09** | 0,86 |
| **Gemini** | 0,90 | 0,66 | 0,96 | 0,66 | 0,90 | 0,86 | 0,77 | 0,76 | **0,91** |

> ⚠️ **Padrão que se repete e que os autores não comentam suficientemente: o colapso da classe
> NEUTRA nos modelos *zero-shot*.** Gemma, DeBERTaV3, XLM-RoBERTa e BART têm *recall* neutro de
> **0,02 a 0,09** — praticamente nunca predizem neutro. Só DeBERTa (ajustado) e Gemini escapam.
>
> **Isso é a nossa fraqueza medida, do outro lado do espelho.** O nosso FinBERT-PT-BR **erra o
> neutro empurrando-o para os extremos** (46,8% dos casos); estes modelos **nunca predizem
> neutro**. A dificuldade da classe neutra em sentimento financeiro é, portanto, um **problema
> estrutural da área**, e não idiossincrasia nossa. **Vale registrar isso na dissertação** — é
> argumento forte, e sustentado por dados de terceiro.

### 5.2 StockEmotions (binário)

| Modelo | P-Pos | P-Neg | R-Pos | R-Neg | F1-Pos | F1-Neg |
|---|---|---|---|---|---|---|
| **SVM** | 0,79 | 0,75 | 0,81 | 0,73 | **0,80** | **0,74** |
| Random Forest | 0,71 | 0,72 | 0,82 | 0,58 | 0,76 | 0,64 |
| **MLP** | 0,78 | 0,77 | 0,83 | 0,71 | **0,80** | **0,74** |
| Gemma | 0,69 | 0,65 | 0,75 | 0,57 | 0,72 | 0,61 |
| DeBERTa | 0,61 | 0,71 | 0,90 | 0,29 | 0,73 | 0,41 |
| DeBERTaV3 | 0,66 | 0,57 | 0,66 | 0,58 | 0,66 | 0,57 |
| XLM-RoBERTa | 0,63 | 0,57 | 0,70 | 0,49 | 0,67 | 0,53 |
| BART | 0,69 | 0,57 | 0,60 | 0,65 | 0,64 | 0,61 |
| Gemini | 0,80 | 0,68 | 0,70 | 0,79 | 0,75 | 0,73 |

**Aqui os clássicos ganham.** Explicação dos autores: o StockEmotions tem **muito mais dados de
treino** (8.000), o que favorece modelos que precisam treinar.

> 💡 **Achado transponível:** *"quanto mais dados forem fornecidos ao modelo clássico, melhores
> resultados ele pode alcançar"*. Com 300 itens, **nós estamos no regime oposto** — o que
> reforça que a nossa aposta deve ser em adaptação de domínio (G3) e comitê (G7), e não em
> treinar classificadores clássicos do zero.

### 5.3 Acurácia global (%) — a tabela-síntese

| Modelo | FPB | StockEmotions | TFN |
|---|---|---|---|
| SVM | 66,115 | 77,000 | 55,024 |
| Random Forest | 54,270 | 71,200 | 53,110 |
| MLP | 65,840 | 77,500 | 55,981 |
| Gemma | 54,270 | 67,300 | 61,722 |
| **DeBERTa** | **86,226** | 63,100 | 47,846 |
| DeBERTaV3 | 65,840 | 62,100 | 64,115 |
| XLM-RoBERTa | 58,402 | 61,100 | 57,416 |
| BART | 65,014 | 62,600 | 61,722 |
| **Gemini 2.0-flash** | 80,441 | 74,100 | **78,947** |

**Conclusão dos autores:**

> *"LLMs como Gemini, Gemma e BART são bons LLMs para serem usados em vários tipos de dados,
> além do DeBERTaV3, que é uma escolha interessante. (…) Gemini foi o modelo mais consistente.
> Mesmo não tendo a maior acurácia entre os três conjuntos, ainda alcançou bons resultados,
> mantendo acurácia acima de 70%."*

> ⚠️ **A leitura crítica que os autores não fazem: o DeBERTa oscila de 86,2% (FPB) a 47,8%
> (TFN).** Uma variação de 38 pontos percentuais entre conjuntos indica sensibilidade extrema ao
> *dataset* — e o valor de 86,2% no FPB é suspeito de contaminação, dado que o DeBERTa foi
> treinado em avaliações da Amazon e quatro outros conjuntos não especificados. **Não citar o
> DeBERTa como "o melhor" sem essa ressalva.** O argumento defensável é o da **consistência do
> Gemini**, não o do pico do DeBERTa.

**Trabalho futuro proposto pelos autores:** *"alinhar esses resultados com uma previsão de série
temporal para melhor monitorar variações de ações/fundos"* — **é literalmente o que já
fazemos.**

---

## 6. Código

❌ Não publicado. O artigo descreve os hiperparâmetros com detalhe suficiente para replicação,
mas não há repositório.

Para o gap G6, o script está em
[`../_codigos/llm_vs_encoder_conjunto_ouro.py`](../_codigos/llm_vs_encoder_conjunto_ouro.py).
Diferenças deliberadas em relação a Teles e Figueiredo:

| Aspecto | Teles e Figueiredo (2025) | **Nosso G6** |
|---|---|---|
| Idioma | Inglês | **Português** |
| Corpus | 3 conjuntos públicos genéricos | **Nosso conjunto-ouro, ativo específico** |
| Encoder de domínio | Ausente | **FinBERT-PT-BR incluído** |
| *Prompt* | Uma frase genérica | **Instrução literal de Santos**, ancorada em rentabilidade |
| Determinismo | Não discutido | **Temperatura 0, seed fixa, e repetição para medir variância** |
| Significância | Ausente | ***Bootstrap* + IC 80% + teste Z** |

---

## 7. Leitura crítica

### 7.1 Como o trabalho cita Santos

Duas citações, ambas na Introdução, **puramente definicionais**:

> *"Sentiment analysis is one of the techniques used in the field of NLP to identify and extract
> information about the emotions expressed in a text, such as positivity, negativity, or
> neutrality [Santos et al. 2023]."*
>
> *"The goal is to understand how people feel about a particular issue or product [Santos et al.
> 2023]."*

Santos é usado para **definir o que é análise de sentimento** — função que qualquer *survey*
cumpriria. Não há engajamento com o método, os resultados ou o modelo.

### 7.2 O que aproveitar

| # | O que | Como | Gap |
|---|---|---|---|
| 1 | **A lacuna que o artigo deixa aberta** | O teste em português, contra encoder de domínio, não existe — é o G6 | **G6** |
| 2 | **A consistência do Gemini** | Justifica escolher um LLM comercial como candidato, e não um *zero-shot* pequeno | G6 |
| 3 | **O colapso da classe neutra nos *zero-shot*** | Evidência de terceiro de que a classe neutra é problema **estrutural** da área | **G2, G7** |
| 4 | **"Mais dados → melhores clássicos"** | Argumento de que, com 300 itens, a aposta certa é domínio e comitê, não classificador clássico | G3, G7 |
| 5 | **O *prompt* simplista deles** | Contraste com a instrução de Santos que vamos usar — o ganho vira achado atribuível | G6 |
| 6 | **A lista de conjuntos públicos** | FPB, StockEmotions e TFN como *benchmarks* de referência ao propor o nosso (G5) | G5 |
| 7 | **O relato de custo** (4 h de *grid search*) | Bom padrão de reporte de custo computacional | — |

### 7.3 O que **não** aproveitar

| Item | Por quê |
|---|---|
| ***Undersampling* pela classe minoritária** | Descartou ~79% do FPB. Com 300 itens seria destrutivo. Preferir `class_weight='balanced'`. |
| **SVD para 500 colunas** | Foi contorno de limitação de memória, não escolha metodológica. Os próprios autores admitem. |
| **Citar o DeBERTa como "o melhor"** | Oscila 38 pp entre conjuntos; provável contaminação. |
| **Usar corpora traduzidos** | Santos já mostrou que o FinBERT-EN sobre texto traduzido (0,67) perde para o modelo nativo (0,76). |

### 7.4 Fragilidades do trabalho

| Fragilidade | Lição |
|---|---|
| **Não inclui o FinBERT-PT-BR**, apesar de citá-lo e de o FPB ter coluna em português | É a lacuna. Registrar explicitamente na dissertação. |
| **Nenhum teste de significância** | Reportam três decimais na acurácia (66,115%) mas nenhum intervalo de confiança. Precisão espúria. **Não imitar** — usar o *bootstrap* de Santos (G12). |
| **Não discute não determinismo dos LLMs** | Gemini e Gemma são estocásticos; nada sobre temperatura, *seed* ou variância entre execuções. **Nós devemos declarar e medir.** |
| **Não reporta custo por chamada** | Relevante para viabilidade. |

### 7.5 Como citar

> *"Teles e Figueiredo (2025) comparam nove modelos na análise de sentimento de notícias
> financeiras e concluem que modelos de linguagem de grande porte superam abordagens clássicas
> na maioria dos casos, com destaque para a consistência do Gemini (acurácia acima de 70% nos
> três conjuntos avaliados). A comparação, contudo, é conduzida integralmente sobre corpora em
> inglês e não inclui encoders de domínio em português, o que impede transpor a conclusão para o
> contexto brasileiro — lacuna que este trabalho endereça ao confrontar, sobre manchetes em
> português referentes a um ativo específico, o FinBERT-PT-BR com um modelo generativo."*

---

## Anexo — quadro-resumo

| | |
|---|---|
| **Objetivo** | Comparar LLMs e modelos clássicos em sentimento de notícias financeiras |
| **Corpora** | FPB (4.845) · StockEmotions (10.000) · TFN (2.486) — **todos em inglês** |
| **Clássicos** | SVM, Random Forest, MLP · TF-IDF + SVD(500) · *undersampling* |
| **LLMs** | Gemma-2-2b-it, DeBERTa, DeBERTaV3, XLM-RoBERTa, BART, **Gemini 2.0-flash** |
| **Bibliotecas** | scikit-learn, Keras, NLTK, `transformers` |
| **Melhor global** | **Gemini** — 80,4% / 74,1% / 78,9%, o mais consistente |
| **Pico isolado** | DeBERTa 86,2% no FPB, mas 47,8% no TFN (⚠️ suspeito) |
| **Achado lateral relevante** | *Zero-shot* colapsa a classe **neutra** (*recall* 0,02–0,09) |
| **Código** | ❌ Não publicado |
| **Valor para nós** | Define o experimento **G6** e documenta a lacuna que a dissertação preenche |
