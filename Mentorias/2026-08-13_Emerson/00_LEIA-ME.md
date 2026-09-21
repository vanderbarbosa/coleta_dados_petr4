# Mentoria de 13 de agosto de 2026 — Prof. Emerson

## O que foi pedido

Procurar **outras pesquisas que façam o mesmo que a nossa** — ler notícias e
prever direção e volatilidade —, independentemente do ativo e do idioma. E dizer
se dá para usar ou adaptar algo delas.

## O que foi feito, em linguagem simples

Levantamos **25 pesquisas** e lemos cada uma. Depois fomos conferir os números que
elas anunciam, porque alguns pareciam bons demais.

**E três não resistiram ao exame:**

- Um trabalho muito citado anuncia 86,7% de acerto. São **13 acertos em 15 dias**,
  e a análise **foi refutada** em 2017.
- Outro anuncia 71,2%, mas mede o preço **vinte minutos depois** da notícia, não
  no dia seguinte. E 71,2% é o melhor de seis recortes; no recorte por ação
  individual, cai para 56,9%.
- Um terceiro anuncia 0,955 de "acurácia", mas prevê o **preço em reais**, não a
  direção. Prever o preço de amanhã é fácil: basta responder "o mesmo de hoje".

**Mas três nos superam de verdade**, e isso também foi registrado. O principal
deles usa 404 ações e dados de 5 em 5 minutos, contra a nossa uma ação e dado
diário. **É falta de dado, não ausência de sinal.**

## O achado que mudou o rumo da pesquisa

Uma das pesquisas (Hashami e Maldonado, sobre petróleo) testou o **mesmo modelo**
de duas formas:

| Como usaram o modelo | Acerto |
|---|---|
| como classificador de sentimento | **0,5368** — o pior da tabela |
| como extrator de *embeddings* | **0,6694** — vence a referência |

Treze pontos de diferença, no mesmo modelo. **Todos os defeitos que auditamos no
nosso classificador estão na parte que rende 0,5368.**

## O que está nesta pasta

Os documentos comparativos, o glossário de termos, as fichas de leitura das 25
pesquisas e **15 PDFs** das que têm acesso aberto.
