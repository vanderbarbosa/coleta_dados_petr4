---
name: pendencia-prophet-mentoria-16out
description: pedido de 16/10/2026 — usar Prophet "para classificar notícias e comunicados" é tecnicamente incompatível (Prophet é previsão de série temporal, não classificador de texto); aguardando confirmação do desenho antes de rodar
metadata:
  type: project
---

**16-18/10/2026.** Mentoria pediu: usar o Prophet para classificar notícias
de jornal e comunicados da CVM, comparar com os classificadores já usados, e
gerar tabela comparativa. Acrescentar à dissertação, atualizar memória e git.

**Obstáculo técnico real, não burocrático.** Prophet (Meta/Facebook) é
biblioteca de **previsão de série temporal** — recebe (data, valor) e
projeta o futuro, aceita regressoras extras, mas **não processa texto**. Não
tem como "classificar uma notícia como positiva/negativa" com ele — isso é
trabalho de encoder de linguagem (FinBERT, já em uso). Não rodei nada ainda:
rodar a coisa errada geraria tabela errada e, pior, conteúdo errado na
dissertação.

**Leitura mais provável, proposta ao Vanderlei (aguardando confirmação):**
Prophet como mais um modelo de PREVISÃO (direção/volatilidade/preço),
comparável ao GARCH+SVM/XGBoost já usado — não como substituto do FinBERT.
Usaria como regressora o sentimento que o FinBERT já classificou nos
comunicados da CVM (pronto p/ os 10 papéis — ver
[[comparativo-top10-ibovespa]]). Notícia de jornal como regressora segue
bloqueada (mesmo motivo de sempre: falta corpus classificado nesta
máquina).

**Perguntas em aberto:** (1) a leitura acima está certa? (2) qual alvo —
direção, volatilidade, ou os dois? (3) só PETR4 ou os 10 papéis de uma vez?

**Também em aberto — acrescentar à dissertação:** o texto vive em
`Exame_qualificacao/PesquisaMestrado_Qualificacao/`, FORA do git
(gitignored) — commitar não basta, precisa subir manual no Overleaf (ver
[[dissertacao-latex-overleaf]]). Existe uma branch não mesclada,
`revisao/dissertacao-final-adaptacao-dominio`, já no GitHub, com capítulos
novos (G3, caixa alta/sigmoide) pendentes de merge na `main`. Perguntei ao
Vanderlei se trabalho nessa branch antes de escrever o resultado do Prophet.

**Why:** evitar gastar a noite rodando e escrevendo algo que não responde ao
que o professor pediu de fato.

**How to apply:** só rodar Prophet depois de resposta às 3 perguntas acima;
instalar o pacote primeiro (`pip install prophet`, não está nesta máquina).
Prazo: pedido de 16/10, preparado em 18/10 — mentoria pode já ter passado,
checar com o Vanderlei.
