# Prophet — o que ele é, e o que fizemos com ele

**Para o Vanderlei explicar ao Prof. Julio, em poucas frases.**

## O que o Prophet é

O Prophet (criado pelo Facebook/Meta) **prevê números ao longo do tempo** —
venda de um produto mês a mês, visitas de um site dia a dia. Ele não lê
texto. Não tem como "classificar uma notícia como positiva ou negativa" —
isso é trabalho de um modelo de linguagem, como o FinBERT, que já usamos.

## O que fizemos, então

Usamos o Prophet como **mais um método de previsão**, ao lado do
GARCH+SVM/XGBoost que já tínhamos — não no lugar do FinBERT. O FinBERT
continua sendo quem lê e classifica os comunicados. O Prophet entra depois,
tentando prever **direção, volatilidade e preço** com base no histórico de
preço — e, numa segunda versão, usando também o sentimento que o FinBERT já
calculou como informação extra.

## Por que isso responde à pergunta do professor

Dá para comparar os dois métodos de forma justa: mesmo alvo, mesmo recorte
de teste, mesma régua de avaliação. Se o Prophet (mais simples de configurar,
mas nunca usado nesta pesquisa) chegar perto ou superar o GARCH+SVM/XGBoost
(mais elaborado, já validado em toda a dissertação), isso é informação real
sobre se vale a pena manter a complexidade que já temos.

## O resultado, resumido

Ver `00_LEIA-ME.md` e `02_Prophet_vs_GARCH_SVM_XGBoost.xlsx`, nesta mesma
pasta, para os números completos nas 10 ações.
