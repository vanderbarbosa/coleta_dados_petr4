# Encoders financeiros em inglês — levantamento, citações e aplicações

**Mestrando:** Vanderlei Barbosa da Silva · **Orientador:** Prof. Dr. Julio Cesar Nievola (PUCPR/PPGIa)
**Co-orientador:** Prof. Dr. Emerson Cabrera Paraiso
**Elaborado em:** 13/08/2026 · **Origem:** mentoria de 13/08/2026 com o Prof. Emerson

---

## O pedido

Na mentoria de 13/08/2026 o Prof. Emerson determinou três tarefas, com a orientação explícita de
**não restringir a busca a um único ativo**, e sim abrir o leque em busca de desempenho melhor:

1. Buscar um BERT financeiro para o inglês
2. Buscar artigos que citam o BERT financeiro em inglês
3. Listar as aplicações encontradas nesses artigos

Este documento e os que o acompanham respondem aos três.

---

## Resumo executivo — os cinco achados que importam

**1. Existem dois "FinBERT" em inglês, e a confusão entre eles é comum na literatura.**
São modelos distintos, de grupos distintos, com corpora e tamanhos distintos, que compartilham o
nome. Qualquer trabalho que escreva apenas "FinBERT" sem identificar o repositório é ambíguo. Ver
[`01_FINBERT_ARACI_2019.md`](01_FINBERT_ARACI_2019.md) e
[`02_FINBERT_YANG_2020.md`](02_FINBERT_YANG_2020.md).

**2. O nosso desempenho de 0,58 NÃO é um problema do português.**
O FinBERT inglês, aplicado sem ajuste a manchetes setoriais, alcança **macro-F1 de 0,555**
(*Electronics*, v. 14, n. 23, art. 4680, 2025 — autoria não recuperada, ver nota de método).
O nosso FinBERT-PT-BR alcança **0,579** na mesma situação. São
estatisticamente indistinguíveis. Isso reposiciona por completo o diagnóstico do Capítulo 4: a
degradação por transferência de domínio é um fenômeno da arquitetura, não do idioma.

**3. Existe um trabalho que faz exatamente o que a dissertação faz — e que SUPERA o HAR.**
Halousková e Lyócsa (2025) combinam FinBERT com o HAR e reduzem o erro de previsão de volatilidade
em 12,74% em média, superando a linha de base em 98,76% dos casos. Nós não superamos. As diferenças
metodológicas que explicam isso são identificáveis e acionáveis — ver
[`04_HALOUSKOVA_LYOCSA_2025.md`](04_HALOUSKOVA_LYOCSA_2025.md).

**4. E esse mesmo trabalho confirma, de forma independente, o nosso efeito de cauda.**
O ganho deles é maior justamente **nos dias de variação extrema**: 14,99% contra 12,74% na média.
É a mesma conclusão da Seção 4.l da dissertação, obtida em outro mercado, com outro idioma, sobre
404 ativos e com dados intradiários.

**5. O padrão-ouro internacional de rotulagem confirma a objeção do Prof. Emerson — com um número.**
O *Financial PhraseBank* (MALO et al., 2014), base sobre a qual o FinBERT inglês é ajustado, foi
anotado por **16 pessoas com formação em finanças**, com **5 a 8 anotações por sentença** e
subconjuntos por nível de concordância. O nosso conjunto-ouro tem **1 anotador e 1 anotação por
manchete**. Ver [`06_FINANCIAL_PHRASEBANK.md`](06_FINANCIAL_PHRASEBANK.md).

---

## Os documentos desta pasta

| # | Documento | Do que trata | Por que importa para nós |
|---|---|---|---|
| **01** | [`01_FINBERT_ARACI_2019.md`](01_FINBERT_ARACI_2019.md) | FinBERT de Araci — o mais baixado | 4,46 milhões de downloads/mês; é a referência que Santos (2023) replicou para o PT-BR |
| **02** | [`02_FINBERT_YANG_2020.md`](02_FINBERT_YANG_2020.md) | FinBERT de Yang, Uy e Huang | 4,9 bilhões de tokens; publicado em periódico A1 de contabilidade; família de 4 modelos |
| **03** | [`03_FLANG_SHAH_2022.md`](03_FLANG_SHAH_2022.md) | FLANG e o *benchmark* FLUE | O sucessor técnico; mascaramento preferencial; EMNLP 2022 |
| **04** | [`04_HALOUSKOVA_LYOCSA_2025.md`](04_HALOUSKOVA_LYOCSA_2025.md) | FinBERT + HAR, 404 ativos | **O trabalho mais importante do levantamento.** Faz o que fazemos e consegue o que não conseguimos |
| **05** | [`05_MINO_WILLIAMSON_2025.md`](05_MINO_WILLIAMSON_2025.md) | BERT + GARCH(1,1)-t | Desenho quase idêntico ao nosso; coeficiente quase idêntico ao nosso |
| **06** | [`06_FINANCIAL_PHRASEBANK.md`](06_FINANCIAL_PHRASEBANK.md) | O padrão-ouro de rotulagem | Protocolo citável para responder ao Prof. Emerson sobre especialistas |
| **07** | [`07_CATALOGO_APLICACOES.md`](07_CATALOGO_APLICACOES.md) | **As aplicações, por tipo** | Resposta direta ao pedido 3; 9 famílias de aplicação identificadas |
| **08** | [`08_LICOES_PARA_A_DISSERTACAO.md`](08_LICOES_PARA_A_DISSERTACAO.md) | O que fazer com tudo isso | Diagnóstico do porquê eles superam o HAR e nós não; 6 ações propostas |

---

## Nota de método e de honestidade

O levantamento foi feito por busca na web em 13/08/2026, com verificação direta das páginas de
origem sempre que acessíveis. Registram-se as seguintes limitações:

- **Contagens de citação divergem por base.** A Semantic Scholar registra 778 citações para Araci
  (2019); o Google Scholar tipicamente reporta número bem superior para o mesmo trabalho. Adota-se
  aqui a cifra verificável, declarando a fonte.
- **Três textos não puderam ser lidos na íntegra** por bloqueio do editor (HTTP 403): o artigo de
  Huang, Wang e Yang (2023) na *Contemporary Accounting Research*, o artigo sobre ajuste setorial na
  *Electronics* (v. 14, n. 23, art. 4680, 2025) e a versão ACM de Halousková e Lyócsa. Para esses, os
  dados provêm da página de resumo, do repositório público ou de fontes secundárias, e cada
  afirmação assim obtida vem assinalada com **[via resumo]**.
- **A autoria do artigo da *Electronics* não foi recuperada** — o MDPI e o ResearchGate bloquearam o
  acesso e as buscas não retornaram os nomes. Antes de citá-lo na dissertação, é preciso abrir
  `https://www.mdpi.com/2079-9292/14/23/4680` no navegador e copiar a referência completa. O dado
  numérico (0,555 → 0,707 com 1.500 manchetes) está confirmado por duas fontes independentes.
- **Um número da literatura foi deliberadamente contestado.** O trabalho FinBERT-LSTM reporta
  "acurácia de 0,955", cifra que não é comparável aos nossos 52,3%. A discussão está em
  [`07_CATALOGO_APLICACOES.md`](07_CATALOGO_APLICACOES.md), seção "A armadilha dos 95%".
