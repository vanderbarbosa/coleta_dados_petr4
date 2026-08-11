# Contato com Lucas Leme Santos — rascunhos

**Objetivo:** obter o código de treinamento do FinBERT-PT-BR, o guia de anotação e o
*checkpoint* do modelo de linguagem puro.

**Destinatário:** `lucaslssantos99@gmail.com` — ✅ **funciona** (o `@usp.br` do artigo está morto).
Perfil público no LinkedIn e no GitHub (`lucas-leme`).

## Histórico

| Data | Evento |
|---|---|
| 08/08/2026 | E-mail enviado ao `@usp.br` — **voltou**, endereço inexistente |
| 08/08/2026 | Reenviado ao `@gmail.com` |
| 08/08/2026, 15:50 | **Respondeu em ~42 min.** Cordial, parabenizou a iniciativa e apontou o dataset no Hugging Face |

**Leitura da resposta.** Curta e rápida — ele está disposto a engajar, mas claramente
**passou o olho**. Respondeu ao item que já tínhamos resolvido sozinhos (o dataset) e
**não tocou nos outros três**: código de treinamento, guia de anotação e o *checkpoint* do
modelo de linguagem puro.

Não é recusa; é e-mail lido às pressas. **A resposta certa é um retorno curto**, com
perguntas que ele possa responder em uma linha cada. Ver a Versão 4, abaixo.

---

## Versão 1 — e-mail (principal)

**Assunto:** `FinBERT-PT-BR aplicado à PETR4 — validação independente e uma solicitação`

---

Prezado Lucas, bom dia.

Meu nome é Vanderlei Barbosa da Silva e sou mestrando em Informática na PUCPR, sob orientação
do Prof. Dr. Julio Cesar Nievola. Escrevo porque o FinBERT-PT-BR é o modelo central da minha
dissertação, e gostaria de compartilhar alguns resultados com você antes de fazer um pedido.

Minha pesquisa investiga o impacto do sentimento de notícias financeiras na previsão de direção
e de volatilidade da PETR4. Apliquei o FinBERT-PT-BR a um corpus de aproximadamente 205 mil
notícias de cinco portais, no período de 2018 a 2026, e construí um índice de sentimento nos
moldes do que você propõe no artigo do BWAIF.

Para validar essa aplicação, montei um conjunto-ouro de 300 manchetes anotadas manualmente e
medi o desempenho do modelo nesse recorte. Dois resultados podem lhe interessar:

- Em manchetes referentes a **um ativo específico**, a acurácia ficou em **0,58** (κ de Cohen
  0,371), contra os 0,76 relatados no artigo para notícias gerais de mercado. Interpreto isso
  como um efeito de transferência de domínio — de sentenças de notícia geral para manchetes de
  uma única empresa —, e não como um problema do modelo.
- A matriz de confusão sugere um viés sistemático em direção à classe negativa no meu recorte:
  cerca de um terço das manchetes que anotei como neutras foram classificadas como negativas.
  Corrigindo as proporções agregadas por inversão da matriz de confusão, o índice de sentimento
  do período sai de −0,345 para −0,044.

Faço questão de registrar que essas medidas dizem respeito ao meu domínio específico e ao meu
gabarito, que tem limitações que reconheço — anotador único, sem métrica de concordância. Não
são, de forma alguma, uma avaliação do modelo nas condições em que ele foi proposto e validado.

Chego então ao pedido. Procurei em seu GitHub, na organização Turing USP e no repositório do
Hugging Face, e não localizei o código de treinamento nem os dados. Seria possível compartilhar,
integralmente ou em parte:

1. **O código de treinamento** — em especial a etapa de adaptação de domínio por *masked
   language modeling* e a implementação do *gradual unfreezing*. Pretendo replicar essa receita
   sobre um corpus setorial, e um ponto de partida fiel evitaria que eu introduzisse diferenças
   involuntárias.
2. **A base de 503 textos rotulados.** Se houver restrição de direitos autorais sobre o texto
   das notícias, os **rótulos acompanhados de identificadores** (URL, *hash* ou data e veículo)
   já seriam de grande valia — eu recuperaria os textos por conta própria.
3. **O guia de anotação** usado pelos três anotadores. Estou reestruturando meu protocolo de
   rotulagem e a rubrica que vocês adotaram é a referência que pretendo seguir.
4. **O modelo de linguagem FinBERT-PT-BR "puro"**, anterior ao ajuste de sentimento, caso o
   *checkpoint* ainda exista. O que está publicado no Hugging Face é o classificador
   (`BertForSequenceClassification`), e partir dele para uma nova etapa de MLM é possível, mas
   menos limpo do ponto de vista metodológico.

Entendo perfeitamente se algum desses itens não puder ser compartilhado. Qualquer um deles,
isoladamente, já ajudaria bastante.

Em contrapartida, coloco-me à disposição para compartilhar o conjunto-ouro anotado, os
resultados da validação e os detalhes da correção de viés, se forem de interesse. O trabalho
citará o artigo do BWAIF e a monografia, e terei satisfação em lhe enviar a versão final.

Agradeço desde já a atenção e parabenizo pelo trabalho — o FinBERT-PT-BR é hoje o principal
recurso aberto para análise de sentimento financeiro em português, e isso se reflete nos mais de
170 mil *downloads* mensais do repositório.

Atenciosamente,

**Vanderlei Barbosa da Silva**
Mestrando em Informática — PPGIa/PUCPR
Orientador: Prof. Dr. Julio Cesar Nievola
vander.barbosa@gmail.com

---

## Versão 2 — LinkedIn / mensagem curta

Use se o e-mail institucional voltar, ou como primeiro contato mais leve.

---

Olá, Lucas, tudo bem?

Sou mestrando em Informática na PUCPR e uso o FinBERT-PT-BR como modelo central da minha
dissertação, sobre sentimento de notícias e volatilidade da PETR4. Já apliquei o modelo a cerca
de 205 mil notícias e montei um conjunto-ouro de 300 manchetes anotadas para validá-lo.

Não encontrei publicados o código de treinamento nem a base de 503 textos rotulados. Seria
possível compartilhar algum deles? Interessa-me especialmente a etapa de adaptação de domínio
(MLM) e o *gradual unfreezing*, que pretendo replicar sobre um corpus setorial.

Em troca, posso compartilhar os resultados da validação — inclusive uma medição de queda de
desempenho por transferência de domínio (0,76 → 0,58 em manchetes de um ativo específico) que
talvez lhe interesse.

Se preferir, envio os detalhes por e-mail. Obrigado desde já!

Vanderlei Barbosa da Silva — PPGIa/PUCPR

---

## Versão 3 — reenvio, caso não haja resposta em ~2 semanas

**Assunto:** `Re: FinBERT-PT-BR aplicado à PETR4 — validação independente e uma solicitação`

---

Prezado Lucas, bom dia.

Retomo brevemente a mensagem abaixo, enviada em [DATA], caso tenha se perdido na caixa de
entrada.

Se o código de treinamento não estiver mais disponível ou não puder ser compartilhado, uma
resposta em uma linha já me ajuda: eu registro na dissertação que a replicação exata não foi
possível e sigo com a implementação própria do protocolo descrito no artigo, o que é o caminho
que estou tomando por ora.

De todo modo, agradeço a atenção.

Atenciosamente,
Vanderlei Barbosa da Silva — PPGIa/PUCPR

---

## Versão 4 — resposta ao retorno dele *(usar esta agora)*

**Assunto:** manter o mesmo (responder na própria conversa, com `Re:`)

---

Lucas, muito obrigado pelo retorno rápido — e pela boa notícia.

Cheguei ao dataset no Hugging Face pouco antes da sua resposta e ele já está em uso. Os
503 textos são exatamente o que faltava para eu treinar a etapa de sentimento com base
decente, então foi de grande ajuda.

Se puder, três perguntas rápidas — pode responder em uma linha cada, ou simplesmente
ignorar as que não fizerem sentido:

1. **O código de treinamento ainda existe em algum lugar?** Mesmo desorganizado, em
   *notebook* solto do Kaggle, já me serviria. Interessa sobretudo a etapa de MLM e a
   implementação do *gradual unfreezing*.
2. **Houve um guia de anotação mais longo** do que a instrução de uma linha que está no
   README — com exemplos resolvidos, casos de fronteira, algo assim? Estou reestruturando
   meu protocolo de rotulagem e queria seguir o mais próximo possível do seu.
3. **Você ainda tem o *checkpoint* do FinBERT-PT-BR "puro"**, antes da cabeça de
   sentimento? O que está publicado é o `BertForSequenceClassification`; para continuar o
   pré-treinamento num corpus setorial, partir do modelo de linguagem seria mais limpo.

Em troca, duas coisas que talvez lhe interessem, já medidas:

- Em manchetes de **um ativo específico** (PETR4, ~205 mil notícias, 2018–2026), a acurácia
  contra gabarito humano fica em **0,58**, contra os 0,76 do artigo. Interpreto como
  transferência de domínio — de sentença de notícia geral para manchete de uma empresa.
- Uma das fontes do meu corpus publica manchetes **em caixa alta**. Como o modelo é *cased*,
  a cobertura do vocabulário cai de ~78% para ~22% e ele passa a classificar 84% desses
  textos como neutros. Normalizar a caixa resolve. **Pode valer uma nota no *model card*** —
  imagino que outros usuários esbarrem nisso sem perceber.

Posso lhe mandar os números completos quando fechar, se quiser.

Abraço e obrigado mais uma vez,
Vanderlei

---

## Observações sobre a estratégia

**Por que abrir com os resultados, e não com o pedido.** Um pedido isolado dá trabalho e não
oferece nada. Um pedido acompanhado de uma validação independente do trabalho dele muda a
natureza da mensagem: passa a ser troca entre pesquisadores. E a informação é genuinamente
relevante para ele — ninguém, entre os sete trabalhos que citam o artigo, mediu o desempenho do
modelo contra gabarito humano.

**Por que o item 2 tem uma alternativa embutida.** Os 503 textos vêm de Valor Econômico, Exame e
InfoMoney. É bem possível que ele não possa redistribuir o conteúdo. Oferecer a saída de
"rótulos + identificadores" remove o principal motivo de recusa e aumenta muito a chance de
resposta parcial.

**Por que o item 4 é o de maior chance de sucesso.** Subir um *checkpoint* que já existe no
disco custa alguns minutos e não envolve direitos de terceiros. É o pedido mais fácil de
atender — e resolveria a objeção metodológica de partirmos do classificador em vez do modelo de
linguagem puro.

**Sobre o parágrafo de ressalva.** É o parágrafo mais importante do e-mail. Apresentar 0,58
contra 0,76 sem qualificar soaria como crítica ao trabalho dele, e a conversa morreria ali.
Deixar explícito que a limitação é do nosso gabarito e do nosso recorte mantém o tom de
colaboração — e é, além disso, o que de fato acreditamos.

**O que não fazer:** não anexar arquivos no primeiro contato, não pedir reunião de imediato, e
não mencionar prazos da dissertação. Nada disso ajuda, e tudo aumenta o custo percebido de
responder.

### Sobre a Versão 4, especificamente

**Por que ela é curta.** Ele respondeu em 42 minutos com três linhas. Esse é o registro da
conversa — um retorno longo seria lido na diagonal, como foi o primeiro. Cada pergunta foi
escrita para caber numa linha de resposta.

**Por que dizer que já tínhamos achado o dataset.** Fingir que a indicação dele resolveu algo
seria falso, e ele perceberia ao ver que já havíamos analisado os 503. Reconhecer que
chegamos lá sozinhos, sem diminuir a ajuda dele, é mais honesto e mais eficaz.

**Por que baixar a barra no pedido nº 1.** *"Mesmo desorganizado, em notebook solto"* remove o
principal motivo de não responder — o constrangimento de compartilhar código bagunçado de um
TCC de quatro anos atrás.

**Por que o achado da caixa alta entra.** É a única coisa que temos que é genuinamente útil
**para ele**: afeta qualquer pessoa que use o modelo em corpus com manchetes maiúsculas, e a
sugestão de nota no *model card* é uma contribuição concreta ao trabalho dele. É reciprocidade
real, não cortesia.

**O que não incluir:** a correção ACC do índice e o teste do teto. São achados nossos, ainda não
consolidados, e alongariam o e-mail sem aumentar a chance de resposta. Ficam para depois, se a
conversa continuar.
