# Mentoria de 26 de agosto de 2026 — Profs. Emerson e Julio

## O que foi pedido

Duas coisas.

**Primeira:** buscar sites ou blogs de especialistas em mercado financeiro,
verificar se eles classificam as notícias, e conferir no preço se o que eles
previram aconteceu.

**Segunda:** buscar publicações no site da CVM, classificá-las com o nosso
programa, e avaliar o impacto delas nos principais ativos da B3.

## O que foi feito, em linguagem simples

### Sobre os especialistas

**Não precisou buscar na internet — eles já estavam no nosso corpus.** Casas de
análise publicam o parecer, e a imprensa reproduz na manchete:

> *"Guide: reajuste do preço do GLP é positivo para a Petrobras"*

Encontramos **224 notícias assim, de 30 casas de análise** — BTG, XP, Itaú BBA,
Fitch, Moody's, S&P e outras.

**E o resultado foi duro para o nosso programa.** Diante das mesmas 224 notícias:

| | Positivas | Neutras | Negativas |
|---|---|---|---|
| Os analistas viram | **84,8%** | 3,1% | 12,1% |
| Nosso programa viu | **21,9%** | 52,7% | 25,4% |

**Ele reconhece a notícia ruim e é cego para a boa.**

### Uma armadilha que foi apontada e evitada

O pedido encadeava três coisas diferentes: (a) o especialista classifica a
notícia, (b) o especialista prevê alta ou baixa, (c) confere-se no preço. **O item
(c) valida o (b), não o (a).**

Se o analista disser "esta notícia é ruim" e a ação subir, **isso não torna o
rótulo errado** — mostra apenas que naquele pregão outra coisa pesou mais. Usar o
preço para julgar o rótulo seria medir com uma régua que já sabíamos ser de cara
ou coroa.

### Sobre a CVM

Coletamos **89.902 comunicados** dos dados abertos da CVM, de 2018 a 2026. E
descobrimos que a pergunta central — *essas publicações causaram impacto?* — **não
precisa do nosso programa**. É estudo de evento puro.

O resultado está detalhado na mentoria seguinte.

## O que está nesta pasta

O protocolo do experimento, o resultado da rotulagem por especialistas e o
primeiro resultado da CVM.
