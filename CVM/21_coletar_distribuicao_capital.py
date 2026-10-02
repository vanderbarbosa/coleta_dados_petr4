# -*- coding: utf-8 -*-
# ==============================================================================
#   DISTRIBUIÇÃO DE CAPITAL — quantos acionistas, e quantas ações cada um tem
#   em média — pedido do Prof. Julio em 30/09/2026, item 1.
#
#   FONTE: dados abertos da CVM, conjunto "Formulário de Referência" (FRE),
#   arquivo fre_cia_aberta_distribuicao_capital_{ano}.csv — o mesmo portal
#   dados.cvm.gov.br já usado para os Fatos Relevantes (IPE). É a informação
#   que o item 6.3 do Formulário de Referência obriga toda companhia aberta a
#   declarar, na data da última assembleia: quantos acionistas pessoa física,
#   pessoa jurídica e investidores institucionais ela tem, e quantas ações
#   estão em circulação (free float), por classe (ON/PN) e no total.
#
#   LIMITAÇÃO IMPORTANTE, e não é desta coleta — é da própria norma: a CVM
#   OBRIGA separar as AÇÕES por classe (ordinária × preferencial), mas NÃO
#   obriga separar a CONTAGEM DE ACIONISTAS por classe. Ou seja: dá para saber
#   quantas ações PN (PETR4) e ON (PETR3) estão em circulação, separadamente,
#   mas não quantos acionistas são especificamente "só de PETR4" — só o total
#   de acionistas da Petrobras como empresa (que podem ter as duas classes).
#   Isso vale para qualquer papel do estudo com mais de uma classe de ação.
#
#   O número também é por ASSEMBLEIA (em geral 1x por ano, às vezes mais), não
#   diário — diferente do restante da pesquisa, que é por pregão.
#
#   Saída: dados/distribuicao_capital_papeis.csv e .json (resumo)
# ==============================================================================
from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path

import pandas as pd
import requests

requests.packages.urllib3.disable_warnings()  # proxy desta rede intercepta SSL

AQUI = Path(__file__).resolve().parent
DADOS = AQUI / "dados"
ANOS = range(2018, 2027)
URL = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FRE/DADOS/fre_cia_aberta_{ano}.zip"


def baixa_ano(ano: int) -> pd.DataFrame | None:
    print(f"  {ano} ...", end=" ", flush=True)
    try:
        r = requests.get(URL.format(ano=ano), verify=False, timeout=90)
        r.raise_for_status()
        z = zipfile.ZipFile(io.BytesIO(r.content))
        nome = f"fre_cia_aberta_distribuicao_capital_{ano}.csv"
        d = pd.read_csv(z.open(nome), sep=";", encoding="cp1252")
        print(f"{len(d):,} linhas")
        return d
    except Exception as e:
        print(f"FALHOU ({e})")
        return None


def main() -> None:
    # os 62 CNPJs/tickers já mapeados no projeto (mesma fonte do Artigo 1)
    ipe = pd.read_csv(DADOS / "cvm_comunicados_2018_2026.csv",
                       usecols=["CNPJ_Companhia", "Ticker"], dtype=str).drop_duplicates()
    mapa = ipe.dropna().drop_duplicates("CNPJ_Companhia")
    print(f"  papéis mapeados no projeto: {mapa['Ticker'].nunique()}")

    print("\n  baixando fre_cia_aberta_distribuicao_capital de cada ano:")
    partes = [d for d in (baixa_ano(a) for a in ANOS) if d is not None]
    todos = pd.concat(partes, ignore_index=True)

    # uma linha por companhia/data de referência (a versão mais recente, se
    # a companhia reapresentou o formulário)
    todos = (todos.sort_values("Versao")
                  .drop_duplicates(["CNPJ_Companhia", "Data_Referencia"], keep="last"))

    d = todos.merge(mapa, on="CNPJ_Companhia", how="inner")
    print(f"\n  linhas após filtrar pelos papéis do projeto: {len(d):,}"
          f"  ({d['Ticker'].nunique()} papéis, {d['CNPJ_Companhia'].nunique()} empresas)")

    d["Qtd_Acionistas_Total"] = (d["Quantidade_Acionistas_PF"]
                                 + d["Quantidade_Acionistas_PJ"]
                                 + d["Quantidade_Acionistas_Investidores_Institucionais"])
    d["Media_Acoes_Por_Acionista"] = (d["Quantidade_Total_Acoes_Circulacao"]
                                      / d["Qtd_Acionistas_Total"].replace(0, pd.NA))

    cols = ["Ticker", "Nome_Companhia", "Data_Referencia", "Qtd_Acionistas_Total",
            "Quantidade_Acionistas_PF", "Quantidade_Acionistas_PJ",
            "Quantidade_Acionistas_Investidores_Institucionais",
            "Quantidade_Acoes_Ordinarias_Circulacao",
            "Quantidade_Acoes_Preferenciais_Circulacao",
            "Quantidade_Total_Acoes_Circulacao", "Percentual_Total_Acoes_Circulacao",
            "Media_Acoes_Por_Acionista"]
    d = d[cols].sort_values(["Ticker", "Data_Referencia"])
    d.to_csv(DADOS / "distribuicao_capital_papeis.csv", index=False, encoding="utf-8-sig")

    # resumo: a leitura mais recente de cada papel
    recente = d.sort_values("Data_Referencia").drop_duplicates("Ticker", keep="last")
    print(f"\n  {'Ticker':<8} {'data-base':<11} {'acionistas':>11} {'ações (mi)':>12} "
          f"{'ações/acionista':>16}")
    print("  " + "-" * 64)
    for _, r in recente.sort_values("Qtd_Acionistas_Total", ascending=False).head(15).iterrows():
        print(f"  {r['Ticker']:<8} {r['Data_Referencia']:<11} {r['Qtd_Acionistas_Total']:>11,.0f} "
              f"{r['Quantidade_Total_Acoes_Circulacao']/1e6:>12,.1f} "
              f"{r['Media_Acoes_Por_Acionista']:>16,.0f}")

    resumo = {
        "fonte": "dados.cvm.gov.br — Formulário de Referência (FRE), item distribuição de capital",
        "n_papeis": int(recente["Ticker"].nunique()),
        "periodicidade": "por assembleia (normalmente 1x/ano), não por pregão",
        "limitacao": ("a quantidade de acionistas é por EMPRESA, não por classe de ação "
                     "(ON x PN); só a quantidade de AÇÕES em circulação é separada por classe"),
        "papeis": recente.set_index("Ticker").to_dict(orient="index"),
    }
    (DADOS / "distribuicao_capital_resumo.json").write_text(
        json.dumps(resumo, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"\n  gravados: dados/distribuicao_capital_papeis.csv "
          f"({len(d):,} linhas) e dados/distribuicao_capital_resumo.json")


if __name__ == "__main__":
    main()
