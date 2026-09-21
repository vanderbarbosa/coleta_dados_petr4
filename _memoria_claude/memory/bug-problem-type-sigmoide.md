---
name: bug-problem-type-sigmoide
description: O config.json do FinBERT-PT-BR declara multi_label_classification — quebra o treino e faz a pipeline usar sigmoide em vez de softmax
metadata: 
  node_type: memory
  type: project
  originSessionId: 08181b53-ca1d-41ae-a256-cc9d79527860
  modified: 2026-08-09T13:51:28.391Z
---

Descoberto em 08/08/2026, ao tentar treinar o notebook do G3.

O `config.json` publicado de `lucas-leme/FinBERT-PT-BR` declara:
```json
"problem_type": "multi_label_classification"
```
Está **errado** para 3 classes mutuamente exclusivas. Duas consequências distintas:

## 1. Quebra qualquer TREINO
O modelo usa `BCEWithLogitsLoss` e espera alvos `[batch, 3]` em vez de `[batch]`:
```
ValueError: Target size ([16]) must be the same as input size ([16, 3])
```
**Correção:** passar `problem_type="single_label_classification"` no `from_pretrained`. Já aplicado em `notebooks/g3_adaptacao_dominio_colab.ipynb` e em `orientacoes/_codigos/reconstrucao_santos_etapa2_sentimento.py`.

## 2. A pipeline aplica SIGMOIDE, não softmax
`TextClassificationPipeline` escolhe a função pela `problem_type`: multi_label → **sigmoide**.

**O que NÃO é afetado:** os rótulos. A sigmoide é monotônica, o argmax é o mesmo. Logo **acurácia 0,580, F1, kappa, matriz de confusão, calibração ACC, teste do teto — tudo continua válido.**

**O que É afetado:** o `Score_Confianca`. No corpus de 205.697 notícias: média 0,686, **máximo 0,8729, ZERO acima de 0,90**. Num softmax de 3 classes, valores acima de 0,95 seriam comuns.

⚠️ **Correção de interpretação minha:** eu havia lido o teto de ~0,86 na confiança como "incompatibilidade de domínio / o modelo sabe que não sabe". **É assinatura de sigmoide**, não de incerteza. O argumento em [[diagnostico-erro-neutro]] (H6) precisa ser revisto.

⚠️ **Afeta o ISM:** `Indice_Sentimento = polaridade × Score_Confianca`. A magnitude está numa escala errada. **Recalcular o ISM com softmax explícito** ao reprocessar o corpus. O sinal e a ordenação não mudam; a escala sim.

**How to apply:** ao reprocessar, calcular `softmax(logits)` explicitamente em vez de usar o `score` da pipeline; e gravar os **logits completos**, que também destrava o teste de reponderação por prior que ficou inconclusivo.

**Vale contar ao Lucas Leme** — é bug real no artefato dele, afeta todo mundo que usa os scores da pipeline, e é conserto de uma linha no `config.json`.

Ver [[bug-caixa-alta-e-dataset-santos]], [[diagnostico-erro-neutro]], [[calibracao-ism-acc]].
