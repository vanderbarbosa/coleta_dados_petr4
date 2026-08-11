# Resultados da revalidação — três hipóteses testadas, duas rejeitadas

**Executado em:** 08/08/2026, Google Colab (T4) · Notebook:
`notebooks/revalidacao_encoder_colab.ipynb`

---

## Veredito em uma tabela

| Experimento | Hipótese | Resultado | Veredito |
|---|---|---|---|
| **1. Caixa alta** | Normalizar recupera as 36 manchetes do Petronoticias | Acurácia **idêntica** (19/36); erro de distribuição cai 57%; impacto no ISM do corpus: **+0,005** | ⚠️ **Parcial — e menor do que eu previ** |
| **2. Granularidade** | `Título+Resumo` (42 palavras) se aproxima do regime de treino de Santos (39) | **Piora**: 0,530 contra 0,580 | ❌ **Rejeitada** |
| **3. Comitê** | O `pysentimiento` contextual complementa o FinBERT léxico | **Piora**: nenhuma configuração supera o FinBERT sozinho | ❌ **Rejeitada** |

**Melhor configuração final: `título normalizado`, com F1-macro +0,0004 sobre a linha de base.**
Ou seja: estatisticamente, nada mudou.

---

## Correção de algo que eu afirmei

Na rodada anterior chamei o problema de caixa alta de **bug com impacto grande**. Medido, o
impacto é pequeno. O mecanismo que descrevi estava certo — a cobertura de vocabulário é mesmo
22,2% contra 78,6%, e a massa de predições realmente saiu da classe neutra. O que eu
superestimei foi a **consequência agregada**: a fonte afetada é 10,5% do corpus, e o efeito no
ISM é de +0,005.

É correção de calibragem minha, não do achado. A distinção importa: o achado é real e a correção
deve ser aplicada, mas **não é a alavanca que eu sugeri que fosse**.

---

## Experimento 1 — caixa alta

### O que mudou, e o que não mudou

| Recorte | Métrica | Antes | Depois |
|---|---|---|---|
| Geral (300) | acurácia | 0,580 | 0,580 |
| Geral (300) | F1-macro | 0,5790 | 0,5794 |
| Geral (300) | kappa | 0,371 | 0,374 |
| **Caixa alta (36)** | acurácia | **0,528** | **0,528** |
| **Caixa alta (36)** | F1-macro | 0,487 | **0,549** |
| **Caixa alta (36)** | kappa | 0,195 | **0,264** |
| Caixa normal (264) — controle | acurácia | 0,587 | 0,587 |

**A acurácia por item não se moveu: 19 de 36 acertos, antes e depois.** O modelo passou a
acertar itens diferentes, não mais itens.

### Mas a distribuição de predições melhorou muito

| Classe | Humano | Antes | Depois | \|erro\| antes | \|erro\| depois |
|---|---|---|---|---|---|
| Negative | 6 | 4 | 9 | 2 | 3 |
| **Neutral** | **17** | **24** | **15** | **7** | **2** |
| Positive | 13 | 8 | 12 | 5 | 1 |
| **Total** | | | | **14** | **6** |

**O erro de distribuição caiu 57%.** A previsão do mecanismo estava correta: o modelo parou de
despejar tudo na classe neutra. O ganho em F1-macro (+0,062) e kappa (+0,069) no subconjunto
reflete isso — são métricas que premiam acertar o balanço de classes.

### Por que isso importa mesmo assim

O ISM é função das **proporções de classe**, não da acurácia por item. Uma correção que acerta a
distribuição é exatamente o tipo de correção que o índice aproveita — é o mesmo princípio da
calibração ACC.

**Mas o efeito agregado é pequeno:**

| | Atual | Projetado |
|---|---|---|
| Negative | 48,5% | 50,5% |
| Neutral | 37,5% | 33,1% |
| Positive | 14,0% | 16,5% |
| **ISM bruto** | **−0,3450** | **−0,3400** |

**Delta de +0,005** — desprezível diante do viés de 0,301 que a calibração ACC já corrige.

> **Recomendação:** aplicar a normalização — é gratuita, o mecanismo é correto e melhora a
> qualidade do dado. Mas **não vale um parágrafo de destaque na dissertação**; vale uma linha na
> seção de tratamento de dados. Com n = 36, o ganho em F1 e kappa quase certamente não é
> significativo.

---

## Experimento 2 — granularidade: hipótese rejeitada

| Configuração | Mediana de palavras | Acurácia | F1-macro | Kappa |
|---|---|---|---|---|
| `Título` normalizado | 13 | **0,580** | **0,579** | **0,374** |
| `Título` + `Resumo` | 42 | 0,530 | 0,525 | 0,313 |

**Piorou em tudo.** E o padrão do erro é revelador:

| Classe | Precisão | Revocação |
|---|---|---|
| Negative | 0,500 | **0,863** |
| **Neutral** | 0,597 | **0,323** |
| Positive | 0,526 | 0,521 |

**Com o resumo, o modelo inunda a classe negativa** (revocação 0,863, precisão 0,500) e a
revocação do neutro despenca de ~0,50 para 0,323. O texto adicional não deu contexto — deu mais
vocabulário carregado para o viés léxico do modelo se agarrar.

Por categoria, só uma melhora:

| Categoria | Título | Tít+Res | Δ |
|---|---|---|---|
| CAT1_Empresa | 0,571 | 0,592 | **+0,020** |
| CAT2_Mercado_Petroleo | 0,646 | 0,506 | **−0,139** |
| CAT3_Geopolitica | 0,500 | 0,463 | −0,037 |
| CAT6_Governanca | 0,733 | 0,667 | −0,067 |
| CAT7_Macro_Energia | 0,558 | 0,512 | −0,047 |

### O que isso significa

Minha hipótese era que o descompasso de comprimento (13 contra 39 palavras) explicava parte da
queda de 0,76 para 0,58. **Está errada.** Igualar o comprimento piora.

Há um confundidor que preciso registrar: **a planilha de rotulagem exibia `Título` e `Resumo`
lado a lado**, então não sabemos se o anotador julgou pelo título apenas ou pelos dois. Se ele
julgou pelo título, o resumo introduz conteúdo que o gabarito não avaliou — e aí a piora é
artefato do desenho, não do modelo. De todo modo, a conclusão prática não muda.

> **Ganho real deste experimento: o gap G9 está fechado com resposta medida.** A escolha por
> manchetes deixa de ser conveniência de coleta e passa a ser **decisão justificada por
> experimento** — algo que a dissertação não tinha.

---

## Experimento 3 — comitê: hipótese rejeitada

| Modelo | Acurácia | F1-macro | Kappa | Revocação do neutro |
|---|---|---|---|---|
| **FinBERT-PT-BR (léxico)** | **0,580** | **0,579** | **0,374** | 0,500 |
| pysentimiento (contextual) | 0,420 | 0,224 | 0,016 | **0,984** |
| Comitê — voto | 0,580 | 0,579 | 0,374 | — |
| Comitê — abstenção | 0,417 | 0,216 | 0,009 | — |
| Comitê — contextual | 0,420 | 0,224 | 0,016 | — |

### Por que falhou

**Revocação do neutro do `pysentimiento`: 122 de 124 = 0,984.** Ele prediz neutro para
praticamente tudo. Kappa de 0,016 é **concordância nula** — equivale a chute.

A causa está no log de carregamento: o download inclui `bpe.codes`, assinatura do
**BERTweet**. O `pysentimiento/bertweet-pt-sentiment` é treinado em **tweets**. Em manchete
jornalística formal ele não discrimina.

**O segundo membro não era complementar — era inútil neste domínio.** E o comitê apenas herdou
a inutilidade: as regras de abstenção e contextual pioraram, e a de voto simplesmente devolveu
o FinBERT.

> Isto também explica, retroativamente, por que **Błoch, Santana e Amantino (2026) não
> publicaram métricas do comitê deles**. Eu havia registrado essa ausência como fragilidade do
> trabalho; agora há motivo concreto para desconfiar dela.

**O comitê não está morto como ideia — o parceiro é que estava errado.** Um candidato adequado
precisaria ser treinado em texto formal, não em rede social.

---

## O que sobra, e a recomendação

Somando esta rodada aos testes anteriores, o quadro de tentativas de melhorar o classificador é:

| Tentativa | Resultado |
|---|---|
| Abstenção por limiar de confiança | Ganha 0,7 pp de acurácia, perde F1 e kappa |
| Reponderação por prior | Piora (teste inconclusivo por falta dos *logits*) |
| **Normalização de caixa alta** | **Acurácia inalterada; distribuição melhora; ISM +0,005** |
| **Granularidade `Título+Resumo`** | **Piora** |
| **Comitê com pysentimiento** | **Piora** |
| Trocar de encoder (BERTimbau, Albertina) | Inconclusivo por protocolo, em jul/2026 |
| *Teto teórico (rótulo humano)* | *+1,2 pp na direção; p = 0,098 na volatilidade* |

**Seis tentativas, nenhuma com ganho relevante.** Combinado com o teste do teto, a leitura
honesta é que **o classificador está próximo do seu limite prático nesta tarefa**, e que o
retorno esperado de continuar investindo nele é baixo.

### A recomendação: mais duas cartas, e depois parar

Restam duas alavancas não testadas, ambas com fundamentação real:

| # | O que | Por que ainda vale | Custo |
|---|---|---|---|
| **G3** | **Adaptação de domínio por MLM** sobre as 205 mil notícias | É a etapa de maior ganho documentado em Santos (perplexidade 1,51 → 1,24) e a única que **muda a representação**, que é onde o diagnóstico apontou o problema. *Self-supervised*. | Colab, 6–10 h |
| **G6** | **LLM × encoder** com a instrução literal de Santos | Teles e Figueiredo (2025) mostram Gemini a 80% em inglês; em português a comparação não existe. Usa o gabarito atual. | 4 h |

> **Se nenhuma das duas mover a agulha, a recomendação é encerrar a linha de melhoria do
> classificador**, aceitar 0,58 com as limitações documentadas, e realocar o tempo restante
> para a modelagem de volatilidade e para a **escrita** — que é o que está atrasado.

Isso não é desistência. É o que os dados indicam, e há material de sobra para justificá-lo:
seis tentativas medidas e reportadas valem mais, metodologicamente, do que uma melhoria
alegada sem teste.

---

## O que estes resultados entregam à dissertação

Nenhum ganho de desempenho — mas três contribuições de método:

1. **O gap G9 fecha com resposta medida.** A escolha por manchetes passa a ser decisão
   justificada, e não conveniência.
2. **O gap G7 fecha parcialmente**, com um achado específico: modelos de rede social não servem
   como parceiro de comitê em texto jornalístico formal. Isso qualifica a leitura de Błoch et al.
3. **Uma seção de "hipóteses testadas e rejeitadas"**, com seis entradas e números. É seção
   legítima de dissertação, e demonstra rigor melhor do que qualquer resultado positivo isolado.

---

## Ações imediatas

| # | Ação | Prazo |
|---|---|---|
| 1 | Aplicar a normalização de caixa alta ao corpus (já feito: `noticias_titulos_normalizados.csv`) e registrar em uma linha na seção de tratamento de dados | — |
| 2 | **Manter `Título`** como unidade de texto, agora com justificativa experimental | — |
| 3 | Levar esta tabela de seis tentativas à mentoria de 10/08 | 10/08 |
| 4 | Rodar **G6** (LLM), que é barato | Semana de 11/08 |
| 5 | Rodar **G3** (MLM de domínio) | Semana de 18/08 |
| 6 | **Decidir**: se G3 e G6 não moverem, encerrar a linha e migrar para escrita | Fim de agosto |
