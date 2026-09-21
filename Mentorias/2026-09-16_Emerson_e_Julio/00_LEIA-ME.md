# Mentoria de 16 de setembro de 2026 — Profs. Emerson e Julio

## O que foi pedido

Uma **engenharia reversa**: temos a publicação e temos o que o preço fez depois.
Confrontar as duas coisas.

Com um recorte importante, sugerido pelos professores: **usar só o que foi
publicado após o fechamento do pregão**, e olhar o **pregão seguinte**.

Em duas rodadas — primeiro com a classificação que já vem na publicação, depois
com a nossa.

E uma sugestão do Prof. Emerson: comparar a volatilidade do dia seguinte com a
**média da semana anterior**, e não com uma média distante.

## O que foi feito, em linguagem simples

### O recorte da noite é a melhor parte do desenho

> É como trancar todo mundo fora do estádio, pôr a notícia no telão, e só então
> abrir os portões. **Ninguém pôde reagir antes.**

Para fazer esse recorte precisávamos da hora exata. **A CVM não publica a hora nos
dados abertos** — e recuperá-la virou a principal contribuição da pesquisa. Como
isso foi feito está em `Artigos/Artigo_1_O_Relogio_da_CVM/03_COMO_OBTIVEMOS_A_HORA.md`.

### A sugestão do Prof. Emerson estava certa, e é mais exigente

Volatilidade é grudenta: depois de uma semana agitada vem outra agitada. **Bater a
média da própria semana anterior é muito mais difícil** que bater uma média de
cem dias atrás.

### Uma correção que evitou dois números errados

A razão entre o dia e a média da semana **já vale mais que 1,00 sem evento
algum** — porque um dia pode ser cinco vezes mais agitado que a média, mas nunca
cinco vezes menos. Medimos esse piso em 105.896 pregões sem comunicado.

Sem esse controle teríamos anunciado **+21,9%** de volatilidade e **+44,6%** de
volume. Os números corretos são **+9,6%** e **+16,5%**.

## Os resultados

| Pergunta | Resposta |
|---|---|
| A publicação move o preço? | **Sim — o risco, não a direção** |
| Move sempre? | **Não. 59% não movem nada** |
| Dá para saber o lado? | Só com a nossa leitura, e só no Fato Relevante |
| A lei acerta? | **Sim. Fato Relevante mexe 2,6× mais que Comunicado** |

## O que está nesta pasta

O plano do experimento, os resultados das duas rodadas, a explicação completa em
linguagem comum e a planilha de apoio.
