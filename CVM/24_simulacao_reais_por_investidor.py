# -*- coding: utf-8 -*-
# ==============================================================================
#   QUANTO DARIA EM REAIS — pedido do Prof. Julio, mentoria de 23/10/2026
#
#   Aplica, sobre o VALOR MÉDIO INVESTIDO POR INVESTIDOR de cada papel (do
#   Formulário de Referência da CVM × preço), as decisões de cada modelo nos
#   579 pregões de teste, e mostra com quanto o investidor terminaria.
#
#   REGRA DA SIMULAÇÃO (a mais simples e realista para investidor comum):
#     "comprado quando o modelo prevê ALTA, fora do mercado quando prevê BAIXA"
#   A referência é comprar e segurar (buy-and-hold) — o que o investidor faria
#   sem modelo algum.
#
#   O QUE ESTA SIMULAÇÃO **NÃO** INCLUI, e precisa ser dito junto do número:
#   corretagem, emolumentos, imposto de renda, spread de compra e venda, e o
#   efeito de sair e entrar do mercado dezenas de vezes. Como o acerto
#   direcional dos modelos está perto de cara-ou-coroa, o resultado em reais é
#   em boa parte SORTE, não habilidade — ver a coluna de acerto na planilha.
#
#   Saída: dados/simulacao_reais_por_investidor.json
# ==============================================================================
from __future__ import annotations

import json
import logging
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from arch import arch_model
from sklearn.metrics import accuracy_score
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
PASSO = 21
XGB = dict(n_estimators=300, max_depth=3, learning_rate=0.05, subsample=0.9,
           colsample_bytree=0.9, random_state=42, eval_metric="logloss", n_jobs=-1)

_OHLCV = pd.read_csv(DADOS / "ohlcv_b3.csv", parse_dates=["Data"])
_CASOS = pd.read_csv(DADOS / "rodada_A_casos.csv", low_memory=False,
                      usecols=["Protocolo_Entrega", "Ticker", "Entrega", "Pregao_reacao"])
_CASOS["Entrega"] = pd.to_datetime(_CASOS["Entrega"], errors="coerce")
_CASOS["Data"] = pd.to_datetime(_CASOS["Pregao_reacao"], errors="coerce")
_CLASS = pd.read_csv(DADOS / "cvm_classificado.csv", low_memory=False)
_DIST = pd.read_csv(DADOS / "distribuicao_capital_papeis.csv")


def painel(ticker: str) -> pd.DataFrame:
    px = _OHLCV[_OHLCV["Ticker"] == ticker].sort_values("Data").reset_index(drop=True)
    px = px[px["Retorno"].notna()].reset_index(drop=True)
    g = arch_model(px["Retorno"].values * 100.0, vol="Garch", p=1, q=1, dist="t").fit(disp="off")
    px["Volatilidade_GARCH"] = g.conditional_volatility

    a = _CASOS[_CASOS["Ticker"] == ticker].copy()
    a = a[a["Entrega"].notna() & a["Data"].notna() & (a["Entrega"].dt.hour >= 17)]
    c = a.merge(_CLASS[["Protocolo_Entrega", "p_pos", "p_neg"]], on="Protocolo_Entrega", how="inner")
    c["ism"] = c["p_pos"] - c["p_neg"]
    cvm = c.groupby("Data").agg(CVM_Sentimento_Ontem=("ism", "mean"),
                                 CVM_Qtd_Ontem=("ism", "size")).reset_index()

    d = px.merge(cvm, on="Data", how="left")
    d[["CVM_Sentimento_Ontem", "CVM_Qtd_Ontem"]] = d[["CVM_Sentimento_Ontem", "CVM_Qtd_Ontem"]].fillna(0.0)
    d["Retorno_Ontem"] = d["Retorno"].shift(1) * 100.0
    d["Volatilidade_Ontem"] = d["Volatilidade_GARCH"].shift(1)
    d["Alvo"] = np.where(d["Retorno"] > 0, 1, 0)
    return d.dropna(subset=["Retorno_Ontem", "Volatilidade_Ontem"]).reset_index(drop=True)


def corta(n):
    return slice(0, int(n * 0.60)), slice(int(n * 0.60), int(n * 0.75)), slice(int(n * 0.75), n)


def prophet_direcao(d: pd.DataFrame, te: slice) -> np.ndarray:
    preds = np.full(te.stop - te.start, np.nan)
    pos = te.start
    while pos < te.stop:
        fim = min(pos + PASSO, te.stop)
        tr = d.iloc[:pos]
        m = Prophet(daily_seasonality=False)
        m.fit(pd.DataFrame({"ds": tr["Data"], "y": tr["Fechamento"]}))
        preds[pos - te.start:fim - te.start] = m.predict(
            pd.DataFrame({"ds": d["Data"].iloc[pos:fim]}))["yhat"].values
        pos = fim
    return (preds > d["Fechamento"].shift(1).iloc[te].values).astype(int)


def simula(ret: np.ndarray, sinal: np.ndarray) -> float:
    """Comprado quando o modelo prevê alta, fora quando prevê baixa.
    Devolve o fator multiplicador final sobre o capital inicial."""
    return float(np.prod(1.0 + ret * sinal))


def main() -> None:
    recente = _DIST.sort_values("Data_Referencia").drop_duplicates("Ticker", keep="last")
    ult_px = _OHLCV.sort_values("Data").drop_duplicates("Ticker", keep="last")
    res = {"regra": "comprado quando prevê alta, fora do mercado quando prevê baixa",
           "ressalva": ("não inclui corretagem, emolumentos, imposto de renda nem spread; "
                        "com acerto direcional perto de cara-ou-coroa, o resultado em reais é "
                        "em boa parte sorte"),
           "papeis": {}}

    for tk in TOP10:
        d = painel(tk)
        tr, va, te = corta(len(d))
        fit = slice(0, te.start)
        y = d["Alvo"].astype(int)
        yte = y.iloc[te].values
        ret = d["Retorno"].iloc[te].values

        BASE = ["Retorno_Ontem", "Volatilidade_Ontem"]
        CVM = BASE + ["CVM_Sentimento_Ontem", "CVM_Qtd_Ontem"]
        sinais = {}
        for nome, cols, kind in [("SVM (preço)", BASE, "svm"), ("XGBoost (preço)", BASE, "xgb"),
                                  ("SVM (preço+CVM)", CVM, "svm"), ("XGBoost (preço+CVM)", CVM, "xgb")]:
            mod = (make_pipeline(StandardScaler(), SVC(kernel="rbf", random_state=42))
                   if kind == "svm" else XGBClassifier(**XGB))
            X = d[cols].fillna(0.0)
            mod.fit(X.iloc[fit], y.iloc[fit])
            sinais[nome] = mod.predict(X.iloc[te])
        sinais["Prophet (preço)"] = prophet_direcao(d, te)

        melhor = max(sinais, key=lambda k: accuracy_score(yte, sinais[k]))
        valor = float(recente.loc[recente["Ticker"] == tk, "Media_Acoes_Por_Acionista"].iloc[0]) \
            * float(ult_px.loc[ult_px["Ticker"] == tk, "Fechamento"].iloc[0])

        papel = {"valor_investido_medio": round(valor, 2),
                 "melhor_modelo": melhor,
                 "buy_and_hold": {"fator": round(simula(ret, np.ones_like(ret)), 4)},
                 "modelos": {}}
        papel["buy_and_hold"]["final_reais"] = round(valor * papel["buy_and_hold"]["fator"], 2)
        papel["buy_and_hold"]["resultado_reais"] = round(
            valor * (papel["buy_and_hold"]["fator"] - 1), 2)
        for nome, s in sinais.items():
            f = simula(ret, s)
            papel["modelos"][nome] = {
                "acuracia": round(float(accuracy_score(yte, s)), 4),
                "dias_comprado": int(s.sum()),
                "fator": round(f, 4),
                "final_reais": round(valor * f, 2),
                "resultado_reais": round(valor * (f - 1), 2),
                "vs_buy_and_hold_reais": round(valor * (f - papel["buy_and_hold"]["fator"]), 2)}
        res["papeis"][tk] = papel
        print(f"{tk}: investido R$ {valor:,.0f} | B&H R$ {papel['buy_and_hold']['resultado_reais']:+,.0f} | "
              f"Prophet R$ {papel['modelos']['Prophet (preço)']['resultado_reais']:+,.0f} | "
              f"{melhor} R$ {papel['modelos'][melhor]['resultado_reais']:+,.0f}", flush=True)

    (DADOS / "simulacao_reais_por_investidor.json").write_text(
        json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    print("gravado: dados/simulacao_reais_por_investidor.json", flush=True)


if __name__ == "__main__":
    main()
