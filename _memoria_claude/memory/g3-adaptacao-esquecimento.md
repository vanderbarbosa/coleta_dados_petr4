---
name: g3-adaptacao-esquecimento
description: "G3 fechado — adaptação de domínio melhora a perplexidade em 49% mas DEGRADA a classificação (p=0,022); linha do classificador encerrada"
metadata: 
  node_type: memory
  type: project
  originSessionId: 08181b53-ca1d-41ae-a256-cc9d79527860
  modified: 2026-08-10T22:49:12.529Z
---

Experimento G3 concluído em 10/08/2026 (Colab + `src/sentimento/comparar_adaptacao_dominio.py` → `Mestrado_PETR4/comparacao_adaptacao_dominio.json`).

## Desenho (o controle C foi o que tornou tudo interpretável)
| | Adaptação MLM | Rótulos | F1-macro |
|---|---|---|---|
| **A** publicado | não | 503 + CV (Santos) | 0,5790 |
| **B** adaptado | **sim**, 205k notícias | 352 | **0,5279** |
| **C** controle | não | 352, **mesmo protocolo de B** | **0,5844** |

## Resultado — bootstrap pareado, 10.000 reamostras
- **C − B = +0,0563 · IC95 [+0,0084, +0,1056] · p = 0,0216 → SIGNIFICATIVA.** A adaptação **DEGRADOU** a classificação.
- C − A = +0,0053 · p = 0,69 → **não** significativa. **Nosso protocolo reproduz o modelo publicado com só 352 rótulos** — valida a implementação e torna a comparação B×C confiável.
- A − B = +0,0510 · p = 0,048 → significativa.

## O achado principal (é reportável e interessante)
**A adaptação funcionou como modelo de linguagem e falhou na tarefa:**
- Perplexidade no mesmo holdout (10k textos, seed 42): **BERTimbau 7,195 → adaptado 3,669 (−49%)**
- Mas F1-macro caiu 0,056

**Dano concentrado na classe POSITIVA:** recall 0,448 (C) → **0,281** (B). Negative e Neutral praticamente iguais.
É **esquecimento catastrófico**: o MLM apagou parte da representação de sentimento que o fine-tune de Santos instalara no corpo, e 352 rótulos não bastaram para recuperar.

⚠️ **A perplexidade "36.511 → 3,67" da 1ª rodada era INVÁLIDA** — o checkpoint publicado é classificador e não tem `cls.predictions.*`; toda a cabeça de MLM veio MISSING (36.511 ≈ vocab 29.794 = cabeça aleatória). A referência válida é a do BERTimbau (7,195).

## G6 — também negativo
Qwen2.5-3B: acc 0,480 · F1 0,388 · κ 0,140 contra 0,580/0,579/0,371 do FinBERT. Previu **Neutral em 248 de 300**; recall de negativo 0,113. ⚠️ É LLM **pequeno e aberto** — não refuta Teles, que usou Gemini 2.0-flash. Teste justo exigiria modelo de fronteira via API.

**How to apply:** **encerrar a linha de melhoria do classificador** — são 8 tentativas medidas sem ganho. Migrar para: recalcular o ISM com softmax, refazer a volatilidade, e **escrever**. Os negativos viram a seção "hipóteses testadas e rejeitadas", com bootstrap — vale mais que melhoria alegada sem teste.

Ver [[revalidacao-tres-hipoteses-rejeitadas]], [[diagnostico-erro-neutro]], [[bug-problem-type-sigmoide]].
