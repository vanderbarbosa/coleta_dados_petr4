# As seis pesquisas essenciais — PDFs

**Situação: 4 das 6 obtidas.** As duas restantes estão atrás de assinatura de editora e precisam ser
baixadas pelo Portal de Periódicos CAPES com o login da PUCPR.

---

## O que está nesta pasta

| Arquivo | Alvo | Pesquisa | Páginas |
|---|---|---|---|
| `VOL_1_HALOUSKOVA_LYOCSA_2025.pdf` | volatilidade | Halousková e Lyócsa (2025) — 404 ações do S&P 500 | 51 |
| `VOL_2_HASHAMI_MALDONADO_2025.pdf` | direção da volatilidade | Hashami e Maldonado (2025) — petróleo Brent | 9 |
| `DIR_1_RUAN_JIANG_2025.pdf` | direção | Ruan e Jiang (2025) — *Mathematics* 13(17):2747 | 22 |
| `DIR_3_SCHUMAKER_CHEN_2009.pdf` | direção (20 min) | Schumaker e Chen (2009) — AZFinText | 29 |

## O que falta, e como obter

| Pesquisa | Onde está | Como obter |
|---|---|---|
| **Bodilsen e Lunde (2025)** | *Journal of Applied Econometrics*, 40(1):18–36 | Portal de Periódicos CAPES (Wiley). Versão de trabalho no SSRN, `abstract_id=4401032` |
| **Nguyen, Shirai e Velcin (2015)** | *Expert Systems with Applications*, 42(24):9603–9611 | Portal de Periódicos CAPES (Elsevier). Cópia no ResearchGate exige conta |

Tentativas feitas para ambas: SSRN, repositório institucional de Aarhus, HAL, Semantic Scholar,
repositório da JAIST e ResearchGate. Todas retornaram bloqueio.

---

## O que a leitura dos PDFs acrescentou

Dois dos quatro trouxeram números que antes constavam como não recuperados. Ambos **melhoram a
nossa posição**.

### Ruan e Jiang (2025) — o alvo é idêntico ao nosso

O artigo define o alvo como $y(t) = 1$ se o fechamento de $t+1$ for maior que o de $t$ —
**exatamente a nossa definição**. Usam XGBoost com atributos técnicos, de volatilidade e de
sentimento do FinBERT, sobre ações do S&P 500, de janeiro de 2018 a dezembro de 2023, em cinco
janelas móveis de seis meses.

| Modelo | Acurácia | F1 | AUC | Lucro simulado |
|---|---|---|---|---|
| Só indicadores técnicos | 0,624 | 0,608 | 0,652 | 3,21% |
| Técnicos + momento | 0,636 | 0,620 | 0,661 | 3,87% |
| Técnicos + VADER | 0,644 | 0,631 | 0,669 | 4,85% |
| **Técnicos + FinBERT** | **0,703** | **0,688** | **0,740** | **7,63%** |
| Técnicos + FinBERT, sem volatilidade | 0,689 | 0,674 | 0,722 | 6,93% |

**O ganho do sentimento é de $+7{,}9$ pontos percentuais** ($0{,}703 - 0{,}624$). O nosso é de
$+4{,}4$. **Ambos dentro da faixa de 2 a 10 relatada por Nguyen et al. (2015).**

Note-se ainda que o VADER, dicionário genérico, rende apenas $+2{,}0$ pontos, contra os $+7{,}9$ do
FinBERT. **A escolha de um codificador de domínio importa** — o que respalda a nossa opção pelo
FinBERT-PT-BR.

⚠️ **Ressalva que convém levantar antes que perguntem.** A linha de base deles, só com indicadores
técnicos, alcança **62,4%** na direção diária. É valor bem acima do que a Hipótese de Mercados
Eficientes faria esperar, e bem acima da nossa linha de base de 50,1%. Três explicações possíveis,
nenhuma verificável no texto: agregação de várias ações num só conjunto, média sobre cinco janelas,
e o fato de o período 2018–2023 ter sido de forte alta no S&P 500. **A comparação segura é o ganho,
não o nível.**

### Schumaker e Chen (2009) — os 71,18% são o melhor de seis

A Tabela 4 do artigo traz o desempenho sob **seis esquemas de particionamento** do corpus:

| Particionamento | Acurácia direcional | Retorno simulado |
|---|---|---|
| **Setor** | **71,18%** | 8,50% |
| Grupo | 66,12% | 4,57% |
| Indústria | 62,37% | 2,02% |
| Universal (sem partição) | 58,17% | 2,86% |
| Sub-indústria | 57,50% | 1,09% |
| **Ação específica** | **56,92%** | 1,01% |

**O número que a literatura cita — 71,18% — é o melhor entre os seis.** A faixa completa vai de
56,92% a 71,18%.

**E o dado decisivo para nós está na última linha.** Quando o particionamento desce ao nível da
**ação individual**, que é exatamente a nossa situação, o desempenho cai para **56,92%** — e isso
no horizonte de vinte minutos, que é o mais fácil de todos.

**Os nossos 54,5% na previsão do pregão seguinte, para uma única ação, passam a ser um resultado
inteiramente coerente com o de um sistema consagrado da área.**

---

## Como citar isto na reunião

> *"Baixei quatro das seis. E ao ler os PDFs achei dois números que ninguém cita. O Ruan e Jiang, de
> 2025, usa a mesma definição de alvo que eu, o mesmo XGBoost e o mesmo tipo de atributo — e o ganho
> do sentimento deles é de 7,9 pontos percentuais, contra os meus 4,4. Ambos dentro da faixa da
> literatura. E o Schumaker, que todo mundo cita com 71,18%, na verdade reporta seis números: quando
> ele desce ao nível de ação individual, que é o meu caso, dá 56,92% — e isso a vinte minutos, não
> no dia seguinte."*
