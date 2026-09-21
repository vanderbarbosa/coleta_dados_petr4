---
name: filtro-relevancia-primeiro-ganho
description: "Filtrar o ISM para CAT1+CAT2 melhora o sinal de volatilidade em 23% (p=0,001) — único ganho em 9 tentativas; mas NÃO bate o HAR fora da amostra"
metadata: 
  node_type: memory
  type: project
  originSessionId: 08181b53-ca1d-41ae-a256-cc9d79527860
  modified: 2026-08-11T01:54:40.316Z
---

Testado em 10/08/2026, a partir de uma pergunta do Vanderlei: *"Santos descartou as notícias sem relação com finanças; nós não descartamos as sem relação com a Petrobras — não teríamos um índice melhor?"*

Três scripts, três etapas:
- `src/sentimento/filtrar_ism_por_relevancia.py` → `filtro_relevancia_ism.json`
- `src/modelagem/07_modelagem_ism_filtrado_petr4.py` → `modelagem_ism_filtrado.json`
- `src/modelagem/08_previsao_volatilidade_ism_filtrado.py` → `previsao_volatilidade_ism.json`

## Os dois filtros NÃO são a mesma coisa
- **Santos** descartou o que **não era financeiro** — 158 de 661 = 23,9%
- **Nosso** rótulo marca o que **não afeta a PETR4**, mas continua sendo financeiro — 189 de 300 = 63,0%
- *"EUA e UE excluem Rússia do Swift"*: Santos MANTÉM, nosso critério DESCARTA
- Nosso corpus já passa por filtro equivalente ao dele **na coleta**, via taxonomia de 152 termos

## Etapa 1 — correlação com volatilidade D+1 (n = 1.988 pregões)
| Variante | Notícias | \|r\| |
|---|---|---|
| A — todas | 205.697 (100%) | 0,1385 |
| **B — CAT1+CAT2** | **120.792 (59%)** | **0,1704** |
| C — só CAT1 | 64.882 (32%) | 0,1495 |

Bootstrap pareado (10.000 reamostras): **B vs A = +0,0319, IC95 [+0,0135; +0,0504], p = 0,0010 SIGNIFICATIVO** (+23%). B vs C: p = 0,098. C vs A: p = 0,475.

## Etapa 2 — propaga para a DIREÇÃO? NÃO
Pipeline do Script 04 replicado, mudando só o ISM. XGBoost de fusão: **52,31% nos dois casos**. McNemar **p = 1,0000** (52 acertos exclusivos de cada lado). Confirma o teste de teto por via independente.

## Etapa 3 — propaga para a PREVISÃO de volatilidade? NÃO (contra o HAR)
HAR (Corsi 2009) sobre volatilidade de Parkinson (High/Low), janela expansiva, 795 previsões, Diebold-Mariano:

| Modelo | EQM | QLIKE | R² fora |
|---|---|---|---|
| HAR sozinho | 0,16451 | −7,3852 | 0,3060 |
| HAR + ISM completo | 0,16546 | −7,3897 | 0,3020 |
| HAR + ISM filtrado | **0,16406** | −7,3891 | **0,3079** |

- **B vs HAR: p = 0,6405 (EQM) / 0,2170 (QLIKE) → NÃO significativo**
- **B vs A: DM = −2,869, p = 0,0041 → SIGNIFICATIVO** (o filtrado ganha do completo)
- Coeficiente do ISM na regressão: filtrado −0,2924 (t = −3,71, **p = 0,0002**), completo −0,3110 (p = 0,0020). Sinal negativo = pessimismo hoje → volatilidade amanhã, como a teoria prevê.
- Quartil turbulento: ganho maior (+0,00292) mas p = 0,1803, não significativo.

**Why:** é o **único ganho** em 9 tentativas — e a assimetria é o achado real: **as 8 que mexeram no MODELO falharam; a 1 que mexeu no CORPUS funcionou**. A lição é curadoria de dados > aperfeiçoamento de modelo. Mas o ganho não chega a superar um modelo econométrico maduro: sentimento e histórico de volatilidade são **redundantes** (dia agitado = dia de muita notícia).

**How to apply:** adotar CAT1+CAT2 como recorte padrão. Ao reportar, **nunca** dizer que o sentimento melhora a previsão de volatilidade — dizer que o efeito é real (p=0,0002) mas não acrescenta ao HAR. Próximo passo proposto: substituir o corte binário por **peso contínuo** de relevância, aprendido da reação do mercado (dispensa o julgamento humano, respondendo à objeção do Emerson).

⚠️ **Tensão registrada na dissertação:** o anotador humano marcou 54 notícias de CAT2 como "não relevantes", mas são justamente elas que fazem B ganhar de C. **O critério humano de relevância e o estatístico não coincidem.**

Escrito como Seção 4.k (`capitulos/4k-relevancia-volatilidade.tex`); Cap. 5 atualizado (linha na tabela de contribuições, limitação revista, 8ª frente futura). Docx para leigos: `orientacoes/EXPLICACAO_SIMPLES_FILTRO_RELEVANCIA.docx`.

Ver [[g3-adaptacao-esquecimento]], [[calibracao-ism-acc]], [[revalidacao-tres-hipoteses-rejeitadas]] e [[gaps-pesquisa-petr4]].
