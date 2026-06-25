# -*- coding: utf-8 -*-
# ==============================================================================
#   DISSERTAÇÃO PETR4 — Etapa 9: Figuras didáticas (Zipf, tuning, correlação)
#   Autor: Vanderlei Barbosa da Silva | Orientador: Prof. Dr. Julio Cesar Nievola
#
#   Gera figuras que enriquecem a explicação visual da pesquisa:
#   (A) Lei de Zipf sobre o corpus real (frequência x ranking, log-log).
#   (B) Mapa de calor do tuning do XGBoost (acurácia de validação na grade).
#   (C) Matriz de correlação dos atributos do modelo.
# ==============================================================================

import re, warnings
from collections import Counter
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
plt.rcParams.update({"figure.dpi": 150, "font.size": 11,
                     "axes.spines.top": False, "axes.spines.right": False})
AZUL = "#0b5394"; AZULC = "#2c7bb6"; VERM = "#b42318"; CINZA = "#5a6b7b"

# ──────────────────────────────────────────────────────────────────────────────
# (A) Lei de Zipf sobre o corpus
# ──────────────────────────────────────────────────────────────────────────────
print("(A) Lei de Zipf...")
news = pd.read_csv(PASTA / "noticias_com_sentimento.csv", usecols=["Titulo", "Resumo"])
texto = (news["Titulo"].fillna("") + " " + news["Resumo"].fillna("")).str.lower()
cont = Counter()
amostra = texto.sample(min(40000, len(texto)), random_state=42)
for t in amostra:
    cont.update(re.findall(r"[a-zà-ÿ]{2,}", t))
freqs = np.array(sorted(cont.values(), reverse=True))
ranks = np.arange(1, len(freqs) + 1)
fig, ax = plt.subplots(figsize=(7, 4))
ax.loglog(ranks, freqs, color=AZUL, lw=1.6, label="Palavras do corpus PETR4")
# linha de referência Zipf ideal: f ~ c / rank
c = freqs[0]
ax.loglog(ranks, c / ranks, color=VERM, ls="--", lw=1.2, label="Lei de Zipf ideal (f = c/r)")
ax.set_xlabel("Ranking da palavra (log)"); ax.set_ylabel("Frequência (log)")
ax.legend(fontsize=8)
fig.savefig(FIG / "fig_zipf.png", bbox_inches="tight"); plt.close(fig)
print(f"    vocabulário: {len(freqs)} palavras; mais frequente ocorre {int(freqs[0])} vezes")

# ──────────────────────────────────────────────────────────────────────────────
# (B) Mapa de calor do tuning do XGBoost (acurácia de validação)
# ──────────────────────────────────────────────────────────────────────────────
print("(B) Tuning XGBoost...")
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score
df = pd.read_csv(PASTA / "base_master_petr4.csv", parse_dates=["Date"]).sort_values("Date")
FE = ["Retorno_Ontem", "Volatilidade_Ontem", "Sentimento_Ontem"]
df = df.dropna(subset=FE + ["Alvo"]).reset_index(drop=True)
n = len(df); i_tr, i_va = int(n*0.60), int(n*0.75)
tr, va = df.iloc[:i_tr], df.iloc[i_tr:i_va]
depths = [2, 3, 4]; lrs = [0.02, 0.05, 0.10]
M = np.zeros((len(depths), len(lrs)))
for i, md in enumerate(depths):
    for j, lr in enumerate(lrs):
        m = XGBClassifier(n_estimators=200, max_depth=md, learning_rate=lr, subsample=0.9,
                          colsample_bytree=0.9, eval_metric="logloss", random_state=42, n_jobs=4)
        m.fit(tr[FE].values, tr["Alvo"].values)
        M[i, j] = accuracy_score(va["Alvo"], m.predict(va[FE].values)) * 100
fig, ax = plt.subplots(figsize=(5.6, 4))
im = ax.imshow(M, cmap="Blues", aspect="auto")
ax.set_xticks(range(len(lrs))); ax.set_xticklabels([f"{x:.2f}" for x in lrs])
ax.set_yticks(range(len(depths))); ax.set_yticklabels(depths)
ax.set_xlabel("Taxa de aprendizado"); ax.set_ylabel("Profundidade máxima")
for i in range(len(depths)):
    for j in range(len(lrs)):
        ax.text(j, i, f"{M[i,j]:.1f}", ha="center", va="center",
                color="white" if M[i,j] > M.mean() else "black", fontsize=10)
fig.colorbar(im, ax=ax, label="Acurácia de validação (%)")
fig.savefig(FIG / "fig_tuning.png", bbox_inches="tight"); plt.close(fig)
best = np.unravel_index(M.argmax(), M.shape)
print(f"    melhor: profundidade={depths[best[0]]}, taxa={lrs[best[1]]:.2f} -> {M.max():.2f}%")

# ──────────────────────────────────────────────────────────────────────────────
# (C) Matriz de correlação dos atributos
# ──────────────────────────────────────────────────────────────────────────────
print("(C) Correlação dos atributos...")
cols = {"Retorno_Ontem": "Retorno(t-1)", "Volatilidade_Ontem": "Volat.(t-1)",
        "Sentimento_Ontem": "Sentim.(t-1)", "Log_Retorno_Pct": "Retorno(t)"}
C = df[list(cols)].rename(columns=cols).corr()
fig, ax = plt.subplots(figsize=(5.2, 4.4))
im = ax.imshow(C, cmap="RdBu_r", vmin=-1, vmax=1)
ax.set_xticks(range(len(C))); ax.set_xticklabels(C.columns, rotation=35, ha="right", fontsize=9)
ax.set_yticks(range(len(C))); ax.set_yticklabels(C.columns, fontsize=9)
for i in range(len(C)):
    for j in range(len(C)):
        ax.text(j, i, f"{C.iloc[i,j]:.2f}", ha="center", va="center",
                color="white" if abs(C.iloc[i,j]) > 0.5 else "black", fontsize=9)
fig.colorbar(im, ax=ax, label="Correlação de Pearson")
fig.savefig(FIG / "fig_correlacao.png", bbox_inches="tight"); plt.close(fig)

print("\n[OK] Figuras: fig_zipf, fig_tuning, fig_correlacao")
