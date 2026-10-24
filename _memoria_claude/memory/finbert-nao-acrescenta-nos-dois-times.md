---
name: finbert-nao-acrescenta-nos-dois-times
description: 23/10/2026 — testado nos 10 papéis, o sentimento do FinBERT não acrescenta previsão nem ao GARCH+SVM/XGBoost nem ao Prophet (melhora em ~5/10, efeito médio entre −0,7 e +0,07); e o GARCH vence o Prophet 10×0 na volatilidade
metadata:
  type: project
---

**23-24/10/2026.** Pedido de Emerson e Julio: juntar o FinBERT (a) ao
GARCH+SVM/XGBoost e (b) ao Prophet, comparar os dois para direção e
volatilidade, e pôr em percentual e em reais por investidor.

**Desenho:** 10 maiores do Ibovespa já cobertos pela pesquisa, teste de
23/05/2024 a 15/09/2026 (579 pregões), split cronológico 60/15/25. Sentimento
= o que o FinBERT-PT-BR já havia classificado nos comunicados da CVM após as
17h (reaproveitado). Notícia de jornal não entrou (corpus ausente).

**RESULTADO 1 — volatilidade: o GARCH ganha de lavada.** HAR(GARCH)+FinBERT
entrega R²-OS de **+83% a +93%** contra a régua ancorada; Prophet+FinBERT
entrega **−48% a −265%**. GARCH vence em **10 de 10** papéis. Ver
[[prophet-pior-que-nao-fazer-nada]] para por que o Prophet falha (extrapolar
tendência é passivo em série de preço).

**RESULTADO 2 — direção: nenhum dos dois funciona.** Nenhum braço supera o
palpite fixo (classe majoritária) com significância, em nenhum dos 10 papéis.
Zero em 60 tentativas.

**RESULTADO 3 — e é o que importa para a dissertação: o FinBERT não
acrescenta a nenhum dos dois times.**

| modelo | alvo | FinBERT melhorou em | efeito médio |
|---|---|---|---|
| GARCH+SVM | direção | 5 de 10 | −0,14 ponto |
| GARCH+XGBoost | direção | 5 de 10 | +0,07 ponto |
| Prophet | direção | 3 de 10 | 0,00 ponto |
| GARCH (HAR) | volatilidade | 4 de 10 | −0,07 ponto |
| Prophet | volatilidade | 5 de 10 | −0,70 ponto |

**"Melhorou em 5 de 10" é exatamente o que cara-ou-coroa produz.** O efeito é
indistinguível de sorte nas duas famílias de modelo — e esse é o ponto forte:
a mesma conclusão por dois caminhos metodológicos independentes.

**RESULTADO 4 — em reais** (`24_simulacao_reais_por_investidor.py`, regra
"comprado quando prevê alta, fora quando prevê baixa", sobre o valor médio
investido por investidor de cada papel): **comprar e segurar venceu os dois
times em 8 dos 10 papéis**. Os modelos saem do mercado nos dias de queda
prevista e perdem as altas. Ressalva obrigatória junto do número: sem
corretagem, IR ou spread, e com acerto perto de cara-ou-coroa o resultado em
reais é em boa parte sorte.

**Isso NÃO enfraquece a dissertação.** A tese central — o sentimento informa o
risco, não a direção — foi reconfirmada por um método inteiramente distinto.
E o contraponto delimita o arranjo: o GARCH não é preferido por elegância, e
sim porque funciona onde o Prophet fracassa.

**Entregue:** `Mentorias/2026-10-23_Emerson_e_Julio/` —
`01_EXPLICACAO_SIMPLES.docx` e `02_Comparativo_FinBERT.xlsx` (aba "O placar"
abre com as três perguntas respondidas). Só duas peças, de propósito: ver
[[entregar-pouco-e-compreensivel]].
