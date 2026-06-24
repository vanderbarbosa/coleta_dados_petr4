# -*- coding: utf-8 -*-
# ==============================================================================
#   DISSERTAÇÃO PETR4 — Etapa 7: Análises finais (robustez, backtest, ROC)
#   Autor: Vanderlei Barbosa da Silva | Orientador: Prof. Dr. Julio Cesar Nievola
#
#   (A) Robustez por subperíodo: walk-forward por ano (treina no passado, testa
#       no ano), revelando estabilidade do sinal entre regimes (2020, 2022, ...).
#   (B) Backtest econômico: estratégia long/flat guiada pela previsão, com custos
#       de transação, comparada ao buy-and-hold.
#   (C) ROC e matriz de confusão do modelo Data Fusion no conjunto de teste.
#
#   Saídas: figuras em PesquisaMestrado_Qualificacao/figuras/ e métricas em
#   Mestrado_PETR4/ (resultados_subperiodo, resultados_backtest).
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
RNG = 42
np.random.seed(RNG)

from sklearn.metrics import accuracy_score, roc_curve, auc, confusion_matrix
from xgboost import XGBClassifier

plt.rcParams.update({"figure.dpi": 150, "font.size": 11,
                     "axes.spines.top": False, "axes.spines.right": False})
AZUL = "#0b5394"; AZULC = "#2c7bb6"; VERDE = "#1a7f37"; VERM = "#b42318"; CINZA = "#5a6b7b"

FEATS = ["Retorno_Ontem", "Volatilidade_Ontem", "Sentimento_Ontem"]

def xgb():
    return XGBClassifier(n_estimators=300, max_depth=3, learning_rate=0.05, subsample=0.9,
                         colsample_bytree=0.9, eval_metric="logloss", random_state=RNG, n_jobs=4)

df = pd.read_csv(PASTA / "base_master_petr4.csv", parse_dates=["Date"]).sort_values("Date")
df = df.dropna(subset=FEATS + ["Alvo", "Log_Retorno_Pct"]).reset_index(drop=True)
df["Ano"] = df["Date"].dt.year

# ──────────────────────────────────────────────────────────────────────────────
# (A) Robustez por subperíodo — walk-forward por ano
# ──────────────────────────────────────────────────────────────────────────────
anos = sorted(df["Ano"].unique())
linhas = []
for ano in anos:
    tr = df[df["Ano"] < ano]
    te = df[df["Ano"] == ano]
    if len(tr) < 250 or len(te) < 30:
        continue
    m = xgb().fit(tr[FEATS].values, tr["Alvo"].values)
    pred = m.predict(te[FEATS].values)
    acc = accuracy_score(te["Alvo"], pred) * 100
    maj = max(te["Alvo"].mean(), 1 - te["Alvo"].mean()) * 100
    linhas.append({"Ano": ano, "Pregoes": len(te), "Acc_modelo": round(acc, 2),
                   "Acc_classe_majoritaria": round(maj, 2), "Altas_pct": round(te["Alvo"].mean()*100, 1)})
sub = pd.DataFrame(linhas)
sub.to_csv(PASTA / "resultados_subperiodo_petr4.csv", index=False)
print("=== (A) Robustez por subperíodo (walk-forward por ano) ===")
print(sub.to_string(index=False))

fig, ax = plt.subplots(figsize=(7.5, 3.6))
x = sub["Ano"].astype(str)
ax.bar(x, sub["Acc_modelo"], color=AZUL, label="Modelo Data Fusion")
ax.plot(x, sub["Acc_classe_majoritaria"], "o--", color=VERM, label="Classe majoritária")
ax.axhline(50, color=CINZA, lw=0.8, ls=":")
ax.set_ylabel("Acurácia (%)"); ax.set_ylim(40, 70); ax.legend(fontsize=8)
for i, v in enumerate(sub["Acc_modelo"]):
    ax.text(i, v + 0.5, f"{v:.0f}", ha="center", fontsize=8)
fig.savefig(FIG / "fig_subperiodo.png", bbox_inches="tight"); plt.close(fig)

# ──────────────────────────────────────────────────────────────────────────────
# Modelo no split cronológico 60/15/25 para backtest, ROC e matriz de confusão.
# Treina apenas nos 60% (mesmo protocolo do resultado principal da Tabela 4.x,
# que reporta 54,5%) e testa nos 25% mais recentes, para manter consistência.
# ──────────────────────────────────────────────────────────────────────────────
n = len(df); i_tr = int(n * 0.60); i_va = int(n * 0.75)
tr = df.iloc[:i_tr]; te = df.iloc[i_va:].copy()
m = xgb().fit(tr[FEATS].values, tr["Alvo"].values)
prob = m.predict_proba(te[FEATS].values)[:, 1]
pred = (prob >= 0.5).astype(int)
y = te["Alvo"].values

# ──────────────────────────────────────────────────────────────────────────────
# (B) Backtest econômico — long/flat com custos
# ──────────────────────────────────────────────────────────────────────────────
ret = te["Log_Retorno_Pct"].values / 100.0          # retorno diário em fração
pos = pred.astype(float)                              # 1 = comprado, 0 = fora
custo_bps = 10.0                                      # 10 bps por troca de posição (ida)
custo = (custo_bps / 1e4) * np.abs(np.diff(np.concatenate([[0], pos])))
estrategia = pos * ret - custo
buyhold = ret
def cresc(r): return np.cumprod(1 + r)
cum_e, cum_b = cresc(estrategia), cresc(buyhold)
def sharpe(r): return float(np.mean(r) / (np.std(r) + 1e-12) * np.sqrt(252))
bt = {
    "n_pregoes": int(len(te)),
    "periodo": [str(te["Date"].iloc[0].date()), str(te["Date"].iloc[-1].date())],
    "custo_bps_por_troca": custo_bps,
    "retorno_total_estrategia_pct": round((cum_e[-1] - 1) * 100, 2),
    "retorno_total_buyhold_pct": round((cum_b[-1] - 1) * 100, 2),
    "sharpe_estrategia": round(sharpe(estrategia), 3),
    "sharpe_buyhold": round(sharpe(buyhold), 3),
    "num_trocas_posicao": int(np.sum(np.abs(np.diff(np.concatenate([[0], pos]))))),
    "dias_comprado_pct": round(pos.mean() * 100, 1),
}
with open(PASTA / "resultados_backtest_petr4.json", "w", encoding="utf-8") as f:
    json.dump(bt, f, ensure_ascii=False, indent=2)
print("\n=== (B) Backtest econômico (long/flat, custo 10 bps/troca) ===")
for k, v in bt.items(): print(f"  {k}: {v}")

fig, ax = plt.subplots(figsize=(8, 3.6))
ax.plot(te["Date"], (cum_e - 1) * 100, color=AZUL, lw=1.4, label="Estratégia (sentimento)")
ax.plot(te["Date"], (cum_b - 1) * 100, color=CINZA, lw=1.4, ls="--", label="Buy-and-hold")
ax.axhline(0, color=CINZA, lw=0.6)
ax.set_ylabel("Retorno acumulado (%)"); ax.set_xlabel("Período de teste"); ax.legend(fontsize=8)
fig.savefig(FIG / "fig_backtest.png", bbox_inches="tight"); plt.close(fig)

# ──────────────────────────────────────────────────────────────────────────────
# (C) Curva ROC e matriz de confusão
# ──────────────────────────────────────────────────────────────────────────────
fpr, tpr, _ = roc_curve(y, prob); auc_v = auc(fpr, tpr)
fig, ax = plt.subplots(figsize=(4.6, 4.2))
ax.plot(fpr, tpr, color=AZUL, lw=2, label=f"Data Fusion (AUC = {auc_v:.3f})")
ax.plot([0, 1], [0, 1], color=CINZA, lw=1, ls="--", label="Acaso")
ax.set_xlabel("Taxa de falsos positivos"); ax.set_ylabel("Taxa de verdadeiros positivos")
ax.legend(fontsize=8, loc="lower right")
fig.savefig(FIG / "fig_roc.png", bbox_inches="tight"); plt.close(fig)

cm = confusion_matrix(y, pred)
fig, ax = plt.subplots(figsize=(4.2, 3.8))
im = ax.imshow(cm, cmap="Blues")
ax.set_xticks([0, 1]); ax.set_xticklabels(["Baixa", "Alta"])
ax.set_yticks([0, 1]); ax.set_yticklabels(["Baixa", "Alta"])
ax.set_xlabel("Previsto"); ax.set_ylabel("Real")
for i in range(2):
    for j in range(2):
        ax.text(j, i, str(cm[i, j]), ha="center", va="center",
                color="white" if cm[i, j] > cm.max()/2 else "black", fontsize=13)
fig.savefig(FIG / "fig_matriz_confusao.png", bbox_inches="tight"); plt.close(fig)

print("\n=== (C) ROC e matriz de confusão ===")
print(f"  AUC teste: {auc_v:.3f}")
print(f"  Matriz de confusão [real x previsto]:\n{cm}")
print("\n[OK] Figuras: fig_subperiodo, fig_backtest, fig_roc, fig_matriz_confusao")
