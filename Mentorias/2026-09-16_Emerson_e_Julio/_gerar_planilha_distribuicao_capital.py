# -*- coding: utf-8 -*-
# ==============================================================================
#   PLANILHA — distribuição de capital: acionistas e ações por papel (item 1
#   do pedido do Prof. Julio, 30/09/2026). Lê CVM/CVM/21_coletar_distribuicao
#   _capital.py e grava 16_Distribuicao_de_Capital.xlsx, nesta mesma pasta.
#
#   Três abas:
#     Resumo (62 papéis)      — leitura mais recente de cada papel
#     PETR4 - Série Histórica — todas as leituras da Petrobras, 2018-2026
#     Todos os papéis         — as 675 linhas brutas, para filtrar no Excel
#
#   A coluna "Ações por acionista" é FÓRMULA (ações totais ÷ acionistas totais),
#   não valor calculado em Python — recalcula se alguém editar a planilha.
# ==============================================================================
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
FONTE_CSV = RAIZ / "CVM" / "dados" / "distribuicao_capital_papeis.csv"
SAIDA = AQUI / "16_Distribuicao_de_Capital.xlsx"

FONTE_NOME = "Arial"
AZUL = "1F3864"
CINZA_CLARO = "F2F2F2"
BORDA = Border(bottom=Side(style="thin", color="BFBFBF"))

COLS = [
    ("Ticker", "Ticker", 10, "@"),
    ("Nome_Companhia", "Empresa", 34, "@"),
    ("Data_Referencia", "Data-base", 12, "@"),
    ("Quantidade_Acionistas_PF", "Acionistas\npessoa física", 14, "#,##0"),
    ("Quantidade_Acionistas_PJ", "Acionistas\npessoa jurídica", 14, "#,##0"),
    ("Quantidade_Acionistas_Investidores_Institucionais", "Acionistas\ninstitucionais", 14, "#,##0"),
    ("Qtd_Acionistas_Total", "Acionistas\n(total)", 13, "#,##0"),
    ("Quantidade_Acoes_Ordinarias_Circulacao", "Ações ON\nem circulação", 16, "#,##0"),
    ("Quantidade_Acoes_Preferenciais_Circulacao", "Ações PN\nem circulação", 16, "#,##0"),
    ("Quantidade_Total_Acoes_Circulacao", "Ações totais\nem circulação", 16, "#,##0"),
    ("Percentual_Total_Acoes_Circulacao", "% em\ncirculação", 10, "0.0%"),
    (None, "Ações por\nacionista", 13, "#,##0"),  # coluna de fórmula
]


def cabecalho(ws: Worksheet, titulo: str, linha: int = 1) -> None:
    for c, (_, rotulo, largura, _) in enumerate(COLS, start=1):
        col = get_column_letter(c)
        ws.column_dimensions[col].width = largura
        cel = ws.cell(row=linha, column=c, value=rotulo)
        cel.font = Font(name=FONTE_NOME, bold=True, size=10, color="FFFFFF")
        cel.fill = PatternFill("solid", fgColor=AZUL)
        cel.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cel.border = BORDA
    ws.row_dimensions[linha].height = 30
    ws.freeze_panes = ws.cell(row=linha + 1, column=1)


def escreve_tabela(ws: Worksheet, df: pd.DataFrame, linha0: int = 2) -> int:
    idx_pct = next(i for i, c in enumerate(COLS, start=1) if c[0] == "Percentual_Total_Acoes_Circulacao")
    idx_tot_acoes = next(i for i, c in enumerate(COLS, start=1) if c[0] == "Quantidade_Total_Acoes_Circulacao")
    idx_tot_acion = next(i for i, c in enumerate(COLS, start=1) if c[0] == "Qtd_Acionistas_Total")
    idx_formula = len(COLS)  # última coluna: Ações por acionista

    r = linha0
    for _, row in df.iterrows():
        for c, (campo, _, _, fmt) in enumerate(COLS, start=1):
            cel = ws.cell(row=r, column=c)
            if campo is None:
                col_acoes = get_column_letter(idx_tot_acoes)
                col_acion = get_column_letter(idx_tot_acion)
                cel.value = f"=IFERROR({col_acoes}{r}/{col_acion}{r},\"\")"
            else:
                v = row[campo]
                if campo == "Percentual_Total_Acoes_Circulacao":
                    v = float(v) / 100.0  # a fonte vem em %, o Excel guarda fração
                cel.value = v
            cel.font = Font(name=FONTE_NOME, size=10)
            cel.number_format = fmt
            cel.alignment = Alignment(horizontal="left" if fmt == "@" else "right")
            if (r - linha0) % 2 == 1:
                cel.fill = PatternFill("solid", fgColor=CINZA_CLARO)
        r += 1
    ws.auto_filter.ref = f"A{linha0 - 1}:{get_column_letter(len(COLS))}{r - 1}"
    return r


def nota_fonte(ws: Worksheet, linha: int) -> None:
    textos = [
        ("Fonte: dados.cvm.gov.br — Formulário de Referência (FRE), arquivo "
         "fre_cia_aberta_distribuicao_capital — item 6.3, declarado por cada "
         "companhia na data da última assembleia. Coletado em 01/10/2026 por "
         "CVM/21_coletar_distribuicao_capital.py."),
        ("Limitação da própria norma, não desta coleta: a CVM separa as AÇÕES por "
         "classe (ON × PN), mas não separa a CONTAGEM DE ACIONISTAS por classe — "
         "o total de acionistas é da empresa inteira, não só de quem tem PETR4."),
        ("Periodicidade: por assembleia (normalmente 1x por ano), não por pregão."),
    ]
    for i, t in enumerate(textos):
        cel = ws.cell(row=linha + i, column=1, value=t)
        cel.font = Font(name=FONTE_NOME, size=9, italic=True, color="595959")
        ws.merge_cells(start_row=linha + i, start_column=1, end_row=linha + i,
                       end_column=len(COLS))


def main() -> None:
    d = pd.read_csv(FONTE_CSV, dtype={"Data_Referencia": str})
    d = d.sort_values(["Ticker", "Data_Referencia"]).reset_index(drop=True)

    wb = Workbook()

    # ── aba 1: Resumo — leitura mais recente de cada papel ──────────────────
    ws1 = wb.active
    ws1.title = "Resumo (62 papéis)"
    recente = (d.sort_values("Data_Referencia")
                .drop_duplicates("Ticker", keep="last")
                .sort_values("Qtd_Acionistas_Total", ascending=False)
                .reset_index(drop=True))
    cabecalho(ws1, "Resumo")
    fim = escreve_tabela(ws1, recente)
    nota_fonte(ws1, fim + 1)

    # ── aba 2: PETR4 — série histórica completa ──────────────────────────────
    ws2 = wb.create_sheet("PETR4 - Série Histórica")
    petr4 = d[d["Ticker"] == "PETR4"].sort_values("Data_Referencia").reset_index(drop=True)
    cabecalho(ws2, "PETR4")
    fim2 = escreve_tabela(ws2, petr4)
    nota_fonte(ws2, fim2 + 1)

    # ── aba 3: todos os papéis, todas as leituras (dado bruto p/ filtrar) ────
    ws3 = wb.create_sheet("Todos os papéis")
    cabecalho(ws3, "Todos")
    fim3 = escreve_tabela(ws3, d)
    nota_fonte(ws3, fim3 + 1)

    wb.save(SAIDA)
    print(f"gravado: {SAIDA}  ({len(recente)} papéis no resumo, "
          f"{len(petr4)} leituras da PETR4, {len(d)} linhas no total)")


if __name__ == "__main__":
    main()
