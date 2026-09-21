---
name: escopo-e-ml-de-verdade
description: CORREÇÃO DE ESCOPO — contar positivas/negativas NUNCA foi o método; o escopo é encoder + XGBoost/SVM + fusão. E a CVM não acrescenta ao protocolo do Cap.3
metadata:
  type: feedback
---

**21/09/2026.** O usuário corrigiu, e com razão: *"não é contar as notícias
positivas e negativas... usar o encoder para classificar e usar Machine Learning
para projetar direção e volatilidade. Contar nunca esteve no nosso escopo."*
E depois: *"leia a pesquisa, não desfoque, não elocubre."*

**O método da dissertação está no Capítulo 3** (`Exame_qualificacao/
PesquisaMestrado_Qualificacao/capitulos/3-metodologia.tex`):
fusão precoce em t−1 (Retorno_Ontem, Volatilidade_Ontem do GARCH(1,1),
Sentimento_Ontem do FinBERT) → **SVM-RBF e XGBoost** (300 árvores, depth 3,
lr 0,05, subsample 0,9) → divisão cronológica **60/15/25** → linhas de base
classe majoritária E apenas-preços → testes **binomial e McNemar**.
Volatilidade: **HAR de Corsi** (1, 5, 22 dias) + combinação quantílica de pesos
variáveis, medida por MAE e **R²-OS**.

A matriz pronta é `Mestrado_PETR4/base_master_petr4.csv` (2.610 pregões).

**Resultado ao acrescentar a CVM** (`CVM/18_pesquisa_com_cvm.py`, teste = 653):
o pipeline REPRODUZ o Cap.4 (majoritária 53,14% nos dois). Mas **nenhum McNemar
passa**: CVM sobre notícia dá p=0,162 (SVM) e p=0,312 (XGB); o embedding no SVM
**PIORA** (27×55, p=0,0026). Volatilidade: HAR +6,90% → notícia +7,53% → CVM
+7,47%. **A CVM não acrescenta.**

**Armadilha a nunca repetir:** SVM+CVM deu 54,36%, acima da majoritária — mas
**AUC 0,489, abaixo de 0,50**. Acertou por chutar na proporção certa. O p
binomial de 0,028 testa contra 50%, não contra a majoritária.

**Why:** eu havia inventado desenho próprio (regras à mão, janela expansiva)
em vez de seguir o que a pesquisa especifica, e isso desfocou várias entregas.

**How to apply:** antes de qualquer experimento novo, **ler o Cap.3** e usar o
protocolo de lá. Regra à mão serve só para MEDIR efeito (ver
[[volatilidade-so-a-combinacao]]), nunca para responder "prever". Falta o
experimento decisivo: **embeddings das 54.259 notícias** — hoje elas entram com
um número por pregão enquanto a CVM entra com 768 dimensões.
Relacionado: [[revisao-ponderacao-confianca]], [[cvm-estudo-de-evento]].
