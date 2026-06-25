# -*- coding: utf-8 -*-
# ==============================================================================
#   DISSERTAÇÃO PETR4 — Etapa 10: Previsão de volatilidade por regressão
#   quantílica com pesos variáveis (inspirado em Silva, 2018)
#   Autor: Vanderlei Barbosa da Silva | Orientador: Prof. Dr. Julio Cesar Nievola
#
#   Objetivo: verificar se o sentimento contribui para a previsão da volatilidade
#   quando se substitui a regressão linear por uma COMBINAÇÃO DE QUANTIS com pesos
#   inversos ao erro de validação, como em Silva (2018), em vez da adição linear
#   simples (que, como já mostrado, não traz ganho fora da amostra).
#
#   Modelo base: HAR (Corsi, 2009) — volatilidade realizada explicada por suas
#   médias de 1, 5 e 22 dias. Aumentado com a intensidade do sentimento.
#
#   Comparações (alvo = volatilidade realizada RV_t = |retorno_t|), todas
#   avaliadas FORA DA AMOSTRA (split cronológico 60/15/25; pesos estimados na
#   validação; teste consultado uma vez):
#     B0 = HAR linear (sem sentimento)            -> referência
#     B1 = HAR linear + sentimento
#     Q0 = HAR quantílico com pesos (sem sentimento)
#     Q1 = HAR quantílico com pesos + sentimento
#   Métrica: R2 fora da amostra (vs B0) e vs média histórica.
#
#   Saídas: Mestrado_PETR4/resultados_vol_quantilica_petr4.json e figura.
# ==============================================================================

import json, warnings
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")
RAIZ = Path(__file__).resolve().parents[2]
PASTA = RAIZ / "Mestrado_PETR4"
FIG = RAIZ / "Exame_qualificacao" / "PesquisaMestrado_Qualificacao" / "figuras"

import statsmodels.api as sm
from statsmodels.regression.quantile_regression import QuantReg

plt.rcParams.update({"figure.dpi": 150, "font.size": 11,
                     "axes.spines.top": False, "axes.spines.right": False})
AZUL = "#0b5394"; VERDE = "#1a7f37"; VERM = "#b42318"; CINZA = "#5a6b7b"

# ── Dados e atributos HAR ─────────────────────────────────────────────────────
df = pd.read_csv(PASTA / "base_master_petr4.csv", parse_dates=["Date"]).sort_values("Date")
df["RV"] = df["Log_Retorno_Pct"].abs()                       # volatilidade realizada
df["RV1"] = df["RV"].shift(1)
df["RV5"] = df["RV"].rolling(5).mean().shift(1)
df["RV22"] = df["RV"].rolling(22).mean().shift(1)
df["SENT"] = df["Sentimento_Ontem"].abs()                    # intensidade do sentimento
df = df.dropna(subset=["RV", "RV1", "RV5", "RV22", "SENT"]).reset_index(drop=True)
n = len(df); i_tr, i_va = int(n * 0.60), int(n * 0.75)
tr, va, te = df.iloc[:i_tr], df.iloc[i_tr:i_va], df.iloc[i_va:]
BASE = ["RV1", "RV5", "RV22"]
QS = [0.10, 0.30, 0.50, 0.70, 0.90]

def sse(y, p): return float(np.sum((np.asarray(y) - np.asarray(p)) ** 2))
def mae(y, p): return float(np.mean(np.abs(np.asarray(y) - np.asarray(p))))

def ols_pred(cols):
    m = sm.OLS(tr["RV"], sm.add_constant(tr[cols])).fit()
    return m.predict(sm.add_constant(te[cols], has_constant="add")).values

def quantil_pred(cols):
    # ajusta um quantil de cada vez; pesos = inverso do MAE na validacao
    preds_va, preds_te, errs = {}, {}, {}
    Xtr = sm.add_constant(tr[cols])
    for q in QS:
        m = QuantReg(tr["RV"], Xtr).fit(q=q)
        pva = m.predict(sm.add_constant(va[cols], has_constant="add")).values
        pte = m.predict(sm.add_constant(te[cols], has_constant="add")).values
        preds_va[q], preds_te[q] = pva, pte
        errs[q] = mae(va["RV"], pva)
    inv = np.array([1.0 / errs[q] for q in QS]); w = inv / inv.sum()   # pesos variaveis
    comb_var = sum(w[i] * preds_te[q] for i, q in enumerate(QS))
    comb_eq = np.mean([preds_te[q] for q in QS], axis=0)               # pesos iguais
    return comb_var, comb_eq, dict(zip([str(q) for q in QS], np.round(w, 3)))

y_te = te["RV"].values
# referencias
p_B0 = ols_pred(BASE)
p_B1 = ols_pred(BASE + ["SENT"])
q0_var, q0_eq, _ = quantil_pred(BASE)
q1_var, q1_eq, w1 = quantil_pred(BASE + ["SENT"])
media_hist = np.full_like(y_te, tr["RV"].mean(), dtype=float)

sse_B0 = sse(y_te, p_B0)
def r2os(p, ref_sse): return round((1 - sse(y_te, p) / ref_sse) * 100, 2)

res = {
    "n": int(n), "n_teste": int(len(te)), "quantis": QS, "pesos_Q1_variaveis": w1,
    "MAE": {"B0_HAR": round(mae(y_te, p_B0), 4), "B1_HAR_sent": round(mae(y_te, p_B1), 4),
            "Q0_quantil_pesos": round(mae(y_te, q0_var), 4),
            "Q1_quantil_pesos_sent": round(mae(y_te, q1_var), 4),
            "media_historica": round(mae(y_te, media_hist), 4)},
    "R2_OS_vs_B0_pct": {"B1_HAR_sent": r2os(p_B1, sse_B0),
                        "Q0_quantil_pesos": r2os(q0_var, sse_B0),
                        "Q1_quantil_pesos_sent": r2os(q1_var, sse_B0),
                        "Q1_pesos_iguais_sent": r2os(q1_eq, sse_B0)},
    "R2_OS_vs_media_hist_pct": {
        "B0_HAR": r2os(p_B0, sse(y_te, media_hist)),
        "Q1_quantil_pesos_sent": r2os(q1_var, sse(y_te, media_hist))},
}
# ganho do sentimento DENTRO do arcabouco quantilico (Q1 vs Q0)
res["ganho_sentimento_no_quantil_pct"] = round((1 - sse(y_te, q1_var) / sse(y_te, q0_var)) * 100, 2)

with open(PASTA / "resultados_vol_quantilica_petr4.json", "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=2)

print("=== Previsão de volatilidade: HAR linear vs HAR quantílico com pesos ===")
print("MAE (fora da amostra):")
for k, v in res["MAE"].items(): print(f"  {k:24s}: {v}")
print("\nR2 fora da amostra vs B0 (HAR sem sentimento):")
for k, v in res["R2_OS_vs_B0_pct"].items(): print(f"  {k:24s}: {v:+.2f}%")
print(f"\nGanho do sentimento dentro do arcabouço quantílico (Q1 vs Q0): {res['ganho_sentimento_no_quantil_pct']:+.2f}%")
print(f"Pesos variáveis de Q1: {w1}")

# ── Figura: R2-OS dos modelos vs baseline HAR ─────────────────────────────────
nomes = ["HAR + sent.\n(linear)", "Quantílico\n(sem sent.)", "Quantílico\n+ sent. (pesos)"]
vals = [res["R2_OS_vs_B0_pct"]["B1_HAR_sent"], res["R2_OS_vs_B0_pct"]["Q0_quantil_pesos"],
        res["R2_OS_vs_B0_pct"]["Q1_quantil_pesos_sent"]]
fig, ax = plt.subplots(figsize=(6.5, 3.8))
cores = [VERM if v < 0 else VERDE for v in vals]
ax.bar(nomes, vals, color=cores)
ax.axhline(0, color=CINZA, lw=1)
ax.set_ylabel("$R^2$ fora da amostra vs HAR (\\%)")
for i, v in enumerate(vals):
    ax.text(i, v + (0.1 if v >= 0 else -0.3), f"{v:+.1f}", ha="center", fontsize=9)
fig.savefig(FIG / "fig_vol_quantilica.png", bbox_inches="tight"); plt.close(fig)
print("\n[OK] figura fig_vol_quantilica.png e métricas salvas.")
