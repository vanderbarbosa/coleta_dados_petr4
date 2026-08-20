# Mentoria com o Prof. Dr. Emerson Cabrera Paraiso — material de apoio

**Mestrando:** Vanderlei Barbosa da Silva
**Orientador:** Prof. Dr. Julio Cesar Nievola · **Co-orientador:** Prof. Dr. Emerson Cabrera Paraiso
**Programa:** PUCPR — Pós-Graduação em Informática (PPGIa)
**Dissertação:** *O Impacto do Sentimento de Notícias Financeiras na Previsão de Direção e
Volatilidade do Ativo PETR4*

---

## O que foi pedido

> *Procurar outras pesquisas que estão fazendo o mesmo que eu — ler notícias e tentar prever a
> direção e a volatilidade que essas notícias possam causar — independentemente do ativo e de ser
> ou não em português. Encontrar pesquisas semelhantes e saber se podemos usá-las ou adaptá-las
> para melhorar os índices.*

Somam-se a esse pedido as três tarefas da mentoria de 13/08/2026: localizar um BERT financeiro para
o inglês, localizar artigos que o citam, e listar as aplicações encontradas.

---

## Por onde começar

**Se houver quinze minutos:** ler o documento `02_EXPLICACAO_PARA_LEIGOS.docx` inteiro. Ele resume
tudo em dez seções, sem jargão, e termina com um roteiro de dois minutos para conversa.

**Se houver cinco minutos:** abrir a planilha `01_PLANILHA_COMPARATIVA_PESQUISAS.xlsx` na aba
**Como usar**, que traz as doze ações propostas ordenadas por custo e retorno esperado.

---

## O que há nesta pasta

| Arquivo ou pasta | Conteúdo |
|---|---|
| **`01_PLANILHA_COMPARATIVA_PESQUISAS.xlsx`** | **A planilha pedida.** 25 pesquisas em 18 colunas, mais duas abas: os nossos números já corrigidos, e o plano de adaptação |
| **`02_EXPLICACAO_PARA_LEIGOS.docx`** | **Documento de abertura.** As cinco descobertas em linguagem comum |
| **`03_RESUMOS_E_COMO_USAR.md`** | Resumo de cada pesquisa próxima e como aproveitá-la |
| `fichas_das_pesquisas/` | 17 fichas detalhadas, separadas em duas subpastas: **A** — encoders e trabalhos em inglês; **B** — trabalhos que citam o FinBERT-PT-BR |
| `documentos_para_leigos/` | 7 documentos detalhados, um por assunto |
| `evidencias_dos_experimentos/` | Os resultados brutos, em JSON, de cada experimento citado |
| `scripts_dos_experimentos/` | O código que produziu cada resultado, comentado |

### A planilha, em detalhe

| Aba | O que traz |
|---|---|
| **Comparativo** | 25 pesquisas × 18 colunas: autor, ano, título, veículo, idioma, mercado, volume de textos, período, encoder, alvo, modelo, resultado, teste de significância, código público, relevância, **como usar** e ressalvas. Com filtro e cores por relevância |
| **Nossos números** | Os 14 resultados da dissertação, **já com as correções de agosto**, indicando onde cada um está no texto |
| **Como usar** | 12 ações propostas, ordenadas por custo, com origem e justificativa |

---

## As cinco descobertas

### 1. O patamar de 0,58 é normal — não é falha do português

O FinBERT **inglês**, aplicado a manchetes de um setor específico sem ajuste, obtém F1 de
**0,555**. O nosso FinBERT-PT-BR obtém **0,579** na mesma situação. **O nosso é ligeiramente
superior.** O teto que resistiu a nove intervenções é o comportamento esperado de qualquer
codificador financeiro em subdomínio, e não uma deficiência do recurso em português.

### 2. O efeito de cauda foi confirmado por fora

Halousková e Lyócsa (2025) fizeram o mesmo desenho sobre **404 ações do S&P 500**, com dados de
cinco minutos, e obtiveram o maior ganho justamente **nos dias de variação extrema** — 14,99%
contra 12,74% na média. É a mesma conclusão a que chegamos com um ativo brasileiro e dados
diários, por caminho inteiramente independente.

### 3. Parte dos números altos não resiste a exame — mas três trabalhos nos superam de fato

Convém separar as duas coisas com honestidade, porque a distinção será cobrada.

**Três números da tabela comparativa não são comparáveis ao nosso:**

- **Bollen (2011), 86,7%** — são **13 acertos em 15 pregões**, sobre um índice e não uma ação. E o
  resultado **foi refutado**: Lachanski e Pav (2017) não encontraram evidência fora da amostra e
  atribuíram o achado a garimpagem de dados.
- **Schumaker (2009), 71,2%** — mede o preço **vinte minutos após** a notícia. É reação, não
  previsão do pregão seguinte, e é o melhor entre vários esquemas.
- **Barak (2017), 83,6%** — outro mercado e outra tarefa. A técnica central já foi replicada aqui
  (Seção 4.d) e ficou no patamar da classe majoritária.

**Mas três outros trabalhos obtiveram, sim, resultados superiores aos nossos, e isso precisa ser
declarado sem rodeios:**

| Trabalho | O que obtiveram | O que obtivemos | Comparável? |
|---|---|---|---|
| **Halousková e Lyócsa (2025)** | **superam o HAR em 98,76% dos casos**, $-12{,}74\%$ de erro | **não superamos o HAR** ($p = 0{,}64$) | **sim** — mesmo alvo, mesma referência, fora da amostra |
| **Bodilsen e Lunde (2025)** | melhora significativa sobre a família HAR | não superamos com recorte algum | **sim** — mesmo objetivo |
| ***Electronics* (2025), art. 4680** | **F1-macro de 0,707** com 1.500 rótulos | **F1-macro de 0,579** | **sim** — mesma tarefa |

Nos dois primeiros casos as diferenças de desenho explicam a distância --- eles empregam 404 ativos
contra o nosso único, variância realizada de cinco minutos contra Parkinson diário, e métodos de
encolhimento contra mínimos quadrados simples. **A explicação, contudo, não anula o resultado.**
No terceiro, a diferença é de volume de supervisão: 1.500 exemplos anotados contra os nossos 352.

**A leitura honesta é esta:** esta pesquisa não apresenta o melhor desempenho do conjunto levantado.
Apresenta a avaliação mais rigorosa --- Mino e Williamson não avaliam fora da amostra, Bollen não
sobreviveu à replicação, Barak e Schumaker reportam o máximo entre configurações. Rigor e desempenho
são méritos distintos, e convém não os confundir na defesa.

**E os três trabalhos que nos superam constituem, precisamente, o roteiro de melhoria:** mais
ativos, medida intradiária, métodos de combinação e mais rótulos. Todos figuram no plano da aba
*Como usar*.

### 4. O melhor resultado da pesquisa apareceu ao testar um artigo de primeira linha

Bodilsen e Lunde (2025), no *Journal of Applied Econometrics*, sustentam que notícia da empresa não
acrescenta ao modelo padrão e que notícia macroeconômica acrescenta, sobretudo em prazos longos.
**Testamos na PETR4 e a hipótese inverte-se:**

| Recorte | 1 dia | 5 dias | 22 dias | Média |
|---|---|---|---|---|
| **Empresa** | +1,03% | +0,37% | **+1,77%** | **+1,06%** |
| Empresa + petróleo | +0,30% | −0,43% | +0,21% | +0,03% |
| Petróleo | −0,12% | −0,48% | −1,06% | −0,55% |
| **Macro** | −0,33% | **−1,09%** | **−1,79%** | **−1,07%** |
| Todas | −0,30% | −1,93% | −2,45% | −1,56% |

A notícia macro **piora de forma significativa** ($p = 0{,}0146$ e $p = 0{,}0200$); a notícia da
empresa em 22 pregões rende **+1,77% com $p = 0{,}0574$** — o resultado mais próximo da superação
do modelo padrão obtido até aqui. A metade da hipótese relativa ao **horizonte** confirma-se.

A explicação é econômica: o "macro" deles é macroeconomia **doméstica dos Estados Unidos** aplicada
a ações **norte-americanas**; o nosso é majoritariamente **geopolítica internacional**, ruído para
um ativo brasileiro isolado. Soma-se a natureza **estatal** da PETR4, cujo risco idiossincrático
domina.

### 5. Há um alvo de previsão que nunca testamos

Hashamia e Maldonado (2025) preveem a **direção da volatilidade** — se amanhã oscilará mais ou
menos que hoje — a partir de 592.858 manchetes da Reuters sobre petróleo, **com código público**.
É a via do meio entre a direção do preço, que é quase acaso, e o nível da volatilidade, em que o
modelo padrão é adversário duríssimo. **É a recomendação principal.**

---

## Duas correções a declarar antes da apresentação

**1. O número 54,93% deve sair.** Ele circula como acurácia da ponderação por confiança, mas é
número de **validação**. No conjunto de teste a ponderação rende **50,31%**, contra **53,88%** sem
ponderar — ou seja, ponderar **piora**. O número correto a apresentar é **54,5%** (XGBoost, três
atributos). A revisão completa está na Seção 4.n da dissertação.

**2. O escore de confiança não é *softmax*, é sigmoide.** Prova aritmética: numa distribuição
*softmax* de três classes a classe vencedora não pode ficar abaixo de $1/3$; observam-se 397
escores abaixo de $0{,}3333$. A causa está documentada na Seção 4.j.

---

## Nota de método

O levantamento foi feito por busca na web entre 13 e 18 de agosto de 2026, com verificação direta
das páginas de origem sempre que acessíveis. Registram-se as limitações:

- **Quatro textos não puderam ser lidos na íntegra** por bloqueio do editor (HTTP 403) ou por PDF
  ilegível. Nesses casos os dados provêm da página de resumo, do repositório público ou de fontes
  secundárias, e vêm assinalados nas fichas.
- **A autoria de um artigo não foi recuperada** — o da *Electronics* v. 14, n. 23, art. 4680, de
  onde vem o número 0,555. O dado está confirmado por duas fontes independentes, mas a referência
  completa precisa ser conferida no MDPI antes de ser citada.
- **Contagens de citação divergem entre bases.** Adota-se a cifra verificável, com a fonte
  declarada.

Todas as afirmações desta pasta que dependem de fonte não verificada estão marcadas como tais.
