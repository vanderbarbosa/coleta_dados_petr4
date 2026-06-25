# -*- coding: utf-8 -*-
# ==============================================================================
#   DISSERTAÇÃO PETR4 — Etapa 11: Estatística descritiva e figuras exploratórias
#   Autor: Vanderlei Barbosa da Silva | Orientador: Prof. Dr. Julio Cesar Nievola
#
#   Gera a estatística descritiva das séries e figuras exploratórias adicionais:
#   (A) Tabela descritiva (média, desvio, assimetria, curtose, Jarque-Bera, ADF).
#   (B) fig_preco_serie    — preço de fechamento da PETR4.
#   (C) fig_retorno_dist   — histograma dos log-retornos com curva normal.
#   (D) fig_sent_categoria — sentimento médio por categoria temática.
# ==============================================================================

import warnings
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
from statsmodels.tsa.stattools import adfuller

warnings.filterwarnings("ignore")
RAIZ = Path(__file__).resolve().parents[2]
PASTA = RAIZ / "Mestrado_PETR4"
FIG = RAIZ / "Exame_qualificacao" / "PesquisaMestrado_Qualificacao" / "figuras"
plt.rcParams.update({"figure.dpi": 150, "font.size": 11,
                     "axes.spines.top": False, "axes.spines.right": False})
AZUL = "#0b5394"; AZULC = "#2c7bb6"; VERM = "#b42318"; VERDE = "#1a7f37"; CINZA = "#5a6b7b"

m = pd.read_csv(PASTA / "base_master_petr4.csv", parse_dates=["Date"]).sort_values("Date")
fin = pd.read_csv(PASTA / "base_financeira_petr4.csv", parse_dates=["Date"]).sort_values("Date")

# ── (A) Estatística descritiva ────────────────────────────────────────────────
print("=== (A) Estatística descritiva ===")
series = {"Log-retorno (%)": m["Log_Retorno_Pct"].dropna(),
          "Volatilidade GARCH": m["Volatilidade_GARCH"].dropna(),
          "Índice de sentimento": m["Indice_Sentimento_Transformer"].dropna()}
for nome, s in series.items():
    jb = stats.jarque_bera(s); adf = adfuller(s, autolag="AIC")
    print(f"\n{nome} (n={len(s)}):")
    print(f"  media={s.mean():.4f} dp={s.std():.4f} min={s.min():.3f} max={s.max():.3f}")
    print(f"  assimetria={stats.skew(s):.3f} curtose={stats.kurtosis(s, fisher=False):.3f}")
    print(f"  Jarque-Bera={jb.statistic:.1f} (p={jb.pvalue:.4f}) | ADF={adf[0]:.2f} (p={adf[1]:.4f})")

# ── (B) Série de preços ───────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 3.4))
ax.plot(fin["Date"], fin["Close"], color=AZUL, lw=1.1)
ax.set_ylabel("Preço de fechamento (R\\$)"); ax.set_xlabel("Ano")
fig.savefig(FIG / "fig_preco_serie.png", bbox_inches="tight"); plt.close(fig)

# ── (C) Distribuição dos retornos ─────────────────────────────────────────────
r = m["Log_Retorno_Pct"].dropna()
fig, ax = plt.subplots(figsize=(6.6, 3.8))
ax.hist(r, bins=80, density=True, color=AZULC, alpha=0.65, label="Log-retornos")
x = np.linspace(r.min(), r.max(), 300)
ax.plot(x, stats.norm.pdf(x, r.mean(), r.std()), color=VERM, lw=1.6, label="Normal")
ax.set_xlabel("Log-retorno diário (%)"); ax.set_ylabel("Densidade"); ax.legend(fontsize=8)
fig.savefig(FIG / "fig_retorno_dist.png", bbox_inches="tight"); plt.close(fig)

# ── (D) Sentimento médio por categoria ────────────────────────────────────────
cat = pd.read_csv(PASTA / "indice_sentimento_categorias_petr4.csv")
rot = {"ISM_CAT1_Empresa": "Empresa", "ISM_CAT2_Mercado_Petroleo": "Mercado petróleo",
       "ISM_CAT3_Geopolitica": "Geopolítica", "ISM_CAT4_Infraestrutura": "Infraestrutura",
       "ISM_CAT5_Sancoes_Navegacao": "Sanções/Naveg.", "ISM_CAT6_Governanca": "Governança",
       "ISM_CAT7_Macro_Energia": "Macro/Energia"}
med = cat[list(rot)].mean().rename(index=rot).sort_values()
fig, ax = plt.subplots(figsize=(7, 3.6))
cores = [VERM if v < 0 else VERDE for v in med.values]
ax.barh(med.index, med.values, color=cores)
ax.axvline(0, color=CINZA, lw=0.8)
ax.set_xlabel("Sentimento médio (ISM)")
fig.savefig(FIG / "fig_sent_categoria.png", bbox_inches="tight"); plt.close(fig)
print("\nSentimento médio por categoria:")
print(med.round(3).to_string())
print("\n[OK] figuras: fig_preco_serie, fig_retorno_dist, fig_sent_categoria")
