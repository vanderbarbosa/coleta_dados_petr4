# -*- coding: utf-8 -*-
# ==============================================================================
#   Resultados das Rodadas A e B — para a reunião com os orientadores
#   Saída: CVM/03_RESULTADOS_A_E_B.docx
# ==============================================================================
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(RAIZ / "src" / "comum"))

import abnt_docx as A  # noqa: E402

FONTE = "Elaborado pelo autor (2026)"
SAIDA = AQUI / "03_RESULTADOS_A_E_B.docx"


def main() -> None:
    doc = A.novo_documento()

    A.capa(
        doc,
        titulo="A notícia da noite e o pregão seguinte",
        subtitulo="Resultado das duas rodadas: a classificação da CVM e a nossa, "
                  "confrontadas com o que o preço fez de fato",
        autor="Vanderlei Barbosa da Silva",
        orientador="Orientador: Prof. Dr. Julio Cesar Nievola",
        instituicao="PUCPR — Programa de Pós-Graduação em Informática (PPGIa)",
        descricao="Execução do experimento pedido pelos orientadores: engenharia "
                  "reversa sobre comunicados divulgados após o fechamento do pregão, "
                  "observando o pregão seguinte. Inclui a medida de volatilidade "
                  "relativa à semana anterior sugerida pelo Prof. Emerson Paraiso, e "
                  "o grupo de controle que corrigiu dois números. Elaborado em 17 de "
                  "setembro de 2026.",
    )

    # ── 1 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "1", "O experimento, em um parágrafo")

    A.paragrafo(doc,
        "Foram isolados **3.435 comunicados entregues à CVM depois que o mercado "
        "fechou**, entre 2018 e 2026, em 57 papéis da B3. Para cada um, observou-se o "
        "**pregão seguinte** — o primeiro momento em que aquela informação pôde ser "
        "negociada. **A hora é oficial**, extraída do Protocolo de Entrega da CVM, com "
        "precisão de segundos.")

    A.paragrafo(doc,
        "Duas rodadas: a primeira usa **apenas o rótulo que já vem da CVM**; a segunda "
        "usa a **nossa classificação**, produzida pelo FinBERT-PT-BR sobre o texto do "
        "comunicado.")

    # ── 2 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "2", "O controle, que veio primeiro")

    A.paragrafo(doc,
        "**Antes de qualquer número, um aviso sobre método.** O Prof. Emerson sugeriu "
        "comparar a volatilidade do pregão seguinte com a **média dos dias anteriores** "
        "— uma semana — em vez de uma média distante. **A sugestão está certa e é mais "
        "exigente:** volatilidade é grudenta, e bater a média da própria semana anterior "
        "é bem mais difícil que bater uma média de cem dias atrás.")

    A.paragrafo(doc,
        "**Mas essa razão precisa de um piso, e o piso não é 1,00.** Medi em 110 mil "
        "pregões **sem comunicado nenhum**: a razão entre um dia qualquer e a média da "
        "semana anterior já dá **1,034** na volatilidade e **1,065** no volume, por pura "
        "assimetria da distribuição.")

    A.paragrafo(doc,
        "**Sem esse controle eu teria reportado 21,9% de excesso de volatilidade e "
        "44,6% de volume. Os valores corretos são 17,6% e 34,2%.**")

    # ── 3 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "3", "Rodada A — só com a classificação da CVM")

    A.tabela_abnt(doc, "1", "O pregão seguinte, comparado a um pregão sem comunicado",
        ["Medida", "Sem comunicado", "Com comunicado", "Excesso", "valor-p"],
        [
            ["Volatilidade (Parkinson)", "1,034", "1,216", "+17,6%", "4,5 × 10⁻⁵⁰"],
            ["VOLUME NEGOCIADO", "1,065", "1,429", "+34,2%", "1,0 × 10⁻⁵⁶"],
            ["Gap de abertura", "0,080%", "0,200%", "+0,12 p.p.", "0,007"],
            ["Intradiário", "−0,070%", "−0,170%", "−0,10 p.p.", "0,088"],
            ["Pregão inteiro (direção)", "0,010%", "0,030%", "+0,02 p.p.", "0,787"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**A resposta à pergunta dos senhores é sim: a publicação move o pregão "
        "seguinte** — e o efeito é enorme estatisticamente. **Mas move o RISCO, não a "
        "direção.**")

    A.paragrafo(doc,
        "**O volume é o sinal mais forte, quase o dobro da volatilidade.** Isso era "
        "previsto no plano que entreguei antes de rodar, e converge com Hashami e "
        "Maldonado (2025), que no petróleo viram a simples contagem de notícias superar "
        "todos os métodos de sentimento.")

    A.paragrafo(doc,
        "**A direção deu nula (p = 0,787), e tinha de dar.** O rótulo da CVM não "
        "distingue notícia boa de ruim — altas e baixas se cancelam. **É precisamente "
        "por isso que a Rodada B existe.**")

    A.secao(doc, "3.1", "A robustez à linha de base", nivel=2)

    A.tabela_abnt(doc, "2", "O efeito não depende de qual semana se escolhe",
        ["Linha de base", "Volatilidade", "Volume"],
        [
            ["1 semana (−6 a −2)", "1,219", "1,446"],
            ["2 semanas (−11 a −2)", "1,209", "1,426"],
            ["1 mês (−23 a −2)", "1,201", "1,421"],
            ["distante (−120 a −21)", "1,227", "1,491"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**Os dois pregões imediatamente anteriores foram deixados de fora de "
        "propósito.** Se houvesse vazamento de informação na véspera, incluí-la "
        "inflaria a linha de base e esconderia o efeito.")

    # ── 4 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "4", "Metade dos fatos relevantes não move nada")

    A.paragrafo(doc,
        "Traduzindo os 3.435 casos para linguagem comum:")

    A.tabela_abnt(doc, "3", "Veredicto caso a caso",
        ["O que aconteceu no pregão seguinte", "Casos", "Proporção"],
        [
            ["MEXEU MUITO (2× ou mais)", "688", "20,0%"],
            ["mexeu (1,3× ou mais)", "938", "27,3%"],
            ["dentro do normal", "1.304", "38,0%"],
            ["ficou MAIS PARADO que o normal", "490", "14,3%"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**47,3% mexeram; 52,3% ficaram no normal ou mais parados.** É o efeito de "
        "cauda dito sem estatística: **o fato relevante típico não faz nada; o efeito "
        "médio vem de uma minoria de eventos.**")

    A.secao(doc, "4.1", "Três casos, para ver de perto", nivel=2)

    A.lista(doc, [
        "**OIBR3, 07/11/2025 às 19h31** — *“Manifestação sobre a Continuidade do Grupo "
        "Oi”*. No pregão seguinte o preço **caiu 44,2%**, com volatilidade 4,9 vezes e "
        "volume 5,7 vezes a média da semana anterior.",
        "**OIBR3, 30/09/2025 às 23h08** — *“Decisão Judicial — Suspensão de Obrigações "
        "e Afastamento da Gestão”*. **Caiu 28,1%**, com volume **15,1 vezes** o normal.",
        "**CVCB3, 15/01/2026 às 20h51** — *“Plano de sucessão da Companhia”*. **Caiu "
        "11,4%.**",
    ])

    A.paragrafo(doc,
        "**A planilha `casos_concretos.csv` traz os 3.435, um por linha**, com empresa, "
        "data, hora, texto do comunicado, volatilidade, volume, direção e o tamanho do "
        "movimento. **É auditável na mão, caso a caso.**")

    # ── 5 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "5", "Rodada B — com a nossa classificação")

    A.paragrafo(doc,
        "O FinBERT-PT-BR leu os 20.421 textos. **A regra de acerto foi declarada antes "
        "de rodar:** positivo prevê alta, negativo prevê baixa, neutro não faz previsão "
        "e fica fora do cálculo.")

    A.tabela_abnt(doc, "4", "Acurácia direcional no pregão seguinte",
        ["Alvo", "Casos", "Acurácia", "Classe majoritária", "Ganho", "valor-p"],
        [
            ["Gap de abertura — todos", "780", "54,7%", "57,2%", "−2,44 p.p.", "0,009"],
            ["Gap — só atribuíveis", "636", "54,7%", "57,4%", "−2,67 p.p.", "0,019"],
            ["PREGÃO INTEIRO — todos", "780", "54,9%", "51,7%", "+3,21 p.p.", "0,007"],
            ["PREGÃO INTEIRO — atribuíveis", "636", "55,0%", "50,2%", "+4,87 p.p.", "0,012"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**Há uma distinção aqui que convém eu mesmo levantar, antes que perguntem.** "
        "Os valores-p comparam o acerto contra o **acaso**, isto é, contra 50%. Mas o "
        "adversário honesto não é o acaso — é a **classe majoritária**, a regra "
        "preguiçosa de sempre apostar no lado mais frequente.")

    A.paragrafo(doc,
        "**No gap de abertura, nós perdemos dessa regra preguiçosa.** O gap sobe em "
        "57,2% das vezes; quem sempre apostasse em alta acertaria mais que o nosso "
        "modelo. **Somos melhores que a moeda, e piores que o palpite trivial.**")

    A.paragrafo(doc,
        "**No pregão inteiro, ganhamos: +4,87 pontos percentuais** sobre a classe "
        "majoritária, com valor-p de 0,012. **E note a convergência: o resultado "
        "principal da dissertação, na PETR4 com manchetes de jornal, é de +4,4 pontos. "
        "Aqui, com comunicados oficiais em 57 papéis, dá +4,87.** Os dois caem dentro "
        "da faixa de 2 a 10 pontos relatada por Nguyen, Shirai e Velcin (2015).")

    A.secao(doc, "5.1", "Onde o sinal realmente mora", nivel=2)

    A.tabela_abnt(doc, "5", "Retorno médio do pregão seguinte, por classe",
        ["Nossa classificação", "Casos", "Volatilidade", "Volume", "Retorno médio"],
        [
            ["Positivo", "303", "1,153", "1,267", "+0,014%"],
            ["Neutro", "2.939", "1,223", "1,446", "+0,028%"],
            ["NEGATIVO", "477", "1,178", "1,350", "−0,353%"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**Esta é a tabela mais informativa da Rodada B.** O que o modelo chama de "
        "negativo é seguido de retorno de **−0,353%**, contra +0,014% do positivo e "
        "+0,028% do neutro. **O sinal existe, e mora quase todo na classe negativa.**")

    A.paragrafo(doc,
        "**E isso é coerente com tudo o que já sabíamos:** o classificador tem viés "
        "contra a classe positiva. Diante de 224 notícias que trinta casas de análise "
        "consideraram favoráveis à Petrobras, ele enxergou 21,9% de positivas contra os "
        "84,8% dos analistas. **Ele reconhece o ruim; não reconhece o bom.**")

    A.paragrafo(doc,
        "No corpus da CVM o padrão se repete de forma ainda mais extrema: de 20.421 "
        "textos, **79,2% saíram neutros**, 11,5% negativos e apenas 9,2% positivos. Na "
        "PETR4, entre 432 comunicados classificados, há **100 negativos e apenas 14 "
        "positivos**.")

    A.secao(doc, "5.2", "O índice contínuo", nivel=2)

    A.tabela_abnt(doc, "6", "Correlação entre o índice de sentimento e o retorno",
        ["Alvo", "Pearson", "valor-p", "Spearman", "valor-p"],
        [
            ["Gap de abertura", "+0,0528", "0,0013", "+0,0553", "0,0007"],
            ["Pregão inteiro", "+0,0296", "0,0708", "+0,0401", "0,0146"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**Os sinais estão todos na direção certa** — quanto melhor a notícia, maior o "
        "retorno — **e a correlação com o gap é significativa. Mas a magnitude é "
        "pequena:** 0,05 numa escala que vai até 1.")

    # ── 6 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "6", "A comparação entre as duas rodadas")

    A.tabela_abnt(doc, "7", "O que cada classificação consegue",
        ["", "Rodada A — CVM", "Rodada B — nossa"],
        [
            ["Volatilidade", "+17,6% (p ≈ 10⁻⁵⁰)", "não distingue as classes"],
            ["Volume", "+34,2% (p ≈ 10⁻⁵⁶)", "não distingue as classes"],
            ["Direção", "impossível — o rótulo não tem sinal",
             "+4,87 p.p. sobre a majoritária (p = 0,012)"],
            ["Onde é forte", "dizer QUE algo aconteceu", "dizer que algo RUIM aconteceu"],
            ["Onde é fraca", "não diz o lado", "não reconhece o que é bom"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**As duas se complementam, e nenhuma substitui a outra.** O rótulo da CVM é "
        "imbatível para dizer que houve informação relevante — e não custa nada, porque "
        "vem pronto. **A nossa classificação é a única capaz de apontar o lado**, e "
        "mesmo assim só de um lado: o ruim.")

    A.secao(doc, "6.1", "O sentimento acrescenta algo além da categoria?", nivel=2)

    A.paragrafo(doc,
        "Regressão com as duas variáveis juntas. Sobre o **tamanho do gap**, ser Fato "
        "Relevante pesa +0,0044 (p < 0,0001) e o índice de sentimento pesa −0,0043 "
        "(p < 0,0001). **Ambos significativos, e independentes um do outro** — o "
        "sentimento acrescenta informação que a categoria não carrega.")

    A.paragrafo(doc,
        "**Sobre a volatilidade, porém, o sentimento não acrescenta nada** (p = 0,85). "
        "Ali quem manda é a categoria.")

    # ── 7 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "7", "Limitações — ditas antes que perguntem")

    A.lista(doc, [
        "**O texto classificado é curto e burocrático.** São 47 caracteres em média — "
        "linhas de assunto, não prosa. E **26% se repetem**: “Notícia divulgada na "
        "mídia” aparece 397 vezes. **O classificador não tem como acertar num texto que "
        "não diz nada.** O documento completo em PDF existe e é o caminho natural para "
        "melhorar isso.",
        "**741 eventos (21,6%) têm mais de um comunicado na mesma noite.** O movimento "
        "não é atribuível a um documento específico. Todos os testes foram rodados "
        "também só com os 2.694 atribuíveis, e o resultado se manteve.",
        "**Faltam 4 papéis** — ELET3, EMBR3, AZUL4 e GOLL4 —, o que tira 14,8% dos "
        "eventos. Caíram por limite do provedor de cotações, não por erro de método.",
        "**A comparação Fato Relevante contra Comunicado ao Mercado ainda está "
        "incompleta**: a hora oficial dos Comunicados está sendo coletada e hoje cobre "
        "cerca de um terço.",
        "**“Causou” é palavra forte.** O desenho — notícia com o mercado fechado, "
        "reação na abertura seguinte — é o experimento natural mais limpo disponível, e "
        "o grupo de controle reforça muito o argumento. Ainda assim, é associação bem "
        "medida, não causa demonstrada.",
    ])

    # ── 8 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "8", "O que eu previ e o que aconteceu")

    A.tabela_abnt(doc, "8", "As previsões registradas antes de rodar",
        ["Previsão", "Resultado", "Acertei?"],
        [
            ["volume com efeito forte", "+34,2%, o mais forte de todos", "SIM"],
            ["volatilidade com efeito forte", "+17,6%", "SIM"],
            ["direção nula na Rodada A", "p = 0,787", "SIM"],
            ["efeito concentrado na cauda", "52,3% não mexeram", "SIM"],
            ["direção FRACA ou nula na Rodada B",
             "fraca, mas REAL: +4,87 p.p., p = 0,012", "parcialmente"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**Errei para menos na Rodada B, e é bom que tenha sido nessa direção.** Eu "
        "esperava nulo; saiu fraco mas significativo, e com o sinal na direção certa em "
        "todos os testes.")

    A.secao(doc, "9", "Em cinco frases, se o tempo apertar")

    A.lista(doc, [
        "“Peguei 3.435 comunicados entregues à CVM depois que o mercado fechou, com "
        "hora oficial, e olhei o pregão seguinte.”",
        "“O volume negocia 34% acima do normal e a volatilidade 18% acima — comparando "
        "com pregões sem comunicado nenhum, não contra 1,00, porque o piso não é 1,00.”",
        "“Mas metade dos fatos relevantes não move nada. O efeito médio vem de uma "
        "minoria — é o efeito de cauda de novo.”",
        "“A classificação da CVM não pode prever direção, porque não diz se a notícia é "
        "boa ou ruim. A minha pode, e acerta 4,87 pontos acima do palpite trivial.”",
        "“E o sinal mora quase todo na classe negativa: o que o modelo chama de ruim "
        "rende −0,35%, contra praticamente zero nas outras classes. Ele reconhece o "
        "ruim; não reconhece o bom.”",
    ])

    try:
        doc.save(SAIDA)
        destino = SAIDA
    except PermissionError:
        destino = SAIDA.with_name(SAIDA.stem + "_ATUALIZADO.docx")
        doc.save(destino)
        print("  [aviso] original aberto no Word; gravado ao lado.")
    print(f"[OK] {destino}")


if __name__ == "__main__":
    main()
