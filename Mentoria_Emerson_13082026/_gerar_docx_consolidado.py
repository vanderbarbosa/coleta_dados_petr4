# -*- coding: utf-8 -*-
# ==============================================================================
#   Documento consolidado para leigos — mentoria com o Prof. Emerson
#   Saída: Mentoria_Emerson_13082026/02_EXPLICACAO_PARA_LEIGOS.docx
#
#   Este é o documento de ABERTURA da pasta. Os documentos detalhados de cada
#   assunto ficam em documentos_para_leigos/.
# ==============================================================================
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(RAIZ / "src" / "comum"))

import abnt_docx as A  # noqa: E402

FONTE = "Elaborado pelo autor (2026)"
SAIDA = AQUI / "02_EXPLICACAO_PARA_LEIGOS.docx"


def main() -> None:
    doc = A.novo_documento()

    A.capa(
        doc,
        titulo="O que encontrei, em linguagem comum",
        subtitulo="Vinte e cinco pesquisas, cinco descobertas e doze coisas a fazer",
        autor="Vanderlei Barbosa da Silva",
        orientador="Orientador: Prof. Dr. Julio Cesar Nievola",
        instituicao="PUCPR — Programa de Pós-Graduação em Informática (PPGIa)",
        descricao="Documento de abertura da pasta da mentoria com o Prof. Dr. Emerson "
                  "Cabrera Paraiso. Escrito para ser entendido sem conhecimento prévio "
                  "de aprendizado de máquina ou de estatística: todo termo técnico é "
                  "explicado com analogia quando aparece pela primeira vez. Os "
                  "documentos detalhados de cada assunto estão na subpasta "
                  "documentos_para_leigos.",
    )

    # ── 1 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "1", "O que foi pedido e o que foi feito")

    A.paragrafo(doc,
        "O Professor Emerson pediu para eu procurar **outras pesquisas que fazem o "
        "mesmo que a minha** — ler notícias e tentar prever a direção do preço e o "
        "risco que essas notícias causam —, **independentemente do ativo e do "
        "idioma**. E saber se dá para usar ou adaptar essas pesquisas para melhorar "
        "os meus resultados.")

    A.paragrafo(doc,
        "Encontrei **vinte e cinco pesquisas relevantes**. Estão todas na planilha "
        "comparativa que acompanha esta pasta, com autor, ano, idioma, mercado, "
        "volume de notícias, tecnologia usada, resultado e — o que mais importa — "
        "**como cada uma pode ser usada na minha pesquisa**.")

    A.paragrafo(doc,
        "Mais do que isso: **duas dessas pesquisas me fizeram rodar experimentos "
        "novos**, e um deles produziu o melhor resultado que a minha pesquisa já "
        "teve.")

    # ── 2 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "2", "Antes de tudo: dois conceitos")

    A.secao(doc, "2.1", "O que é um encoder", nivel=2)

    A.paragrafo(doc,
        "Pense num **funcionário que você contrata para ler notícias**. Ele tem duas "
        "partes:")

    A.lista(doc, [
        "**A compreensão** — ele leu milhões de textos financeiros e formou um "
        "entendimento profundo do assunto. Sabe que “alavancagem” não tem a ver com "
        "alavancas.",
        "**O parecer** — ele resume tudo isso numa palavra só: positivo, negativo ou "
        "neutro.",
    ])

    A.paragrafo(doc,
        "**Encoder** é o nome técnico desse funcionário. O que eu uso chama-se "
        "**FinBERT-PT-BR**, feito para português.")

    A.secao(doc, "2.2", "Direção e volatilidade não são a mesma coisa", nivel=2)

    A.paragrafo(doc,
        "**Direção** é para onde o preço vai — sobe ou desce. **Volatilidade** é o "
        "tamanho do sacolejo, independentemente do lado. Um dia que sobe 5% e um que "
        "cai 5% têm a **mesma** volatilidade, alta.")

    A.paragrafo(doc,
        "Essa distinção é o eixo de tudo. **A direção é praticamente imprevisível** — "
        "eu provei isso, mostrando que nem um leitor perfeito melhoraria. **A esperança "
        "sempre esteve na volatilidade**, que é o que interessa a quem gere risco.")

    # ── 3 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "3", "Descoberta 1 — o meu 0,58 é normal, não é fracasso")

    A.paragrafo(doc,
        "O meu modelo acerta **58 de cada 100** manchetes quando comparado ao meu "
        "julgamento. Passei meses tratando isso como um problema a consertar, e nove "
        "tentativas de conserto falharam.")

    A.paragrafo(doc, "**Não era um problema.**")

    A.tabela_abnt(doc, "1", "O mesmo teste, em inglês e em português",
        ["Modelo", "Situação", "Acerto (F1)"],
        [
            ["FinBERT inglês", "manchetes de um setor, sem ajuste", "0,555"],
            ["FinBERT-PT-BR (o meu)", "manchetes da PETR4, sem ajuste", "0,579"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "O modelo inglês — treinado com **bilhões** de palavras, com 4,5 milhões de "
        "downloads por mês, publicado em revista de primeira linha — obtém **0,555** "
        "na mesma situação. **O meu obtém 0,579. É melhor.**")

    A.paragrafo(doc,
        "Isso significa que o teto de 0,58 **não é culpa do português, nem do modelo "
        "brasileiro, nem de uma escolha errada minha**. É o que acontece com qualquer "
        "modelo desse tipo aplicado a um recorte específico sem treinamento adicional. "
        "**É o comportamento esperado.**")

    # ── 4 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "4", "Descoberta 2 — o efeito é de cauda, e o mundo concorda")

    A.paragrafo(doc,
        "A minha descoberta mais importante é que **o sentimento das notícias não move "
        "o pregão comum — ele importa nos dias extremos.**")

    A.paragrafo(doc,
        "Cheguei nisso por dois caminhos internos. A regressão quantílica mostrou "
        "efeito forte nos 5% piores dias e **zero** nos dias normais. E a comparação "
        "entre duas formas de medir correlação mostrou a mesma coisa: uma delas, que "
        "leva em conta o tamanho dos números, encontra a relação; a outra, que só olha "
        "a ordem, não encontra.")

    A.paragrafo(doc,
        "**E agora tenho confirmação de fora.** Halousková e Lyócsa (2025) fizeram o "
        "mesmo que eu — mas com **404 ações americanas** e dados de 5 em 5 minutos. O "
        "ganho deles é maior justamente **nos dias de variação extrema**: 14,99% contra "
        "12,74% na média.")

    A.paragrafo(doc,
        "**Cheguei ao mesmo lugar com uma ação brasileira e dados diários.** Quando "
        "duas pesquisas independentes chegam ao mesmo resultado por caminhos "
        "diferentes, aquilo deixa de ser “uma coisa que eu achei” e vira **um fato do "
        "fenômeno**.")

    # ── 5 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "5", "Descoberta 3 — os números altos da literatura não resistem")

    A.paragrafo(doc,
        "A minha tabela comparativa mostrava outras pesquisas com 86,7%, 83,6% e "
        "71,2%, ao lado dos meus 54,5%. Fui conferir os três na fonte.")

    A.tabela_abnt(doc, "2", "O que esses números realmente são",
        ["Pesquisa", "O número", "O que ele realmente é"],
        [
            ["Bollen (2011)", "86,7%", "13 acertos em 15 pregões — e foi REFUTADO"],
            ["Schumaker (2009)", "71,2%", "preço 20 MINUTOS após a notícia, não o dia seguinte"],
            ["Barak (2017)", "83,6%", "outro mercado e tarefa — e eu já testei: não funcionou"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**O caso do Bollen é o mais eloquente.** É o artigo mais citado da área e "
        "virou até fundo de investimento. Os 86,7% são **treze acertos em quinze "
        "dias** — o meu conjunto de teste tem 497 pregões. E em 2017, Lachanski e Pav "
        "refizeram a análise, estenderam os dados e **não encontraram nada**, "
        "atribuindo o resultado original a “garimpagem de dados”.")

    A.paragrafo(doc,
        "**Isso muda a minha defesa.** Se alguém disser “mas o Bollen conseguiu "
        "86,7%”, eu respondo com a referência da refutação.")

    # ── 6 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "6", "Descoberta 4 — o melhor resultado que já tive")

    A.paragrafo(doc,
        "Aqui a busca deixou de ser leitura e virou experimento.")

    A.paragrafo(doc,
        "Encontrei um artigo de 2025 no *Journal of Applied Econometrics*, revista de "
        "primeiríssima linha, que fez **exatamente o que eu faço** e chegou a duas "
        "conclusões que eu nunca tinha testado:")

    A.lista(doc, [
        "**Notícia sobre a própria empresa NÃO ajuda** — o histórico de volatilidade "
        "já contém aquilo.",
        "**Notícia MACROECONÔMICA ajuda muito** — e mais ainda em **prazos longos**.",
    ])

    A.paragrafo(doc,
        "Isso descrevia o meu caso com precisão: eu uso principalmente notícia ligada "
        "à empresa, e medi tudo a **um dia** de distância. Se eles estivessem certos, "
        "eu teria escolhido a pior fatia do corpus, no pior prazo. **Fui testar.**")

    A.tabela_abnt(doc, "3", "Ganho sobre o modelo padrão (positivo = ajuda)",
        ["Que notícias eu uso", "1 dia", "5 dias", "22 dias", "Média"],
        [
            ["EMPRESA", "+1,03%", "+0,37%", "+1,77%", "+1,06%"],
            ["Empresa + petróleo", "+0,30%", "−0,43%", "+0,21%", "+0,03%"],
            ["Só petróleo", "−0,12%", "−0,48%", "−1,06%", "−0,55%"],
            ["MACRO (geopolítica)", "−0,33%", "−1,09%", "−1,79%", "−1,07%"],
            ["Todas", "−0,30%", "−1,93%", "−2,45%", "−1,56%"],
        ], fonte=FONTE)

    A.paragrafo(doc, "**Deu o contrário — e de forma clara.**")

    A.lista(doc, [
        "**A notícia da EMPRESA é a melhor de todas.** Em 22 dias dá **+1,77%**. "
        "**É o resultado mais próximo de vencer o modelo padrão que a minha pesquisa "
        "já teve** — ficou de fora do critério estatístico por muito pouco.",
        "**A notícia MACRO não é só inútil: ela ATRAPALHA de verdade**, e isso é "
        "estatisticamente comprovado nos dois prazos mais longos.",
        "**Usar todas as notícias é quase a pior opção.** Menos é mais.",
    ])

    A.paragrafo(doc,
        "**E por que deu o contrário deles?** Duas razões, e as duas são defensáveis. "
        "Primeiro, o “macro” deles é a economia **dos Estados Unidos** aplicada a ações "
        "**americanas** — que se movem com ela. O meu “macro” são 46 mil notícias de "
        "**geopolítica internacional**: Ucrânia, sanções, OPEP. Para uma ação "
        "brasileira isolada, **isso é ruído**.")

    A.paragrafo(doc,
        "Segundo, e mais importante: **a Petrobras é estatal.** O que mexe com o risco "
        "dela é preço de combustível, troca de diretoria, intervenção do governo, "
        "dividendos — coisas **de dentro da empresa**. É coerente que a notícia da "
        "empresa informe mais.")

    A.paragrafo(doc,
        "**E uma metade da hipótese deles se confirmou:** o melhor resultado apareceu "
        "no prazo de um mês, não no de um dia.")

    # ── 7 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "7", "Descoberta 5 — existe um caminho que nunca tentei")

    A.paragrafo(doc,
        "A pesquisa mais parecida com a minha que encontrei é sobre **petróleo Brent**, "
        "usa **592.858 manchetes da Reuters**, e **tem o código público**. O meu corpus "
        "tem 205.697 manchetes — mesma ordem de grandeza, e o petróleo é justamente o "
        "que move a PETR4.")

    A.paragrafo(doc,
        "E eles fazem uma pergunta que eu **nunca fiz**. Compare as três:")

    A.lista(doc, [
        "**“A ação sobe ou cai amanhã?”** — quase cara ou coroa. Já provei que não dá.",
        "**“Qual o tamanho do sacolejo amanhã?”** — o modelo padrão já responde bem "
        "usando só o histórico. Difícil de superar.",
        "**“Amanhã vai sacudir MAIS ou MENOS que hoje?”** — **esta eu nunca testei.**",
    ])

    A.paragrafo(doc,
        "A terceira é uma via do meio: é uma pergunta de sim ou não, como a primeira, "
        "mas sobre **risco**, que é onde o meu sinal existe. E o modelo padrão não é "
        "adversário natural dela, porque ele prevê o **nível** do sacolejo, não a "
        "**mudança** de nível.")

    A.paragrafo(doc,
        "**É a minha recomendação número um**, e dá para testar com os dados que já "
        "tenho.")

    A.secao(doc, "7.1", "E existe um BERT só do petróleo", nivel=2)

    A.paragrafo(doc,
        "Chama-se **CrudeBERT**. O interessante não é o modelo — é **como** foi "
        "construído. Os autores não perguntaram “esta manchete é boa ou ruim?”. "
        "Perguntaram **“esta manchete é um choque de OFERTA ou de DEMANDA?”**")

    A.paragrafo(doc,
        "**Por que isso importa para a objeção do Professor Emerson.** Ele suspendeu a "
        "minha rotulagem dizendo que precisaria de especialista em finanças. A "
        "preocupação dele é com **julgamento subjetivo** — dizer se uma notícia é "
        "“positiva” depende de quem lê.")

    A.paragrafo(doc,
        "Mas dizer se uma notícia é **“aumento de oferta de petróleo”** ou **“mudança "
        "na política de preços de combustíveis”** é bem menos subjetivo. **É "
        "classificação de fato, não de opinião.** Isso desloca o critério do gosto "
        "pessoal para a teoria econômica — e responde à objeção dele por um caminho "
        "que ele provavelmente aceitaria.")

    # ── 8 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "8", "O que preciso corrigir antes de apresentar")

    A.paragrafo(doc,
        "Duas coisas, e é melhor eu mesmo levantá-las do que ser corrigido:")

    A.paragrafo(doc,
        "**Primeira: o número 54,93%.** Ele circula na minha tabela como “acurácia com "
        "ponderação por confiança”. **Não se sustenta.** É um número de **validação**, "
        "não de teste — e validação é onde a gente escolhe entre várias opções, então "
        "o melhor resultado ali costuma ser sorte. No teste de verdade, ponderar dá "
        "**50,31%**, contra 53,88% sem ponderar. **Ponderar piora.** O número correto "
        "é **54,5%**.")

    A.paragrafo(doc,
        "**Segunda: a comparação com quem acerta 86,7%.** Como expliquei na seção 5, "
        "aqueles números não medem a mesma coisa que os meus. Levo a explicação pronta, "
        "com as referências.")

    # ── 9 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "9", "O que fazer agora")

    A.paragrafo(doc,
        "A planilha traz doze ações ordenadas por custo e retorno. As quatro "
        "primeiras:")

    A.tabela_abnt(doc, "4", "As ações mais baratas e de maior retorno",
        ["#", "O que fazer", "Custo"],
        [
            ["1", "Prever a DIREÇÃO da volatilidade (mais ou menos que hoje)", "baixo"],
            ["2", "Adotar o recorte EMPRESA e testar prazos de 10 a 30 dias", "muito baixo"],
            ["3", "Testar a contagem de notícias contra esse novo alvo", "baixo"],
            ["4", "Normalizar as manchetes em CAIXA ALTA para minúsculas", "baixo"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**A número 2 é praticamente rodar o mesmo script com outros prazos**, para ver "
        "se aquele resultado que ficou perto do limiar estatístico o cruza em algum "
        "horizonte intermediário.")

    # ── 10 ───────────────────────────────────────────────────────────────────
    A.secao(doc, "10", "O que dizer ao Professor Emerson, em dois minutos")

    A.lista(doc, [
        "“Procurei quem faz o mesmo que eu, em qualquer ativo e qualquer idioma. Achei "
        "vinte e cinco pesquisas. Estão numa planilha comparativa.”",
        "“Descobri que o meu 0,58 é normal: o FinBERT inglês dá 0,555 na mesma "
        "situação. O meu é melhor. Não é problema do português.”",
        "“A minha descoberta do efeito de cauda foi confirmada de fora, por um estudo "
        "com 404 ações americanas.”",
        "“Os números altos da literatura não resistem a exame. O 86,7% do Bollen são "
        "13 acertos em 15 dias e foram refutados em 2017.”",
        "“Testei a hipótese de um artigo do Journal of Applied Econometrics nos meus "
        "dados e deu o contrário — e foi aí que apareceu o melhor resultado que já "
        "tive: notícia da empresa, prazo de um mês.”",
        "“E encontrei um caminho novo: prever a DIREÇÃO da volatilidade, em vez do "
        "nível. É uma pergunta que eu nunca fiz, e tem pesquisa com código público "
        "sobre petróleo mostrando que funciona.”",
    ])

    doc.save(SAIDA)
    print(f"[OK] Documento gerado: {SAIDA}")


if __name__ == "__main__":
    main()
