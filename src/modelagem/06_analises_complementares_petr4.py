# -*- coding: utf-8 -*-
# ==============================================================================
#   DISSERTAÇÃO PETR4 — Etapa 6: Análises complementares (fechamento de gaps)
#   Autor: Vanderlei Barbosa da Silva | Orientador: Prof. Dr. Julio Cesar Nievola
#
#   Reúne quatro análises que eliminam lacunas apontáveis pela banca:
#     (A) ISM PONDERADO — variantes de construção do índice de sentimento
#         (média simples, ponderado por confiança, saldo/voto) e seu efeito
#         na previsão de direção.
#     (B) BASELINE e SIGNIFICÂNCIA — classe majoritária, teste binomial vs 50%
#         e teste de McNemar (Data Fusion vs apenas preços).
#     (C) CAUSALIDADE DE GRANGER — sentimento(t-1..k) → retorno e → volatilidade,
#         fundamentando empiricamente a hipótese Lead-Lag.
#     (D) AVALIAÇÃO DA VOLATILIDADE — qualidade da previsão do GARCH contra a
#         volatilidade realizada (Mincer-Zarnowitz, MAE, RMSE, QLIKE).
#
#   Saídas (Mestrado_PETR4/):
#     - resultados_ism_ponderado_petr4.csv
#     - resultados_significancia_petr4.json
#     - resultados_granger_petr4.csv
#     - resultados_volatilidade_petr4.json
# ==============================================================================

import json, warnings
from pathlib import Path
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
RAIZ = Path(__file__).resolve().parents[2]
PASTA = RAIZ / "Mestrado_PETR4"
RNG = 42
np.random.seed(RNG)

from sklearn.metrics import accuracy_score, roc_auc_score
from xgboost import XGBClassifier
from scipy.stats import binomtest
from statsmodels.stats.contingency_tables import mcnemar
from statsmodels.tsa.stattools import grangercausalitytests
import statsmodels.api as sm

POL = {"Positive": 1, "Negative": -1, "Neutral": 0}

def xgb():
    return XGBClassifier(n_estimators=300, max_depth=3, learning_rate=0.05, subsample=0.9,
                         colsample_bytree=0.9, eval_metric="logloss", random_state=RNG, n_jobs=4)

def split3(df):
    n = len(df); a, b = int(n*0.60), int(n*0.75)
    return df.iloc[:a], df.iloc[a:b], df.iloc[b:]

# ──────────────────────────────────────────────────────────────────────────────
# Carga
# ──────────────────────────────────────────────────────────────────────────────
master = pd.read_csv(PASTA / "base_master_petr4.csv", parse_dates=["Date"]).sort_values("Date")
news = pd.read_csv(PASTA / "noticias_com_sentimento.csv")
news["pol"] = news["Label_Sentimento"].map(POL)
news["conf"] = news["Score_Confianca"].astype(float)
news["idx"] = news["Indice_Sentimento"].astype(float)
news["dia"] = pd.to_datetime(news["Data_Ajustada"], errors="coerce")
news = news.dropna(subset=["dia", "pol"])

# ──────────────────────────────────────────────────────────────────────────────
# (A) ISM PONDERADO — variantes de construção do índice
# ──────────────────────────────────────────────────────────────────────────────
def construir_variantes_ism(g):
    n = len(g)
    pos = (g["pol"] == 1).sum(); neg = (g["pol"] == -1).sum()
    soma_conf = g["conf"].sum()
    return pd.Series({
        # 1) simples: média dos índices (cada item = polaridade x confiança) — ATUAL
        "ISM_simples":   g["idx"].mean(),
        # 2) ponderado por confiança: média de polaridade PONDERADA pela confiança
        "ISM_confianca": (g["conf"] * g["pol"]).sum() / soma_conf if soma_conf > 0 else 0.0,
        # 3) saldo/voto: (positivas - negativas) / total  (ignora a confiança)
        "ISM_saldo":     (pos - neg) / n if n > 0 else 0.0,
    })

ism = news.groupby("dia").apply(construir_variantes_ism).reset_index().rename(columns={"dia": "Date"})

base = master[["Date", "Retorno_Ontem", "Volatilidade_Ontem", "Alvo"]].merge(ism, on="Date", how="left")
for c in ["ISM_simples", "ISM_confianca", "ISM_saldo"]:
    base[c + "_L1"] = base[c].shift(1)
base = base.dropna(subset=["Retorno_Ontem", "Volatilidade_Ontem", "Alvo"]).fillna(0.0).reset_index(drop=True)

corr = base[["ISM_simples", "ISM_confianca", "ISM_saldo"]].corr().round(3)

res_ism = []
tr, va, te = split3(base)
for var in ["(sem sentimento)", "ISM_simples", "ISM_confianca", "ISM_saldo"]:
    feats = ["Retorno_Ontem", "Volatilidade_Ontem"] + ([] if var == "(sem sentimento)" else [var + "_L1"])
    m = xgb().fit(tr[feats].values, tr["Alvo"].values)
    p = m.predict_proba(te[feats].values)[:, 1]
    acc = accuracy_score(te["Alvo"], (p >= 0.5).astype(int)) * 100
    auc = roc_auc_score(te["Alvo"], p)
    res_ism.append({"Variante_ISM": var, "Acc_teste": round(acc, 2), "AUC_teste": round(auc, 4)})

pd.DataFrame(res_ism).to_csv(PASTA / "resultados_ism_ponderado_petr4.csv", index=False)
print("=== (A) ISM ponderado — efeito na previsão de direção ===")
print(pd.DataFrame(res_ism).to_string(index=False))
print("\nCorrelação entre variantes do ISM:\n", corr.to_string())

# ──────────────────────────────────────────────────────────────────────────────
# (B) BASELINE e SIGNIFICÂNCIA
# ──────────────────────────────────────────────────────────────────────────────
b = base.copy()
trb, vab, teb = split3(b)
classe_maj = int(trb["Alvo"].mode().iloc[0])
acc_maj = (teb["Alvo"] == classe_maj).mean() * 100

# modelos: apenas preços vs Data Fusion (ISM_simples)
f_prec = ["Retorno_Ontem", "Volatilidade_Ontem"]
f_fus = f_prec + ["ISM_simples_L1"]
m_prec = xgb().fit(trb[f_prec].values, trb["Alvo"].values)
m_fus = xgb().fit(trb[f_fus].values, trb["Alvo"].values)
pred_prec = m_prec.predict(teb[f_prec].values)
pred_fus = m_fus.predict(teb[f_fus].values)
y = teb["Alvo"].values
acc_prec = accuracy_score(y, pred_prec) * 100
acc_fus = accuracy_score(y, pred_fus) * 100

# binomial: Data Fusion supera o acaso (50%)?
n_te = len(y); acertos_fus = int((pred_fus == y).sum())
p_binom = binomtest(acertos_fus, n_te, 0.5, alternative="greater").pvalue

# McNemar: Data Fusion difere de apenas preços?
b01 = int(((pred_prec == y) & (pred_fus != y)).sum())   # preços acerta, fusion erra
b10 = int(((pred_prec != y) & (pred_fus == y)).sum())   # fusion acerta, preços erra
tab = [[0, b01], [b10, 0]]
p_mcnemar = float(mcnemar(tab, exact=True).pvalue)

sig = {"n_teste": n_te, "classe_majoritaria": classe_maj, "acc_classe_majoritaria": round(acc_maj, 2),
       "acc_apenas_precos": round(acc_prec, 2), "acc_data_fusion": round(acc_fus, 2),
       "acertos_fusion": acertos_fus, "p_binomial_vs_50": round(p_binom, 4),
       "mcnemar_precos_acerta_fusion_erra": b01, "mcnemar_fusion_acerta_precos_erra": b10,
       "p_mcnemar_fusion_vs_precos": round(p_mcnemar, 4)}
with open(PASTA / "resultados_significancia_petr4.json", "w", encoding="utf-8") as f:
    json.dump(sig, f, ensure_ascii=False, indent=2)
print("\n=== (B) Baseline e significância ===")
for k, v in sig.items():
    print(f"  {k}: {v}")

# ──────────────────────────────────────────────────────────────────────────────
# (C) CAUSALIDADE DE GRANGER  (sentimento -> retorno e -> volatilidade)
# ──────────────────────────────────────────────────────────────────────────────
g = master.merge(ism[["Date", "ISM_simples"]], on="Date", how="left").copy()
g["ISM_simples"] = g["ISM_simples"].fillna(0.0)
g = g.dropna(subset=["Log_Retorno_Pct", "Volatilidade_GARCH"]).reset_index(drop=True)

def granger_pvals(causa, efeito, maxlag=5):
    dados = g[[efeito, causa]].dropna()      # ordem: [efeito, causa] => causa -> efeito
    out = grangercausalitytests(dados, maxlag=maxlag, verbose=False)
    return {lag: round(out[lag][0]["ssr_ftest"][1], 4) for lag in range(1, maxlag + 1)}

gr_ret = granger_pvals("ISM_simples", "Log_Retorno_Pct")
gr_vol = granger_pvals("ISM_simples", "Volatilidade_GARCH")
linhas_gr = []
for lag in gr_ret:
    linhas_gr.append({"Defasagem_dias": lag, "p_sent_para_retorno": gr_ret[lag],
                      "p_sent_para_volatilidade": gr_vol[lag]})
pd.DataFrame(linhas_gr).to_csv(PASTA / "resultados_granger_petr4.csv", index=False)
print("\n=== (C) Causalidade de Granger (p-valores; <0,05 = causalidade preditiva) ===")
print(pd.DataFrame(linhas_gr).to_string(index=False))

# ──────────────────────────────────────────────────────────────────────────────
# (D) AVALIAÇÃO DA VOLATILIDADE (GARCH vs realizada)
#     Proxy de volatilidade realizada: |retorno| (em pontos percentuais).
# ──────────────────────────────────────────────────────────────────────────────
v = master.dropna(subset=["Log_Retorno_Pct", "Volatilidade_GARCH"]).copy()
v["vol_realizada"] = v["Log_Retorno_Pct"].abs()
prev = v["Volatilidade_GARCH"].values          # previsão (desvio condicional, %)
real = v["vol_realizada"].values               # realizado |retorno| (%)
mae = float(np.mean(np.abs(prev - real)))
rmse = float(np.sqrt(np.mean((prev - real) ** 2)))
# QLIKE (sobre variâncias): real2/prev2 - ln(real2/prev2) - 1
real2 = np.maximum(real ** 2, 1e-8); prev2 = np.maximum(prev ** 2, 1e-8)
qlike = float(np.mean(real2 / prev2 - np.log(real2 / prev2) - 1))
# Mincer-Zarnowitz: realizada = a + b*prevista
X = sm.add_constant(prev); mz = sm.OLS(real, X).fit()
mz_a, mz_b = float(mz.params[0]), float(mz.params[1])
mz_r2 = float(mz.rsquared)
corr_vr = float(np.corrcoef(prev, real)[0, 1])
vol = {"n": int(len(v)), "MAE": round(mae, 4), "RMSE": round(rmse, 4), "QLIKE": round(qlike, 4),
       "MZ_intercepto_a": round(mz_a, 4), "MZ_coef_b": round(mz_b, 4), "MZ_R2": round(mz_r2, 4),
       "correlacao_prev_real": round(corr_vr, 4),
       "proxy": "volatilidade realizada = |retorno diário| (%)"}
with open(PASTA / "resultados_volatilidade_petr4.json", "w", encoding="utf-8") as f:
    json.dump(vol, f, ensure_ascii=False, indent=2)
print("\n=== (D) Avaliação da previsão de volatilidade (GARCH) ===")
for k, val in vol.items():
    print(f"  {k}: {val}")

print("\n[OK] Análises complementares concluídas.")
