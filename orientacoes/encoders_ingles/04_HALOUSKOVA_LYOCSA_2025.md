# Halousková e Lyócsa (2025) — o trabalho mais importante deste levantamento

> **Por que este documento é o mais relevante da pasta:** este é o trabalho que faz *exatamente* o
> que a nossa dissertação faz — FinBERT para extrair sentimento, HAR como referência de
> volatilidade, avaliação fora da amostra — e que **consegue o que nós não conseguimos**: superar o
> HAR. As diferenças metodológicas que explicam isso são identificáveis, e três delas são
> implementáveis no prazo da dissertação.

## 1. Ficha bibliográfica

| Campo | Conteúdo |
|---|---|
| **Referência** | HALOUSKOVÁ, M.; LYÓCSA, Š. **Forecasting U.S. equity market volatility with attention and sentiment to the economy.** arXiv:2503.19767, 2025. |
| **Codificador** | **FinBERT**, descrito como pré-treinado sobre o *Financial PhraseBank* |
| **Saída do codificador** | Razões de sentimento positivo e negativo, no intervalo de 0 a 1 |

## 2. Desenho experimental

| Elemento | Halousková e Lyócsa (2025) | **Nossa dissertação** |
|---|---|---|
| Ativos | **404 ações do S&P 500** | 1 ativo (PETR4) |
| Período | 10/03/2010 a 24/02/2021 | 2018–2025 |
| Medida de volatilidade | **Variância realizada de retornos de 5 minutos** | Parkinson (máxima/mínima diária) e \|retorno\| |
| Referências | HAR, HAR-M, CSR-HAR | HAR |
| Modelos com sentimento | CSR-S, ALA-S, HAR-S | HAR + ISM |
| Método de combinação | **Regressão de subconjuntos completos; LASSO adaptativo** | Mínimos quadrados com uma variável extra |
| Fontes de sinal | Notícias (WSJ, FT), Google Trends, Wikipédia, Twitter, estimativas de analistas | Notícias apenas |
| Teste de significância | **Model Confidence Set**, 5% | Diebold-Mariano |

## 3. Resultados

| Modelo | Supera o HAR em | Ganho médio de EQM |
|---|---|---|
| **CSR-S** (subconjuntos completos com sentimento) | **98,76% dos casos** | **12,74%** |
| HAR-S (só sentimento geral) | 98,51% | não declarado |
| ALA-S (LASSO adaptativo com sentimento) | 94,31% | 11,79% |
| CSR-A (só atenção) | 90,59% | 8,12% |

**E o dado decisivo:** o maior ganho, de **14,99% em média**, ocorre **nos dias de variação
extrema de preço**.

## 4. As duas leituras que este trabalho impõe à dissertação

### 4.1 A boa notícia: ele confirma o nosso efeito de cauda

A Seção 4.l da dissertação estabeleceu, por meio da divergência entre as correlações de Pearson
($-0{,}1309$, $p < 0{,}0001$) e de Spearman ($-0{,}0268$, $p = 0{,}2367$), que o efeito do
sentimento sobre a volatilidade é um **fenômeno de cauda**: existe nos dias excepcionais e some no
pregão típico. A regressão quantílica havia chegado à mesma conclusão pelo lado do retorno.

Halousková e Lyócsa (2025) chegam **à mesma conclusão** — o ganho concentra-se nos dias de variação
extrema — em outro mercado, em outro idioma, com 404 ativos, dados intradiários e um método
estatístico inteiramente distinto.

**Isso é uma validação externa de peso considerável, e deve ser incorporada à dissertação.** Um
achado obtido em um único ativo brasileiro passa a ter respaldo em um estudo de larga escala no
mercado norte-americano.

### 4.2 A notícia incômoda: eles superam o HAR e nós não

A Seção 4.k reportou que o nosso índice de sentimento **não supera** o HAR de forma significativa
($p = 0{,}6405$ pelo EQM; $p = 0{,}2170$ pela QLIKE). Eles superam em 98,76% dos casos. Quatro
diferenças explicam a distância, e três são acionáveis:

| # | Diferença | Impacto provável | Acionável? |
|---|---|---|---|
| 1 | **Variância realizada intradiária de 5 min** contra Parkinson diário | **Alto.** A medida deles é muito menos ruidosa. Ruído na variável dependente reduz o poder do teste e pode sozinho explicar a não significância. | **Sim** — depende de obter dados intradiários da PETR4 |
| 2 | **404 ativos** contra 1 | **Alto.** Com 404 séries obtém-se poder estatístico que uma série jamais oferece. O "98,76% dos casos" é uma taxa de vitórias entre ativos, estatística que não temos como calcular. | **Sim** — replicar para VALE3, ITUB4, BBDC4, ABEV3 e outros |
| 3 | **Regressão de subconjuntos completos e LASSO adaptativo** contra uma variável extra em MQO | **Médio.** Métodos de combinação e encolhimento extraem sinal que a inclusão ingênua de um regressor não extrai. | **Sim** — é só código, roda localmente |
| 4 | **Atenção somada ao sentimento** (Google Trends, Wikipédia, Twitter) | **Médio.** Testamos volume de notícias como *proxy* de atenção e falhou ($p = 0{,}222$), mas Google Trends é sinal distinto e mais forte. | Parcialmente — Google Trends é gratuito |

**A conclusão honesta:** não há evidência de que o nosso resultado negativo decorra de ausência de
sinal. Ele é compatível com **falta de poder estatístico** — medida ruidosa, um único ativo, método
de combinação simples. Isso não autoriza a afirmar que o sentimento supera o HAR na PETR4; autoriza
a **reformular a limitação** com precisão, indicando o que seria necessário para decidir a questão.

## 5. O que fazer com isto — proposta

**Imediato, sem dados novos:**
- Incorporar o trabalho à dissertação como validação externa do efeito de cauda (Seções 4.k e 4.l).
- Reescrever a limitação da Seção 4.k: em vez de "o sentimento não supera o HAR", dizer "não foi
  possível detectar superação com uma medida diária de volatilidade sobre um único ativo, ao passo
  que a literatura a detecta com medida intradiária sobre 404 ativos".

**Barato e rápido (dias):**
- Implementar a regressão de subconjuntos completos e o LASSO adaptativo sobre os nossos dados
  atuais. É apenas código, roda na máquina local, e testa diretamente a hipótese 3.

**Médio prazo (semanas):**
- Replicar o *pipeline* para cinco a dez ativos líquidos da B3. Responde ao pedido do Prof. Emerson
  de "não focar em um ativo" e ataca a hipótese 2, que é a de maior impacto esperado.
- Avaliar a obtenção de dados intradiários da PETR4 para computar variância realizada.

## 6. Leitura crítica

**O que aproveitar:** tudo o que está na seção 5.

**Cuidado ao comparar:** o período deles (2010–2021) inclui a pandemia de 2020, episódio de
volatilidade extrema que favorece justamente a detecção de efeitos de cauda. O nosso período
(2018–2025) também contém 2020, o que torna a comparação razoável — mas convém verificar se o
ganho deles sobrevive à exclusão de 2020, informação que o resumo não fornece.

**O que verificar antes de citar:** o texto foi lido pela versão HTML do arXiv. Se houver versão
publicada em periódico, a referência deve ser atualizada.
