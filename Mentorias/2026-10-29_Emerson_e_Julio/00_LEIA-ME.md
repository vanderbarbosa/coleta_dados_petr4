# Mentoria de 29 de outubro de 2026 — Profs. Emerson Paraiso e Julio Nievola

## A hipótese que foi testada

Na conversa anterior surgiu uma constatação: em **60,4% dos pregões não há
comunicado nenhum** na véspera, e nesses a coluna de sentimento é um zero de
preenchimento. Medir "o sentimento ajuda?" sobre todos os pregões dilui o
sinal em dois terços de dias mudos.

Daí a hipótese, e ela é razoável: **restringindo a avaliação aos pregões que
tiveram comunicado, os índices devem melhorar.**

## A resposta, sem rodeio: a hipótese não se confirmou

Os índices **não melhoraram — pioraram.** E, mais importante que o resultado,
está o motivo, que é instrutivo.

### O que foi feito

Para os 10 papéis, nos mesmos 579 pregões de teste, com o mesmo protocolo:

| Avaliação | O que mede |
|---|---|
| Todos os pregões | o que já tínhamos |
| **Só os pregões com comunicado** | a hipótese |
| Só os pregões sem comunicado | o controle |
| **Modelo especialista** | treinado *só* com dias de comunicado, para afastar a objeção de que o modelo geral não estaria preparado |

E duas fórmulas de sentimento em paralelo (ver adiante), porque havia uma
divergência entre o código e a dissertação.

### Por papel: amostra pequena demais para concluir qualquer coisa

| Papel | Pregões com comunicado | Margem de erro |
|---|---|---|
| PETR4 | 165 (28,5%) | ±7,6 pontos |
| VALE3 | 127 (21,9%) | ±8,7 pontos |
| B3SA3 | 76 (13,1%) | ±11,2 pontos |
| BBDC4 | 33 (5,7%) | ±17,1 pontos |
| **ABEV3** | **5 (0,9%)** | **não avaliável** |

Com margem de erro de ±8 a ±17 pontos, **não há como detectar um efeito de 2
ou 3 pontos** — que é a ordem de grandeza relevante aqui. Qualquer número que
apareça nessa faixa é ruído.

Resultado: piorou em **8 dos 9 papéis avaliáveis**, e **nenhum braço, em
nenhum papel, superou a classe majoritária com significância**. O modelo
especialista também não resolveu.

### Agrupando os 10 papéis — aí sim há poder estatístico

Como nenhum papel isolado tinha amostra suficiente, juntei os dez num só
conjunto. Isso é legítimo porque todos passaram pelo mesmo protocolo e pela
mesma janela. O número de dias com comunicado sobe para **670** e a margem de
erro cai para **±3,8 pontos**.

| Arranjo | Todos os dias | Só com comunicado |
|---|---|---|
| SVM — só preço | −1,43 pp (p=0,030) | **−4,48 pp (p=0,022)** |
| XGBoost — só preço | −1,61 pp (p=0,015) | **−5,82 pp (p=0,003)** |
| SVM — preço + sentimento (A) | −1,57 pp (p=0,017) | −2,69 pp (p=0,164) |
| XGBoost — preço + sentimento (A) | −1,54 pp (p=0,020) | −3,43 pp (p=0,081) |
| SVM — preço + sentimento (B) | −1,54 pp (p=0,020) | −3,13 pp (p=0,104) |
| XGBoost — preço + sentimento (B) | −0,64 pp (p=0,331) | −1,34 pp (p=0,486) |

*(ganho sobre a classe majoritária de cada subconjunto; negativo = pior que o palpite fixo)*

**Com poder estatístico de verdade, todos os arranjos ficam abaixo do palpite
fixo — e nos dias com comunicado o déficit é maior, não menor.**

### Um padrão que vale registrar, mas não afirmar

Repare nas duas primeiras linhas contra as quatro seguintes: nos dias com
comunicado, os arranjos **só com preço** ficam em −4,5 e −5,8, enquanto os
**com sentimento** ficam entre −1,3 e −3,4. Ou seja, nesses dias o sentimento
parece **reduzir o erro**, ainda que não produza acerto.

É um padrão consistente, mas **não testei a diferença entre os arranjos
diretamente** — isso exigiria um teste pareado que não fiz. Fica como
conjectura, não como achado.

## O que isso significa — e por que fortalece a dissertação

A limitação **não está no modelo nem na forma de representar o sentimento.
Está na frequência do fenômeno.** Divulgação oficial depois do fechamento é
evento raro: de 1% a 28% dos pregões, conforme o papel. Para detectar um
efeito de 2 ou 3 pontos com o rigor que esta pesquisa adota, seria preciso
mais eventos do que uma década de histórico de dez papéis oferece.

**O caminho não passa por modelo mais elaborado — passa por base maior.**
Mais ativos, horizonte mais longo, ou os dois.

E isso é coerente com o efeito de cauda que a pesquisa já documentou: a
divulgação move o preço, com significância inequívoca, mas o movimento se
concentra numa minoria de eventos. A regularidade que a previsão exigiria não
está no caso típico.

## O refinamento proposto depois: só os dias com tom declarado

Surgiu uma segunda proposta, razoável: descartar também os pregões cujos
comunicados são **todos neutros**, treinando e projetando só onde há tom
declarado — positivo ou negativo. Começando pela PETR4.

**Medi antes de rodar, e registrei a expectativa:**

| PETR4 | Treino | Teste | Margem de erro |
|---|---|---|---|
| Todos os pregões | 1.389 | 579 | ±4,1 |
| Com qualquer comunicado | 588 | 165 | ±7,6 |
| **Só com tom declarado** | **290** | **56** | **±13,1** |

O filtro vai na direção contrária da que precisamos: encolhe a amostra, e a
amostra já era o gargalo.

**O que aconteceu:** pior que o previsto. **Oito dos dez papéis não puderam
nem ser avaliados** — ITUB4 ficou com 3 pregões de teste, ABEV3 com 1. Só
PETR4 (56) e VALE3 (49) sobreviveram. Mesmo juntando as duas, são 105 pregões
e margem de erro de ±9,6.

| Agrupado (n=105) | Ganho | p |
|---|---|---|
| XGBoost — preço + tom, treinado em tudo | +5,71 pp | 0,282 |
| SVM — preço + tom, treinado em tudo | −7,62 pp | 0,119 |
| XGBoost — só preço, **treinado só nos dias com tom** | −11,43 pp | 0,024 |
| SVM — só preço, **treinado só nos dias com tom** | −10,48 pp | 0,040 |

O **+5,71 pp** parece animador e **não é**: está dentro da margem de ±9,6, tem
p=0,282, e é um entre oito braços. O limiar de Bonferroni para as **132
tentativas acumuladas do estudo** é de 0,000379 — nada chega perto.

E repare nas duas últimas linhas: treinar **só** com dias de tom piorou muito,
porque o modelo perdeu a maior parte dos dados de treino.

### Duas ressalvas que esse resultado carrega

1. **O filtro usa um rótulo que erra.** A validação contra o conjunto-ouro
   humano desta própria pesquisa aferiu **58% de acurácia** no rótulo do
   FinBERT. Filtrar por "não-neutro" descarta dias que não eram neutros e
   mantém dias que eram.
2. **Foi a quarta fatia testada.** Cada tentativa nova eleva a chance de um
   achado fortuito — por isso o limiar de Bonferroni acumulado está reportado.

### O padrão das quatro tentativas, dito sem rodeio

**Cada filtro que aplicamos troca sinal por tamanho de amostra — e a amostra
já era o fator limitante.** Não é falta de engenho na especificação; é um
limite de informação da base disponível.

## O que mudou de verdade: trocar o ALVO

Depois das quatro tentativas de fatiar a base, a pergunta virou outra: e se o
problema não for *quais dias* olhamos, mas **o que estamos tentando prever?**

**A incoerência que encontrei na pesquisa:**

| | O que prevê ou mede |
|---|---|
| Estudo de evento (Artigo 1) | retorno **anormal** — desconta o Ibovespa pelo modelo de mercado |
| Experimentos de ML (scripts 16 a 26) | retorno **bruto** |

Os dez papéis sobem ou descem **juntos em 64,5% dos pregões** — quase metade
do movimento diário de cada ação é o mercado, não a ação. **O lado de ML vinha
tentando prever algo que é ~49% ruído de mercado**, que nenhum sentimento de
uma empresa específica poderia explicar. O lado de estudo de evento já
removia esse ruído corretamente.

### O resultado da troca

Refiz tudo com o alvo sendo o **retorno anormal** — quanto a ação andou *além
do que o mercado explicaria*. Os coeficientes do modelo de mercado foram
estimados **só no treino**, nunca no teste.

| Alvo | Média dos 8 braços | Braços positivos | Melhor |
|---|---|---|---|
| Retorno **bruto** | −0,84 pp | **0 de 8** | −0,42 pp |
| Retorno **anormal** | +0,32 pp | **5 de 8** | **+0,95 pp** |

**O sinal inverteu.** Pela primeira vez em todos os experimentos, os modelos
deixaram de ser *ativamente piores* que o palpite fixo. E, também pela
primeira vez, o melhor braço é **preço + sentimento** (+0,95) acima de só
preço (+0,64).

**Mas atenção, e isto é importante: ainda não é vitória.** O melhor braço tem
p = 0,203 e intervalo de confiança de [−0,40; +2,34] — o zero está dentro.
O que mudou foi o **sinal e a direção**, não a significância.

Os betas de mercado estimados saíram todos plausíveis, o que valida o
procedimento: PETR4 1,37 (agressiva), BPAC11 1,26, BBAS3 1,22, ITUB4 0,98,
VALE3 0,92, **ABEV3 0,67** (defensiva, como se espera de uma empresa de
bebidas).

## Uma correção que preciso fazer no meu próprio alerta

Na conversa anterior eu avisei que os intervalos de confiança agrupados
estavam otimistas em **2,3 vezes**, porque os papéis andam juntos. **Eu
errei.** Calculei pela correlação dos *retornos* (0,486), mas o que importa
para a inferência é a correlação do **acerto**, não a do retorno.

Medido do jeito certo (bootstrap em blocos de data, 2.000 reamostras):

| | |
|---|---|
| IC95% supondo independência | ±1,29 pontos |
| IC95% por bootstrap em blocos de data | ±1,35 pontos |
| **Inflação real** | **1,05×** |

Faz sentido: um modelo que acerta perto de 50% erra de forma quase
independente entre papéis, mesmo quando os retornos andam juntos. **Os
intervalos que reportei antes estavam substancialmente corretos.** O
bootstrap por data vira o padrão mesmo assim, porque é o método correto — e
agora está medido, não suposto.

## E a recomendação de ampliar para 56 papéis também estava errada

| Cenário | Empilhado | N efetivo | IC correto |
|---|---|---|---|
| 10 papéis, todos os dias | 5.790 | 1.077 | ±3,0% |
| **56 papéis**, todos os dias | 32.424 | **1.169** | **±2,9%** |

**Ampliar de 10 para 56 papéis move a margem de ±3,0 para ±2,9.** O fator de
mercado impõe um teto: o N efetivo satura em *número de dias ÷ correlação*, e
**só o horizonte move esse teto**. Mais papéis ajudam o modelo a *aprender*;
não ajudam a *medir*.

## O modelo de painel

Treinei também **um único modelo** com os 10 papéis empilhados e a identidade
do papel como atributo (inclinação comum, intercepto por papel). A previsão
continua individual: entram os atributos de um papel num dia, sai a resposta
daquele papel.

**Resultado equivalente a treinar um modelo por papel** — as diferenças ficam
dentro do intervalo de confiança. Mais dados correlacionados não acrescentam
informação proporcional.

## Uma divergência corrigida entre o código e a dissertação

Encontrei, ao verificar, que a dissertação e o código usavam **fórmulas
diferentes** para o índice de sentimento:

| | Fórmula | Efeito |
|---|---|---|
| **Dissertação (Cap. 3) e o ramo de notícias** | polaridade × confiança | documento neutro vira **exatamente zero** |
| **Ramo da CVM** (scripts 18 a 24) | p(positivo) − p(negativo) | documento neutro **conserva** a inclinação residual |

Isso importa porque **70% dos comunicados da Petrobras são classificados como
neutros** — sob a primeira fórmula, todos virariam zero.

**Como foi resolvido:** em vez de escolher uma no escuro, rodei **as duas como
variantes** (linhas A e B da tabela acima), e a Seção 3 da dissertação agora
documenta ambas, com a medição de que o desvio-padrão é parecido (0,319 contra
0,344). A diferença entre elas não altera nenhuma conclusão.

## O que entrou na dissertação

| Onde | O quê |
|---|---|
| **Cap. 3, nova subseção** | **A cadeia de componentes** — tabela de o que cada peça consome e entrega, e por que FinBERT, GARCH, SVM e XGBoost não são alternativas concorrentes |
| Cap. 3, nova subsubseção | As duas formas do índice de sentimento, com a medição |
| **Cap. 4, nova seção 4q** | A restrição aos pregões com divulgação — o experimento desta mentoria |

O validador do projeto passa: 112 entradas no bib, 102 rótulos, todas as
citações e referências cruzadas resolvem, **pronto para compilar**.

## Arquivos desta pasta

| Arquivo | O quê |
|---|---|
| `01_EXPLICACAO_SIMPLES.docx` | a explicação em linguagem comum, incluindo o que são p(positivo) e p(negativo) |
| `02_Dias_Com_Evento.xlsx` | as tabelas, por papel e agrupado |

Scripts: `CVM/25_dias_com_evento.py` (o experimento),
`docs/_gerar_secao_dias_evento_tex.py` (a seção 4q).
Dados: `CVM/dados/dias_com_evento.json`.
