# -*- coding: utf-8 -*-
# ==============================================================================
#   PROPHET COM ALVO ANORMAL — completa a reexecução da mentoria de 29/10/2026
#
#   O Prophet já havia falhado prevendo preço e volatilidade brutos (Script
#   23). Resta verificar se a troca do alvo para o retorno ANORMAL o salva,
#   como salvou parcialmente o SVM e o XGBoost no Script 27.
#
#   PREVISÃO REGISTRADA ANTES (e conferida na PETR4 antes de rodar os dez):
#   não salva. O Prophet decompõe a série em tendência e sazonalidade de
#   calendário; o retorno anormal é aproximadamente estacionário e de média
#   quase nula, de modo que não há tendência a extrapolar. O que se espera é
#   uma previsão de amplitude muito menor que a realidade — na PETR4, desvio
#   de 0,31 contra 1,65 do real, cinco vezes menor — e acerto abaixo do
#   palpite fixo (−1,93 pp na PETR4).
#
#   Saída: dados/prophet_alvo_anormal.json
# ==============================================================================
from __future__ import annotations

import json
import logging
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

logging.getLogger("prophet").setLevel(logging.ERROR)
logging.getLogger("cmdstanpy").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")
from prophet import Prophet  # noqa: E402

import importlib.util  # noqa: E402

AQUI = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("base", AQUI / "28_reexecucao_com_alvo_anormal.py")
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)

TOP10 = _base.TOP10
PASSO = 21


def roda(ticker: str) -> dict:
    d = _base.monta(ticker)
    n = len(d)
    te = slice(int(n * 0.75), n)
    serie = pd.DataFrame({"ds": d["Data"], "y": d["Ret_Anormal"] * 100})
    preds, pos = [], te.start
    while pos < te.stop:
        fim = min(pos + PASSO, te.stop)
        m = Prophet(daily_seasonality=False).fit(serie.iloc[:pos])
        preds.append(m.predict(pd.DataFrame({"ds": serie["ds"].iloc[pos:fim]}))["yhat"].values)
        pos = fim
    yhat = np.concatenate(preds)
    real = d["Ret_Anormal"].values[te] * 100
    alvo = (real > 0).astype(int)
    pred = (yhat > 0).astype(int)
    maj = float(max(alvo.mean(), 1 - alvo.mean()))
    acc = float((pred == alvo).mean())
    return {"n_teste": int(len(alvo)),
            "desvio_previsto": round(float(yhat.std()), 4),
            "desvio_real": round(float(real.std()), 4),
            "razao_amplitude": round(float(yhat.std() / real.std()), 3),
            "pct_previu_alta": round(float(pred.mean()) * 100, 1),
            "acuracia": round(acc, 4), "majoritaria": round(maj, 4),
            "ganho_pp": round((acc - maj) * 100, 2)}


def main() -> None:
    res = {"previsao_registrada_antes": (
        "o Prophet não deve ser salvo pela troca de alvo: o retorno anormal é quase estacionário "
        "e de média nula, sem tendência a extrapolar; espera-se amplitude muito menor que a real "
        "e acerto abaixo do palpite fixo"), "papeis": {}}
    for tk in TOP10:
        r = roda(tk)
        res["papeis"][tk] = r
        print(f"{tk}: amplitude prevista/real {r['razao_amplitude']:.2f}x | prevê alta em "
              f"{r['pct_previu_alta']:5.1f}% | acerto {r['acuracia']:.2%} vs palpite fixo "
              f"{r['majoritaria']:.2%} | ganho {r['ganho_pp']:+.2f}pp", flush=True)
    g = [v["ganho_pp"] for v in res["papeis"].values()]
    res["resumo"] = {"ganho_medio_pp": round(float(np.mean(g)), 2),
                     "papeis_positivos": int(sum(x > 0 for x in g)),
                     "razao_amplitude_media": round(
                         float(np.mean([v["razao_amplitude"] for v in res["papeis"].values()])), 3)}
    print(f"\nmédia {np.mean(g):+.2f}pp | positivos {sum(x > 0 for x in g)}/10 | "
          f"amplitude média {res['resumo']['razao_amplitude_media']:.2f}x da real")
    (AQUI / "dados" / "prophet_alvo_anormal.json").write_text(
        json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    print("gravado: dados/prophet_alvo_anormal.json")


if __name__ == "__main__":
    main()
