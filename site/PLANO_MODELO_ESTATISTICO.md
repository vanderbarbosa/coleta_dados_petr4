# Plano de reengenharia do modelo estatístico (FinBERT + XGBoost)

Dissertação PETR4 | Vanderlei Barbosa da Silva

> Documento honesto de **planejamento**. Ele separa o que é melhoria de engenharia
> (factível e mensurável) do que é limite **intrínseco** do problema — para não
> prometer à banca uma acurácia que a literatura mostra ser irreal.

## 1. Enquadramento honesto (o que dizer à banca)

Prever a **direção diária** de uma ação a partir de notícias é, por natureza, difícil:
a Hipótese dos Mercados Eficientes implica que informação pública já está, em boa
parte, no preço. Na literatura, acurácia direcional de **52–56%** já é considerada
um resultado relevante. Portanto:

- **Não é responsável** apresentar meta de "acurácia máxima/alta". A meta correta é
  **superar de forma estatisticamente significativa** um baseline ingênuo (classe
  majoritária / persistência), com validação temporal sem vazamento.
- A contribuição científica está tanto no **número** quanto na **interpretabilidade**
  (a leitura setorial) e no **rigor** (validação, testes pareados, backtest com custos).

## 2. Diagnóstico do modelo atual

- **Features (3):** retorno recente, volatilidade recente, índice de sentimento.
  É pouco — e, no endpoint interativo, retorno/volatilidade são **fixos** (contexto
  da data de referência), então só o sentimento varia por notícia.
- **Rótulo:** direção do próximo pregão (alta/baixa) sem *dead-band* — dias de
  variação ~0 viram ruído.
- **Acurácia atual:** ~53% (honesta, modesta).

## 3. Melhorias factíveis (engenharia) — em ordem de custo/benefício

1. **Enriquecer features** (maior ganho esperado):
   - Índice de sentimento **por categoria** (ISM das 7 CATs), não só o agregado.
   - **Defasagens** (lags 1–5) de retorno, volatilidade (GARCH) e sentimento.
   - **Volume**, amplitude (máx–mín), dia da semana, proximidade de resultados.
   - Exógenas: **Brent/WTI** e **câmbio (USD/BRL)** — canais de Kilian/Hamilton.
   - Lead-lag notícia→preço (a maioria das notícias sai após o fechamento).
2. **Rótulo com *dead-band*:** ignorar |retorno| < ε (ex.: 0,3%) no treino, ou
   modelar **3 classes** (alta/estável/baixa). Reduz ruído e melhora a separação.
3. **Modelos e validação:**
   - Baselines explícitos: classe majoritária e persistência (ontem→hoje).
   - Regressão logística (interpretável) vs. **XGBoost com tuning por validação
     temporal (walk-forward)**; opcional LSTM/atenção como comparação.
   - **Sem vazamento**: split temporal estrito (treino<val<teste), *scaler* ajustado
     só no treino, nenhuma feature futura.
   - Métricas: acurácia, F1, AUC, e **MCC**; teste de significância vs. baseline
     (McNemar/DeLong) e por subperíodo.
4. **Camada de sentimento:**
   - Comparar **FinBERT-PT-BR × BERTimbau** (já previsto) lado a lado.
   - **Tratar negação/cessação** (ex.: "deixar de pagar dividendos") também no nível
     do texto — hoje isso é corrigido pela leitura setorial; avaliar mover parte
     para o pré-processamento do sentimento.
   - Sentimento **aspect-based** (por categoria) em vez de polaridade única.
5. **Volatilidade (frente mais promissora):** a previsão de **volatilidade**
   (GARCH-X com sentimento) tende a ser mais informativa e defensável que a direção —
   priorizar como resultado central, com a direção como complemento.
6. **Backtest honesto:** estratégia simples com **custos de transação** e teto de
   não-negociação (Milgrom-Stokey), reportando Sharpe e drawdown — não só acurácia.

## 4. Endpoint interativo (curto prazo)

Tornar retorno/volatilidade **função da data** informada (ou do dia corrente),
em vez de fixos, para o número do XGBoost variar de forma coerente por notícia.

## 5. Como isso entra na dissertação

- Script 04 (`Mestrado_PETR4/`) é onde o re-treino acontece; requer os CSVs
  completos (não versionados) e tempo de processamento.
- Cada rodada deve registrar features, split, sementes e métricas
  (reprodutibilidade — Apêndice B).
- **Entrega parcial já disponível:** a leitura setorial (regras) tem acurácia
  medida por `site/backend/avaliar_regras.py` (conjunto rotulado), servindo de
  camada interpretável e auditável ao lado do modelo estatístico.

## 6. Próximos passos sugeridos (posso executar sob demanda)

- [ ] Implementar o *feature set* enriquecido + baselines + walk-forward no Script 04.
- [ ] Introduzir *dead-band*/3 classes e reavaliar.
- [ ] Comparação FinBERT × BERTimbau com testes pareados.
- [ ] Endpoint interativo com contexto por data.
- [ ] Ampliar o conjunto rotulado da leitura setorial (mais casos independentes)
      para medir generalização de forma mais robusta.
