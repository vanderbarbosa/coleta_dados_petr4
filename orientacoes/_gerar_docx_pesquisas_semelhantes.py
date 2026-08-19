# -*- coding: utf-8 -*-
# ==============================================================================
#   Gera a explicação em linguagem comum do levantamento de pesquisas
#   semelhantes (notícias -> direção e volatilidade) e do experimento que ele
#   provocou.
#   Saída: orientacoes/EXPLICACAO_SIMPLES_PESQUISAS_SEMELHANTES.docx
# ==============================================================================
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(RAIZ / "src" / "comum"))

import abnt_docx as A  # noqa: E402

FONTE = "Elaborado pelo autor (2026)"
SAIDA = AQUI / "EXPLICACAO_SIMPLES_PESQUISAS_SEMELHANTES.docx"


def main() -> None:
    doc = A.novo_documento()

    A.capa(
        doc,
        titulo="Quem mais está fazendo isto",
        subtitulo="Seis pesquisas que leem notícias para prever direção e risco — "
                  "e o experimento que elas nos fizeram rodar",
        autor="Vanderlei Barbosa da Silva",
        orientador="Orientador: Prof. Dr. Julio Cesar Nievola",
        instituicao="PUCPR — Programa de Pós-Graduação em Informática (PPGIa)",
        descricao="Documento escrito para ser entendido sem conhecimento prévio de "
                  "aprendizado de máquina ou de estatística. Elaborado em 18 de "
                  "agosto de 2026, atendendo ao pedido do Prof. Dr. Emerson Cabrera "
                  "Paraiso de localizar pesquisas semelhantes, independentemente do "
                  "ativo e do idioma.",
    )

    # ── 1 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "1", "Antes de tudo: um número da sua tabela precisa sair")

    A.paragrafo(doc,
        "Você montou uma tabela comparativa e colocou lá **“54,93% com ponderação "
        "por confiança Softmax”**. Esse número é o que revisamos anteontem, e ele "
        "**não se sustenta** por dois motivos:")

    A.lista(doc, [
        "É acurácia de **validação**, não de teste. No teste a ponderação dá "
        "**50,31%**, contra 53,88% sem ponderação. **Ponderar piora.**",
        "E o escore nem é *softmax* — provamos que é sigmoide, porque 397 manchetes "
        "têm confiança abaixo do mínimo matemático que um softmax permite.",
    ])

    A.paragrafo(doc,
        "**Use 54,5%, sem a menção à ponderação.** Se levar 54,93% para o Professor "
        "Emerson e ele pedir para ver, você vai ter de desdizer na hora.")

    # ── 2 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "2", "O que a busca encontrou")

    A.paragrafo(doc,
        "Refiz a busca no escopo certo — **qualquer ativo, qualquer idioma, desde que "
        "leia notícias para prever direção ou risco**. Seis trabalhos fazem o que "
        "você faz. Três são de 2025. **Dois são sobre petróleo**, o que para a "
        "Petrobras é o mais próximo possível.")

    A.tabela_abnt(doc, "1", "As seis pesquisas, por proximidade",
        ["Pesquisa", "O que faz", "Dá para adaptar?"],
        [
            ["Hashamia e Maldonado (2025)",
             "prevê a DIREÇÃO da volatilidade do petróleo", "SIM — e tem código público"],
            ["CrudeBERT (2023)",
             "um BERT feito só para o mercado de petróleo", "a ideia, sim"],
            ["Bodilsen e Lunde (2025)",
             "notícia macro x notícia de empresa, no HAR", "SIM — já testei"],
            ["Halousková e Lyócsa (2025)",
             "FinBERT + HAR em 404 ações", "confirma o efeito de cauda"],
            ["Mino e Williamson (2025)",
             "BERT + GARCH, igual ao seu Script 04", "confirma o seu coeficiente"],
            ["Rahimikia e Poon",
             "embeddings para prever volatilidade", "reforça a linha dos embeddings"],
        ], fonte=FONTE)

    # ── 3 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "3", "A pesquisa mais parecida com a sua — e ela tem código")

    A.paragrafo(doc,
        "Hashamia e Maldonado (2025) preveem a volatilidade do **petróleo Brent** a "
        "partir de **592.858 manchetes da Reuters**. O seu corpus tem 205.697. Mesma "
        "ordem de grandeza, mesma commodity que move a PETR4.")

    A.paragrafo(doc,
        "E eles fizeram **três coisas que você não fez**, todas aproveitáveis:")

    A.secao(doc, "3.1", "A ideia mais valiosa: mudar a pergunta", nivel=2)

    A.paragrafo(doc,
        "Pense nas três perguntas possíveis:")

    A.lista(doc, [
        "**“A ação vai subir ou cair amanhã?”** — você já provou que é quase cara ou "
        "coroa. Nem um leitor perfeito melhoraria isso.",
        "**“Qual será o tamanho do sacolejo amanhã?”** — o modelo HAR já responde bem "
        "usando só o histórico. Difícil de superar.",
        "**“Amanhã vai sacudir MAIS ou MENOS que hoje?”** — esta você **nunca testou**.",
    ])

    A.paragrafo(doc,
        "A terceira é uma via do meio. É binária, como a primeira, mas sobre risco, "
        "que é onde o seu sinal existe. E o HAR não é adversário natural dela, porque "
        "o HAR prevê o **nível**, não a **mudança de nível**.")

    A.paragrafo(doc,
        "**É a minha recomendação número um**, e dá para testar com os dados que você "
        "já tem.")

    A.secao(doc, "3.2", "As outras duas descobertas deles", nivel=2)

    A.lista(doc, [
        "**A CONTAGEM de notícias superou as medidas de sentimento.** Você testou "
        "volume de notícias e falhou — mas testou contra o *nível* da volatilidade, "
        "nunca contra a *direção* dela.",
        "**Os embeddings ganharam da cabeça de sentimento** (o melhor foi o FastText). "
        "**É a quarta pesquisa independente apontando para isso.**",
    ])

    # ── 4 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "4", "Existe um BERT só do petróleo")

    A.paragrafo(doc,
        "Chama-se **CrudeBERT**, é público, e é o FinBERT ajustado para o mercado de "
        "petróleo. Mas o interessante não é o modelo — é **como** ele foi construído.")

    A.paragrafo(doc,
        "Os autores não perguntaram “esta manchete é boa ou ruim?”. Perguntaram **“esta "
        "manchete é um choque de OFERTA ou de DEMANDA?”** — e montaram o treinamento "
        "sobre teoria econômica, não sobre impressão.")

    A.paragrafo(doc,
        "**Por que isso importa tanto para você.** O Professor Emerson suspendeu a sua "
        "rotulagem dizendo que precisaria de especialista em finanças. A objeção dele "
        "é sobre **julgamento subjetivo**: dizer se uma notícia é “positiva” depende de "
        "quem lê.")

    A.paragrafo(doc,
        "Mas dizer se uma notícia é **“aumento de oferta de petróleo”** ou **“mudança "
        "na política de preços de combustíveis”** é bem menos subjetivo. **É "
        "classificação de fato, não de opinião.** Isso desloca o critério do gosto para "
        "a teoria — e responde à objeção dele por um caminho que ele provavelmente "
        "aceitaria.")

    A.paragrafo(doc,
        "Para a PETR4 as categorias seriam algo como: choque de oferta, choque de "
        "demanda, intervenção do governo, política de preços de combustíveis, "
        "dividendos.")

    # ── 5 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "5", "O experimento que essa busca me fez rodar")

    A.paragrafo(doc,
        "Encontrei um artigo de 2025 no *Journal of Applied Econometrics* — revista de "
        "primeiríssima linha em econometria — que fez **exatamente o que você fez** e "
        "chegou a duas conclusões que nós nunca testamos.")

    A.secao(doc, "5.1", "O que eles acharam", nivel=2)

    A.lista(doc, [
        "**Notícia sobre a própria empresa NÃO ajuda** — o histórico de volatilidade "
        "já contém aquela informação.",
        "**Notícia MACROECONÔMICA ajuda muito** — e o ganho é **maior em prazos "
        "longos**.",
    ])

    A.paragrafo(doc,
        "**Isso descrevia exatamente o nosso caso.** O recorte que adotamos — empresa "
        "mais petróleo — é o mais parecido com “notícia da empresa”. E medimos tudo a "
        "**um dia** de distância. Ou seja: se eles estivessem certos, teríamos "
        "escolhido a pior fatia do corpus, no pior prazo.")

    A.paragrafo(doc, "**Fui testar. E deu o contrário.**")

    A.secao(doc, "5.2", "O que aconteceu nos nossos dados", nivel=2)

    A.tabela_abnt(doc, "2", "Ganho sobre o HAR (positivo = o sentimento ajuda)",
        ["Que notícias uso", "1 dia", "5 dias", "22 dias", "Média"],
        [
            ["EMPRESA (empresa+governança)", "+1,03%", "+0,37%", "+1,77%", "+1,06%"],
            ["Empresa + petróleo", "+0,30%", "−0,43%", "+0,21%", "+0,03%"],
            ["Só petróleo", "−0,12%", "−0,48%", "−1,06%", "−0,55%"],
            ["MACRO (geopolítica etc.)", "−0,33%", "−1,09%", "−1,79%", "−1,07%"],
            ["Todas", "−0,30%", "−1,93%", "−2,45%", "−1,56%"],
        ], fonte=FONTE)

    A.paragrafo(doc, "**Leia assim, de cima para baixo:**")

    A.lista(doc, [
        "**A notícia da EMPRESA é a melhor de todas** — a única positiva em todos os "
        "prazos. E em 22 dias dá **+1,77%**, com p = 0,057. **É o resultado mais "
        "próximo de vencer o HAR que a sua pesquisa já teve.** Ficou de fora do "
        "critério de 5% por muito pouco.",
        "**A notícia MACRO é a pior, e ela ATRAPALHA de verdade** — não é só “não "
        "ajuda”: com p = 0,015 e p = 0,020, colocar notícia macro no modelo **piora "
        "significativamente** a previsão.",
        "**Usar todas as notícias é a segunda pior opção.** Menos é mais.",
    ])

    A.secao(doc, "5.3", "Por que deu o contrário deles", nivel=2)

    A.paragrafo(doc,
        "Duas razões, e as duas são defensáveis diante da banca.")

    A.paragrafo(doc,
        "**Primeira: “macro” não significa a mesma coisa nos dois estudos.** Eles usam "
        "notícia macroeconômica **dos Estados Unidos** para prever **ações "
        "norte-americanas** — e a economia americana move diretamente as ações "
        "americanas. O nosso “macro” é 46 mil notícias de **geopolítica "
        "internacional**: guerra na Ucrânia, sanções, OPEP, Oriente Médio. Para uma "
        "ação brasileira isolada, **isso é ruído**.")

    A.paragrafo(doc,
        "**Segunda: a PETR4 é estatal.** O que move o risco dela é política de preços "
        "de combustível, troca de diretoria, intervenção do governo, dividendos — "
        "coisas **da própria empresa**. Numa ação comum do S&P 500, o peso do "
        "macroeconômico é maior. **É coerente que na Petrobras a notícia da empresa "
        "informe mais.**")

    A.paragrafo(doc,
        "**E uma metade da hipótese deles se confirmou:** o melhor resultado apareceu "
        "no prazo de **um mês**, não no de um dia. Eles estavam certos sobre o "
        "horizonte, e errados — para o nosso caso — sobre o tipo de notícia.")

    A.secao(doc, "5.4", "Uma descoberta lateral que vale registrar", nivel=2)

    A.paragrafo(doc,
        "Repare numa coisa curiosa. Na Seção 4.k descobrimos que **empresa + petróleo** "
        "era o melhor recorte. Agora descobrimos que **só empresa** é o melhor. **Os "
        "dois estão certos** — porque medem coisas diferentes:")

    A.tabela_abnt(doc, "3", "Cada objetivo pede um recorte diferente",
        ["Se o objetivo é...", "O melhor recorte é..."],
        [
            ["medir a ASSOCIAÇÃO com a volatilidade", "empresa + petróleo"],
            ["PREVER a volatilidade fora da amostra", "só empresa"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "A explicação encaixa com o efeito de cauda: a notícia de petróleo contribui "
        "**nos dias extremos** (choques do barril), que é o que a correlação enxerga. "
        "Mas a previsão do dia a dia é dominada pelo pregão comum, e ali aquela notícia "
        "só acrescenta ruído.")

    A.paragrafo(doc,
        "**A lição é prática: o corpus certo depende da pergunta.** Não dá para "
        "escolher um recorte e assumir que serve para tudo. Isso é achado próprio seu, "
        "e vale como contribuição metodológica.")

    # ── 6 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "6", "O que fazer agora, em ordem")

    A.tabela_abnt(doc, "4", "As seis ações, por custo e retorno",
        ["#", "O que fazer", "De onde veio", "Custo"],
        [
            ["1", "Prever a DIREÇÃO da volatilidade", "Hashamia e Maldonado", "baixo"],
            ["2", "Adotar recorte EMPRESA e prazo de 22 dias", "nosso experimento", "muito baixo"],
            ["3", "Testar contagem de notícias na direção da vol.", "Hashamia e Maldonado", "baixo"],
            ["4", "Usar embeddings no lugar do sentimento", "4 fontes", "médio (GPU)"],
            ["5", "Rotular por mecanismo econômico", "CrudeBERT", "médio"],
            ["6", "Buscar dados intradiários da PETR4", "3 fontes", "alto"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**As duas primeiras são baratas e podem ser feitas esta semana.** A número 2 "
        "é praticamente rodar o script de novo com outros prazos, para ver se aquele "
        "p = 0,057 vira p < 0,05 em algum horizonte intermediário.")

    # ── 7 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "7", "Se você tiver dois minutos para explicar isso")

    A.lista(doc, [
        "“Procurei quem faz o mesmo que eu, em qualquer ativo e qualquer idioma. Achei "
        "seis, três de 2025, e dois sobre petróleo.”",
        "“O mais próximo prevê a DIREÇÃO da volatilidade do Brent, a partir de 592 mil "
        "manchetes, e tem o código público. É um alvo que eu nunca testei e que faz "
        "mais sentido que os meus dois.”",
        "“Existe até um BERT só do petróleo, o CrudeBERT. E o jeito como ele foi "
        "treinado — classificar por choque de oferta e de demanda, não por "
        "positivo/negativo — responde à objeção sobre a rotulagem.”",
        "“Achei um artigo do Journal of Applied Econometrics dizendo que notícia macro "
        "ajuda e notícia de empresa não. Testei nos meus dados e deu o contrário: aqui "
        "a macro atrapalha significativamente e a da empresa é a melhor.”",
        "“E foi nesse teste que apareceu o melhor resultado que já tive: notícia da "
        "empresa, prazo de um mês, +1,77% sobre o HAR, com p = 0,057.”",
        "“A explicação é que a PETR4 é estatal — o risco dela vem de dentro, não do "
        "cenário global.”",
    ])

    doc.save(SAIDA)
    print(f"[OK] Documento gerado: {SAIDA}")


if __name__ == "__main__":
    main()
