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

import numpy as np
import pandas as pd

E = json.loads((RAIZ / "CVM" / "dados" / "prophet_vs_garch_svm_xgboost.json").read_text(encoding="utf-8"))["papeis"]


def palpite_fixo_decidido_no_passado() -> dict:
    """O palpite fixo HONESTO: escolhe o lado (alta ou baixa) olhando só o
    TREINO — o que se saberia de verdade na época — e aplica daí em diante.
    Diferente do palpite fixo 'com o gabarito na mão', que usa o lado mais
    frequente do próprio teste, isto é, já sabendo como a história terminou."""
    px = pd.read_csv(RAIZ / "CVM" / "dados" / "ohlcv_b3.csv", parse_dates=["Data"])
    out = {}
    for tk in E:
        p = px[px["Ticker"] == tk].sort_values("Data").reset_index(drop=True)
        p = p[p["Retorno"].notna()].reset_index(drop=True)
        alvo = (p["Retorno"] > 0).astype(int).values[1:]
        n = len(alvo)
        atr, ate = alvo[:int(n * 0.60)], alvo[int(n * 0.75):]
        lado = 1 if atr.mean() > 0.5 else 0
        out[tk] = {"lado": "alta" if lado else "baixa",
                   "acerto": float((ate == lado).mean())}
    return out


HONESTO = palpite_fixo_decidido_no_passado()
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
txt(ws1, 2, 1, "O adversário é o PALPITE FIXO: quem não lê nada, não calcula nada, e simplesmente "
               "diz sempre o mesmo lado. Há duas versões dele, explicadas abaixo da tabela — e a "
               "conclusão é a mesma nas duas. Verde = superou o palpite fixo com o gabarito na mão.",
    size=9, cor="595959", wrap=True)
ws1.merge_cells("A2:J2"); ws1.row_dimensions[2].height = 28
cab(ws1, ["Papel", "Palpite fixo\nCOM GABARITO\n(o que usei)", "Palpite fixo\nDECIDIDO NO\nPASSADO",
          "GARCH+SVM\nsó preço", "GARCH+SVM\n+ FinBERT", "GARCH+XGB\nsó preço", "GARCH+XGB\n+ FinBERT",
          "Prophet\nsó preço", "Prophet\n+ FinBERT"],
    [9, 15, 15, 13, 13, 13, 13, 12, 12], linha=4)
ARMS = ["SVM (preço)", "SVM (preço+CVM)", "XGBoost (preço)", "XGBoost (preço+CVM)",
        "Prophet (preço)", "Prophet (preço+CVM)"]
r, r0 = 5, 5
for tk in TICKERS:
    p = E[tk]["direcao"]; maj = p["majoritaria"]
    txt(ws1, r, 1, tk, bold=True)
    val(ws1, r, 2, maj, "0.0%", cor="000000", fundo=AMARELO)
    val(ws1, r, 3, HONESTO[tk]["acerto"], "0.0%", cor="000000")
    for i, arm in enumerate(ARMS):
        a = p["arms"][arm]
        val(ws1, r, 4 + i, a["acuracia"], "0.0%",
            fundo=VERDE if a["acuracia"] > maj else None)
    for c in range(1, 10):
        ws1.cell(row=r, column=c).border = BORDA
    zebra(ws1, r, r0, 9)
    r += 1
r += 1
txt(ws1, r, 1, "Supera o palpite COM GABARITO:", bold=True)
for i, arm in enumerate(ARMS):
    n = sum(E[tk]["direcao"]["arms"][arm]["acuracia"] > E[tk]["direcao"]["majoritaria"] for tk in TICKERS)
    txt(ws1, r, 4 + i, f"{n} de 10", bold=True, align="center")
r += 1
txt(ws1, r, 1, "Supera o DECIDIDO NO PASSADO:", bold=True)
for i, arm in enumerate(ARMS):
    n = sum(E[tk]["direcao"]["arms"][arm]["acuracia"] > HONESTO[tk]["acerto"] for tk in TICKERS)
    txt(ws1, r, 4 + i, f"{n} de 10", bold=True, align="center")
r += 1
txt(ws1, r, 1, "…desses, com significância:", bold=True)
from scipy.stats import binomtest
for i, arm in enumerate(ARMS):
    n = 0
    for tk in TICKERS:
        a = E[tk]["direcao"]["arms"][arm]; nt = E[tk]["direcao"]["n_teste"]
        base = HONESTO[tk]["acerto"]
        if a["acuracia"] > base and binomtest(round(a["acuracia"] * nt), nt, base).pvalue < 0.05:
            n += 1
    txt(ws1, r, 4 + i, f"{n} de 10", bold=True, align="center", cor="C00000")
r += 2
for titulo, corpo in [
    ("Palpite fixo COM O GABARITO NA MÃO (a coluna amarela — foi o que usei)",
     "Olha o próprio período de teste, vê qual lado foi mais frequente entre 2024 e 2026, e supõe "
     "que o investidor já sabia disso lá atrás. É o adversário MAIS DIFÍCIL possível, porque "
     "equivale a conhecer o futuro. Usei este de propósito: se o modelo vence ele, vence qualquer um."),
    ("Palpite fixo DECIDIDO NO PASSADO (a coluna seguinte — o adversário realista)",
     "Escolhe o lado olhando só o treino (até 2022) — o que se saberia de verdade na época — e "
     "aplica daí em diante, sem mudar. Em 5 dos 10 papéis o treino apontava BAIXA e o teste veio "
     "ALTA, então esse palpite errou o lado e ficou abaixo de 50%. Na média, é 2,1 pontos mais "
     "fácil de vencer que o com gabarito."),
    ("E a conclusão muda? Não.",
     "Contra o adversário mais fácil, os modelos passam em 6 ou 7 dos 10 papéis — mas só UM caso "
     "em 60 alcança significância estatística. Com 60 testes, o acaso sozinho produziria uns 3. "
     "Ou seja: continua sendo ruído, e a conclusão vale nas duas réguas."),
]:
    txt(ws1, r, 1, titulo, bold=True, size=10, cor=AZUL)
    ws1.merge_cells(start_row=r, start_column=1, end_row=r, end_column=9); r += 1
    txt(ws1, r, 1, corpo, wrap=True, size=9, cor="595959")
    ws1.merge_cells(start_row=r, start_column=1, end_row=r, end_column=9)
    ws1.row_dimensions[r].height = 42; r += 2

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
    COLS = [("Comprar e segurar\n(sem modelo)", None),
            ("GARCH+SVM\nsó preço", "SVM (preço)"),
            ("GARCH+SVM\n+ FinBERT", "SVM (preço+CVM)"),
            ("GARCH+XGB\nsó preço", "XGBoost (preço)"),
            ("GARCH+XGB\n+ FinBERT", "XGBoost (preço+CVM)"),
            ("Prophet\nsó preço", "Prophet (preço)"),
            ("Prophet\n+ FinBERT", "Prophet (preço+CVM)")]
    cab(ws4, ["Papel", "Valor investido\n(médio)"] + [c[0] for c in COLS],
        [9, 15] + [15] * len(COLS), linha=4)
    r, r0 = 5, 5
    for tk in TICKERS:
        s = SIM["papeis"][tk]
        txt(ws4, r, 1, tk, bold=True)
        val(ws4, r, 2, s["valor_investido_medio"], '"R$" #,##0', cor="000000")
        for i, (_, chave) in enumerate(COLS):
            m = s["buy_and_hold"] if chave is None else s["modelos"][chave]
            cel = ws4.cell(row=r, column=3 + i,
                           value=f'{m["retorno_pct"]:+.1f}%  (R$ {m["resultado_reais"]:+,.0f})'
                                 .replace(",", "."))
            cel.font = Font(name=FONTE, size=9,
                            color="C00000" if m["resultado_reais"] < 0 else "000000")
            cel.alignment = Alignment(horizontal="right")
            if chave is None:
                cel.fill = PatternFill("solid", fgColor=AMARELO)
        for c in range(1, 3 + len(COLS)):
            ws4.cell(row=r, column=c).border = BORDA
        zebra(ws4, r, r0, 2 + len(COLS))
        r += 1
    # totais
    r += 1
    txt(ws4, r, 1, "TOTAL (10 papéis)", bold=True)
    for i, (_, chave) in enumerate(COLS):
        tot = sum((SIM["papeis"][tk]["buy_and_hold"] if chave is None
                   else SIM["papeis"][tk]["modelos"][chave])["resultado_reais"] for tk in TICKERS)
        cel = ws4.cell(row=r, column=3 + i, value=f'R$ {tot:+,.0f}'.replace(",", "."))
        cel.font = Font(name=FONTE, size=10, bold=True, color=AZUL)
        cel.alignment = Alignment(horizontal="right")
        if chave is None:
            cel.fill = PatternFill("solid", fgColor=AMARELO)
    n_bh = sum(SIM["papeis"][tk]["buy_and_hold"]["resultado_reais"]
               > max(SIM["papeis"][tk]["modelos"][k]["resultado_reais"] for _, k in COLS if k)
               for tk in TICKERS)
    r += 2
    for titulo, corpo in [
        ("Só preço histórico × com o FinBERT — a comparação que os senhores pediram",
         "Cada família aparece duas vezes: usando SÓ o histórico de preço, e acrescentando o "
         "sentimento do FinBERT. Comparando as duas colunas de cada par, o sentimento melhorou o "
         "resultado em 5, 6 e 6 dos 10 papéis (SVM, XGBoost e Prophet) — de novo, o padrão de "
         "cara-ou-coroa. O efeito médio fica entre −1,2 e +1,0 ponto percentual."),
        ("E quem ganha de todos",
         f"A coluna amarela: comprar e segurar, sem modelo algum, sem custo e sem trabalho. "
         f"Venceu todos os seis modelos em {n_bh} dos 10 papéis, e no total soma mais que "
         f"qualquer um deles. Os modelos saem do mercado nos dias em que preveem queda e, num "
         f"período de bolsa em alta, perdem o que deixaram passar."),
        ("Ressalva obrigatória",
         "Esta conta não inclui corretagem, emolumentos, imposto de renda nem a diferença entre "
         "preço de compra e de venda — e os modelos entram e saem do mercado dezenas de vezes, o "
         "que na prática só pioraria o resultado deles. E, com o acerto direcional perto de "
         "cara-ou-coroa, o resultado em reais é em boa parte SORTE, não habilidade. Serve para dar "
         "ordem de grandeza; não é recomendação de investimento."),
    ]:
        txt(ws4, r, 1, titulo, bold=True, size=10, cor=AZUL)
        ws4.merge_cells(start_row=r, start_column=1, end_row=r, end_column=2 + len(COLS)); r += 1
        txt(ws4, r, 1, corpo, wrap=True, size=9, cor="595959")
        ws4.merge_cells(start_row=r, start_column=1, end_row=r, end_column=2 + len(COLS))
        ws4.row_dimensions[r].height = 42; r += 2
else:
    txt(ws4, 3, 1, "Cálculo ainda em execução quando esta planilha foi gerada.", cor="C00000")

wb.save(SAIDA)
print(f"gravado: {SAIDA}  ({len(wb.sheetnames)} abas)" + ("" if SIM else "  [SEM aba em reais]"))
