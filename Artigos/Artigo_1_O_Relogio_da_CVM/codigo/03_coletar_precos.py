# -*- coding: utf-8 -*-
# ==============================================================================
#   Etapa 6 — Preços completos: Abertura, Máxima, Mínima, Fechamento e Volume
#
#   Até aqui só tínhamos o fechamento. Faltam três coisas que o desenho pedido
#   pelos orientadores exige:
#
#     ABERTURA  -> permite isolar o GAP: ln(Abertura de d+1 / Fechamento de d).
#                  Para notícia divulgada após o fechamento, o gap é a reação
#                  PURA — ninguém pôde negociar antes da abertura.
#     MÁX e MÍN -> permitem o estimador de Parkinson, que mede a volatilidade
#                  do dia pelo intervalo percorrido, e não só pelo fechamento.
#                  É cerca de cinco vezes mais eficiente.
#     VOLUME    -> os orientadores pediram explicitamente. Volume anormal é a
#                  medida clássica de chegada de informação ao mercado.
#
#   Saída: CVM/dados/ohlcv_b3.csv  (formato longo: Data, Ticker, O, H, L, C, V)
# ==============================================================================
from __future__ import annotations

import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import requests
import urllib3
import yfinance as yf

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore")

AQUI = Path(__file__).resolve().parent
DADOS = AQUI / "dados"

INICIO, FIM = "2017-06-01", "2026-09-16"


def sessao() -> requests.Session:
    s = requests.Session()
    s.verify = False        # rede com proxy interceptador; ver Etapa 2
    s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    return s


def baixa(tk: str, s: requests.Session, tent: int = 4) -> pd.DataFrame | None:
    for k in range(1, tent + 1):
        try:
            h = yf.Ticker(tk, session=s).history(start=INICIO, end=FIM)
            if h is not None and not h.empty:
                h = h[["Open", "High", "Low", "Close", "Volume"]].copy()
                h.index = pd.to_datetime(h.index).tz_localize(None).normalize()
                return h
        except Exception:                                     # noqa: BLE001
            pass
        time.sleep(3 * k)
    return None


def main() -> None:
    print("=" * 76)
    print("ETAPA 6 — PREÇOS COMPLETOS (abertura, máxima, mínima, volume)")
    print("=" * 76)

    com = pd.read_csv(DADOS / "cvm_para_classificar.csv", dtype=str)
    tickers = sorted(com["Ticker"].dropna().unique())
    print(f"  {len(tickers)} papéis + Ibovespa\n")

    s = sessao()
    partes, falhou = [], []
    for i, t in enumerate(tickers + ["^BVSP"], start=1):
        nome = "IBOV" if t == "^BVSP" else t
        alvo = t if t == "^BVSP" else f"{t}.SA"
        h = baixa(alvo, s)
        if h is None or len(h) < 250:
            falhou.append(nome)
            print(f"  [{i:>2}/{len(tickers)+1}] {nome:8s} FALHOU")
        else:
            h = h.reset_index()
            h.columns = ["Data", "Abertura", "Maxima", "Minima", "Fechamento", "Volume"]
            h.insert(1, "Ticker", nome)
            partes.append(h)
            print(f"  [{i:>2}/{len(tickers)+1}] {nome:8s} {len(h):>5,} pregões")
        time.sleep(0.5)

    d = pd.concat(partes, ignore_index=True).sort_values(["Ticker", "Data"])

    # ── medidas derivadas, calculadas uma vez só ─────────────────────────────
    g = d.groupby("Ticker", group_keys=False)
    d["Fech_ant"] = g["Fechamento"].shift(1)

    # gap de abertura: reação à notícia da noite
    d["Gap"] = np.log(d["Abertura"] / d["Fech_ant"])
    # intradiário: o que veio depois da abertura
    d["Intradia"] = np.log(d["Fechamento"] / d["Abertura"])
    # pregão inteiro
    d["Retorno"] = np.log(d["Fechamento"] / d["Fech_ant"])

    # volatilidade de Parkinson: usa a amplitude do dia
    d["Parkinson"] = np.sqrt(
        (np.log(d["Maxima"] / d["Minima"]) ** 2) / (4 * np.log(2)))

    print("\n" + "-" * 76)
    print(f"  papéis coletados ... {d['Ticker'].nunique()}")
    if falhou:
        print(f"  sem dado ........... {', '.join(falhou)}")
    print(f"  período ............ {d['Data'].min():%Y-%m-%d} a {d['Data'].max():%Y-%m-%d}")
    print(f"  observações ........ {len(d):,}")
    print(f"  com volume > 0 ..... {(d['Volume'] > 0).mean():.1%}")

    d.to_csv(DADOS / "ohlcv_b3.csv", index=False, encoding="utf-8-sig")
    print(f"\n  gravado: ohlcv_b3.csv")


if __name__ == "__main__":
    main()
