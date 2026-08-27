# -*- coding: utf-8 -*-
# ==============================================================================
#   Etapa 1 — Coleta dos comunicados da CVM (dados abertos oficiais)
#   Pedido do Prof. Emerson Paraiso (mentoria de 26/08/2026)
#
#   Fonte: dados.cvm.gov.br — IPE (Informações Periódicas e Eventuais).
#   São dados ABERTOS e oficiais; não há raspagem nem termo de uso a discutir.
#
#   O que interessa e por quê:
#     Fato Relevante ...... a Resolução CVM nº 44 obriga a companhia a divulgar
#                           todo fato capaz de INFLUIR na cotação. Ou seja: é o
#                           próprio regulador declarando que aquilo é relevante.
#     Comunicado ao Mercado  um degrau abaixo em obrigatoriedade, e serve de
#                           grupo de comparação natural.
#
#   Saída: CVM/dados/cvm_comunicados_2018_2026.csv
# ==============================================================================
from __future__ import annotations

import io
import re
import sys
import time
import unicodedata
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
DADOS = AQUI / "dados"
DADOS.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/IPE/DADOS/ipe_cia_aberta_{}.zip"
ANOS = range(2018, 2027)          # mesmo recorte do corpus de notícias
CATEGORIAS = ["Fato Relevante", "Comunicado ao Mercado"]

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

# ── mapa companhia -> papel negociado na B3 ─────────────────────────────────
# Trecho da razão social (normalizada) -> ticker principal. Cobre o grosso do
# Ibovespa; o que não casar fica com ticker vazio e não entra no estudo.
MAPA = {
    "petroleo brasileiro": "PETR4", "vale s a": "VALE3",
    "itau unibanco holding": "ITUB4", "banco bradesco": "BBDC4",
    "banco do brasil": "BBAS3", "ambev": "ABEV3",
    "b3 s a brasil bolsa balcao": "B3SA3", "weg s a": "WEGE3",
    "itausa": "ITSA4", "banco btg pactual": "BPAC11",
    "cia saneamento basico estado sao paulo": "SBSP3",
    "centrais eletricas brasileiras": "ELET3", "localiza": "RENT3",
    "suzano s a": "SUZB3", "rede d or": "RDOR3", "jbs s a": "JBSS3",
    "equatorial energia": "EQTL3", "petro rio": "PRIO3", "prio s a": "PRIO3",
    "rumo s a": "RAIL3", "gerdau s a": "GGBR4", "metalurgica gerdau": "GOAU4",
    "cosan": "CSAN3", "telefonica brasil": "VIVT3", "ultrapar": "UGPA3",
    "brf s a": "BRFS3", "klabin s a": "KLBN11", "cia energetica de minas gerais": "CMIG4",
    "cia paranaense de energia": "CPLE6", "totvs": "TOTS3", "embraer": "EMBR3",
    "sendas distribuidora": "ASAI3", "lojas renner": "LREN3",
    "natura cosmeticos": "NTCO3", "natura co": "NTCO3", "hapvida": "HAPV3",
    "ccr s a": "CCRO3", "magazine luiza": "MGLU3", "cyrela brazil": "CYRE3",
    "bb seguridade": "BBSE3", "banco santander brasil": "SANB11",
    "tim s a": "TIMS3", "energisa": "ENGI11", "cia siderurgica nacional": "CSNA3",
    "usinas siderurgicas de minas gerais": "USIM5", "brava energia": "BRAV3",
    "vibra energia": "VBBR3", "multiplan": "MULT3", "allos s a": "ALOS3",
    "sao martinho": "SMTO3", "raia drogasil": "RADL3", "hypera": "HYPE3",
    "cpfl energia": "CPFE3", "azul s a": "AZUL4", "slc agricola": "SLCE3",
    "minerva s a": "BEEF3", "marfrig": "MRFG3", "cvc brasil": "CVCB3",
    "cia brasileira de distribuicao": "PCAR3", "locaweb": "LWSA3",
    "yduqs": "YDUQ3", "cogna": "COGN3", "oi s a": "OIBR3", "light s a": "LIGT3",
    "eletrobras": "ELET3", "engie brasil": "EGIE3", "gol linhas": "GOLL4",
    "porto seguro": "PSSA3", "iguatemi": "IGTI11", "braskem": "BRKM5",
}


def normaliza(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9 ]", " ", s.lower()).strip()


def para_ticker(nome: str) -> str:
    n = normaliza(nome)
    n = re.sub(r"\s+", " ", n)
    for chave, tk in MAPA.items():
        if chave in n:
            return tk
    return ""


def baixa_ano(ano: int) -> pd.DataFrame | None:
    url = BASE_URL.format(ano)
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=120) as r:
            bruto = r.read()
    except Exception as e:                                        # noqa: BLE001
        print(f"  [FALHA] {ano}: {type(e).__name__} {str(e)[:60]}")
        return None

    z = zipfile.ZipFile(io.BytesIO(bruto))
    d = pd.read_csv(z.open(z.namelist()[0]), sep=";", encoding="latin-1",
                    low_memory=False)
    d = d[d["Categoria"].isin(CATEGORIAS)].copy()
    d["Ano"] = ano
    print(f"  [OK] {ano}: {len(d):>6,} comunicados  "
          f"({(d['Categoria'] == 'Fato Relevante').sum():>5,} fatos relevantes)")
    return d


def main() -> None:
    print("=" * 76)
    print("ETAPA 1 — COMUNICADOS DA CVM (dados abertos oficiais)")
    print("=" * 76)
    print(f"  fonte: dados.cvm.gov.br | anos {ANOS.start}–{ANOS.stop - 1}\n")

    partes = []
    for ano in ANOS:
        d = baixa_ano(ano)
        if d is not None:
            partes.append(d)
        time.sleep(1.0)

    if not partes:
        sys.exit("nenhum ano coletado")

    d = pd.concat(partes, ignore_index=True)
    d["Ticker"] = d["Nome_Companhia"].apply(para_ticker)
    d["Data_Entrega"] = pd.to_datetime(d["Data_Entrega"], errors="coerce")

    print("\n" + "-" * 76)
    print(f"  TOTAL ............................ {len(d):,}")
    print(f"    Fato Relevante ................. {(d['Categoria']=='Fato Relevante').sum():,}")
    print(f"    Comunicado ao Mercado .......... {(d['Categoria']=='Comunicado ao Mercado').sum():,}")
    print(f"  companhias distintas ............. {d['Nome_Companhia'].nunique():,}")
    print(f"  com ticker do Ibovespa mapeado ... {(d['Ticker'] != '').sum():,}"
          f"  ({(d['Ticker'] != '').mean():.1%})")
    print(f"  papéis distintos ................. {d.loc[d['Ticker']!='', 'Ticker'].nunique()}")
    print(f"  campo Assunto preenchido ......... {d['Assunto'].notna().mean():.1%}")

    print("\n  Papéis com mais comunicados:")
    for k, v in d.loc[d["Ticker"] != "", "Ticker"].value_counts().head(12).items():
        print(f"    {k:8s} {v:>5,}")

    saida = DADOS / "cvm_comunicados_2018_2026.csv"
    d.to_csv(saida, index=False, encoding="utf-8-sig")
    print(f"\n  gravado: {saida}")

    # subconjunto pronto para o classificador
    pronto = d[(d["Ticker"] != "") & d["Assunto"].notna()].copy()
    pronto = pronto[["Data_Entrega", "Ano", "Ticker", "Nome_Companhia", "Codigo_CVM",
                     "Categoria", "Tipo", "Especie", "Assunto", "Protocolo_Entrega",
                     "Link_Download"]]
    p2 = DADOS / "cvm_para_classificar.csv"
    pronto.sort_values("Data_Entrega").to_csv(p2, index=False, encoding="utf-8-sig")
    print(f"  gravado: {p2}  ({len(pronto):,} linhas prontas para o FinBERT)")


if __name__ == "__main__":
    main()
