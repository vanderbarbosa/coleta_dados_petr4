---
name: diagnostico-erro-neutro
description: O erro do FinBERT no nosso corpus é 90% fronteira do NEUTRO + prior shift; pós-processamento não resolve; e ninguém mais mediu o modelo
metadata: 
  node_type: memory
  type: project
  originSessionId: 08181b53-ca1d-41ae-a256-cc9d79527860
  modified: 2026-08-08T16:22:55.363Z
---

Decomposição do erro rodada em 08/08/2026 (`src/sentimento/diagnosticar_erro_modelo.py` e `testar_consertos_baratos.py`), respondendo "por que nosso desempenho é baixo se todos usam o encoder sem alterá-lo".

**A premissa cai primeiro: ninguém mais mede.** Dos trabalhos que usam o FinBERT-PT-BR (prio3, ICMC/USP, scrap-fin), **nenhum** valida contra gabarito. Błoch comparou com historiador mas não publicou métricas. **Só existem 2 medições do modelo: a do autor (0,76) e a nossa (0,58).**

**0,58 não é ruim em absoluto:** acaso 0,333 · baseline maioria 0,413 · nós 0,580 (+16,7 pp) · Santos 0,760.

**O que NÃO explica a diferença (testado):**
- Casos difíceis: filtrar por confiança "Alta" dá só **+1,7 pp** (0,580→0,597)
- Recorte por ativo: relevante 0,586 vs não relevante 0,577 (**0,9 pp**)

**O que EXPLICA — a fronteira do NEUTRO:**
- Recall: Negative 0,750 · Neutral 0,532 · **Positive 0,500**
- **Descartando o neutro, Positivo × Negativo dá acc 0,783 e κ 0,565**
- **113 dos 126 erros (90%) envolvem a classe Neutral**
- Top confusões: Neutral→Negative 32 · Positive→Neutral 27 · Neutral→Positive 26

**Causa estrutural — PRIOR SHIFT:** no treino de Santos o neutro era a **menor** classe (27,8%); no nosso corpus é a **maior** (41,3%). Ele descartou 49,7% dos textos (inclusive "não se aplica"), removendo justamente as notícias sem carga. O modelo aprendeu a ser decidido; nosso corpus pede prudência. As predições (37,7% negativo) ficam entre o prior de treino (40,4%) e a realidade (26,7%).

**Evidências de apoio:** confiança máxima nas 300 manchetes é **0,856 — NENHUMA passa de 0,90** (incompatibilidade de domínio, não aleatoriedade); a confiança discrimina (≤0,60 → acc 0,424). Pior categoria: **CAT3_Geopolitica (acc 0,481, κ 0,216)** — é onde a inversão "notícia ruim = boa p/ produtora de petróleo" é mais forte.

⚠️ **Consertos baratos NÃO funcionam (testado):** abstenção por limiar ganha +0,7 pp de acurácia mas **perde F1 e κ**; reponderação por prior piora tudo — mas esse teste é **inconclusivo**, porque só gravamos top-1 e não a softmax completa (re-executar o Script 03 salvando logits).

**Why:** se ajustar a saída não resolve, o problema é de **representação**, não de calibração. Isso justifica investir em G7 (comitê c/ modelo contextual) e G3 (MLM de domínio), e descarta atalhos de pós-processamento.

## As TRÊS camadas — não confundir (a pergunta "o que está baixo?")
1. **Classificação da notícia** → 0,580 (baseline 0,413) = **MEDIANA**, erro localizado no neutro
2. **Índice de sentimento** → **NÃO é baixo, é DESLOCADO** em 87%; já corrigido por ACC
3. **Direção do preço** → **É ESTA que está baixa**: 49,7% modelo · 50,9% rótulo humano · 46,7% aposta declarada — todos abaixo do baseline "sempre alta" de 52,8%

## TESTE DO TETO (`src/sentimento/testar_teto_do_classificador.py`) — o mais importante
Usa o rótulo humano como classificador perfeito por construção:
- **DIREÇÃO: modelo 49,7% → humano 50,9%. Ganho de 1,2 pp.** Melhorar o encoder é **INÚTIL** para direção — o gargalo não é o texto.
- **VOLATILIDADE: modelo p=0,502 → humano p=0,098** (|ret| após negativa 1,21% vs positiva 1,00%, razão 1,20×). O sinal **existe no rótulo perfeito e some no do modelo**. ⚠️ p=0,098 é tendência, não resultado.

**Consequência:** justificar G7 e G3 pelo eixo da **VOLATILIDADE**, nunca pela promessa de melhorar direção.

Documentos: `orientacoes/POR_QUE_O_DESEMPENHO_E_BAIXO.md` (md) e `DIAGNOSTICO_DESEMPENHO_PETR4.docx` (ABNT, 17 tabelas).
Ver [[calibracao-ism-acc]], [[conjunto-ouro-quatro-rotulos]], [[gaps-pesquisa-petr4]].
