---
name: encoders-ingles-levantamento
description: "Levantamento dos FinBERT em inglês (mentoria Emerson 13/08/2026): o nosso 0,58 é NORMAL — o FinBERT inglês dá 0,555 na mesma situação"
metadata: 
  node_type: memory
  type: project
  originSessionId: 08181b53-ca1d-41ae-a256-cc9d79527860
  modified: 2026-08-13T20:08:24.455Z
---

Feito em 13/08/2026, atendendo às 3 tarefas do Prof. Emerson: buscar um BERT financeiro em inglês, buscar quem o cita, listar as aplicações. Orientação explícita: **não focar em um ativo, abrir o leque**.

Fichas completas em `orientacoes/encoders_ingles/` (00_INDICE + 8 documentos). Docx para leigos: `EXPLICACAO_SIMPLES_ENCODERS_INGLES.docx`. Seção 4.m da dissertação.

## O ACHADO PRINCIPAL — o 0,58 é normal
| Modelo | Condição | F1-macro |
|---|---|---|
| FinBERT inglês | manchetes setoriais, zero-shot | **0,555** |
| **FinBERT-PT-BR (nosso)** | manchetes PETR4, zero-shot | **0,579** |
| FinBERT inglês | ajustado c/ 1.500 manchetes | 0,707 |

**O nosso é LIGEIRAMENTE MELHOR.** O teto de 0,58 não é problema do português, nem do FinBERT-PT-BR, nem de arquitetura — é o comportamento esperado de qualquer encoder financeiro em subdomínio sem supervisão. Fonte: *Electronics* v.14 n.23 art.4680 (2025) — ⚠️ **autoria não recuperada, confirmar no MDPI antes de citar**.

Corolário: o G3 não fracassou porque adaptar não funciona — fracassou porque **352 exemplos não bastam** (eles usaram 1.500). Somar a hipótese de Shah et al. (2022): mascaramento aleatório é subótimo; o preferencial (termos do domínio) seria o correto.

## Existem DOIS FinBERT em inglês
- **Araci (2019)** — dissertação de mestrado, Amsterdã, `ProsusAI/finbert`, **4.459.091 downloads/mês**, 778 citações (Semantic Scholar). Base `uncased` → **imune ao nosso bug de caixa alta**.
- **Yang/Uy/Huang (2020)** → **Huang, Wang, Yang (2023)** na *Contemporary Accounting Research*. **4,9 bilhões de tokens**. `yiyanghkust/finbert-tone`, 704.839 downloads/mês, ajustado c/ 10.000 sentenças. Família: `-tone`, `-esg`, `-fls`, `-pretrain`.

## Dois trabalhos com o NOSSO desenho
**Halousková & Lyócsa (2025)** arXiv:2503.19767 — FinBERT + HAR, 404 ações S&P500, variância realizada 5min, 2010–2021. **Superam o HAR em 98,76% dos casos** (−12,74% EQM). E **o maior ganho, 14,99%, é nos dias de variação EXTREMA** → **confirma nosso efeito de cauda de forma independente**.
Por que eles superam e nós não: (1) 404 ativos vs 1; (2) variância intradiária vs Parkinson diário; (3) subconjuntos completos/LASSO adaptativo vs MQO; (4) + Google Trends/Twitter. **Conclusão honesta: nosso negativo é compatível com falta de PODER, não com ausência de sinal.**

**Mino & Williamson (2025)** arXiv:2510.16503 — BERT + GARCH(1,1)-t, S&P500. Coeficiente **−0,2275 (p=0,0016)** vs nosso **−0,2924 (p=0,0002)**. Quase idêntico → nossa medida não é artefato do Brasil/português.
⚠️ **Eles PARAM onde nós continuamos:** só ajuste dentro da amostra, sem out-of-sample, sem estratificar regime (declaram como limitação), 105 observações vs nossos 1.988. **Se tivéssemos parado ali, teríamos relatado sucesso e estaríamos errados.** Isso é contribuição metodológica nossa.

## Financial PhraseBank (Malo et al. 2014) — responde ao Emerson
16 anotadores **com formação em finanças** (3 pesquisadores + **13 mestrandos**), **5 a 8 anotações por sentença**, 4 subconjuntos por concordância. **Só 46,7% (2.264/4.846) tiveram acordo unânime.**
- Emerson estava certo sobre especialistas — mas a barra é "mestrandos em finanças", alcançável na PUCPR
- **O gargalo real não é formação, é REDUNDÂNCIA**: 5–8 rótulos vs nosso 1
- Proposta: reanotar as MESMAS 300 com 3 anotadores (não rotular 900 novas)
- ⚠️ Ressalva obrigatória: teste de teto → classificador perfeito rende só +1,2pp na direção. **Rotular melhor NÃO melhora previsão**; serve para saber se o 0,58 é culpa do modelo ou do anotador.

## 9 famílias de aplicação (pedido 3)
Sentimento · **volatilidade** · preço/direção · **declarações prospectivas** · ESG · carteira · bancos centrais · outros mercados (BondBERT, cripto, BioFinBERT, setorial) · explicabilidade.

**A melhor ideia do levantamento:** `finbert-fls` separa notícia que relata PASSADO de notícia que projeta FUTURO. Nossa Seção 4.l mostrou que o sinal colapsa de P0 para P1 porque é jornalismo narrando o ocorrido. **Filtrar por prospectividade deveria concentrar o sinal** — e segue a lição de [[filtro-relevancia-primeiro-ganho]] (mexer no corpus funciona, no modelo não). Dá para fazer em PT-BR por regras (futuro do presente, "deve", "prevê", "projeta", "espera-se").

⚠️ **Armadilha dos 95%:** artigos FinBERT-LSTM anunciam "acurácia 0,955" — mas reportam MAE e MAPE, que são métricas de REGRESSÃO. O alvo é o NÍVEL do preço (trivial, autocorrelação ~1), não a direção. 0,955 ≈ 1 − MAPE(0,045). **Não é comparável aos nossos 52,3%.** Inferência forte, mas não verificada no texto integral (PDF ilegível, ACM 403).

## 5 achados nossos confirmados externamente
efeito de cauda · coeficiente ≈−0,29 · erro concentrado no Neutro · LLM perde para encoder (FinBERT 83% > todos os LLMs em ESG 10-K) · degradação por transferência de domínio.

**How to apply:** prioridade = (1) escrever as validações externas [feito na 4.m]; (2) testar filtro de prospectividade; (3) replicar para 5–10 ativos da B3 (atende ao Emerson + ataca a falta de poder + testa a predição de que o efeito de cauda cresce com a volatilidade do ativo).

Ver [[efeito-de-cauda-auditoria-noticia]], [[filtro-relevancia-primeiro-ganho]], [[g3-adaptacao-esquecimento]], [[encoders-sentimento-ptbr]] e [[conjunto-ouro-quatro-rotulos]].
