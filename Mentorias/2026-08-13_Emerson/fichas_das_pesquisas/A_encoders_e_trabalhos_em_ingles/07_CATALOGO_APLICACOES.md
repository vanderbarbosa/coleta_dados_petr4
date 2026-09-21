# Catálogo das aplicações encontradas — resposta ao pedido 3

> Pedido do Prof. Emerson em 13/08/2026: *"listar as aplicações encontradas nos artigos que usaram
> o BERT financeiro em inglês"*.

Foram identificadas **nove famílias de aplicação**. Para cada uma registram-se: o que se faz, um ou
mais trabalhos representativos, e — o que mais interessa — **se aquilo é aproveitável na nossa
pesquisa**.

---

## Visão geral

| # | Família de aplicação | Aproveitável para nós? |
|---|---|---|
| 1 | Análise de sentimento de notícias e relatórios | Já é o que fazemos |
| 2 | **Previsão de volatilidade** | **Sim — é o eixo central** |
| 3 | Previsão de preço e de direção | Parcialmente — com ressalva importante |
| 4 | **Classificação de declarações prospectivas** | **Sim — a ideia mais promissora** |
| 5 | Classificação ESG | Não no escopo atual |
| 6 | Otimização de carteira e estratégia | Trabalho futuro |
| 7 | Comunicação de bancos centrais | Não — mas metodologicamente instrutivo |
| 8 | Extensão a outros mercados (renda fixa, cripto, setorial) | Sim — atende ao "abrir o leque" |
| 9 | Explicabilidade e auditoria de modelos | Sim — barato e valorizado pela banca |

---

## 1. Análise de sentimento de notícias, relatórios e teleconferências

**O que se faz:** classificar sentenças ou documentos financeiros em positivo, negativo e neutro.
É a aplicação original e a mais comum.

**Escalas observadas:** um estudo mediu o sentimento de **28.873 transcrições de teleconferências
de resultados** entre 2003 e 2020, associando-o à reação do mercado. Outro examinou a distribuição
de sentimento dos formulários 10-K e 10-Q da SEC.

**Para nós:** é o que já fazemos. O ponto de interesse é a **escala** — 28.873 transcrições contra
as nossas 205.697 manchetes. Volume comparável, mas o objeto deles (transcrições completas) é muito
mais rico que o nosso (título e resumo). A dissertação já declara essa limitação.

---

## 2. Previsão de volatilidade — o eixo central

**O que se faz:** usar o sentimento como variável explicativa em modelos de volatilidade
(GARCH, HAR e variantes).

**Trabalhos representativos:**

| Trabalho | Modelo | Resultado |
|---|---|---|
| Halousková e Lyócsa (2025) | FinBERT + HAR, 404 ações do S&P 500 | **Supera o HAR em 98,76% dos casos**, ganho médio de 12,74%; **14,99% nos dias extremos** |
| Mino e Williamson (2025) | BERT + GARCH(1,1)-*t*, S&P 500 | Coeficiente do sentimento $-0{,}2275$ ($p = 0{,}0016$) |

**Para nós:** esta é a família mais importante e ganhou ficha própria —
[`04_HALOUSKOVA_LYOCSA_2025.md`](04_HALOUSKOVA_LYOCSA_2025.md) e
[`05_MINO_WILLIAMSON_2025.md`](05_MINO_WILLIAMSON_2025.md). Em resumo: **a literatura confirma o
nosso efeito de cauda e mostra que superar o HAR é possível**, com medida intradiária de
volatilidade, muitos ativos e métodos de encolhimento.

---

## 3. Previsão de preço e de direção — e a armadilha dos 95%

**O que se faz:** acoplar o sentimento a modelos de séries temporais (LSTM, XGBoost) para prever
preço ou direção.

**Trabalhos representativos:** a família FinBERT-LSTM, com diversas variantes publicadas entre 2022
e 2024 sobre o NASDAQ-100 e notícias da Benzinga; e um trabalho de 2025 que funde sinais do FinBERT
com atributos de preço e volatilidade em árvores impulsionadas por gradiente, sobre ações do S&P 500
entre 2018 e 2023, reportando superação de linhas de base técnicas e lexicais.

### ⚠️ A armadilha dos 95%

Um trabalho da família FinBERT-LSTM reporta **"acurácia de 0,955"**. Esse número **não é comparável
aos nossos 52,3%**, e a diferença precisa ser compreendida, porque a banca pode perguntar.

**A evidência disponível:** o trabalho reporta como métricas **MAE, MAPE e "acurácia"**, com MAPE de
0,045. MAE e MAPE são **métricas de regressão**, não de classificação. A presença delas indica que
o alvo é o **nível do preço**, e não a direção; e a "acurácia" de 0,955 é, com alta probabilidade,
uma transformação do MAPE (1 − 0,045 = 0,955).

**Por que isso é enganoso.** Prever o nível do preço de amanhã é trivial: basta responder "o mesmo
de hoje". O preço tem autocorrelação próxima de 1, e qualquer modelo obtém erro percentual baixo
sem conter informação alguma. **Prever a direção é o problema difícil**, porque a direção é
próxima de um lançamento de moeda. Os dois números medem coisas incomparáveis.

**Ressalva de honestidade:** não foi possível ler o texto integral (o PDF do arXiv retornou conteúdo
ilegível e a versão ACM retornou HTTP 403). A leitura acima é **inferência a partir das métricas
declaradas**, e não verificação direta. Antes de afirmá-la na dissertação, é preciso obter o PDF e
confirmar. A inferência é, contudo, forte: nenhum trabalho sério de classificação direcional
reporta MAPE.

**Para nós:** esta é uma **contribuição potencial da dissertação** — apontar que boa parte da
literatura de "previsão de ações com FinBERT" reporta métricas de regressão sobre o nível do preço
e apresenta números que parecem espetaculares sem o serem. A nossa Seção 4.l, ao reportar 47,6% para
a regra ingênua, faz o oposto: mede a tarefa difícil e relata o número desfavorável.

---

## 4. Classificação de declarações prospectivas — a ideia mais promissora

**O que se faz:** separar o que é **relato de fato passado** do que é **projeção sobre o futuro**.
O modelo `yiyanghkust/finbert-fls` é dedicado a essa tarefa.

**Para nós — e esta é a recomendação principal deste catálogo:**

A Seção 4.l estabeleceu que **o nosso sentimento acompanha o mercado em vez de antecedê-lo**: o
ordenamento das classes é limpo no pregão que reage ($P_0$) e colapsa no pregão seguinte ($P_1$).
A interpretação registrada foi que boa parte do sinal aparente é jornalismo narrando o que já
ocorreu.

Se essa interpretação estiver correta, então **separar as notícias prospectivas das retrospectivas
deveria concentrar o sinal preditivo**. É uma hipótese diretamente testável, e é a continuação
natural do filtro de relevância da Seção 4.k — que já demonstrou que **mexer na seleção das notícias
funciona, enquanto mexer no modelo não**.

**Como testar sem depender de tradução:** não é necessário usar o modelo em inglês. Basta construir
um classificador de prospectividade para o português — por regras (tempo verbal futuro, expressões
como "deve", "prevê", "projeta", "estima", "espera-se") ou por ajuste leve — e refazer o índice
apenas com as notícias prospectivas. **Custo baixo, hipótese clara, ligação direta com dois achados
já estabelecidos da dissertação.**

---

## 5. Classificação ESG

**O que se faz:** classificar textos corporativos quanto a temas ambientais, sociais e de
governança. Modelos dedicados: `yiyanghkust/finbert-esg` e o `FinBERT-ESG-9-Categories`.

**Resultados:** 89,5% de acurácia na rotulagem de discussões ESG [via resumo]. Em estudo de
classificação de risco ESG em formulários 10-K, o **FinBERT obteve 83% de acurácia e macro-F1 de
0,83, superando todos os grandes modelos de linguagem testados**.

**Para nós:** fora do escopo atual. Registre-se, contudo, o dado do parágrafo anterior — **um
codificador especializado superou os LLMs** em tarefa de domínio. Isso corrobora, por via
independente, o resultado do nosso experimento G6, em que o Qwen2.5-3B obteve 0,480 contra 0,580 do
FinBERT-PT-BR. Não é um resultado isolado nosso: é um padrão.

**Observação para a Petrobras, se um dia interessar:** governança e questões ambientais são
determinantes conhecidos do risco da PETR4, e a nossa taxonomia já tem a categoria
`CAT6_Governanca`. Há aqui uma linha de doutorado plausível.

---

## 6. Otimização de carteira e estratégia de negociação

**O que se faz:** integrar o sentimento do FinBERT a decisões de alocação.

**Trabalho representativo:** estratégia que combina um índice de estresse financeiro com o
sentimento do FinBERT, reportando melhora na acurácia de previsão de mercado e no desempenho da
carteira, com razões mais altas e **redução do rebaixamento máximo** (*maximum drawdown*).

**Para nós:** trabalho futuro. A dissertação já contém uma simulação de negociação preliminar. O
elemento novo e aproveitável é a métrica: **rebaixamento máximo é métrica de risco**, e nós
argumentamos que o sentimento informa risco e não direção. **É, portanto, a métrica coerente com a
nossa própria tese** — mais do que o retorno acumulado. Vale incorporar à simulação existente.

---

## 7. Comunicação de bancos centrais

**O que se faz:** analisar comunicados do FOMC e de outros bancos centrais. Existe um
`FinBERT-FOMC` especializado.

**Trabalho representativo:** avaliação comparando Llama-3-70B, GPT-4, FinBERT-FOMC, FinBERT e VADER
na análise de comunicação de banco central, sob o título "*Is small really beautiful for central
bank communication?*".

**Para nós:** fora de escopo, mas **metodologicamente instrutivo**. Trata-se de uma comparação
sistemática entre modelos pequenos especializados e grandes modelos generalistas — exatamente o
desenho do nosso experimento G6. É uma referência útil para sustentar aquela seção.

---

## 8. Extensão a outros mercados — atende ao "abrir o leque"

**O que se faz:** aplicar o FinBERT fora do mercado acionário norte-americano.

| Extensão | Trabalho | Observação |
|---|---|---|
| **Renda fixa** | BondBERT (arXiv:2511.01869, 2025) | 30.000 artigos do mercado britânico de títulos, 2018–2025. Os autores registram que **o uso em renda fixa é escasso** — lacuna declarada |
| **Criptomoedas** | FinBERT-BiLSTM (arXiv:2411.12748) | Explicitamente motivado pela **alta volatilidade** do mercado |
| **Biotecnologia** | BioFinBERT (arXiv:2401.11011) | Sentimento em torno de pontos de inflexão de ações de biotecnologia |
| **Setorial** | *Electronics*, v. 14, n. 23, art. 4680 (2025) | 1.500 manchetes setoriais anotadas; F1 de 0,555 para 0,707 |

**Para nós — resposta direta à orientação do Prof. Emerson:**

O padrão da literatura é claro: **especializar por segmento produz ganho**. BondBERT para renda
fixa, BioFinBERT para biotecnologia, ajuste setorial para setores específicos. Todos partem do
mesmo diagnóstico — o modelo genérico degrada no subdomínio — e todos respondem com especialização.

É exatamente o nosso diagnóstico da Seção 4 (degradação de 0,760 para 0,580). **A diferença é que a
literatura responde com mais dados rotulados do subdomínio, e nós respondemos com adaptação não
supervisionada (o G3), que falhou.** O caminho que funciona, na literatura, é o supervisionado.

Registre-se ainda que o caso das criptomoedas é justificado pela **volatilidade elevada**. Se o
efeito do sentimento é de cauda, como estabelecemos, então **ativos mais voláteis devem exibir
efeito maior**. Isso sugere um teste: replicar o *pipeline* em ativos brasileiros de volatilidade
distinta e verificar se o coeficiente do sentimento cresce com a volatilidade do ativo. Seria uma
confirmação forte da tese de cauda, e responde ao pedido de não focar em um único ativo.

---

## 9. Explicabilidade e auditoria

**O que se faz:** abrir a caixa-preta do classificador, identificando quais palavras determinam a
decisão. Técnicas: Integrated Gradients e LIME, com auditoria de fidelidade por curvas de deleção
e AOPC.

**Trabalho representativo:** o artigo de ajuste setorial já citado, que conclui que **o LIME é o
mais fiel** (AOPC = 0,365).

**Para nós:** barato e valorizado. A dissertação já contém uma auditoria substancial do
FinBERT-PT-BR — a primeira contra padrão humano, mais os dois achados de implementação. Acrescentar
LIME sobre as manchetes que o modelo erra permitiria **mostrar quais palavras o levam ao erro**, o
que enriqueceria a Seção 4 com evidência qualitativa. É uma biblioteca pronta, e o custo é de
horas, não de semanas.

---

## Síntese: as três aplicações a perseguir

Da leitura conjunta das nove famílias, três se destacam pela razão entre ganho esperado e custo:

1. **Declarações prospectivas (família 4).** Testa diretamente a explicação que demos para o
   colapso entre $P_0$ e $P_1$, e segue a lição já estabelecida de que mexer no corpus funciona.
   Custo baixo.
2. **Múltiplos ativos com volatilidades distintas (família 8).** Atende à orientação do Prof.
   Emerson, ataca a limitação de poder estatístico identificada na ficha 04 e permite testar a
   predição de que o efeito de cauda cresce com a volatilidade do ativo. Custo médio.
3. **Métodos de encolhimento e combinação (família 2).** Regressão de subconjuntos completos e
   LASSO adaptativo sobre os dados que já temos. É só código. Custo muito baixo.
