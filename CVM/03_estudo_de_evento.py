# -*- coding: utf-8 -*-
# ==============================================================================
#   Etapa 3 — Estudo de evento: os comunicados da CVM movem o preço?
#
#   Esta etapa responde à pergunta central do Prof. Emerson SEM depender de
#   classificação de sentimento. É um teste de impacto, não de direção.
#
#   Método (padrão da literatura de finanças):
#     1. modelo de mercado  R_it = a + b*R_mt + e_it, estimado numa janela de
#        estimação anterior ao evento (-120 a -21 pregões);
#     2. retorno anormal    AR_it = R_it - (a + b*R_mt) no entorno do evento;
#     3. acumula-se o AR na janela e testa-se se a média difere de zero.
#
#   Duas perguntas, e a segunda é a que interessa a esta dissertação:
#     (a) DIREÇÃO — o AR médio difere de zero? (o mercado sobe ou desce?)
#     (b) MAGNITUDE — o |AR| é maior que no dia comum? (o preço SACODE mais?)
#
#   Grupo de comparação: o Comunicado ao Mercado, que é menos obrigatório que o
#   Fato Relevante. Se a lei acerta ao chamar um de "relevante", o efeito do
#   Fato Relevante tem de ser maior.
#
#   Saída: CVM/dados/estudo_evento_resultado.json e _ar_por_evento.csv
# ==============================================================================
from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")

AQUI = Path(__file__).resolve().parent
DADOS = AQUI / "dados"

EST_INI, EST_FIM = -120, -21      # janela de estimação
MIN_EST = 60                      # mínimo de pregões para estimar o modelo
JANELAS = {"[0]": (0, 0), "[0,+1]": (0, 1), "[-1,+1]": (-1, 1), "[0,+5]": (0, 5)}


def main() -> None:
    print("=" * 76)
    print("ETAPA 3 — ESTUDO DE EVENTO: OS COMUNICADOS DA CVM MOVEM O PREÇO?")
    print("=" * 76)

    px = pd.read_csv(DADOS / "precos_b3.csv", index_col=0, parse_dates=True).sort_index()
    ret = np.log(px / px.shift(1))
    if "IBOV" not in ret.columns:
        raise SystemExit("IBOV ausente em precos_b3.csv")
    mkt = ret["IBOV"]
    pregoes = ret.index

    com = pd.read_csv(DADOS / "cvm_para_classificar.csv", parse_dates=["Data_Entrega"])
    com = com[com["Ticker"].isin(ret.columns)].copy()
    print(f"\n  comunicados com preço ......... {len(com):,}")

    # a data de entrega vira o pregão seguinte se cair em dia sem negociação
    pos = pregoes.searchsorted(com["Data_Entrega"].values, side="left")
    com["idx"] = pos
    com = com[com["idx"] < len(pregoes) - 6]
    com = com[com["idx"] > abs(EST_INI) + 5]
    print(f"  com janela completa ........... {len(com):,}")

    linhas = []
    for _, r in com.iterrows():
        t, i = r["Ticker"], int(r["idx"])
        y = ret[t].iloc[i + EST_INI: i + EST_FIM]
        x = mkt.iloc[i + EST_INI: i + EST_FIM]
        m = y.notna() & x.notna()
        if m.sum() < MIN_EST:
            continue
        b, a = np.polyfit(x[m], y[m], 1)
        resid = y[m] - (a + b * x[m])
        sigma = resid.std(ddof=2)
        if not np.isfinite(sigma) or sigma == 0:
            continue

        reg = {"Ticker": t, "Data": r["Data_Entrega"], "Categoria": r["Categoria"],
               "Assunto": r["Assunto"], "sigma_est": sigma}
        for nome, (d0, d1) in JANELAS.items():
            yy = ret[t].iloc[i + d0: i + d1 + 1]
            xx = mkt.iloc[i + d0: i + d1 + 1]
            if yy.isna().any() or xx.isna().any():
                reg[f"CAR{nome}"] = np.nan
                continue
            ar = yy.values - (a + b * xx.values)
            reg[f"CAR{nome}"] = ar.sum()
            reg[f"ABS{nome}"] = np.abs(ar).mean()
        reg["CAR_padronizado"] = reg["CAR[0,+1]"] / (sigma * np.sqrt(2)) \
            if pd.notna(reg.get("CAR[0,+1]")) else np.nan
        linhas.append(reg)

    ev = pd.DataFrame(linhas)
    print(f"  eventos com modelo estimado ... {len(ev):,}")

    fr = ev[ev["Categoria"] == "Fato Relevante"]
    cm = ev[ev["Categoria"] == "Comunicado ao Mercado"]
    print(f"    Fato Relevante .............. {len(fr):,}")
    print(f"    Comunicado ao Mercado ....... {len(cm):,}")

    res = {"n_eventos": int(len(ev)), "n_fato_relevante": int(len(fr)),
           "n_comunicado": int(len(cm)), "direcao": {}, "magnitude": {}}

    # ── (a) DIREÇÃO ──────────────────────────────────────────────────────────
    print("\n" + "=" * 76)
    print("  (a) DIREÇÃO — o retorno anormal médio difere de zero?")
    print("=" * 76)
    print(f"  {'janela':>9} | {'grupo':<22} | {'CAR médio':>10} | {'t':>7} | {'valor-p':>8}")
    print("  " + "-" * 72)
    for nome in JANELAS:
        for rot, sub in [("Fato Relevante", fr), ("Comunicado ao Mercado", cm)]:
            v = sub[f"CAR{nome}"].dropna()
            if len(v) < 30:
                continue
            t, p = stats.ttest_1samp(v, 0.0)
            print(f"  {nome:>9} | {rot:<22} | {v.mean()*100:>9.3f}% | {t:>7.2f} | "
                  f"{p:>8.4f}{' *' if p < 0.05 else ''}")
            res["direcao"].setdefault(nome, {})[rot] = {
                "n": int(len(v)), "car_medio_pct": round(float(v.mean() * 100), 4),
                "t": round(float(t), 3), "p": round(float(p), 5)}

    # ── (b) MAGNITUDE ────────────────────────────────────────────────────────
    print("\n" + "=" * 76)
    print("  (b) MAGNITUDE — o preço sacode mais que no dia comum?")
    print("=" * 76)
    print("  Razão entre o |retorno anormal| do evento e o desvio-padrão típico")
    print("  do próprio papel. Valor 1,0 = dia comum. Acima de 1 = sacode mais.\n")
    print(f"  {'janela':>9} | {'grupo':<22} | {'razão':>7} | {'t (vs 1)':>9} | {'valor-p':>8}")
    print("  " + "-" * 70)
    for nome in JANELAS:
        for rot, sub in [("Fato Relevante", fr), ("Comunicado ao Mercado", cm)]:
            col = f"ABS{nome}"
            if col not in sub.columns:
                continue
            razao = (sub[col] / (sub["sigma_est"] * np.sqrt(2 / np.pi))).dropna()
            if len(razao) < 30:
                continue
            t, p = stats.ttest_1samp(razao, 1.0)
            print(f"  {nome:>9} | {rot:<22} | {razao.mean():>7.3f} | {t:>9.2f} | "
                  f"{p:>8.2e}{' *' if p < 0.05 else ''}")
            res["magnitude"].setdefault(nome, {})[rot] = {
                "n": int(len(razao)), "razao": round(float(razao.mean()), 4),
                "t": round(float(t), 3), "p": float(p)}

    # ── (c) o Fato Relevante é mesmo mais forte que o Comunicado? ────────────
    print("\n" + "=" * 76)
    print("  (c) A LEI ACERTA? Fato Relevante contra Comunicado ao Mercado")
    print("=" * 76)
    a = (fr["ABS[0,+1]"] / (fr["sigma_est"] * np.sqrt(2 / np.pi))).dropna()
    b_ = (cm["ABS[0,+1]"] / (cm["sigma_est"] * np.sqrt(2 / np.pi))).dropna()
    t, p = stats.ttest_ind(a, b_, equal_var=False)
    print(f"  Fato Relevante ......... {a.mean():.3f}  (n={len(a):,})")
    print(f"  Comunicado ao Mercado .. {b_.mean():.3f}  (n={len(b_):,})")
    print(f"  diferença .............. {a.mean()-b_.mean():+.3f}   t={t:.2f}   p={p:.2e}"
          f"{'  *' if p < 0.05 else ''}")
    res["fr_vs_cm"] = {"fr": round(float(a.mean()), 4), "cm": round(float(b_.mean()), 4),
                       "dif": round(float(a.mean() - b_.mean()), 4),
                       "t": round(float(t), 3), "p": float(p)}

    # ── (d) o efeito é de cauda? ─────────────────────────────────────────────
    print("\n" + "=" * 76)
    print("  (d) O EFEITO É DE CAUDA? distribuição do |AR| padronizado")
    print("=" * 76)
    q = a.quantile([.5, .75, .9, .95, .99])
    print(f"  mediana ......... {q[.50]:.3f}   <- o Fato Relevante TÍPICO")
    print(f"  percentil 75 .... {q[.75]:.3f}")
    print(f"  percentil 90 .... {q[.90]:.3f}")
    print(f"  percentil 95 .... {q[.95]:.3f}")
    print(f"  percentil 99 .... {q[.99]:.3f}   <- os excepcionais")
    print(f"\n  média {a.mean():.3f} contra mediana {q[.50]:.3f}: "
          f"razão {a.mean()/q[.50]:.2f}")
    res["cauda"] = {"media": round(float(a.mean()), 4),
                    **{f"p{int(k*100)}": round(float(v), 4) for k, v in q.items()}}

    ev.to_csv(DADOS / "_ar_por_evento.csv", index=False, encoding="utf-8-sig")
    (DADOS / "estudo_evento_resultado.json").write_text(
        json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n  gravados: _ar_por_evento.csv e estudo_evento_resultado.json")


if __name__ == "__main__":
    main()
