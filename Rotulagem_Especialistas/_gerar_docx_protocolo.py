# -*- coding: utf-8 -*-
# ==============================================================================
#   Protocolo — rotulagem por especialistas públicos
#   Pedido dos Profs. Emerson Paraiso e Julio Nievola (reunião de agosto/2026)
#   Saída: Rotulagem_Especialistas/01_PROTOCOLO.docx
# ==============================================================================
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(RAIZ / "src" / "comum"))

import abnt_docx as A  # noqa: E402

FONTE = "Elaborado pelo autor (2026)"
SAIDA = AQUI / "01_PROTOCOLO.docx"


def main() -> None:
    doc = A.novo_documento()

    A.capa(
        doc,
        titulo="Rotular pelas mãos de quem já rotula",
        subtitulo="Protocolo para usar as análises públicas de especialistas como "
                  "rótulo e como régua — resposta ao pedido dos Profs. Emerson "
                  "Paraiso e Julio Nievola",
        autor="Vanderlei Barbosa da Silva",
        orientador="Orientador: Prof. Dr. Julio Cesar Nievola",
        instituicao="PUCPR — Programa de Pós-Graduação em Informática (PPGIa)",
        descricao="Avaliação de viabilidade e protocolo experimental para a proposta "
                  "de obter rótulos a partir de análises publicadas por especialistas "
                  "de mercado, e de confrontar as previsões desses especialistas com o "
                  "preço efetivamente observado. Inclui o precedente na literatura, o "
                  "teste de acesso às fontes, três experimentos com protocolo definido "
                  "e os riscos identificados. Elaborado em 26 de agosto de 2026.",
    )

    # ── 1 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "1", "Resposta curta")

    A.paragrafo(doc,
        "**Sim, é possível, e recomendo que se faça.** Por três razões concretas:")

    A.lista(doc, [
        "**Há precedente de primeira linha.** Chen, De, Hu e Hwang (2014) publicaram na "
        "*Review of Financial Studies* — uma das três revistas mais respeitadas de "
        "finanças — um trabalho que faz exatamente isto: extrair a opinião de "
        "especialistas publicada na internet e verificar se ela antecipa o retorno das "
        "ações. **A resposta deles foi sim.**",
        "**As fontes existem e estão acessíveis.** Testei três nesta data e todas "
        "responderam, com arquivo histórico recuperável até 2021 no mínimo.",
        "**A infraestrutura já é nossa.** O InfoMoney e o Money Times — as duas fontes "
        "mais promissoras — já são raspados pelos nossos coletores.",
    ])

    A.paragrafo(doc,
        "**E há uma distinção no pedido que precisa ser desfeita antes de escrever a "
        "primeira linha de código**, sob pena de o experimento nascer torto. É o "
        "assunto da Seção 3.")

    A.paragrafo(doc,
        "Registro ainda que **isto não reabre a rotulagem manual suspensa**. São coisas "
        "diferentes: lá eu **produziria** rótulos; aqui eu **colho** rótulos que já "
        "existem, publicados, assinados e datados. O custo em horas minhas é de "
        "coleta, não de julgamento.")

    # ── 2 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "2", "O precedente: Chen, De, Hu e Hwang (2014)")

    A.paragrafo(doc,
        "*Review of Financial Studies*, 27(5):1367–1403. Texto integral aberto em "
        "bhwang.com.", recuo=False)

    A.paragrafo(doc,
        "**O que fizeram:** coletaram artigos publicados no Seeking Alpha — sítio onde "
        "analistas independentes escrevem sobre ações, cada artigo trazendo uma opinião "
        "explícita — e também os **comentários dos leitores** a esses artigos. Mediram "
        "o teor de cada um e verificaram se antecipavam o retorno da ação e a surpresa "
        "no resultado trimestral.")

    A.paragrafo(doc,
        "**O que encontraram:** tanto os artigos quanto os comentários **antecipam** "
        "retornos futuros e surpresas de resultado.")

    A.paragrafo(doc,
        "**Por que isso nos serve:** legitima o desenho inteiro. Quando a banca "
        "perguntar de onde veio a ideia de usar análise pública como rótulo, a resposta "
        "não é “foi uma sugestão da reunião” — é **um artigo em periódico de primeira "
        "linha, com mais de mil citações**.")

    A.paragrafo(doc,
        "**Onde eles diferem de nós, e isso importa:** o Seeking Alpha traz rótulo "
        "**explícito e estruturado** em cada artigo. Em português não existe "
        "equivalente com essa organização. **A nossa dificuldade não é conceitual, é de "
        "engenharia de coleta.**")

    # ── 3 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "3", "A distinção que precisa ser desfeita")

    A.paragrafo(doc,
        "O pedido, como formulado, encadeia três coisas — e elas **não são a mesma "
        "coisa**:")

    A.tabela_abnt(doc, "1", "Três perguntas diferentes dentro de um mesmo pedido",
        ["", "O que é", "Para que serve"],
        [
            ["(a)", "o especialista classifica uma NOTÍCIA como boa ou ruim para a "
                    "empresa", "seria um RÓTULO — o gabarito que falta ao nosso "
                    "classificador"],
            ["(b)", "o especialista PREVÊ que a ação vai subir ou cair",
             "é uma PREVISÃO — comparável ao que o nosso modelo faz"],
            ["(c)", "conferir no preço se aconteceu o previsto",
             "valida (b). NÃO valida (a)."],
        ], fonte=FONTE)

    A.secao(doc, "3.1", "Por que conferir o rótulo pelo preço é uma armadilha", nivel=2)

    A.paragrafo(doc,
        "Suponha que um analista escreva: *“o corte de preço da gasolina anunciado hoje "
        "é péssimo para a Petrobras”*. E suponha que, no dia seguinte, a PETR4 **suba**.")

    A.paragrafo(doc, "**Isso significa que o rótulo “negativo” estava errado?**")

    A.paragrafo(doc,
        "**Não.** Significa apenas que, naquele pregão, outra coisa pesou mais. E nós "
        "**já demonstramos** que é isso o que acontece na esmagadora maioria dos dias — "
        "é o efeito de cauda: a notícia não move o pregão comum, ela importa nos "
        "extremos.")

    A.paragrafo(doc,
        "**Duas evidências nossas dizem que esse critério não se sustenta:**")

    A.lista(doc, [
        "no nosso conjunto-ouro, a **rotulagem humana de direção acertou 46,7%** — "
        "**abaixo do acaso**;",
        "no teste de horizontes, o sinal do pregão de reação (55,0% / 53,2% / 51,6%, "
        "ordenado) **colapsa** no dia seguinte (52,5% / 52,4% / 51,5%).",
    ])

    A.paragrafo(doc,
        "**Ou seja: se adotarmos “o preço confirmou” como critério de qualidade do "
        "rótulo, estaremos julgando bons rótulos com uma régua que nós mesmos já "
        "provamos ser de cara ou coroa.** Rejeitaríamos rótulos corretos e aceitaríamos "
        "rótulos errados, ao sabor do ruído do pregão.")

    A.paragrafo(doc,
        "**A saída é simples:** manter (a) e (b) **separados**. O rótulo do especialista "
        "vale por si — ele é um leitor profissional, e é isso que queremos capturar. A "
        "conferência pelo preço vira **um experimento próprio**, sobre a previsão, não "
        "sobre o rótulo.")

    # ── 4 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "4", "O reenquadramento que torna isto valioso")

    A.paragrafo(doc,
        "Desfeita a confusão, aparece uma oportunidade que considero **a mais valiosa "
        "à nossa disposição neste momento** — e que não estava no pedido original.")

    A.paragrafo(doc,
        "**Não usar o especialista apenas como fonte de rótulo. Usá-lo como RÉGUA.**")

    A.paragrafo(doc,
        "A crítica mais provável na defesa é: *“54,5% de acerto é muito pouco”*. Hoje eu "
        "respondo com o argumento do ganho — 4,4 pontos percentuais sobre um modelo só "
        "de preços, dentro da faixa de 2 a 10 relatada na literatura. É uma resposta "
        "correta, mas indireta.")

    A.paragrafo(doc,
        "**A resposta direta seria esta:** se analistas profissionais, publicando com "
        "nome e reputação em jogo, acertam a direção da PETR4 em X% dos casos no mesmo "
        "período — e o nosso modelo acerta 54,5% —, **temos uma comparação que qualquer "
        "banca entende em cinco segundos.**")

    A.paragrafo(doc,
        "E note o que já sabemos: **a rotulagem humana de direção, no nosso "
        "conjunto-ouro, acertou 46,7%.** Se esse número se confirmar em analistas "
        "profissionais, ao longo de anos, deixa de ser curiosidade de um conjunto "
        "pequeno e **vira achado publicável**.")

    A.paragrafo(doc,
        "**Não conheço trabalho brasileiro que confronte um modelo de sentimento com "
        "as previsões públicas de especialistas sobre o mesmo ativo e o mesmo "
        "período.** É contribuição original, e barata.")

    # ── 5 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "5", "As fontes reais, com teste de acesso")

    A.paragrafo(doc,
        "Testei o acesso em 26 de agosto de 2026. O que segue não é levantamento "
        "bibliográfico, é verificação de que os dados podem de fato ser obtidos.")

    A.tabela_abnt(doc, "2", "Fontes avaliadas",
        ["Fonte", "O que fornece", "Histórico", "Acesso testado"],
        [
            ["InfoMoney — carteiras recomendadas",
             "quantas corretoras recomendam PETR4 no mês", "mensal, recuperável",
             "OK (200); artigo de 05/01/2021 recuperado"],
            ["Money Times — carteiras",
             "mesma informação, outra apuração", "mensal", "OK (200)"],
            ["TradingView — Ideias",
             "rótulo explícito “viés de alta” / “viés de baixa” com data",
             "desde cerca de 2020", "OK; rótulos e datas visíveis"],
            ["Seeking Alpha (PBR)",
             "nota explícita por artigo, de compra forte a venda forte", "longo",
             "BLOQUEADO (403) — e é a PBR em Nova York, não a PETR4"],
            ["Casas de análise (XP, BTG, Genial, Suno)",
             "tese e preço-alvo com data", "sim", "parcial — parte atrás de assinatura"],
            ["Economatica / Refinitiv",
             "consenso histórico estruturado", "completo", "A VERIFICAR com a PUCPR"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**Duas observações práticas.**")

    A.paragrafo(doc,
        "**Primeira, e é a mais importante:** vale perguntar à biblioteca da PUCPR se a "
        "instituição assina **Economatica** ou **Refinitiv Eikon**. Se assinar, o "
        "problema muda de natureza — passa a existir a série histórica de consenso de "
        "analistas, estruturada, sem raspagem e sem discussão de termos de uso. "
        "**Registre-se que a base Eikon é justamente a que Hashami e Maldonado (2025) "
        "usaram.** É a pergunta de maior retorno por minuto gasto em todo este "
        "protocolo.")

    A.paragrafo(doc,
        "**Segunda:** o Seeking Alpha bloqueou o acesso automatizado, e isso é um "
        "recado. Convém respeitar os termos de uso e o `robots.txt` de cada sítio. Para "
        "as fontes que restringem, o caminho legítimo é amostra coletada à mão ou "
        "acesso institucional — **não contornar bloqueio**.")

    # ── 6 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "6", "Os três experimentos")

    A.secao(doc, "6.1", "E1 — O especialista como régua (prioridade)", nivel=2)

    A.paragrafo(doc,
        "**Pergunta:** analistas profissionais acertam a direção da PETR4 melhor que o "
        "nosso modelo? Melhor que o acaso?")

    A.paragrafo(doc, "**Protocolo:**")

    A.lista(doc, [
        "coletar as chamadas direcionais datadas — carteiras mensais do InfoMoney e do "
        "Money Times, e ideias do TradingView;",
        "para cada chamada, apurar o retorno da PETR4 no horizonte declarado (o mês "
        "seguinte, no caso das carteiras);",
        "calcular a taxa de acerto, com teste binomial contra 50% e contra a classe "
        "majoritária;",
        "comparar com o nosso modelo pelo teste de McNemar, **nas mesmas datas**.",
    ])

    A.paragrafo(doc,
        "**Por que é a prioridade:** é o de menor risco — se os especialistas forem bem, "
        "temos uma referência honesta; se forem mal, temos um achado forte. **Nos dois "
        "casos o experimento rende.** E o horizonte mensal das carteiras coincide com "
        "o nosso melhor resultado, que é o de 22 pregões.")

    A.secao(doc, "6.2", "E2 — O rótulo do especialista", nivel=2)

    A.paragrafo(doc,
        "**Pergunta:** quando um especialista lê uma notícia sobre a Petrobras e diz se "
        "ela é boa ou ruim, o nosso FinBERT-PT-BR concorda com ele?")

    A.paragrafo(doc, "**Protocolo:**")

    A.lista(doc, [
        "localizar análises que comentem uma notícia **identificável** — “a Petrobras "
        "anunciou X, e isso é bom/ruim porque...”;",
        "extrair o par (notícia, classificação do especialista);",
        "casar cada notícia com a manchete correspondente no nosso corpus de 205.697;",
        "medir a concordância entre o especialista e o nosso modelo — F1 por classe e "
        "kappa;",
        "**sem usar o preço como critério.**",
    ])

    A.paragrafo(doc,
        "**O que isto entrega:** um conjunto-ouro construído por leitores profissionais, "
        "que é o que faltava ao nosso. E responde à objeção do especialista que já nos "
        "foi feita, porque desta vez o julgamento não é meu.")

    A.paragrafo(doc,
        "**O risco:** o casamento entre a análise e a manchete é trabalhoso e o "
        "rendimento tende a ser baixo. **Convém estimar em uma amostra de trinta casos "
        "antes de escalar.**")

    A.secao(doc, "6.3", "E3 — A notícia move o preço?", nivel=2)

    A.paragrafo(doc,
        "**Pergunta:** as notícias que os especialistas destacam como relevantes movem "
        "o preço mais que uma notícia qualquer?")

    A.paragrafo(doc, "**Protocolo:** estudo de evento clássico — janela em torno da "
        "data, retorno anormal e volatilidade anormal, contra uma amostra de controle "
        "de notícias não destacadas.")

    A.paragrafo(doc,
        "**A previsão que faço, e que convém registrar antes de rodar:** o efeito "
        "aparecerá **concentrado em poucos eventos**, não distribuído. Se isso se "
        "confirmar, é a **quarta** confirmação independente do efeito de cauda — e desta "
        "vez com eventos escolhidos por profissionais, não por um critério estatístico "
        "meu.")

    # ── 7 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "7", "Riscos, ditos antes e não depois")

    A.tabela_abnt(doc, "3", "O que pode dar errado",
        ["Risco", "Gravidade", "Como tratar"],
        [
            ["Amostra rala — especialistas publicam poucas vezes por mês, não por dia",
             "ALTA",
             "abandonar a frequência diária; trabalhar em base mensal, que é o nosso "
             "melhor horizonte de todo modo"],
            ["Viés de seleção — analista escreve mais quando há notícia grande",
             "ALTA", "declarar como limitação; comparar sempre contra amostra de "
             "controle, nunca contra o conjunto todo"],
            ["Arquivo histórico incompleto ou reescrito",
             "MÉDIA", "registrar a data de coleta e guardar o HTML bruto"],
            ["Termos de uso e robots.txt", "MÉDIA",
             "respeitar; onde houver bloqueio, amostra manual ou acesso institucional"],
            ["Chamada sem horizonte declarado — “vai subir”, mas quando?",
             "MÉDIA", "fixar horizonte por convenção e testar sensibilidade em 1, 5 e "
             "22 pregões"],
            ["O especialista errar muito e o resultado parecer deboche",
             "BAIXA", "é achado, não deboche. Apresentar com o número da literatura ao "
             "lado e sem adjetivo"],
        ], fonte=FONTE)

    # ── 8 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "8", "O que recomendo")

    A.lista(doc, [
        "**Perguntar à PUCPR sobre Economatica ou Refinitiv.** Uma pergunta; muda tudo "
        "se a resposta for sim.",
        "**Fazer o E1 primeiro**, com as carteiras mensais. É o de melhor relação entre "
        "valor e risco, e rende nos dois desfechos possíveis.",
        "**Fazer uma sondagem de trinta casos do E2** antes de decidir se escala.",
        "**Deixar o E3 por último** — depende do E2 estar de pé.",
        "**Não usar o preço para validar rótulo**, em nenhum dos três.",
    ])

    A.paragrafo(doc,
        "**E uma observação de método que convém dizer aos professores:** o pedido, "
        "como formulado, tem dentro de si um experimento excelente e uma armadilha "
        "metodológica. Separar os dois **antes** de coletar dado é mais barato que "
        "descobrir depois — e é o tipo de cuidado que a banca reconhece.")

    doc.save(SAIDA)
    print(f"[OK] {SAIDA}")


if __name__ == "__main__":
    main()
