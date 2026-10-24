# -*- coding: utf-8 -*-
# ==============================================================================
#   PLANILHA — FinBERT + GARCH/SVM/XGBoost  ×  FinBERT + Prophet
#   Pedido dos Profs. Emerson e Julio, mentoria de 23/10/2026.
#   Gera 02_Comparativo_FinBERT.xlsx, nesta mesma pasta.
# ==============================================================================
import json
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
SAIDA = AQUI / "02_Comparativo_FinBERT.xlsx"

FONTE, AZUL, AZUL_IN = "Arial", "1F3864", "0000FF"
CINZA, AMARELO, VERDE, VERMELHO = "F2F2F2", "FFF2CC", "E2EFDA", "FCE4E4"
BORDA = Border(bottom=Side(style="thin", color="BFBFBF"))

E = json.loads((RAIZ / "CVM" / "dados" / "prophet_vs_garch_svm_xgboost.json").read_text(encoding="utf-8"))["papeis"]
TOP = json.loads((RAIZ / "CVM" / "dados" / "comparativo_top10_acoes.json").read_text(encoding="utf-8"))["papeis"]
try:
    SIM = json.loads((RAIZ / "CVM" / "dados" / "simulacao_reais_por_investidor.json").read_text(encoding="utf-8"))
    # só aceita a simulação NOVA (com percentuais e o braço FinBERT+Prophet)
    _a = SIM["papeis"][next(iter(SIM["papeis"]))]
    if "retorno_pct" not in _a["buy_and_hold"] or "Prophet (preço+CVM)" not in _a["modelos"]:
        SIM = None
except Exception:
    SIM = None
TICKERS = list(E.keys())


def cab(ws, titulos, largs, linha=1):
    for c, (rot, lg) in enumerate(zip(titulos, largs), start=1):
        ws.column_dimensions[get_column_letter(c)].width = lg
        cel = ws.cell(row=linha, column=c, value=rot)
        cel.font = Font(name=FONTE, bold=True, size=10, color="FFFFFF")
        cel.fill = PatternFill("solid", fgColor=AZUL)
        cel.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cel.border = BORDA
    ws.row_dimensions[linha].height = 34
    ws.freeze_panes = ws.cell(row=linha + 1, column=1)


def txt(ws, r, c, v, bold=False, size=10, cor="000000", wrap=False, align=None):
    cel = ws.cell(row=r, column=c, value=v)
    cel.font = Font(name=FONTE, bold=bold, size=size, color=cor)
    cel.alignment = Alignment(wrap_text=wrap, horizontal=align, vertical="center")
    return cel


def val(ws, r, c, v, fmt=None, cor=AZUL_IN, fundo=None):
    cel = ws.cell(row=r, column=c, value=v)
    cel.font = Font(name=FONTE, size=10, color=cor)
    if fmt:
        cel.number_format = fmt
    if fundo:
        cel.fill = PatternFill("solid", fgColor=fundo)
    cel.alignment = Alignment(horizontal="right")
    return cel


def zebra(ws, r, r0, n):
    if (r - r0) % 2 == 1:
        for c in range(1, n + 1):
            if ws.cell(row=r, column=c).fill.fgColor.rgb in (None, "00000000"):
                ws.cell(row=r, column=c).fill = PatternFill("solid", fgColor=CINZA)


wb = Workbook()

# ═══ ABA 1 — O PLACAR ═══════════════════════════════════════════════════════
ws = wb.active
ws.title = "O placar"
txt(ws, 1, 1, "FinBERT + GARCH/SVM/XGBoost  ×  FinBERT + Prophet", bold=True, size=15, cor=AZUL)
txt(ws, 2, 1, "As três perguntas que os senhores fizeram, e a resposta de cada uma. "
              "Os detalhes estão nas abas seguintes.", size=10, cor="595959", wrap=True)
ws.merge_cells("A2:E2"); ws.row_dimensions[2].height = 28

cab(ws, ["#", "A pergunta", "A resposta curta", "O número", "Onde conferir"],
    [5, 40, 34, 26, 20], linha=4)
LINHAS = [
    ("1", "O sentimento do FinBERT ajuda a acertar se o preço SOBE ou DESCE?",
     "Não — nem com GARCH/SVM/XGBoost, nem com Prophet.",
     "0 de 10 papéis superam o palpite fixo com significância, em qualquer um dos 6 modelos",
     "aba 'Direção'"),
    ("2", "E ajuda a prever o TAMANHO do sacolejo (volatilidade)?",
     "O GARCH prevê muito bem. O Prophet é ruim. Mas o sentimento quase não muda nada nos dois.",
     "GARCH vence o Prophet em 10 de 10; o sentimento acrescenta −0,07 ponto (GARCH)",
     "aba 'Volatilidade'"),
    ("3", "Quanto isso dá em dinheiro, para o investidor médio?",
     "Menos do que comprar e segurar, que não custa nada e não dá trabalho.",
     "ver aba 'Em reais'" if SIM else "cálculo em andamento",
     "aba 'Em reais'"),
]
r = 5
for num, perg, resp, nums, onde in LINHAS:
    txt(ws, r, 1, num, bold=True, align="center")
    txt(ws, r, 2, perg, wrap=True)
    txt(ws, r, 3, resp, bold=True, wrap=True)
    txt(ws, r, 4, nums, size=9, wrap=True, cor="595959")
    txt(ws, r, 5, onde, size=9, cor="595959")
    for c in range(1, 6):
        ws.cell(row=r, column=c).border = BORDA
        ws.cell(row=r, column=c).fill = PatternFill("solid", fgColor=AMARELO)
    ws.row_dimensions[r].height = 56
    r += 1

r += 1
txt(ws, r, 1, "A conclusão em uma frase", bold=True, size=12, cor=AZUL); r += 1
ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=5)
txt(ws, r, 1,
    "Trocar o GARCH+SVM/XGBoost pelo Prophet piora tudo. E, nos dois, acrescentar o sentimento do "
    "FinBERT muda tão pouco que o efeito é indistinguível de sorte — ele melhora o resultado em "
    "cerca de 5 dos 10 papéis, que é exatamente o que se esperaria de cara-ou-coroa.",
    wrap=True)
ws.row_dimensions[r].height = 48

# ═══ ABA 2 — DIREÇÃO ════════════════════════════════════════════════════════
ws1 = wb.create_sheet("Direção")
txt(ws1, 1, 1, "Acerto na direção do pregão seguinte — 579 pregões de teste por papel",
    bold=True, size=12, cor=AZUL)
txt(ws1, 2, 1, "O adversário é o PALPITE FIXO: quem não lê nada e sempre chuta o lado mais "
               "frequente. Verde = superou o palpite fixo. Nenhum caso teve significância estatística.",
    size=9, cor="595959", wrap=True)
ws1.merge_cells("A2:H2"); ws1.row_dimensions[2].height = 28
cab(ws1, ["Papel", "Palpite fixo\n(o adversário)", "GARCH+SVM\nsó preço", "GARCH+SVM\n+ FinBERT",
          "GARCH+XGB\nsó preço", "GARCH+XGB\n+ FinBERT", "Prophet\nsó preço", "Prophet\n+ FinBERT"],
    [9, 14, 13, 13, 13, 13, 12, 12], linha=4)
ARMS = ["SVM (preço)", "SVM (preço+CVM)", "XGBoost (preço)", "XGBoost (preço+CVM)",
        "Prophet (preço)", "Prophet (preço+CVM)"]
r, r0 = 5, 5
for tk in TICKERS:
    p = E[tk]["direcao"]; maj = p["majoritaria"]
    txt(ws1, r, 1, tk, bold=True)
    val(ws1, r, 2, maj, "0.0%", cor="000000")
    for i, arm in enumerate(ARMS):
        a = p["arms"][arm]
        val(ws1, r, 3 + i, a["acuracia"], "0.0%",
            fundo=VERDE if a["acuracia"] > maj else None)
    for c in range(1, 9):
        ws1.cell(row=r, column=c).border = BORDA
    zebra(ws1, r, r0, 8)
    r += 1
r += 1
txt(ws1, r, 1, "Supera o palpite fixo em:", bold=True)
for i, arm in enumerate(ARMS):
    n = sum(E[tk]["direcao"]["arms"][arm]["acuracia"] > E[tk]["direcao"]["majoritaria"] for tk in TICKERS)
    txt(ws1, r, 3 + i, f"{n} de 10", bold=True, align="center")
r += 1
txt(ws1, r, 1, "Com significância (p<0,05):", bold=True)
for i, arm in enumerate(ARMS):
    n = sum(E[tk]["direcao"]["arms"][arm]["p_vs_majoritaria"] < 0.05 and
            E[tk]["direcao"]["arms"][arm]["acuracia"] > E[tk]["direcao"]["majoritaria"] for tk in TICKERS)
    txt(ws1, r, 3 + i, f"{n} de 10", bold=True, align="center", cor="C00000")
r += 2
ws1.merge_cells(start_row=r, start_column=1, end_row=r, end_column=8)
txt(ws1, r, 1, "Como ler: a linha de baixo é a que decide. ZERO modelos, em ZERO papéis, superaram "
               "o palpite fixo de forma estatisticamente confiável. Os poucos casos em verde estão "
               "dentro da margem de erro — com 579 pregões, qualquer diferença menor que ~4 pontos "
               "percentuais é indistinguível de sorte.", wrap=True, size=9, cor="595959")
ws1.row_dimensions[r].height = 48

# ═══ ABA 3 — VOLATILIDADE ═══════════════════════════════════════════════════
ws2 = wb.create_sheet("Volatilidade")
txt(ws2, 1, 1, "Previsão do tamanho do sacolejo (volatilidade)", bold=True, size=12, cor=AZUL)
txt(ws2, 2, 1, "A régua é a previsão ancorada: segurar o último valor conhecido, com exatamente a "
               "mesma informação que o Prophet recebe. Positivo = melhor que a régua. "
               "Negativo = pior que não fazer nada.", size=9, cor="595959", wrap=True)
ws2.merge_cells("A2:F2"); ws2.row_dimensions[2].height = 28
cab(ws2, ["Papel", "GARCH (HAR)\nsó preço", "GARCH (HAR)\n+ FinBERT", "Prophet\nsó preço",
          "Prophet\n+ FinBERT", "Quem vence"], [9, 15, 15, 14, 14, 16], linha=4)
r, r0 = 5, 5
for tk in TICKERS:
    a = E[tk]["volatilidade"]["arms"]
    h0 = a["HAR (GARCH, referência)"]["r2os_vs_ancorada"]
    hc = a["HAR + CVM"]["r2os_vs_ancorada"]
    p0 = a["Prophet (volatilidade)"]["r2os_vs_ancorada"]
    pc = a["Prophet (volatilidade+CVM)"]["r2os_vs_ancorada"]
    txt(ws2, r, 1, tk, bold=True)
    for i, v in enumerate([h0, hc, p0, pc]):
        val(ws2, r, 2 + i, v / 100, "+0.0%;-0.0%", fundo=VERDE if v > 0 else VERMELHO)
    txt(ws2, r, 6, "GARCH" if max(h0, hc) > max(p0, pc) else "Prophet", bold=True, align="center")
    for c in range(1, 7):
        ws2.cell(row=r, column=c).border = BORDA
    zebra(ws2, r, r0, 6)
    r += 1
r += 1
ws2.merge_cells(start_row=r, start_column=1, end_row=r, end_column=6)
txt(ws2, r, 1, "Como ler: o GARCH acerta muito bem (verde, +83% a +93%) e o Prophet erra mais do que "
               "simplesmente não fazer nada (vermelho). A diferença entre as duas colunas de cada "
               "família — com e sem FinBERT — é de menos de um ponto: o sentimento praticamente não "
               "muda a previsão de volatilidade.", wrap=True, size=9, cor="595959")
ws2.row_dimensions[r].height = 48

# ═══ ABA 4 — O QUE O FINBERT ACRESCENTA ═════════════════════════════════════
ws3 = wb.create_sheet("O que o FinBERT acrescenta")
txt(ws3, 1, 1, "O sentimento acrescenta alguma coisa? (com FinBERT menos sem FinBERT)",
    bold=True, size=12, cor=AZUL)
txt(ws3, 2, 1, "Esta é a pergunta central da dissertação. Valores em pontos percentuais.",
    size=9, cor="595959")
cab(ws3, ["Papel", "GARCH+SVM\n(direção)", "GARCH+XGB\n(direção)", "Prophet\n(direção)",
          "GARCH/HAR\n(volatilidade)", "Prophet\n(volatilidade)"], [9, 14, 14, 13, 16, 15], linha=4)
PARES_D = [("SVM (preço)", "SVM (preço+CVM)"), ("XGBoost (preço)", "XGBoost (preço+CVM)"),
           ("Prophet (preço)", "Prophet (preço+CVM)")]
PARES_V = [("HAR (GARCH, referência)", "HAR + CVM"),
           ("Prophet (volatilidade)", "Prophet (volatilidade+CVM)")]
r, r0 = 5, 5
for tk in TICKERS:
    txt(ws3, r, 1, tk, bold=True)
    for i, (sem, com) in enumerate(PARES_D):
        dif = (E[tk]["direcao"]["arms"][com]["acuracia"] - E[tk]["direcao"]["arms"][sem]["acuracia"]) * 100
        val(ws3, r, 2 + i, dif, "+0.00;-0.00", fundo=VERDE if dif > 0 else VERMELHO)
    for i, (sem, com) in enumerate(PARES_V):
        dif = (E[tk]["volatilidade"]["arms"][com]["r2os_vs_ancorada"]
               - E[tk]["volatilidade"]["arms"][sem]["r2os_vs_ancorada"])
        val(ws3, r, 5 + i, dif, "+0.00;-0.00", fundo=VERDE if dif > 0 else VERMELHO)
    for c in range(1, 7):
        ws3.cell(row=r, column=c).border = BORDA
    zebra(ws3, r, r0, 6)
    r += 1
r += 1
txt(ws3, r, 1, "Melhorou em:", bold=True)
for i, (sem, com) in enumerate(PARES_D):
    n = sum(E[tk]["direcao"]["arms"][com]["acuracia"] > E[tk]["direcao"]["arms"][sem]["acuracia"] for tk in TICKERS)
    txt(ws3, r, 2 + i, f"{n} de 10", bold=True, align="center")
for i, (sem, com) in enumerate(PARES_V):
    n = sum(E[tk]["volatilidade"]["arms"][com]["r2os_vs_ancorada"]
            > E[tk]["volatilidade"]["arms"][sem]["r2os_vs_ancorada"] for tk in TICKERS)
    txt(ws3, r, 5 + i, f"{n} de 10", bold=True, align="center")
r += 2
ws3.merge_cells(start_row=r, start_column=1, end_row=r, end_column=6)
txt(ws3, r, 1, "Como ler: 'melhorou em 5 de 10' é exatamente o que cara-ou-coroa produziria. "
               "As médias ficam entre −0,14 e +0,07 ponto percentual na direção — ou seja, perto de "
               "zero. O sentimento dos comunicados da CVM, nesta forma de uso, não acrescenta poder "
               "de previsão a nenhuma das duas famílias de modelo.", wrap=True, size=9, cor="595959")
ws3.row_dimensions[r].height = 48

# ═══ ABA 5 — EM REAIS ═══════════════════════════════════════════════════════
ws4 = wb.create_sheet("Em reais")
txt(ws4, 1, 1, "Quanto o investidor médio ganharia ou perderia", bold=True, size=12, cor=AZUL)
if SIM:
    txt(ws4, 2, 1, f"Regra: {SIM['regra']}. Período: 579 pregões (23/05/2024 a 15/09/2026). "
                   f"Sobre o valor médio investido por investidor de cada papel.",
        size=9, cor="595959", wrap=True)
    ws4.merge_cells("A2:H2"); ws4.row_dimensions[2].height = 28
    cab(ws4, ["Papel", "Valor investido\n(médio por investidor)", "Comprar e segurar\n(%)",
              "Comprar e segurar\n(R$)", "FinBERT+GARCH\n(%)", "FinBERT+GARCH\n(R$)",
              "FinBERT+Prophet\n(%)", "FinBERT+Prophet\n(R$)"],
        [9, 18, 14, 15, 14, 15, 14, 15], linha=4)
    r, r0 = 5, 5
    for tk in TICKERS:
        s = SIM["papeis"][tk]
        cla = max(["SVM (preço+CVM)", "XGBoost (preço+CVM)"],
                  key=lambda k: s["modelos"][k]["resultado_reais"])
        pro = s["modelos"]["Prophet (preço+CVM)"]
        txt(ws4, r, 1, tk, bold=True)
        val(ws4, r, 2, s["valor_investido_medio"], '"R$" #,##0', cor="000000")
        val(ws4, r, 3, s["buy_and_hold"]["retorno_pct"] / 100, "+0.0%;-0.0%", fundo=AMARELO)
        val(ws4, r, 4, s["buy_and_hold"]["resultado_reais"], '"R$" #,##0;[Red]-"R$" #,##0', fundo=AMARELO)
        val(ws4, r, 5, s["modelos"][cla]["retorno_pct"] / 100, "+0.0%;-0.0%")
        val(ws4, r, 6, s["modelos"][cla]["resultado_reais"], '"R$" #,##0;[Red]-"R$" #,##0')
        val(ws4, r, 7, pro["retorno_pct"] / 100, "+0.0%;-0.0%")
        val(ws4, r, 8, pro["resultado_reais"], '"R$" #,##0;[Red]-"R$" #,##0')
        for c in range(1, 9):
            ws4.cell(row=r, column=c).border = BORDA
        zebra(ws4, r, r0, 8)
        r += 1
    n_bh = sum(SIM["papeis"][tk]["buy_and_hold"]["resultado_reais"]
               > max(SIM["papeis"][tk]["modelos"][k]["resultado_reais"]
                     for k in ["SVM (preço+CVM)", "XGBoost (preço+CVM)", "Prophet (preço+CVM)"])
               for tk in TICKERS)
    r += 1
    ws4.merge_cells(start_row=r, start_column=1, end_row=r, end_column=8)
    txt(ws4, r, 1,
        f"Como ler: a coluna amarela é o que o investidor faria SEM modelo algum — comprar e "
        f"segurar. Ela venceu os dois modelos em {n_bh} dos 10 papéis. O motivo é simples: os "
        f"modelos saem do mercado nos dias em que preveem queda, e acabam perdendo as altas. "
        f"RESSALVA: não inclui corretagem, imposto de renda nem spread; e, com o acerto perto de "
        f"cara-ou-coroa, o resultado em reais é em boa parte sorte.", wrap=True, size=9, cor="595959")
    ws4.row_dimensions[r].height = 56
else:
    txt(ws4, 3, 1, "Cálculo ainda em execução quando esta planilha foi gerada.", cor="C00000")

wb.save(SAIDA)
print(f"gravado: {SAIDA}  ({len(wb.sheetnames)} abas)" + ("" if SIM else "  [SEM aba em reais]"))
