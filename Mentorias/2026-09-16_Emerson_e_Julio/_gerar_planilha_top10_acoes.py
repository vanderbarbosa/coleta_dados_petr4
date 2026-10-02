# -*- coding: utf-8 -*-
# ==============================================================================
#   PLANILHA — comparativo individual das 10 principais ações do Ibovespa,
#   pedido na mentoria de 30/09/2026. Lê CVM/dados/comparativo_top10_acoes.json
#   (gerado por CVM/22_comparativo_top10_acoes.py) e CVM/dados/
#   distribuicao_capital_papeis.csv. Grava 18_Comparativo_Top10_Acoes.xlsx.
#
#   11 abas: Visão Geral + uma por ação, cada uma com preço atual, investidores
#   por ação, ações por investidor, e a comparação de direção (preço / preço+
#   CVM todos / preço+CVM só Fato Relevante) com McNemar.
#
#   Os 60 testes (10 papéis x 3 braços x 2 modelos) são tratados como UM
#   conjunto para a correção de Bonferroni — não 10 conjuntos separados —
#   porque é assim que a múltipla comparação real aconteceu. O limiar é
#   FÓRMULA (0,05 ÷ 60), em célula própria, referenciada por todas as abas.
# ==============================================================================
import json
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
SAIDA = AQUI / "18_Comparativo_Top10_Acoes.xlsx"

FONTE_NOME = "Arial"
AZUL_CAB = "1F3864"
AZUL_INPUT = "0000FF"
CINZA_CLARO = "F2F2F2"
AMARELO = "FFF2CC"
BORDA = Border(bottom=Side(style="thin", color="BFBFBF"))
N_TESTES_TOTAL = 60  # 10 papéis x 3 braços x 2 modelos — base da correção de Bonferroni

d = json.loads((RAIZ / "CVM" / "dados" / "comparativo_top10_acoes.json").read_text(encoding="utf-8"))
dist_cap = pd.read_csv(RAIZ / "CVM" / "dados" / "distribuicao_capital_papeis.csv")
NOME_COMPANHIA = (dist_cap.sort_values("Data_Referencia")
                  .drop_duplicates("Ticker", keep="last")
                  .set_index("Ticker")["Nome_Companhia"].to_dict())

BRACOS_ROTULO = {
    "apenas preço": "Apenas preço histórico",
    "preço + CVM (todos)": "Preço + CVM (TODOS os comunicados)",
    "preço + CVM (só FR)": "Preço + CVM (SÓ Fato Relevante)",
}
MCNEMAR_ROTULO = {
    "FR acrescenta sobre só preço?": "SÓ Fato Relevante acrescenta sobre só preço?",
    "TODOS acrescentam sobre só preço?": "TODOS os comunicados acrescentam sobre só preço?",
    "SÓ FR x TODOS os comunicados": "SÓ Fato Relevante × TODOS os comunicados",
}


def cab(ws, titulos, larguras, linha=1):
    for c, (rot, larg) in enumerate(zip(titulos, larguras), start=1):
        col = get_column_letter(c)
        ws.column_dimensions[col].width = larg
        cel = ws.cell(row=linha, column=c, value=rot)
        cel.font = Font(name=FONTE_NOME, bold=True, size=10, color="FFFFFF")
        cel.fill = PatternFill("solid", fgColor=AZUL_CAB)
        cel.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cel.border = BORDA
    ws.row_dimensions[linha].height = 30


def zebra(ws, r, linha0, ncols):
    if (r - linha0) % 2 == 1:
        for c in range(1, ncols + 1):
            ws.cell(row=r, column=c).fill = PatternFill("solid", fgColor=CINZA_CLARO)


def texto(ws, r, c, v, bold=False, size=10, cor="000000", wrap=False, align=None):
    cel = ws.cell(row=r, column=c, value=v)
    cel.font = Font(name=FONTE_NOME, bold=bold, size=size, color=cor)
    cel.alignment = Alignment(wrap_text=wrap, horizontal=align, vertical="center")
    return cel


def entrada(ws, r, c, v, fmt=None):
    cel = ws.cell(row=r, column=c, value=v)
    cel.font = Font(name=FONTE_NOME, size=10, color=AZUL_INPUT)
    if fmt:
        cel.number_format = fmt
    cel.alignment = Alignment(horizontal="right")
    return cel


wb = Workbook()

# ═══ ABA 1 — VISÃO GERAL ════════════════════════════════════════════════════
ws0 = wb.active
ws0.title = "Visão Geral"
texto(ws0, 1, 1, "Comparativo — as 10 principais ações do Ibovespa", bold=True, size=14, cor=AZUL_CAB)
texto(ws0, 2, 1,
      ("Os 10 papéis de maior peso na carteira teórica oficial do Ibovespa (B3, consultada em "
       "02/10/2026) QUE JÁ fazem parte da pesquisa — isto é, que já têm comunicados da CVM "
       "coletados/classificados e preço coletado. Ficaram de fora, por falta de dado coletado: "
       "WEGE3, AXIA3 (ex-Eletrobras), EMBJ3 (Embraer), CPLE3, ENEV3."), size=9, cor="595959", wrap=True)
ws0.merge_cells("A2:L2")
ws0.row_dimensions[2].height = 30

ws0.cell(row=4, column=1, value="Limiar de Bonferroni (60 testes = 10 papéis × 3 braços × 2 modelos):")
ws0.cell(row=4, column=1).font = Font(name=FONTE_NOME, bold=True, size=10)
ws0.merge_cells("A4:F4")
ws0["G4"] = f"=0.05/{N_TESTES_TOTAL}"
ws0["G4"].number_format = "0.000000"
ws0["G4"].font = Font(name=FONTE_NOME, size=10, color=AZUL_INPUT, bold=True)

titulos0 = ["Ticker", "Empresa", "Peso\nIbovespa", "Preço atual\n(15/09/2026)",
            "Investidores\n(total)", "Ações por\ninvestidor", "Eventos CVM\n(FR / todos)",
            "Melhor braço\n(maior acerto)", "Melhor\nacerto", "Classe\nmajoritária",
            "p mínimo\n(6 testes)", "Sobrevive\nBonferroni?"]
larg0 = [9, 30, 9, 13, 12, 11, 12, 32, 10, 11, 10, 10]
cab(ws0, titulos0, larg0, linha=6)

r, linha0 = 7, 7
for tk, info in d["papeis"].items():
    bracos = info["direcao"]
    melhor_nome, melhor_mn, melhor_acc, melhor_p = None, None, -1, None
    p_min = 1.0
    for braco, modelos in bracos.items():
        for mn, m in modelos.items():
            p_min = min(p_min, m["p_binomial_vs_majoritaria"])
            if m["acuracia"] > melhor_acc:
                melhor_nome, melhor_mn, melhor_acc = braco, mn, m["acuracia"]
                melhor_p = m["p_binomial_vs_majoritaria"]

    texto(ws0, r, 1, tk, bold=True)
    texto(ws0, r, 2, NOME_COMPANHIA.get(tk, info["empresa"]))
    entrada(ws0, r, 3, info["peso_ibovespa_pct"] / 100.0, "0.00%")
    entrada(ws0, r, 4, info["preco_atual"], '"R$" #,##0.00')
    entrada(ws0, r, 5, info["investidores"]["total"], "#,##0")
    entrada(ws0, r, 6, info["investidores"]["acoes_por_investidor"], "#,##0")
    texto(ws0, r, 7, f"{info['n_eventos_cvm']['fato_relevante']} / {info['n_eventos_cvm']['todos']}",
          align="center")
    texto(ws0, r, 8, f"{BRACOS_ROTULO[melhor_nome]} ({melhor_mn})")
    entrada(ws0, r, 9, melhor_acc, "0.00%")
    entrada(ws0, r, 10, info["majoritaria_teste"], "0.00%")
    entrada(ws0, r, 11, p_min, "0.0000")
    ws0.cell(row=r, column=12, value=f"=IF(K{r}<$G$4,\"Sim\",\"Não\")")
    ws0.cell(row=r, column=12).font = Font(name=FONTE_NOME, size=10, bold=True)
    for c in range(1, 13):
        ws0.cell(row=r, column=c).border = BORDA
        if ws0.cell(row=r, column=c).alignment.horizontal is None:
            ws0.cell(row=r, column=c).alignment = Alignment(horizontal="left", vertical="center")
    zebra(ws0, r, linha0, 12)
    ws0.row_dimensions[r].height = 20
    r += 1
ws0.freeze_panes = "A7"
ws0.auto_filter.ref = f"A6:{get_column_letter(12)}{r-1}"

r += 1
ws0.merge_cells(start_row=r, start_column=1, end_row=r, end_column=12)
texto(ws0, r, 1,
      ("Conclusão: dos 60 testes, 9 deram p<0,05 sem correção — número compatível com o esperado "
       "só por acaso (~3 em 60, a 5%). NENHUM sobrevive à correção de Bonferroni. Nenhum papel, "
       "nenhuma combinação de atributos, bate o palpite fixo de forma estatisticamente confiável "
       "neste protocolo."), wrap=True, cor="595959", size=9)
ws0.row_dimensions[r].height = 46

# ═══ UMA ABA POR AÇÃO ═══════════════════════════════════════════════════════
for tk, info in d["papeis"].items():
    ws = wb.create_sheet(tk)
    nome_cheio = NOME_COMPANHIA.get(tk, info["empresa"])
    texto(ws, 1, 1, f"{tk} — {nome_cheio}", bold=True, size=14, cor=AZUL_CAB)
    ws.merge_cells("A1:F1")

    # ── bloco de identificação ───────────────────────────────────────────────
    campos = [
        ("Peso na carteira do Ibovespa", info["peso_ibovespa_pct"] / 100.0, "0.00%"),
        (f"Preço de fechamento em {info['data_preco']}", info["preco_atual"], '"R$" #,##0.00'),
        (f"Investidores — total ({info['investidores']['data_referencia']})",
         info["investidores"]["total"], "#,##0"),
        ("  dos quais pessoa física", info["investidores"]["pessoa_fisica"], "#,##0"),
        ("  dos quais pessoa jurídica", info["investidores"]["pessoa_juridica"], "#,##0"),
        ("  dos quais institucionais", info["investidores"]["institucionais"], "#,##0"),
        ("Ações em circulação (free float)", info["investidores"]["acoes_em_circulacao"], "#,##0"),
        ("Ações por investidor (em média)", info["investidores"]["acoes_por_investidor"], "#,##0"),
        ("Eventos CVM após 17h — Fato Relevante", info["n_eventos_cvm"]["fato_relevante"], "#,##0"),
        ("Eventos CVM após 17h — todos", info["n_eventos_cvm"]["todos"], "#,##0"),
        ("Pregões de teste (25% mais recentes)", info["n"]["teste"], "#,##0"),
        ("Classe majoritária no teste", info["majoritaria_teste"], "0.00%"),
    ]
    r = 3
    for rot, val, fmt in campos:
        texto(ws, r, 1, rot)
        entrada(ws, r, 2, val, fmt)
        r += 1
    ws.column_dimensions["A"].width = 38
    ws.column_dimensions["B"].width = 14

    texto(ws, r + 1, 1, "Limiar de Bonferroni (60 testes, todos os papéis):", bold=True)
    ws.merge_cells(start_row=r + 1, start_column=1, end_row=r + 1, end_column=3)
    ws.cell(row=r + 1, column=4, value=f"=0.05/{N_TESTES_TOTAL}")
    ws.cell(row=r + 1, column=4).number_format = "0.000000"
    ws.cell(row=r + 1, column=4).font = Font(name=FONTE_NOME, size=10, color=AZUL_INPUT, bold=True)
    linha_bonf = f"$D${r+1}"
    r += 3

    # ── tabela de direção ────────────────────────────────────────────────────
    titulos_d = ["Braço", "Modelo", "N teste", "Classe\nmajoritária", "Acurácia",
                 "Ganho\n(pontos)", "Precisão", "F1", "AUC", "p vs\nmajoritária",
                 "Passa\n(p<0,05)?", "Sobrevive\nBonferroni?"]
    larg_d = [30, 10, 9, 12, 10, 9, 10, 9, 8, 10, 10, 11]
    cab(ws, titulos_d, larg_d, linha=r)
    linha0 = r + 1
    r += 1
    for braco, modelos in info["direcao"].items():
        for mn, m in modelos.items():
            texto(ws, r, 1, BRACOS_ROTULO[braco])
            texto(ws, r, 2, mn)
            entrada(ws, r, 3, m["n_teste"], "0")
            entrada(ws, r, 4, info["majoritaria_teste"], "0.00%")
            entrada(ws, r, 5, m["acuracia"], "0.00%")
            ws.cell(row=r, column=6, value=f"=(E{r}-D{r})*100")
            ws.cell(row=r, column=6).number_format = "+0.00;-0.00"
            ws.cell(row=r, column=6).font = Font(name=FONTE_NOME, size=10)
            entrada(ws, r, 7, m["precisao"], "0.00%")
            entrada(ws, r, 8, m["f1"], "0.00%")
            entrada(ws, r, 9, m["auc"], "0.000")
            entrada(ws, r, 10, m["p_binomial_vs_majoritaria"], "0.0000")
            ws.cell(row=r, column=11, value=f"=IF(J{r}<0.05,\"Sim\",\"Não\")")
            ws.cell(row=r, column=11).font = Font(name=FONTE_NOME, size=10)
            ws.cell(row=r, column=12, value=f"=IF(J{r}<{linha_bonf},\"Sim\",\"Não\")")
            ws.cell(row=r, column=12).font = Font(name=FONTE_NOME, size=10, bold=True)
            for c in range(3, 13):
                ws.cell(row=r, column=c).alignment = Alignment(horizontal="right")
            for c in range(1, 13):
                ws.cell(row=r, column=c).border = BORDA
            zebra(ws, r, linha0, 12)
            r += 1
    r += 1

    # ── tabela de McNemar ────────────────────────────────────────────────────
    titulos_m = ["Comparação (McNemar)", "Modelo", "Ganhou", "Perdeu", "p-valor",
                 "Significativo\n(p<0,05)?"]
    larg_m = [42, 10, 9, 9, 10, 12]
    cab(ws, titulos_m, larg_m, linha=r)
    linha0 = r + 1
    r += 1
    for chave, m in info["mcnemar"].items():
        modelo = chave.split(" — ")[0]
        rot_raw = chave.split(" — ", 1)[1]
        rotulo = MCNEMAR_ROTULO.get(rot_raw, rot_raw)
        texto(ws, r, 1, rotulo)
        texto(ws, r, 2, modelo)
        entrada(ws, r, 3, m["acertos_so_do_novo"], "0")
        entrada(ws, r, 4, m["acertos_so_do_antigo"], "0")
        entrada(ws, r, 5, m["p"], "0.0000")
        ws.cell(row=r, column=6, value=f"=IF(E{r}<0.05,\"Sim\",\"Não\")")
        ws.cell(row=r, column=6).font = Font(name=FONTE_NOME, size=10)
        for c in range(3, 7):
            ws.cell(row=r, column=c).alignment = Alignment(horizontal="center")
        for c in range(1, 7):
            ws.cell(row=r, column=c).border = BORDA
        zebra(ws, r, linha0, 6)
        r += 1

    r += 1
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=12)
    texto(ws, r, 1,
          ("Protocolo: Cap. 3 da dissertação (GARCH(1,1) próprio deste papel + SVM-RBF/XGBoost, "
           "divisão cronológica 60/15/25, McNemar). NÃO inclui notícia de jornal — bloqueado nesta "
           "máquina por falta do corpus classificado, mesma razão do PETR4. 'Sobrevive Bonferroni?' "
           "usa o limiar de TODOS os 60 testes do estudo, não só os 6 desta aba."),
          wrap=True, cor="595959", size=9)
    ws.row_dimensions[r].height = 46

wb.save(SAIDA)
print(f"gravado: {SAIDA}  ({len(wb.sheetnames)} abas)")
