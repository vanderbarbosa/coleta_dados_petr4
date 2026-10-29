# -*- coding: utf-8 -*-
# ==============================================================================
#   REEXECUÇÃO COM ALVO ANORMAL — mentoria de 29/10/2026
#
#   O Script 27 mostrou que trocar o alvo de retorno BRUTO para ANORMAL
#   (descontando o Ibovespa) inverteu o sinal na previsão de direção: de zero
#   braços positivos em oito para cinco. Isso levanta a suspeita de que o alvo
#   bruto contaminava TAMBÉM os experimentos que deram nulo antes. Aqui eles
#   são refeitos com o alvo corrigido:
#
#     (a) VOLATILIDADE — o HAR passa a prever a volatilidade do retorno
#         ANORMAL, isto é, a volatilidade idiossincrática, que é a parte que
#         um comunicado da própria empresa poderia de fato explicar. A
#         volatilidade do retorno bruto embute a agitação do mercado inteiro.
#
#     (b) DIAS COM COMUNICADO — a restrição que piorou tudo no Script 25,
#         agora com o alvo anormal.
#
#   INFERÊNCIA: bootstrap em blocos de DATA (sorteia datas com reposição e
#   leva todos os papéis daquelas datas), como estabelecido no Script 27.
#   Medido lá: a inflação sobre o IC de independência é de apenas 1,05x, mas
#   o bootstrap continua sendo o método correto.
#
#   Saída: dados/reexecucao_alvo_anormal.json
# ==============================================================================
from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from arch import arch_model
from sklearn.linear_model import LinearRegression
from sklearn.metrics import accuracy_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from xgboost import XGBClassifier

warnings.filterwarnings("ignore")

AQUI = Path(__file__).resolve().parent
DADOS = AQUI / "dados"
TOP10 = ["VALE3", "ITUB4", "PETR4", "SBSP3", "BBDC4", "B3SA3", "ITSA4",
         "BPAC11", "BBAS3", "ABEV3"]
B_BOOT = 2000
RNG = np.random.default_rng(42)
XGB = dict(n_estimators=300, max_depth=3, learning_rate=0.05, subsample=0.9,
           colsample_bytree=0.9, random_state=42, eval_metric="logloss", n_jobs=-1)

_OHLCV = pd.read_csv(DADOS / "ohlcv_b3.csv", parse_dates=["Data"])
_PRECOS = pd.read_csv(DADOS / "precos_b3.csv", index_col=0, parse_dates=True)
_IBOV = _PRECOS["IBOV"].pct_change().rename("Rm")
_CASOS = pd.read_csv(DADOS / "rodada_A_casos.csv", low_memory=False,
                      usecols=["Protocolo_Entrega", "Ticker", "Entrega", "Pregao_reacao"])
_CASOS["Entrega"] = pd.to_datetime(_CASOS["Entrega"], errors="coerce")
_CASOS["Data"] = pd.to_datetime(_CASOS["Pregao_reacao"], errors="coerce")
_CLASS = pd.read_csv(DADOS / "cvm_classificado.csv", low_memory=False)


def monta(ticker: str) -> pd.DataFrame:
    px = _OHLCV[_OHLCV["Ticker"] == ticker].sort_values("Data").reset_index(drop=True)
    px = px[px["Retorno"].notna()].reset_index(drop=True)
    d = px.merge(_IBOV, left_on="Data", right_index=True, how="inner")
    d = d[d["Rm"].notna()].reset_index(drop=True)
    corte = d["Data"].iloc[int(len(d) * 0.75)]
    tr = d["Data"] < corte
    mm = LinearRegression().fit(d.loc[tr, ["Rm"]], d.loc[tr, "Retorno"])
    d["Ret_Anormal"] = d["Retorno"] - mm.predict(d[["Rm"]])
    for col, serie in [("Vol_Bruta", d["Retorno"]), ("Vol_Anormal", d["Ret_Anormal"])]:
        g = arch_model(serie.values * 100, vol="Garch", p=1, q=1, dist="t").fit(disp="off")
        d[col] = g.conditional_volatility

    a = _CASOS[(_CASOS["Ticker"] == ticker) & _CASOS["Entrega"].notna() & _CASOS["Data"].notna()]
    a = a[a["Entrega"].dt.hour >= 17]
    c = a.merge(_CLASS[["Protocolo_Entrega", "p_pos", "p_neg"]], on="Protocolo_Entrega", how="inner")
    c["ism"] = c["p_pos"] - c["p_neg"]
    cvm = c.groupby("Data").agg(Sent=("ism", "mean"), Qtd=("ism", "size")).reset_index()
    d = d.merge(cvm, on="Data", how="left")
    d["TEM_EVENTO"] = d["Qtd"].notna()
    d[["Sent", "Qtd"]] = d[["Sent", "Qtd"]].fillna(0.0)

    d["Ticker"] = ticker
    d["Ret_Ontem"] = d["Retorno"].shift(1) * 100
    d["RetAn_Ontem"] = d["Ret_Anormal"].shift(1) * 100
    d["VolB_Ontem"] = d["Vol_Bruta"].shift(1)
    d["VolA_Ontem"] = d["Vol_Anormal"].shift(1)
    d["Alvo_Bruto"] = np.where(d["Retorno"] > 0, 1, 0)
    d["Alvo_Anormal"] = np.where(d["Ret_Anormal"] > 0, 1, 0)
    for pre, v in [("hB", d["Vol_Bruta"]), ("hA", d["Vol_Anormal"])]:
        d[f"{pre}1"] = v.shift(1)
        d[f"{pre}5"] = v.shift(1).rolling(5).mean()
        d[f"{pre}22"] = v.shift(1).rolling(22).mean()
    return d.dropna(subset=["Ret_Ontem", "RetAn_Ontem", "hB22", "hA22"]).reset_index(drop=True)


def boot_datas(cod, valores, func, maj=None) -> dict:
    """Bootstrap em blocos de data sobre uma estatística agregada."""
    n_d = cod.max() + 1
    soma = np.bincount(cod, weights=valores, minlength=n_d)
    cont = np.bincount(cod, minlength=n_d).astype(float)
    am = np.empty(B_BOOT)
    for b in range(B_BOOT):
        e = RNG.integers(0, n_d, n_d)
        am[b] = soma[e].sum() / cont[e].sum()
    obs = float(valores.mean())
    lo, hi = np.percentile(am, [2.5, 97.5])
    out = {"n": int(len(valores)), "n_datas": int(n_d), "valor": round(obs, 4),
           "ic95": [round(float(lo), 4), round(float(hi), 4)]}
    if maj is not None:
        p = 2 * min((am <= maj).mean(), (am >= maj).mean())
        out.update({"majoritaria": round(float(maj), 4),
                    "ganho_pp": round((obs - maj) * 100, 2),
                    "ic95_pp": [round((lo - maj) * 100, 2), round((hi - maj) * 100, 2)],
                    "p_bootstrap": round(float(min(p, 1.0)), 4)})
    return out


def boot_r2os(cod, e_mod, e_ref) -> dict:
    """R²-OS com IC por bootstrap de data: 1 - SSE(modelo)/SSE(referência)."""
    n_d = cod.max() + 1
    s_mod = np.bincount(cod, weights=e_mod ** 2, minlength=n_d)
    s_ref = np.bincount(cod, weights=e_ref ** 2, minlength=n_d)
    am = np.empty(B_BOOT)
    for b in range(B_BOOT):
        e = RNG.integers(0, n_d, n_d)
        am[b] = (1 - s_mod[e].sum() / s_ref[e].sum()) * 100
    obs = (1 - (e_mod ** 2).sum() / (e_ref ** 2).sum()) * 100
    lo, hi = np.percentile(am, [2.5, 97.5])
    p = 2 * min((am <= 0).mean(), (am >= 0).mean())
    return {"r2os_pct": round(float(obs), 3), "ic95_pct": [round(float(lo), 3), round(float(hi), 3)],
            "p_bootstrap": round(float(min(p, 1.0)), 4)}


def main() -> None:
    partes = {tk: monta(tk) for tk in TOP10}
    comuns = set.intersection(*[set(v["Data"]) for v in partes.values()])
    P = pd.concat([v[v["Data"].isin(comuns)] for v in partes.values()], ignore_index=True)
    P = P.sort_values(["Data", "Ticker"]).reset_index(drop=True)
    datas = np.sort(P["Data"].unique())
    corte = datas[int(len(datas) * 0.75)]
    tr_m, te_m = (P["Data"] < corte).values, (P["Data"] >= corte).values
    cod_te, _ = pd.factorize(P.loc[te_m, "Data"])
    ev_te = P.loc[te_m, "TEM_EVENTO"].values
    cod_ev, _ = pd.factorize(P.loc[te_m, "Data"][ev_te])
    print(f"painel {len(P):,} linhas | teste {int(te_m.sum()):,} ({len(np.unique(cod_te))} datas) | "
          f"com evento {int(ev_te.sum()):,}")

    res = {"nota": ("alvo ANORMAL = retorno descontado do Ibovespa pelo modelo de mercado, "
                    "coeficientes estimados só no treino; inferência por bootstrap em blocos de data"),
           "volatilidade": {}, "direcao_por_subconjunto": {}}

    # ══ (a) VOLATILIDADE: bruta × anormal, com e sem sentimento ═════════════
    print(f"\n{'VOLATILIDADE — o sentimento acrescenta ao HAR?':<58}{'R²-OS':>9}{'IC95%':>20}{'p':>8}")
    print("-" * 96)
    for alvo_nome, alvo, pre in [("volatilidade BRUTA", "Vol_Bruta", "hB"),
                                  ("volatilidade ANORMAL (idiossincrática)", "Vol_Anormal", "hA")]:
        har = [f"{pre}1", f"{pre}5", f"{pre}22"]
        y = P[alvo].values
        ref = LinearRegression().fit(P.loc[tr_m, har], y[tr_m])
        e_ref = y[te_m] - ref.predict(P.loc[te_m, har])
        com = LinearRegression().fit(P.loc[tr_m, har + ["Sent", "Qtd"]], y[tr_m])
        e_com = y[te_m] - com.predict(P.loc[te_m, har + ["Sent", "Qtd"]])
        for sub, cod_, m_ in [("todos os dias", cod_te, np.ones(int(te_m.sum()), bool)),
                              ("só dias com comunicado", cod_ev, ev_te)]:
            r = boot_r2os(cod_, e_com[m_], e_ref[m_])
            res["volatilidade"][f"{alvo_nome} — {sub}"] = r
            print(f"  {alvo_nome:40}{sub:16}{r['r2os_pct']:>+8.3f}%"
                  f"  [{r['ic95_pct'][0]:+6.3f},{r['ic95_pct'][1]:+6.3f}]{r['p_bootstrap']:>8.3f}")

    # ══ (b) DIREÇÃO por subconjunto: alvo bruto × anormal ═══════════════════
    print(f"\n{'DIREÇÃO — a restrição a dias com comunicado, por alvo':<58}{'ganho':>9}{'IC95%':>20}{'p':>8}")
    print("-" * 96)
    for alvo_nome, alvo, base in [("BRUTO", "Alvo_Bruto", ["Ret_Ontem", "VolB_Ontem"]),
                                   ("ANORMAL", "Alvo_Anormal", ["RetAn_Ontem", "VolA_Ontem"])]:
        y = P[alvo].astype(int)
        cols = base + ["Sent", "Qtd"]
        mod = XGBClassifier(**XGB).fit(P.loc[tr_m, cols], y[tr_m])
        pred = mod.predict(P.loc[te_m, cols])
        acerto = (pred == y[te_m].values).astype(float)
        for sub, cod_, m_ in [("todos os dias", cod_te, np.ones(int(te_m.sum()), bool)),
                              ("só dias com comunicado", cod_ev, ev_te)]:
            yy = y[te_m].values[m_]
            maj = float(max(yy.mean(), 1 - yy.mean()))
            r = boot_datas(cod_, acerto[m_], None, maj)
            res["direcao_por_subconjunto"][f"alvo {alvo_nome} — {sub}"] = r
            print(f"  alvo {alvo_nome:12} {sub:24} n={r['n']:5} {r['ganho_pp']:>+7.2f}pp"
                  f"  [{r['ic95_pp'][0]:+6.2f},{r['ic95_pp'][1]:+6.2f}]{r['p_bootstrap']:>8.3f}")

    (DADOS / "reexecucao_alvo_anormal.json").write_text(
        json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\ngravado: dados/reexecucao_alvo_anormal.json")


if __name__ == "__main__":
    main()
