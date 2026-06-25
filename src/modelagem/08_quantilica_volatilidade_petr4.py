# -*- coding: utf-8 -*-
# ==============================================================================
#   DISSERTAÇÃO PETR4 — Etapa 8: Análises econométricas inspiradas em Silva (2018)
#   Autor: Vanderlei Barbosa da Silva | Orientador: Prof. Dr. Julio Cesar Nievola
#
#   (A) REGRESSÃO QUANTÍLICA do log-retorno sobre o sentimento defasado, ao longo
#       dos quantis (0,05 a 0,95), para detectar efeito ASSIMÉTRICO nas caudas
#       (Koenker e Bassett, 1978). Efeito reportado em pontos-base.
#   (B) PREVISÃO DE VOLATILIDADE com sentimento: compara um modelo de referência
#       (volatilidade defasada) com um modelo aumentado (+ sentimento defasado),
#       medindo a redução do erro de previsão FORA DA AMOSTRA (MAE, RMSE, R2-OS).
#   (C) CONDICIONAMENTO POR INCERTEZA: efeito do sentimento sobre o retorno em
#       regimes de alta vs baixa incerteza (proxy: topo 25% da volatilidade).
#
#   Saídas: figuras em PesquisaMestrado_Qualificacao/figuras/ e métricas em
#   Mestrado_PETR4/ (resultados_quantilica, resultados_vol_sentimento).
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
AZUL = "#0b5394"; AZULC = "#2c7bb6"; VERM = "#b42318"; CINZA = "#5a6b7b"; VERDE = "#1a7f37"

df = pd.read_csv(PASTA / "base_master_petr4.csv", parse_dates=["Date"]).sort_values("Date")
df = df.dropna(subset=["Log_Retorno_Pct", "Retorno_Ontem", "Volatilidade_Ontem", "Sentimento_Ontem"]).reset_index(drop=True)
# unidades: Log_Retorno_Pct está em % ; 1% = 100 pontos-base (bps)
y = df["Log_Retorno_Pct"].values                       # retorno de hoje (%)
X = df[["Retorno_Ontem", "Volatilidade_Ontem", "Sentimento_Ontem"]].copy()
Xc = sm.add_constant(X)

# ──────────────────────────────────────────────────────────────────────────────
# (A) Regressão quantílica: efeito do sentimento por quantil do retorno
# ──────────────────────────────────────────────────────────────────────────────
print("=== (A) Regressão quantílica do retorno sobre o sentimento defasado ===")
taus = [0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95]
linhas = []
for t in taus:
    res = QuantReg(y, Xc).fit(q=t)
    coef = res.params["Sentimento_Ontem"]              # % por unidade de ISM
    se = res.bse["Sentimento_Ontem"]
    p = res.pvalues["Sentimento_Ontem"]
    linhas.append({"quantil": t, "coef_bps": round(coef * 100, 2),       # % -> bps
                   "ic_inf_bps": round((coef - 1.96 * se) * 100, 2),
                   "ic_sup_bps": round((coef + 1.96 * se) * 100, 2),
                   "p_valor": round(p, 4)})
    print(f"  tau={t:.2f}: sentimento = {coef*100:+7.2f} bps (p={p:.3f})")
qr = pd.DataFrame(linhas)
qr.to_csv(PASTA / "resultados_quantilica_petr4.csv", index=False)

# OLS (efeito médio) para comparação
ols = sm.OLS(y, Xc).fit()
ols_coef_bps = ols.params["Sentimento_Ontem"] * 100
ols_p = ols.pvalues["Sentimento_Ontem"]
print(f"  OLS (média): sentimento = {ols_coef_bps:+.2f} bps (p={ols_p:.3f})")
sd_ism = float(df["Sentimento_Ontem"].std())
print(f"  desvio-padrão do ISM defasado = {sd_ism:.3f}")
print(f"  efeito por 1 DP do ISM: tau=0,05 -> {qr.loc[qr.quantil==0.05,'coef_bps'].iloc[0]*sd_ism:+.1f} bps ; "
      f"tau=0,50 -> {qr.loc[qr.quantil==0.50,'coef_bps'].iloc[0]*sd_ism:+.1f} bps")
qr.attrs["sd_ism"] = sd_ism

# Figura: coeficiente do sentimento por quantil, com banda de confiança e linha OLS
fig, ax = plt.subplots(figsize=(7.5, 4.0))
ax.plot(qr["quantil"], qr["coef_bps"], "o-", color=AZUL, lw=1.8, label="Efeito por quantil")
ax.fill_between(qr["quantil"], qr["ic_inf_bps"], qr["ic_sup_bps"], color=AZULC, alpha=0.2, label="IC 95%")
ax.axhline(ols_coef_bps, color=VERM, ls="--", lw=1.3, label=f"Efeito médio (OLS) = {ols_coef_bps:.1f} bps")
ax.axhline(0, color=CINZA, lw=0.8)
ax.set_xlabel("Quantil do retorno"); ax.set_ylabel("Efeito do sentimento (pontos-base)")
ax.legend(fontsize=8)
fig.savefig(FIG / "fig_quantilica.png", bbox_inches="tight"); plt.close(fig)

# ──────────────────────────────────────────────────────────────────────────────
# (B) Previsão de volatilidade com sentimento (redução do erro fora da amostra)
# ──────────────────────────────────────────────────────────────────────────────
print("\n=== (B) Previsão de volatilidade: referência vs aumentado com sentimento ===")
df["RV"] = df["Log_Retorno_Pct"].abs()                 # proxy de volatilidade realizada
df["RV_Ontem"] = df["Retorno_Ontem"].abs()             # vol. realizada de ontem (AR simples)
df["Sent_Abs_Ontem"] = df["Sentimento_Ontem"].abs()    # INTENSIDADE do sentimento (não o sinal)
d = df.dropna(subset=["RV", "RV_Ontem", "Volatilidade_Ontem", "Sent_Abs_Ontem"]).reset_index(drop=True)
n = len(d); corte = int(n * 0.75)                       # split cronológico 75/25

def oos(cols):
    Xtr = sm.add_constant(d.loc[:corte-1, cols]); ytr = d.loc[:corte-1, "RV"]
    m = sm.OLS(ytr, Xtr).fit()
    Xte = sm.add_constant(d.loc[corte:, cols], has_constant="add"); yte = d.loc[corte:, "RV"]
    err = yte.values - m.predict(Xte).values
    return float(np.mean(np.abs(err))), float(np.sqrt(np.mean(err**2))), float(np.sum(err**2))

# Dois baselines: (1) autorregressivo simples (estilo Silva) e (2) GARCH (forte)
cenarios = {
    "AR_simples": (["RV_Ontem"], ["RV_Ontem", "Sent_Abs_Ontem"]),
    "GARCH": (["Volatilidade_Ontem"], ["Volatilidade_Ontem", "Sent_Abs_Ontem"]),
}
vol = {"n": int(n), "n_treino": int(corte), "n_teste": int(n - corte)}
for nome, (cb, ca) in cenarios.items():
    mae_b, rmse_b, sse_b = oos(cb)
    mae_a, rmse_a, sse_a = oos(ca)
    vol[nome] = {
        "MAE_ref": round(mae_b, 4), "MAE_aug": round(mae_a, 4),
        "RMSE_ref": round(rmse_b, 4), "RMSE_aug": round(rmse_a, 4),
        "reducao_MAE_pct": round((mae_b - mae_a) / mae_b * 100, 2),
        "R2_fora_amostra_pct": round((1.0 - sse_a / sse_b) * 100, 2),
    }
    print(f"  baseline {nome:11s}: MAE {mae_b:.3f}->{mae_a:.3f} | R2-OS = {vol[nome]['R2_fora_amostra_pct']:+.2f}%")

# significância da intensidade do sentimento (in-sample), controlando pela volatilidade GARCH
m_full = sm.OLS(d["RV"], sm.add_constant(d[["Volatilidade_Ontem", "Sent_Abs_Ontem"]])).fit()
vol["coef_sent_abs_insample"] = round(m_full.params["Sent_Abs_Ontem"], 4)
vol["p_sent_abs_insample"] = round(m_full.pvalues["Sent_Abs_Ontem"], 4)
print(f"  in-sample: |sentimento| coef={vol['coef_sent_abs_insample']:+.3f} (p={vol['p_sent_abs_insample']:.4f})")
with open(PASTA / "resultados_vol_sentimento_petr4.json", "w", encoding="utf-8") as f:
    json.dump(vol, f, ensure_ascii=False, indent=2)

# ──────────────────────────────────────────────────────────────────────────────
# (C) Condicionamento por incerteza (alta = topo 25% da volatilidade)
# ──────────────────────────────────────────────────────────────────────────────
print("\n=== (C) Efeito do sentimento sobre o retorno por regime de incerteza ===")
lim = df["Volatilidade_Ontem"].quantile(0.75)
reg = {}
for nome, mask in [("baixa_incerteza", df["Volatilidade_Ontem"] < lim),
                   ("alta_incerteza", df["Volatilidade_Ontem"] >= lim)]:
    sub = df[mask]
    mm = sm.OLS(sub["Log_Retorno_Pct"], sm.add_constant(sub[["Retorno_Ontem", "Volatilidade_Ontem", "Sentimento_Ontem"]])).fit()
    reg[nome] = {"n": int(len(sub)), "coef_sent_bps": round(mm.params["Sentimento_Ontem"]*100, 2),
                 "p_valor": round(mm.pvalues["Sentimento_Ontem"], 4)}
    print(f"  {nome}: n={len(sub)}  sentimento={reg[nome]['coef_sent_bps']:+.2f} bps (p={reg[nome]['p_valor']:.3f})")
with open(PASTA / "resultados_regime_incerteza_petr4.json", "w", encoding="utf-8") as f:
    json.dump(reg, f, ensure_ascii=False, indent=2)

print("\n[OK] Figuras: fig_quantilica.png | métricas salvas.")
