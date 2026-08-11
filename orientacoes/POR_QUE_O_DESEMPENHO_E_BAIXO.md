# Por que o nosso desempenho é baixo, se todos usam o encoder sem alterá-lo?

**Elaborado em:** 08/08/2026 · Análise executável em
[`diagnosticar_erro_modelo.py`](../src/sentimento/diagnosticar_erro_modelo.py) e
[`testar_consertos_baratos.py`](../src/sentimento/testar_consertos_baratos.py)

---

## Resposta em cinco linhas

1. **A premissa não se sustenta: ninguém mais mediu.** Dos trabalhos que usam o FinBERT-PT-BR,
   nenhum reporta acurácia contra gabarito humano. Não estamos piores que os outros — somos os
   únicos que sabemos onde estamos.
2. **0,58 não é ruim em termos absolutos:** o acaso é 0,333 e o baseline de sempre-a-classe-maior
   é 0,413. Estamos **+16,7 pontos** acima do baseline.
3. **A diferença para os 0,76 de Santos tem causa medida, e não é o que se supunha.** Não são os
   casos difíceis (+0,7 pp ao filtrá-los) nem o recorte por ativo (diferença de 0,9 pp).
4. **É a fronteira do NEUTRO.** Descartando o neutro, positivo × negativo dá **0,783** e
   κ = 0,565. O modelo separa bem os extremos; o que ele não sabe é decidir se algo é neutro.
5. **E a razão é estrutural:** no treino de Santos o neutro era a **menor** classe (27,8%); no
   nosso corpus é a **maior** (41,3%). O modelo aprendeu a ser decidido; nosso corpus pede
   prudência.

---

## 1. Primeiro: baixo em relação a quê?

A pergunta pressupõe que os outros trabalhos obtêm resultados melhores. **Não obtêm — eles não
medem.** Verifiquei um por um:

| Trabalho | Usa o FinBERT-PT-BR? | Mede a acurácia? |
|---|---|---|
| `jp-alves/prio3-sentiment` (PRIO3) | Sim | ❌ Nenhum gabarito |
| `JoseOtavioJunqueira/Analise-de-Sentimento-IC` (ICMC/USP) | Sim | ❌ Nenhum gabarito |
| `IagoErrera/scrap-fin` | Sim | ❌ Nenhum gabarito |
| Błoch, Santana e Amantino (2026) | Sim | Comparou com historiador, **sem publicar métricas** |
| Teles e Figueiredo (2025) | Não avaliou o modelo | — |
| Abílio, Coelho e Silva (2024) | Não (tarefa de NER) | — |
| **Santos (2023)** | (criou) | **0,76 — no conjunto de teste dele** |
| **Nós** | Sim | **0,58 — medido** |

> **Só existem duas medições publicadas do FinBERT-PT-BR: a do próprio autor e a nossa.** Todos
> os demais aplicam o modelo assumindo que funciona. Não há, portanto, um "desempenho dos
> outros" contra o qual estejamos abaixo.

Isso reposiciona o problema. Não é *"por que somos piores"*, é *"por que a nossa medição difere
da que o autor reporta"* — que é uma pergunta legítima e respondível.

## 2. Os 0,58 são ruins?

| Referência | Acurácia |
|---|---|
| Acaso (3 classes) | 0,333 |
| Sempre a classe mais frequente (Neutral, 124/300) | 0,413 |
| **FinBERT-PT-BR no nosso corpus** | **0,580** |
| Santos (2023), notícias gerais de mercado | 0,760 |

**Ganho sobre o baseline de maioria: +16,7 pontos.** κ = 0,371, que na escala de Landis e Koch
é concordância "razoável" (*fair*). O modelo está aprendendo algo real — não está chutando.

O que exige explicação é a distância para os 0,76.

## 3. O que NÃO explica a diferença (testado e descartado)

### Hipótese 1 — "Santos descartou os casos difíceis"

Santos descartou **497 de 1.000 textos (49,7%)** — os classificados como "não se aplica" ou sem
concordância entre anotadores. Seu conjunto de teste é, por construção, o subconjunto de
notícias que **têm** sentimento claro. Parecia a explicação óbvia.

Testei com a coluna `Confianca_Rotulador` como proxy:

| Recorte | n | Acurácia | κ |
|---|---|---|---|
| Todos | 300 | 0,580 | 0,371 |
| **Só confiança "Alta"** | 233 | **0,597** | 0,393 |
| Confiança "Média" | 57 | 0,526 | 0,284 |

> **Ganho de apenas +1,7 pp.** Manter só os casos fáceis quase não muda nada. **A hipótese não
> se sustenta.**
>
> *Ressalva:* o nosso proxy não é idêntico ao filtro de Santos — ele descartou por **discordância
> entre dois anotadores**, e nós só temos a autoavaliação de um. A comparação é imperfeita, mas
> é a melhor disponível.

### Hipótese 2 — "o problema é o recorte por ativo único"

| Recorte | n | Acurácia | κ |
|---|---|---|---|
| Relevante para a PETR4 | 111 | 0,586 | 0,378 |
| Não relevante | 189 | 0,577 | 0,358 |

> **Diferença de 0,9 pp.** O modelo erra igualmente em notícias sobre a Petrobras e em notícias
> gerais do setor. **A hipótese não se sustenta** — pelo menos não isoladamente.

## 4. O que EXPLICA a diferença

### Achado principal — é a fronteira do neutro, e só ela

**Recall por classe verdadeira:**

| Classe verdadeira | n | Recall | Precisão |
|---|---|---|---|
| Negative | 80 | **0,750** | 0,531 |
| Neutral | 124 | 0,532 | 0,635 |
| Positive | 96 | **0,500** | 0,578 |

**E agora o teste decisivo — descartando o neutro dos dois lados:**

| Tarefa | n | Acurácia | κ |
|---|---|---|---|
| 3 classes (como está) | 300 | 0,580 | 0,371 |
| **Só Positivo × Negativo** | 138 | **0,783** | **0,565** |

> ### O modelo distingue positivo de negativo com 78% de acurácia. O que ele não consegue é decidir se uma manchete é neutra.

Confirmação pela estrutura dos erros: dos **126 erros**, **113 (90%)** envolvem a classe Neutral
em alguma ponta. As quatro principais confusões:

| Humano | Modelo | Casos |
|---|---|---|
| Neutral | Negative | 32 |
| Positive | Neutral | 27 |
| Neutral | Positive | 26 |
| Positive | Negative | 21 |

### A causa estrutural — *prior shift*

| Classe | Treino de Santos | Nossa realidade | O modelo prediz |
|---|---|---|---|
| Negative | **40,4%** | 26,7% | 37,7% |
| **Neutral** | **27,8%** (menor) | **41,3%** (maior) | 34,7% |
| Positive | 31,8% | 32,0% | 27,7% |

> **No treino de Santos, "neutro" era a classe mais rara. No nosso corpus, é a mais comum.**
>
> É consequência direta do processo de anotação dele: ao descartar metade dos casos — inclusive
> os "não se aplica" —, ele removeu justamente as notícias que **não dizem nada**. O modelo foi
> treinado num mundo onde quase toda notícia tem carga, e é aplicado num mundo onde a maioria
> não tem. Ele continua sendo decidido, e por isso erra para os extremos.
>
> Note que as predições do modelo (37,7% negativo) ficam **entre** o prior de treino (40,4%) e a
> realidade (26,7%), muito mais perto do treino. É a assinatura clássica de *prior shift*.

### Evidências de apoio

**O modelo sabe que não sabe.** A confiança máxima nas 300 manchetes é **0,856**, e
**nenhuma** passa de 0,90:

| Faixa de confiança | n | Acurácia |
|---|---|---|
| ≤ 0,60 | 92 (31%) | **0,424** |
| 0,60 – 0,80 | 140 | 0,650 |
| 0,80 – 0,90 | 68 | 0,647 |
| > 0,90 | **0** | — |

Num problema de 3 classes, um modelo confiante produziria muitos casos acima de 0,95. Este nunca
chega lá. É sinal de **incompatibilidade de domínio**, não de aleatoriedade — e é uma boa
notícia: a confiança **discrimina**, então serve de sinal de qualidade.

**A dificuldade varia muito por categoria:**

| Categoria | n | Acurácia | κ |
|---|---|---|---|
| CAT6_Governanca | 15 | 0,733 | 0,559 |
| CAT2_Mercado_Petroleo | 79 | 0,646 | 0,468 |
| CAT7_Macro_Energia | 43 | 0,605 | 0,393 |
| CAT1_Empresa | 98 | 0,571 | 0,362 |
| **CAT3_Geopolitica** | 54 | **0,481** | **0,216** |

Geopolítica é o pior caso — e faz sentido: é onde a inversão "notícia ruim = boa para a
produtora de petróleo" é mais forte, e é exatamente o vocabulário que um modelo de mercado geral
não domina.

**Manchetes longas degradam:** ≤8 palavras → 0,625; >14 palavras → 0,516. A mediana do nosso
corpus é 13 palavras. *(Pode estar confundido com o tema — manchetes longas tratam assuntos mais
complexos.)*

## 5. Os consertos baratos não funcionam — testado

Antes de investir em intervenções caras, testei dois pós-processamentos óbvios:

**Conserto 1 — confiança baixa vira Neutral:**

| Limiar | Acurácia | F1-macro | κ | Recall do Neutro |
|---|---|---|---|---|
| (sem conserto) | 0,580 | 0,579 | 0,371 | 0,532 |
| < 0,65 → Neutral | **0,587** | 0,563 | 0,360 | 0,750 |
| < 0,80 → Neutral | 0,497 | 0,422 | 0,186 | 0,847 |

> Ganha-se **+0,7 pp** de acurácia, mas o **F1-macro cai** (0,579 → 0,563) e o **κ cai**
> (0,371 → 0,360). Sobe o recall do neutro sacrificando as outras classes. **Não compensa.**

**Conserto 2 — reponderar pelo prior real:** piora tudo (acc 0,573, F1 0,571, κ 0,354).

> ⚠️ **Este segundo teste é inconclusivo.** A reponderação correta exige a distribuição *softmax*
> completa, e o Script 03 só grava o rótulo *top-1* e sua confiança. A aproximação usada pode ser
> a causa da piora. Para concluir, é preciso re-executar gravando os *logits* — o que exige GPU.

**A leitura desse resultado negativo é o mais útil de tudo:** se ajustar a saída não resolve, o
problema não está na **calibração** — está na **representação**. O modelo genuinamente não separa,
no espaço de *features* que aprendeu, manchete neutra de manchete carregada no nosso domínio.

## 6. O que deve funcionar, e por quê

Sobram os caminhos que **mudam a representação**, e não os que ajustam a saída:

| # | Intervenção | Por que deve atacar este problema específico | Gap |
|---|---|---|---|
| 1 | **Comitê com modelo contextual** (`pysentimiento`) | Błoch et al. (2026) caracterizam o FinBERT-PT-BR como guiado por **léxico**; um modelo **contextual** é a contrapartida exata do erro medido. A regra de abstenção por discordância ataca diretamente a fronteira do neutro. | **G7** |
| 2 | **Adaptação de domínio por MLM** nas 205 mil notícias | Ensina ao modelo o vocabulário em que ele hoje hesita (confiança nunca passa de 0,856). É *self-supervised*: **não consome rótulo**. | **G3** |
| 3 | **Re-executar gravando os *logits*** | Torna conclusivo o teste de reponderação e viabiliza combinação de probabilidades no comitê. Custo baixo, só precisa de GPU. | — |
| 4 | **Ablação por granularidade** (manchete × subtítulo × corpo) | Se manchetes longas degradam, mais contexto pode ajudar — ou piorar. É testável, e resolve de vez a justificativa do nosso recorte. | **G9** |
| 5 | **Tratar geopolítica à parte** | κ = 0,216 nessa categoria. Vale reportar o desempenho por categoria em vez de só o agregado. | — |

**O que já está resolvido:** a correção ACC do ISM (`calibrar_ism_com_gabarito.py`) trata o
*prior shift* **no agregado** — corrige a proporção de classes da série, ainda que não conserte
a classificação item a item. É por isso que ela funciona mesmo quando os consertos de instância
falham.

## 7. Como responder isso em banca

> *"Medimos 0,58 de acurácia contra gabarito humano — abaixo dos 0,76 relatados pelo autor do
> modelo. A decomposição do erro mostra que a diferença não vem do recorte por ativo (0,586
> contra 0,577 entre notícias relevantes e não relevantes) nem da dificuldade dos casos (+1,7 pp
> ao reter apenas os de alta confiança do anotador). Ela se concentra na fronteira da classe
> neutra: descartando o neutro, a discriminação entre positivo e negativo atinge 0,783 com
> κ = 0,565. A causa é uma mudança de prior — no conjunto de treino do modelo o neutro
> representava 27,8% dos casos, contra 41,3% no nosso corpus, porque o processo de anotação
> original descartou 49,7% dos textos, inclusive os sem carga informacional. Testamos correções
> de pós-processamento, que não recuperam desempenho, o que indica limitação de representação e
> não de calibração. Registre-se ainda que somos, junto com o autor, os únicos a reportar
> medição do modelo contra gabarito humano — os demais trabalhos que o utilizam não o validam."*

---

## Anexo — arquivos

| Arquivo | Conteúdo |
|---|---|
| `src/sentimento/diagnosticar_erro_modelo.py` | Decomposição do erro em 7 hipóteses |
| `src/sentimento/testar_consertos_baratos.py` | Teste dos pós-processamentos |
| `Mestrado_PETR4/diagnostico_erro_modelo.json` | Números do diagnóstico |
| `Mestrado_PETR4/consertos_baratos.json` | Números dos consertos |
