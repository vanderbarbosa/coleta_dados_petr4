# -*- coding: utf-8 -*-
# ==============================================================================
#   Etapa 5 — O estudo de evento, agora separado pelo HORÁRIO OFICIAL
#
#   Com a hora oficial de entrega em mãos, é possível fazer o que antes não
#   dava: separar os comunicados por MOMENTO da divulgação e verificar em que
#   pregão o mercado reage.
#
#   A previsão, registrada ANTES de rodar:
#     entregue ANTES DA ABERTURA  -> o mercado reage no MESMO pregão (D0)
#     entregue COM O PREGÃO ABERTO-> reage em parte em D0, resto em D+1
#     entregue APÓS O FECHAMENTO  -> só pode reagir em D+1
#
#   Se esse padrão aparecer, é prova de que o carimbo é real e de que a janela
#   [0,+1] usada na Etapa 3 estava correta — porque cobre os dois casos.
#
#   Saída: CVM/dados/evento_por_horario.json
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

EST_INI, EST_FIM, MIN_EST = -120, -21, 60
GRUPOS = [("antes da abertura (até 09h59)", 0, 9),
          ("com o pregão aberto (10h–16h59)", 10, 16),
          ("após o fechamento (17h em diante)", 17, 23)]


def main() -> None:
    print("=" * 78)
    print("ETAPA 5 — EM QUE PREGÃO O MERCADO REAGE, SEGUNDO O HORÁRIO OFICIAL")
    print("=" * 78)

    px = pd.read_csv(DADOS / "precos_b3.csv", index_col=0, parse_dates=True).sort_index()
    ret = np.log(px / px.shift(1))
    mkt, pregoes = ret["IBOV"], ret.index

    base = pd.read_csv(DADOS / "cvm_para_classificar.csv", dtype=str)
    base["numSequencia"] = base["Link_Download"].str.extract(r"numSequencia=(\d+)")
    hora = pd.read_csv(DADOS / "cvm_hora_entrega.csv", dtype=str).drop_duplicates("numSequencia")

    d = base.merge(hora, on="numSequencia", how="inner")
    d["dh"] = pd.to_datetime(d["Data_Entrega_oficial"] + " " + d["Hora_Entrega_oficial"],
                             format="%d/%m/%Y %H:%M:%S", errors="coerce")
    d = d[d["dh"].notna() & d["Ticker"].isin(ret.columns)]
    print(f"\n  fatos relevantes com hora oficial e preço: {len(d):,}")

    print("\n  DISTRIBUIÇÃO POR HORA DO DIA:")
    hh = d["dh"].dt.hour.value_counts().sort_index()
    for h, n in hh.items():
        barra = "#" * max(1, int(n / max(hh) * 42))
        print(f"    {h:>02}h  {n:>5,}  {barra}")

    # ── retorno anormal em D0 e D+1, separadamente ───────────────────────────
    pos = pregoes.searchsorted(d["dh"].dt.normalize().values, side="left")
    d = d.assign(idx=pos)
    d = d[(d["idx"] > abs(EST_INI) + 5) & (d["idx"] < len(pregoes) - 6)]

    linhas = []
    for _, r in d.iterrows():
        t, i = r["Ticker"], int(r["idx"])
        y, x = ret[t].iloc[i + EST_INI:i + EST_FIM], mkt.iloc[i + EST_INI:i + EST_FIM]
        m = y.notna() & x.notna()
        if m.sum() < MIN_EST:
            continue
        b, a = np.polyfit(x[m], y[m], 1)
        sd = (y[m] - (a + b * x[m])).std(ddof=2)
        if not np.isfinite(sd) or sd == 0:
            continue
        reg = {"Ticker": t, "hora": r["dh"].hour, "sigma": sd}
        for rot, k in (("D0", 0), ("D1", 1)):
            yy, xx = ret[t].iloc[i + k], mkt.iloc[i + k]
            reg[rot] = np.nan if (pd.isna(yy) or pd.isna(xx)) else abs(yy - (a + b * xx)) / sd
        linhas.append(reg)

    ev = pd.DataFrame(linhas).dropna(subset=["D0", "D1"])
    print(f"  eventos com modelo estimado: {len(ev):,}")

    # normaliza: 1,0 = |retorno| de um dia comum
    esc = np.sqrt(2 / np.pi)
    ev["D0"] /= esc
    ev["D1"] /= esc

    print("\n" + "=" * 78)
    print("  SACOLEJO NO DIA DO COMUNICADO (D0) E NO SEGUINTE (D+1)")
    print("  1,0 = dia comum. A previsão está no cabeçalho do arquivo.")
    print("=" * 78)
    print(f"  {'grupo':<36} {'n':>6} {'D0':>7} {'D+1':>7}   {'quem manda':>12}")
    print("  " + "-" * 74)

    res = {"n_total": int(len(ev)), "grupos": {}}
    for rot, h0, h1 in GRUPOS:
        s = ev[(ev["hora"] >= h0) & (ev["hora"] <= h1)]
        if len(s) < 30:
            continue
        d0, d1 = s["D0"].mean(), s["D1"].mean()
        t, p = stats.ttest_rel(s["D0"], s["D1"])
        manda = "D0" if d0 > d1 else "D+1"
        print(f"  {rot:<36} {len(s):>6,} {d0:>7.3f} {d1:>7.3f}   {manda:>12}"
              f"  (p={p:.1e})")
        res["grupos"][rot] = {"n": int(len(s)), "D0": round(float(d0), 4),
                              "D1": round(float(d1), 4), "domina": manda,
                              "p_D0_vs_D1": float(p)}

    # ── o teste decisivo ─────────────────────────────────────────────────────
    print("\n" + "=" * 78)
    print("  O TESTE DECISIVO — o carimbo de hora é informativo?")
    print("=" * 78)
    antes = ev[ev["hora"] <= 9]
    depois = ev[ev["hora"] >= 17]
    if len(antes) > 30 and len(depois) > 30:
        ra, rd = antes["D0"] - antes["D1"], depois["D0"] - depois["D1"]
        t, p = stats.ttest_ind(ra, rd, equal_var=False)
        print(f"  Entregue antes da abertura: D0 − D+1 = {ra.mean():+.3f}")
        print(f"  Entregue após o fechamento: D0 − D+1 = {rd.mean():+.3f}")
        print(f"  diferença entre os dois grupos: {ra.mean()-rd.mean():+.3f}  "
              f"t={t:.2f}  p={p:.2e}{'  *' if p < 0.05 else ''}")
        res["teste_decisivo"] = {"antes_D0_menos_D1": round(float(ra.mean()), 4),
                                 "depois_D0_menos_D1": round(float(rd.mean()), 4),
                                 "dif": round(float(ra.mean() - rd.mean()), 4),
                                 "t": round(float(t), 3), "p": float(p)}
        print("\n  COMO LER: se o carimbo for real e o mercado racional, o grupo da")
        print("  manhã deve concentrar o movimento em D0 (diferença positiva) e o")
        print("  grupo da noite deve empurrá-lo para D+1 (diferença menor ou negativa).")

    # ── a janela [0,+1] da Etapa 3 se sustenta? ──────────────────────────────
    print("\n" + "=" * 78)
    print("  A JANELA [0,+1] DA ETAPA 3 SE SUSTENTA?")
    print("=" * 78)
    ev["melhor"] = ev[["D0", "D1"]].max(axis=1)
    print(f"  usando só D0 ................. {ev['D0'].mean():.3f}")
    print(f"  usando só D+1 ................ {ev['D1'].mean():.3f}")
    print(f"  usando a janela [0,+1] ....... {ev[['D0','D1']].mean(axis=1).mean():.3f}")
    print(f"  usando o melhor dos dois ..... {ev['melhor'].mean():.3f}")
    res["janela"] = {"D0": round(float(ev["D0"].mean()), 4),
                     "D1": round(float(ev["D1"].mean()), 4),
                     "media_0_1": round(float(ev[["D0","D1"]].mean(axis=1).mean()), 4)}

    (DADOS / "evento_por_horario.json").write_text(
        json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n  gravado: evento_por_horario.json")


if __name__ == "__main__":
    main()
