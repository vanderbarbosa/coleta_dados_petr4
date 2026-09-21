# FinBERT (Araci, 2019) — o mais adotado

## 1. Ficha bibliográfica

| Campo | Conteúdo |
|---|---|
| **Referência** | ARACI, D. T. **FinBERT: financial sentiment analysis with pre-trained language models.** 2019. Dissertação (Mestrado em Data Science) — University of Amsterdam. arXiv:1908.10063. |
| **Natureza** | Dissertação de mestrado, depositada como *preprint* |
| **Citações** | **778** (Semantic Scholar, consulta em 13/08/2026). O Google Scholar reporta cifra superior; adota-se aqui a verificável. |
| **Repositório** | `ProsusAI/finbert` no Hugging Face |
| **Downloads** | **4.459.091 por mês** · 1,22 mil curtidas (consulta em 13/08/2026) |
| **Código** | Público, com o modelo e os pesos |

**Contexto institucional:** o autor era mestrando na Universidade de Amsterdã e o trabalho foi
incorporado pela Prosus, empresa do grupo Naspers. Vale registrar que o artefato mais baixado da
área de análise de sentimento financeiro é, na origem, **uma dissertação de mestrado** — fato de
algum alento para o nosso próprio trabalho.

## 2. Objetivo

Adaptar o BERT ao domínio financeiro e demonstrar que a adaptação supera tanto o BERT genérico
quanto os métodos anteriores baseados em dicionário e em aprendizado clássico.

## 3. Dados

| Etapa | Corpus | Volume |
|---|---|---|
| Pré-treinamento continuado | TRC2-financial (subconjunto do Reuters TRC2) | ~1,8 milhão de notícias, 2008–2010 |
| Ajuste fino | *Financial PhraseBank* (MALO et al., 2014) | 4.846 sentenças |

## 4. Arquitetura e método

- **Base:** `bert-base-uncased` — modelo genérico em inglês, **não sensível a maiúsculas**
- **Etapa 1:** pré-treinamento continuado por modelagem de linguagem mascarada sobre o TRC2
- **Etapa 2:** ajuste fino supervisionado de três classes sobre o *Financial PhraseBank*
- **Rótulos:** *positive*, *negative*, *neutral*, com saída por **softmax**

**Detalhe relevante para nós:** o modelo é `uncased`, isto é, converte tudo para minúsculas antes
de processar. Isso o torna **imune** ao problema de caixa alta que documentamos na Seção 4.j da
dissertação — as 21.619 manchetes em CAIXA ALTA do nosso corpus quebram o FinBERT-PT-BR
justamente porque este é `cased`. É uma decisão de projeto que o autor brasileiro não replicou.

## 5. Resultados declarados

Superação do estado da arte anterior em todas as métricas medidas, sobre dois conjuntos de análise
de sentimento financeiro, com eficiência amostral superior — ou seja, atinge bom desempenho com
menos exemplos rotulados que os métodos concorrentes.

## 6. Ligação com a nossa pesquisa

| Aspecto | Araci (2019) | Santos et al. (2023) — o nosso |
|---|---|---|
| Base | `bert-base-uncased` | BERTimbau (`cased`) |
| Corpus de adaptação | 1,8 milhão de notícias | 1,4 milhão de textos |
| Rotulados para ajuste | 4.846 (16 anotadores) | 503 (anotação própria) |
| Sensível a caixa | Não — imune ao nosso *bug* | **Sim** — vulnerável |
| Downloads/mês | 4.459.091 | ~170.000 |

**Santos et al. (2023) replicaram o desenho de Araci para o português.** A diferença decisiva está
no volume de dados rotulados: 4.846 contra 503, quase dez vezes menos. Esse é um candidato
plausível a explicar parte da distância de desempenho, e é uma hipótese que a dissertação pode
enunciar com apoio documental.

## 7. Leitura crítica

**O que aproveitar:**
- A decisão `uncased` é uma correção barata e testável para o nosso problema de caixa alta:
  normalizar tudo para minúsculas antes de classificar, em vez de tentar preservar siglas.
- O trabalho é uma dissertação de mestrado com 778 citações e 4,5 milhões de downloads mensais.
  Serve de precedente sobre o alcance possível de um trabalho desta natureza.

**O que não aproveitar:**
- O corpus é de 2008–2010. Há aí um problema de deriva conceitual (*concept drift*) que
  Imai et al. (2024) documentam e que se aplica igualmente ao nosso caso.

**O que verificar antes de citar:**
- A contagem de 778 citações é da Semantic Scholar. Se a dissertação preferir a cifra do Google
  Scholar, é preciso consultá-la diretamente e declarar a base.
