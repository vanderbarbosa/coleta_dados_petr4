# 03 · Abílio, Coelho e Silva (2024) — NER financeiro em PT-BR (BraFiNER)

> **O único da lista publicado em periódico de alto impacto, e o único com dataset + código
> integralmente públicos sob licença MIT.** A tarefa é NER, não sentimento — mas o trabalho
> entrega três coisas que usamos diretamente: evidência de que **monolíngue supera multilíngue**
> em domínio financeiro PT-BR, uma **advertência crítica sobre modelos generativos**, e um
> **corpus financeiro brasileiro** que pode alimentar a nossa adaptação de domínio.
>
> Fonte: leitura integral do *preprint* arXiv (46 páginas), versão idêntica à publicada.

---

## 1. Ficha bibliográfica

| Campo | Valor |
|---|---|
| **Referência** | ABÍLIO, R.; COELHO, G. P.; SILVA, A. D. Evaluating Named Entity Recognition: a comparative analysis of mono- and multilingual transformer models on a novel Brazilian corporate earnings call transcripts dataset. **Applied Soft Computing**, 2024. |
| **DOI** | 10.1016/j.asoc.2024.112158 · **arXiv:2403.12212** |
| **Veículo** | Applied Soft Computing (Elsevier) — periódico de alto fator de impacto |
| **Data** | 18/03/2024 |
| **Instituição** | UNICAMP (Coelho e Silva — FT/UNICAMP) |
| **Código e dados** | ✅ **https://github.com/rsabilio/NerEval-BrazilianCorporateTranscripts** — licença **MIT**, último *push* 24/01/2025 |
| **Arquivo local** | `../_abilio2024.pdf` · `../_abilio2024.txt` |

---

## 2. Objetivo e pergunta de pesquisa

Duas perguntas explícitas:

1. Como se comportam modelos **monolíngues** (BERTimbau, PTT5) e **multilíngues** (mBERT, mT5)
   numa tarefa de **reconhecimento de entidades nomeadas** no domínio financeiro brasileiro?
2. **Quais são os requisitos computacionais** de ajuste fino e de inferência de cada um?

Contribuição adicional: propõem uma abordagem que **reformula a classificação de tokens como
problema de geração de texto** (para os modelos T5).

---

## 3. Dados — o corpus BraFiNER

| Item | Valor |
|---|---|
| **Nome** | **BraFiNER** — Brazilian Financial NER |
| **Fonte** | Transcrições de *earnings calls* (teleconferências de resultados) de **bancos brasileiros** |
| **Seleção** | Revisaram os dados abertos da **CVM** e identificaram **29 bancos ativos**; visitaram os sites de RI para verificar disponibilidade das transcrições |
| **Formato original** | PDF |
| **Período** | 2006–2023 |
| **Anotação** | **Supervisão fraca** (*weakly supervised*), esquema **BIO** |
| **Duplicatas removidas** | 10.833 sentenças duplicadas |
| **Tokens (entrada)** | 2.004.673 |

Bancos incluídos (amostra da Tabela 2): ABCB, BMGB, BPAN, BRSR, ITUB, NU (Nu Holdings), PRBC,
SANB — mistura de privados e estatais.

> 💡 **Por que isso interessa a nós.** É **corpus financeiro em português brasileiro, público e
> de acesso livre**. Duas aplicações possíveis:
> 1. **Enriquecer o corpus da adaptação de domínio (G3)**. As nossas ~205 mil notícias são de
>    portais jornalísticos; as *earnings calls* trazem o **registro falado e técnico** da
>    linguagem corporativa financeira — vocabulário que o modelo não vê em manchete.
> 2. **Como corpus de controle** — medir a perplexidade do nosso modelo adaptado também neste
>    corpus, para verificar se a adaptação ao subdomínio Petrobras degradou o desempenho no
>    domínio financeiro geral (teste de *catastrophic forgetting*).

**Ferramentas de processamento declaradas:**

| Ferramenta | Uso |
|---|---|
| **`pdfplumber`** | Extração de texto dos PDFs |
| **`NLTK`** | Segmentação em sentenças |
| **`spaCy`** | Processamento linguístico |
| **`doccano`** | Interface de anotação |
| **`datasets`** (HuggingFace) | Estruturação do corpus |

> 💡 **`doccano` é diretamente aproveitável.** É uma interface web de anotação de texto, de
> código aberto, com suporte a múltiplos anotadores e cálculo de concordância. **Quando a
> rotulagem for retomada (gap G5), é a ferramenta certa** — resolve a dupla anotação, que hoje
> fazemos em planilha Excel (`conjunto_ouro_para_rotular.xlsx`).

---

## 4. Tecnologias, bibliotecas e encoders

### 4.1 Os quatro modelos comparados

| Arquitetura | Modelo | Idioma | Versão | Parâmetros |
|---|---|---|---|---|
| BERT (*encoder*) | **BERTimbau** | Português | Base | 110M |
| BERT (*encoder*) | **mBERT** | Multilíngue | Base | 110M |
| T5 (*encoder-decoder*) | **PTT5** | Português | Base | 220M |
| T5 (*encoder-decoder*) | **mT5** | Multilíngue | Small | 300M |

Critério de seleção declarado: versões **recomendadas pelos autores originais**, com número
comparável de parâmetros, e as menores variantes por restrição de infraestrutura.

### 4.2 Diferença de *tokenizer* documentada

| Modelo | *Tokenizer* | Vocabulário | Marcação |
|---|---|---|---|
| BERT | **WordPiece** | — | `##` para subpalavras (`Santa` + `##nder`); `[CLS]` e `[SEP]` |
| PTT5 | **SentencePiece** | 32.100 | `_` antes de cada palavra; `</s>` no fim |
| mT5 | SentencePiece | **250.100** | idem |

Interseção entre os vocabulários de PTT5 e mT5: **14.459 subpalavras** — quase o mesmo número
da interseção entre BERTimbau e mBERT, apesar de o vocabulário do mT5 ser **7,8× maior**.

Razão subpalavras/tokens (quanto menor, melhor o encaixe do vocabulário no domínio):

| Modelo | Entrada | Alvo |
|---|---|---|
| **PTT5** | **1,16** | 1,53 |
| mT5 | 1,58 | 1,70 |

> 💡 **Métrica que podemos usar e que quase ninguém usa.** A **razão subpalavras/tokens** é um
> diagnóstico barato e objetivo de quão bem o vocabulário de um encoder cobre o nosso domínio.
> Calcular isso para FinBERT-PT-BR, BERTimbau e Albertina sobre o nosso corpus de PETR4 daria,
> em minutos e **sem gabarito nenhum**, uma justificativa quantitativa para a escolha do
> encoder — algo que hoje não temos.

---

## 5. Método e hiperparâmetros

### 5.1 Ajuste fino dos modelos BERT

| Hiperparâmetro | Valor |
|---|---|
| *Batch size* | 16 |
| Épocas | 2 |
| Taxa de aprendizado | **5e-5** (valor padrão do `TrainingArguments` do HuggingFace) |
| Justificativa declarada | Alinhado a Devlin et al. (2018) e adequado à infraestrutura |
| GPU | **NVIDIA T4, 15 GB** |

### 5.2 Ajuste fino dos modelos T5

| Hiperparâmetro | Valor |
|---|---|
| *Batch size* | 8 |
| Épocas | 2 |
| Comprimento máximo | 512 (definido para evitar truncamento — o máximo observado foi 509) |
| GPUs | T4 e **A100** |

### 5.3 Avaliação

Inferência com *batch* 16, sobre cinco subconjuntos do conjunto de teste; reportam **média e
desvio-padrão** — bom padrão, que devemos imitar.

---

## 6. Resultados completos

### 6.1 Custo de ajuste fino

| Modelo | GPU | Memória (GB) | Tempo (min) | Precisão | *Recall* | F1 |
|---|---|---|---|---|---|---|
| **BERTimbau** | T4 | **11,2** | **14** | 0,9970 | 0,9985 | **0,9978** |
| mBERT | T4 | — | — | — | — | ligeiramente inferior |
| PTT5 | T4 | 14,2 | 180 | 0,9917 | 0,9920 | 0,9919 |
| PTT5 | A100 | 15,8 | 150 | 0,9915 | 0,9901 | 0,9908 |
| mT5 | A100 | **33,5** | 107 | 0,9922 | 0,9930 | 0,9926 |

### 6.2 Custo de inferência — a diferença mais expressiva

| Modelo | Tempo médio de inferência | Memória |
|---|---|---|
| **BERTimbau** | **16,04 s (± 3,58 s)** | **3,7 GB** |
| mBERT | — | 4,4 GB |
| mT5 | — | 4,4 GB |
| **PTT5** | **338,14 s (± 43,57 s)** ≈ 28 min | **12,4 GB** |

> **O PTT5 é ~21× mais lento e consome ~3,4× mais memória que o BERTimbau**, para desempenho
> equivalente ou pior.

### 6.3 Desempenho final

| Modelo | Precisão média | F1-macro médio | Desvio-padrão |
|---|---|---|---|
| **BERTimbau** | **99,44%** | **98,99%** | **0,64% / 0,48%** — os menores |

**Conclusões dos autores:**

1. Modelos **baseados em BERT superam consistentemente** os baseados em T5.
2. Entre monolíngue e multilíngue: **BERTimbau supera o mBERT** em F1 **e** em recursos
   computacionais.
3. Entre os T5, mT5 supera o PTT5 em métricas de desempenho.
4. ⚠️ **PTT5 e mT5 geraram sentenças com alteração de valores monetários e percentuais** — os
   autores destacam "a importância da acurácia e da consistência no domínio financeiro".

---

## 7. Código

✅ **Público, MIT:** https://github.com/rsabilio/NerEval-BrazilianCorporateTranscripts

Estrutura do repositório:

```
0-transcripts/
  ├─ extract-and-preprocess.ipynb     ← extração de PDF + pré-processamento
  └─ pdf-files/                       ← os PDFs originais das earnings calls
                                        (ex.: abcb-2008-1T08-...pdf)
```

O *notebook* `extract-and-preprocess.ipynb` é o que interessa: mostra a pipeline completa
`pdfplumber → NLTK → sentenças → anotação`. **É diretamente reaproveitável** se decidirmos
incorporar *earnings calls* da Petrobras ao corpus de adaptação de domínio.

---

## 8. Leitura crítica

### 8.1 Como o trabalho cita Santos (contexto verificado)

Três citações, todas na Seção 2.1:

> *"Examples of these models include FinBERT [27], **FinBERT PT-BR [28]**, and FLANG-BERT and
> FLANG-ELECTRA [29]."*
>
> *"The **FinBERT-PT-BR [28]** model is based on BERTimbau [22] (…) the authors continued the
> pre-training of BERTimbau by adding news from the Brazilian financial market."*
>
> *"Besides, **unlike Santos et al. [28]**, our dataset comprises text from earnings call
> transcripts for NER, while they used financial news for Sentiment Analysis."*

**Função:** posicionar o FinBERT-PT-BR numa taxonomia internacional (ao lado do FinBERT-EN e da
família FLANG) e **delimitar a própria contribuição por contraste**. O Semantic Scholar
classifica a intenção como `methodology` — a única assim classificada entre os sete citantes.

### 8.2 O que aproveitar

| # | O que | Como usar | Gap |
|---|---|---|---|
| 1 | **Evidência mono > multilíngue em domínio financeiro PT-BR**, em periódico de alto impacto | Sustentar a escolha por FinBERT-PT-BR/BERTimbau contra XLM-R e mDeBERTa — hoje a nossa justificativa é só teórica | **G3** |
| 2 | **Advertência sobre modelos generativos alterarem valores numéricos** | Contraponto obrigatório na discussão do gap G6 (LLM × encoder) | **G6** |
| 3 | **Corpus BraFiNER** (público, MIT) | Enriquecer o corpus de MLM e/ou servir de corpus de controle contra esquecimento | **G3** |
| 4 | **`doccano`** para anotação | Substituir a planilha Excel quando a rotulagem for retomada — resolve dupla anotação e concordância | **G5** |
| 5 | **Razão subpalavras/tokens** | Diagnóstico barato e sem gabarito da adequação do vocabulário ao nosso domínio | G3 |
| 6 | **Reportar custo computacional junto com desempenho** | Tabela de memória e tempo por modelo — a nossa comparação de encoders não reporta isso | G12 |
| 7 | **Média ± desvio sobre 5 subconjuntos** | Padrão de reporte que devemos imitar | G12 |
| 8 | **O padrão retórico da citação** | *"unlike Santos et al., our… while they…"* — a nossa dissertação precisa da mesma frase | — |

### 8.3 O que **não** aproveitar

| Item | Por quê |
|---|---|
| **A tarefa (NER)** | Tarefa diferente. Aplicar NER exigiria novo corpus anotado — está na lista de "não perseguir". Interessante para o doutorado. |
| **Os F1 de ~0,99** | São altíssimos porque a anotação é por **supervisão fraca** (regras), o que torna a tarefa parcialmente circular: o modelo aprende a regra do anotador. Não comparar com os nossos números de sentimento, que vêm de gabarito humano. |

### 8.4 Uma fragilidade a não repetir

O F1 de 0,9978 em NER com anotação por supervisão fraca merece ceticismo: quando o gabarito é
gerado por regras determinísticas, um modelo suficientemente capaz aprende **a regra**, e não a
tarefa. Os autores não discutem esse limite.

> **Lição para nós:** é um argumento a favor do nosso gabarito humano, ainda que pequeno e com
> anotador único. **Vale explicitar essa comparação na dissertação** — 300 itens anotados por
> humano dizem mais sobre a tarefa real do que milhares anotados por regra.

### 8.5 Como citar

> *"A superioridade de encoders monolíngues sobre multilíngues no domínio financeiro em
> português brasileiro é documentada por Abílio, Coelho e Silva (2024), que reportam F1-macro de
> 98,99% para o BERTimbau contra desempenho inferior do mBERT, com menor consumo de memória e
> tempo. Os mesmos autores registram que modelos generativos (PTT5 e mT5) produziram sentenças
> com alteração de valores monetários e percentuais, o que recomenda cautela na substituição de
> encoders por modelos generativos em pipelines financeiros."*

---

## Anexo — quadro-resumo

| | |
|---|---|
| **Objetivo** | Comparar encoders mono/multilíngues em NER financeiro PT-BR + medir custo computacional |
| **Corpus** | **BraFiNER** — *earnings calls* de bancos brasileiros, 2006–2023, anotação BIO por supervisão fraca |
| **Encoders** | BERTimbau, mBERT, PTT5, mT5 |
| **Bibliotecas** | `pdfplumber`, NLTK, spaCy, **doccano**, `transformers`, `datasets` |
| **Hiperparâmetros** | BERT: batch 16, 2 épocas, lr 5e-5 · T5: batch 8, 2 épocas, 512 tokens |
| **Infraestrutura** | NVIDIA T4 (15 GB) e A100 |
| **Resultado** | BERTimbau: F1-macro **98,99%**, 16 s de inferência, 3,7 GB · PTT5: 28 min, 12,4 GB |
| **Achado crítico** | **T5 alterou valores monetários e percentuais** |
| **Código** | ✅ **MIT** — github.com/rsabilio/NerEval-BrazilianCorporateTranscripts |
| **Valor para nós** | **Alto** — sustenta a escolha do encoder, dá corpus adicional e a ferramenta de anotação |
