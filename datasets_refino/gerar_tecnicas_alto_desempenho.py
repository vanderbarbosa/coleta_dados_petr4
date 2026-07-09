# -*- coding: utf-8 -*-
# Item da banca: "procure nas referências o que obteve MAIOR desempenho para
# replicarmos ao nosso (data fusion)". Extrai da RSL (04_...) as técnicas de alto
# desempenho e o que é replicável ao nosso modelo. Fonte: PDFs/Cap.2 (sourced).
from pathlib import Path
import csv
OUT = Path(__file__).resolve().parents[1] / "datasets_refino"

# (estudo, tecnica_de_alto_desempenho, desempenho_reportado, replicavel_no_nosso, como_replicamos)
T = [
 ("Barak et al. (2017)", "FUSÃO/ENSEMBLE de classificadores diversos (Bagging/Boosting/AdaBoost) + meta-classificador (stacking)",
  "Até 83,6% (retorno) e 88,2% (risco) — dataset próprio", "SIM — é o núcleo de um data fusion",
  "Stacking de RF+XGBoost+SVM com meta-classificador (LogisticRegression)"),
 ("Nobre e Neves (2019)", "XGBoost + redução de dimensão (PCA) + denoise (Wavelet) + OTIMIZAÇÃO de hiperparâmetros (algoritmo genético MOO-GA)",
  "Sinal de negociação lucrativo", "SIM (parcial)", "Tuning de hiperparâmetros do XGBoost/RF por busca em grade na validação; seleção de atributos"),
 ("Ballings et al. (2015)", "ENSEMBLES (Random Forest/AdaBoost/Kernel Factory) superam classificadores únicos; métrica AUC",
  "RF é o melhor entre os testados", "SIM", "Incluir RF e reportar AUC além da acurácia"),
 ("Nguyen et al. (2015)", "Sentimento por TÓPICO (TSLDA) em vez de sentimento único",
  "+6,07% de acurácia sobre modelo só-preços", "SIM — já temos ISM por categoria",
  "Feature set com os 7 ISM por categoria (ISM_CATx_L1)"),
 ("Oliveira et al. (2017)", "Validação rigorosa com JANELAS DESLIZANTES + testes formais de comparação de previsão",
  "Valor preditivo p/ retorno, VOLATILIDADE e volume", "SIM", "Walk-forward + teste binomial e comparação com baseline"),
 ("Hagenau et al. (2013)", "SELEÇÃO robusta de atributos + feedback de mercado; features sensíveis a contexto",
  "Acurácia significativamente acima de abordagens anteriores", "SIM (parcial)", "Seleção de atributos por importância (top-k)"),
 ("Li et al. (2020)", "FUSÃO sequencial de preços (indicadores técnicos) + sentimento de notícias em deep learning",
  "Fusão melhora a previsão (Hong Kong)", "PARCIAL", "Nosso data fusion já concatena preço+risco+sentimento; deep sequencial fica como trabalho futuro"),
 ("Silva (2018)", "Regressão QUANTÍLICA + GARCH para o efeito assimétrico e a VOLATILIDADE",
  "Efeito assimétrico do sentimento; prevê volatilidade", "SIM — já aplicado",
  "Já replicado (quantílica τ=0,05 +261bps; Granger sent→vol p<0,001)"),
]
CAB = ["Estudo", "Tecnica_de_alto_desempenho", "Desempenho_reportado", "Replicavel", "Como_replicamos_no_data_fusion"]
with open(OUT / "05_tecnicas_alto_desempenho_rsl_v1.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(CAB)
    for row in T:
        w.writerow(row)
print("✓ 05_tecnicas_alto_desempenho_rsl_v1.csv:", len(T), "técnicas.")
print("  Núcleo replicável: STACKING (Barak) + TUNING (Nobre) + ISM por categoria (Nguyen) + RF/AUC (Ballings) + walk-forward (Oliveira).")
