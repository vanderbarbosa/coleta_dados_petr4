# -*- coding: utf-8 -*-
# ==============================================================================
#   Painel de resultados — planilha para projetar na reunião
#   Saída: CVM/05_PAINEL_RESULTADOS.xlsx
#
#   Seis abas: Painel, Rodada A, Rodada B, Casos, PETR4 e Glossário.
# ==============================================================================
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

AQUI = Path(__file__).resolve().parent
DADOS = AQUI / "dados"
SAIDA = AQUI / "05_PAINEL_RESULTADOS.xlsx"

AZUL, CAB = "1F3864", "D9E2F3"
VERDE, VERM, AMAR, CINZA = "C6EFCE", "FFC7CE", "FFEB9C", "F2F2F2"
B = Border(*[Side(style="thin", color="BFBFBF")] * 4)


def titulo(ws, txt, n_cols, linha=1, sub=None):
    ws.merge_cells(start_row=linha, start_column=1, end_row=linha, end_column=n_cols)
    c = ws.cell(row=linha, column=1, value=txt)
    c.font = Font(bold=True, size=13, color="FFFFFF")
    c.fill = PatternFill("solid", fgColor=AZUL)
    c.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[linha].height = 26
    if sub:
        ws.merge_cells(start_row=linha + 1, start_column=1,
                       end_row=linha + 1, end_column=n_cols)
        c = ws.cell(row=linha + 1, column=1, value=sub)
        c.font = Font(italic=True, size=9, color="404040")
        c.alignment = Alignment(horizontal="center")


def cabecalho(ws, cols, linha):
    for j, (nome, larg) in enumerate(cols, start=1):
        c = ws.cell(row=linha, column=j, value=nome)
        c.font = Font(bold=True, size=10, color=AZUL)
        c.fill = PatternFill("solid", fgColor=CAB)
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = B
        ws.column_dimensions[get_column_letter(j)].width = larg
    ws.row_dimensions[linha].height = 32


def linha(ws, r, valores, cor=None, negrito=False, altura=None):
    for j, v in enumerate(valores, start=1):
        c = ws.cell(row=r, column=j, value=v)
        c.alignment = Alignment(vertical="center", wrap_text=True)
        c.border = B
        c.font = Font(size=10, bold=negrito)
        if cor:
            c.fill = PatternFill("solid", fgColor=cor)
    if altura:
        ws.row_dimensions[r].height = altura


def main() -> None:
    A = json.loads((DADOS / "rodada_A.json").read_text(encoding="utf-8"))
    Bj = json.loads((DADOS / "rodada_B.json").read_text(encoding="utf-8"))
    FC = json.loads((DADOS / "fr_vs_cm.json").read_text(encoding="utf-8"))
    BC = json.loads((DADOS / "rodada_B_por_categoria.json").read_text(encoding="utf-8"))
    casos_df = pd.read_csv(DADOS / "casos_concretos.csv")
    ver = casos_df["Veredicto"].value_counts()
    n_casos = len(casos_df)
    ctl = A["controle"]
    wb = Workbook()

    # ══════════════════════════════════════════════════════ ABA 1 — PAINEL ═══
    ws = wb.active
    ws.title = "PAINEL"
    titulo(ws, "A NOTÍCIA DA NOITE E O PREGÃO SEGUINTE — RESULTADO", 5,
           sub=f"{n_casos:,} comunicados entregues à CVM após o fechamento · 57 papéis da B3 · ".replace(",", ".") + 
               "2018 a 2026 · hora oficial do Protocolo de Entrega")

    r = 4
    ws.cell(row=r, column=1, value="A PERGUNTA 1: A NOTÍCIA MEXE NO PREÇO?").font = \
        Font(bold=True, size=12, color=AZUL)
    r += 1
    cabecalho(ws, [("Régua", 30), ("Dia SEM notícia", 16), ("Dia APÓS a notícia", 18),
                   ("Excesso", 14), ("Chance de ser sorte", 20)], r)
    r += 1
    v = ctl["volatilidade (Parkinson)"]
    q = ctl["volume negociado"]
    for rot, d, exc, cor in [
        ("Sacolejo do preço (volatilidade)", v, f"+{(v['com']/v['sem']-1)*100:.1f}%", VERDE),
        ("VOLUME negociado", q, f"+{(q['com']/q['sem']-1)*100:.1f}%", VERDE),
    ]:
        linha(ws, r, [rot, f"{d['sem']:.3f}", f"{d['com']:.3f}", exc,
                      f"{d['p']:.0e}  (praticamente nula)"], cor, True, 22)
        r += 1
    g = ctl["gap de abertura (%)"]
    linha(ws, r, ["Salto da abertura", f"{g['sem']*100:.3f}%", f"{g['com']*100:.3f}%",
                  f"+{(g['com']-g['sem'])*100:.2f} ponto", f"{g['p']:.3f}"], AMAR, False, 20)
    r += 1
    p_ = ctl["pregão inteiro (%)"]
    linha(ws, r, ["DIREÇÃO no pregão inteiro", f"{p_['sem']*100:.3f}%",
                  f"{p_['com']*100:.3f}%", "quase zero",
                  f"{p_['p']:.2f}  (pode ser sorte)"], VERM, False, 20)
    r += 2

    ws.cell(row=r, column=1,
            value="RESPOSTA: SIM, mexe — mas mexe no RISCO, não na direção.").font = \
        Font(bold=True, size=11, color="006100")
    r += 2

    ws.cell(row=r, column=1, value="A PERGUNTA 2: MEXE EM TODOS OS CASOS?").font = \
        Font(bold=True, size=12, color=AZUL)
    r += 1
    cabecalho(ws, [("No dia seguinte à notícia...", 30), ("Casos", 16),
                   ("Proporção", 18), ("", 14), ("", 20)], r)
    r += 1
    for chave, rot, cor in [("MEXEU MUITO", "MEXEU MUITO (2x o normal ou mais)", VERDE),
                            ("mexeu", "mexeu (1,3x ou mais)", VERDE),
                            ("dentro do normal", "ficou dentro do normal", CINZA),
                            ("dia mais parado que o normal",
                             "ficou MAIS PARADO que o normal", VERM)]:
        n = int(ver.get(chave, 0))
        linha(ws, r, [rot, f"{n:,}".replace(",", "."), f"{n/n_casos:.1%}", "", ""],
              cor, False, 20)
        r += 1
    r += 1
    nao = (n_casos - ver.get("MEXEU MUITO", 0) - ver.get("mexeu", 0)) / n_casos
    ws.cell(row=r, column=1,
            value=f"RESPOSTA: NAO. {nao:.1%} nao mexeram. O efeito medio vem de uma "
                  "MINORIA de casos -- e o efeito de cauda.").font = \
        Font(bold=True, size=11, color="9C0006")
    r += 2

    ws.cell(row=r, column=1,
            value="A PERGUNTA 3: DÁ PARA SABER SE VAI SUBIR OU DESCER?").font = \
        Font(bold=True, size=12, color=AZUL)
    r += 1
    cabecalho(ws, [("Quem faz a previsão", 30), ("Acertou", 16),
                   ("Quem não lê nada", 18), ("Ganho", 14), ("Chance de ser sorte", 20)], r)
    r += 1
    linha(ws, r, ["O rotulo da CVM", "nao se aplica",
                  "-", "IMPOSSIVEL", "o rotulo nao diz o lado"], CINZA, False, 22)
    r += 1
    for k_, rot, cor in [("so FATO RELEVANTE", "Nossa leitura - em FATO RELEVANTE", VERDE),
                         ("so COMUNICADO AO MERCADO",
                          "Nossa leitura - em Comunicado ao Mercado", VERM),
                         ("TODOS (FR + Comunicados)",
                          "Nossa leitura - os dois juntos", CINZA)]:
        b_ = BC[k_]
        obs = f"{b_['p']:.3f}" + ("  *" if b_["p"] < 0.05 else "  (pode ser sorte)")
        linha(ws, r, [rot, f"{b_['acuracia']:.1%}", f"{b_['maj']:.1%}",
                      f"{b_['ganho_pp']:+.2f} pts", obs], cor, b_["p"] < 0.05, 22)
        r += 1
    r += 1
    ws.cell(row=r, column=1,
            value="RESPOSTA: so a nossa leitura pode responder -- e SO funciona no "
                  "Fato Relevante, onde ganha 2,6 pontos. No Comunicado, ganha zero."
            ).font = Font(bold=True, size=11, color="006100")
    r += 2

    ws.cell(row=r, column=1,
            value="A LEI ACERTA? Fato Relevante contra Comunicado ao Mercado"
            ).font = Font(bold=True, size=12, color=AZUL)
    r += 1
    cabecalho(ws, [("Regua", 30), ("Fato Relevante", 16), ("Comunicado", 18),
                   ("Quantas vezes mais", 14), ("Chance de ser sorte", 20)], r)
    r += 1
    for k_, rot in [("volatilidade (sacolejo)", "Sacolejo do preco"),
                    ("volume negociado", "VOLUME negociado")]:
        f_ = FC[k_]
        linha(ws, r, [rot, f"+{f_['exc_fr_pct']:.1f}%", f"+{f_['exc_cm_pct']:.1f}%",
                      f"{f_['razao']:.1f}x", f"{f_['p']:.0e}"], VERDE, True, 22)
        r += 1
    r += 1
    ws.cell(row=r, column=1,
            value="SIM. O que a lei chama de RELEVANTE mexe 3 VEZES MAIS que o que "
                  "ela chama de simples comunicado."
            ).font = Font(bold=True, size=11, color="006100")
    r += 2

    ws.cell(row=r, column=1, value="E ONDE ESTÁ O SINAL?").font = \
        Font(bold=True, size=12, color=AZUL)
    r += 1
    cabecalho(ws, [("O programa disse que era...", 30), ("Casos", 16),
                   ("O preço fez, em média", 18), ("", 14), ("", 20)], r)
    r += 1
    for cls, cor in [("Positive", CINZA), ("Neutral", CINZA), ("Negative", VERM)]:
        d = Bj["por_classe"][cls]
        nome = {"Positive": "Positivo", "Neutral": "Neutro", "Negative": "NEGATIVO"}[cls]
        obs = "nada" if abs(d["retorno_pct"]) < 0.05 else ""
        linha(ws, r, [nome, f"{d['n']:,}".replace(",", "."),
                      f"{d['retorno_pct']:+.3f}%  {obs}", "", ""],
              cor, cls == "Negative", 20)
        r += 1
    r += 1
    ws.cell(row=r, column=1,
            value="O programa reconhece a notícia RUIM. Não reconhece a BOA.").font = \
        Font(bold=True, size=11, color="9C0006")

    # ═══════════════════════════════════════════════════ ABA 2 — RODADA A ════
    ws = wb.create_sheet("Rodada A - CVM")
    titulo(ws, "RODADA A — usando SÓ o rótulo que já vem da CVM", 6,
           sub="O rótulo diz que algo aconteceu, mas não diz se foi bom ou ruim. "
               "Por isso só pode testar TAMANHO, nunca direção.")
    r = 4
    ws.cell(row=r, column=1,
            value="Robustez: o efeito muda se eu escolher outra semana de comparação?"
            ).font = Font(bold=True, size=11, color=AZUL)
    r += 1
    cabecalho(ws, [("Linha de base usada", 26), ("Sacolejo", 14), ("Volume", 14),
                   ("", 10), ("", 10), ("", 10)], r)
    r += 1
    for nome in A["volatilidade"]:
        vv = A["volatilidade"][nome].get("Fato Relevante", {})
        qq = A["volume"][nome].get("Fato Relevante", {})
        linha(ws, r, [nome, f"{vv.get('razao','-')}", f"{qq.get('razao','-')}",
                      "", "", ""], None, False, 18)
        r += 1
    r += 1
    ws.cell(row=r, column=1,
            value="O efeito NÃO depende da janela escolhida — fica estável em torno "
                  "de 1,20 no sacolejo e 1,43 no volume.").font = Font(size=10, italic=True)
    r += 2
    ws.cell(row=r, column=1, value="Por que o piso NÃO é 1,00").font = \
        Font(bold=True, size=11, color=AZUL)
    r += 1
    for txt in [
        "A conta é: sacolejo do dia seguinte DIVIDIDO pela média da semana anterior.",
        "Parece que 1,00 seria o ponto neutro. Não é.",
        "Um dia pode ser 5x mais agitado que a média, mas nunca 5x menos — o piso é zero.",
        "Então a divisão já dá mais que 1 mesmo sem notícia nenhuma:",
        f"    sem notícia: {ctl['volatilidade (Parkinson)']['sem']:.3f} no sacolejo, "
        f"{ctl['volume negociado']['sem']:.3f} no volume",
        "É contra ESSES números que o excesso deve ser medido — e foi o que fiz.",
        "Sem esse cuidado eu teria anunciado +21,9% e +44,6%, em vez de +16,5% e +31,6%.",
    ]:
        ws.cell(row=r, column=1, value=txt).font = Font(size=10)
        r += 1

    # ═══════════════════════════════════════════════════ ABA 3 — RODADA B ════
    ws = wb.create_sheet("Rodada B - nossa")
    titulo(ws, "RODADA B — usando a NOSSA leitura do texto (FinBERT-PT-BR)", 10,
           sub="Regra declarada ANTES de rodar: Positivo prevê alta, Negativo prevê "
               "baixa, Neutro não prevê nada.")
    r = 4
    cabecalho(ws, [("Teste", 34), ("Casos", 9), ("Acertou", 10),
                   ("Palpite fixo", 12), ("Ganho", 10), ("p vs acaso", 11),
                   ("F1 macro", 10), ("kappa", 9), ("MCC", 9), ("", 8)], r)
    r += 1
    for k, t in Bj["testes"].items():
        cor = VERDE if t["ganho_sobre_majoritaria"] > 0 else VERM
        linha(ws, r, [k, t["n"], f"{t['acuracia']:.1%}",
                      f"{t['classe_majoritaria']:.1%}",
                      f"{t['ganho_sobre_majoritaria']*100:+.2f}",
                      f"{t['p_binomial_vs_50']:.4f}", f"{t['f1_macro']:.3f}",
                      f"{t['kappa']:+.3f}", f"{t['mcc']:+.3f}", ""], cor, False, 20)
        r += 1
    r += 1
    for txt in [
        "COMO LER 'palpite fixo': é quem não lê notícia nenhuma e sempre chuta o mesmo lado.",
        "Se a ação sobe em 57% dos dias, esse palpite acerta 57% sem esforço algum.",
        "Um modelo que acerte MENOS que isso não serve para nada, por mais sofisticado que seja.",
        "",
        "No SALTO DA ABERTURA nós perdemos dele: 54,7% contra 57,4%.",
        "No PREGÃO INTEIRO nós ganhamos: 55,0% contra 50,2%.",
        "",
        "kappa e MCC medem concordância ALÉM do acaso: 0 = puro acaso, 1 = perfeito.",
        "Os nossos ficam entre +0,09 e +0,13 — positivos, portanto reais, mas fracos.",
    ]:
        ws.cell(row=r, column=1, value=txt).font = Font(size=10, italic=not txt.startswith("COMO"))
        r += 1
    r += 1
    ws.cell(row=r, column=1, value="Correlação entre o tom do texto e o retorno").font = \
        Font(bold=True, size=11, color=AZUL)
    r += 1
    cabecalho(ws, [("Alvo", 34), ("Pearson", 9), ("p", 10), ("Spearman", 12),
                   ("p", 10), ("", 11), ("", 10), ("", 9), ("", 9), ("", 8)], r)
    r += 1
    for k, c in Bj["correlacao"].items():
        linha(ws, r, [k, c["pearson"], f"{c['p_pearson']:.4f}", c["spearman"],
                      f"{c['p_spearman']:.4f}", "", "", "", "", ""], None, False, 18)
        r += 1

    # ═════════════════════════════════════════════════════ ABA 4 — CASOS ═════
    casos = pd.read_csv(DADOS / "casos_concretos.csv")
    top = (casos[casos["Atribuivel"] & ~casos["Generico"]]
           .dropna(subset=["Volatilidade_vs_semana"])
           .nlargest(40, "Volatilidade_vs_semana"))
    ws = wb.create_sheet("Casos concretos")
    titulo(ws, "OS 40 MAIORES — notícia publicada à noite, pregão do dia seguinte", 8,
           sub="Só casos em que houve UM ÚNICO comunicado naquela noite, para que o "
               "movimento seja atribuível a ele")
    r = 4
    cabecalho(ws, [("Publicado em", 17), ("Papel", 8), ("O que a empresa comunicou", 52),
                   ("Pregão seguinte", 14), ("Sacolejo", 10), ("Volume", 10),
                   ("Direção", 10), ("Variação", 11)], r)
    r += 1
    for _, x in top.iterrows():
        cor = VERM if x["Direcao"] == "CAIU" else VERDE
        linha(ws, r, [str(x["Entrega"])[:16], x["Ticker"], str(x["Assunto"])[:150],
                      str(x["Pregao_reacao"])[:10],
                      f"{x['Volatilidade_vs_semana']:.1f}x",
                      f"{x['Volume_vs_semana']:.1f}x", x["Direcao"],
                      f"{x['Variacao_pct']:+.1f}%"], cor, False, 30)
        r += 1
    ws.freeze_panes = "A5"

    # ═════════════════════════════════════════════════════ ABA 5 — PETR4 ═════
    p4 = (casos[(casos["Ticker"] == "PETR4") & casos["Atribuivel"] & ~casos["Generico"]]
          .dropna(subset=["Volatilidade_vs_semana"])
          .nlargest(30, "Volatilidade_vs_semana"))
    ws = wb.create_sheet("PETR4")
    titulo(ws, "PETR4 — os 30 maiores", 8,
           sub=f"{(casos['Ticker']=='PETR4').sum()} comunicados da Petrobras após o "
               f"fechamento no período")
    r = 4
    cabecalho(ws, [("Publicado em", 17), ("Papel", 8), ("O que a empresa comunicou", 52),
                   ("Pregão seguinte", 14), ("Sacolejo", 10), ("Volume", 10),
                   ("Direção", 10), ("Variação", 11)], r)
    r += 1
    for _, x in p4.iterrows():
        cor = VERM if x["Direcao"] == "CAIU" else VERDE
        linha(ws, r, [str(x["Entrega"])[:16], x["Ticker"], str(x["Assunto"])[:150],
                      str(x["Pregao_reacao"])[:10],
                      f"{x['Volatilidade_vs_semana']:.1f}x",
                      f"{x['Volume_vs_semana']:.1f}x", x["Direcao"],
                      f"{x['Variacao_pct']:+.1f}%"], cor, False, 30)
        r += 1
    ws.freeze_panes = "A5"

    # ═════════════════════════════════════════════════ ABA 6 — GLOSSÁRIO ═════
    ws = wb.create_sheet("Glossário")
    titulo(ws, "OS TERMOS, EM LINGUAGEM COMUM", 3)
    r = 4
    cabecalho(ws, [("Termo", 26), ("O que é", 62), ("A analogia", 56)], r)
    r += 1
    for t, o, an in [
        ("Fato Relevante",
         "documento que a empresa é obrigada por lei a publicar quando acontece algo "
         "capaz de mexer no preço da ação",
         "é o aviso oficial no cartório do mercado"),
        ("Volatilidade / sacolejo",
         "o tamanho do balanço do preço, sem olhar para que lado",
         "perguntar se o mar estava agitado, e não para onde o barco foi"),
        ("Volume",
         "quantas ações trocaram de mão no dia",
         "a lotação do estádio: o placar pode empatar, mas se foi muita gente, "
         "algo importante estava em jogo"),
        ("Salto da abertura (gap)",
         "a diferença entre o preço de abertura e o fechamento do dia anterior",
         "o que mudou enquanto os portões estavam fechados"),
        ("Palpite fixo / classe majoritária",
         "quem não lê nada e sempre chuta o mesmo lado",
         "o adversário honesto: se ele acerta 57%, um modelo que acerte 54% não serve"),
        ("Valor-p",
         "a chance de o resultado ser pura sorte; abaixo de 0,05 conta, acima não",
         "jogar a moeda 10 vezes e dar 7 caras não prova nada; 10 mil vezes e 7 mil, sim"),
        ("kappa e MCC",
         "medem concordância além do que o acaso explicaria; 0 = acaso, 1 = perfeito",
         "descontar do acerto a parte que qualquer chute já daria"),
        ("Efeito de cauda",
         "o efeito médio não vem de todos os casos um pouco, vem de poucos casos com "
         "muita força",
         "a renda média de um bairro pode subir por causa de dois milionários"),
        ("FinBERT-PT-BR",
         "programa que leu 1,4 milhão de textos financeiros em português e aprendeu a "
         "dizer se um texto é positivo, negativo ou neutro",
         "um leitor treinado que devolve uma palavra sobre o tom"),
        ("Grupo de controle",
         "os 110 mil pregões em que NÃO houve comunicado nenhum",
         "o grupo que toma o remédio de mentira, para saber se o remédio de verdade "
         "faz alguma coisa"),
    ]:
        linha(ws, r, [t, o, an], None, False, 34)
        ws.cell(row=r, column=1).font = Font(size=10, bold=True)
        r += 1

    wb.save(SAIDA)
    print(f"[OK] {SAIDA}")
    print(f"     abas: {', '.join(wb.sheetnames)}")


if __name__ == "__main__":
    main()
