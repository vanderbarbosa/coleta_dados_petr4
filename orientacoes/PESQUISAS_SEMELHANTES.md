# Pesquisas que fazem o mesmo que a nossa — e o que dá para adaptar

**Data:** 18/08/2026 · **Origem:** mentoria com o Prof. Emerson
**Pedido:** *"procurar outras pesquisas que estão fazendo o mesmo que eu — ler notícias e tentar
prever a direção e a volatilidade que essas notícias possam causar — independentemente do ativo e de
ser ou não em português. Encontrar pesquisas semelhantes e saber se podemos usá-las/adaptá-las para
melhorar os índices."*

---

## Correção prévia, antes da tabela

A tabela comparativa que você montou traz **"54,93% com ponderação por confiança Softmax"**. Esse
número foi revisado em 17/08 e **não se sustenta**, por duas razões:

- Ele é acurácia de **validação**, não de teste. No conjunto de teste a ponderação rende
  **50,31%**, contra **53,88%** da polaridade pura — ou seja, ponderar **piora**.
- O escore não é *softmax*: 397 manchetes têm confiança abaixo de 0,3333, piso matemático de um
  *softmax* de três classes. É sigmoide.

A Seção 4.n da dissertação já traz a correção. **Use 54,5% (XGBoost, três atributos), sem a menção
à ponderação.**

---

## Parte 1 — O que a busca encontrou

Seis trabalhos fazem, em alguma medida, o que esta pesquisa faz. Estão ordenados por proximidade.

### 1.1 Hashamia e Maldonado (2025) — **o mais próximo de todos**

> *Can News Predict the Direction of Oil Price Volatility? A Language Model Approach with SHAP
> Explanations.* arXiv:2508.20707.
> Código: `github.com/Romina-Hashami/Textual_Direction_Prediction_Oil_Volatility`

| Elemento | Eles | Nós |
|---|---|---|
| Ativo | Futuros de Brent | PETR4 (produtora de petróleo) |
| Corpus | **592.858 manchetes da Reuters**, 2014–2023 | 205.697 manchetes, 2018–2025 |
| Alvo | **direção da volatilidade do dia seguinte** | direção do preço e nível da volatilidade |
| Referência | **HAR** | HAR |
| Teste | **McNemar** | McNemar e Diebold-Mariano |
| Sentimento testado | VADER, TextBlob, FinBERT, **CrudeBERT** | FinBERT-PT-BR |
| *Embeddings* testados | GloVe, FastText, BERT, FinBERT, Gemini, LLaMA | nenhum |
| Regimes | pré-COVID, pandemia, pós-pandemia, Rússia–Ucrânia | não estratificado |

**Três achados deles que importam para nós:**

1. **O alvo é a DIREÇÃO DA VOLATILIDADE**, e não a direção do preço nem o nível da volatilidade.
   É um alvo que nunca testamos, e é mais bem posto que os nossos dois: a direção do preço é quase
   um lançamento de moeda, e o nível da volatilidade o HAR já prevê bem. Perguntar *"amanhã vai
   sacudir mais ou menos que hoje?"* é uma terceira via.
2. **A contagem de notícias superou as medidas de sentimento.** Nós testamos volume de notícias
   como *proxy* de atenção e falhou ($p = 0{,}222$) --- mas testamos contra o **nível** da
   volatilidade, não contra a **direção** dela.
3. **O FastText foi o melhor entre os *embeddings***, superando as cabeças de sentimento. É a
   terceira confirmação independente da linha dos *embeddings*.

**Adaptável?** Sim, e é a recomendação principal. O código é público, o ativo é o mais próximo
possível do nosso, e o alvo é implementável com os dados que já temos.

### 1.2 CrudeBERT (Kaplan et al., 2023) — um BERT do petróleo

> *CrudeBERT: Applying Economic Theory towards fine-tuning Transformer-based Sentiment Analysis
> Models to the Crude Oil Market.* ICEIS 2023, p. 324–334. arXiv:2305.06140.
> Modelo: `Captain-1337/CrudeBERT` (777 transferências/mês)

Trata-se do FinBERT ajustado ao mercado de petróleo. A inovação **não está nos rótulos** --- que
permanecem positivo, negativo e neutro --- e sim na **construção do conjunto de treinamento**: os
autores partiram da teoria econômica de oferta e demanda e montaram a base com manchetes que
representam **choques de oferta e de demanda** na commodity. Reportam superação do FinBERT na
previsão de movimentos do preço do petróleo.

**Adaptável?** O modelo em si, não --- é em inglês. **A ideia, sim, e é valiosa.** Em vez de rotular
manchetes como "positiva" ou "negativa" em abstrato, rotulá-las pelo **mecanismo econômico** que
acionam na PETR4: choque de oferta, choque de demanda, intervenção do controlador, política de
preços de combustíveis, decisão de dividendos. Isso responde de forma direta à objeção do Prof.
Emerson sobre a rotulagem, porque **desloca o critério do juízo subjetivo para a teoria econômica**.

### 1.3 Bodilsen e Lunde (2025) — **o mais credível, e o que gerou o experimento**

> *Exploiting News Analytics for Volatility Forecasting.* Journal of Applied Econometrics,
> v. 40, n. 1, p. 18–36, 2025.

Periódico de primeira linha em econometria aplicada; Asger Lunde é coautor de
Hansen e Lunde (2005), já citado na dissertação. Acrescentam sentimento de notícias a modelos de
volatilidade realizada e chegam a duas conclusões:

1. **Notícia específica da empresa não acrescenta nada** ao que a volatilidade passada já captura.
2. **Notícia macroeconômica melhora de forma significativa**, e a melhora é **substancialmente
   maior em horizontes longos**.

**Isso descreveria exatamente o nosso caso**: o recorte que adotamos --- empresa mais mercado de
petróleo --- é o mais próximo do "específico da empresa", e toda a nossa avaliação foi feita a um
dia de distância. Se eles estivessem certos, teríamos testado a fatia errada do corpus, no prazo
errado. **Fomos verificar.** O resultado está na Parte 2.

### 1.4 Halousková e Lyócsa (2025)

> *Forecasting U.S. equity market volatility with attention and sentiment to the economy.*
> arXiv:2503.19767.

FinBERT com HAR sobre 404 ações do S&P 500, variância realizada de 5 minutos. **Superam o HAR em
98,76% dos casos**, com ganho médio de 12,74% --- e **14,99% nos dias de variação extrema**, o que
confirma o nosso efeito de cauda por via independente. Ficha completa em
[`encoders_ingles/04_HALOUSKOVA_LYOCSA_2025.md`](encoders_ingles/04_HALOUSKOVA_LYOCSA_2025.md).

### 1.5 Mino e Williamson (2025)

> *Sentiment and Volatility in Financial Markets: A Review of BERT and GARCH Applications during
> Geopolitical Crises.* arXiv:2510.16503.

BERT com GARCH(1,1) *t*-Student no S&P 500 --- a mesma especificação do nosso Script 04. Coeficiente
do sentimento de $-0{,}2275$ ($p = 0{,}0016$), contra os nossos $-0{,}2924$ ($p = 0{,}0002$).
Ficha em [`encoders_ingles/05_MINO_WILLIAMSON_2025.md`](encoders_ingles/05_MINO_WILLIAMSON_2025.md).

### 1.6 Rahimikia e Poon — *embeddings* para volatilidade realizada

> *Realised Volatility Forecasting: Machine Learning via Financial Word Embedding.*
> arXiv:2108.00480.

Constroem um *embedding* financeiro próprio e o aplicam à previsão de volatilidade realizada, em vez
de passar por uma cabeça de sentimento. **Quarta confirmação da linha dos *embeddings***.

---

## Parte 2 — Testamos a hipótese de Bodilsen e Lunde nos nossos dados

Script: `src/modelagem/10_macro_vs_empresa_horizontes.py` → `Mestrado_PETR4/macro_vs_empresa.json`

Cruzaram-se cinco recortes do corpus com três horizontes, medindo se o acréscimo do sentimento ao
HAR reduz o erro fora da amostra (795 previsões, janela expansiva, Diebold-Mariano).

**Ganho percentual sobre o HAR (valores positivos = o sentimento ajuda):**

| Recorte | Notícias | 1 dia | 5 dias | 22 dias | **Média** |
|---|---|---|---|---|---|
| **EMPRESA** (CAT1+CAT6) | 71.003 | +1,03% | +0,37% | **+1,77%** | **+1,06%** |
| EMP+PETR (CAT1+CAT2) | 120.792 | +0,30% | −0,43% | +0,21% | +0,03% |
| PETROLEO (CAT2) | 55.910 | −0,12% | −0,48% | −1,06% | −0,55% |
| **MACRO** (CAT3+CAT5+CAT7) | 76.438 | −0,33% | **−1,09%** | **−1,79%** | **−1,07%** |
| TODAS | 205.697 | −0,30% | −1,93% | −2,45% | −1,56% |

**O resultado é o inverso do deles, e de forma estatisticamente detectável.**

- **A notícia MACRO piora a previsão de maneira significativa**: $p = 0{,}0146$ em 5 dias e
  $p = 0{,}0200$ em 22 dias, com o teste favorecendo o HAR puro. Não é ausência de ganho --- é
  prejuízo mensurável.
- **A notícia da EMPRESA é o melhor recorte**, e em 22 dias chega a $+1{,}77\%$ com
  $p = 0{,}0574$ --- o resultado mais próximo de superar o HAR que esta pesquisa já obteve, ainda
  que aquém do limiar convencional.
- **A metade da hipótese que se confirma é a do horizonte**: o melhor desempenho da notícia da
  empresa aparece em 22 dias, não em 1.

**A explicação econômica é plausível e defensável.** Bodilsen e Lunde empregam notícia
macroeconômica **doméstica** aplicada a ações **norte-americanas** --- e a macroeconomia dos Estados
Unidos é determinante direto do preço de uma ação norte-americana. O nosso recorte "macro" é
composto majoritariamente de **geopolítica internacional** (46.412 das 76.438 notícias): guerra na
Ucrânia, sanções, OPEP, tensões no Oriente Médio. Para um ativo brasileiro isolado, isso é
sobretudo ruído.

Some-se a natureza da PETR4. Trata-se de empresa de controle estatal, cujo risco idiossincrático
--- política de preços de combustíveis, intervenção do controlador, trocas de diretoria, política de
dividendos --- domina o risco sistêmico de modo bem mais acentuado do que numa ação típica do
S&P 500. **É razoável que a notícia da empresa carregue, aqui, mais informação do que a macro.**

**Consequência prática:** há tensão a registrar entre este resultado e o da Seção 4.k. Para a
**associação** com a volatilidade, o melhor recorte é CAT1+CAT2. Para a **previsão** fora da
amostra, é CAT1+CAT6. Associação e previsão não premiam o mesmo corte do corpus --- o que é, por si
só, um achado metodológico.

---

## Parte 3 — O que dá para adaptar, em ordem de prioridade

### Prioridade 1 — Mudar o alvo para a DIREÇÃO da volatilidade
*De Hashamia e Maldonado (2025).* Em vez de prever o nível da volatilidade --- em que o HAR é
adversário duríssimo --- prever se amanhã sacudirá **mais ou menos** que hoje. É binário,
interpretável, e nunca foi testado aqui. **Custo: baixo. Os dados já existem.**

### Prioridade 2 — Adotar o recorte EMPRESA e o horizonte de 22 dias
*Do experimento da Parte 2.* É o melhor resultado da pesquisa até agora ($+1{,}77\%$,
$p = 0{,}0574$). Vale investigar horizontes intermediários e verificar se a significância aparece.
**Custo: muito baixo. É rodar o script com outros valores.**

### Prioridade 3 — Testar contagem de notícias contra a direção da volatilidade
*De Hashamia e Maldonado (2025).* A contagem superou o sentimento no estudo deles. Aqui ela falhou
contra o **nível** ($p = 0{,}222$), mas nunca foi testada contra a **direção**. **Custo: baixo.**

### Prioridade 4 — Usar *embeddings* em vez da cabeça de sentimento
*De quatro fontes independentes:* Hashamia e Maldonado (FastText), Rahimikia e Poon, Costa Neto e
Anjos, Pinheiro e outros. Todos os defeitos documentados do FinBERT-PT-BR --- viés de 87%, teto de
0,58, escala sigmoide, ausência de pregões positivos --- estão na **cabeça de classificação**.
Nenhum afeta os *embeddings*. **Custo: médio; exige GPU.**

### Prioridade 5 — Rotular pelo mecanismo econômico, à maneira do CrudeBERT
*De Kaplan et al. (2023).* Substituir "positiva/negativa/neutra" por categorias de choque:
oferta, demanda, intervenção do controlador, política de preços, dividendos. **Responde à objeção
do Prof. Emerson deslocando o critério do juízo subjetivo para a teoria econômica.**
**Custo: médio; exige rotulagem, mas com critério objetivo.**

### Prioridade 6 — Dados intradiários
*De Halousková e Lyócsa (2025), de Schumaker e Chen (2009) e do nosso próprio contraste $P_0$ contra
$P_1$.* Três apoios independentes indicam que o sinal vive no curtíssimo prazo. **Custo: alto;
depende de obter dados intradiários da PETR4.**

---

## Síntese para levar ao Prof. Emerson

1. **Seis trabalhos fazem o mesmo que nós**, três deles publicados em 2025. Dois são sobre petróleo
   especificamente, e um deles tem código público.
2. **Existe um BERT do petróleo** (CrudeBERT), e a ideia por trás dele --- rotular pelo mecanismo
   econômico --- é adaptável ao português.
3. **Testamos a hipótese de um artigo do *Journal of Applied Econometrics* nos nossos dados e deu o
   contrário**, com explicação econômica plausível ligada à natureza estatal da PETR4. É achado
   próprio, e é publicável.
4. **O melhor resultado da pesquisa apareceu nesse teste**: notícia da empresa, horizonte de 22
   dias, $+1{,}77\%$ sobre o HAR ($p = 0{,}0574$).
5. **A recomendação principal é mudar o alvo** para a direção da volatilidade --- terceira via entre
   a direção do preço, que é quase acaso, e o nível da volatilidade, em que o HAR é imbatível.
