---
name: retorno-anormal-e-inferencia-por-data
description: 29/10/2026 — trocar o alvo de retorno bruto para ANORMAL (descontando o Ibovespa) inverte o sinal: de 0/8 braços positivos para 5/8; e a correção de inferência que eu alardeei (2,3x) é de apenas 1,05x
metadata:
  type: project
---

**29/10/2026.** `CVM/27_retorno_anormal_e_painel.py`. Três itens executados
juntos: correção de inferência, troca do alvo para retorno anormal, e modelo
de painel. Painel comum de 23.010 linhas (2.301 datas × 10 papéis), corte de
treino em 09/05/2024, teste com 576 datas.

**ACHADO 1 — o alvo errado explicava parte do fracasso.** O estudo de evento
(Artigo 1) sempre descontou o Ibovespa pelo modelo de mercado; os
experimentos de ML vinham prevendo o retorno BRUTO, que é ~49% mercado. Ao
trocar o alvo para o **retorno anormal** ($R_{it} - \alpha_i - \beta_i R_{mt}$,
com α e β estimados SÓ no treino):

| alvo | média dos 8 braços | positivos | melhor |
|---|---|---|---|
| retorno BRUTO | −0,84 pp | **0 de 8** | −0,42 pp |
| retorno ANORMAL | +0,32 pp | **5 de 8** | **+0,95 pp** |

**O sinal inverteu.** Nenhum braço é significativo (o melhor tem p=0,203, IC
[−0,40, +2,34]), então NÃO é vitória — mas os modelos deixaram de ser
ativamente piores que o palpite fixo, o que não acontecia em nenhum
experimento anterior. E, pela primeira vez, o melhor braço é
**preço+sentimento** (+0,95) acima de só preço (+0,64).

Betas estimados, todos plausíveis: PETR4 1,37 · BPAC11 1,26 · BBAS3 1,22 ·
B3SA3 1,18 · BBDC4 1,13 · ITUB4 0,98 · SBSP3 0,95 · ITSA4 0,94 · VALE3 0,92 ·
**ABEV3 0,67** (defensiva, como se espera).

**ACHADO 2 — ERREI no alerta de inferência, e a correção é minha.** Eu avisei
que os IC agrupados estavam otimistas em **2,3×**, calculando pelo N efetivo
com a correlação dos RETORNOS (0,486). **Está errado:** o que importa para a
inferência é a correlação do **ACERTO**, não a do retorno. Medido por
bootstrap em blocos de data (2.000 reamostras, sorteando datas e levando
todos os papéis):

| | |
|---|---|
| IC95 supondo independência | ±1,29 pp |
| IC95 por bootstrap em blocos de data | ±1,35 pp |
| **fator real de inflação** | **1,05×** |

Faz sentido: um modelo que acerta ~50% erra de forma quase independente entre
papéis, mesmo quando os retornos andam juntos. **Os IC que reportei antes
estavam substancialmente corretos.** O bootstrap por data passa a ser o
padrão mesmo assim — é o método certo, e agora está medido.

**ACHADO 3 — o painel não mudou nada.** Treinar um modelo com os 10 papéis
empilhados e efeito de ativo deu resultado equivalente a treinar um por
papel (diferenças dentro do IC). Mais dados correlacionados não acrescentam
informação proporcional.

**E a correção da recomendação anterior:** eu havia sugerido ampliar de 10
para 56 papéis. **Não compra precisão** — o N efetivo satura em
(nº de dias ÷ correlação), então só o HORIZONTE move o teto. Ampliar papéis
ajuda o modelo a aprender, não a medir.

**PRÓXIMO PASSO ÓBVIO, não executado:** refazer com alvo anormal os
experimentos que deram nulo antes (volatilidade/HAR, dias com evento,
Prophet). O alvo bruto contaminava todos eles. Ver
[[restringir-a-dias-de-evento-nao-ajuda]] e
[[finbert-nao-acrescenta-nos-dois-times]].

**How to apply:** daqui em diante, **alvo padrão = retorno anormal**, não
bruto. E toda inferência agrupada por bootstrap em blocos de data — não pela
fórmula de proporção.
