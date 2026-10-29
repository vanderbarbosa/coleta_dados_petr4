# -*- coding: utf-8 -*-
# ==============================================================================
#   RETORNO ANORMAL, MODELO DE PAINEL E INFERÊNCIA AGRUPADA POR DATA
#   Mentoria de 29/10/2026 — os três itens recomendados, de uma vez.
#
#   ─── ITEM 1: a correção de inferência ────────────────────────────────────
#   Os dez papéis têm correlação média de retorno de 0,486 no mesmo dia e
#   sobem ou descem juntos em 64,5% dos pregões. Logo, dez papéis num dia NÃO
#   são dez observações independentes: há um fator de mercado comum. Os
#   intervalos agrupados que reportei antes (±3,8 pontos) supunham
#   independência e estavam otimistas em cerca de 2,3 vezes. Aqui a inferência
#   é feita por BOOTSTRAP EM BLOCOS DE DATA: sorteiam-se datas com reposição e
#   levam-se TODOS os papéis daquelas datas, de modo que a correlação
#   transversal é preservada na reamostragem.
#
#   ─── ITEM 2: o alvo passa a ser o retorno ANORMAL ────────────────────────
#   O estudo de evento desta pesquisa (Artigo 1) sempre descontou o Ibovespa
#   pelo modelo de mercado. Os experimentos de aprendizado, porém, vinham
#   prevendo o retorno BRUTO — isto é, uma série cujo movimento é, em boa
#   parte, o mercado inteiro, que nenhum sentimento de empresa específica
#   poderia explicar. Aqui o alvo passa a ser também o retorno anormal:
#       R_it = alfa_i + beta_i * R_mt + e_it     →  anormal = e_it
#   Os coeficientes alfa e beta são estimados ESTRITAMENTE na janela de
#   treino, nunca no teste, para não contaminar a avaliação.
#
#   ─── ITEM 3: modelo de painel ────────────────────────────────────────────
#   Além de um modelo por papel, treina-se UM modelo com todos os papéis
#   empilhados (cada linha é um par papel-dia), com a identidade do papel como
#   atributo — inclinação comum, intercepto por papel. A previsão continua
#   individual: entram os atributos de um papel num dia, sai a resposta
#   daquele papel. O agrupamento é sobre de onde vem o aprendizado.
#
#   Saída: dados/retorno_anormal_e_painel.json
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
_CASOS = pd.read_csv(DADOS / "rodada_A_casos.csv", low_memory=False,
                      usecols=["Protocolo_Entrega", "Ticker", "Entrega", "Pregao_reacao"])
_CASOS["Entrega"] = pd.to_datetime(_CASOS["Entrega"], errors="coerce")
_CASOS["Data"] = pd.to_datetime(_CASOS["Pregao_reacao"], errors="coerce")
_CLASS = pd.read_csv(DADOS / "cvm_classificado.csv", low_memory=False)
_IBOV = _PRECOS["IBOV"].pct_change().rename("Rm")


def monta(ticker: str, corte_treino: pd.Timestamp | None = None) -> pd.DataFrame:
    """Painel de um papel. O modelo de mercado é estimado só até corte_treino."""
    px = _OHLCV[_OHLCV["Ticker"] == ticker].sort_values("Data").reset_index(drop=True)
    px = px[px["Retorno"].notna()].reset_index(drop=True)
    d = px.merge(_IBOV, left_on="Data", right_index=True, how="inner")
    d = d[d["Rm"].notna()].reset_index(drop=True)

    # ── modelo de mercado, coeficientes estimados SÓ no treino ──────────────
    corte = corte_treino if corte_treino is not None else d["Data"].iloc[int(len(d) * 0.75)]
    tr = d["Data"] < corte
    mm = LinearRegression().fit(d.loc[tr, ["Rm"]], d.loc[tr, "Retorno"])
    d["Ret_Anormal"] = d["Retorno"] - mm.predict(d[["Rm"]])
    beta = float(mm.coef_[0])

    # GARCH de cada série
    g1 = arch_model(d["Retorno"].values * 100, vol="Garch", p=1, q=1, dist="t").fit(disp="off")
    g2 = arch_model(d["Ret_Anormal"].values * 100, vol="Garch", p=1, q=1, dist="t").fit(disp="off")
    d["Vol_Bruta"] = g1.conditional_volatility
    d["Vol_Anormal"] = g2.conditional_volatility

    # ── sentimento dos comunicados (FinBERT, já classificado) ───────────────
    a = _CASOS[(_CASOS["Ticker"] == ticker) & _CASOS["Entrega"].notna() & _CASOS["Data"].notna()]
    a = a[a["Entrega"].dt.hour >= 17]
    c = a.merge(_CLASS[["Protocolo_Entrega", "p_pos", "p_neg"]], on="Protocolo_Entrega", how="inner")
    c["ism"] = c["p_pos"] - c["p_neg"]
    cvm = c.groupby("Data").agg(Sent=("ism", "mean"), Qtd=("ism", "size")).reset_index()
    d = d.merge(cvm, on="Data", how="left")
    d[["Sent", "Qtd"]] = d[["Sent", "Qtd"]].fillna(0.0)

    d["Ticker"] = ticker
    d["beta_mercado"] = beta
    d["Ret_Ontem"] = d["Retorno"].shift(1) * 100
    d["RetAn_Ontem"] = d["Ret_Anormal"].shift(1) * 100
    d["VolB_Ontem"] = d["Vol_Bruta"].shift(1)
    d["VolA_Ontem"] = d["Vol_Anormal"].shift(1)
    d["Alvo_Bruto"] = np.where(d["Retorno"] > 0, 1, 0)
    d["Alvo_Anormal"] = np.where(d["Ret_Anormal"] > 0, 1, 0)
    return d.dropna(subset=["Ret_Ontem", "VolB_Ontem", "RetAn_Ontem", "VolA_Ontem"]).reset_index(drop=True)


def ic_bootstrap_por_data(datas, acerto, maj) -> dict:
    """Sorteia DATAS com reposição e leva todos os papéis daquelas datas.
    Preserva a correlação transversal que a suposição de independência ignora."""
    cod, _ = pd.factorize(pd.Series(datas))      # datas viram códigos inteiros
    acerto = np.asarray(acerto, dtype=float)
    ordem = np.argsort(cod, kind="stable")
    cod_ord, acerto_ord = cod[ordem], acerto[ordem]
    # soma e contagem por data, para reamostrar sem reconstruir vetores
    n_datas = cod_ord.max() + 1
    soma = np.bincount(cod_ord, weights=acerto_ord, minlength=n_datas)
    cont = np.bincount(cod_ord, minlength=n_datas).astype(float)
    amostras = np.empty(B_BOOT)
    for b in range(B_BOOT):
        esc = RNG.integers(0, n_datas, n_datas)   # sorteia DATAS com reposição
        amostras[b] = soma[esc].sum() / cont[esc].sum()
    df = pd.DataFrame({"a": acerto})
    lo, hi = np.percentile(amostras, [2.5, 97.5])
    acc = float(df["a"].mean())
    # p bicaudal: fração de reamostras em que o modelo não supera a majoritária
    p = 2 * min((amostras <= maj).mean(), (amostras >= maj).mean())
    return {"n": int(len(df)), "n_datas": int(n_datas),
            "acuracia": round(acc, 4), "majoritaria": round(float(maj), 4),
            "ganho_pp": round((acc - maj) * 100, 2),
            "ic95_pp": [round((lo - maj) * 100, 2), round((hi - maj) * 100, 2)],
            "meia_largura_pp": round(float((hi - lo) / 2) * 100, 2),
            "p_bootstrap": round(float(min(p, 1.0)), 4)}


def main() -> None:
    # painel comum, alinhado nas datas em que todos os 10 existem
    partes = {tk: monta(tk) for tk in TOP10}
    datas_comuns = set.intersection(*[set(v["Data"]) for v in partes.values()])
    P = pd.concat([v[v["Data"].isin(datas_comuns)] for v in partes.values()], ignore_index=True)
    P = P.sort_values(["Data", "Ticker"]).reset_index(drop=True)
    datas = np.sort(P["Data"].unique())
    corte = datas[int(len(datas) * 0.75)]
    print(f"painel: {len(P):,} linhas | {len(datas):,} datas | 10 papéis")
    print(f"treino até {pd.Timestamp(corte).date()} | teste a partir daí "
          f"({(datas >= corte).sum()} datas)")
    print(f"betas de mercado estimados: " +
          ", ".join(f"{tk} {partes[tk]['beta_mercado'].iloc[0]:.2f}" for tk in TOP10))

    tr_m, te_m = P["Data"] < corte, P["Data"] >= corte
    res = {"n_painel": int(len(P)), "n_datas": int(len(datas)),
           "corte_treino": str(pd.Timestamp(corte).date()),
           "betas": {tk: round(float(partes[tk]["beta_mercado"].iloc[0]), 4) for tk in TOP10},
           "nota_inferencia": ("IC e p por bootstrap em blocos de DATA (2000 reamostras): "
                               "sorteiam-se datas com reposição levando todos os papéis, "
                               "preservando a correlação transversal de 0,486"),
           "arms": {}}

    ALVOS = [("retorno BRUTO", "Alvo_Bruto", ["Ret_Ontem", "VolB_Ontem"]),
             ("retorno ANORMAL (desconta o Ibovespa)", "Alvo_Anormal", ["RetAn_Ontem", "VolA_Ontem"])]
    dummies = pd.get_dummies(P["Ticker"], prefix="pap").astype(float)

    print(f"\n{'braço':62}{'ganho':>8}{'IC95%':>18}{'p':>8}")
    print("-" * 96)
    for alvo_nome, alvo, base in ALVOS:
        y = P[alvo].astype(int)
        maj_te = float(max(y[te_m].mean(), 1 - y[te_m].mean()))
        for feat_nome, cols in [("só preço", base), ("preço + sentimento", base + ["Sent", "Qtd"])]:
            for desenho in ["por papel", "painel (com efeito de ativo)"]:
                for mn in ["SVM", "XGBoost"]:
                    novo = (lambda: make_pipeline(StandardScaler(), SVC(kernel="rbf", random_state=42))) \
                        if mn == "SVM" else (lambda: XGBClassifier(**XGB))
                    pred = np.empty(int(te_m.sum()))
                    if desenho == "por papel":
                        for tk in TOP10:
                            m_tk = (P["Ticker"] == tk).values
                            mod = novo()
                            mod.fit(P.loc[tr_m & m_tk, cols], y[tr_m & m_tk])
                            pred[(P.loc[te_m, "Ticker"] == tk).values] = mod.predict(
                                P.loc[te_m & m_tk, cols])
                    else:
                        X = pd.concat([P[cols], dummies], axis=1)
                        mod = novo()
                        mod.fit(X[tr_m.values], y[tr_m])
                        pred = mod.predict(X[te_m.values])
                    acerto = (pred == y[te_m].values).astype(float)
                    nome = f"{mn} — {feat_nome} — {desenho} — {alvo_nome}"
                    res["arms"][nome] = ic_bootstrap_por_data(
                        P.loc[te_m, "Data"].values, acerto, maj_te)
                    v = res["arms"][nome]
                    print(f"{mn:8}{feat_nome:21}{desenho:30}{v['ganho_pp']:+7.2f}pp"
                          f"  [{v['ic95_pp'][0]:+6.2f},{v['ic95_pp'][1]:+6.2f}]{v['p_bootstrap']:>8.3f}")
        print()

    (DADOS / "retorno_anormal_e_painel.json").write_text(
        json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    print("gravado: dados/retorno_anormal_e_painel.json")


if __name__ == "__main__":
    main()
