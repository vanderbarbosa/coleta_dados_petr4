# 06 · Reichert e Perlin (2025) — Dicionários de sentimento financeiro por ChatGPT

> **A linha de base léxica que nos falta** — o equivalente brasileiro do Loughran-McDonald.
> Marcelo Perlin é professor da Escola de Administração da UFRGS e uma das referências
> brasileiras em finanças quantitativas computacionais (autor dos pacotes `GetHFData`,
> `BatchGetSymbols`/`yfR` e do livro *Analyzing Financial and Economic Data with R*).
>
> ⚠️ **Ficha incompleta por restrição de acesso.** O texto integral está atrás do *paywall* da
> Springer. Este resumo foi montado a partir do **resumo integral verificado** e dos metadados
> das bases. **É, junto com Imai et al. (2024), uma das duas fichas sem texto integral.**
> Obter pelo Portal de Periódicos da CAPES via PUCPR antes da versão final.

---

## 1. Ficha bibliográfica

| Campo | Valor |
|---|---|
| **Referência** | REICHERT, M. H.; PERLIN, M. S. Using ChatGPT for creating multi-language finance related sentiment dictionaries. **Computational Economics**, 2025. |
| **DOI** | 10.1007/s10614-025-11233-3 |
| **Veículo** | Computational Economics (Springer) |
| **Data** | 23/12/2025 |
| **Instituição** | UFRGS — Escola de Administração |
| **Acesso** | ❌ *Paywall* Springer |
| **Palavras-chave declaradas** | *Sentiment* · *Word list* · *Finance* · *LLM* |
| **Código/dicionário** | Não declarado publicamente — verificar no artigo |

---

## 2. Objetivo e pergunta de pesquisa

**Resumo integral, verbatim:**

> *"The finance literature is abundant with applications of text sentiment based on English
> dictionaries. However, a large proportion of financial documents are written in languages
> other than English. As such, **there is a gap in literature for the development of sentiment
> dictionaries in other languages**. Using a reproducible and low cost approach based on
> ChatGPT's API, and with minimal interventions, we attempt to fill this gap with the proposal of
> a **methodology for building finance-related sentiment word lists for any language**."*

**A lacuna que os autores declaram é uma variante da nossa.** Eles: "faltam dicionários de
sentimento financeiro fora do inglês". Nós: "falta validação de modelos neurais de sentimento
financeiro em português, aplicados a ativo específico". **São complementares, não concorrentes**
— e é exatamente por isso que o trabalho serve de linha de base.

---

## 3. Dados e validação

| Item | Valor |
|---|---|
| **Línguas** | Múltiplas — **o português está incluído** |
| **Corpus de validação (PT)** | Os **últimos 50 comunicados do COPOM** (Comitê de Política Monetária do Banco Central) |
| **Comparação declarada** | Contra *"full-text NLP models"* |
| **Resultado declarado** | O dicionário apresentou *"a more balanced sentiment classification profile"* |

> ⚠️ **Ponto a confirmar com o texto integral, e é o mais importante desta ficha.** Se os
> *"full-text NLP models"* comparados **incluírem o FinBERT-PT-BR**, este é o **único trabalho da
> lista que compara o FinBERT-PT-BR diretamente a uma alternativa** — e o resultado **não lhe é
> favorável**. Precisamos saber disso antes da banca, e não durante.

> 💡 **Os comunicados do COPOM são um corpus interessante e que não estamos usando.** São texto
> financeiro brasileiro institucional, datado, público e com impacto direto sobre a taxa de juros
> — logo, sobre a precificação de todas as ações, inclusive a PETR4. Poderiam servir de
> **variável de controle macroeconômica textual** no nosso modelo de volatilidade, embora isso
> amplie o escopo e deva ser avaliado com cuidado.

---

## 4. Metodologia (do que é possível apurar)

| Etapa | Descrição |
|---|---|
| **Tentativa inicial** | *Crowdsourcing* com votantes acadêmicos — **abandonado por inconsistência** |
| **Abordagem adotada** | Classificação de palavras pela **API do ChatGPT** |
| **Justificativa** | A classificação por LLM mostrou-se *"far more flexible and reliable"* que o *crowdsourcing* |
| **Intervenção humana** | *"minimal interventions"* |
| **Reprodutibilidade e custo** | Declarados como *"reproducible and low cost"* |

> 💡 **Este é o achado metodológico mais relevante para o gap G5.** Os autores **tentaram
> anotação humana distribuída e desistiram por inconsistência**, migrando para LLM. É um
> precedente publicado em periódico de economia computacional que sustenta, de forma
> independente, o argumento de que **anotação humana não calibrada produz gabarito ruidoso** —
> que é exatamente o diagnóstico do nosso conjunto-ouro com anotador único.
>
> **Cuidado ao usar esse argumento.** Ele corta os dois lados: reforça a crítica ao nosso
> gabarito atual, e ao mesmo tempo indica que a solução não é necessariamente "mais anotadores
> humanos", mas **anotação assistida por modelo com verificação humana** — que é precisamente o
> que Poursabzi-Sangdeh e Boyd-Graber (2015) propõem com modelagem de tópicos, e o que
> recomendamos no protocolo de retomada da rotulagem.

---

## 5. Resultados

| Achado declarado no resumo | Detalhe |
|---|---|
| Metodologia funciona para **qualquer língua** | Proposta generalizável |
| Validação em português sobre **50 comunicados do COPOM** | — |
| Perfil de classificação **mais equilibrado** que os modelos de texto completo | *"a more balanced sentiment classification profile"* |
| ChatGPT superou *crowdsourcing* em consistência | — |

⚠️ **Números exatos, métricas e a lista dos modelos comparados estão no texto integral.**

---

## 6. Código

Não declarado publicamente. Pontos a verificar ao obter o artigo:

1. O **dicionário em português está disponível**? (Perlin tem histórico de publicar pacotes e
   dados abertos — é provável.)
2. Existe pacote R ou Python associado?
3. **Quais foram exatamente os *"full-text NLP models"* comparados?**
4. Quais métricas foram reportadas na validação com o COPOM?

**Se o dicionário estiver disponível**, a aplicação ao nosso conjunto-ouro é trivial:

```python
# Linha de base léxica — o equivalente PT-BR do Loughran-McDonald
def sentimento_lexico(texto, positivas: set, negativas: set) -> str:
    tokens = normalizar(texto).split()
    p = sum(t in positivas for t in tokens)
    n = sum(t in negativas for t in tokens)
    if p > n:  return "Positive"
    if n > p:  return "Negative"
    return "Neutral"
```

Isso completaria o quadro comparativo do capítulo de resultados com **quatro** abordagens em vez
de duas:

| Abordagem | Status |
|---|---|
| Encoder de domínio (FinBERT-PT-BR) | ✅ Temos — 58,0% / κ 0,371 |
| Comitê de encoders (gap G7) | Script pronto |
| LLM generativo (gap G6) | Script pronto |
| **Dicionário léxico (gap G8)** | **Depende deste artigo** |

---

## 7. Leitura crítica

### 7.1 Como o trabalho cita Santos

❌ **Não verificável.** A citação está registrada por **OpenAlex** e **Semantic Scholar**, mas
nenhuma das duas bases expõe o trecho, e a página pública da Springer não exibe a lista de
referências. Uma consulta à página de resumo não localizou menção a FinBERT no texto visível —
o que **não é prova de ausência**, apenas de que a parte visível não a contém.

**É a única das sete citações que permanece não verificada.** Registrar como tal na dissertação,
em vez de afirmar o que não se conferiu.

### 7.2 O que aproveitar

| # | O que | Como | Gap |
|---|---|---|---|
| 1 | **Dicionário léxico financeiro em português** | Quarta linha de base no capítulo de resultados | **G8** |
| 2 | **O precedente de abandonar *crowdsourcing* por inconsistência** | Sustenta, com fonte de economia computacional, o diagnóstico do nosso gabarito | **G5** |
| 3 | **LLM para classificação como alternativa reprodutível e barata** | Converge com o G6 e amplia a justificativa | **G6** |
| 4 | **A lacuna declarada** ("faltam dicionários fora do inglês") | Complementa a nossa lacuna na introdução | — |
| 5 | **Os comunicados do COPOM como corpus** | Possível variável de controle macroeconômica textual | — |
| 6 | **O nome de Perlin** | Autor de referência em finanças quantitativas no Brasil; citá-lo reforça a ancoragem em finanças, e não só em computação | — |

### 7.3 O que **não** aproveitar

| Item | Por quê |
|---|---|
| **Substituir o encoder pelo dicionário** | Dicionários não capturam negação, ironia nem contexto. O valor é como **linha de base**, não como método principal. |
| **Construir o nosso próprio dicionário** | Escopo grande, e já existe um. Reinventar seria desperdício de tempo até mar/2027. |
| **Afirmar que o dicionário superou o FinBERT-PT-BR** | ⚠️ **Ainda não sabemos** quais modelos foram comparados. Não afirmar antes de ler. |

### 7.4 Ações concretas

| # | Ação | Prazo |
|---|---|---|
| 1 | **Baixar o PDF pelo Portal CAPES/PUCPR** | Antes da versão final |
| 2 | Verificar se os *"full-text NLP models"* incluem o FinBERT-PT-BR | Idem |
| 3 | Verificar se o dicionário PT está disponível para download | Idem |
| 4 | Transcrever o trecho literal da citação a Santos | Idem |
| 5 | Se disponível: aplicar ao conjunto-ouro e incluir na tabela comparativa | Pós-10/08 |

### 7.5 Como citar (formulação cautelosa, dado o acesso parcial)

> *"Reichert e Perlin (2025) propõem uma metodologia reprodutível e de baixo custo para a
> construção de dicionários de sentimento financeiro em qualquer idioma, a partir da API do
> ChatGPT, validando a versão em português sobre os últimos cinquenta comunicados do COPOM. Os
> autores relatam ter abandonado uma tentativa inicial de anotação por crowdsourcing acadêmico
> em razão de inconsistência entre os votantes — observação convergente com a literatura sobre
> concordância entre anotadores (ARTSTEIN; POESIO, 2008)."*

---

## Anexo — quadro-resumo

| | |
|---|---|
| **Objetivo** | Metodologia reprodutível e barata para construir dicionários de sentimento financeiro em qualquer língua |
| **Tecnologia central** | **API do ChatGPT** para classificação de palavras |
| **Abordagem abandonada** | *Crowdsourcing* com votantes acadêmicos — **inconsistência** |
| **Línguas** | Múltiplas, **incluindo português** |
| **Validação (PT)** | Últimos **50 comunicados do COPOM** |
| **Resultado** | Perfil de classificação **mais equilibrado** que modelos de texto completo |
| **Autor de destaque** | **Marcelo Perlin** (UFRGS) — referência em finanças quantitativas no Brasil |
| **Acesso** | ❌ *Paywall* Springer — **obter pela CAPES/PUCPR** |
| **Citação a Santos** | ⚠️ **Registrada pelas bases, não verificada no texto** |
| **Valor para nós** | **Médio-alto** — é a linha de base léxica que falta (G8), pendente de acesso |
