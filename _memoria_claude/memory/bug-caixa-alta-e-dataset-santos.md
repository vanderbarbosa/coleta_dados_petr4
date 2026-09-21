---
name: bug-caixa-alta-e-dataset-santos
description: O dataset dos 503 textos ESTÁ público; e-mail certo é gmail; e achamos bug real — 21.619 manchetes em CAIXA ALTA contra modelo cased
metadata: 
  node_type: memory
  type: project
  originSessionId: 08181b53-ca1d-41ae-a256-cc9d79527860
  modified: 2026-08-08T17:37:38.473Z
---

Achados de 08/08/2026, a partir de links que o Vanderlei localizou.

## 1. O dataset de Santos ESTÁ publicado
**https://huggingface.co/datasets/lucas-leme/Sentiments-FinBERT-PT-BR** → `sentiments.csv`, Apache 2.0. Baixado em `orientacoes/_santos_sentiments.csv`.
**661 linhas:** Negativo 203 · Positivo 160 · Neutro 140 (= os **503 de treino**) + **Não se aplica 158**.
⚠️ **São a base de TREINO do modelo — avaliar o FinBERT sobre eles é contaminado.** Servem p/ treinar (G7/G3) e p/ caracterizar o domínio de origem, nunca p/ medir.

## 2. E-mail correto: `lucaslssantos99@gmail.com`
O do artigo (`@usp.br`) está morto — foi por isso que voltou. O gmail está no README do dataset. Reenviar **sem o pedido nº 2** (base rotulada), que já é pública.

## 3. Nosso uso do encoder está CORRETO
`pipeline("sentiment-analysis", ...)` é **alias** de `"text-classification"` — mesma `TextClassificationPipeline`. Não há diferença funcional para o model card oficial.

## 4. ⚠️ BUG REAL — caixa alta contra modelo *cased*
**WP_Petronoticias publica 100% das manchetes em CAIXA ALTA: 21.619 notícias = 10,5% do corpus.**
O FinBERT-PT-BR tem `do_lower_case: False` (herda o BERTimbau *cased*).
- **Nenhuma** das 12 palavras-chave do domínio existe em caixa alta no vocab (29.795 tokens)
- Cobertura do vocabulário: **22,2% em caixa alta vs 78,6% em caixa normal**
- O modelo classifica **84,3% delas como Neutral** (vs 32,0% nas normais); confiança 0,589 vs 0,697
- No gabarito: caixa alta acc **0,528** / κ **0,195** (n=36) vs normal acc 0,587 / κ 0,386 (n=264)
- O humano discordou: modelo disse 24 neutras, humano disse 17

**Correção pronta:** `src/sentimento/normalizar_caixa_titulos.py` (`.capitalize()` preservando siglas ANP/OPEP/CNPE/CADE/FPSO…) → recupera cobertura para 77,6%. Já gerou `Mestrado_PETR4/noticias_titulos_normalizados.csv`.

## 5. ⚠️ Unidade de texto ERRADA
Os textos de treino de Santos são **sentenças de corpo de notícia**, não manchetes:
- **Santos: mediana 39 palavras** (só 15,9% têm ≤15)
- **Nosso `Título`: mediana 13 palavras**
- **Nosso `Título`+`Resumo`: mediana 42** ← praticamente igual ao de Santos

**How to apply:** rodar a ablação G9 (`Título` × `Título`+`Resumo`) sobre o gabarito — o rótulo humano é do evento, não do recorte, então **não consome rotulagem nova**.

**Why:** todos os números medidos até aqui (acc 0,580, viés de 87% do ISM, matriz de confusão) vêm de um corpus com 10,5% mal tokenizado e com a unidade de texto errada. **São um PISO, não inválidos.** Dizer isso na dissertação é honesto e provavelmente favorável.

Documento: `orientacoes/ACHADOS_DATASET_E_USO_DO_ENCODER.md`.
Ver [[diagnostico-erro-neutro]], [[calibracao-ism-acc]], [[conjunto-ouro-quatro-rotulos]].
