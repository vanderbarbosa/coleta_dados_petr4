# Avaliação crítica da análise do NotebookLM

**Data:** 17/08/2026 · **Origem:** conversa do Vanderlei com o NotebookLM sobre o PDF da dissertação
e as fontes citantes do FinBERT-PT-BR

---

## Veredito em uma linha

O levantamento **encontrou duas fontes citantes que nós não tínhamos** e apontou uma aplicação do
FinBERT-PT-BR que não havíamos catalogado. Mas trabalhou sobre um **PDF desatualizado**, e por isso
recomenda coisas que já testamos e rejeitamos, além de conter **dois erros factuais verificáveis**.

---

## 1. O problema de fundo: o PDF é anterior à revisão

Boa parte das recomendações não é descoberta externa — é a **própria dissertação sendo lida de
volta**, e numa versão antiga. Casos concretos:

| O que o NotebookLM recomenda | Situação real |
|---|---|
| ``Aumentar o conjunto-ouro para 500–1000 e ajustar o BERTimbau-large, que superará o FinBERT-PT-BR'' | **Era uma frase da dissertação que nós removemos.** O experimento G3 depois mostrou que ajustar degrada o desempenho ($p = 0{,}022$). A recomendação foi retirada do texto justamente por contradizer o resultado. |
| ``Rótulo com zona morta'' | Já está na Seção 4.e como **proposta não testada**. É o nosso próprio item (ii) de trabalhos futuros. |
| ``Filtro de relevância por menção direta'' | Já está na Seção 4.e, e foi **superado** pela Seção 4.k, que mede o filtro por categoria com resultado significativo ($p = 0{,}001$). |
| ``Regressão quantílica com pesos variáveis, $+10{,}9\%$ de $R^2$'' | Já está implementada e reportada. |
| ``Manter a parcimônia, configuração E0'' | Já é a conclusão da suíte de refinamento. |
| ``Regra Lead-Lag das 17h'' | Já implementada desde a coleta. |
| ``ISM ponderado por confiança'' | Já implementado — e agora **revisado**, ver seção 3 adiante. |
| *Baseline* de $50{,}9\%$ | Corrigido para $50{,}1\%$ na revisão. O PDF traz o número antigo. |

**Consequência prática:** se levar essa lista ao Prof. Emerson como ``descobertas'', ele verá
recomendações que já constam do seu próprio texto. Convém apresentar apenas o que é efetivamente
novo — que existe, e está na seção 4 deste documento.

---

## 2. Erro factual 1: o corpus do Santos é de 1,4 milhão, não 1,6

O NotebookLM afirma ``1,6 milhão de sentenças'', citando uma monografia da UNIRIO --- fonte
secundária.

**Verificação na fonte primária.** O cartão do modelo em
`huggingface.co/lucas-leme/FinBERT-PT-BR` declara: *``trained with more than 1.4 million texts of
financial news in Portuguese''*, e *``a sentiment classifier with few labeled texts (500)''*.

A dissertação já usa **1,4 milhão de textos**, que é o número correto. Não alterar.

---

## 3. Erro factual 2: o escore NÃO é softmax — e isso foi provado aritmeticamente

Este é o erro mais importante, porque o NotebookLM o afirma com ênfase ao se corrigir:

> *``r['score'] corresponde exatamente à probabilidade normalizada via Softmax na última camada''*

**Isso é falso, e a prova dispensa qualquer suposição.** Numa distribuição *softmax* sobre três
classes, a probabilidade da classe vencedora não pode ficar abaixo de $1/3$ — as três somam 1, e a
maior é no mínimo a média.

| Medida no nosso corpus | Valor |
|---|---|
| Escore mínimo observado | **0,2845** |
| Escore máximo observado | 0,8729 |
| Piso matemático do *softmax* | 0,3333 |
| **Escores abaixo do piso** | **397** |

A causa está documentada na Seção 4.j: o `problem_type: multi_label_classification` declarado na
configuração publicada faz a biblioteca aplicar **sigmoide**. Os rótulos não são afetados; a escala
do escore, sim.

---

## 4. O que o levantamento trouxe de genuinamente valioso

Três coisas, e vale a pena aproveitá-las.

### 4.1 Duas fontes citantes que não tínhamos — ambas verificadas

**Pinheiro, Muinhos e Fernandes — *The role of fiscal sentiment in Brazil's yield curve***
Constroem o Índice de Sentimento Fiscal (FSI-BR) de alta frequência a partir de jornais e do
Broadcast da Agência Estado, 2008–2022. Extraem sentimento no nível da **sentença** com o
FinBERT-PT-BR e remapeiam para $\{-1, 0, +1\}$. Avaliam o efeito sobre a estrutura a termo da curva
de juros. *Existência confirmada; PDF localizado.*

**Costa Neto e Anjos — informatividade de notas explicativas (USP/FIPECAFI)**
25.804 notas explicativas trimestrais de 1.152 empresas na CVM, 2011–2023. Pontuam os relatórios em
três dimensões: *Boilerplateness*, *Completeness* e *Density*. *Existência confirmada; as três
dimensões conferem.*

### 4.2 Uma aplicação que não havíamos catalogado: embeddings + agrupamento

Este é o achado mais interessante do levantamento, e passou despercebido no meio do resto.

**Os dois trabalhos acima usam o FinBERT-PT-BR como extrator de *embeddings*, e não como
classificador de sentimento**, aplicando K-means (ou K-means++) sobre os vetores para construir
tópicos ou dicionários endógenos.

Por que isso importa para nós: todos os nossos problemas com o artefato estão concentrados na
**cabeça de sentimento** — o viés de negatividade de 87%, o teto de 0,58, a escala sigmoide, os
zero pregões de maioria positiva. **Nada disso afeta os *embeddings***, que vêm da parte do modelo
efetivamente adaptada ao domínio financeiro e que é a de maior qualidade.

É uma linha experimental nova, barata e que contorna --- em vez de tentar consertar --- o componente
que resistiu a nove intervenções.

### 4.3 A configuração CNN + LSTM, se a banca pedir comparação

Da monografia da UNIRIO: convolução unidimensional com 200 filtros e janela 2 (bigramas), ReLU;
*max pooling*; *dropout* de 25%; LSTM de 100 unidades com *tanh*; *dropout* final de 50%; *softmax*.
Não é prioridade, mas é uma linha de base concreta caso solicitada.

---

## 5. O reexame que esta conversa provocou — e a correção que ele exigiu

O NotebookLM insistiu que a ponderação por confiança carrega o sinal preditivo, citando a nossa
própria Tabela de $54{,}93\%$ contra $50{,}30\%$. Como se descobriu que o escore está na escala
errada, a questão tornou-se decisiva: se a ponderação carrega o ganho, corrigir a escala é urgente.

Testou-se (`src/sentimento/testar_ponderacao_confianca.py`), sobre o **mesmo recorte** da medição
original --- notícias posteriores ao fechamento, 1.906 pregões:

| Construção | $\lvert r\rvert$ volatilidade | Acur. validação | Acur. teste |
|---|---|---|---|
| Ponderada pela confiança | 0,0513 | **56,64%** | **50,31%** |
| **Polaridade pura** | 0,0503 | 53,85% | **53,88%** |
| Só alta confiança | 0,0436 | 53,50% | 53,04% |
| Saldo de votos | 0,0503 | 53,85% | 53,88% |

**Três achados, e os três contrariam a leitura original:**

1. **A ponderação PIORA a acurácia de teste** — $-3{,}57$ pontos percentuais no recorte original,
   $-1{,}41$ no corpus integral. Sentido oposto ao reportado.
2. **A variante ponderada tem a MAIOR validação e a MENOR teste** (56,64% contra 50,31%). Diferença
   de mais de seis pontos: assinatura clássica de seleção sobre a validação. É explicação plausível
   para a cifra de 54,93%.
3. **Polaridade pura e saldo de votos dão resultados idênticos** — e têm de dar, porque a média de
   $\{+1,0,-1\}$ é algebricamente igual a $(n_{pos}-n_{neg})/n_{total}$. **São a mesma quantidade.**
   A tabela original atribuía-lhes 54,53% e 50,30%, o que não pode ocorrer sob a definição
   declarada. O código daquela suíte não foi preservado, de modo que a origem da discrepância não
   pôde ser reconstituída.

Sobre a volatilidade, a ponderação acrescenta $+0{,}0084$ no corpus integral ($p = 0{,}021$) —
real, mas modesto: $6\%$ de acréscimo, contra os $23\%$ do filtro de relevância. A razão é
aritmética: as séries ponderada e pura correlacionam-se a **0,9903**.

**Corolário favorável:** como a ponderação quase não redistribui, **a escala sigmoide equivocada tem
efeito prático desprezível**. Recalcular o índice com *softmax* — que exigiria nova inferência sobre
205.697 notícias em GPU — mudaria uma ponderação cujo efeito já é marginal. O item deixa de ser
prioridade.

**A dissertação foi corrigida:** nova Seção 4.n, e a leitura original da Seção 4 foi substituída por
remissão à revisão.

---

## 6. Onde o NotebookLM acertou

Por justiça, três pontos corretos e úteis:

- **A autocrítica sobre o softmax foi bem-vinda** — ele reconheceu o erro quando corrigido, ainda
  que a correção estivesse tecnicamente errada.
- **A distinção entre as fontes que analisam notícias e as que analisam outros textos** é
  organizacionalmente útil e vale para o capítulo de trabalhos correlatos.
- **A afirmação de que nenhuma das fontes faz o que fazemos** procede para a literatura em
  português. Registre-se, porém, que **em inglês há dois trabalhos com desenho equivalente** —
  Halousková e Lyócsa (2025) e Mino e Williamson (2025), ambos documentados em
  `orientacoes/encoders_ingles/`. A originalidade deve ser reivindicada com esse cuidado, sob pena
  de a banca apresentar o contraexemplo.

---

## 7. Como usar isto na próxima orientação

**O que levar:**
1. As duas fontes citantes novas, com a aplicação de *embeddings* + K-means.
2. A proposta de usar o FinBERT-PT-BR como extrator de *embeddings*, contornando a cabeça de
   sentimento.
3. A revisão da ponderação por confiança, como exemplo de autocorreção metodológica.

**O que não levar:** a lista de ``recomendações'' que já constam da dissertação.

**Sobre a ferramenta:** o NotebookLM lê bem e organiza bem, mas não verifica aritmética nem
distingue o que é conclusão da fonte do que é proposta de trabalho futuro. Convém tratá-lo como um
bom resumidor, e conferir todo número antes de citar. Vale reenviar o PDF atualizado antes de
qualquer nova consulta.
