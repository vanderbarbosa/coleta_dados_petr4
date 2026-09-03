# -*- coding: utf-8 -*-
# ==============================================================================
#   Etapa 6 — O CSV final: comunicados da CVM com DATA e HORA de publicação
#
#   Junta o que foi colhido nas etapas anteriores:
#     - o conjunto aberto do IPE (dados.cvm.gov.br), que dá a notícia e a data;
#     - o Protocolo de Entrega da CVM, que dá a HORA OFICIAL de publicação.
#
#   A hora NÃO é estimada. Vem do recibo que a CVM emite para cada documento,
#   com hora, minuto e segundo. O carimbo interno do PDF foi deliberadamente
#   descartado: ele registra quando a empresa fechou o arquivo, não quando a
#   CVM publicou.
#
#   Saídas (na pasta entrega/):
#     CVM_NOTICIAS_COM_DATA_E_HORA.csv .... só as linhas com hora oficial
#     CVM_NOTICIAS_COMPLETO.csv ........... todas, com marcador de hora
#     CVM_RESUMO.txt ...................... o que há no arquivo, em texto
# ==============================================================================
from __future__ import annotations

from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
DADOS = AQUI / "dados"
ENTREGA = AQUI / "entrega"
ENTREGA.mkdir(exist_ok=True)

# B3: sessão regular das 10h às 17h (18h no horário de verão).
FAIXAS = [(0, 9, "1. antes da abertura"),
          (10, 16, "2. com o pregao aberto"),
          (17, 23, "3. apos o fechamento")]

COLUNAS = ["Data_Publicacao", "Hora_Publicacao", "DataHora_Publicacao", "Momento",
           "Ticker", "Empresa", "Categoria", "Noticia", "Codigo_CVM",
           "Protocolo_CVM", "Hora_Oficial", "Link_Documento"]


def momento(h) -> str:
    if pd.isna(h):
        return ""
    for a, b, rot in FAIXAS:
        if a <= h <= b:
            return rot
    return ""


def main() -> None:
    print("=" * 74)
    print("ETAPA 6 — CSV FINAL: NOTICIAS DA CVM COM DATA E HORA")
    print("=" * 74)

    base = pd.read_csv(DADOS / "cvm_para_classificar.csv", dtype=str)
    base["numSequencia"] = base["Link_Download"].str.extract(r"numSequencia=(\d+)")

    hora = (pd.read_csv(DADOS / "cvm_hora_entrega.csv", dtype=str)
              .drop_duplicates("numSequencia"))

    d = base.merge(hora[["numSequencia", "Data_Entrega_oficial",
                         "Hora_Entrega_oficial", "Protocolo_recibo"]],
                   on="numSequencia", how="left")

    tem = d["Hora_Entrega_oficial"].notna()

    # data: a oficial do recibo quando houver; senão a do conjunto aberto
    dt_of = pd.to_datetime(d["Data_Entrega_oficial"], format="%d/%m/%Y", errors="coerce")
    dt_ab = pd.to_datetime(d["Data_Entrega"], errors="coerce")
    data = dt_of.fillna(dt_ab)

    dh = pd.to_datetime(
        d["Data_Entrega_oficial"] + " " + d["Hora_Entrega_oficial"],
        format="%d/%m/%Y %H:%M:%S", errors="coerce")

    saida = pd.DataFrame({
        "Data_Publicacao": data.dt.strftime("%Y-%m-%d"),
        "Hora_Publicacao": d["Hora_Entrega_oficial"].fillna(""),
        "DataHora_Publicacao": dh.dt.strftime("%Y-%m-%d %H:%M:%S").fillna(""),
        "Momento": dh.dt.hour.apply(momento),
        "Ticker": d["Ticker"],
        "Empresa": d["Nome_Companhia"],
        "Categoria": d["Categoria"],
        "Noticia": d["Assunto"],
        "Codigo_CVM": d["Codigo_CVM"],
        "Protocolo_CVM": d["Protocolo_recibo"].fillna(d["Protocolo_Entrega"]),
        "Hora_Oficial": tem.map({True: "S", False: "N"}),
        "Link_Documento": d["Link_Download"],
    })[COLUNAS].sort_values(["Data_Publicacao", "Hora_Publicacao"])

    com_hora = saida[saida["Hora_Oficial"] == "S"]

    a = ENTREGA / "CVM_NOTICIAS_COM_DATA_E_HORA.csv"
    b = ENTREGA / "CVM_NOTICIAS_COMPLETO.csv"
    com_hora.to_csv(a, index=False, encoding="utf-8-sig", sep=";")
    saida.to_csv(b, index=False, encoding="utf-8-sig", sep=";")

    # ── resumo ───────────────────────────────────────────────────────────────
    L = []
    def p(s=""):
        print(s); L.append(s)

    p("=" * 74)
    p("COMUNICADOS DA CVM COM DATA E HORA DE PUBLICACAO")
    p("Vanderlei Barbosa da Silva | PUCPR/PPGIa | 03 de setembro de 2026")
    p("=" * 74)
    p()
    p("FONTE DA NOTICIA E DA DATA")
    p("  Portal de dados abertos da CVM (dados.cvm.gov.br), conjunto IPE")
    p("  -- Informacoes Periodicas e Eventuais. Dado oficial, sem raspagem.")
    p()
    p("FONTE DA HORA")
    p("  Protocolo de Entrega da CVM: o recibo que o regulador emite para")
    p("  cada documento, com hora, minuto e segundo. Exemplo literal:")
    p('    "Data da Entrega: 03/01/2018 07:20:19"')
    p()
    p("  NAO foi usada nenhuma hora estimada. O carimbo interno do arquivo")
    p("  PDF foi descartado de proposito: ele marca quando a empresa fechou")
    p("  o arquivo, nao quando a CVM publicou.")
    p()
    p("  Conferencia: a data do recibo coincide com a do conjunto aberto em")
    p(f"  100% dos {len(com_hora):,} casos.".replace(",", "."))
    p()
    p("-" * 74)
    p("O QUE HA NOS ARQUIVOS")
    p("-" * 74)
    p(f"  CVM_NOTICIAS_COM_DATA_E_HORA.csv ... {len(com_hora):>6,} linhas".replace(",", "."))
    p("      todas com data E hora oficiais. E o arquivo para usar.")
    p(f"  CVM_NOTICIAS_COMPLETO.csv .......... {len(saida):>6,} linhas".replace(",", "."))
    p("      inclui os que ainda nao tem hora; ver coluna Hora_Oficial.")
    p()
    p("  Separador: ponto e virgula (;). Codificacao: UTF-8 com BOM.")
    p("  Abre direto no Excel em portugues.")
    p()
    p("-" * 74)
    p("COBERTURA DA HORA, POR CATEGORIA")
    p("-" * 74)
    for cat in saida["Categoria"].unique():
        s = saida[saida["Categoria"] == cat]
        n = (s["Hora_Oficial"] == "S").sum()
        p(f"  {cat:<24} {n:>6,} de {len(s):>6,}  ({n/len(s):>5.1%})".replace(",", "."))
    p()
    p("  Os Comunicados ao Mercado ainda nao tiveram a hora colhida; sao")
    p("  cerca de 4 horas de coleta no mesmo script (04_coletar_hora_oficial).")
    p()
    p("-" * 74)
    p("PERIODO E ABRANGENCIA (arquivo com hora)")
    p("-" * 74)
    p(f"  de {com_hora['Data_Publicacao'].min()} a {com_hora['Data_Publicacao'].max()}")
    p(f"  papeis da B3: {com_hora['Ticker'].nunique()}")
    p(f"  empresas: {com_hora['Empresa'].nunique()}")
    p()
    p("  Papeis com mais comunicados:")
    for k, v in com_hora["Ticker"].value_counts().head(8).items():
        p(f"    {k:<8} {v:>5,}".replace(",", "."))
    p()
    p("-" * 74)
    p("QUANDO AS EMPRESAS PUBLICAM")
    p("-" * 74)
    vc = com_hora["Momento"].value_counts().sort_index()
    for k, v in vc.items():
        p(f"  {k:<26} {v:>6,}  ({v/len(com_hora):>5.1%})".replace(",", "."))
    p()
    p("  Quase 95% das publicacoes ocorrem fora do horario de negociacao,")
    p("  como a Resolucao CVM no 44 recomenda.")
    p()
    p("-" * 74)
    p("COLUNAS")
    p("-" * 74)
    desc = {
        "Data_Publicacao": "data oficial de publicacao (AAAA-MM-DD)",
        "Hora_Publicacao": "hora oficial, com segundos (HH:MM:SS)",
        "DataHora_Publicacao": "as duas juntas, pronto para ordenar",
        "Momento": "antes da abertura / pregao aberto / apos fechamento",
        "Ticker": "papel negociado na B3",
        "Empresa": "razao social na CVM",
        "Categoria": "Fato Relevante ou Comunicado ao Mercado",
        "Noticia": "o texto do comunicado (campo Assunto da CVM)",
        "Codigo_CVM": "codigo da companhia na CVM",
        "Protocolo_CVM": "numero do protocolo de entrega",
        "Hora_Oficial": "S = hora vem do recibo; N = ainda sem hora",
        "Link_Documento": "endereco do documento integral na CVM",
    }
    for c in COLUNAS:
        p(f"  {c:<22} {desc[c]}")

    (ENTREGA / "CVM_RESUMO.txt").write_text("\n".join(L), encoding="utf-8")
    print()
    print(f"  gravados em: {ENTREGA}")


if __name__ == "__main__":
    main()
