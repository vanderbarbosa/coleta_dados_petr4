# O dataset do Santos, o e-mail correto e um bug real no nosso pipeline

**Elaborado em:** 08/08/2026 · A partir dos links que você localizou

---

## Resumo do que mudou

| # | Achado | Impacto |
|---|---|---|
| 1 | **O dataset dos 503 textos rotulados ESTÁ publicado** | Resolve boa parte do gap G5 e destrava a comparação direta |
| 2 | **O e-mail correto é `lucaslssantos99@gmail.com`** | O do artigo (@usp.br) está morto — daí o retorno |
| 3 | **Nosso uso do encoder está correto** quanto ao pipeline | `"sentiment-analysis"` é alias de `"text-classification"` |
| 4 | ⚠️ **BUG REAL: 21.619 manchetes em CAIXA ALTA** contra um modelo *cased* | 10,5% do corpus mal classificado — mecanismo comprovado |
| 5 | ⚠️ **Unidade de texto errada**: alimentamos 13 palavras onde o modelo viu 39 | Explica parte da queda de 0,76 para 0,58 |

---

# 1. O dataset — o que ele contém

**https://huggingface.co/datasets/lucas-leme/Sentiments-FinBERT-PT-BR**
Arquivo `sentiments.csv`, licença Apache 2.0, 3.170 *downloads*, última alteração em 12/05/2025.
Baixado para `orientacoes/_santos_sentiments.csv`.

**661 linhas, 3 colunas** (`Unnamed: 0`, `text`, `sentiment`):

| Rótulo | n |
|---|---|
| Negativo | 203 |
| Positivo | 160 |
| Neutro | 140 |
| **Subtotal — a base de treino de 503** | **503** |
| Não se aplica | 158 |
| **Total** | **661** |

> Os 503 batem **exatamente** com o artigo. Os 158 "Não se aplica" são parte dos 497
> descartados; os demais foram descartados por falta de concordância e não estão no arquivo.

**O README também confirma, agora em fonte primária, tudo o que havíamos reconstruído:** três
anotadores, todos os textos anotados por ao menos dois, quatro categorias, a instrução literal
de anotação, etapa de calibração prévia, 90,4% de concordância e α de Krippendorff de 0,88.

## 1.1 O que isso destrava

| Uso | Observação |
|---|---|
| **Comparar a nossa distribuição com a dele** | Já feito — ver Seção 3 |
| **Ampliar o nosso conjunto de treino** | 503 exemplos rotulados por 3 pessoas, com α = 0,88 — qualidade muito superior à do nosso gabarito de anotador único |
| **Treinar o comitê (G7) e o ajuste fino (G3)** | Passa a haver base rotulada de verdade, sem depender da rotulagem suspensa |
| **Aprender com a categoria "Não se aplica"** | 158 exemplos do que o modelo **nunca viu**, e que no nosso corpus é maioria |

> ⚠️ **Cuidado obrigatório: estes 503 são a base de TREINO do modelo.** Avaliar o
> FinBERT-PT-BR sobre eles é contaminado — ele já os viu. Servem para **treinar** e para
> **caracterizar o domínio de origem**, nunca para medir desempenho.

## 1.2 O e-mail correto

O artigo do BWAIF traz `lucaslssantos99@usp.br` — que é o que deu retorno. O README do dataset
traz **`lucaslssantos99@gmail.com`**, e é o endereço que ele mantém atualizado (o dataset foi
alterado em maio de 2025).

**Reenvie para o gmail.** O rascunho em `CONTATO_LUCAS_LEME_rascunho.md` continua válido, com
dois ajustes:

- **Remova o pedido nº 2** (a base rotulada) — já está pública. Substitua por um agradecimento:
  *"localizei o dataset publicado no Hugging Face, que já me foi de grande valia"*. Isso mostra
  que você pesquisou antes de pedir.
- **Mantenha os pedidos 1, 3 e 4** (código de treinamento, guia de anotação detalhado e o
  *checkpoint* do modelo de linguagem puro).

O pedido do LinkedIn continua sendo boa ideia — é onde ele está mais ativo.

---

# 2. Estamos usando o encoder corretamente?

## 2.1 O pipeline em si: sim, está correto

**Nosso código** ([`03_analise_sentimento_bertimbau_petr4.py:171`](../src/sentimento/03_analise_sentimento_bertimbau_petr4.py#L171)):

```python
modelo_nlp = pipeline(
    task       = "sentiment-analysis",
    model      = NOME_MODELO,
    tokenizer  = NOME_MODELO,
    max_length = 512,
    truncation = True,
    device     = device_id,
)
```

**Model card oficial:**

```python
pipe = pipeline("text-classification", model="lucas-leme/FinBERT-PT-BR")
```

> **`"sentiment-analysis"` é um alias de `"text-classification"` na biblioteca
> `transformers`** — as duas *strings* instanciam exatamente a mesma
> `TextClassificationPipeline`. Não há diferença funcional.
>
> A forma alternativa do *model card* (`AutoModelForSequenceClassification` +
> `AutoTokenizer`) é a construção manual do mesmo objeto. **Nosso uso é equivalente e
> correto**, e ainda passa `truncation` e `max_length` explicitamente, o que é boa prática.

Uma diferença menor: classificamos **um texto por vez**
(`modelo_nlp(texto)[0]`, linha 305) em vez de passar listas em lote. Isso não afeta o
resultado, só a velocidade — e o Bloco 8 já processa em lotes de 32 no nível do laço.

## 2.2 Mas há dois problemas reais — e não estavam no pipeline

---

# 3. ⚠️ Problema 1: manchetes em CAIXA ALTA contra um modelo *cased*

## 3.1 O que encontramos

O portal **Petronoticias publica 100% das manchetes em caixa alta**:

> `COBRA, CSE E ENESA SÃO AS VENCEDORAS DA LICITAÇÃO PARA MANUTENÇÃO DAS PLATAFORMAS...`
> `CNPE CONFIRMA DIREITO DE PREFERÊNCIA DA PETROBRÁS EM TRÊS ÁREAS DO PRÉ-SAL`

| Fonte | Notícias | % em caixa alta |
|---|---|---|
| **WP_Petronoticias** | **21.619** | **100,0%** |
| WP_Exame | 41.035 | 0,0% |
| WP_InfoMoney | 39.352 | 0,0% |
| WP_MoneyTimes | 67.400 | 0,0% |
| WP_Poder360 | 36.291 | 0,0% |
| **Total** | **205.697** | **10,5%** |

## 3.2 Por que isso quebra o modelo

O `tokenizer_config.json` do FinBERT-PT-BR declara **`"do_lower_case": False`**. É um modelo
***cased***, herdado do `bert-base-portuguese-cased`. Para ele, `PETROBRAS` e `Petrobras` são
sequências completamente diferentes.

**Verificação no vocabulário publicado (29.795 tokens):**

| Palavra | CAIXA ALTA | Capitalizada | minúscula |
|---|---|---|---|
| petrobras | ❌ | ✅ | ❌ |
| gasolina | ❌ | ❌ | ✅ |
| lucro | ❌ | ❌ | ✅ |
| produção | ❌ | ✅ | ✅ |
| preço | ❌ | ❌ | ✅ |
| petróleo | ❌ | ❌ | ✅ |
| energia | ❌ | ✅ | ✅ |
| mercado | ❌ | ✅ | ✅ |

> **Nenhuma das doze palavras-chave do domínio existe em caixa alta no vocabulário.** Todas
> são fragmentadas em subpalavras que o modelo raramente viu.

**Cobertura de vocabulário (palavras inteiras encontradas no vocab):**

| Texto | Cobertura |
|---|---|
| Petronoticias, como está | **22,2%** |
| InfoMoney (caixa normal) | 78,6% |
| Petronoticias após normalizar | **77,6%** |

## 3.3 O efeito medido

**No corpus completo** — o modelo praticamente desiste de classificar essas notícias:

| | Negative | Neutral | Positive | Confiança média |
|---|---|---|---|---|
| Caixa normal (184.078) | 53,5% | 32,0% | 14,5% | 0,697 |
| **CAIXA ALTA (21.619)** | **6,1%** | **84,3%** | 9,6% | **0,589** |

**No conjunto-ouro** — onde há gabarito para confrontar:

| Recorte | n | Acurácia | F1-macro | Kappa |
|---|---|---|---|---|
| Caixa normal | 264 | 0,587 | 0,585 | **0,386** |
| **CAIXA ALTA** | **36** | **0,528** | 0,487 | **0,195** |

E o humano **não** achou essas manchetes neutras: dos 36 casos, o modelo disse 24 neutras, mas o
humano marcou apenas 17 — e apontou 13 positivas contra as 8 do modelo.

> **Uma fonte inteira do corpus está sendo despejada na classe neutra por um problema de
> tokenização, e não por ser neutra.** São 21.619 notícias — 10,5% do corpus — que entram no ISM
> como ruído estruturado.

## 3.4 A correção

Script pronto: [`src/sentimento/normalizar_caixa_titulos.py`](../src/sentimento/normalizar_caixa_titulos.py).
Já executado — gerou `Mestrado_PETR4/noticias_titulos_normalizados.csv`.

Quatro estratégias avaliadas por cobertura de vocabulário:

| Estratégia | Cobertura |
|---|---|
| como está | 22,3% |
| `.title()` | 56,4% |
| **`.capitalize()` com siglas preservadas** | **77,6%** ← adotada |
| `.lower()` | 78,2% |
| *(referência: fonte em caixa normal)* | *78,4%* |

Adotou-se `.capitalize()` preservando siglas do domínio (ANP, OPEP, CNPE, CADE, FPSO, GLP…):

```
ANTES : CNPE CONFIRMA DIREITO DE PREFERÊNCIA DA PETROBRÁS EM TRÊS ÁREAS DO PRÉ-SAL
DEPOIS: CNPE confirma direito de preferência da petrobrás em três áreas do pré-sal
```

> ⚠️ **A cobertura de vocabulário é uma aproximação do ganho, não a medida dele.** A validação
> definitiva é reclassificar as 36 manchetes do gabarito e comparar acurácia e kappa contra os
> atuais (0,528 e 0,195). **Isso exige GPU** — o torch local segue inoperante.
>
> Note também que a normalização perde maiúsculas de nomes próprios ("petrobrás", "petrogal").
> Um dicionário de nomes próprios do domínio melhoraria marginalmente, mas a cobertura já
> empata com a das fontes em caixa normal.

---

# 4. ⚠️ Problema 2: estamos alimentando o modelo com a unidade de texto errada

Este é o achado que o dataset permitiu comprovar, e que antes era só hipótese.

## 4.1 Os textos de Santos não são manchetes

```
"O aumento de preços do etanol em novembro decorreu da proximidade da entressafra
 da cana-de-açúcar, que se inicia em dezembro, diz Eulina."

"RIO – A Transpetro recebe segunda-feira, no Estaleiro Mauá, na cidade fluminense
 de Niterói, o navio de produtos Celso Furtado, a primeira embarcação do Programa
 de Modernização..."
```

São **sentenças de corpo de notícia**. As nossas são **manchetes**.

| Corpus | Mediana | Média | q25 | q75 |
|---|---|---|---|---|
| **Santos (503 de treino)** | **39 palavras** | 39,8 | 24 | 54 |
| **Nosso — só `Título`** | **13 palavras** | 13,1 | 11 | 15 |
| Nosso — `Título` + `Resumo` | **42 palavras** | 49,0 | 30 | 70 |

> **Os textos com que o modelo foi treinado são 3× mais longos do que os que lhe damos.**
> Apenas **80 de 503 (15,9%)** dos exemplos de treino têm 15 palavras ou menos.
>
> **E `Título` + `Resumo` dá mediana de 42 palavras — praticamente idêntica aos 39 de Santos.**

## 4.2 Por que isso importa

Um classificador de sentimento treinado em sentenças completas aprende a apoiar-se em estrutura
sintática, conectivos e contexto. A manchete remove tudo isso: é elíptica, usa jogo de palavras
e omite o sujeito. É plausível que boa parte da queda de 0,76 para 0,58 venha daí — e agora há
como testar.

Isso conecta com dois achados anteriores:

- Manchetes **longas** já apresentavam desempenho pior (>14 palavras → 0,516 contra 0,625 nas de
  até 8). Confundido com o tema, mas coerente.
- A confiança do modelo **nunca passa de 0,856** nas nossas 300 manchetes.

## 4.3 O experimento a rodar

**É o gap G9, e agora com uma hipótese precisa e uma expectativa quantificada.** Classificar o
conjunto-ouro em três granularidades e comparar contra o mesmo gabarito humano:

| Configuração | Mediana de palavras | Expectativa |
|---|---|---|
| `Título` (atual) | 13 | 0,580 (medido) |
| **`Título` + `Resumo`** | **42** | **mais próximo do regime de treino** |
| `Título` + primeiro parágrafo | — | a medir |

O gabarito humano **continua válido** para as três: o rótulo é do evento noticioso, não do
recorte de texto. **Não consome rotulagem nova.**

> Se a hipótese estiver certa, `Título + Resumo` deve superar `Título` isolado de forma
> relevante. Se não estiver, também é resultado — e fecha a justificativa formal do nosso
> recorte, que hoje não existe na dissertação.

---

# 5. O que fazer, em ordem

| # | Ação | Custo | Depende de GPU? |
|---|---|---|---|
| 1 | **Reenviar o e-mail** para `lucaslssantos99@gmail.com`, sem o pedido nº 2 | 10 min | Não |
| 2 | **Reclassificar o conjunto-ouro com títulos normalizados** e medir o ganho nas 36 em caixa alta | 1 h | **Sim** |
| 3 | **Ablação de granularidade** (`Título` × `Título+Resumo`) sobre o gabarito | 2 h | **Sim** |
| 4 | Se 2 e 3 confirmarem: **reprocessar o corpus e refazer o ISM** | 6–8 h | **Sim** |
| 5 | **Recalibrar o ISM** com a nova matriz de confusão | 30 min | Não |
| 6 | Usar os **503 textos de Santos** para treinar o comitê (G7) e o ajuste fino (G3) | — | **Sim** |

> **Os itens 2, 3 e 4 são pré-requisito de tudo o que veio antes.** Todos os números que
> medimos — 0,580 de acurácia, o viés de 87% do ISM, a matriz de confusão — foram obtidos com
> um corpus que contém 10,5% de texto mal tokenizado e com a unidade de texto errada. **Não são
> inválidos, mas são um piso.** É provável que melhorem, e é honesto dizer isso na dissertação.

## 5.1 Como apresentar isso na mentoria

Não como erro escondido, mas como o que é — **auditoria que encontrou o que tinha de encontrar**:

> *"Ao localizar o conjunto de dados original publicado pelo autor do modelo, foi possível
> caracterizar o domínio de treino e compará-lo ao nosso. Duas incompatibilidades foram
> identificadas e corrigidas: 10,5% do corpus é publicado em caixa alta por uma das fontes, o
> que degrada a tokenização de um modelo *cased* — a cobertura de vocabulário cai de 78,6% para
> 22,2% —, e a unidade de texto empregada (manchete, mediana de 13 palavras) difere da unidade
> de treino do modelo (sentença de corpo de notícia, mediana de 39 palavras). As métricas
> reportadas até aqui devem, portanto, ser lidas como limite inferior."*

---

## Anexo — arquivos desta rodada

| Arquivo | Conteúdo |
|---|---|
| `orientacoes/_santos_sentiments.csv` | Os 661 textos rotulados de Santos (503 de treino + 158 NSA) |
| `src/sentimento/normalizar_caixa_titulos.py` | Correção de caixa alta, com preservação de siglas |
| `Mestrado_PETR4/noticias_titulos_normalizados.csv` | Corpus com os 21.619 títulos corrigidos |
| `Mestrado_PETR4/normalizacao_caixa_relatorio.json` | Contagens e cobertura antes/depois |
