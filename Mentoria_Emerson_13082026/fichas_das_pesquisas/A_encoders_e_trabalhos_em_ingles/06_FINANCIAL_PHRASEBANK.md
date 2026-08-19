# Financial PhraseBank (Malo et al., 2014) — o padrão-ouro de rotulagem

> **Por que esta ficha existe:** ela responde, com um protocolo documentado e citável, à objeção
> que o Prof. Emerson levantou em 29/07/2026 — a de que a rotulagem, para ser válida, precisaria ser
> feita por especialistas em finanças. A resposta é: **ele tem razão, e a literatura internacional
> mostra exatamente como se faz.**

## 1. Ficha bibliográfica

| Campo | Conteúdo |
|---|---|
| **Referência** | MALO, P. et al. **Good debt or bad debt: detecting semantic orientations in economic texts.** *Journal of the Association for Information Science and Technology*, 2014. |
| **Instituição** | Aalto University School of Business (Finlândia) |
| **Disponibilidade** | Público — `takala/financial_phrasebank` no Hugging Face |
| **Papel na área** | É o conjunto sobre o qual **ambos** os FinBERT ingleses são ajustados |

## 2. O protocolo de anotação

| Elemento | Especificação |
|---|---|
| **Sentenças** | 4.846, de notícias financeiras e comunicados de empresas |
| **Anotadores** | **16 pessoas com formação adequada em mercados financeiros** |
| **Composição do painel** | 3 pesquisadores e 13 mestrandos da Escola de Negócios de Aalto, com ênfase em finanças, contabilidade e economia |
| **Anotações por sentença** | **5 a 8** |
| **Critério de rotulagem** | "Atribuir o rótulo conforme o modo como a informação da sentença **poderia afetar o preço da ação da empresa mencionada**" |

## 3. Os quatro subconjuntos por concordância

Em vez de descartar as sentenças controversas ou de impor um rótulo por maioria simples, os autores
publicam **quatro versões** do conjunto, cada uma com um piso de concordância diferente:

| Subconjunto | Sentenças | Interpretação |
|---|---|---|
| Concordância $\geq$ 50% | 4.846 | inclui os casos ambíguos |
| Concordância $\geq$ 66% | 4.217 | |
| Concordância $\geq$ 75% | 3.453 | |
| **Concordância de 100%** | **2.264** | apenas os casos inequívocos |

Note-se que **apenas 47% das sentenças obtêm concordância unânime** entre anotadores treinados em
finanças. Esse dado, por si só, é um argumento poderoso: mesmo entre especialistas, mais da metade
dos casos gera divergência. A tarefa é intrinsecamente ambígua.

## 4. O confronto com o nosso conjunto-ouro

| Elemento | Financial PhraseBank | **Nosso conjunto-ouro** |
|---|---|---|
| Itens | 4.846 sentenças | 300 manchetes |
| Anotadores | **16, com formação em finanças** | **1 (o mestrando)** |
| Anotações por item | **5 a 8** | **1** |
| Métrica de concordância | Sim, com quatro cortes | **Não existe** |
| Critério | Efeito esperado no preço da ação | Efeito esperado no preço da PETR4 (mesma lógica) |

**Três observações se impõem.**

**Primeira: o Prof. Emerson estava certo.** O padrão internacional exige, de fato, anotadores com
formação em finanças. Isso está documentado e é citável.

**Segunda: a barra é mais baixa do que parece.** Os anotadores não eram operadores de mercado com
décadas de experiência — eram **13 mestrandos** em finanças, contabilidade e economia, e 3
pesquisadores. O critério declarado é "formação adequada em mercados financeiros". Isso é
alcançável: um grupo de mestrandos do PPGIa ou de um programa de finanças da própria PUCPR
satisfaria o critério.

**Terceira, e a mais importante: o problema maior não é a formação, é a redundância.** A diferença
decisiva entre os dois protocolos não é "especialista contra leigo" — é **5 a 8 anotações por item
contra 1**. Sem múltiplas anotações não há como calcular concordância, e sem concordância não há
como distinguir erro do modelo de ruído do anotador. Essa é, aliás, exatamente a limitação que a
dissertação já declara no Capítulo 5.

## 5. Proposta concreta, se a rotulagem for retomada

O protocolo do Financial PhraseBank oferece um desenho pronto, e há um caminho de custo baixo:

1. **Não ampliar o volume — ampliar a redundância.** Reanotar as mesmas 300 manchetes com 3
   anotadores, em vez de rotular 900 novas com 1. Três anotações por item já permitem calcular o
   *alpha* de Krippendorff e o *kappa* de Fleiss.
2. **Recrutar entre mestrandos de finanças, economia ou contabilidade**, e declarar essa
   composição — é exatamente o que Malo et al. (2014) fizeram e documentaram.
3. **Publicar os subconjuntos por concordância**, à maneira deles. O subconjunto de concordância
   total é o padrão de referência mais defensável; os demais medem a ambiguidade da tarefa.
4. **Usar o critério deles, textualmente:** "como esta informação poderia afetar o preço da ação
   mencionada". É o mesmo que a nossa coluna `Direcao_Esperada_PETR4` já registra, o que facilita a
   comparação.

**Ressalva necessária, e ela é séria.** O teste de teto reportado na Seção 4 da dissertação mostrou
que um classificador **perfeito** elevaria a acurácia direcional em apenas 1,2 ponto percentual.
Ampliar a qualidade da rotulagem **não vai melhorar a previsão de direção** — isso já está
estabelecido. O valor de refazer a rotulagem é outro, e é preciso ser explícito quanto a ele:
permite afirmar com rigor **de quem é a culpa** pelo desempenho de 0,58 — do modelo ou do anotador.
Hoje não é possível saber, e essa indeterminação é uma fragilidade real da dissertação.

## 6. O dado adicional que muda a leitura do nosso 0,58

Um trabalho de 2025 (*Electronics*, v. 14, n. 23, art. 4680 — autoria a confirmar) construiu um
conjunto-ouro de **1.500 manchetes financeiras setoriais** anotadas manualmente e mediu:

| Condição | Macro-F1 |
|---|---|
| FinBERT inglês, sem ajuste (*zero-shot*) | **0,555** |
| FinBERT inglês, ajustado nas 1.500 manchetes | **0,707** |

**Compare-se com o nosso número: macro-F1 de 0,579 para o FinBERT-PT-BR no conjunto-ouro.**

O modelo em inglês, com todo o seu corpus de bilhões de tokens, obtém **0,555** quando aplicado sem
ajuste a manchetes setoriais. O nosso obtém **0,579** — ligeiramente superior. **A degradação por
transferência de domínio que a dissertação documenta não é um problema do português nem do
FinBERT-PT-BR: é um fenômeno geral da abordagem.**

Este é, provavelmente, o achado de maior valor argumentativo de todo o levantamento, e deve ser
incorporado ao Capítulo 4 e ao Capítulo 5.

**Mas há um contraponto que também precisa ser dito.** Eles subiram de 0,555 para 0,707 com 1.500
manchetes. O nosso experimento G3 de adaptação, com cerca de 350 exemplos, **piorou** o desempenho.
A diferença de volume — 1.500 contra 350 — é a explicação mais simples e mais plausível. Isso não
contradiz o resultado do G3; contextualiza-o: **não é que ajustar não funcione, é que 350 exemplos
não bastam.** A dissertação deve dizer isso com essas palavras, porque é mais preciso e mais útil
do que a formulação atual.
