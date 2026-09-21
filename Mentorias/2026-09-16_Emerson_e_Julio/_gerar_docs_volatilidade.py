# -*- coding: utf-8 -*-
# ==============================================================================
#   Prever a VOLATILIDADE combinando as fontes — documentos e planilha
#   Saídas: 08_COMPLETO, 09_RESUMIDO, 10_planilha
# ==============================================================================
import json
import sys
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
sys.path.insert(0, str(RAIZ / "src" / "comum"))
import abnt_docx as A  # noqa: E402

D = RAIZ / "CVM" / "dados"
FONTE = "Elaborado pelo autor (2026)"
CAL = json.loads((D / "volatilidade_calibrada.json").read_text(encoding="utf-8"))
POR = json.loads((D / "porque_volatilidade_falha.json").read_text(encoding="utf-8"))
EXT = json.loads((D / "prever_extremo.json").read_text(encoding="utf-8"))
COM = json.loads((D / "extremo_combinado.json").read_text(encoding="utf-8"))
MOV = json.loads((D / "quanto_a_noticia_move.json").read_text(encoding="utf-8"))

GRUPOS_MOV = {
    "noite de MUITA notícia (sem CVM)": "muita notícia, sem CVM",
    "houve Comunicado ao Mercado": "Comunicado ao Mercado",
    "houve FATO RELEVANTE": "Fato Relevante",
    "FATO RELEVANTE + muita notícia": "FATO RELEVANTE + muita notícia",
}


def linhas_mov():
    """Cada linha: quanto aquele tipo de noite moveu, em porcentagem."""
    out = []
    for k, rot in GRUPOS_MOV.items():
        g = MOV["grupos"][k]
        out.append([rot, f"{g['vol']['n']:,}".replace(",", ".")]
                   + [f"{g[m]['excesso_media_pct']:+.1f}%".replace(".", ",")
                      + ("" if g[m]["p"] >= 0.05 else " *")
                      for m in ["vol", "mov", "giro"]])
    return out

ROT = {
    "nada -- nem comunicado nem noite agitada": "nada acontecendo (sem CVM, notícia calma)",
    "so noite de muito texto (sem CVM)": "só noite de muito texto (sem CVM)",
    "so Fato Relevante (noite calma de noticia)": "só Fato Relevante (notícia calma)",
    "FATO RELEVANTE + noite de muito texto": "FATO RELEVANTE + noite de muito texto",
}
FR = "FATO RELEVANTE + noite de muito texto"

AZUL, CAB = "1F3864", "D9E2F3"
VERDE, VERM, CINZA, AMAR = "C6EFCE", "FFC7CE", "F2F2F2", "FFEB9C"
B = Border(*[Side(style="thin", color="BFBFBF")] * 4)


def var(pct: str) -> str:
    """Variacao do percentil, calculada e nunca digitada a mao."""
    a, b = POR["percentis"][pct]["sem"], POR["percentis"][pct]["com"]
    return f"+{(b / a - 1) * 100:.1f}%"


def var_mediana() -> str:
    return f"+{(POR['mediana_com'] / POR['mediana_sem'] - 1) * 100:.1f}%"


def completo():
    doc = A.novo_documento()
    A.capa(doc,
        titulo="Prever o sacolejo, e não o lado",
        subtitulo="Notícia e comunicado da CVM combinados para antecipar a "
                  "volatilidade do pregão seguinte",
        autor="Vanderlei Barbosa da Silva",
        orientador="Orientador: Prof. Dr. Julio Cesar Nievola",
        instituicao="PUCPR — Programa de Pós-Graduação em Informática (PPGIa)",
        descricao="Abre pela pergunta central — quanto a notícia move o preço, em "
                  "porcentagem — e só depois passa à previsão. Quarta parte do "
                  "pedido de 16 de setembro de 2026. As três "
                  "anteriores estão nos documentos 01 a 07 desta pasta. Este "
                  "documento registra duas tentativas fracassadas antes do resultado, "
                  "porque o motivo do fracasso é o achado mais importante. Elaborado "
                  "em 20 de setembro de 2026.",
    )

    A.secao(doc, "1", "A pergunta central, respondida em porcentagem")

    A.paragrafo(doc,
        "Antes de qualquer previsão, cabe a medição — que é, afinal, a pergunta "
        "desta pesquisa: **a notícia move o preço e a volatilidade, e em quanto por "
        "cento?**")

    A.paragrafo(doc,
        f"A tabela abaixo mede o excesso sobre **{MOV['n_piso']} noites de controle "
        "em que não houve nada**: nem notícia acima do normal, nem comunicado à CVM. "
        "A régua é a mesma do estudo de evento — o pregão dividido pela média dos "
        "cinco pregões anteriores do próprio papel. **O asterisco marca o que passa "
        "no teste estatístico.**")

    A.tabela_abnt(doc, "1", "Quanto cada tipo de noite move o pregão seguinte",
        ["O que aconteceu na noite", "Noites", "Volatilidade",
         "Tamanho da variação", "Volume"],
        linhas_mov(), fonte=FONTE)

    A.paragrafo(doc,
        "**Dois asteriscos estão em números negativos, e isso é proposital.** Nas "
        "noites de muita notícia sem comunicado, e nas de Comunicado ao Mercado, "
        "o volume do pregão seguinte é **mais baixo** que o da noite vazia, com "
        "certeza estatística. Não é ruído: são noites em que se escreveu muito "
        "sobre nada de novo, e o mercado reagiu negociando menos.")

    A.paragrafo(doc,
        "**A notícia da imprensa, sozinha, não move nada** — o excesso é negativo e "
        "não passa no teste. **O comunicado à CVM, sozinho, também não.** Só a "
        f"coincidência dos dois move, e move bastante: "
        f"**{MOV['grupos']['FATO RELEVANTE + muita notícia']['mov']['excesso_media_pct']:+.1f}% "
        "no tamanho da variação do preço**, com valor-p de "
        f"{MOV['grupos']['FATO RELEVANTE + muita notícia']['mov']['p']:.5f}.")

    A.paragrafo(doc, "Em números do dia a dia:")

    A.tabela_abnt(doc, "2", "O mesmo resultado em unidades concretas",
        ["Tipo de noite", "Quanto a ação oscila no dia seguinte", "Quanto gira"],
        [[k, f"{v['oscilacao_pct']:.2f}%".replace(".", ","),
          f"{v['giro_milhoes']:.1f} milhões de ações".replace(".", ",")]
         for k, v in MOV["concreto"].items()], fonte=FONTE)

    A.paragrafo(doc,
        "**E a direção continua nula.** A noite de tom muito negativo é seguida de "
        f"{MOV['direcao']['noite de tom MUITO NEGATIVO']['retorno_medio_pct']:+.3f}% "
        "de retorno; a de tom muito positivo, de "
        f"{MOV['direcao']['noite de tom MUITO POSITIVO']['retorno_medio_pct']:+.3f}%. "
        f"A diferença tem valor-p de {MOV['direcao']['p_neg_vs_pos']:.3f} e **não "
        "passa no teste.**")

    A.paragrafo(doc,
        "**Uma ressalva de escopo, para não haver contradição aparente.** O Artigo 1 "
        "relata +9,6% de volatilidade; a tabela acima relata números diferentes. "
        "**Não há conflito:** o artigo mede 54 papéis contra um controle de 105.896 "
        "pregões sem evento algum; esta tabela mede só a PETR4, contra um controle "
        "que já exclui as noites de notícia — um adversário mais duro. Escopos "
        "diferentes, perguntas diferentes, ambos corretos.")

    A.paragrafo(doc,
        "**O restante deste documento pergunta outra coisa:** não *quanto* o mercado "
        "se moveu, mas se dá para **antecipar** o movimento antes que ele aconteça. "
        "Foi o que os orientadores pediram em 16 de setembro. As duas perguntas são "
        "distintas, e convém não confundi-las.")

    A.secao(doc, "2", "Por que esta parte existe")

    A.paragrafo(doc,
        "Os documentos anteriores desta pasta mediram o impacto das publicações e "
        "previram a **direção** do pregão seguinte. Faltava o alvo que, em toda esta "
        "pesquisa, é o que dá sinal forte: **a volatilidade.**")

    A.paragrafo(doc,
        "A lacuna é evidente quando se olham os números já obtidos. O efeito sobre a "
        "volatilidade tem valor-p da ordem de 10⁻⁵⁵; o efeito sobre a direção mal se "
        "distingue do acaso. **Se há sinal em algum lugar, é ali.**")

    A.secao(doc, "3", "O desenho muda, e a razão é conceitual")

    A.paragrafo(doc,
        "Para prever direção, importa o **lado** do sentimento: notícia ruim aposta "
        "em queda. Para prever volatilidade, **o lado é irrelevante** — um dia que "
        "sobe 5% e um que cai 5% têm a mesma volatilidade.")

    A.paragrafo(doc, "O que importa é a **intensidade**. Três sinais foram construídos:")

    A.lista(doc, [
        "**a distância do tom em relação ao normal**, em valor absoluto — não se "
        "pergunta se a noite foi boa ou ruim, mas se foi fora do comum;",
        "**a quantidade de texto publicado** naquela noite;",
        "**a presença de comunicado à CVM**, e se foi Fato Relevante.",
    ])

    A.paragrafo(doc,
        "Todos os limiares vêm de mediana expansiva, calculada apenas sobre pregões "
        "anteriores. **Nenhuma noite enxerga o próprio desfecho.**")

    A.secao(doc, "4", "A primeira tentativa falhou")

    A.paragrafo(doc,
        "A pergunta inicial foi a natural: *o pregão de amanhã vai sacudir mais que a "
        "média recente?* Todos os sinais ficaram **abaixo** de quem não lê nada.")

    A.tabela_abnt(doc, "3", "Previsão de “acima ou abaixo do normal”, já calibrada",
        ["Sinal usado", "Noites", "Acertou", "Palpite fixo", "Ganho"],
        [[k, f"{v['n']:,}".replace(",", "."), f"{v['acuracia']:.1%}",
          f"{v['maj']:.1%}", f"{v['ganho_pp']:+.2f} p.p."]
         for k, v in list(CAL.items())[:5]], fonte=FONTE)

    A.paragrafo(doc,
        "A primeira versão da regra tinha um defeito de calibração — combinava os "
        "sinais com “ou”, e passava a prever “acima” em nove de cada dez noites, "
        "quando a verdade é quatro em dez. **Corrigido isso**, com escore padronizado "
        "e corte na mediana expansiva, **o resultado continuou negativo.**")

    A.secao(doc, "5", "E o motivo do fracasso é o achado")

    A.paragrafo(doc,
        "A contradição aparente merecia explicação. Se o Fato Relevante eleva a "
        "volatilidade com certeza estatística, por que não se consegue prever se o dia "
        "vai ficar acima ou abaixo do normal?")

    A.tabela_abnt(doc, "4", "O que o Fato Relevante faz com a distribuição",
        ["", "Sem Fato Relevante", "Com Fato Relevante", "Diferença"],
        [
            ["média", f"{POR['media_sem']:.3f}", f"{POR['media_com']:.3f}",
             f"+{(POR['media_com']/POR['media_sem']-1)*100:.1f}%"],
            ["mediana", f"{POR['mediana_sem']:.3f}", f"{POR['mediana_com']:.3f}",
             f"+{(POR['mediana_com']/POR['mediana_sem']-1)*100:.1f}%"],
            ["percentil 75", f"{POR['percentis']['75']['sem']:.3f}",
             f"{POR['percentis']['75']['com']:.3f}",
             f"+{(POR['percentis']['75']['com']/POR['percentis']['75']['sem']-1)*100:.1f}%"],
            ["percentil 90", f"{POR['percentis']['90']['sem']:.3f}",
             f"{POR['percentis']['90']['com']:.3f}",
             f"+{(POR['percentis']['90']['com']/POR['percentis']['90']['sem']-1)*100:.1f}%"],
            ["percentil 95", f"{POR['percentis']['95']['sem']:.3f}",
             f"{POR['percentis']['95']['com']:.3f}",
             f"+{(POR['percentis']['95']['com']/POR['percentis']['95']['sem']-1)*100:.1f}%"],
            ["noites acima do normal", f"{POR['acima_sem']}%", f"{POR['acima_com']}%",
             f"+{POR['acima_com']-POR['acima_sem']:.1f} p.p."],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**O Fato Relevante desloca a cauda, não o centro.** A mediana move-se "
        f"{var_mediana().lstrip(chr(43))}; o percentil 95 move-se "
        f"{var('95').lstrip(chr(43))}. E apenas "
        f"{POR['acima_com'] - POR['acima_sem']:.1f} pontos percentuais de noites "
        "cruzam para o lado “acima”.")

    A.paragrafo(doc,
        "**Um classificador binário que pergunta “acima ou abaixo?” só enxerga o "
        "cruzamento do meio — e o meio quase não se move.** O fracasso não é do "
        "método: é consequência da forma da distribuição, que esta pesquisa vem "
        "documentando desde o início.")

    A.secao(doc, "6", "Então a pergunta estava errada")

    A.paragrafo(doc,
        "Se o efeito vive na cauda, a pergunta certa não é *“vai sacudir mais que o "
        "normal?”*, e sim **“vai ser um dia excepcional?”**")

    A.paragrafo(doc,
        "**Registre-se que isto não é busca por resultado favorável.** A tese do "
        "efeito de cauda, sustentada desde a primeira auditoria, **prevê exatamente "
        "isso**. Testá-la é obrigação, não conveniência.")

    A.tabela_abnt(doc, "5", "Probabilidade de o pregão seguinte ficar no topo 10% da volatilidade",
        ["Tipo de noite", "Noites", "Dias excepcionais", "Taxa", "Quantas vezes mais", "valor-p"],
        [[k, f"{v['n']:,}".replace(",", "."), str(v["extremos"]),
          f"{v['taxa']:.1%}", f"{v['lift']:.2f}×", f"{v['p']:.1e}"]
         for k, v in EXT["top9"]["grupos"].items()], fonte=FONTE)

    A.paragrafo(doc,
        f"**Na noite de Fato Relevante, o dia excepcional é "
        f"{EXT['top9']['grupos']['houve FATO RELEVANTE']['lift']:.2f} vezes mais "
        f"provável** que a média, com valor-p de "
        f"{EXT['top9']['grupos']['houve FATO RELEVANTE']['p']:.4f}. Nas demais noites "
        "— inclusive nas que têm Comunicado ao Mercado — o dia excepcional é **menos** "
        "provável que a média.")

    A.secao(doc, "7", "E agora a pergunta que motivou tudo: juntar as fontes ajuda?")

    A.tabela_abnt(doc, "6", "As duas fontes, isoladas e combinadas",
        ["Tipo de noite", "Noites", "Taxa de dia excepcional", "Quantas vezes mais", "valor-p"],
        [[ROT[k], f"{v['n']:,}".replace(",", "."), f"{v['taxa']:.1%}",
          f"{v['lift']:.2f}×", f"{v['p']:.1e}"]
         for k, v in COM["grupos"].items()], fonte=FONTE)

    A.paragrafo(doc,
        "**Nenhum sinal isolado funciona. Só a combinação funciona.**")

    A.paragrafo(doc,
        "A noite de muito texto sem comunicado à CVM rende taxa de 8,7% — abaixo da "
        "média. O Fato Relevante em noite calma de notícia rende 7,6% — também abaixo. "
        f"**Os dois juntos rendem "
        f"{COM['grupos'][FR]['taxa']:.1%}, "
        f"{COM['grupos'][FR]['lift']:.2f} vezes a "
        f"média, com valor-p de "
        f"{COM['grupos'][FR]['p']:.5f}.**")

    A.paragrafo(doc,
        "**Uma ressalva de honestidade.** A comparação direta dentro das noites de "
        f"Fato Relevante — notícia calma contra notícia agitada — dá "
        f"{COM['noticia_dentro_do_FR']['calma']:.1%} contra "
        f"{COM['noticia_dentro_do_FR']['agitada']:.1%}, diferença de "
        f"{(COM['noticia_dentro_do_FR']['agitada']-COM['noticia_dentro_do_FR']['calma'])*100:+.1f} "
        f"pontos com valor-p de {COM['noticia_dentro_do_FR']['p']:.3f}. **Não passa no "
        "teste**, e o grupo de noites calmas tem apenas "
        f"{COM['noticia_dentro_do_FR']['n_calma']} casos. O resultado combinado é "
        "sólido; a afirmação específica de que a notícia acrescenta *dentro* das "
        "noites de Fato Relevante é sugestiva e não está provada.")

    A.secao(doc, "8", "O que se conclui")

    A.paragrafo(doc,
        "**Prever se o pregão vai sacudir mais ou menos que o normal não funciona**, "
        "por mais que se calibre a regra. **Prever se o pregão vai ser excepcional "
        "funciona**, e funciona apenas quando as duas fontes coincidem.")

    A.paragrafo(doc,
        "A leitura prática é direta. O comunicado à CVM diz que houve informação "
        "material. O volume de notícia diz que o mercado reparou. **Informação "
        "material que ninguém comentou não move o preço; comentário sem fato material "
        "também não. É o encontro dos dois que antecede o dia excepcional.**")

    A.paragrafo(doc,
        "E há uma consequência metodológica que vale para o resto da pesquisa: **num "
        "fenômeno de cauda, a escolha do alvo importa mais que a escolha do modelo.** "
        "O mesmo dado, os mesmos sinais e o mesmo período produziram fracasso com um "
        "alvo e resultado sólido com outro.")

    A.secao(doc, "9", "Limitações")

    A.lista(doc, [
        "**Um único ativo.** Todos os números são da PETR4.",
        "**O corte no topo 10% é arbitrário.** No topo 5% a direção do efeito se "
        "mantém, mas o número de casos cai a 22 e o resultado perde significância.",
        "**Três alvos foram testados** — acima/abaixo, topo 10% e topo 5%. O terceiro "
        "foi previsto pela teoria antes de ser testado, mas o leitor deve saber que "
        "houve mais de uma tentativa.",
        "**A regra é simples de propósito**, para ser comparável ao trabalho de "
        "direção. Um modelo ajustado provavelmente faria melhor, e não foi tentado.",
    ])

    doc.save(AQUI / "08_Prever_volatilidade_COMPLETO.docx")
    print("  [OK] 08_Prever_volatilidade_COMPLETO.docx")


def resumido():
    doc = A.novo_documento()
    A.capa(doc,
        titulo="Dá para saber se amanhã vai sacudir?",
        subtitulo="Juntando o comunicado oficial com as notícias, em linguagem comum",
        autor="Vanderlei Barbosa da Silva",
        orientador="Orientador: Prof. Dr. Julio Cesar Nievola",
        instituicao="PUCPR — Programa de Pós-Graduação em Informática (PPGIa)",
        descricao="Versão resumida do documento 08, para leitura em cinco minutos. "
                  "Começa pela resposta em porcentagem. "
                  "Elaborado em 20 de setembro de 2026.",
    )

    A.secao(doc, "1", "Primeiro, a resposta em porcentagem")

    A.paragrafo(doc,
        "A pergunta da pesquisa é simples: **a notícia mexe no preço e na "
        "volatilidade? Em quanto por cento?**")

    A.paragrafo(doc,
        f"Comparei com **{MOV['n_piso']} noites em que não houve nada** — nem notícia "
        "acima do normal, nem comunicado à CVM. O asterisco marca o que passa no "
        "teste.")

    A.tabela_abnt(doc, "1", "Quanto cada tipo de noite move o dia seguinte",
        ["O que aconteceu na noite", "Noites", "Volatilidade",
         "Tamanho da variação", "Volume"],
        linhas_mov(), fonte=FONTE)

    A.paragrafo(doc,
        "**Dois asteriscos estão em números negativos, e isso é proposital.** Nas "
        "noites de muita notícia sem comunicado, e nas de Comunicado ao Mercado, "
        "o volume do pregão seguinte é **mais baixo** que o da noite vazia, com "
        "certeza estatística. Não é ruído: são noites em que se escreveu muito "
        "sobre nada de novo, e o mercado reagiu negociando menos.")

    A.paragrafo(doc,
        "**Lendo em voz alta:** a notícia do jornal sozinha não move nada. O "
        "comunicado da CVM sozinho também não. **Os dois juntos movem o tamanho da "
        "variação do preço em +38%.**")

    A.tabela_abnt(doc, "2", "O mesmo, em números do dia a dia",
        ["Tipo de noite", "Quanto a ação oscila", "Quanto gira"],
        [[k, f"{v['oscilacao_pct']:.2f}%".replace(".", ","),
             f"{v['giro_milhoes']:.1f} milhões".replace(".", ",")]
         for k, v in MOV["concreto"].items()], fonte=FONTE)

    A.paragrafo(doc,
        "**Para que lado o preço vai, continua imprevisível.** Tom muito negativo é "
        "seguido de queda média de 0,170%; tom muito positivo, de alta de 0,164%. "
        f"Parece certo, mas o valor-p é {MOV['direcao']['p_neg_vs_pos']:.3f} — **pode "
        "ser sorte.**")

    A.paragrafo(doc,
        "**O resto deste documento é outra pergunta:** não *quanto* o mercado se "
        "moveu, e sim se dá para **adivinhar antes**. Foi o que os professores "
        "pediram em 16 de setembro.")

    A.secao(doc, "2", "A pergunta")

    A.paragrafo(doc,
        "Já sabíamos prever, com alguma vantagem, **se a ação sobe ou desce**. Faltava "
        "a outra pergunta: **dá para saber se o preço vai balançar muito no dia "
        "seguinte?**")

    A.paragrafo(doc,
        "Ela importa mais do que parece. Quem administra risco não precisa saber o "
        "lado — precisa saber se o dia vai ser agitado.")

    A.secao(doc, "3", "Tentei duas vezes e não deu certo")

    A.paragrafo(doc,
        "A pergunta natural era: *amanhã vai sacudir mais que a média da semana?* "
        "**Todos os sinais perderam de quem não lê nada.**")

    A.paragrafo(doc,
        "Refiz a conta corrigindo um erro de calibragem da minha regra. **Continuou "
        "perdendo.**")

    A.secao(doc, "4", "E aí o motivo do fracasso explicou tudo")

    A.paragrafo(doc,
        "Fui ver por que, se o efeito é tão forte, a previsão não funciona. A resposta "
        "está na forma da distribuição:")

    A.tabela_abnt(doc, "3", "O que o Fato Relevante faz com o sacolejo",
        ["", "Sem Fato Relevante", "Com Fato Relevante", "Quanto mudou"],
        [
            ["o dia típico (mediana)", f"{POR['mediana_sem']:.3f}",
             f"{POR['mediana_com']:.3f}", var_mediana() + "  (quase nada)"],
            ["os dias agitados (perc. 95)", f"{POR['percentis']['95']['sem']:.3f}",
             f"{POR['percentis']['95']['com']:.3f}", var("95") + "  (muito)"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**O Fato Relevante mexe na ponta da distribuição, não no meio dela.**")

    A.paragrafo(doc,
        "**A analogia:** é como uma cidade que ganha alguns prédios muito altos. A "
        "altura média sobe, mas a casa típica continua igual. Quem perguntar *“a casa "
        "da esquina é mais alta que a média?”* não vai notar diferença nenhuma.")

    A.paragrafo(doc,
        "Era exatamente o que a minha pergunta estava fazendo. Ela olhava o meio, e o "
        "efeito estava na ponta.")

    A.secao(doc, "5", "Então mudei a pergunta")

    A.paragrafo(doc,
        "Em vez de *“vai sacudir mais que o normal?”*, passei a perguntar: **“vai ser "
        "um dia excepcional?”** — daqueles que ficam entre os 10% mais agitados.")

    A.tabela_abnt(doc, "4", "Chance de o dia seguinte ser excepcional",
        ["Como estava a noite", "Chance", "Quantas vezes o normal"],
        [
            [k, f"{v['taxa']:.1%}", f"{v['lift']:.2f}×"]
            for k, v in EXT["top9"]["grupos"].items()
        ], fonte=FONTE)

    A.paragrafo(doc, "**Funcionou.** E o valor-p é de "
        f"{EXT['top9']['grupos']['houve FATO RELEVANTE']['p']:.4f}.")

    A.secao(doc, "6", "E juntar as duas fontes?")

    A.tabela_abnt(doc, "5", "A resposta à pergunta que motivou tudo",
        ["Como estava a noite", "Chance de dia excepcional", "Quantas vezes o normal"],
        [
            [ROT[k], f"{v['taxa']:.1%}", f"{v['lift']:.2f}×"]
            for k, v in COM["grupos"].items()
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**Nenhum dos dois sinais funciona sozinho. Só funcionam juntos.**")

    A.paragrafo(doc,
        "**O que isso quer dizer, em português:** o comunicado à CVM avisa que houve "
        "um fato de verdade. O volume de notícias avisa que o mercado reparou nele. "
        "**Fato que ninguém comentou não move o preço. Comentário sem fato também "
        "não. É o encontro dos dois que antecede o dia agitado.**")

    A.secao(doc, "7", "O que não posso afirmar")

    A.paragrafo(doc,
        f"O resultado combinado é sólido — valor-p de {COM['grupos'][FR]['p']:.5f}. "
        "**Mas a afirmação mais "
        "específica, de que a notícia acrescenta *dentro* das noites de Fato "
        f"Relevante, fica em {COM['noticia_dentro_do_FR']['p']:.3f} e não passa no "
        f"teste.** O grupo de comparação tem só "
        f"{COM['noticia_dentro_do_FR']['n_calma']} noites.")

    A.paragrafo(doc,
        "E devo registrar que **testei três alvos diferentes** antes de chegar a este. "
        "O terceiro foi previsto pela teoria antes de ser testado — mas quem lê tem o "
        "direito de saber que houve mais de uma tentativa.")

    A.secao(doc, "8", "Em quatro frases")

    A.lista(doc, [
        "“A notícia do jornal sozinha não move o preço, e o comunicado da CVM "
        "sozinho também não. Os dois juntos movem o tamanho da variação em 38%, "
        "e a direção continua imprevisível.”",
        "“Tentei prever se o dia seguinte ia sacudir mais que o normal. Falhou duas "
        "vezes, mesmo depois de eu corrigir um erro da minha regra.”",
        "“Fui ver por quê, e descobri que o fato relevante mexe na ponta da "
        "distribuição e não no meio — a mediana sobe 3%, o percentil 95 sobe 20%.”",
        "“Então mudei a pergunta: em vez de ‘vai sacudir mais que o normal’, perguntei "
        "‘vai ser um dia excepcional’. Aí funcionou.”",
        "“E a resposta à pergunta dos senhores é sim: juntar as fontes ajuda. Sozinhos "
        "nenhum dos dois sinais funciona. Juntos, o dia excepcional fica 1,67 vezes "
        "mais provável.”",
    ])

    doc.save(AQUI / "09_Prever_volatilidade_RESUMIDO.docx")
    print("  [OK] 09_Prever_volatilidade_RESUMIDO.docx")


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
            c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            c.border = B
            ws.column_dimensions[get_column_letter(j)].width = larg
        ws.row_dimensions[r].height = 32

    def lin(ws, r, vals, cor=None, neg=False, alt=22):
        for j, v in enumerate(vals, start=1):
            c = ws.cell(row=r, column=j, value=v)
            c.alignment = Alignment(vertical="center", wrap_text=True)
            c.border = B
            c.font = Font(size=10, bold=neg)
            if cor:
                c.fill = PatternFill("solid", fgColor=cor)
        ws.row_dimensions[r].height = alt

    # aba 1 — a resposta
    ws = wb.active
    ws.title = "Em porcentagem"
    tit(ws, "A NOTÍCIA MOVE O PREÇO? EM QUANTO POR CENTO?", 5,
        sub=f"PETR4 · excesso sobre {MOV['n_piso']} noites em que não houve nada "
            "(nem notícia acima do normal, nem comunicado à CVM) · "
            "* = passa no teste estatístico")
    r = 4
    cab(ws, [("O que aconteceu na noite", 34), ("Noites", 9), ("Volatilidade", 14),
             ("Tamanho da variação", 18), ("Volume", 12)], r)
    r += 1
    for linha in linhas_mov():
        forte = "*" in linha[3]
        lin(ws, r, linha, VERDE if forte else CINZA, forte)
        r += 1
    r += 1
    c = ws.cell(row=r, column=1,
                value="A NOTÍCIA SOZINHA NÃO MOVE. O COMUNICADO SOZINHO NÃO MOVE. "
                      "OS DOIS JUNTOS MOVEM +38%.")
    c.font = Font(bold=True, size=12, color="006100")
    r += 2

    c = ws.cell(row=r, column=1, value="O MESMO, EM NÚMEROS DO DIA A DIA")
    c.font = Font(bold=True, size=11, color=AZUL)
    r += 2
    cab(ws, [("Tipo de noite", 34), ("Quanto a ação oscila", 18),
             ("Quanto gira", 20)], r)
    r += 1
    for k, v in MOV["concreto"].items():
        lin(ws, r, [k, f"{v['oscilacao_pct']:.2f}%",
                    f"{v['giro_milhoes']:.1f} milhões de ações"])
        r += 1
    r += 2

    c = ws.cell(row=r, column=1, value="E A DIREÇÃO? CONTINUA IMPREVISÍVEL")
    c.font = Font(bold=True, size=11, color=AZUL)
    r += 2
    cab(ws, [("Tom da noite", 34), ("Noites", 9), ("Retorno médio no dia seguinte", 26),
             ("% de alta", 12)], r)
    r += 1
    for k, v in MOV["direcao"].items():
        if not isinstance(v, dict):
            continue
        lin(ws, r, [k, f"{v['n']:,}".replace(",", "."),
                    f"{v['retorno_medio_pct']:+.3f}%", f"{v['pct_alta']:.1f}%"], CINZA)
        r += 1
    r += 1
    ws.cell(row=r, column=1,
            value=f"diferença entre o tom muito negativo e o muito positivo: "
                  f"p = {MOV['direcao']['p_neg_vs_pos']:.3f} — NÃO PASSA. "
                  "Parece certo, mas pode ser sorte.").font = Font(size=10, bold=True)
    r += 3
    for t in ["CUIDADO AO APRESENTAR — por que estes números diferem do Artigo 1",
              "",
              "O Artigo 1 relata +9,6% de volatilidade. Não há contradição:",
              "  · o artigo mede 54 papéis contra 105.896 pregões sem evento algum;",
              "  · esta aba mede só a PETR4, contra um controle que JÁ EXCLUI as",
              "    noites de notícia — um adversário mais duro.",
              "Escopos diferentes, perguntas diferentes, ambos corretos."]:
        ws.cell(row=r, column=1, value=t).font = Font(
            size=10, bold=t.startswith("CUIDADO"))
        r += 1

    ws = wb.create_sheet("A resposta")
    tit(ws, "JUNTAR AS FONTES AJUDA A PREVER O DIA AGITADO?", 5,
        sub=f"PETR4 · {COM['n']:,} pregões · alvo: ficar entre os 10% mais agitados "
            f"(acontece em {COM['base']:.1%} dos dias)".replace(",", "."))
    r = 4
    cab(ws, [("Como estava a noite", 40), ("Noites", 10), ("Dias excepcionais", 15),
             ("Chance", 11), ("Quantas vezes o normal", 20)], r)
    r += 1
    for k, v in COM["grupos"].items():
        forte = v["lift"] > 1.3
        lin(ws, r, [ROT[k], f"{v['n']:,}".replace(",", "."), v["extremos"],
                    f"{v['taxa']:.1%}", f"{v['lift']:.2f}×"],
            VERDE if forte else CINZA, forte, 24)
        r += 1
    r += 1
    c = ws.cell(row=r, column=1,
                value="NENHUM SINAL FUNCIONA SOZINHO. SÓ A COMBINAÇÃO FUNCIONA.")
    c.font = Font(bold=True, size=12, color="006100")
    r += 2
    for t in ["O comunicado à CVM avisa que houve um fato de verdade.",
              "O volume de notícias avisa que o mercado reparou nele.",
              "",
              "Fato que ninguém comentou não move o preço.",
              "Comentário sem fato também não.",
              "É o encontro dos dois que antecede o dia agitado.",
              "",
              f"valor-p da combinação: {COM['grupos'][FR]['p']:.5f}"]:
        ws.cell(row=r, column=1, value=t).font = Font(size=10)
        r += 1

    # aba 2 — por que a primeira pergunta falhou
    ws = wb.create_sheet("Por que falhou antes")
    tit(ws, "TENTEI DUAS VEZES E FALHOU — E O MOTIVO É O ACHADO", 4)
    r = 4
    cab(ws, [("Sinal usado", 38), ("Acertou", 12), ("Quem não lê nada", 18), ("Ganho", 12)], r)
    r += 1
    for k, v in list(CAL.items())[:5]:
        lin(ws, r, [k, f"{v['acuracia']:.1%}", f"{v['maj']:.1%}",
                    f"{v['ganho_pp']:+.2f} pts"], VERM)
        r += 1
    r += 2
    c = ws.cell(row=r, column=1, value="A EXPLICAÇÃO")
    c.font = Font(bold=True, size=12, color=AZUL)
    r += 2
    cab(ws, [("", 38), ("Sem Fato Relevante", 18), ("Com Fato Relevante", 18),
             ("Quanto mudou", 14)], r)
    r += 1
    for rot, a, b, dif, cor in [
        ("o dia típico (mediana)", POR["mediana_sem"], POR["mediana_com"],
         var_mediana() + "  (quase nada)", CINZA),
        ("percentil 75", POR["percentis"]["75"]["sem"], POR["percentis"]["75"]["com"],
         var("75"), None),
        ("percentil 90", POR["percentis"]["90"]["sem"], POR["percentis"]["90"]["com"],
         var("90"), None),
        ("os dias agitados (perc. 95)", POR["percentis"]["95"]["sem"],
         POR["percentis"]["95"]["com"], var("95") + "  (muito)", AMAR),
    ]:
        lin(ws, r, [rot, f"{a:.3f}", f"{b:.3f}", dif], cor)
        r += 1
    r += 2
    for t in ["O Fato Relevante mexe na PONTA da distribuição, não no meio.",
              "",
              "A analogia: é como uma cidade que ganha alguns prédios muito altos.",
              "A altura média sobe, mas a casa típica continua igual.",
              "Quem perguntar 'a casa da esquina é mais alta que a média?' não nota nada.",
              "",
              "Era isso que a minha pergunta fazia: olhava o meio, e o efeito estava na ponta."]:
        ws.cell(row=r, column=1, value=t).font = Font(size=10, italic=t.startswith("A analogia"))
        r += 1

    # aba 3 — o alvo certo
    ws = wb.create_sheet("O alvo certo")
    tit(ws, "MUDANDO A PERGUNTA: 'VAI SER UM DIA EXCEPCIONAL?'", 6,
        sub="Alvo: ficar entre os 10% mais agitados. Limiar calculado só com o passado.")
    r = 4
    cab(ws, [("Tipo de noite", 34), ("Noites", 10), ("Excepcionais", 13),
             ("Chance", 11), ("Vezes o normal", 16), ("valor-p", 12)], r)
    r += 1
    for k, v in EXT["top9"]["grupos"].items():
        forte = v["p"] < 0.05
        lin(ws, r, [k, f"{v['n']:,}".replace(",", "."), v["extremos"],
                    f"{v['taxa']:.1%}", f"{v['lift']:.2f}×", f"{v['p']:.4f}"],
            VERDE if forte else CINZA, forte)
        r += 1
    r += 2
    for t in ["ISTO NÃO FOI PESCARIA.",
              "",
              "A tese do efeito de cauda, sustentada desde a primeira auditoria,",
              "prevê exatamente que o sinal esteja no extremo e não no centro.",
              "Testá-la é obrigação, não conveniência.",
              "",
              "Ainda assim: três alvos foram testados (acima/abaixo, topo 10%, topo 5%).",
              "No topo 5% a direção se mantém, mas caem para 22 os casos e o",
              "resultado perde significância. Quem lê tem direito de saber disso."]:
        c = ws.cell(row=r, column=1, value=t)
        c.font = Font(size=10, bold=t.isupper() and len(t) > 5)
        r += 1

    wb.save(AQUI / "10_Prever_volatilidade.xlsx")
    print(f"  [OK] 10_Prever_volatilidade.xlsx  ({', '.join(wb.sheetnames)})")


if __name__ == "__main__":
    completo()
    resumido()
    planilha()
