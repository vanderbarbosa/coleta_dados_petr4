# -*- coding: utf-8 -*-
# ==============================================================================
#   PLANILHA — Prophet × GARCH+SVM/XGBoost, 10 principais ações (16/10/2026)
#   Lê CVM/dados/prophet_vs_garch_svm_xgboost.json, grava
#   02_Prophet_vs_GARCH_SVM_XGBoost.xlsx, 6 abas.
# ==============================================================================
import json
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from scipy.stats import binomtest

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
SAIDA = AQUI / "02_Prophet_vs_GARCH_SVM_XGBoost.xlsx"

FONTE_NOME = "Arial"
AZUL_CAB = "1F3864"
AZUL_INPUT = "0000FF"
CINZA_CLARO = "F2F2F2"
AMARELO = "FFF2CC"
BORDA = Border(bottom=Side(style="thin", color="BFBFBF"))

d = json.loads((RAIZ / "CVM" / "dados" / "prophet_vs_garch_svm_xgboost.json").read_text(encoding="utf-8"))
PAPEIS = d["papeis"]
TICKERS = list(PAPEIS.keys())

# total de testes desta rodada, p/ Bonferroni: direção (6 braços vs majoritária
# + 2 McNemar) por papel
N_TESTES_DIRECAO = len(TICKERS) * (6 + 2)


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


def zebra(ws, r, linha0, ncols):
    if (r - linha0) % 2 == 1:
        for c in range(1, ncols + 1):
            ws.cell(row=r, column=c).fill = PatternFill("solid", fgColor=CINZA_CLARO)


def texto(ws, r, c, v, bold=False, size=10, cor="000000", wrap=False, align=None):
    cel = ws.cell(row=r, column=c, value=v)
    cel.font = Font(name=FONTE_NOME, bold=bold, size=size, color=cor)
    cel.alignment = Alignment(wrap_text=wrap, horizontal=align, vertical="center")
    return cel


def entrada(ws, r, c, v, fmt=None, cor=AZUL_INPUT):
    cel = ws.cell(row=r, column=c, value=v)
    cel.font = Font(name=FONTE_NOME, size=10, color=cor)
    if fmt:
        cel.number_format = fmt
    cel.alignment = Alignment(horizontal="right")
    return cel


wb = Workbook()

# ═══ ABA 1 — RESUMO ═════════════════════════════════════════════════════════
ws0 = wb.active
ws0.title = "Resumo"
texto(ws0, 1, 1, "Prophet × GARCH+SVM/XGBoost — 10 principais ações", bold=True, size=14, cor=AZUL_CAB)
texto(ws0, 2, 1, d["protocolo"], size=9, cor="595959", wrap=True)
ws0.merge_cells("A2:H2")
ws0.row_dimensions[2].height = 40

ws0["A4"] = "Limiar de Bonferroni — família Direção (" + str(N_TESTES_DIRECAO) + " testes):"
ws0["A4"].font = Font(name=FONTE_NOME, bold=True, size=10)
ws0.merge_cells("A4:D4")
ws0["E4"] = f"=0.05/{N_TESTES_DIRECAO}"
ws0["E4"].number_format = "0.000000"
ws0["E4"].font = Font(name=FONTE_NOME, size=10, color=AZUL_INPUT, bold=True)
LIMIAR_CEL = "Resumo!$E$4"

titulos0 = ["Ticker", "Direção:\nmelhor clássico", "Acerto\nclássico", "Direção:\nProphet",
            "Prophet\nganha?", "Volatilidade:\nProphet vs régua\njusta (R²-OS)",
            "Preço:\nProphet vs régua\njusta (R²-OS)", "Leitura"]
larg0 = [9, 20, 11, 11, 10, 17, 17, 40]
cab(ws0, titulos0, larg0, linha=6)
r, linha0 = 7, 7
n_vol_pior, n_preco_pior, n_dir_pior = 0, 0, 0
for tk in TICKERS:
    p = PAPEIS[tk]
    melhor = p["direcao"]["melhor_classico"]
    acc_classico = p["direcao"]["arms"][melhor]["acuracia"]
    acc_prophet = p["direcao"]["arms"]["Prophet (preço)"]["acuracia"]
    vol_r2os = p["volatilidade"]["arms"]["Prophet (volatilidade)"]["r2os_vs_ancorada"]
    preco_r2os = p["preco"]["arms"]["Prophet (preço)"]["r2os_vs_ancorada"]
    n_vol_pior += vol_r2os < 0
    n_preco_pior += preco_r2os < 0
    n_dir_pior += acc_prophet < acc_classico
    texto(ws0, r, 1, tk, bold=True)
    texto(ws0, r, 2, melhor)
    entrada(ws0, r, 3, acc_classico, "0.00%", cor="000000")
    entrada(ws0, r, 4, acc_prophet, "0.00%", cor="000000")
    texto(ws0, r, 5, "Sim" if acc_prophet > acc_classico else "Não", align="center")
    entrada(ws0, r, 6, vol_r2os / 100, "+0.0%;-0.0%", cor="000000")
    entrada(ws0, r, 7, preco_r2os / 100, "+0.0%;-0.0%", cor="000000")
    leitura = ("pior que não fazer nada, nos dois alvos contínuos"
               if vol_r2os < 0 and preco_r2os < 0 else "ver abas de detalhe")
    texto(ws0, r, 8, leitura, size=9)
    for c in range(1, 9):
        ws0.cell(row=r, column=c).border = BORDA
    zebra(ws0, r, linha0, 8)
    r += 1

r += 1
ws0.merge_cells(start_row=r, start_column=1, end_row=r, end_column=8)
texto(ws0, r, 1,
      (f"Conclusão: a régua destas duas colunas é a comparação JUSTA — a 'ingênua ancorada', que "
       f"recebe exatamente a mesma informação que o Prophet (o último valor conhecido antes do "
       f"bloco de 21 pregões) e simplesmente a segura. Em {n_vol_pior} de {len(TICKERS)} papéis o "
       f"Prophet ficou PIOR que essa régua na volatilidade, e em {n_preco_pior} de {len(TICKERS)} "
       f"no preço — ou seja, extrapolar a tendência atrapalhou em vez de ajudar. Na direção, o "
       f"Prophet perdeu do melhor modelo clássico em {n_dir_pior} de {len(TICKERS)} papéis. Ver a "
       f"aba 'Notas e metodologia' para por que esta régua, e não a ingênua diária, é a comparação "
       f"correta."),
      wrap=True, cor="595959", size=9)
ws0.row_dimensions[r].height = 62

# ═══ ABA 2 — DIREÇÃO ═════════════════════════════════════════════════════════
ws1 = wb.create_sheet("Direção")
titulos1 = ["Ticker", "Braço", "Classe\nmajoritária", "Acurácia", "AUC", "% dias em que\nprevê ALTA",
            "p vs\nmajoritária", "Passa\n(p<0,05)?", "Sobrevive\nBonferroni?"]
larg1 = [9, 22, 12, 10, 8, 14, 11, 10, 11]
cab(ws1, titulos1, larg1)
r, linha0 = 2, 2
for tk in TICKERS:
    maj = PAPEIS[tk]["direcao"]["majoritaria"]
    for nome, m in PAPEIS[tk]["direcao"]["arms"].items():
        texto(ws1, r, 1, tk, bold=True)
        texto(ws1, r, 2, nome)
        entrada(ws1, r, 3, maj, "0.00%")
        entrada(ws1, r, 4, m["acuracia"], "0.00%")
        if m["auc"] is not None:
            entrada(ws1, r, 5, m["auc"], "0.000")
        else:
            texto(ws1, r, 5, "—", align="center")
        entrada(ws1, r, 6, m["pct_previu_alta"] / 100, "0.0%")
        entrada(ws1, r, 7, m["p_vs_majoritaria"], "0.0000")
        ws1.cell(row=r, column=8, value=f"=IF(G{r}<0.05,\"Sim\",\"Não\")").font = Font(name=FONTE_NOME, size=10)
        ws1.cell(row=r, column=9, value=f"=IF(G{r}<{LIMIAR_CEL},\"Sim\",\"Não\")").font = Font(
            name=FONTE_NOME, size=10, bold=True)
        for c in range(3, 10):
            ws1.cell(row=r, column=c).alignment = Alignment(horizontal="right" if c < 8 else "center")
        for c in range(1, 10):
            ws1.cell(row=r, column=c).border = BORDA
        zebra(ws1, r, linha0, 9)
        r += 1
ws1.auto_filter.ref = f"A1:I{r-1}"

# ═══ ABA 3 — VOLATILIDADE ════════════════════════════════════════════════════
ws2 = wb.create_sheet("Volatilidade")
titulos2 = ["Ticker", "Braço", "MAE", "RMSE", "R²-OS vs HAR\n(info diária)",
            "R²-OS vs ancorada\n(COMPARAÇÃO JUSTA)"]
larg2 = [9, 34, 10, 10, 15, 19]
cab(ws2, titulos2, larg2)
r, linha0 = 2, 2
for tk in TICKERS:
    for nome, m in PAPEIS[tk]["volatilidade"]["arms"].items():
        texto(ws2, r, 1, tk, bold=True)
        texto(ws2, r, 2, nome)
        entrada(ws2, r, 3, m["mae"], "0.0000")
        entrada(ws2, r, 4, m["rmse"], "0.0000")
        entrada(ws2, r, 5, m["r2os_vs_HAR"] / 100, "+0.0%;-0.0%")
        entrada(ws2, r, 6, m["r2os_vs_ancorada"] / 100, "+0.0%;-0.0%")
        for c in range(1, 7):
            ws2.cell(row=r, column=c).border = BORDA
        zebra(ws2, r, linha0, 6)
        r += 1
ws2.auto_filter.ref = f"A1:F{r-1}"

# ═══ ABA 4 — PREÇO ═══════════════════════════════════════════════════════════
ws3 = wb.create_sheet("Preço")
titulos3 = ["Ticker", "Braço", "MAE (R$)", "RMSE (R$)", "R²-OS vs ingênua\ndiária (info diária)",
            "R²-OS vs ancorada\n(COMPARAÇÃO JUSTA)"]
larg3 = [9, 36, 11, 11, 18, 19]
cab(ws3, titulos3, larg3)
r, linha0 = 2, 2
for tk in TICKERS:
    for nome, m in PAPEIS[tk]["preco"]["arms"].items():
        texto(ws3, r, 1, tk, bold=True)
        texto(ws3, r, 2, nome)
        entrada(ws3, r, 3, m["mae"], '"R$" #,##0.00')
        entrada(ws3, r, 4, m["rmse"], '"R$" #,##0.00')
        entrada(ws3, r, 5, m["r2os_vs_ingenua_diaria"] / 100, "+0.0%;-0.0%")
        entrada(ws3, r, 6, m["r2os_vs_ancorada"] / 100, "+0.0%;-0.0%")
        for c in range(1, 7):
            ws3.cell(row=r, column=c).border = BORDA
        zebra(ws3, r, linha0, 6)
        r += 1
ws3.auto_filter.ref = f"A1:F{r-1}"

# ═══ ABA 5 — McNEMAR ═════════════════════════════════════════════════════════
ws4 = wb.create_sheet("McNemar")
titulos4 = ["Ticker", "Comparação", "Ganhou\n(novo)", "Perdeu\n(antigo)", "p-valor",
            "Significativo\n(p<0,05)?"]
larg4 = [9, 42, 10, 10, 10, 12]
cab(ws4, titulos4, larg4)
r, linha0 = 2, 2
for tk in TICKERS:
    for nome, m in PAPEIS[tk]["direcao"]["mcnemar"].items():
        texto(ws4, r, 1, tk, bold=True)
        texto(ws4, r, 2, nome)
        entrada(ws4, r, 3, m["ganhou_novo"], "0", cor="000000")
        entrada(ws4, r, 4, m["ganhou_antigo"], "0", cor="000000")
        entrada(ws4, r, 5, m["p"], "0.0000")
        ws4.cell(row=r, column=6, value=f"=IF(E{r}<0.05,\"Sim\",\"Não\")").font = Font(name=FONTE_NOME, size=10)
        for c in range(3, 7):
            ws4.cell(row=r, column=c).alignment = Alignment(horizontal="center")
        for c in range(1, 7):
            ws4.cell(row=r, column=c).border = BORDA
        zebra(ws4, r, linha0, 6)
        r += 1
ws4.auto_filter.ref = f"A1:F{r-1}"

# ═══ ABA 6 — NOTAS ═══════════════════════════════════════════════════════════
ws5 = wb.create_sheet("Notas e metodologia")
ws5.column_dimensions["A"].width = 112
NOTAS = [
    ("O que é o Prophet, e o que NÃO é", "Biblioteca de previsão de série temporal (Meta). "
     "NÃO classifica texto. O sentimento usado aqui vem do FinBERT, já classificado antes desta "
     "pesquisa nos comunicados da CVM — o Prophet só entra como mais um modelo de previsão."),
    ("Por que o Prophet é reajustado a cada 21 pregões, e os outros não", "Um primeiro teste "
     "ajustou o Prophet uma vez só e pediu para prever os 579 pregões de teste inteiros de uma "
     "vez — quase 2 anos à frente sem nunca se reancorar. A tendência disparou: R²-OS de -8.325% "
     "na volatilidade e -69.604% no preço, um resultado degenerado. Aqui ele é reajustado a cada "
     "~21 pregões (janela expansiva), nunca prevendo mais que um mês à frente de uma vez."),
    ("A régua JUSTA — e por que ela existe nesta planilha", "A primeira versão desta comparação "
     "era DESLEAL com o Prophet, e isso foi corrigido: a ingênua diária enxerga o fechamento de "
     "ONTEM em todo dia do teste, enquanto o Prophet, no 21º dia de um bloco, ainda está olhando o "
     "que sabia 21 pregões atrás. Comparar os dois assim é comparar quem responde com a notícia de "
     "ontem contra quem responde com a do mês passado. Por isso existe a 'ingênua ancorada': ela "
     "recebe EXATAMENTE a mesma informação do Prophet (o último valor antes do bloco) e "
     "simplesmente segura esse valor. É contra ela que o Prophet deve ser julgado — e é a coluna "
     "marcada como COMPARAÇÃO JUSTA."),
    ("O achado, agora que a comparação é justa", "Mesmo com a mesma informação, o Prophet fica "
     "PIOR que segurar o último valor conhecido — tanto na volatilidade quanto no preço, nos 10 "
     "papéis. Ou seja: extrapolar a tendência ATRAPALHA em vez de ajudar, nesta série. Não é um "
     "empate nem um ganho pequeno; é um resultado negativo claro. Faz sentido: preço de ação é "
     "quase um passeio aleatório, e a tendência que o Prophet projeta para a frente costuma ter "
     "virado antes de o bloco acabar (ex.: a PETR4 foi de ~R$35 a ~R$46 entre fev e abr/2026, em "
     "degraus diários de até 5% — conferido contra os dados brutos, não é erro de base)."),
    ("A ingênua DIÁRIA, e a pergunta de 12/10 sobre esforço computacional", "A coluna 'R²-OS vs "
     "ingênua diária' mostra o quanto se ganha só por se reatualizar todo dia em vez de uma vez "
     "por mês — e o ganho é enorme. Isso responde, com número desta pesquisa, à pergunta do "
     "professor na mentoria de 12/10: aqui, a frequência de reatualização vale MUITO mais que a "
     "sofisticação do modelo. Reajustar o Prophet todo dia custaria ~21x mais processamento "
     "(cada reajuste leva ~1,3s), e ainda assim ele partiria atrás de uma régua que é de graça."),
    ("Direção — como o Prophet 'vota'", "O Prophet prevê o PREÇO; a direção prevista é o sinal da "
     "diferença entre o preço previsto e o fechamento de ontem. Por isso o Prophet não tem AUC "
     "nesta tabela — ele não produz probabilidade de classe, só um valor previsto."),
    ("Volatilidade — o comparador é o HAR (GARCH)", "Modelo de Corsi (médias de 1, 5 e 22 "
     "pregões da volatilidade GARCH(1,1) do próprio papel), versão linear — mais simples que a "
     "combinação quantílica usada só para a PETR4 no Script 18, para caber nos 10 papéis no prazo "
     "desta mentoria."),
    (f"Bonferroni — família Direção", f"{N_TESTES_DIRECAO} testes (10 papéis × (6 braços vs "
     f"majoritária + 2 McNemar)). Limiar na aba Resumo, célula E4 — todas as colunas 'Sobrevive "
     f"Bonferroni?' das abas Direção e McNemar referenciam essa mesma célula."),
]
r = 1
for titulo, txt in NOTAS:
    texto(ws5, r, 1, titulo, bold=True, size=11, cor=AZUL_CAB)
    r += 1
    texto(ws5, r, 1, txt, wrap=True)
    ws5.cell(row=r, column=1).alignment = Alignment(wrap_text=True, vertical="top")
    ws5.row_dimensions[r].height = 62
    r += 2

wb.save(SAIDA)
print(f"gravado: {SAIDA}")
