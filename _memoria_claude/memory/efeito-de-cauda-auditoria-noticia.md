---
name: efeito-de-cauda-auditoria-noticia
description: "Auditoria direta das 205.697 notícias: o sentimento acompanha o mercado, não o antecede; e o efeito na volatilidade é de CAUDA (Pearson acha, Spearman não)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 08181b53-ca1d-41ae-a256-cc9d79527860
  modified: 2026-08-11T02:31:40.152Z
---

Feito em 10/08/2026, a partir de uma cobrança do Vanderlei: *"temos as notícias, temos os preços, e nunca checamos se a direção e a volatilidade foram assertivas com o pregão do dia seguinte."* Estava certo — tudo até então era mediado por modelo.

Script: `src/modelagem/09_acertividade_noticia_a_noticia.py` → `Mestrado_PETR4/acertividade_noticia.json`. Seção 4.l da dissertação.

## Dois cuidados que decidem a validade
- **P0 vs P1.** P0 = primeiro pregão que fecha após a publicação (mesmo dia, para notícia intradiária) → mistura reação e previsão. P1 = pregão seguinte → estritamente preditivo. `Data_Ajustada` já desloca +1 dia de calendário para notícia ≥17h (54.259 = 26%), mas **não trata fim de semana**; o mapeamento para pregão real é refeito com `merge_asof(direction='forward')`.
- **Pseudorreplicação.** 205.697 notícias em 1.989 pregões = mesmo retorno contado ~100×. Teste só vale colapsando por pregão (voto majoritário). Errei isso na 1ª versão e corrigi.

## Achado 1 — o sentimento ACOMPANHA, não antecede
| | Positivo | Neutro | Negativo |
|---|---|---|---|
| P0 (mesmo dia) subiu | 55,0% | 53,2% | 51,6% |
| **P1 (dia seguinte) subiu** | **52,5%** | **52,4%** | **51,5%** |

Ordenamento limpo em P0, colapsa em P1. Referência: PETR4 subiu em 52,78% dos pregões. A separação em P0 é jornalismo narrando o movimento em curso.

## Achado 2 — a regra ingênua PERDE (47,59% por pregão, p<0,0001)
IC95 [45,37%; 49,81%] — nem alcança 50%. **Não é anti-previsão, é aritmética:** 48,5% dos rótulos são Negativos e o papel subiu 52,78% dos dias. Regra que aposta na baixa num papel que sobe perde por construção.
- **Não contradiz os 54,5% do XGBoost** — lá é modelo treinado que combina ISM + retorno + volatilidade defasados e aprende a *ponderar* o sentimento. A comparação valoriza a etapa de aprendizado.
- Nenhum recorte salva: categoria 48,09–50,01%; após-17h 49,52% vs 49,33%; **confiança é ANTI-informativa** (Q1 50,18% → Q4 48,83%; Spearman −0,0346, p=0,0020) — casa com o bug sigmoide/softmax de [[bug-problem-type-sigmoide]].

## Achado 3 — ZERO pregões de maioria positiva
1.488 Negativos, 457 Neutros, **0 Positivos**. ISM diário negativo em **100%** dos 1.989 pregões (mediana −0,260). A comparação canônica Neg×Pos é **impossível** neste corpus. Vira limitação declarada no Cap. 5: a pesquisa nunca observa o mercado após imprensa francamente otimista.

## Achado 4 (O PRINCIPAL) — o efeito é de CAUDA
| Medida | Valor | p | Enxerga |
|---|---|---|---|
| Pearson | −0,1309 | <0,0001 | magnitudes |
| **Spearman** | **−0,0268** | **0,2367** | só ordenação |
| Razão médias (terço pess./otim.) | 1,237× | — | extremos |
| Razão medianas | 1,048× | — | dia típico |

Pearson acha, Spearman não → **a associação vive nos dias excepcionais e some no pregão comum.** Terços do ISM: p=0,210, não significativo. Alarme de volatilidade: precisão 32,2% vs base 34,4%, p=0,491 — pior que o acaso.

**Why:** converge com a **regressão quantílica** (efeito +542 bps no quantil 0,05, nulo nos altos), que é sobre RETORNO enquanto isto é sobre VOLATILIDADE. Dois métodos independentes localizam o sinal na mesma região.

**How to apply:** a tese central passa a ser enunciada como **"o sentimento não move o pregão comum; ele importa nos extremos"** — mais forte que "informa risco, não direção", porque *explica* os resultados anteriores: por que a direção falha (maioria dos dias é comum), por que a média dava p marginal, por que a quantílica funcionou, por que não bate o HAR ([[filtro-relevancia-primeiro-ganho]]).

⚠️ Ao reportar diferenças sobre a tabela de notícias, **sempre** colapsar por pregão antes de testar. E reportar Pearson e Spearman lado a lado sempre que a variável for volatilidade — a divergência entre eles é informação, não ruído.

Docx para leigos: `orientacoes/EXPLICACAO_SIMPLES_AUDITORIA_NOTICIA.docx`.

Ver [[filtro-relevancia-primeiro-ganho]], [[calibracao-ism-acc]], [[bug-problem-type-sigmoide]] e [[diagnostico-erro-neutro]].
