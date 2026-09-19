# Pedido de acesso ao FinBERTimbau (UFPR)

## Como enviar — duas vias, nesta ordem

**1ª via, e é a preferencial: o próprio Zenodo.**
Entre em https://zenodo.org/records/18463339 **logado** numa conta Zenodo (criar
é gratuito, leva um minuto). Registros com arquivo restrito mostram o botão
*Request access* só depois do login. É o canal que os próprios autores
configuraram, vai direto para eles e fica registrado na plataforma.

**2ª via: e-mail**, se o botão não aparecer ou não houver resposta em uma semana.

| Destinatário | Endereço | Situação |
|---|---|---|
| Prof. Adalto Acir Althaus Junior | `adalto.althaus@ufpr.br` | **não consegui confirmar na fonte oficial** — apareceu em busca, não na página da UFPR |
| CEPPAD/UFPR (centro dele) | `ceppad@ufpr.br` | **confirmado** na página institucional |

Sugestão: mandar para os dois, com o endereço pessoal em *Para* e o do centro em
*Cópia*. Se o pessoal estiver errado, o do centro encaminha.

O primeiro autor é **Luiz Felipe Meier** (ORCID 0009-0004-2794-9539), provável
mestrando ou doutorando — vale citá-lo pelo nome no corpo do e-mail.

---

## Assunto

```
Solicitação de acesso ao FinBERTimbau (Zenodo 10.5281/zenodo.18463339) — pesquisa de mestrado PUCPR
```

---

## Corpo do e-mail

```
Prezado Prof. Adalto Althaus Junior,
Prezado Luiz Felipe Meier,

Escrevo-lhes a respeito do conjunto FinBERTimbau: Curated Brazilian Portuguese
Financial Text Corpus and Sentiment Annotation Data, depositado no Zenodo sob o
DOI 10.5281/zenodo.18463339. O registro indica que o acesso aos arquivos pode ser
concedido mediante solicitação para fins acadêmicos, e é nesse sentido que os
procuro.

Sou aluno do Programa de Pós-Graduação em Informática da PUCPR, sob orientação do
Prof. Dr. Julio Cesar Nievola, e desenvolvo dissertação sobre o impacto do
sentimento de notícias financeiras na previsão de direção e volatilidade de ativos
da B3. O trabalho está em fase de validação e emprega o FinBERT-PT-BR (Santos,
Bianchi e Costa, 2023) sobre dois corpora: cerca de 205 mil manchetes de portais
brasileiros e, mais recentemente, 20.419 comunicados obtidos dos dados abertos da
CVM, cada um com data e hora oficiais de entrega extraídas do Protocolo de Entrega.

O interesse pelo trabalho dos senhores tem dois motivos concretos.

O primeiro é que o FinBERTimbau incorpora documentos da CVM na sua composição —
exatamente o tipo de texto que passei a utilizar. A linguagem do comunicado
societário difere bastante da manchete de portal, e tenho observado que o
classificador treinado majoritariamente em notícia se comporta de modo distinto
nesse registro: dos 20.419 comunicados que classifiquei, 79,2% foram rotulados
como neutros.

O segundo é metodológico. Toda a avaliação da minha dissertação depende hoje de um
único artefato, o próprio FinBERT-PT-BR, o que me deixa sem referência externa para
julgá-lo. Uma auditoria que conduzi indica viés contra a classe positiva: em 224
notícias nas quais casas de análise declararam publicamente parecer favorável à
Petrobras, o modelo identificou apenas 21,9% como positivas. Dispor de um conjunto
anotado de forma independente, com validação humana sob critério de consenso como
os senhores descrevem, permitiria distinguir o que é limitação do artefato do que é
limitação da tarefa.

O uso pretendido é estritamente acadêmico e não comercial, restrito à dissertação e
a eventual publicação dela derivada, com a citação devida ao depósito e à licença
CC-BY-4.0. Comprometo-me a não redistribuir os arquivos e a observar as restrições
de direito autoral que os senhores mencionam quanto à porção de notícias.

Em contrapartida, coloco à disposição o que produzi e que possa lhes ser útil: o
corpus de 20.419 comunicados da CVM já classificados, com data e hora oficiais de
entrega — que, ao que pude verificar, não consta do conjunto aberto da autarquia —,
além dos embeddings extraídos e do código de coleta. Fico igualmente à disposição
para conversar sobre os achados, caso haja interesse.

Agradeço desde já a atenção e coloco-me à disposição para prestar qualquer
esclarecimento ou formalizar o pedido pela via que os senhores preferirem.

Atenciosamente,

Vanderlei Barbosa da Silva
Mestrando em Informática — PPGIa/PUCPR
Orientador: Prof. Dr. Julio Cesar Nievola
vander.barbosa@gmail.com
```

---

## Por que o e-mail está escrito assim

**Diz o que se pede e sob qual condição, logo no primeiro parágrafo.** Quem recebe
precisa saber em cinco segundos do que se trata.

**Dá dois motivos concretos, não genéricos.** "Seria útil para minha pesquisa" não
convence ninguém. "O conjunto de vocês tem documentos da CVM, que é o que passei a
usar" convence.

**Mostra que o trabalho já existe e tem substância.** Os números — 205 mil
manchetes, 20.419 comunicados, os 79,2% de neutros, os 21,9% contra 84,8% — provam
que não é pedido de quem está começando do zero.

**Oferece reciprocidade real.** O corpus da CVM com hora oficial é algo que eles
não têm, porque a CVM não publica a hora no conjunto aberto. Isso muda a natureza
do pedido: deixa de ser favor e vira troca.

**Não promete o que não se pode cumprir.** Nada de coautoria ou parceria — só
acesso, citação e disponibilidade para conversar.
