# -*- coding: utf-8 -*-
# ==============================================================================
#   Etapa 2 — Preços dos papéis que têm comunicado na CVM
#
#   Coleta o histórico diário dos tickers mapeados, mais o IBOVESPA, que serve
#   de carteira de mercado no cálculo do retorno anormal.
#
#   Sobre o SSL: esta rede tem proxy que intercepta o tráfego, e o curl_cffi
#   usado pelo yfinance não valida o certificado do interceptador. Repete-se
#   aqui a solução já adotada em src/coleta/01_coleta_dados_financeiros_petr4.py
#   — sessão própria com verify=False. São dados públicos de mercado, sem
#   credencial em jogo.
#
#   Saída: CVM/dados/precos_b3.csv  e  precos_retornos.csv
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

INICIO, FIM = "2017-06-01", "2026-08-27"   # folga antes de 2018 p/ janela de estimação


def sessao() -> requests.Session:
    s = requests.Session()
    s.verify = False
    s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    return s


def baixa(ticker: str, s: requests.Session, tentativas: int = 3) -> pd.Series | None:
    for k in range(1, tentativas + 1):
        try:
            h = yf.Ticker(ticker, session=s).history(start=INICIO, end=FIM)
            if h is not None and not h.empty:
                c = h["Close"].copy()
                c.index = pd.to_datetime(c.index).tz_localize(None).normalize()
                return c
        except Exception:                                         # noqa: BLE001
            pass
        time.sleep(3 * k)
    return None


def main() -> None:
    print("=" * 76)
    print("ETAPA 2 — PREÇOS DIÁRIOS DOS PAPÉIS DA B3")
    print("=" * 76)

    com = pd.read_csv(DADOS / "cvm_para_classificar.csv")
    tickers = sorted(com["Ticker"].dropna().unique())
    print(f"  {len(tickers)} papéis + o índice Ibovespa\n")

    s = sessao()
    series, falhou = {}, []
    for i, t in enumerate(tickers + ["^BVSP"], start=1):
        nome = "IBOV" if t == "^BVSP" else t
        alvo = t if t == "^BVSP" else f"{t}.SA"
        c = baixa(alvo, s)
        if c is None or c.notna().sum() < 250:
            falhou.append(nome)
            print(f"  [{i:>2}/{len(tickers)+1}] {nome:8s} FALHOU")
        else:
            series[nome] = c
            print(f"  [{i:>2}/{len(tickers)+1}] {nome:8s} {c.notna().sum():>5,} pregões")
        time.sleep(0.6)

    if not series:
        raise SystemExit("nenhum papel coletado")

    fech = pd.DataFrame(series).sort_index()
    print("\n" + "-" * 76)
    print(f"  coletados ......... {len(series)} de {len(tickers)+1}")
    if falhou:
        print(f"  sem dado .......... {', '.join(falhou)}")
    print(f"  período ........... {fech.index.min().date()} a {fech.index.max().date()}")
    print(f"  pregões ........... {len(fech):,}")

    fech.to_csv(DADOS / "precos_b3.csv", encoding="utf-8-sig")

    ret = np.log(fech / fech.shift(1))
    longo = (ret.reset_index().rename(columns={"index": "Data", "Date": "Data"})
                .melt(id_vars="Data", var_name="Ticker", value_name="Retorno")
                .dropna())
    longo.to_csv(DADOS / "precos_retornos.csv", index=False, encoding="utf-8-sig")
    print(f"\n  gravados: precos_b3.csv e precos_retornos.csv ({len(longo):,} obs.)")

    disp = com["Ticker"].isin(series.keys())
    print(f"  comunicados com preço disponível: {disp.sum():,} de {len(com):,} "
          f"({disp.mean():.1%})")


if __name__ == "__main__":
    main()
