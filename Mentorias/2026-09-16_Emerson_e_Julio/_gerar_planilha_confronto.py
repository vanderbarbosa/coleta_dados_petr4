# -*- coding: utf-8 -*-
# ==============================================================================
#   Planilha do confronto de fontes — para projetar na reunião
#   Saída: 07_Combinar_as_fontes.xlsx
# ==============================================================================
import json
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
SAIDA = AQUI / "07_Combinar_as_fontes.xlsx"

N = json.loads((RAIZ / "CVM" / "dados" / "numeros_confronto.json").read_text(encoding="utf-8"))
C, F, CO = N["confronto"], N["filtro"], N["cobertura"]
RI, RC = N["regra_ingenua"], N["regra_corrigida"]

AZUL, CAB = "1F3864", "D9E2F3"
VERDE, VERM, CINZA, AMAR = "C6EFCE", "FFC7CE", "F2F2F2", "FFEB9C"
B = Border(*[Side(style="thin", color="BFBFBF")] * 4)


def tit(ws, txt, n, linha=1, sub=None):
    ws.merge_cells(start_row=linha, start_column=1, end_row=linha, end_column=n)
    c = ws.cell(row=linha, column=1, value=txt)
    c.font = Font(bold=True, size=13, color="FFFFFF")
    c.fill = PatternFill("solid", fgColor=AZUL)
    c.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[linha].height = 26
    if sub:
        ws.merge_cells(start_row=linha + 1, start_column=1, end_row=linha + 1, end_column=n)
        c = ws.cell(row=linha + 1, column=1, value=sub)
        c.font = Font(italic=True, size=9, color="404040")
        c.alignment = Alignment(horizontal="center")


def cab(ws, cols, linha):
    for j, (nome, larg) in enumerate(cols, start=1):
        c = ws.cell(row=linha, column=j, value=nome)
        c.font = Font(bold=True, size=10, color=AZUL)
        c.fill = PatternFill("solid", fgColor=CAB)
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = B
        ws.column_dimensions[get_column_letter(j)].width = larg
    ws.row_dimensions[linha].height = 32


def lin(ws, r, vals, cor=None, neg=False, alt=None):
    for j, v in enumerate(vals, start=1):
        c = ws.cell(row=r, column=j, value=v)
        c.alignment = Alignment(vertical="center", wrap_text=True)
        c.border = B
        c.font = Font(size=10, bold=neg)
        if cor:
            c.fill = PatternFill("solid", fgColor=cor)
    if alt:
        ws.row_dimensions[r].height = alt


def nota(ws, r, txt, cor="006100", tam=11):
    c = ws.cell(row=r, column=1, value=txt)
    c.font = Font(bold=True, size=tam, color=cor)
    return r + 2


def main() -> None:
    wb = Workbook()

    # ═══════════════════════════════════════════════════ ABA 1 — RESPOSTA ════
    ws = wb.active
    ws.title = "A resposta"
    tit(ws, "JUNTAR JORNAL COM COMUNICADO OFICIAL AJUDA A PREVER O DIA SEGUINTE?", 6,
        sub=f"PETR4 · {CO['pregoes']:,} pregões · ".replace(",", ".") +
            f"{CO['com_ambos']:,} noites com as duas fontes · ".replace(",", ".") +
            f"{CO['com_fr']} noites com Fato Relevante")

    r = 4
    r = nota(ws, r, "NOS DIAS EM QUE AS DUAS FONTES EXISTEM", AZUL, 12)
    cab(ws, [("Quem faz a previsão", 30), ("Noites", 10), ("Acertou", 11),
             ("Quem não lê nada", 16), ("Ganho", 13), ("Vale?", 22)], r)
    r += 1
    for k, rot in [("inter_dev_news", "Só o jornal"),
                   ("inter_dev_cvm", "Só o comunicado da CVM"),
                   ("inter_dev_ambos", "Os dois juntos")]:
        o = C[k]
        bom = o["p"] < 0.05
        lin(ws, r, [rot, f"{o['n']:,}".replace(",", "."), f"{o['acuracia']:.1%}",
                    f"{o['maj']:.1%}", f"{o['ganho_pp']:+.2f} pts",
                    f"sim (p={o['p']:.3f})" if bom else f"não (p={o['p']:.2f})"],
            VERDE if bom else VERM, bom, 22)
        r += 1
    r += 1
    r = nota(ws, r, "O jornal funciona. O comunicado oficial, sozinho, NÃO prevê direção.")

    r = nota(ws, r, "E NAS NOITES DE FATO RELEVANTE?", AZUL, 12)
    cab(ws, [("Quem faz a previsão", 30), ("Noites", 10), ("Acertou", 11),
             ("Quem não lê nada", 16), ("Ganho", 13), ("Vale?", 22)], r)
    r += 1
    for k, rot in [("fatorel_dev_news", "Só o jornal"),
                   ("fatorel_dev_cvm", "Só o comunicado da CVM"),
                   ("fatorel_dev_ambos", "OS DOIS JUNTOS")]:
        o = C[k]
        bom = o["p"] < 0.05
        lin(ws, r, [rot, f"{o['n']:,}".replace(",", "."), f"{o['acuracia']:.1%}",
                    f"{o['maj']:.1%}", f"{o['ganho_pp']:+.2f} pts",
                    f"sim (p={o['p']:.3f})" if bom else f"não (p={o['p']:.3f})"],
            VERDE if bom else CINZA, bom, 22)
        r += 1
    r += 1
    r = nota(ws, r, "MELHOR RESULTADO DE DIREÇÃO DA PESQUISA INTEIRA. "
                    "E o jornal sozinho não passa no teste — só a combinação passa.")

    # ═════════════════════════════════════════════════ ABA 2 — O FRACASSO ════
    ws = wb.create_sheet("O que deu errado")
    tit(ws, "A PRIMEIRA REGRA FALHOU — E O DIAGNÓSTICO É O QUE IMPORTA", 4,
        sub="Registrado porque explica seis pontos percentuais de diferença")
    r = 4
    cab(ws, [("", 44), ("Regra inicial", 20), ("Regra corrigida", 20), ("", 10)], r)
    r += 1
    for rot, a, b, cor in [
        ("A pergunta que ela fazia",
         "houve mais notícias positivas que negativas?",
         "esta noite foi pior que o habitual desta ação?", None),
        ("Com o que comparava", "com zero",
         "com a média dos 60 pregões anteriores", None),
        ("Quanto previa ALTA", "1,0% das noites",
         f"{RC['preve_alta_pct']}% das noites", AMAR),
        ("Acurácia", f"{RI['acuracia']}%",
         f"{C['todos_dev_news']['acuracia']:.1%}", VERDE),
        ("Contra quem não lê nada", f"{RI['majoritaria']}%",
         f"{C['todos_dev_news']['maj']:.1%}", None),
        ("Resultado", "ABAIXO do acaso",
         f"{C['todos_dev_news']['ganho_pp']:+.2f} pontos de vantagem", None),
    ]:
        lin(ws, r, [rot, a, b, ""], cor, False, 30)
        r += 1
    r += 1
    for t in [
        "POR QUE A PRIMEIRA REGRA FALHOU",
        "",
        "O programa que lê os textos enxerga quase metade do corpus como negativo,",
        "e só 14% como positivo. Somar uma noite inteira, com um leitor assim, quase",
        "nunca dá saldo positivo.",
        "",
        f"Resultado: ela previu BAIXA em {RI['preve_baixa_pct']}% das noites.",
        "",
        "Uma regra que diz a mesma coisa em 99% dos casos não é previsão, é constante.",
        "Ela não estava errando. Ela não estava dizendo nada.",
        "",
        "E inverter o sinal também não resolveria: daria 52,2%, ainda abaixo dos 52,5%",
        "de quem chuta sempre o mesmo lado.",
    ]:
        c = ws.cell(row=r, column=1, value=t)
        c.font = Font(bold=t.isupper() and len(t) > 5, size=10)
        r += 1

    # ══════════════════════════════════════════════════ ABA 3 — O FILTRO ═════
    ws = wb.create_sheet("A CVM como filtro")
    tit(ws, "HIPÓTESE: A CVM DIZ EM QUAL NOITE VALE A PENA LER O JORNAL", 5,
        sub="Mesma regra, lendo só o jornal. Muda apenas o tipo de noite.")
    r = 4
    cab(ws, [("Tipo de noite", 34), ("Noites", 10), ("Acertou", 11),
             ("Quem não lê nada", 16), ("Vantagem do jornal", 20)], r)
    r += 1
    for k, rot, cor in [
        ("noite SEM comunicado nenhum", "Sem comunicado nenhum", CINZA),
        ("noite com Comunicado, sem Fato Relevante", "Com Comunicado ao Mercado", CINZA),
        ("noite com FATO RELEVANTE", "Com FATO RELEVANTE", AMAR),
    ]:
        o = F[k]
        lin(ws, r, [rot, f"{o['n']:,}".replace(",", "."), f"{o['acuracia']:.1%}",
                    f"{o['maj']:.1%}", f"{o['ganho_pp']:+.2f} pontos"],
            cor, k.endswith("RELEVANTE"), 22)
        r += 1
    r += 1
    for t in [
        "A vantagem TRIPLICA conforme a noite fica mais importante.",
        "A ordem é exatamente a que a tese da pesquisa prevê.",
        "",
        "MAS ISTO NÃO É UM RESULTADO — É UMA HIPÓTESE.",
        "",
        f"A diferença entre as noites de Fato Relevante e as demais é de "
        f"{F['teste_filtro']['dif_pp']:+.2f} pontos,",
        f"com valor-p de {F['teste_filtro']['p']:.2f}. Não passa no teste estatístico.",
        "",
        "Para decidir seriam precisas cerca de 15.200 noites de Fato Relevante.",
        "Temos 393. Estendendo para VALE3, ITUB4 e BBAS3 chega-se a 626 — ainda",
        "24 vezes menos do que o necessário.",
        "",
        "Apresentar isto como achado seria impróprio. Fica como hipótese.",
    ]:
        c = ws.cell(row=r, column=1, value=t)
        c.font = Font(bold=t.isupper() and len(t) > 10, size=10,
                      color="9C0006" if "NÃO É UM RESULTADO" in t else "000000")
        r += 1

    # ═════════════════════════════════════════════════ ABA 4 — COBERTURA ═════
    ws = wb.create_sheet("Como foi montado")
    tit(ws, "AS TRÊS EXIGÊNCIAS, PARA QUE A COMPARAÇÃO FOSSE JUSTA", 3)
    r = 4
    cab(ws, [("Exigência", 26), ("Por quê", 58), ("", 10)], r)
    r += 1
    for a, b in [
        ("A mesma janela",
         "Conta o que foi publicado entre o fechamento de um pregão e a abertura do "
         "seguinte. As duas fontes enxergam o mesmo intervalo."),
        ("Os mesmos dias",
         "Jornal existe quase toda noite; comunicado da CVM, não. Comparar um em "
         "2.000 dias com o outro em 900 não diz nada."),
        ("A mesma regra",
         "Saldo positivo prevê alta, negativo prevê baixa. Igual para as duas."),
        ("O mesmo adversário",
         "Tudo comparado contra quem não lê nada e sempre chuta o lado mais "
         "frequente. É o adversário honesto."),
    ]:
        lin(ws, r, [a, b, ""], None, False, 34)
        ws.cell(row=r, column=1).font = Font(size=10, bold=True)
        r += 1
    r += 1
    r = nota(ws, r, "COBERTURA", AZUL, 12)
    cab(ws, [("", 40), ("Pregões", 14), ("", 10)], r)
    r += 1
    for rot, v in [
        ("analisados", CO["pregoes"]),
        ("com ao menos uma notícia na noite", CO["com_noticia"]),
        ("com ao menos um comunicado da CVM", CO["com_cvm"]),
        ("com as DUAS fontes", CO["com_ambos"]),
        ("com Fato Relevante", CO["com_fr"]),
    ]:
        lin(ws, r, [rot, f"{v:,}".replace(",", ".") +
                    (f"  ({v/CO['pregoes']:.0%})" if rot != "analisados" else ""), ""],
            None, rot.startswith("com as DUAS"), 20)
        r += 1

    wb.save(SAIDA)
    print(f"  [OK] {SAIDA.name}  ({', '.join(wb.sheetnames)})")


if __name__ == "__main__":
    main()
