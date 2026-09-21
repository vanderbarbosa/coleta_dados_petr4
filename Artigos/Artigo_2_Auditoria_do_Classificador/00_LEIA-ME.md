# Artigo 2 — Auditoria do classificador

**O que um classificador de sentimento financeiro em português não enxerga**

## Estado: material reunido, falta escrever

## A contribuição

Uma auditoria sistemática do FinBERT-PT-BR contra **referência externa
independente**: 224 notícias em que trinta casas de análise declararam
publicamente se o fato era favorável ou desfavorável à companhia.

## Os achados reunidos

- viés estrutural: 48,5% do corpus rotulado negativo; **zero pregões com maioria
  positiva em oito anos**
- contra o gabarito profissional: **21,9% contra 84,8%**; kappa de 0,075
- defeito de configuração que faz a biblioteca aplicar sigmoide em vez de softmax
- o modelo é *cased* e quebra com as 21.619 manchetes em caixa alta
- nove tentativas de melhoria, oito fracassaram
- em texto regulatório, 79,2% saem neutros

## O que falta

- [ ] **auditar à mão os 224 pareceres** — `dados/224_pareceres_PARA_AUDITAR.csv`
      tem duas colunas em branco para isso. Sem essa conferência, o número
      principal fica preliminar. Cerca de duas horas.
- [ ] escrever

## Cuidado editorial

O texto precisa ser escrito **sem tom de ataque** ao trabalho de Santos, Bianchi e
Costa (2023). O enquadramento correto é o de **estudo de limites de
aplicabilidade**: o modelo foi treinado para uma tarefa e está sendo cobrado por
outra.
