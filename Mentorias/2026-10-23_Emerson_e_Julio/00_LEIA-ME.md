# Mentoria de 23 de outubro de 2026 — Profs. Emerson Paraiso e Julio Nievola

## O que foi pedido

1. Juntar a análise de sentimento do FinBERT com **GARCH + SVM/XGBoost**.
2. Juntar a análise de sentimento do FinBERT com o **Prophet**.
3. Comparar os índices dos dois para projeção de **volatilidade** e **direção**.
4. Calcular o **percentual e o valor em reais** de ganho ou perda, se um
   investidor médio usasse um ou outro — sobre a média de reais por investidor.

E, acima de tudo: **revisar tudo e gerar resultados que dê para compreender e
explicar.** Esse foi o pedido mais importante, e é o que organiza esta pasta.

## O que mudou em relação ao que já estava feito

Boa parte do cálculo já existia das mentorias anteriores. O que foi feito agora:

- **Acrescentado o braço que faltava:** FinBERT + Prophet na simulação em
  reais. É exatamente o braço que os senhores pediram para comparar com o
  FinBERT + GARCH/SVM/XGBoost, e ele não existia.
- **Acrescentado o percentual**, que antes só saía em reais.
- **Refeita a apresentação dos resultados do zero.** O material anterior estava
  correto mas difícil de ler: seis braços de modelo, três réguas de comparação
  diferentes e números como "−532%" sem explicação do que significavam.

## Como ler esta pasta, na ordem

| Arquivo | Para quê |
|---|---|
| **`01_EXPLICACAO_SIMPLES.docx`** | **Comece por aqui.** Explica do zero quem é cada programa, contra quem eles competem e o que deu — em linguagem comum, com analogias |
| `02_Comparativo_FinBERT.xlsx` | As tabelas estatísticas. A primeira aba é "O placar": três perguntas, três respostas |

**São só duas peças, de propósito.** O material das mentorias anteriores tinha
documento técnico, documento resumido, planilha e leia-me para cada assunto —
e virou mais do que dava para ler. Aqui o método e as ressalvas estão neste
próprio leia-me, os números estão na planilha, e a explicação está no
documento 01. Se os senhores quiserem a versão técnica em separado, ela se
monta a partir da planilha em poucos minutos.

## O resultado, em quatro linhas

1. **Volatilidade:** o GARCH é muito melhor que o Prophet — vence em 10 de 10
   papéis, e por margem enorme (+83% a +93% contra números negativos).
2. **Direção:** nenhum dos dois funciona. Nenhum supera o palpite fixo com
   significância estatística, em nenhum dos 10 papéis.
3. **O FinBERT:** não mudou o resultado de nenhum dos dois times. Melhorou em
   cerca de 5 dos 10 papéis — que é exatamente o que uma moeda produziria.
4. **Em dinheiro:** comprar e segurar (não fazer nada) venceu os dois times na
   maioria dos papéis.

## Por que isso não enfraquece a dissertação

A tese central sempre foi que **o sentimento informa o risco, não a direção**.
Agora isso foi testado por um caminho completamente diferente — outro tipo de
modelo, outra família de método — e deu a mesma coisa. Resultado que se repete
sob método diferente é resultado **mais forte**, não mais fraco.

E o contraponto delimita o arranjo da pesquisa com precisão: o GARCH não é
preferido por ser elaborado, e sim porque funciona; o Prophet, que é mais
simples de configurar, fracassa justamente onde o GARCH acerta.

## Método, em resumo

- **Papéis:** as 10 maiores do Ibovespa que já têm comunicados da CVM
  classificados e preço coletados (critério: peso na carteira oficial da B3).
- **Janela:** treino 05/06/2017 a 28/12/2022; validação até 22/05/2024; teste
  **23/05/2024 a 15/09/2026 (579 pregões)**, cronológico 60/15/25, sem
  embaralhar.
- **Sentimento:** o que o FinBERT-PT-BR já classificou nos comunicados da CVM
  entregues após as 17h — reaproveitado, não reclassificado.
- **Notícia de jornal:** não entrou, em nenhum papel e em nenhum dos times.
  Continua faltando o corpus classificado nesta máquina.

## Scripts usados

| Script | O que faz |
|---|---|
| `CVM/23_prophet_vs_garch_svm_xgboost.py` | o experimento: direção, volatilidade e preço nos 10 papéis |
| `CVM/24_simulacao_reais_por_investidor.py` | a simulação em reais e percentual |
| `_gerar_explicacao_simples.js` | gera o documento 01 |
| `_gerar_planilha_comparativo.py` | gera a planilha 02 |

Os dados ficam em `CVM/dados/prophet_vs_garch_svm_xgboost.json` e
`CVM/dados/simulacao_reais_por_investidor.json`.
