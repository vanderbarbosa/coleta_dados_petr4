# Mino e Williamson (2025) — BERT com GARCH, o desenho mais próximo do nosso

## 1. Ficha bibliográfica

| Campo | Conteúdo |
|---|---|
| **Referência** | MINO, D.; WILLIAMSON, C. **Sentiment and volatility in financial markets: a review of BERT and GARCH applications during geopolitical crises.** arXiv:2510.16503, 2025. |
| **Instituição** | School of Mathematical Sciences, University College Cork |
| **Codificador** | BERT genérico ajustado para linguagem financeira (**não** FinBERT) |
| **Modelo de volatilidade** | **GARCH(1,1) com distribuição *t*-Student** |

## 2. Por que este trabalho importa

O desenho é quase idêntico ao da nossa dissertação: notícias processadas por um codificador
contextual, agregadas em índice diário, e a relação com a volatilidade estimada por
**GARCH(1,1) com distribuição *t*-Student** — a mesma especificação, item por item, adotada no
nosso Script 04.

## 3. Dados

| Elemento | Conteúdo |
|---|---|
| Fonte | Plataforma Goperigon, agregando as 100 principais fontes noticiosas dos EUA |
| Volume | Mais de 10.000 manchetes |
| Período | 01/01/2024 a 17/07/2024 (cerca de sete meses) |
| Ativo | Retornos diários do S&P 500 |
| Observações | 105 períodos diários |
| Controles | VIX, juro do título de 10 anos, Índice de Estresse Financeiro (OFR), Índice de Incerteza de Política Econômica (EPU) |

## 4. Resultados

| Variável | Coeficiente | valor-$p$ |
|---|---|---|
| **Escore de sentimento** | **$-0{,}2275$** | **0,0016** |
| VIX | $-0{,}2865$ | 0,0094 |
| Título de 10 anos, OFR, EPU | não significativos | $> 0{,}05$ |

$R^2$ ajustado = 0,1481 · estatística $F$ = 4,687 ($p = 0{,}0006$)

## 5. A comparação que vale a pena fazer

| | Mino e Williamson (2025) | **Nossa dissertação (Seção 4.k)** |
|---|---|---|
| Mercado | S&P 500 (EUA) | PETR4 (Brasil) |
| Idioma | Inglês | Português |
| Codificador | BERT ajustado | FinBERT-PT-BR |
| Modelo | GARCH(1,1)-*t* | GARCH(1,1)-*t* e HAR |
| Observações | 105 dias | 1.988 pregões |
| **Coeficiente do sentimento** | **$-0{,}2275$ ($p = 0{,}0016$)** | **$-0{,}2924$ ($p = 0{,}0002$)** com índice filtrado; $-0{,}3110$ ($p = 0{,}0020$) com índice completo |

**Os coeficientes são de magnitude quase idêntica, e ambos negativos.** Dois mercados diferentes,
dois idiomas diferentes, dois codificadores diferentes, dois corpora diferentes — e a mesma
estimativa: sentimento mais pessimista hoje, volatilidade maior amanhã, com efeito da ordem de
$-0{,}23$ a $-0{,}31$.

Essa convergência é o achado mais útil desta ficha. Ela permite escrever na dissertação que a nossa
estimativa **não é um artefato do mercado brasileiro nem do português**, e sim uma medida
consistente com o que se obtém de forma independente no maior mercado acionário do mundo.

## 6. As duas lacunas deles que a nossa dissertação já preenche

Este é o ponto em que o levantamento devolve algo à nossa pesquisa em vez de apenas cobrar dela.

**Lacuna 1 — eles não avaliam fora da amostra.** O artigo reporta apenas coeficientes e valores-$p$
de ajuste dentro da amostra. **Não há métrica de previsão fora da amostra** (RMSE, MAE, QLIKE) nem
teste de comparação preditiva. A nossa Seção 4.k faz exatamente isso: janela expansiva, 795
previsões, EQM e QLIKE, teste de Diebold-Mariano contra o HAR.

Ou seja: **eles param onde nós continuamos.** E foi justamente ao continuar que descobrimos que a
significância dentro da amostra não se converte em ganho preditivo. Se tivéssemos parado onde eles
param, teríamos relatado sucesso — e estaríamos errados.

**Lacuna 2 — eles não estratificam por regime.** Os próprios autores declaram como limitação que
não separaram períodos de crise dos períodos normais nem testaram quebras estruturais. A nossa
Seção 4.l faz precisamente essa estratificação, e é dela que emerge o efeito de cauda.

**Consequência para a dissertação:** estas duas lacunas devem ser explicitadas no capítulo de
contribuições. Elas convertem o que hoje se apresenta como resultado negativo — "não superamos o
HAR" — em contribuição metodológica: **fomos mais longe na avaliação do que o trabalho comparável
publicado, e é por isso que encontramos o limite que ele não encontrou.**

## 7. Leitura crítica

**Fragilidades do trabalho deles, a registrar com honestidade:**
- **105 observações**, contra os nossos 1.988 pregões. Amostra pequena para inferência sobre
  volatilidade.
- **Sete meses de dados**, período curto demais para caracterizar regimes.
- Usam **BERT genérico**, não um modelo financeiro, embora citem o FinBERT como aprimoramento
  futuro. Nós usamos um modelo de domínio.
- O título anuncia "*review*", mas o trabalho apresenta análise empírica própria — a natureza do
  texto é ambígua e isso deve ser verificado antes de classificá-lo na revisão de literatura.

**Conclusão:** é um trabalho comparável em desenho, porém **inferior em rigor de avaliação e em
tamanho de amostra** ao nosso. Serve como validação externa do coeficiente e como demonstração de
que a nossa avaliação é mais exigente que a de trabalhos publicados na mesma linha.
