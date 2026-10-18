# -*- coding: utf-8 -*-
# ==============================================================================
#   PROPHET × GARCH+SVM/XGBoost — pedido do Prof. Julio, mentoria 16/10/2026
#
#   Prophet NÃO classifica texto — é previsão de série temporal (Meta). Aqui
#   ele entra como mais um método de PREVISÃO, lado a lado com o que a
#   pesquisa já usa, nos três alvos pedidos: direção, volatilidade e preço.
#   O sentimento que entra como regressora do Prophet é o que o FinBERT JÁ
#   classificou nos comunicados da CVM (reaproveitado, não recalculado aqui).
#
#   Por alvo, o comparador "nativo" da pesquisa:
#     DIREÇÃO      — SVM-RBF e XGBoost (igual aos Scripts 20/22)
#     VOLATILIDADE — HAR de Corsi (GARCH), versão linear, igual em espírito
#                    ao Script 18 (sem a combinação quantílica, p/ caber nos
#                    10 papéis no tempo da mentoria)
#     PREÇO        — a previsão mais simples que existe: hoje repete amanhã
#                    (ingênua). Preço é quase um passeio aleatório — por isso
#                    ESTA é a régua, não um "achismo".
#
#   SOBRE O REAJUSTE DO PROPHET — isto NÃO é cosmético, é o que torna o
#   resultado válido. Um primeiro teste (registrado na memória do projeto)
#   ajustou o Prophet UMA vez e pediu para prever os 579 pregões de teste
#   inteiros de uma vez (quase 2 anos de leitura à frente, sem nunca se
#   reancorar) — a tendência disparou e o R²-OS veio em -8.325% e -69.604%,
#   um resultado degenerado, não um resultado ruim de verdade. Aqui o Prophet
#   é reajustado a cada ~21 pregões (janela expansiva: sempre do início até a
#   véspera do bloco previsto), prevendo só esse bloco por vez — nunca mais
#   que um mês à frente sem se reancorar. SVM, XGBoost e o HAR continuam
#   ajustados uma única vez (como sempre nesta pesquisa), porque não têm o
#   mesmo problema de deriva de tendência de longo prazo.
#
#   Saída: dados/prophet_vs_garch_svm_xgboost.json
# ==============================================================================
from __future__ import annotations

import json
import logging
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from arch import arch_model
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from xgboost import XGBClassifier

logging.getLogger("prophet").setLevel(logging.WARNING)
logging.getLogger("cmdstanpy").setLevel(logging.WARNING)
warnings.filterwarnings("ignore")
from prophet import Prophet  # noqa: E402

AQUI = Path(__file__).resolve().parent
DADOS = AQUI / "dados"

TOP10 = ["VALE3", "ITUB4", "PETR4", "SBSP3", "BBDC4", "B3SA3", "ITSA4",
         "BPAC11", "BBAS3", "ABEV3"]
PASSO_REAJUSTE = 21  # pregões entre reajustes do Prophet (~1 mês)

XGB = dict(n_estimators=300, max_depth=3, learning_rate=0.05, subsample=0.9,
           colsample_bytree=0.9, random_state=42, eval_metric="logloss", n_jobs=-1)

_OHLCV = pd.read_csv(DADOS / "ohlcv_b3.csv", parse_dates=["Data"])
_CVM_CASOS = pd.read_csv(DADOS / "rodada_A_casos.csv", low_memory=False,
                          usecols=["Protocolo_Entrega", "Ticker", "Categoria",
                                   "Entrega", "Pregao_reacao"])
_CVM_CASOS["Entrega"] = pd.to_datetime(_CVM_CASOS["Entrega"], errors="coerce")
_CVM_CASOS["Date"] = pd.to_datetime(_CVM_CASOS["Pregao_reacao"], errors="coerce")
_CVM_CLASS = pd.read_csv(DADOS / "cvm_classificado.csv", low_memory=False)


# ──────────────────────────────────────────────────────────────────────────────
def painel_preco(ticker: str) -> tuple[pd.DataFrame, dict]:
    px = _OHLCV[_OHLCV["Ticker"] == ticker].sort_values("Data").reset_index(drop=True)
    px = px[px["Retorno"].notna()].reset_index(drop=True)
    ret_pct = px["Retorno"].values * 100.0
    g = arch_model(ret_pct, vol="Garch", p=1, q=1, dist="t").fit(disp="off")
    px["Volatilidade_GARCH"] = g.conditional_volatility
    garch_params = {"omega": round(float(g.params["omega"]), 5),
                    "alpha": round(float(g.params["alpha[1]"]), 4),
                    "beta": round(float(g.params["beta[1]"]), 4)}
    return px[["Data", "Fechamento", "Retorno", "Volatilidade_GARCH"]].copy(), garch_params


def bloco_cvm_todos(ticker: str) -> pd.DataFrame:
    """Sentimento do FinBERT nos comunicados da CVM (todos), já classificado
    ANTES desta pesquisa — reaproveitado, não recalculado aqui."""
    a = _CVM_CASOS[_CVM_CASOS["Ticker"] == ticker].copy()
    a = a[a["Entrega"].notna() & a["Date"].notna()]
    a = a[a["Entrega"].dt.hour >= 17]
    c = a.merge(_CVM_CLASS[["Protocolo_Entrega", "p_pos", "p_neg"]],
                on="Protocolo_Entrega", how="inner")
    c["ism"] = c["p_pos"] - c["p_neg"]
    g = c.groupby("Date")
    f = pd.DataFrame({"CVM_Sentimento_Ontem": g["ism"].mean(), "CVM_Qtd_Ontem": g.size()}).reset_index()
    return f


def corta(n: int) -> tuple[slice, slice, slice]:
    a, b = int(n * 0.60), int(n * 0.75)
    return slice(0, a), slice(a, b), slice(b, n)


def mcnemar(y, a, b) -> dict:
    ca, cb = (np.asarray(a) == y), (np.asarray(b) == y)
    n01, n10 = int((~ca & cb).sum()), int((ca & ~cb).sum())
    if n01 + n10 == 0:
        return {"ganhou_novo": 0, "ganhou_antigo": 0, "p": 1.0}
    return {"ganhou_novo": n01, "ganhou_antigo": n10,
            "p": float(stats.binomtest(n01, n01 + n10, 0.5).pvalue)}


def r2os(erro, ref) -> float:
    return float(1 - (np.asarray(erro) ** 2).sum() / (np.asarray(ref) ** 2).sum())


def prophet_rolling(serie: pd.DataFrame, te: slice, usa_cvm: bool,
                     passo: int = PASSO_REAJUSTE) -> np.ndarray:
    """serie tem colunas Data, y, CVM_Sentimento_Ontem. Reajusta o Prophet a
    cada `passo` pregões, em janela EXPANSIVA (sempre do início até a véspera
    do bloco previsto), prevendo só esse bloco por vez. Nunca olha o futuro."""
    preds = np.full(te.stop - te.start, np.nan)
    pos = te.start
    while pos < te.stop:
        fim = min(pos + passo, te.stop)
        treino = serie.iloc[:pos]
        base_df = pd.DataFrame({"ds": treino["Data"], "y": treino["y"]})
        m = Prophet(daily_seasonality=False)
        if usa_cvm:
            base_df["cvm_sent"] = treino["CVM_Sentimento_Ontem"].values
            m.add_regressor("cvm_sent")
        m.fit(base_df)
        bloco = serie.iloc[pos:fim]
        fut = pd.DataFrame({"ds": bloco["Data"]})
        if usa_cvm:
            fut["cvm_sent"] = bloco["CVM_Sentimento_Ontem"].values
        preds[pos - te.start:fim - te.start] = m.predict(fut)["yhat"].values
        pos = fim
    return preds


def ingenua_ancorada(serie: pd.DataFrame, te: slice,
                      passo: int = PASSO_REAJUSTE) -> np.ndarray:
    """A régua JUSTA para o Prophet: repete o último valor conhecido ANTES do
    bloco, e segura esse valor pelo bloco inteiro — exatamente a mesma
    informação que o Prophet tem. Sem isto, a comparação seria desleal: a
    ingênua diária enxerga o fechamento de ontem todo dia, enquanto o Prophet,
    no 21º dia do bloco, ainda está olhando o que sabia 21 pregões atrás."""
    preds = np.full(te.stop - te.start, np.nan)
    pos = te.start
    while pos < te.stop:
        fim = min(pos + passo, te.stop)
        ancora = serie["y"].iloc[pos - 1]
        preds[pos - te.start:fim - te.start] = ancora
        pos = fim
    return preds


# ──────────────────────────────────────────────────────────────────────────────
def roda_tudo(ticker: str) -> dict:
    dp, garch_params = painel_preco(ticker)
    cvm = bloco_cvm_todos(ticker).rename(columns={"Date": "Data"})

    d = dp.merge(cvm, on="Data", how="left")
    d["CVM_Sentimento_Ontem"] = d["CVM_Sentimento_Ontem"].fillna(0.0)
    d["CVM_Qtd_Ontem"] = d["CVM_Qtd_Ontem"].fillna(0.0)
    d["Retorno_Ontem"] = d["Retorno"].shift(1) * 100.0
    d["Volatilidade_Ontem"] = d["Volatilidade_GARCH"].shift(1)
    d["Alvo"] = np.where(d["Retorno"] > 0, 1, 0)
    d = d.dropna(subset=["Retorno_Ontem", "Volatilidade_Ontem"]).reset_index(drop=True)
    tr, va, te = corta(len(d))
    fit = slice(0, te.start)
    yte_dir = d["Alvo"].astype(int).iloc[te].values
    maj = max(yte_dir.mean(), 1 - yte_dir.mean())

    # ── Prophet, reajustado por janela expansiva: preço e volatilidade ───────
    serie_preco = d[["Data", "Fechamento", "CVM_Sentimento_Ontem"]].rename(columns={"Fechamento": "y"})
    serie_vol = d[["Data", "Volatilidade_GARCH", "CVM_Sentimento_Ontem"]].rename(columns={"Volatilidade_GARCH": "y"})
    prev_preco = {usa: prophet_rolling(serie_preco, te, usa) for usa in (False, True)}
    prev_vol = {usa: prophet_rolling(serie_vol, te, usa) for usa in (False, True)}

    # ── DIREÇÃO ────────────────────────────────────────────────────────────
    BASE, CVM = ["Retorno_Ontem", "Volatilidade_Ontem"], ["CVM_Sentimento_Ontem", "CVM_Qtd_Ontem"]
    arms_dir, guarda = {}, {}
    for nome, cols, mod_nome in [("SVM (preço)", BASE, "SVM"), ("XGBoost (preço)", BASE, "XGB"),
                                  ("SVM (preço+CVM)", BASE + CVM, "SVM"),
                                  ("XGBoost (preço+CVM)", BASE + CVM, "XGB")]:
        mod = (make_pipeline(StandardScaler(), SVC(kernel="rbf", probability=True, random_state=42))
               if mod_nome == "SVM" else XGBClassifier(**XGB))
        X, y = d[cols].fillna(0.0), d["Alvo"].astype(int)
        mod.fit(X.iloc[fit], y.iloc[fit])
        pv = mod.predict(X.iloc[te])
        pp = mod.predict_proba(X.iloc[te])[:, 1]
        arms_dir[nome] = {"acuracia": round(float(accuracy_score(yte_dir, pv)), 4),
                          "auc": round(float(roc_auc_score(yte_dir, pp)), 4),
                          "pct_previu_alta": round(float(pv.mean()) * 100, 1),
                          "p_vs_majoritaria": float(stats.binomtest(
                              int((yte_dir == pv).sum()), len(yte_dir), maj).pvalue)}
        guarda[nome] = pv

    fech_ontem = d["Fechamento"].shift(1).iloc[te].values
    for nome, usa in [("Prophet (preço)", False), ("Prophet (preço+CVM)", True)]:
        pv = (prev_preco[usa] > fech_ontem).astype(int)
        arms_dir[nome] = {"acuracia": round(float(accuracy_score(yte_dir, pv)), 4), "auc": None,
                          "pct_previu_alta": round(float(pv.mean()) * 100, 1),
                          "p_vs_majoritaria": float(stats.binomtest(
                              int((yte_dir == pv).sum()), len(yte_dir), maj).pvalue)}
        guarda[nome] = pv

    melhor_classico = max(["SVM (preço)", "XGBoost (preço)"], key=lambda k: arms_dir[k]["acuracia"])
    mcn = {"Prophet(preço) supera o melhor entre SVM/XGB(preço)?":
               mcnemar(yte_dir, guarda[melhor_classico], guarda["Prophet (preço)"]),
           "CVM ajuda o Prophet na direção?":
               mcnemar(yte_dir, guarda["Prophet (preço)"], guarda["Prophet (preço+CVM)"])}
    direcao = {"n_teste": int(len(yte_dir)), "majoritaria": round(float(maj), 4),
              "melhor_classico": melhor_classico, "arms": arms_dir, "mcnemar": mcn}

    # ── VOLATILIDADE ──────────────────────────────────────────────────────
    yte_vol = d["Volatilidade_GARCH"].iloc[te].values
    v = d["Volatilidade_GARCH"]
    h_cols = pd.DataFrame({"har1": v.shift(1), "har5": v.shift(1).rolling(5).mean(),
                           "har22": v.shift(1).rolling(22).mean()})
    arms_vol = {}
    for nome, cols in [("HAR (GARCH, referência)", ["har1", "har5", "har22"]),
                       ("HAR + CVM", ["har1", "har5", "har22"])]:
        X = h_cols.copy()
        if "CVM" in nome:
            X["CVM_Sentimento_Ontem"] = d["CVM_Sentimento_Ontem"]
            X["CVM_Qtd_Ontem"] = d["CVM_Qtd_Ontem"]
        lin = LinearRegression().fit(X.iloc[fit].fillna(0), v.iloc[fit])
        pred = lin.predict(X.iloc[te].fillna(0))
        arms_vol[nome] = {"mae": round(float(np.abs(yte_vol - pred).mean()), 4),
                          "rmse": round(float(np.sqrt(((yte_vol - pred) ** 2).mean())), 4),
                          "_pred": pred}
    erro_ref_vol = yte_vol - arms_vol["HAR (GARCH, referência)"]["_pred"]
    # régua JUSTA p/ o Prophet: mesma informação (ancorada no início do bloco)
    pred_anc_vol = ingenua_ancorada(serie_vol, te)
    erro_anc_vol = yte_vol - pred_anc_vol
    arms_vol["Ingênua ancorada (mesma info do Prophet)"] = {
        "mae": round(float(np.abs(erro_anc_vol).mean()), 4),
        "rmse": round(float(np.sqrt((erro_anc_vol ** 2).mean())), 4), "_pred": pred_anc_vol}
    for nome, usa in [("Prophet (volatilidade)", False), ("Prophet (volatilidade+CVM)", True)]:
        erro = yte_vol - prev_vol[usa]
        arms_vol[nome] = {"mae": round(float(np.abs(erro).mean()), 4),
                          "rmse": round(float(np.sqrt((erro ** 2).mean())), 4), "_pred": prev_vol[usa]}
    for nome, v_ in arms_vol.items():
        e = yte_vol - v_["_pred"]
        v_["r2os_vs_HAR"] = round(r2os(e, erro_ref_vol) * 100, 2)
        v_["r2os_vs_ancorada"] = round(r2os(e, erro_anc_vol) * 100, 2)
        v_.pop("_pred", None)
    volatilidade = {"n_teste": int(len(yte_vol)), "arms": arms_vol}

    # ── PREÇO ─────────────────────────────────────────────────────────────
    yte_preco = d["Fechamento"].iloc[te].values
    erro_ref_preco = yte_preco - fech_ontem                     # ingênua DIÁRIA
    pred_anc_preco = ingenua_ancorada(serie_preco, te)
    erro_anc_preco = yte_preco - pred_anc_preco                 # ingênua ANCORADA (justa)
    arms_preco = {}
    for nome, pred in [("Ingênua diária (fechamento de ontem)", fech_ontem),
                       ("Ingênua ancorada (mesma info do Prophet)", pred_anc_preco),
                       ("Prophet (preço)", prev_preco[False]),
                       ("Prophet (preço+CVM)", prev_preco[True])]:
        erro = yte_preco - pred
        arms_preco[nome] = {
            "mae": round(float(np.abs(erro).mean()), 4),
            "rmse": round(float(np.sqrt((erro ** 2).mean())), 4),
            "r2os_vs_ingenua_diaria": round(r2os(erro, erro_ref_preco) * 100, 2),
            "r2os_vs_ancorada": round(r2os(erro, erro_anc_preco) * 100, 2)}
    preco = {"n_teste": int(len(yte_preco)), "arms": arms_preco}

    return {"garch": garch_params, "direcao": direcao, "volatilidade": volatilidade, "preco": preco}


def main() -> None:
    resultado = {
        "protocolo": (f"GARCH(1,1) próprio por papel; SVM/XGBoost/HAR ajustados uma vez "
                      f"(treino+validação); Prophet reajustado a cada {PASSO_REAJUSTE} pregões "
                      f"em janela expansiva, nunca prevendo mais que isso à frente sem se "
                      f"reancorar; split cronológico 60/15/25"),
        "papeis": {}}
    for tk in TOP10:
        print(f"\n{'='*90}\n  {tk}\n{'='*90}")
        r = roda_tudo(tk)
        print("  DIREÇÃO:", {k: v["acuracia"] for k, v in r["direcao"]["arms"].items()})
        print("  VOLATILIDADE (R²-OS vs ancorada, justo):",
              {k: v.get("r2os_vs_ancorada") for k, v in r["volatilidade"]["arms"].items()})
        print("  PREÇO (R²-OS vs ancorada, justo):",
              {k: v.get("r2os_vs_ancorada") for k, v in r["preco"]["arms"].items()})
        resultado["papeis"][tk] = r

    (DADOS / "prophet_vs_garch_svm_xgboost.json").write_text(
        json.dumps(resultado, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print("\n  gravado: dados/prophet_vs_garch_svm_xgboost.json")


if __name__ == "__main__":
    main()
