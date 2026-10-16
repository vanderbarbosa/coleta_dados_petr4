# -*- coding: utf-8 -*-
# ==============================================================================
#   PLANILHA — itens 1 e 2 do pedido do Prof. Julio (mentoria 12/10/2026):
#     1. número de ações médio por investidor (ações em circulação ÷ acionistas)
#     2. valor médio investido por investidor (nº médio de ações × preço da ação)
#
#   Fontes: CVM/dados/distribuicao_capital_papeis.csv (acionistas e ações —
#   Formulário de Referência da CVM) + CVM/dados/ohlcv_b3.csv (preço de
#   fechamento mais recente, 15/09/2026). Não inventa preço para quem não tem:
#   6 papéis (EMBR3, BRFS3, MRFG3, ELET3, AZUL4, GOLL4) têm investidor mas não
#   preço coletado — ficam marcados como "sem preço", não com valor estimado.
#
#   Grava 01_Valor_Medio_Investido.xlsx, nesta mesma pasta. 2 abas: Top 10
#   (destaque) e Todos os papéis (57 com preço + 6 sem preço, ao final).
# ==============================================================================
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
SAIDA = AQUI / "01_Valor_Medio_Investido.xlsx"

FONTE_NOME = "Arial"
AZUL_CAB = "1F3864"
AZUL_INPUT = "0000FF"
CINZA_CLARO = "F2F2F2"
AMARELO = "FFF2CC"
BORDA = Border(bottom=Side(style="thin", color="BFBFBF"))

TOP10 = ["VALE3", "ITUB4", "PETR4", "SBSP3", "BBDC4", "B3SA3", "ITSA4",
         "BPAC11", "BBAS3", "ABEV3"]

dist = pd.read_csv(RAIZ / "CVM" / "dados" / "distribuicao_capital_papeis.csv")
rec = dist.sort_values("Data_Referencia").drop_duplicates("Ticker", keep="last")
px = pd.read_csv(RAIZ / "CVM" / "dados" / "ohlcv_b3.csv",
                  usecols=["Data", "Ticker", "Fechamento"], parse_dates=["Data"])
ultimo_px = px.sort_values("Data").drop_duplicates("Ticker", keep="last")
DATA_PRECO = str(ultimo_px["Data"].max().date())

d = rec.merge(ultimo_px[["Ticker", "Fechamento"]], on="Ticker", how="left")
d = d.sort_values("Qtd_Acionistas_Total", ascending=False).reset_index(drop=True)


def cab(ws, titulos, larguras, linha=1):
    for c, (rot, larg) in enumerate(zip(titulos, larguras), start=1):
        col = get_column_letter(c)
        ws.column_dimensions[col].width = larg
        cel = ws.cell(row=linha, column=c, value=rot)
        cel.font = Font(name=FONTE_NOME, bold=True, size=10, color="FFFFFF")
        cel.fill = PatternFill("solid", fgColor=AZUL_CAB)
        cel.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cel.border = BORDA
    ws.row_dimensions[linha].height = 32
    ws.freeze_panes = ws.cell(row=linha + 1, column=1)


def escreve(ws, df, linha0, destaque_top10=False):
    r = linha0
    for _, row in df.iterrows():
        tem_preco = pd.notna(row["Fechamento"])
        cel_tk = ws.cell(row=r, column=1, value=row["Ticker"])
        cel_tk.font = Font(name=FONTE_NOME, bold=True, size=10)
        ws.cell(row=r, column=2, value=row["Nome_Companhia"]).font = Font(name=FONTE_NOME, size=10)
        ws.cell(row=r, column=3, value=row["Data_Ultima_Assembleia"]).font = Font(name=FONTE_NOME, size=10)

        c4 = ws.cell(row=r, column=4, value=int(row["Qtd_Acionistas_Total"]))
        c4.number_format = "#,##0"
        c4.font = Font(name=FONTE_NOME, size=10, color=AZUL_INPUT)

        c5 = ws.cell(row=r, column=5, value=int(row["Quantidade_Total_Acoes_Circulacao"]))
        c5.number_format = "#,##0"
        c5.font = Font(name=FONTE_NOME, size=10, color=AZUL_INPUT)

        # item 1 — FÓRMULA: ações em circulação ÷ acionistas
        c6 = ws.cell(row=r, column=6, value=f"=IFERROR(E{r}/D{r},\"\")")
        c6.number_format = "#,##0"
        c6.font = Font(name=FONTE_NOME, size=10)

        if tem_preco:
            c7 = ws.cell(row=r, column=7, value=float(row["Fechamento"]))
            c7.number_format = '"R$" #,##0.00'
            c7.font = Font(name=FONTE_NOME, size=10, color=AZUL_INPUT)
            # item 2 — FÓRMULA: nº médio de ações x preço da ação
            c8 = ws.cell(row=r, column=8, value=f"=F{r}*G{r}")
            c8.number_format = '"R$" #,##0'
            c8.font = Font(name=FONTE_NOME, size=10)
        else:
            ws.cell(row=r, column=7, value="sem preço coletado").font = Font(
                name=FONTE_NOME, size=9, italic=True, color="C00000")
            ws.cell(row=r, column=8, value="—").font = Font(name=FONTE_NOME, size=10)

        for c in range(4, 9):
            ws.cell(row=r, column=c).alignment = Alignment(horizontal="right")
        for c in range(1, 9):
            ws.cell(row=r, column=c).border = BORDA
        if (r - linha0) % 2 == 1:
            for c in range(1, 9):
                ws.cell(row=r, column=c).fill = PatternFill("solid", fgColor=CINZA_CLARO)
        if destaque_top10 and row["Ticker"] in TOP10:
            for c in range(1, 9):
                ws.cell(row=r, column=c).fill = PatternFill("solid", fgColor=AMARELO)
        r += 1
    return r


def nota(ws, linha, ncols=8):
    textos = [
        (f"Fontes: CVM/dados/distribuicao_capital_papeis.csv (Formulário de Referência da "
         f"CVM — acionistas e ações em circulação, por assembleia) + CVM/dados/ohlcv_b3.csv "
         f"(preço de fechamento em {DATA_PRECO}). Datas-base diferentes entre as duas fontes — "
         f"é a mesma limitação já registrada na planilha 16 da pasta de 16/09."),
        ("Item 1 e item 2 são FÓRMULA (colunas F e H) — recalculam se você editar os acionistas, "
         "as ações em circulação ou o preço."),
        ("CUIDADO AO LER A MÉDIA: é uma média simples sobre uma distribuição muito desigual — "
         "poucos acionistas grandes (controlador, fundos) puxam o número para cima. O investidor "
         "individual típico tem MENOS que essa média, não esse valor. Não temos, nesta base, como "
         "medir a mediana (só o total de ações e o total de acionistas, não a distribuição entre eles)."),
        ("6 papéis têm acionistas cadastrados mas não têm preço coletado nesta pesquisa — EMBR3, "
         "BRFS3, MRFG3, ELET3 (trocou para AXIA3), AZUL4, GOLL4. Aparecem no fim da aba 'Todos os "
         "papéis', sem item 2 calculado — não inventei preço para eles."),
    ]
    for i, t in enumerate(textos):
        cel = ws.cell(row=linha + i, column=1, value=t)
        cel.font = Font(name=FONTE_NOME, size=9, italic=True, color="595959")
        ws.merge_cells(start_row=linha + i, start_column=1, end_row=linha + i, end_column=ncols)
        ws.row_dimensions[linha + i].height = 28


titulos = ["Ticker", "Empresa", "Data da\nassembleia", "Acionistas\n(total)",
           "Ações em\ncirculação", "1. Ações por\ninvestidor\n(média)",
           "Preço atual\n(fechamento)", "2. Valor médio\ninvestido\n(média)"]
larg = [9, 32, 12, 12, 13, 13, 12, 14]

wb = Workbook()
ws0 = wb.active
ws0.title = "Top 10 (destaque)"
cab(ws0, titulos, larg)
top10_df = d[d["Ticker"].isin(TOP10)].copy()
top10_df["ordem"] = top10_df["Ticker"].map({t: i for i, t in enumerate(TOP10)})
top10_df = top10_df.sort_values("ordem")
fim = escreve(ws0, top10_df, 2)
nota(ws0, fim + 1)
ws0.auto_filter.ref = f"A1:{get_column_letter(8)}{fim-1}"

ws1 = wb.create_sheet("Todos os papéis (62)")
cab(ws1, titulos, larg)
com_preco = d[d["Fechamento"].notna()].sort_values("Qtd_Acionistas_Total", ascending=False)
sem_preco = d[d["Fechamento"].isna()].sort_values("Qtd_Acionistas_Total", ascending=False)
todos_df = pd.concat([com_preco, sem_preco])
fim1 = escreve(ws1, todos_df, 2, destaque_top10=True)
nota(ws1, fim1 + 1)
ws1.auto_filter.ref = f"A1:{get_column_letter(8)}{fim1-1}"

wb.save(SAIDA)
print(f"gravado: {SAIDA}  (top10: {len(top10_df)} linhas | todos: {len(todos_df)} linhas, "
      f"{len(sem_preco)} sem preço)")
