# O artigo em linguagem simples

Para ler em cinco minutos antes da reunião.

---

## A pergunta

Quando uma empresa de capital aberto tem algo importante a contar — venda de
ativo, troca de diretoria, decisão judicial —, **ela é obrigada por lei a avisar**.
A Resolução CVM nº 44 manda divulgar todo fato *capaz de influir na cotação*.

**A lei presume que aquilo move preço. O artigo verifica se a presunção é
verdadeira.**

---

## Por que ninguém tinha feito isso direito

Para saber se a notícia moveu o preço, é preciso saber **o que veio primeiro**.

Se o comunicado sai às 11h e a ação cai às 11h30, a sequência é ambígua: pode a
notícia ter derrubado o preço, ou pode a empresa ter se manifestado *porque* o
preço já caía.

**A solução é usar só o que foi divulgado com a bolsa fechada.** Aí não há dúvida:
a informação chegou, ninguém pôde negociar, e a primeira oportunidade é a abertura
do dia seguinte.

**Mas isso exige saber a hora — e a CVM não publica a hora nos dados abertos.**

É aqui que entra a contribuição do artigo. Recuperamos a hora oficial de **20.419
comunicados**, com precisão de segundos. Como, está no documento
`03_COMO_OBTIVEMOS_A_HORA.md`.

---

## O que medimos

Três coisas diferentes, que costumam ser confundidas:

| Régua | O que é | A analogia |
|---|---|---|
| **Volatilidade** | o tamanho do balanço do preço, sem olhar o lado | *"o mar estava agitado?"* |
| **Volume** | quantas ações trocaram de mão | *a lotação do estádio* |
| **Direção** | subiu ou desceu | *"para onde o barco foi?"* |

E comparamos o pregão seguinte à divulgação com **a média da semana anterior
daquela mesma ação** — não com uma média de meses atrás.

> **Por que a semana anterior é mais exigente:** volatilidade é grudenta. Depois
> de uma semana agitada vem outra agitada. Bater a média da própria semana é bem
> mais difícil que bater uma média velha.

---

## Uma correção que quase passou despercebida

A conta é uma divisão: *o sacolejo do dia dividido pela média da semana*.

Parece que 1,00 seria o ponto neutro. **Não é.**

Medimos a mesma divisão em **105.896 pregões em que não houve comunicado nenhum**,
e ela já dá **1,031**.

**Por quê:** um dia pode ser cinco vezes mais agitado que a média, mas nunca cinco
vezes menos — o mínimo é zero. Os dias agitados puxam a média para cima e os
calmos não puxam de volta na mesma proporção.

> **Sem essa correção, teríamos anunciado +21,9% de volatilidade e +44,6% de
> volume. Os números corretos são +9,6% e +16,5%.**

---

## Os resultados

### 1. Quando as empresas divulgam

| | |
|---|---|
| até 09h59, antes da abertura | 23,9% |
| das 10h às 16h59, com o pregão aberto | **11,6%** |
| das 17h em diante, após o fechamento | **64,5%** |

**Quase 90% divulgam fora do horário de negociação**, como a norma recomenda.

### 2. A hora recuperada é verdadeira — e há prova

Registramos a previsão **antes** de testar: quem divulga de manhã deve mover o
preço no mesmo pregão; quem divulga à noite, no seguinte.

| Divulgado | Move em |
|---|---|
| de manhã | **o mesmo pregão** |
| com o pregão aberto | **o mesmo pregão** |
| à noite | **o pregão seguinte** |

Diferença entre os grupos: **0,786**, com valor-p de **3 × 10⁻²³**.

**Se a hora fosse inventada, esse padrão não apareceria.**

### 3. A divulgação move o risco, não a direção

| Medida | Sem comunicado | Com comunicado | Excesso |
|---|---|---|---|
| volatilidade | 1,031 | 1,130 | **+9,6%** |
| volume | 1,060 | 1,235 | **+16,5%** |
| direção | — | — | **nada** |

Em números concretos: a ação oscila **2,03%** num dia comum e **2,25%** no dia
seguinte a um comunicado. O giro passa de **11,2** para **19,2 milhões** de ações.

**A direção deu zero — e tinha de dar.** O rótulo "Fato Relevante" não diz se a
notícia é boa ou ruim. Havendo fatos relevantes bons e ruins, as altas e as baixas
se cancelam.

### 4. A lei acerta

| | Fato Relevante | Comunicado ao Mercado | Razão |
|---|---|---|---|
| volatilidade | +18,2% | +6,9% | **2,6×** |
| volume | +36,4% | +12,2% | **3,0×** |

**O que a norma chama de mais relevante mexe quase três vezes mais.** É validação
empírica do critério do regulador.

E há um detalhe que fortalece: **quem enquadra o documento é a própria empresa**,
não a CVM. Que a separação apareça mesmo com esse ruído sugere que a diferença
real seja ainda maior.

### 5. E o achado central

**59% das divulgações não movem o preço.**

| | Fato Relevante | Comunicado |
|---|---|---|
| o caso típico (mediana) | 1,065 | 0,975 |
| percentil 99 | 3,440 | 3,174 |
| **não movem nada** | **51,9%** | **62,0%** |

**O Fato Relevante mediano produz movimento indistinguível de uma semana comum.**

O excesso médio de 9,6% **não vem de todos os eventos produzirem um pouco de
movimento — vem de uma minoria produzir muito.**

---

## A frase que resume o artigo

> **A presunção legal de relevância é válida em média e falsa na maioria dos casos
> individuais.**

Parece paradoxo, mas não é. O conjunto dos Fatos Relevantes move volatilidade e
volume com certeza estatística. **O Fato Relevante típico não move nada.**

---

## O que o artigo NÃO afirma

Quatro coisas que estão declaradas como limitação, e que convém você dizer antes
que perguntem:

1. **Não é causalidade.** É associação bem medida, com grupo de controle amplo e
   ordem temporal inequívoca. Mas ninguém sorteia quais empresas divulgam.
2. **Em 28,8% das noites há mais de um comunicado da mesma empresa** — nesses, o
   movimento não é atribuível a um documento específico. Os testes foram
   refeitos só com os isolados, sem mudança.
3. **O conteúdo não foi lido.** O artigo mede o efeito da divulgação, não do que
   ela diz. Foi escolha deliberada: quisemos medir sem a incerteza de um
   classificador de texto.
4. **Faltam 15% dos eventos**, por indisponibilidade de cotação de quatro papéis.
