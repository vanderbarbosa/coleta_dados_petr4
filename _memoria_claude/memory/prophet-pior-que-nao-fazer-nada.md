---
name: prophet-pior-que-nao-fazer-nada
description: Prophet testado nos 10 papéis (16/10/2026) — com a mesma informação, erra MAIS que segurar o último valor conhecido, em 10 de 10 papéis na volatilidade e no preço; e a frequência de reancoragem vale mais que a sofisticação do modelo
metadata:
  type: project
---

**16-18/10/2026.** Pedido do Prof. Julio: usar o Prophet e comparar com o
GARCH+SVM/XGBoost, nos 10 principais ativos da B3, em direção, volatilidade e
preço. A premissa do pedido ("usar o Prophet para classificar notícias") foi
corrigida antes de rodar — ver [[pendencia-prophet-mentoria-16out]]; o
Vanderlei confirmou a leitura: Prophet entra como modelo de PREVISÃO, com o
sentimento do FinBERT (comunicados da CVM) como regressora.

**DUAS armadilhas de desenho, ambas minhas, ambas corrigidas — e a segunda é
a lição que fica.**

*Primeira:* ajustar o Prophet uma vez e pedir previsão para os 579 pregões de
teste de uma vez (≈2 anos sem reancorar) faz a tendência divergir: R²-OS de
−8.325% (volatilidade) e −69.604% (preço). Resultado degenerado, não
resultado ruim. Corrigido com reajuste a cada 21 pregões, janela expansiva.

*Segunda, mais sutil:* comparar o Prophet contra a ingênua DIÁRIA é desleal —
a ingênua vê o fechamento de ontem todo dia, o Prophet (no 21º dia do bloco)
vê o de 21 pregões atrás. Criada a **"ingênua ancorada"**: segura o último
valor antes do bloco, pelo bloco inteiro, com exatamente a mesma informação
do Prophet. **É esta a régua correta.** Sem ela, o número parece catástrofe
do modelo quando é, em boa parte, assimetria de informação.

**O resultado, com a comparação justa (n=579 pregões de teste por papel):**

| alvo | Prophet vs régua ancorada | papéis em que ficou pior |
|---|---|---|
| volatilidade | −47% a −265% | **10 de 10** |
| preço | −180% a −533% | **10 de 10** |
| direção | 46,3% a 51,1% | pior que o melhor clássico em 7 de 10 |

**Mesmo com a mesma informação, o Prophet erra mais que NÃO FAZER NADA.**
Extrapolar tendência é passivo em série de preço de ativo (quase passeio
aleatório): a inclinação estimada já virou antes de o bloco acabar. O
sentimento da CVM como regressora não mudou nada relevante.

**O achado que responde o item 3 de 12/10 (ver
[[piso-estatistico-custo-computacional]]):** a coluna da persistência diária
contra a ancorada mede o ganho de só reatualizar todo dia em vez de uma vez
por mês — **+90% a +94%**. Nesta base, **a frequência de reancoragem vale
muito mais que a sofisticação do modelo**. Reajustar o Prophet diariamente
custaria ~21× mais processamento (≈1,3s por ajuste) para disputar com uma
régua de custo zero. É o exemplo concreto que faltava para a pergunta do
professor sobre quando o esforço computacional se justifica.

**Para a dissertação, isso FORTALECE o arranjo atual**, não enfraquece: o HAR
e os classificadores sobre atributos defasados não são preferidos por
elegância, mas porque operam sobre o dado da véspera em vez de projetar
tendência. E a conclusão central — o sentimento informa o risco, não a
direção — se manteve sob um método de previsão inteiramente distinto.

**Entregue:** `CVM/23_prophet_vs_garch_svm_xgboost.py` →
`dados/prophet_vs_garch_svm_xgboost.json`;
`Mentorias/2026-10-16_Julio/02_Prophet_vs_GARCH_SVM_XGBoost.xlsx` (6 abas);
seção **4p** da dissertação, gerada por `docs/_gerar_secao_prophet_tex.py`,
com a referência Taylor e Letham (2018) no bib — validador do projeto passou.

**How to apply:** sempre que comparar um modelo de horizonte longo contra um
de horizonte curto, construir a régua ancorada ANTES de olhar o número. E
nunca citar o R²-OS do Prophet sem dizer contra qual das duas réguas.
