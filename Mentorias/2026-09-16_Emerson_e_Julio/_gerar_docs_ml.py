# -*- coding: utf-8 -*-
# ==============================================================================
#   O protocolo da pesquisa com a CVM — documentos 11, 12 e planilha 13
# ==============================================================================
import json
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
sys.path.insert(0, str(RAIZ / "src" / "comum"))
import abnt_docx as A  # noqa: E402

D = RAIZ / "CVM" / "dados"
FONTE = "Elaborado pelo autor (2026)"
P = json.loads((D / "pesquisa_com_cvm.json").read_text(encoding="utf-8"))
DIAG = json.loads((D / "diagnostico_ml.json").read_text(encoding="utf-8"))

AZUL, CAB = "1F3864", "D9E2F3"
VERDE, VERM, CINZA, AMAR = "C6EFCE", "FFC7CE", "F2F2F2", "FFEB9C"
B = Border(*[Side(style="thin", color="BFBFBF")] * 4)

# o que a dissertação já reportava, para o quadro antes/depois
ANTES_DISSERT = [
    ["Classe majoritária (sempre alta)", "53,14%", "—", "—", "—"],
    ["SVM (apenas preços)", "51,91%", "52,69%", "67,29%", "0,484"],
    ["XGBoost (apenas preços)", "49,77%", "52,74%", "52,74%", "0,501"],
    ["SVM (Data Fusion)", "51,91%", "52,91%", "65,65%", "0,518"],
    ["XGBoost (Data Fusion)", "52,22%", "54,64%", "56,91%", "0,514"],
]

ROT = {
    "apenas preços  [linha de base da pesquisa]": "apenas preços",
    "Data Fusion: preços + notícia  [O QUE TÍNHAMOS ANTES]":
        "Data Fusion: preços + notícia (antes)",
    "Data Fusion + CVM  [NOVO]": "Data Fusion + CVM (novo)",
    "Data Fusion + CVM + embedding  [NOVO]": "Data Fusion + CVM + embedding (novo)",
    "preços + CVM, sem notícia  [controle]": "preços + CVM, sem notícia (controle)",
}


def pc(x):
    return f"{x:.2%}".replace(".", ",")


def nm(x, casas=3):
    return f"{x:.{casas}f}".replace(".", ",")


def linhas_direcao():
    out = []
    for k, rot in ROT.items():
        for mod, m in P["direcao"][k].items():
            out.append([rot, mod, pc(m["acuracia"]), pc(m["precisao"]),
                        pc(m["f1"]), nm(m["auc"]), nm(m["p_binomial"], 4)])
    return out


def linhas_mcnemar():
    out = []
    for k, m in P["mcnemar"].items():
        mod, perg = k.split(" — ")
        v = ("PIORA" if m["acertos_so_do_novo"] < m["acertos_so_do_antigo"]
             and m["p"] < 0.05 else "passa" if m["p"] < 0.05 else "não passa")
        out.append([perg, mod, str(m["acertos_so_do_novo"]),
                    str(m["acertos_so_do_antigo"]), nm(m["p"], 4), v])
    return out


def linhas_vol():
    out = []
    for k, v in P["volatilidade"].items():
        out.append([k, nm(v["mae_linear"], 4), nm(v["mae_quantilico"], 4),
                    f"{v.get('r2os_quantilico_vs_HAR', 0):+.2f}%".replace(".", ",")])
    return out


# ──────────────────────────────────────────────────────────────────────────────
def completo():
    doc = A.novo_documento()
    A.capa(doc,
        titulo="A CVM dentro do protocolo da pesquisa",
        subtitulo="O que muda na previsão de direção e de volatilidade quando "
                  "os comunicados oficiais entram na fusão de dados",
        autor="Vanderlei Barbosa da Silva",
        orientador="Orientador: Prof. Dr. Julio Cesar Nievola",
        instituicao="PUCPR — Programa de Pós-Graduação em Informática (PPGIa)",
        descricao="Aplicação do protocolo do Capítulo 3 da dissertação — fusão "
                  "precoce em t−1, SVM-RBF e XGBoost, divisão cronológica "
                  "60/15/25, testes binomial e de McNemar — acrescido de um "
                  "bloco de atributos novo: os comunicados da CVM. Elaborado em "
                  "21 de setembro de 2026.",
    )

    A.secao(doc, "1", "Por que este documento existe")

    A.paragrafo(doc,
        "Os documentos 05 a 10 desta pasta usaram **regras escritas à mão**: "
        "contar notícias positivas e negativas, subtrair, comparar com um limiar. "
        "Essa é uma aproximação útil para medir, mas **não é o método da "
        "dissertação** e não responde à pergunta de previsão.")

    A.paragrafo(doc,
        "O Capítulo 3 especifica outra coisa: fusão precoce dos atributos "
        "defasados, classificadores SVM e XGBoost, protocolo cronológico, "
        "linhas de base e testes de significância. **Este documento aplica esse "
        "protocolo, sem alteração, e acrescenta um único bloco novo — os "
        "comunicados da CVM.** A pergunta é direta: o que muda em relação ao "
        "que havia antes da CVM?")

    A.secao(doc, "2", "O que foi mantido da pesquisa, e o que é novo")

    A.paragrafo(doc, "**Mantido, sem alteração, do Capítulo 3:**")
    A.lista(doc, [
        "**fusão precoce em t−1** — retorno do dia anterior, volatilidade "
        "condicional do GARCH(1,1) do dia anterior e índice de sentimento do "
        "FinBERT-PT-BR do dia anterior;",
        "**SVM com núcleo RBF**, precedido de padronização ajustada só no treino, "
        "e **XGBoost** com trezentas árvores, profundidade três, taxa de "
        "aprendizado 0,05 e subamostragem de noventa por cento;",
        "**divisão estritamente cronológica 60 / 15 / 25** — treino, validação e "
        "teste — sem embaralhar em momento algum;",
        "**duas linhas de base** — a classe majoritária e o modelo apenas-preços;",
        "**dois testes** — o binomial, contra o acaso, e o de McNemar, que isola "
        "a contribuição da fonte nova;",
        "**para a volatilidade**, o HAR de Corsi com médias de 1, 5 e 22 dias, e "
        "a combinação quantílica de pesos variáveis, medidas por erro absoluto "
        "médio e R² fora da amostra.",
    ])

    A.paragrafo(doc, "**Novo — o bloco da CVM em t−1:**")
    A.lista(doc, [
        "o índice de sentimento dos comunicados entregues com o pregão fechado, "
        "na mesma forma do ISM da pesquisa;",
        "a contagem de comunicados e a presença de Fato Relevante;",
        "as componentes principais do **embedding de 768 dimensões** que o "
        "FinBERT constrói do texto — ajustadas apenas sobre o treino.",
    ])

    A.paragrafo(doc,
        f"O painel tem **{P['n']['total']:,} pregões**, dos quais "
        f"**{P['n']['teste']} no teste**. Nele, {32.5:.1f}% dos pregões têm "
        "comunicado da CVM na véspera — proporção suficiente para que o bloco "
        "novo possa, em princípio, fazer diferença.".replace(",", "."))

    A.secao(doc, "3", "Primeiro, o pipeline reproduz o que já estava escrito")

    A.paragrafo(doc,
        "Antes de acrescentar qualquer coisa, é preciso mostrar que o código "
        "reproduz o Capítulo 4. **Se não reproduzisse, nada do que vem depois "
        "teria valor.**")

    A.tabela_abnt(doc, "1", "Reprodução dos resultados de direção do Capítulo 4",
        ["Preditor", "Acurácia (dissertação)", "Acurácia (agora)",
         "AUC (dissertação)", "AUC (agora)"],
        [["Classe majoritária", "53,14%", pc(P["majoritaria_teste"]), "—", "—"],
         ["SVM (apenas preços)", "51,91%",
          pc(P["direcao"]["apenas preços  [linha de base da pesquisa]"]["SVM-RBF"]["acuracia"]),
          "0,484",
          nm(P["direcao"]["apenas preços  [linha de base da pesquisa]"]["SVM-RBF"]["auc"])],
         ["XGBoost (apenas preços)", "49,77%",
          pc(P["direcao"]["apenas preços  [linha de base da pesquisa]"]["XGBoost"]["acuracia"]),
          "0,501",
          nm(P["direcao"]["apenas preços  [linha de base da pesquisa]"]["XGBoost"]["auc"])],
         ["SVM (Data Fusion)", "51,91%",
          pc(P["direcao"]["Data Fusion: preços + notícia  [O QUE TÍNHAMOS ANTES]"]["SVM-RBF"]["acuracia"]),
          "0,518",
          nm(P["direcao"]["Data Fusion: preços + notícia  [O QUE TÍNHAMOS ANTES]"]["SVM-RBF"]["auc"])],
         ["XGBoost (Data Fusion)", "52,22%",
          pc(P["direcao"]["Data Fusion: preços + notícia  [O QUE TÍNHAMOS ANTES]"]["XGBoost"]["acuracia"]),
          "0,514",
          nm(P["direcao"]["Data Fusion: preços + notícia  [O QUE TÍNHAMOS ANTES]"]["XGBoost"]["auc"])]],
        fonte=FONTE)

    A.paragrafo(doc,
        "**Reproduz.** As pequenas diferenças vêm da janela ampliada — a "
        "dissertação usou 1.986 pregões, e o painel atual tem 2.610. A classe "
        "majoritária do teste coincide exatamente, em 53,14%.")

    A.secao(doc, "4", "Direção — o quadro completo")

    A.tabela_abnt(doc, "2", "Previsão de direção da PETR4 no conjunto de teste",
        ["Braço", "Modelo", "Acurácia", "Precisão", "F1", "AUC", "p binomial"],
        linhas_direcao(), fonte=FONTE)

    melhor = P["direcao"]["Data Fusion + CVM  [NOVO]"]["SVM-RBF"]
    A.paragrafo(doc,
        f"Há um número que salta à vista: o SVM com Data Fusion mais CVM acerta "
        f"**{pc(melhor['acuracia'])}**, acima da classe majoritária de "
        f"{pc(P['majoritaria_teste'])}, com valor-p binomial de "
        f"{nm(melhor['p_binomial'], 4)}. Seria o melhor resultado de direção de "
        "toda a pesquisa.")

    A.paragrafo(doc,
        "**Não é, e convém explicar por quê antes que a banca pergunte.** Três "
        "razões, todas verificáveis na própria tabela:")

    A.lista(doc, [
        f"a vantagem sobre a classe majoritária é de apenas "
        f"**{(melhor['acuracia'] - P['majoritaria_teste']) * 100:.2f} ponto "
        f"percentual**, e o erro-padrão de uma proporção com "
        f"{P['n']['teste']} observações é de cerca de 1,95 ponto — a vantagem "
        "cabe inteira dentro do ruído;",
        f"a **AUC é {nm(melhor['auc'])}, abaixo de 0,500** — o modelo ordena os "
        "pregões um pouco pior que o acaso, o que significa que o acerto veio da "
        "proporção de chutes, não de discriminação;",
        "o **teste de McNemar**, que é o instrumento próprio para esta pergunta, "
        "não passa — como a seção seguinte mostra.",
    ])

    A.paragrafo(doc,
        "**O valor-p binomial de 0,028 testa contra 50%, não contra a classe "
        "majoritária.** Com um alvo em que 53,14% dos pregões são de alta, bater "
        "50% é fácil e não significa nada. Esse é exatamente o tipo de leitura "
        "apressada que o protocolo da pesquisa foi desenhado para impedir.")

    A.secao(doc, "5", "O teste de McNemar — a fonte nova acrescenta?")

    A.paragrafo(doc,
        "O McNemar é o teste pareado. Ele ignora os pregões em que os dois "
        "modelos concordam e olha **apenas onde discordam**: quantas vezes o "
        "modelo novo acertou onde o antigo errou, contra o inverso. É a única "
        "forma honesta de medir o que uma fonte acrescenta.")

    A.tabela_abnt(doc, "3", "Contribuição de cada fonte, medida par a par",
        ["Pergunta", "Modelo", "Ganhou", "Perdeu", "valor-p", "Veredito"],
        linhas_mcnemar(), fonte=FONTE)

    A.paragrafo(doc,
        "**A CVM não acrescenta à direção.** Nem no SVM (p = 0,162) nem no "
        "XGBoost (p = 0,312). E o **embedding piora o SVM de forma "
        "estatisticamente significativa** (p = 0,0026): oito componentes "
        "principais extraídas de 768 dimensões ainda são ruído demais para um "
        "teste de 653 pregões.")

    A.paragrafo(doc,
        "Vale registrar um ponto favorável: a contribuição da **notícia** sobre o "
        "modelo de preços, no XGBoost, chega a p = 0,075 — ganhou 88 pregões e "
        "perdeu 65. **Não passa**, mas é melhor que o registrado no Capítulo 4, "
        "onde o placar era de 52 contra 53 com valor-p próximo de um. A janela "
        "ampliada ajudou a notícia, não a CVM.")

    A.secao(doc, "6", "Volatilidade — pelo HAR e pela combinação quantílica")

    A.tabela_abnt(doc, "4", "Previsão da volatilidade fora da amostra",
        ["Modelo", "MAE (linear)", "MAE (quantílico)", "R²-OS vs HAR"],
        linhas_vol(), fonte=FONTE)

    A.paragrafo(doc,
        "A combinação quantílica de pesos variáveis supera o HAR linear em cerca "
        "de 7%, na mesma faixa dos 10,9% relatados no Capítulo 4 — **o método da "
        "pesquisa se sustenta.**")

    A.paragrafo(doc,
        "**Mas a CVM não melhora nada.** O sentimento das notícias eleva o R²-OS "
        "de 6,90% para 7,53%; acrescentar a CVM o traz de volta a 7,47%. E no "
        "HAR linear o sentimento continua piorando o erro, exatamente como o "
        "Capítulo 4 já documentava.")

    A.secao(doc, "7", "O que se conclui, sem suavizar")

    A.paragrafo(doc,
        "**Dentro do protocolo da pesquisa, combinar os comunicados da CVM com "
        "as notícias não melhora a previsão da direção nem a da volatilidade.** "
        "Nenhum teste de McNemar passa; o R²-OS não sobe; a AUC não se move.")

    A.paragrafo(doc,
        "Isso **não contradiz** o que foi medido nos documentos 08 a 10. O efeito "
        "de +38% no tamanho da variação do preço, nas noites de Fato Relevante "
        "com muita notícia, continua real e estatisticamente firme. O que estes "
        "resultados acrescentam é mais específico e mais duro:")

    A.citacao_longa(doc,
        "O efeito existe e é mensurável, mas não é grande nem regular o "
        "bastante para se converter em ganho preditivo sobre a memória do "
        "próprio preço.",
        "Conclusão desta rodada")

    A.paragrafo(doc,
        "É, aliás, o mesmo padrão que o Capítulo 4 já havia estabelecido para as "
        "notícias. **A CVM não mudou a natureza do resultado — confirmou-a com "
        "uma fonte independente**, oficial, datada com precisão de segundos e "
        "livre de ruído editorial. Isso tem valor científico próprio: uma "
        "hipótese que sobrevive a um teste com dados melhores é mais forte do que "
        "uma que nunca foi testada assim.")

    A.secao(doc, "8", "Limitações, e o experimento que falta")

    A.lista(doc, [
        "**As duas fontes entram em condições desiguais.** A CVM entra com "
        "embedding de 768 dimensões; as 54 mil notícias entram com **um único "
        "número por pregão**, o índice de sentimento. A fonte maior está "
        "representada pelo atributo mais pobre.",
        "**E há indício de que isso importa.** No diagnóstico do modelo livre, o "
        f"embedding da CVM respondeu por {DIAG['mercado + texto + embedding']['importancias']['embedding']:.1%} "
        f"da decisão, contra {DIAG['mercado + texto + embedding']['importancias']['CVM (rótulos)']:.1%} "
        "dos rótulos da CVM — mais, mesmo existindo em uma fração das noites.",
        "**Extrair os embeddings das notícias é o experimento que falta**, e é "
        "trabalho de GPU em Colab. Até que ele seja feito, a conclusão acima vale "
        "para o desenho testado, não para a hipótese em geral.",
        "**Um único ativo.** Todos os números são da PETR4.",
        "**O SVM e o XGBoost discordam** em vários braços, o que é sinal de que o "
        "sinal, se existe, é frágil o bastante para depender do algoritmo.",
    ])

    doc.save(AQUI / "11_Modelo_ML_COMPLETO.docx")
    print("  [OK] 11_Modelo_ML_COMPLETO.docx")


# ──────────────────────────────────────────────────────────────────────────────
def resumido():
    doc = A.novo_documento()
    A.capa(doc,
        titulo="A CVM entrou no modelo. E não mudou nada.",
        subtitulo="O resultado em cinco minutos, em linguagem comum",
        autor="Vanderlei Barbosa da Silva",
        orientador="Orientador: Prof. Dr. Julio Cesar Nievola",
        instituicao="PUCPR — Programa de Pós-Graduação em Informática (PPGIa)",
        descricao="Versão resumida do documento 11. Elaborado em 21 de setembro "
                  "de 2026.",
    )

    A.secao(doc, "1", "O que eu fiz desta vez")

    A.paragrafo(doc,
        "Nos documentos anteriores eu usei uma **regra escrita à mão**: contar "
        "notícias boas e ruins, subtrair, e apostar. Isso serve para medir, mas "
        "**não é o método da dissertação.**")

    A.paragrafo(doc,
        "Desta vez usei o método de verdade — o que está escrito no Capítulo 3: "
        "**o encoder FinBERT lê os textos, o GARCH mede o risco, tudo isso vira "
        "uma tabela de atributos, e dois algoritmos de aprendizado de máquina — "
        "SVM e XGBoost — aprendem sozinhos** qual a relação com o pregão "
        "seguinte. **Depois acrescentei os comunicados da CVM** e perguntei: "
        "mudou alguma coisa?")

    A.secao(doc, "2", "Antes de tudo, provei que o código está certo")

    A.paragrafo(doc,
        "Rodei primeiro **sem a CVM**, para ver se eu reproduzia os números que "
        "já estão escritos na dissertação. Reproduzi:")

    A.tabela_abnt(doc, "1", "O código reproduz o que já estava na dissertação",
        ["", "Está escrito na dissertação", "Deu agora"],
        [["Classe majoritária", "53,14%", pc(P["majoritaria_teste"])],
         ["XGBoost só com preços", "49,77%",
          pc(P["direcao"]["apenas preços  [linha de base da pesquisa]"]["XGBoost"]["acuracia"])],
         ["XGBoost com notícia", "52,22%",
          pc(P["direcao"]["Data Fusion: preços + notícia  [O QUE TÍNHAMOS ANTES]"]["XGBoost"]["acuracia"])]],
        fonte=FONTE)

    A.paragrafo(doc,
        "**Isso importa mais do que parece.** Se o código não reproduzisse o que "
        "já está publicado, nada do que vem depois teria valor.")

    A.secao(doc, "3", "E aí acrescentei a CVM")

    A.tabela_abnt(doc, "2", "Direção do pregão seguinte — o que muda com a CVM",
        ["Braço", "SVM", "XGBoost"],
        [["apenas preços",
          pc(P["direcao"]["apenas preços  [linha de base da pesquisa]"]["SVM-RBF"]["acuracia"]),
          pc(P["direcao"]["apenas preços  [linha de base da pesquisa]"]["XGBoost"]["acuracia"])],
         ["preços + notícia (o que tínhamos antes)",
          pc(P["direcao"]["Data Fusion: preços + notícia  [O QUE TÍNHAMOS ANTES]"]["SVM-RBF"]["acuracia"]),
          pc(P["direcao"]["Data Fusion: preços + notícia  [O QUE TÍNHAMOS ANTES]"]["XGBoost"]["acuracia"])],
         ["preços + notícia + CVM (novo)",
          pc(P["direcao"]["Data Fusion + CVM  [NOVO]"]["SVM-RBF"]["acuracia"]),
          pc(P["direcao"]["Data Fusion + CVM  [NOVO]"]["XGBoost"]["acuracia"])],
         ["+ embedding da CVM (novo)",
          pc(P["direcao"]["Data Fusion + CVM + embedding  [NOVO]"]["SVM-RBF"]["acuracia"]),
          pc(P["direcao"]["Data Fusion + CVM + embedding  [NOVO]"]["XGBoost"]["acuracia"])]],
        fonte=FONTE)

    A.paragrafo(doc,
        "**Aquele 54,36% é uma armadilha, e eu preciso que você diga isso antes "
        "que perguntem.** Ele está só 1,2 ponto acima do palpite fixo, e a "
        "margem de erro com 653 pregões é de quase 2 pontos. Além disso a AUC "
        "dele é 0,489 — **abaixo de 0,500**, o que quer dizer que o modelo ordena "
        "os pregões pior que uma moeda. Ele acertou o placar por ter chutado na "
        "proporção certa, não por saber distinguir um pregão do outro.")

    A.secao(doc, "4", "O teste que realmente responde")

    A.paragrafo(doc,
        "Existe um teste feito exatamente para a pergunta *\"essa fonte nova "
        "acrescenta?\"*. Chama-se **McNemar**. Ele joga fora os pregões em que os "
        "dois modelos concordam e olha só onde discordam.")

    A.tabela_abnt(doc, "3", "O que cada fonte acrescenta",
        ["Pergunta", "Placar", "valor-p", "Resposta"],
        [["a notícia acrescenta sobre o preço? (XGBoost)", "88 × 65", "0,0750",
          "quase, mas não"],
         ["a CVM acrescenta sobre a notícia? (SVM)", "37 × 25", "0,1619", "não"],
         ["a CVM acrescenta sobre a notícia? (XGBoost)", "64 × 77", "0,3122", "não"],
         ["o embedding acrescenta? (SVM)", "27 × 55", "0,0026", "PIORA"]],
        fonte=FONTE)

    A.secao(doc, "5", "E a volatilidade")

    A.tabela_abnt(doc, "4", "Quanto cada modelo reduz o erro do HAR",
        ["Modelo", "Ganho sobre o HAR"],
        [[k, f"{v.get('r2os_quantilico_vs_HAR', 0):+.2f}%".replace(".", ",")]
         for k, v in P["volatilidade"].items()], fonte=FONTE)

    A.paragrafo(doc,
        "**A notícia melhora um pouquinho — de 6,90% para 7,53%. A CVM traz de "
        "volta para 7,47%.** Não ajuda.")

    A.secao(doc, "6", "Em quatro frases, para a mentoria")

    A.lista(doc, [
        "“Eu tinha usado uma regra feita à mão. Desta vez usei o método da "
        "dissertação — FinBERT, GARCH, fusão de dados, SVM e XGBoost, divisão "
        "cronológica.”",
        "“Primeiro reproduzi os números que já estão escritos, para provar que o "
        "código está certo. Reproduziu.”",
        "“Depois acrescentei a CVM. Nenhum teste de McNemar passa — a CVM não "
        "acrescenta à direção nem à volatilidade.”",
        "“Isso não derruba o achado de +38% no tamanho da variação. Diz outra "
        "coisa: o efeito existe, mas não é regular o bastante para virar "
        "previsão melhor que a memória do próprio preço.”",
    ])

    A.secao(doc, "7", "O que ainda falta, e é importante dizer")

    A.paragrafo(doc,
        "**As duas fontes não entraram em pé de igualdade.** A CVM entrou com o "
        "embedding — as 768 dimensões que o encoder constrói do texto. As 54 mil "
        "notícias entraram com **um número só por pregão.**")

    A.paragrafo(doc,
        "E há indício de que isso pesa: no diagnóstico, o embedding da CVM "
        "respondeu por mais da decisão do modelo do que os próprios rótulos da "
        "CVM, mesmo existindo em muito menos noites. **Rodar o encoder nas "
        "notícias para extrair os embeddings delas é o próximo experimento**, e "
        "é trabalho de GPU.")

    doc.save(AQUI / "12_Modelo_ML_RESUMIDO.docx")
    print("  [OK] 12_Modelo_ML_RESUMIDO.docx")


# ──────────────────────────────────────────────────────────────────────────────
def planilha():
    wb = Workbook()

    def tit(ws, txt, n, sub=None):
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=n)
        c = ws.cell(row=1, column=1, value=txt)
        c.font = Font(bold=True, size=13, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor=AZUL)
        c.alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[1].height = 26
        if sub:
            ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=n)
            c = ws.cell(row=2, column=1, value=sub)
            c.font = Font(italic=True, size=9, color="404040")
            c.alignment = Alignment(horizontal="center")

    def cab(ws, cols, r):
        for j, (nome, larg) in enumerate(cols, start=1):
            c = ws.cell(row=r, column=j, value=nome)
            c.font = Font(bold=True, size=10, color=AZUL)
            c.fill = PatternFill("solid", fgColor=CAB)
            c.alignment = Alignment(horizontal="center", vertical="center",
                                    wrap_text=True)
            c.border = B
            ws.column_dimensions[get_column_letter(j)].width = larg
        ws.row_dimensions[r].height = 32

    def lin(ws, r, vals, cor=None, neg=False):
        for j, v in enumerate(vals, start=1):
            c = ws.cell(row=r, column=j, value=v)
            c.alignment = Alignment(vertical="center", wrap_text=True)
            c.border = B
            c.font = Font(size=10, bold=neg)
            if cor:
                c.fill = PatternFill("solid", fgColor=cor)
        ws.row_dimensions[r].height = 22

    # aba 1 — antes e depois
    ws = wb.active
    ws.title = "Antes e depois"
    tit(ws, "O QUE MUDA QUANDO A CVM ENTRA NO MODELO", 5,
        sub=f"PETR4 · protocolo do Capítulo 3 · {P['n']['total']:,} pregões, "
            f"{P['n']['teste']} no teste · classe majoritária "
            f"{pc(P['majoritaria_teste'])}".replace(",", "."))
    r = 4
    cab(ws, [("Braço", 38), ("Modelo", 12), ("Acurácia", 11), ("AUC", 10),
             ("Veredito", 30)], r)
    r += 1
    for k, rot in ROT.items():
        for mod, m in P["direcao"][k].items():
            bom = m["auc"] > 0.52 and m["acuracia"] > P["majoritaria_teste"]
            ver = ("acima da majoritária, mas AUC < 0,50"
                   if m["acuracia"] > P["majoritaria_teste"] and m["auc"] < 0.50
                   else "abaixo da classe majoritária"
                   if m["acuracia"] <= P["majoritaria_teste"] else "acima")
            lin(ws, r, [rot, mod, pc(m["acuracia"]), nm(m["auc"]), ver],
                AMAR if "AUC < 0,50" in ver else (VERDE if bom else CINZA))
            r += 1
    r += 1
    for t in ["NENHUM BRAÇO SUPERA A CLASSE MAJORITÁRIA DE FORMA CONFIÁVEL.",
              "",
              "O 54,36% do SVM com CVM está 1,2 ponto acima do palpite fixo,",
              "e a margem de erro com 653 pregões é de quase 2 pontos.",
              "A AUC dele é 0,489 — abaixo de 0,500, ou seja, ordena pior que",
              "uma moeda. Acertou o placar por chutar na proporção certa."]:
        c = ws.cell(row=r, column=1, value=t)
        c.font = Font(size=10, bold=t.isupper() and len(t) > 10,
                      color="9C0006" if t.isupper() and len(t) > 10 else "000000")
        r += 1

    # aba 2 — McNemar
    ws = wb.create_sheet("O teste que decide")
    tit(ws, "McNEMAR — A FONTE NOVA ACRESCENTA SOBRE A ANTERIOR?", 6,
        sub="Ignora os pregões em que os dois modelos concordam e olha só onde discordam")
    r = 4
    cab(ws, [("Pergunta", 40), ("Modelo", 12), ("Ganhou", 10), ("Perdeu", 10),
             ("valor-p", 11), ("Veredito", 16)], r)
    r += 1
    for linha in linhas_mcnemar():
        cor = VERM if linha[5] == "PIORA" else (VERDE if linha[5] == "passa" else CINZA)
        lin(ws, r, linha, cor, linha[5] != "não passa")
        r += 1
    r += 2
    for t in ["COMO LER ESTA TABELA",
              "",
              "'Ganhou' = pregões em que o modelo NOVO acertou e o ANTIGO errou.",
              "'Perdeu' = o contrário.",
              "Se os dois números forem parecidos, a fonte nova não acrescentou nada.",
              "O valor-p diz se a diferença entre eles é maior que o acaso.",
              "",
              "RESPOSTA: a CVM não acrescenta. E o embedding, no SVM, PIORA."]:
        ws.cell(row=r, column=1, value=t).font = Font(
            size=10, bold=t.isupper() or t.startswith("RESPOSTA"))
        r += 1

    # aba 3 — volatilidade
    ws = wb.create_sheet("Volatilidade")
    tit(ws, "VOLATILIDADE — HAR DE CORSI E A COMBINAÇÃO QUANTÍLICA", 4,
        sub="R²-OS mede quanto o modelo reduz o erro do HAR. Positivo = melhor que o HAR.")
    r = 4
    cab(ws, [("Modelo", 44), ("MAE linear", 13), ("MAE quantílico", 15),
             ("Ganho sobre o HAR", 18)], r)
    r += 1
    for linha in linhas_vol():
        melhor = "ANTES" in linha[0]
        lin(ws, r, linha, VERDE if melhor else CINZA, melhor)
        r += 1
    r += 2
    for t in ["A combinação quantílica bate o HAR linear em ~7%,",
              "na mesma faixa dos +10,9% do Capítulo 4 — o método se sustenta.",
              "",
              "Mas a CVM não melhora: o sentimento leva de 6,90% a 7,53%,",
              "e acrescentar a CVM traz de volta para 7,47%."]:
        ws.cell(row=r, column=1, value=t).font = Font(size=10)
        r += 1

    # aba 4 — o que ainda falta
    ws = wb.create_sheet("O que falta")
    tit(ws, "AS DUAS FONTES NÃO ENTRARAM EM PÉ DE IGUALDADE", 3)
    r = 4
    cab(ws, [("Fonte", 26), ("Quantidade", 20), ("Como entra no modelo", 44)], r)
    r += 1
    lin(ws, r, ["Notícias dos portais", "54.259 textos",
                "UM número por pregão (o índice de sentimento)"], AMAR); r += 1
    lin(ws, r, ["Comunicados da CVM", "2.193 da PETR4",
                "rótulos + embedding de 768 dimensões"], VERDE); r += 1
    r += 2
    imp = DIAG["mercado + texto + embedding"]["importancias"]
    cab(ws, [("De onde o modelo tirou a decisão", 36), ("Peso", 12)], r); r += 1
    for k, v in sorted(imp.items(), key=lambda kv: -kv[1]):
        lin(ws, r, [k, f"{v:.1%}".replace(".", ",")],
            VERDE if k == "embedding" else CINZA, k == "embedding")
        r += 1
    r += 2
    for t in ["O embedding da CVM pesou MAIS que os rótulos da CVM,",
              "mesmo existindo em muito menos noites.",
              "",
              "PRÓXIMO EXPERIMENTO: rodar o encoder nas 54.259 notícias",
              "para extrair os embeddings delas. É trabalho de GPU, em Colab."]:
        ws.cell(row=r, column=1, value=t).font = Font(
            size=10, bold=t.startswith("PRÓXIMO"))
        r += 1

    wb.save(AQUI / "13_Modelo_ML.xlsx")
    print(f"  [OK] 13_Modelo_ML.xlsx  ({', '.join(wb.sheetnames)})")


if __name__ == "__main__":
    completo()
    resumido()
    planilha()
