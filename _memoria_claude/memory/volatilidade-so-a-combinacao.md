---
name: volatilidade-so-a-combinacao
description: Prever "acima/abaixo do normal" falha sempre; prever o dia EXCEPCIONAL funciona, e só quando CVM e notícia coincidem (1,67×, p=0,00015)
metadata:
  type: project
---

Setembro/2026, PETR4, 2.059 pregões. Quarta parte do pedido de 16/09/2026.

**Prever se a volatilidade do pregão seguinte fica acima ou abaixo da média da
semana NÃO funciona** — todos os sinais perdem da classe majoritária, mesmo depois
de calibrar (a primeira versão previa ACIMA em 82–90% das noites quando a base é
44%). Melhor arm: "FR: intensidade do tom", +0,57 p.p., p=0,39.

**Motivo, e é o achado:** o Fato Relevante desloca a cauda, não o centro. Mediana
+3,4% (p=0,068); percentil 95 +19,6%. Só 3,9 p.p. de noites cruzam para "acima".
Um classificador binário só enxerga o cruzamento do meio.

**Trocando o alvo para "dia excepcional" (topo ~10%, base 9,4%) funciona:**

| noite | taxa | lift | p |
|---|---|---|---|
| nada acontecendo | 8,2% | 0,88× | 0,52 |
| só muito texto, sem CVM | 8,7% | 0,93× | 0,56 |
| só Fato Relevante, notícia calma (n=92) | 7,6% | 0,81× | 0,71 |
| **FR + noite de muito texto (n=300)** | **15,7%** | **1,67×** | **0,00015** |

**Nenhum sinal isolado funciona; só a combinação.** Fato sem repercussão não move
preço; repercussão sem fato também não.

**Ressalva:** notícia *dentro* das noites de FR dá +8,1 p.p. com p=0,057 — não
passa. No topo 5% a direção se mantém mas cai a 22 casos (p=0,22).

**Why:** responde diretamente ao que os orientadores pediram em 16/09 e é o
resultado de volatilidade mais forte da pesquisa; confirma [[efeito-de-cauda-auditoria-noticia]].

**How to apply:** ao relatar volatilidade, sempre enquadrar como previsão de
EVENTO EXTREMO, nunca como acima/abaixo da média — num fenômeno de cauda a escolha
do alvo importa mais que a escolha do modelo. Documentado em
`Mentorias/2026-09-16_Emerson_e_Julio/08..10`; código em `CVM/14_prever_volatilidade.py`.
Relacionado: [[cvm-estudo-de-evento]], [[banca-julho2026-refino]].

## A mesma coisa em PORCENTAGEM (é assim que ele quer ouvir)

Ele corrigiu o enquadramento em 21/09/2026: "chance de dia excepcional" não é o
foco da pesquisa — **a pesquisa pergunta se a notícia influencia preço e
volatilidade, e em QUANTO POR CENTO.** Medido em `CVM/15_quanto_a_noticia_move.py`,
PETR4, 2.309 pregões, contra piso de 618 noites sem nada:

| noite | volatilidade | tamanho da variação | volume |
|---|---|---|---|
| muita notícia, sem CVM | −3,5% | −0,6% | −5,0% * |
| Comunicado ao Mercado | −0,5% | −1,3% | −1,1% * |
| Fato Relevante | +6,4% | **+18,9%** * | +11,9% |
| **FR + muita notícia** | **+13,2%** * | **+38,2%** * | +19,4% |

Direção nula: tom muito negativo −0,170%, muito positivo +0,164%, p=0,291.
Concreto: oscila 1,31% após noite vazia, 1,70% após FR+notícia; giro 46,3 → 62,5 mi.

**Não confundir com o Artigo 1 (+9,6%):** lá são 54 papéis contra 105.896 pregões
sem evento; aqui só PETR4 contra controle que já exclui noites de notícia.
