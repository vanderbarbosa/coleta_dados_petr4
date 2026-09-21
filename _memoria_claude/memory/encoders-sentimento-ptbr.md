---
name: encoders-sentimento-ptbr
description: Encoders candidatos p/ o sentimento PT-BR financeiro — o que já foi testado, por que os testes falharam e qual a recomendação atual
metadata:
  node_type: memory
  type: reference
  originSessionId: 9477fc8b-d091-44dd-9de3-ae811eed9316
  modified: 2026-08-04T01:43:38.322Z
---

Modelo em produção: `lucas-leme/FinBERT-PT-BR` (BERTimbau + 1,4M notícias MLM + 503 rotuladas; Apache 2.0; 177k downloads/mês; última atualização 13/02/2024).

**Já testados contra o conjunto-ouro (300 manchetes) — todos PIORES que o FinBERT-PT-BR (58,0% / κ 0,37):**
BERTimbau large −1,67 pp · BERTimbau base −5,33 pp · Albertina-100M −12 a −16 pp.
**Os testes são inconclusivos, não conclusivos:** 300 exemplos, 3 épocas, sem adaptação de domínio, sem *gradual unfreezing*, lr inadequado, e comparação assimétrica (o FinBERT entra pronto, os outros com cabeça de classificação aleatória). O Albertina colapsou p/ a classe majoritária (κ = 0,000 em 3 dos 5 folds). Santos usou 11 épocas, lr 5e-6, gradual unfreezing e um LM já adaptado ao domínio.

**Recomendação atual (mudou em ago/2026):** NÃO trocar de encoder. Replicar a etapa 1 de Santos — **adaptação de domínio por MLM** (máscara 15%, lr 2e-5) sobre as ~205k notícias, medida por **perplexidade** (Santos: 1,51 → 1,24). É *self-supervised*, **não consome rótulo** → é a única frente que avança sob a suspensão da rotulagem. Ordem: (1) MLM sobre o próprio FinBERT-PT-BR; (2) MLM sobre BERTimbau-large; (3) Albertina **900M** só depois; (4) mdeberta-v3-base como controle. Nunca o Albertina 100M de novo.

**`turing-usp/FinBertPTBR` — DESCARTAR.** O model card o declara *"Depreciated model"* e aponta para o `lucas-leme/FinBERT-PT-BR`; é o antecessor do mesmo grupo (Lucas Leme é coautor). Citar só como antecedente histórico.

**Armadilha do artefato:** o `config.json` do FinBERT-PT-BR tem `id2label` correto (**0=POSITIVE, 1=NEGATIVE, 2=NEUTRAL** — ordem contraintuitiva) mas `label2id` quebrado (`LABEL_0/1/2`). O Script 03 tem fallback `LABEL_*` **invertido**; hoje não é acionado (a pipeline retorna as strings), mas inverteria o ISM em silêncio se fosse.

Ressalva que permanece válida: o gargalo da DIREÇÃO é a eficiência do mercado, não o encoder — sentimento melhor tende a ajudar mais a VOLATILIDADE.

Ver [[mentoria-emerson-agosto2026]] e [[banca-julho2026-refino]].
