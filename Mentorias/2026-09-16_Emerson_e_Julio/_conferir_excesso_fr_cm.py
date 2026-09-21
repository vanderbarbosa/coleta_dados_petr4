# Recalcula, para o documento 15, o excesso do Fato Relevante e do Comunicado ao Mercado
# contra pregoes sem comunicado (p-valores certos, IC por bootstrap de dias e medianas).
# Nao grava nada no projeto. Uso: python _conferir_excesso_fr_cm.py
# Reproduz o controle da Rodada A (07_rodada_A.py, bloco A.4) sem gravar nada no projeto
# e calcula o teste CERTO: Fato Relevante / Comunicado contra pregões sem comunicado.
import numpy as np
import pandas as pd
from scipy import stats

from pathlib import Path
RAIZ = Path(__file__).resolve().parents[2]
DADOS = str(RAIZ / "CVM" / "dados")
MIN_BASE = 3
try:
    import importlib.util, re
    src = open(RAIZ / "CVM" / "07_rodada_A.py", encoding="utf-8").read()
    MIN_BASE = int(re.search(r"^MIN_BASE\s*=\s*(\d+)", src, re.M).group(1))
except Exception as e:
    print("MIN_BASE padrao", MIN_BASE, e)
print("MIN_BASE =", MIN_BASE)

px = pd.read_csv(f"{DADOS}\\ohlcv_b3.csv", parse_dates=["Data"]).sort_values(["Ticker", "Data"])
d = pd.read_csv(f"{DADOS}\\rodada_A_casos.csv", parse_dates=["Pregao_reacao"])
print("eventos:", len(d), d["Categoria"].value_counts().to_dict())

chave = set(zip(d["Ticker"], d["Pregao_reacao"]))
ini, fim = d["Pregao_reacao"].min(), d["Pregao_reacao"].max()
ctl = []
for tk, g in px[px["Ticker"].isin(d["Ticker"].unique())].groupby("Ticker"):
    g = g.reset_index(drop=True)
    pk, vl = g["Parkinson"].values, g["Volume"].values.astype(float)
    for i in range(130, len(g) - 1):
        dia = g["Data"].iloc[i]
        if dia < ini or dia > fim:
            continue
        jp, jv = pk[i - 6:i - 1], vl[i - 6:i - 1]
        jp = jp[np.isfinite(jp) & (jp > 0)]
        jv = jv[np.isfinite(jv) & (jv > 0)]
        if len(jp) < MIN_BASE or len(jv) < MIN_BASE or not np.isfinite(pk[i]) or pk[i] <= 0:
            continue
        ctl.append({"tk": tk, "dia": dia, "ev": (tk, dia) in chave,
                    "rv": pk[i] / jp.mean(), "rq": vl[i] / jv.mean()})
c = pd.DataFrame(ctl)
sem = c[~c["ev"]]
print(f"controle (sem comunicado): {len(sem):,}   (doc: 105.896)")
com = c[c["ev"]]
print(f"pregões-papel COM comunicado (1 linha por papel-dia): {len(com):,}  (eventos: {len(d):,})")
print(f"  excesso vol por pregão-papel : {com['rv'].mean()/sem['rv'].mean()-1:+.1%}   (artigo: +9,6%)")
print(f"  excesso volume por pregão-papel: {com['rq'].mean()/sem['rq'].mean()-1:+.1%}   (artigo: +16,5%)")
import sys; sys.stdout.flush()

col = {"vol": ("razaoVol_1 semana (-6 a -2)", "rv"),
       "volume": ("razaoVolume_1 semana (-6 a -2)", "rq")}
grupos = {"Fato Relevante": d[d["Categoria"] == "Fato Relevante"],
          "Comunicado ao Mercado": d[d["Categoria"] == "Comunicado ao Mercado"],
          "Os dois juntos": d}
rng = np.random.default_rng(42)

for medida, (cev, cct) in col.items():
    print(f"\n=== {medida} ===")
    x = sem[cct].dropna()
    # soma e contagem por dia, para bootstrap por blocos de dia (dias em comum entre papéis)
    dias = np.array(sorted(set(sem["dia"]) | set(d["Pregao_reacao"])))
    idx = {t: k for k, t in enumerate(dias)}
    s_sem = np.zeros(len(dias)); n_sem = np.zeros(len(dias))
    for t, v in zip(sem["dia"], sem[cct]):
        s_sem[idx[t]] += v; n_sem[idx[t]] += 1
    for nome, g in grupos.items():
        y = g[cev].dropna()
        exc = y.mean() / x.mean() - 1
        w = stats.ttest_ind(y, x, equal_var=False).pvalue
        mw = stats.mannwhitneyu(y, x, alternative="two-sided").pvalue
        gg = g.dropna(subset=[cev])
        s_g = np.zeros(len(dias)); n_g = np.zeros(len(dias))
        for t, v in zip(gg["Pregao_reacao"], gg[cev]):
            s_g[idx[t]] += v; n_g[idx[t]] += 1
        B = 2000
        bs = np.empty(B)
        for b in range(B):
            k = rng.integers(0, len(dias), len(dias))
            bs[b] = (s_g[k].sum() / n_g[k].sum()) / (s_sem[k].sum() / n_sem[k].sum()) - 1
        lo, hi = np.percentile(bs, [2.5, 97.5])
        print(f"{nome:24} n={len(y):6,}  excesso {exc*100:+6.1f}%  IC95 por dia [{lo*100:+5.1f}%, {hi*100:+5.1f}%]"
              f"  p(Welch)={w:.1e}  p(Mann-Whitney)={mw:.1e}")
    # o efeito é da média ou do meio da distribuição? mediana do grupo contra mediana do controle
    for nome, g in grupos.items():
        y = g[cev].dropna()
        print(f"   mediana {nome:24} {y.median():.3f} vs controle {x.median():.3f}  -> {y.median()/x.median()-1:+.1%}")
    # FR contra CM (o "p = 7e-18" citado antes)
    a = grupos["Fato Relevante"][cev].dropna(); b_ = grupos["Comunicado ao Mercado"][cev].dropna()
    print(f"FR contra CM: p(Welch)={stats.ttest_ind(a, b_, equal_var=False).pvalue:.1e}  "
          f"p(Mann-Whitney)={stats.mannwhitneyu(a, b_).pvalue:.1e}")

