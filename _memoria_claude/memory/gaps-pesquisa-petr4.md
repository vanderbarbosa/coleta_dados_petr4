---
name: gaps-pesquisa-petr4
description: Os 13 gaps de pesquisa levantados em ago/2026 e a ordem de ataque — 12 dos 13 não dependem de rotulagem manual
metadata: 
  node_type: memory
  type: project
  originSessionId: 08181b53-ca1d-41ae-a256-cc9d79527860
  modified: 2026-08-04T02:12:20.067Z
---

Levantamento de gaps pedido pelo orientador (ago/2026), derivado dos 7 trabalhos que citam Santos et al. (2023) + as 28 referências do artigo-base. Detalhamento em `coleta_dados_petr4/orientacoes/CITACOES_E_GAPS_2026-08-10.md` e `gaps_pesquisa.csv`.

**Why:** define a agenda técnica e editorial até a defesa (mar/2027) e dá resposta pronta às perguntas previsíveis da banca.

**How to apply:** atacar nesta ordem — **G1/G2** (editorial, custo zero), **G3** (MLM de domínio), **G6** (LLM × encoder), **G7** (comitê), **G12** (bootstrap). O G5 só quando a rotulagem for liberada.

**Os cinco que importam:**
- **G1 — volatilidade.** Nenhum dos 7 citantes nem das 28 referências prevê volatilidade; todos ficam em direção/retorno/carteira. É a contribuição principal e já está computacionalmente pronta — falta só reposicionar o texto.
- **G2 — transferência de domínio.** Santos declara 0,76/F1 0,73 em notícias gerais; medimos 0,58 (κ 0,371) em manchetes de PETR4. **Ninguém quantificou essa queda.** Tratar como RESULTADO, não como limitação.
- **G3 — adaptação de domínio setorial.** Santos propõe em Trabalhos Futuros ("aplicar a metodologia para setores específicos da bolsa"); 3 anos depois ninguém fez. MLM sobre as ~205k notícias, métrica = perplexidade. *Self-supervised.*
- **G6 — LLM × encoder em PT-BR.** Teles e Figueiredo (2025) mostram LLM ganhando, mas **só em inglês**. O teste em português é o vão que o artigo deixa aberto. Usa o gabarito que já existe.
- **G7 — comitê de modelos.** FinBERT-PT-BR (léxico) + pysentimiento (contexto), como Błoch et al. (2026) fizeram em História. Ataca exatamente a fraqueza medida na classe Neutra.

**Regra que decide tudo:** **12 dos 13 gaps NÃO consomem rotulagem manual.** Só o G5 (publicar um benchmark PT-BR de sentimento financeiro — que não existe: Santos não liberou os 503 textos) depende dela.

**Ressalva a repetir sempre:** isto é **hipótese de gap por levantamento dirigido**, não RSL. Antes de afirmar ineditismo no texto final, passar cada gap priorizado pela revisão sistemática (`datasets_refino/gerar_rsl_dataset.py`).

**Não perseguir:** treinar encoder do zero; estender a estratégia de carteira de Santos; índice × macroeconomia; ampliar o gabarito p/ 600 no protocolo atual; NER financeiro; migrar o pipeline inteiro p/ LLM.

Ver [[mentoria-emerson-agosto2026]], [[encoders-sentimento-ptbr]] e [[banca-julho2026-refino]].
