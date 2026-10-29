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
