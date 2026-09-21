---
name: calibracao-ism-acc
description: "O ISM bruto tem viés de 87% (o corpus não é negativo, é neutro) — mas calibrar não melhora a previsão; e o código do FinBERT-PT-BR não existe publicamente"
metadata: 
  node_type: memory
  type: project
  originSessionId: 08181b53-ca1d-41ae-a256-cc9d79527860
  modified: 2026-08-08T15:00:57.829Z
---

Demonstração prática rodada em 08/08/2026 (`src/sentimento/calibrar_ism_com_gabarito.py` + `avaliar_ganho_calibracao.py`), respondendo ao Prof. Emerson sobre o uso prático dos rótulos.

**Matriz de confusão ponderada** (peso_amostral soma exatamente 205.697 = corpus inteiro):
- Neutro verdadeiro → 33% classificado como **negativo**
- **Positivo verdadeiro → só 30% acerta; 34% vai para "negativo"**
- O modelo puxa tudo para negativo, sistematicamente.

**Resultado da calibração ACC** (Adjusted Classify and Count, Forman 2008):
- ISM bruto **−0,3450** → calibrado **−0,0439**. Viés de **87%**.
- IC95% por bootstrap: [−0,2250; +0,1857] — o bruto está **fora**, o viés é distinguível de zero.
- Proporções: Negative 48,5%→31,2% · Positive 14,0%→26,8%
- **49 dos 96 meses trocam de SINAL.**
- Correlação bruto×calibrado = 0,973 (muda o NÍVEL, não a forma); dp 0,065→0,167.

**Why:** o corpus de notícias PETR4 **não é negativo, é ~neutro** — a negatividade era artefato do classificador. Qualquer afirmação de "mercado pessimista em X" muda em metade da série.

**How to apply:** calibrar na agregação **mensal** (diário amplifica ruído: 82 dias com <10 notícias); manter ISM diário bruto p/ curto prazo; declarar no método.

⚠️ **RESULTADO NEGATIVO, reportar sem esconder:** a calibração **NÃO melhora a previsão** (vol mês seguinte: |r| 0,118→0,051; contemporânea 0,309→0,273). Correlação é invariante a deslocamento de nível, e a calibração desloca sobretudo o nível. Ela conserta a **interpretação**, não o **poder preditivo**. Para melhorar índice o caminho é o **classificador** (comitê G7, adaptação de domínio G3), não a agregação.

**Achado lateral:** relação **contemporânea** é significativa (r=−0,309, p=0,002), a **preditiva** não (p=0,26). Sentimento coincide com volatilidade, não a antecipa (janela mensal).

**Ressalvas:** a "verdade" é 1 anotador; a linha Positive tem só 96 itens (maior erro amostral, e é a que mais corrige); ACC pressupõe matriz estável no período (ver drift, G4).

**Código-fonte do FinBERT-PT-BR: CONFIRMADO inexistente** por 4 caminhos (GitHub pessoal, org turing-usp, HF, busca de código autenticada — 92 hits, todos de consumidores). Mas achei em `orientacoes/_codigos/terceiros/`: `IagoErrera/scrap-fin` (chunking c/ overlap 400/50 p/ texto longo — serve ao G9), `JoseOtavioJunqueira/Analise-de-Sentimento-IC` (ICMC/USP, pipeline completo c/ RF/LogReg/Q-Learning), `MarcoAfB/soybean-...`, `ajdavidl/corpus-atas-copom`. E **hiperparâmetros reais** de quem fez fine-tune a partir do modelo (`Asthem/FinBERT-PT-BR-news`): lr 2e-5, batch 8, seed 42, **10 épocas** — corrobora que nossas 3 épocas eram poucas.

Documento: `orientacoes/DEMONSTRACAO_PRATICA_E_CODIGO_FONTE.md`.
Ver [[conjunto-ouro-quatro-rotulos]], [[gaps-pesquisa-petr4]], [[encoders-sentimento-ptbr]].
