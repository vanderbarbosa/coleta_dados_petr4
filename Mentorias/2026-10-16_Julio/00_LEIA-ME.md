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

### Confirmado e executado

A leitura foi confirmada em 18/10. O Prophet foi instalado e rodado nos 10
papéis, nos três alvos (direção, volatilidade e preço), no mesmo protocolo e
split 60/15/25 dos demais modelos.

## O resultado

### Primeiro, uma falha que eu mesmo encontrei e corrigi — duas vezes

**Erro 1.** Na primeira execução, ajustei o Prophet uma vez só e pedi para
prever os 579 pregões de teste de uma vez — quase dois anos à frente sem
nunca se reancorar. A tendência disparou: R²-OS de **−8.325%** na
volatilidade e **−69.604%** no preço. Isso não é "o Prophet é ruim", é
resultado degenerado, sem valor. Corrigido: passou a reajustar a cada 21
pregões, em janela expansiva.

**Erro 2, mais sutil e mais importante.** Mesmo corrigido, eu estava
comparando o Prophet contra uma régua que enxerga **mais informação que
ele**: a previsão ingênua ("repete o fechamento de ontem") sabe o preço de
ontem em todo dia do teste, enquanto o Prophet, no 21º dia de um bloco, ainda
olha o que sabia três semanas antes. É como comparar quem responde com a
notícia de ontem contra quem responde com a do mês passado. Corrigido com uma
**régua ancorada**: segurar o último valor conhecido antes do bloco, pelo
bloco inteiro — exatamente a mesma informação do Prophet.

### Com a comparação justa, o resultado é negativo e claro

| Alvo | Prophet contra a régua justa | Em quantos papéis ficou pior |
|---|---|---|
| Volatilidade | −47% a −265% | **10 de 10** |
| Preço | −180% a −533% | **10 de 10** |
| Direção | 46,3% a 51,1% | pior que o melhor clássico em **7 de 10** |

**Mesmo recebendo a mesma informação, o Prophet erra mais do que
simplesmente não fazer nada** (segurar o último valor). Extrapolar tendência
atrapalha numa série de preço de ação — faz sentido, porque preço é quase um
passeio aleatório, e a inclinação estimada no passado recente em geral já
virou antes de o bloco acabar.

Acrescentar o sentimento da CVM como regressora não mudou nada relevante.

### O brinde: isso responde o item 3 que ficou pendente de 12/10

A planilha traz uma coluna a mais: o quanto se ganha **só por se reatualizar
todo dia** em vez de uma vez por mês. O ganho é de **90% a 94%** — enorme.
Em outras palavras, nesta base, **a frequência de reatualização vale muito
mais que a sofisticação do modelo**. Reajustar o Prophet diariamente custaria
cerca de 21× mais processamento (cada ajuste leva ~1,3s) para disputar com
uma régua que é de graça. É o exemplo concreto que faltava para a pergunta do
professor sobre quando o esforço computacional se justifica.

### O que isso significa para a dissertação — e não é ruim

O contraponto **não enfraquece** o arranjo da pesquisa; ele delimita. O HAR e
os classificadores sobre atributos defasados não são preferidos por serem
elaborados, e sim porque trabalham com o dado da véspera em vez de projetar
tendência. E a conclusão central do capítulo se manteve sob um método de
previsão completamente diferente — **o sentimento informa o risco, não a
direção** —, o que lhe acrescenta robustez.

## Acrescentado à dissertação (obs. 3) — feito, com uma ressalva de git

Escrita a seção **4p — "Um contraponto de série temporal: o Prophet"**, em
`Exame_qualificacao/PesquisaMestrado_Qualificacao/capitulos/4p-prophet-series-temporais.tex`,
já ligada ao Capítulo 4 e com a referência do Prophet (Taylor e Letham, 2018)
acrescentada ao `references.bib`. O validador do próprio projeto
(`_validar_latex.py`) passou: 112 entradas no bib, todas as citações e
referências cruzadas resolvem, tudo balanceado, **pronto para compilar**.

A seção é gerada por `docs/_gerar_secao_prophet_tex.py`, que lê os números
direto do JSON do experimento — nada digitado à mão, no mesmo padrão dos
outros geradores de seção da pesquisa.

## A ressalva de git que continua valendo

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

## O que está nesta pasta

| Arquivo | O que é |
|---|---|
| `01_Explicacao_Prophet.md` | o texto curto para você explicar ao professor o que é o Prophet |
| `02_Prophet_vs_GARCH_SVM_XGBoost.xlsx` | 6 abas: Resumo, Direção, Volatilidade, Preço, McNemar, Notas |
| `_gerar_planilha_prophet.py` | gerador da planilha |

Código do experimento: `CVM/23_prophet_vs_garch_svm_xgboost.py`.
Dados: `CVM/dados/prophet_vs_garch_svm_xgboost.json`.
Seção da dissertação: `docs/_gerar_secao_prophet_tex.py` → `capitulos/4p-prophet-series-temporais.tex`.
