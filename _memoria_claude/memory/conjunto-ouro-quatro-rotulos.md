---
name: conjunto-ouro-quatro-rotulos
description: O conjunto-ouro tem 4 rótulos (não 1) e a validação contra o mercado — base das respostas às duas perguntas do Prof. Emerson
metadata: 
  node_type: memory
  type: project
  originSessionId: 08181b53-ca1d-41ae-a256-cc9d79527860
  modified: 2026-08-08T14:38:54.971Z
---

O gabarito (`conjunto_ouro/conjunto_ouro_para_rotular.xlsx`, aba `Rotular`, 300 itens, 2018–2025) tem **quatro** colunas de rótulo, com exigências de competência diferentes:

| Coluna | Distribuição | Exige finanças? |
|---|---|---|
| `Sentimento_Humano` | Neutro 124 · Positivo 96 · Negativo 80 | Não (Santos usou 2 engenheiros + 1 linguista, α=0,88) |
| `Relevante_PETR4` | **Não 189 · Sim 111** (37%) | Parcialmente |
| `Direcao_Esperada_PETR4` | **Indefinida 240 (80%)** · Alta 39 · Baixa 21 | **Sim, integralmente** |
| `Confianca_Rotulador` | Alta 233 · Média 57 · Baixa 9 | — |

**Why:** a objeção do Prof. Emerson ("precisa de especialista em finanças") atinge só a 3ª coluna. Saber disso reposiciona a conversa inteira.

**How to apply:** aposentar a coluna de direção e substituí-la pelo retorno realizado (não precisa de anotador); usar o especialista como **árbitro de ~55 casos** (os relevantes com confiança média/baixa), não como anotador de 300.

**Validação contra o mercado** (`src/sentimento/validar_rotulos_contra_mercado.py` → `Mestrado_PETR4/validacao_rotulos_contra_mercado.json`):
- **Direção esperada pelo humano acertou 46,7%** (28/60 pregões distintos, p=0,699, IC95% [33,7%; 60,0%]). A regra ingênua "sempre Alta" teria dado 52,8%. ⚠️ IC largo — **não prova** que um especialista falharia.
- Relevância **não** prediz volatilidade em D+1 (mediana 1,01% vs 1,05%, p=0,76). Ressalva: as "não relevantes" também passaram pelo filtro da taxonomia, então o contraste é conservador.
- Tom negativo → |retorno| ~30% maior que tom positivo (1,64% vs 1,26% na média). **p=0,44, é indício e não resultado** — mas aponta para o eixo da volatilidade.
- Tom × direção nas relevantes: **Negativo deu 11 Alta contra 13 Baixa** — tom negativo não implica queda numa produtora de petróleo. Explica, no dado bruto, por que a direção fica no acaso.

**Resposta à 2ª pergunta ("como usaria na prática"):** o conjunto-ouro **não é base de treino** (300 itens não ajustam 110M de parâmetros; o Albertina colapsou). É **instrumento de medida e calibração**. O uso mais forte é **corrigir o viés de classificação do ISM** por inversão da matriz de confusão (quantificação / Adjusted Classify and Count) — 300 rótulos calibram 8 anos de série. Também: medir 0,58 vs 0,76 de Santos, arbitrar escolhas de modelo, diagnosticar a classe neutra, e quantificar a atenuação (o efeito do sentimento na volatilidade é um **piso**, porque o ISM tem erro de medida conhecido).

⚠️ **As duas rodadas não podem ser somadas.** Rodada 1 (300) = estratificada com `peso_amostral` → serve para **medir**. Rodada 2 (`rotulagem_ampliacao.xlsx`, 400, só 33 feitas) = **amostragem por incerteza** → serve para **treinar**, e enviesaria a acurácia para baixo se misturada.

Documento completo: `orientacoes/RESPOSTA_DUAS_PERGUNTAS_EMERSON.md`.
Ver [[mentoria-emerson-agosto2026]], [[gaps-pesquisa-petr4]] e [[resumos-pesquisas-finbert]].
