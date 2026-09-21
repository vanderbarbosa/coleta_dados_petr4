---
name: revalidacao-tres-hipoteses-rejeitadas
description: "Revalidação no Colab (08/08/2026) — caixa alta rende quase nada, granularidade e comitê PIORAM; classificador perto do teto prático"
metadata: 
  node_type: memory
  type: project
  originSessionId: 08181b53-ca1d-41ae-a256-cc9d79527860
  modified: 2026-08-08T18:32:32.392Z
---

Notebook `notebooks/revalidacao_encoder_colab.ipynb` rodado no Colab em 08/08/2026. **Duas das três hipóteses foram rejeitadas; a terceira rendeu quase nada.** Melhor configuração final ganhou **+0,0004 de F1-macro** sobre a linha de base — nada.

## EXP 1 — caixa alta: PARCIAL, e menor do que previsto
- Acurácia nas 36 em caixa alta: **idêntica** (19/36 antes e depois)
- F1-macro 0,487→0,549 · kappa 0,195→0,264 (n=36, quase certamente não significativo)
- **Erro de distribuição caiu 57%** (14→6): o modelo parou de despejar tudo em Neutral (24→15, humano=17)
- **Impacto no ISM do corpus: +0,005** — desprezível diante do viés de 0,301 que o ACC corrige (as caps são só 10,5% do corpus)
- ⚠️ **Eu havia superestimado isso como "bug grande".** O mecanismo estava certo (cobertura 22% vs 78%), a consequência agregada é pequena. Aplicar a correção (é gratuita), mas é linha de tratamento de dados, não destaque.

## EXP 2 — granularidade: REJEITADA
`Título+Resumo` (42 palavras) **PIORA**: acc 0,530 vs 0,580; kappa 0,313 vs 0,374. Revocação do neutro despenca p/ 0,323 e a negativa infla p/ 0,863. Só CAT1_Empresa melhora (+0,020); CAT2_Mercado_Petroleo cai −0,139.
**A hipótese do descompasso de comprimento (13 vs 39 palavras) estava ERRADA.**
Confundidor a registrar: a planilha exibia Título e Resumo lado a lado, então não se sabe se o anotador julgou por um ou pelos dois.
✅ **Ganho real: o gap G9 fecha.** Manter `Título`, agora com justificativa experimental.

## EXP 3 — comitê: REJEITADA
`pysentimiento` sozinho: acc 0,420, F1 0,224, **kappa 0,016** (nulo), **recall do neutro 0,984** — prediz neutro para tudo. O log mostra `bpe.codes`: é o **bertweet-pt, treinado em TWEETS**. Não discrimina manchete jornalística formal.
Nenhuma regra de comitê supera o FinBERT sozinho.
✅ Explica retroativamente por que **Błoch et al. (2026) não publicaram métricas do comitê deles**.
O comitê não morreu como ideia — **o parceiro estava errado** (precisa ser treinado em texto formal).

## Quadro acumulado: 6 tentativas, nenhum ganho relevante
abstenção por limiar · reponderação por prior · normalização de caixa · granularidade · comitê · troca de encoder (jul/26, inconclusiva).
Somado ao **teste do teto** (rótulo perfeito dá +1,2 pp na direção), a leitura é que **o classificador está perto do limite prático** e o retorno de continuar investindo é baixo.

**How to apply — a recomendação:** restam **duas cartas**: **G3** (MLM de domínio, Colab 6–10 h, self-supervised, foi a etapa de maior ganho em Santos) e **G6** (LLM × encoder, 4 h). **Se nenhuma mover, ENCERRAR a linha de melhoria do classificador**, aceitar 0,58 documentado, e migrar o tempo para volatilidade e **escrita** — que é o que está atrasado.

**Why:** seis tentativas medidas e reportadas valem mais metodologicamente do que uma melhoria alegada sem teste. Vira seção de "hipóteses testadas e rejeitadas".

Documento: `orientacoes/RESULTADOS_REVALIDACAO_2026-08-08.md`.
Ver [[diagnostico-erro-neutro]], [[bug-caixa-alta-e-dataset-santos]], [[gaps-pesquisa-petr4]].
