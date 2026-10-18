# Mentoria de 16 de outubro de 2026 — Prof. Julio

> **Nota de data:** pedido de 16/10/2026, preparado em 18/10 — dois dias
> depois. Mesma observação das últimas vezes: avise se a reunião foi adiada.

## O que foi pedido

1. Usar o Prophet para classificar as notícias capturadas da internet e os
   comunicados da CVM.
2. Comparar o resultado com os classificadores já usados até o momento.
3. Gerar uma tabela quantitativa/estatística comparando-os.

E seis observações: criar esta pasta; registrar as tarefas; acrescentar os
testes à dissertação; atualizar a memória do projeto; atualizar o git; e
lembrar que ficou faltando o item 3 da mentoria de 12/10 (quanto de ganho
justifica o esforço computacional).

## Item 3 da mentoria de 12/10 — já estava respondido, trago de volta aqui

Não ficou faltando — está em
`Mentorias/2026-10-12_Julio/00_LEIA-ME.md`, mas resumo de novo, para não
precisar procurar:

**Não há um percentual universal, mas há um piso calculável para esta
pesquisa.** Com os tamanhos de teste que usamos (579 a 653 pregões), o
intervalo de confiança de 95% de uma taxa de acerto é de **~±4 pontos
percentuais** — um ganho menor que isso não é distinguível de acaso, com a
nossa amostra. Acima desse piso, usar a régua que a pesquisa já adota:
**+2,4 pp** de ganho em direção, ou **R²-OS acima de +5%** em volatilidade,
foram os números que a própria dissertação já considerou dignos de reportar.
Só vale o esforço computacional extra se o ganho passar as duas coisas: o
teste estatístico (McNemar, corrigido por Bonferroni se houver mais de uma
comparação) **e** essa régua de tamanho.

## O obstáculo técnico real, antes de rodar qualquer coisa

**O Prophet não é um classificador de texto — é uma biblioteca de previsão
de séries temporais** (criada pelo Meta/Facebook). Ele recebe uma série de
números ao longo do tempo (`data`, `valor`) e projeta o valor futuro; pode
usar variáveis extras como regressoras, mas **não lê frase nenhuma e não
teria como "classificar uma notícia como positiva ou negativa"**. Isso é
trabalho do FinBERT (um encoder de linguagem), que já fazemos. São famílias
de modelo completamente diferentes — não dá para substituir uma pela outra
no mesmo papel.

Não instalei nem rodei nada ainda, porque rodar a coisa errada hoje
significaria comparar errado, tabelar errado, e **escrever errado na
dissertação** — melhor confirmar antes.

### A leitura mais provável, e a que eu recomendo

O professor provavelmente quer o Prophet como **mais um modelo de
PREVISÃO**, para comparar com o GARCH/SVM/XGBoost que já usamos — não como
substituto do FinBERT. Nesse caso, o Prophet entraria prevendo o preço, a
direção ou a volatilidade, usando como variável extra (regressora) o
sentimento que o FinBERT **já classificou** nos comunicados da CVM (todos os
10 papéis já têm isso pronto) e, onde existir, da notícia de jornal (hoje só
a PETR4 tem o pipeline, e está bloqueado nesta máquina por falta do corpus
classificado — mesmo problema de sempre).

### O que preciso que você confirme antes de eu rodar

1. Essa leitura está certa — Prophet como mais um modelo de previsão,
   comparado ao GARCH/SVM/XGBoost, e **não** como substituto do FinBERT?
2. Qual alvo: direção (como os outros 60 testes), volatilidade, ou os dois?
3. Rodar primeiro só na PETR4, ou já nos 10 papéis do Ibovespa?

Assim que confirmar, instalo o Prophet (não está nesta máquina ainda) e
rodo no mesmo protocolo e split 60/15/25 dos outros modelos, para a
comparação ser justa.

## Sobre acrescentar à dissertação (obs. 3) — um aviso antes de mexer

O texto da dissertação vive em
`Exame_qualificacao/PesquisaMestrado_Qualificacao/`, que está **fora do
git** (`.gitignore`) — "atualizar o git" não vai levar essas mudanças para o
GitHub sozinho; precisa subir manualmente no Overleaf depois (ver
`dissertacao-latex-overleaf` na memória do projeto). Além disso, há uma
branch `revisao/dissertacao-final-adaptacao-dominio`, já empurrada para o
GitHub, com capítulos novos (G3, caixa alta/sigmoide) que **ainda não foram
mesclados na `main`**. Antes de escrever o resultado do Prophet na
dissertação, preciso saber: trabalho nessa branch, ou direto na pasta local,
sem mexer no histórico do git?

## O que já está pronto nesta pasta

Só esta leia-me, por enquanto — o resto depende das confirmações acima.
