# -*- coding: utf-8 -*-
# ==============================================================================
#   Coleta de notícias para VALE3, ITUB4 e BBAS3
#
#   POR QUÊ: o teste da "CVM como filtro" deu o gradiente esperado — o ganho da
#   notícia triplica nas noites de Fato Relevante —, mas NÃO passou no teste
#   estatístico (p = 0,57). Com 393 noites só da PETR4 não há poder suficiente.
#   Estendendo para mais três papéis de grande porte, espera-se chegar a cerca
#   de 1.500 noites e dar ao teste a chance de decidir.
#
#   A ROTA: a mesma do corpus original — a API REST do WordPress que os portais
#   brasileiros expõem publicamente. Devolve o TIMESTAMP EXATO da publicação,
#   que é o que permite separar a notícia da noite da notícia do pregão.
#
#   CUIDADO COM OS TERMOS: "Vale" e "Banco do Brasil" são expressões comuns em
#   português — "vale a pena", "vale-refeição", notícia de governo. Por isso os
#   termos são precisos, e ainda assim tudo passa por um filtro de relevância
#   depois da coleta.
#
#   Saída: CVM/dados/noticias_3ativos.csv
# ==============================================================================
from __future__ import annotations

import html
import re
import time
import unicodedata
import warnings
from pathlib import Path

import pandas as pd
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore")

AQUI = Path(__file__).resolve().parent
DADOS = AQUI / "dados"
SAIDA = DADOS / "noticias_3ativos.csv"

INICIO, FIM = "2018-01-01T00:00:00", "2026-09-01T00:00:00"

PORTAIS = {
    "InfoMoney": ("https://www.infomoney.com.br/wp-json/wp/v2/posts", 0.25),
    "Exame": ("https://exame.com/wp-json/wp/v2/posts", 0.35),
    "MoneyTimes": ("https://www.moneytimes.com.br/wp-json/wp/v2/posts", 0.6),
}

# (termo, portais onde buscar) — termos amplos evitam o portal mais lento
BUSCAS = {
    "VALE3": [("VALE3", None), ("mineradora Vale", None),
              ("minério de ferro", None), ("Vale S.A.", None)],
    "ITUB4": [("ITUB4", None), ("Itaú Unibanco", None)],
    "BBAS3": [("BBAS3", None),
              ("Banco do Brasil", ["InfoMoney", "Exame"])],
}

# o texto precisa conter ao menos uma destas marcas para ser da empresa
RELEVANCIA = {
    "VALE3": ["vale3", "mineradora vale", "vale s.a", "vale sa", "minerio de ferro",
              "minério de ferro", "a vale ", "da vale ", "na vale ", "pela vale"],
    "ITUB4": ["itub4", "itau unibanco", "itaú unibanco", "banco itau", "banco itaú",
              "o itau", "o itaú", "do itau", "do itaú"],
    "BBAS3": ["bbas3", "banco do brasil", "bb seguridade", "o bb ", "do bb "],
}


def limpa(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", html.unescape(str(s or "")))
    return re.sub(r"\s+", " ", s).strip()


def sem_acento(s: str) -> str:
    return unicodedata.normalize("NFKD", s.lower()).encode("ascii", "ignore").decode()


def relevante(titulo: str, resumo: str, ticker: str) -> bool:
    alvo = sem_acento(f"{titulo} {resumo}")
    return any(sem_acento(m) in alvo for m in RELEVANCIA[ticker])


def sessao() -> requests.Session:
    s = requests.Session()
    s.verify = False
    s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                    "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"})
    return s


def colhe(s, url, termo, pausa, ticker, portal) -> list[dict]:
    fora, pag = [], 1
    while True:
        try:
            r = s.get(url, timeout=60, params={
                "search": termo, "per_page": 100, "page": pag,
                "after": INICIO, "before": FIM, "orderby": "date", "order": "desc",
                "_fields": "date,date_gmt,title,excerpt,link"})
            if r.status_code != 200:
                break
            itens = r.json()
            if not itens:
                break
            for it in itens:
                tit = limpa(it.get("title", {}).get("rendered", ""))
                res = limpa(it.get("excerpt", {}).get("rendered", ""))
                if not tit or not relevante(tit, res, ticker):
                    continue
                fora.append({"data_publicacao": it.get("date"),
                             "data_gmt": it.get("date_gmt"),
                             "ativo": ticker, "Fonte": f"WP_{portal}",
                             "dominio": portal, "termo_busca": termo,
                             "Titulo": tit, "Resumo": res,
                             "URL": it.get("link", "")})
            tot_pag = int(r.headers.get("X-WP-TotalPages", 0) or 0)
            if pag >= tot_pag or pag >= 400:
                break
            pag += 1
            time.sleep(pausa)
        except Exception:                                     # noqa: BLE001
            time.sleep(3)
            pag += 1
            if pag > 400:
                break
    return fora


def main() -> None:
    print("=" * 76)
    print("COLETA DE NOTÍCIAS — VALE3, ITUB4 e BBAS3")
    print("=" * 76)

    s = sessao()
    tudo, t0 = [], time.time()

    for ticker, buscas in BUSCAS.items():
        print(f"\n  ── {ticker} " + "─" * 58)
        for termo, so_em in buscas:
            portais = {k: v for k, v in PORTAIS.items()
                       if so_em is None or k in so_em}
            for portal, (url, pausa) in portais.items():
                n0 = len(tudo)
                tudo.extend(colhe(s, url, termo, pausa, ticker, portal))
                print(f"     {termo:<20} {portal:<11} "
                      f"{len(tudo)-n0:>6,} relevantes   "
                      f"({(time.time()-t0)/60:.0f} min)", flush=True)

    d = pd.DataFrame(tudo)
    antes = len(d)
    d["hash"] = (d["Titulo"].str.lower().str.replace(r"\W", "", regex=True)
                 + d["data_gmt"].astype(str).str[:10])
    d = d.drop_duplicates("hash").drop(columns="hash")

    print("\n" + "-" * 76)
    print(f"  colhidas ................ {antes:,}")
    print(f"  sem repetição ........... {len(d):,}")
    print(f"\n  por ativo:")
    for k, v in d["ativo"].value_counts().items():
        print(f"    {k:8s} {v:>7,}")
    print(f"\n  por portal:")
    for k, v in d["dominio"].value_counts().items():
        print(f"    {k:12s} {v:>7,}")

    d["dt"] = pd.to_datetime(d["data_gmt"], errors="coerce")
    print(f"\n  período: {d['dt'].min():%Y-%m-%d} a {d['dt'].max():%Y-%m-%d}")
    d = d.drop(columns="dt")
    d.to_csv(SAIDA, index=False, encoding="utf-8-sig")
    print(f"\n  gravado: {SAIDA.name}  ({SAIDA.stat().st_size // 1024} KB)")
    print(f"  tempo total: {(time.time()-t0)/60:.0f} min")


if __name__ == "__main__":
    main()
