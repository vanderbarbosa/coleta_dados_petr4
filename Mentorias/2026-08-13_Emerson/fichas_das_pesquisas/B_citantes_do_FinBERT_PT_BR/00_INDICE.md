# Resumos completos das pesquisas — índice e guia de leitura

**Mestrando:** Vanderlei Barbosa da Silva · **Orientador:** Prof. Dr. Julio Cesar Nievola (PUCPR/PPGIa)
**Elaborado em:** 04/08/2026 · **Para:** mentoria de 10/08/2026 (Prof. Dr. Emerson Cabrera Paraiso)

---

## O que há nesta pasta

Um documento por pesquisa, com o mesmo esqueleto de sete blocos, para que possam ser lidos
em paralelo e comparados campo a campo:

1. **Ficha bibliográfica** — referência ABNT, veículo, fomento, links, disponibilidade de código
2. **Objetivo e pergunta de pesquisa**
3. **Dados** — fonte, volume, período, tratamento
4. **Tecnologias, bibliotecas e encoders** — tudo o que foi usado, com versões quando declaradas
5. **Método passo a passo** — incluindo todos os hiperparâmetros declarados
6. **Resultados** — tabelas numéricas completas
7. **Código** — o script real quando publicado; reconstrução fiel e assinalada quando não
8. **Leitura crítica** — o que aproveitar, o que não aproveitar, gaps e melhorias

---

## Os documentos

| # | Documento | Pesquisa | Por que está aqui |
|---|---|---|---|
| **01** | [`01_SANTOS_2023_FinBERT-PT-BR.md`](01_SANTOS_2023_FinBERT-PT-BR.md) | **Santos, Bianchi e Costa (2023)** + monografia de 2022 | É o modelo que usamos. Documento mais longo e detalhado do conjunto. |
| **02** | [`02_BLOCH_2026_maquina_de_comite.md`](02_BLOCH_2026_maquina_de_comite.md) | Błoch, Santana e Amantino (2026) | **O único que executou o FinBERT-PT-BR.** Método de comitê replicável. |
| **03** | [`03_ABILIO_2024_NER_earnings_calls.md`](03_ABILIO_2024_NER_earnings_calls.md) | Abílio, Coelho e Silva (2024) | Corpus financeiro PT-BR **público**, com código MIT. Evidência mono > multilíngue. |
| **04** | [`04_IMAI_2024_concept_drift.md`](04_IMAI_2024_concept_drift.md) | Imai et al. (2024) — PPGIa/PUCPR | *Concept drift*. Autores do nosso programa. Ameaça direta à nossa validade. |
| **05** | [`05_TELES_2025_LLMs_sentimento.md`](05_TELES_2025_LLMs_sentimento.md) | Teles e Figueiredo (2025) | Benchmark LLM × clássicos. Define o experimento G6. |
| **06** | [`06_REICHERT_PERLIN_2025_dicionarios.md`](06_REICHERT_PERLIN_2025_dicionarios.md) | Reichert e Perlin (2025) | Dicionário léxico financeiro **com português**. Linha de base que nos falta. |
| **07** | [`07_JPALVES_2025_PRIO3.md`](07_JPALVES_2025_PRIO3.md) | jp-alves (2025) — repositório PRIO3 | **Não é trabalho citante.** É o pipeline público mais parecido com o nosso. Código completo. |

### Scripts reconstruídos e coletados

A pasta [`../_codigos/`](../_codigos/) contém o código real baixado dos repositórios públicos e
as reconstruções fiéis dos pipelines não publicados. Cada arquivo declara no cabeçalho se é
**código original de terceiro** ou **reconstrução**.

---

## Critério de inclusão e exclusão

Foram incluídos os trabalhos com **relação ou potencial de colaboração** com a dissertação.
Dois trabalhos citantes foram **excluídos**, com a razão registrada por transparência:

| Excluído | Razão |
|---|---|
| **Alves et al. (2024)** — *Sentimentos em Cena*, comentários de trailers da Netflix no YouTube | Domínio de entretenimento. A única contribuição aproveitável é uma frase de introdução ("predominação de análises em inglês… falta de trabalhos na língua portuguesa"), já registrada em `citacoes_por_trabalho.csv`. Não há método, dado ou código transponível. |
| **Tanaka et al. (2026)** — *churn* em cooperativa agroindustrial | Não opera com texto. A citação a Santos é provavelmente imprecisa (invocada para "amostragem estratificada", que Santos não trata). O único aproveitamento é o uso de SHAP, já registrado como gap G13. |

Foi **incluído** um trabalho que **não** cita Santos: o repositório `jp-alves/prio3-sentiment`
(documento 07). Não é publicação acadêmica, mas é o pipeline público mais próximo do nosso —
notícias de petróleo, ação brasileira, FinBERT-PT-BR, estudo de evento e causalidade de
Granger — e o código está inteiro disponível.

---

## Mapa de leitura sugerido

Se o tempo for curto antes de 10/08, ler nesta ordem:

1. **Documento 01, seções 5 e 7** — os hiperparâmetros e o script de adaptação de domínio.
   É o insumo direto do gap G3, a nossa frente técnica principal.
2. **Documento 02, seção 8** — a caracterização léxico-versus-contexto e o método de comitê.
   Explica a nossa matriz de confusão e dá o gap G7.
3. **Documento 07 inteiro** — é curto e mostra um pipeline completo funcionando, com achados
   que convergem com os nossos (impacto intradiário desprezível, *drift* de médio prazo).
4. **Documento 04, seção 8** — a ameaça de *concept drift*, para não ser pego de surpresa.

Os documentos 03, 05 e 06 são de consulta, e podem ser lidos depois da mentoria.

---

## Quadro comparativo geral

| | Santos (2023) | Błoch (2026) | Abílio (2024) | Imai (2024) | Teles (2025) | Reichert (2025) | jp-alves (2025) | **Nossa pesquisa** |
|---|---|---|---|---|---|---|---|---|
| **Idioma** | PT-BR | PT (histórico) | PT-BR | PT-BR | Inglês | Multi (inc. PT) | PT-BR | **PT-BR** |
| **Domínio** | Finanças | História | Finanças | Notícias gerais | Finanças | Finanças | Finanças | **Finanças** |
| **Tarefa** | Sentimento | Sentimento | NER | Classificação | Sentimento | Léxico | Sentimento | **Sentimento** |
| **Usa FinBERT-PT-BR** | (criou) | **Sim** | Não | Não | Não | Não | **Sim** | **Sim** |
| **Ativo único** | Não | — | Não | — | Não | Não | **Sim (PRIO3)** | **Sim (PETR4)** |
| **Prevê direção** | Não | — | Não | — | Não | Não | Sim (evento) | **Sim** |
| **Prevê volatilidade** | **Não** | — | **Não** | — | **Não** | **Não** | **Não** | **SIM** |
| **Modelo econométrico** | Não | Não | Não | Não | Não | Não | Granger | **GARCH + Granger** |
| **Gabarito humano** | Sim (503) | Sim (subconj.) | Superv. fraca | Não | Sim (datasets) | Sim (COPOM) | **Não** | **Sim (300)** |
| **Código público** | **NÃO** | Não | **Sim (MIT)** | Não | Não | Não decl. | **Sim** | Sim (interno) |

**A linha que decide a dissertação é a da volatilidade.** É a única em que a nossa coluna é a
única com "sim".
