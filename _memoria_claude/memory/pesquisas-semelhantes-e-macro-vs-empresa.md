---
name: pesquisas-semelhantes-e-macro-vs-empresa
description: "6 pesquisas que leem notícias p/ prever direção e volatilidade; e o experimento que inverteu Bodilsen & Lunde: na PETR4 notícia da EMPRESA ajuda e MACRO atrapalha"
metadata: 
  node_type: memory
  type: project
  originSessionId: 08181b53-ca1d-41ae-a256-cc9d79527860
  modified: 2026-08-19T21:39:38.127Z
---

Feito em 18/08/2026. O Vanderlei corrigiu o escopo que eu tinha usado: o Emerson **não** pediu só BERTs financeiros em inglês — pediu **pesquisas que fazem o mesmo que ele (ler notícias → prever direção e volatilidade), qualquer ativo, qualquer idioma**, e se dá para adaptar.

Documento: `orientacoes/PESQUISAS_SEMELHANTES.md`. Docx: `EXPLICACAO_SIMPLES_PESQUISAS_SEMELHANTES.docx`. Seção 4.o da dissertação.

## As 6 pesquisas (por proximidade)
1. **Hashamia & Maldonado (2025)** arXiv:2508.20707 — **a mais próxima**. Brent, **592.858 manchetes Reuters** 2014–2023, alvo = **DIREÇÃO da volatilidade** (binário), baseline HAR, McNemar. Testam VADER/TextBlob/FinBERT/**CrudeBERT** e embeddings GloVe/FastText/BERT/FinBERT/Gemini/LLaMA. **Código público:** `github.com/Romina-Hashami/Textual_Direction_Prediction_Oil_Volatility`. Achados: **contagem de notícias > sentimento**; **FastText foi o melhor embedding**.
2. **CrudeBERT** (Kaplan et al., ICEIS 2023, arXiv:2305.06140) — FinBERT ajustado ao petróleo, `Captain-1337/CrudeBERT`, 777 downloads/mês. Rótulos continuam pos/neg/neutro; **a inovação é o conjunto de treino, montado a partir de choques de OFERTA e DEMANDA** (teoria econômica).
3. **Bodilsen & Lunde (2025)**, *J. Applied Econometrics* 40(1):18–36 — notícia de empresa NÃO acrescenta ao HAR; **macro acrescenta**, ganho maior em **horizonte longo**. (Lunde = o de Hansen & Lunde 2005, já no bib.)
4. Halousková & Lyócsa (2025) — ver [[encoders-ingles-levantamento]]
5. Mino & Williamson (2025) — ver [[encoders-ingles-levantamento]]
6. Rahimikia & Poon, arXiv:2108.00480 — embeddings financeiros para volatilidade realizada

## ⭐ O experimento: testamos Bodilsen & Lunde na PETR4 e INVERTEU
`src/modelagem/10_macro_vs_empresa_horizontes.py` → `macro_vs_empresa.json`. 5 recortes × 3 horizontes, HAR+Parkinson, janela expansiva, 795 previsões, Diebold-Mariano.

Ganho % sobre o HAR (positivo = sentimento ajuda):
| Recorte | 1d | 5d | 22d | Média |
|---|---|---|---|---|
| **EMPRESA** (CAT1+CAT6) | +1,03 | +0,37 | **+1,77** | **+1,06** |
| EMP+PETR (CAT1+CAT2) | +0,30 | −0,43 | +0,21 | +0,03 |
| PETROLEO (CAT2) | −0,12 | −0,48 | −1,06 | −0,55 |
| **MACRO** (CAT3+CAT5+CAT7) | −0,33 | **−1,09** | **−1,79** | **−1,07** |
| TODAS | −0,30 | −1,93 | −2,45 | −1,56 |

- **MACRO PIORA significativamente:** p=0,0146 (5d) e p=0,0200 (22d), DM favorecendo o HAR puro. Não é ausência de ganho — é prejuízo.
- **EMPRESA em 22 dias: +1,77%, p=0,0574** — 🏆 **o resultado mais próximo de vencer o HAR que a pesquisa já teve.**
- **A metade do horizonte CONFIRMA-SE**: o melhor resultado é em 22 dias, não em 1.

**Why (explicação econômica, defensável):** (a) o "macro" deles é macro **doméstica dos EUA** para ações **dos EUA**; o nosso é **geopolítica internacional** (46.412 de 76.438) — ruído para um ativo brasileiro isolado. (b) **PETR4 é estatal**: política de preços de combustíveis, intervenção do controlador, troca de diretoria e dividendos dominam o risco idiossincrático.

⚠️ **Tensão nova a registrar:** para **ASSOCIAÇÃO** o melhor recorte é CAT1+CAT2 ([[filtro-relevancia-primeiro-ganho]], +23%, p=0,001); para **PREVISÃO** é CAT1+CAT6. **Os dois critérios não premiam o mesmo corte.** Provável causa: correlação é sensível à cauda e a notícia de petróleo contribui nos choques do barril, mas a previsão do dia típico é dominada por ruído. Mais uma manifestação do efeito de cauda ([[efeito-de-cauda-auditoria-noticia]]).

## Prioridades de adaptação
1. **Mudar o alvo para DIREÇÃO da volatilidade** (Hashamia & Maldonado) — via do meio entre direção do preço (≈acaso) e nível da volatilidade (HAR imbatível). Nunca testado. Custo baixo.
2. **Adotar EMPRESA + horizonte 22d** e varrer horizontes intermediários p/ ver se p=0,057 vira p<0,05. Custo muito baixo.
3. **Contagem de notícias contra a DIREÇÃO da volatilidade** — falhou contra o nível (p=0,222), nunca testada contra a direção.
4. **Embeddings no lugar da cabeça de sentimento** — 4ª confirmação independente ([[revisao-ponderacao-confianca]]).
5. **Rotular por mecanismo econômico** (CrudeBERT): oferta, demanda, intervenção do controlador, política de preços, dividendos. **Responde à objeção do Emerson deslocando o critério do juízo subjetivo para a teoria econômica** — classificação de fato, não de opinião.
6. Dados intradiários. Custo alto.

⚠️ **A tabela comparativa que o Vanderlei montou traz "54,93% com ponderação por confiança Softmax" — número REVISADO e incorreto** (é validação; no teste dá 50,31% vs 53,88% da polaridade pura; e não é softmax, é sigmoide). Usar **54,5%**. Ver [[revisao-ponderacao-confianca]].

Ver [[numeros-altos-da-literatura]], [[encoders-ingles-levantamento]], [[filtro-relevancia-primeiro-ganho]] e [[efeito-de-cauda-auditoria-noticia]].
