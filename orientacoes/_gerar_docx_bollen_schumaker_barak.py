# -*- coding: utf-8 -*-
# ==============================================================================
#   Gera a explicação em linguagem comum sobre os 80%+ de Bollen, Schumaker
#   e Barak — por que não são comparáveis e o que se pode aproveitar deles.
#   Saída: orientacoes/EXPLICACAO_SIMPLES_OS_80_PORCENTO.docx
# ==============================================================================
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(RAIZ / "src" / "comum"))

import abnt_docx as A  # noqa: E402

FONTE = "Elaborado pelo autor (2026)"
SAIDA = AQUI / "EXPLICACAO_SIMPLES_OS_80_PORCENTO.docx"


def main() -> None:
    doc = A.novo_documento()

    A.capa(
        doc,
        titulo="Os 86,7% que não existem",
        subtitulo="Por que Bollen, Schumaker e Barak reportam mais de 70% — "
                  "e o que realmente dá para aproveitar deles",
        autor="Vanderlei Barbosa da Silva",
        orientador="Orientador: Prof. Dr. Julio Cesar Nievola",
        instituicao="PUCPR — Programa de Pós-Graduação em Informática (PPGIa)",
        descricao="Documento escrito para ser entendido sem conhecimento prévio de "
                  "aprendizado de máquina ou de estatística. Elaborado em 18 de "
                  "agosto de 2026, a partir da conferência dos três trabalhos "
                  "citados na tabela comparativa do Capítulo 4.",
    )

    # ── 1 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "1", "A sua pergunta era certeira")

    A.paragrafo(doc,
        "Você olhou a tabela comparativa da sua dissertação, viu **86,7%**, "
        "**83,6%** e **71,2%** ao lado dos seus **54,5%**, e perguntou por que eu "
        "nunca tinha mostrado isso e por que não dá para usar essas pesquisas.")

    A.paragrafo(doc,
        "**A pergunta estava certa e eu devia ter chegado nela antes.** Fui conferir "
        "os três, um por um, na fonte. E o que encontrei **melhora a sua posição**, "
        "não piora.")

    A.paragrafo(doc,
        "O resumo é este: dois dos três números não medem o que parece medir, e um "
        "deles **foi refutado publicamente** por outros pesquisadores. O terceiro nós "
        "já testamos e não funcionou. Mas há **duas ideias boas** nesses trabalhos — "
        "só que não são as acurácias.")

    # ── 2 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "2", "Primeiro: por que eu não tinha trazido isso")

    A.paragrafo(doc,
        "Resposta honesta: **por causa do recorte que o Professor Emerson pediu.** "
        "Ele mandou procurar BERTs financeiros em inglês e os artigos que os citam.")

    A.paragrafo(doc,
        "Esses três trabalhos **são anteriores ao BERT**. O BERT surgiu em 2018. "
        "Bollen é de 2011, Schumaker de 2009, Barak de 2017 — e nenhum usa "
        "transformers:")

    A.lista(doc, [
        "**Bollen** usou dicionários de palavras (OpinionFinder e GPOMS).",
        "**Schumaker** usou saco-de-palavras com máquina de vetores de suporte.",
        "**Barak** trabalhou com indicadores de mercado, não com texto.",
    ])

    A.paragrafo(doc,
        "Por isso nunca apareceram numa busca por “quem usa o FinBERT”. **E eles já "
        "estão na sua dissertação** — na tabela do Capítulo 4 e no referencial "
        "teórico. Não são novidade; são o seu próprio material.")

    # ── 3 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "3", "Bollen: os 86,7% são 13 acertos em 15 dias")

    A.paragrafo(doc,
        "Este é o artigo mais famoso da área inteira. Chegou a virar fundo de "
        "investimento. E o número dele é bem mais frágil do que aparenta.")

    A.secao(doc, "3.1", "O que ele realmente fez", nivel=2)

    A.tabela_abnt(doc, "1", "A base empírica dos 86,7%",
        ["Item", "Detalhe"],
        [
            ["Treinou com", "28/02/2008 a 28/11/2008"],
            ["Testou em", "01/12/2008 a 19/12/2008"],
            ["Total de pregões no teste", "15"],
            ["Acertos", "13"],
            ["13 ÷ 15", "86,7%"],
            ["Alvo", "índice Dow Jones (não uma ação)"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**O número mais citado da área é treze acertos em quinze dias.**")

    A.paragrafo(doc,
        "Ponha em perspectiva: o seu conjunto de teste tem **497 pregões**. O dele tem "
        "**15**. É a diferença entre avaliar um aluno com uma prova de 497 questões e "
        "avaliar com uma de 15. Na prova de 15, acertar 13 por sorte acontece com "
        "alguma facilidade — e se você fizer o aluno repetir a prova várias vezes com "
        "variações, uma hora ele acerta 13.")

    A.secao(doc, "3.2", "E foi exatamente isso que outros pesquisadores mostraram",
            nivel=2)

    A.paragrafo(doc,
        "Em 2017, Lachanski e Pav publicaram na revista *Econ Journal Watch* um "
        "trabalho chamado, em tradução livre, **“Aquém do limite de caracteres: "
        "‘O humor do Twitter prevê o mercado’ revisitado”**.")

    A.paragrafo(doc,
        "Eles refizeram a análise e estenderam os dados para incluir 2007. "
        "Resultado: **não encontraram nenhuma evidência** de que o humor do Twitter "
        "ajude a prever o mercado fora da amostra. E explicaram por quê:")

    A.lista(doc, [
        "**Data snooping** — testar muitas coisas e reportar a que deu certo.",
        "**Viés de comparações múltiplas** — Bollen testou **sete** dimensões de "
        "humor, em várias defasagens. Testando bastante, alguma coisa dá "
        "significativa por acaso.",
    ])

    A.paragrafo(doc,
        "**Isso muda a sua defesa por completo.** Se alguém na banca disser “mas "
        "Bollen conseguiu 86,7%”, você responde: *“Aqueles 86,7% são 13 acertos em 15 "
        "pregões, sobre um índice e não sobre uma ação, e o resultado foi refutado por "
        "Lachanski e Pav em 2017, que atribuíram o achado a data snooping.”*")

    A.paragrafo(doc,
        "**Já coloquei isso na dissertação, com a referência.** Você deixa de estar na "
        "defensiva e passa a demonstrar domínio da literatura.")

    A.secao(doc, "3.3", "Mas há uma ideia MUITO boa escondida ali", nivel=2)

    A.paragrafo(doc,
        "E esta é a parte que quase ninguém cita.")

    A.paragrafo(doc,
        "Bollen não mediu apenas “positivo e negativo”. Ele mediu **sete dimensões de "
        "humor**: calma, atenção, segurança, vitalidade, gentileza, felicidade, e a "
        "polaridade comum.")

    A.paragrafo(doc,
        "**E das sete, só UMA teve poder preditivo: a calma.** A polaridade "
        "positivo/negativo — que é exatamente o que você usa, e o que quase toda a "
        "literatura usa — **não funcionou.**")

    A.paragrafo(doc,
        "Isso conversa direto com os seus próprios resultados. Você descobriu que "
        "**90% dos erros do modelo envolvem a classe “Neutro”**, e que se você olhar "
        "só Positivo contra Negativo o desempenho salta para 0,783. Ou seja: **a "
        "divisão em três classes pode ser a representação errada do problema.**")

    A.paragrafo(doc,
        "**É uma linha de pesquisa concreta**, e ela se junta à ideia dos embeddings "
        "que apareceu no levantamento anterior: em vez de espremer a notícia em uma "
        "palavra (“positivo”), usar uma representação mais rica.")

    # ── 4 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "4", "Schumaker: 71,2% em 20 minutos, não no dia seguinte")

    A.paragrafo(doc,
        "Este trabalho é sério e o número é real. Só que mede outra coisa.")

    A.tabela_abnt(doc, "2", "O que o Schumaker realmente previu",
        ["Item", "Detalhe"],
        [
            ["O que prevê", "o preço 20 MINUTOS após a notícia sair"],
            ["Período de dados", "5 semanas"],
            ["Os 71,2%", "o melhor entre vários esquemas testados"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**Vinte minutos depois da notícia sair não é previsão do dia seguinte. É a "
        "reação imediata do mercado.**")

    A.paragrafo(doc,
        "E aqui está o detalhe bonito: **você já mediu isso.** Na sua Seção 4.l você "
        "separou dois momentos:")

    A.tabela_abnt(doc, "3", "O seu próprio resultado, que diz a mesma coisa",
        ["Momento", "Positivo", "Neutro", "Negativo"],
        [
            ["P0 — pregão que reage", "55,0%", "53,2%", "51,6%"],
            ["P1 — dia seguinte", "52,5%", "52,4%", "51,5%"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**No momento da reação o sinal é limpo e ordenado; no dia seguinte ele "
        "some.** Schumaker mediu o momento da reação, com precisão de 20 minutos. "
        "Você mediu com precisão de um dia — e ainda assim viu o mesmo padrão.")

    A.paragrafo(doc,
        "**Não há contradição entre 71,2% e 54,5%.** São medidas de momentos "
        "diferentes. E o seu próprio dado explica a diferença.")

    A.paragrafo(doc,
        "**A lição aproveitável:** o sinal vive no curtíssimo prazo. Isso agora tem "
        "**três apoios independentes** — o Schumaker, o seu P0 contra P1, e os "
        "Halousková e Lyócsa, que superam o HAR justamente usando dados de 5 em 5 "
        "minutos. **Dados intradiários da PETR4 são a melhoria de maior potencial "
        "que a sua pesquisa tem pela frente.**")

    # ── 5 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "5", "Barak: você já testou, e não funcionou")

    A.paragrafo(doc,
        "Este é o mais direto de responder. A técnica central do Barak é **juntar "
        "vários modelos diferentes e combiná-los** (chama-se *ensemble* ou "
        "*stacking*).")

    A.paragrafo(doc,
        "**Você já replicou isso**, na rodada de refinamento de julho. Está na tabela "
        "da Seção 4.d:")

    A.tabela_abnt(doc, "4", "O que o stacking rendeu na sua pesquisa",
        ["Configuração", "Acurácia de teste"],
        [
            ["XGBoost simples (3 atributos)", "54,52%"],
            ["Stacking (3 atributos)", "53,14%"],
            ["Stacking (10 atributos)", "52,99%"],
            ["Stacking (17 atributos)", "53,14%"],
            ["Baseline de classe majoritária", "53,14%"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**As três versões do stacking ficaram no baseline ou abaixo dele.** O modelo "
        "mais simples ganhou de todos. Além disso, Barak trabalha no mercado de "
        "Teerã, menos líquido que a B3, prevê retorno e risco em vez da direção "
        "diária, e reporta o melhor entre várias configurações.")

    # ── 6 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "6", "A resposta à sua segunda pergunta")

    A.paragrafo(doc,
        "*“Por que não posso usar essas pesquisas para melhorar os meus resultados?”*")

    A.paragrafo(doc,
        "**Você pode — só que não copiando as acurácias, e sim as decisões de "
        "desenho.** Duas delas valem de verdade:")

    A.tabela_abnt(doc, "5", "O que dá para aproveitar de cada um",
        ["Trabalho", "A acurácia serve?", "O que serve"],
        [
            ["Bollen (2011)", "não — 13/15, refutado",
             "medir HUMOR em várias dimensões, não só positivo/negativo"],
            ["Schumaker (2009)", "não — mede reação em 20 min",
             "trabalhar em horizonte INTRADIÁRIO"],
            ["Barak (2017)", "não — outro mercado e tarefa",
             "nada: já testado, ficou no baseline"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**E repare que as duas ideias que sobraram convergem com tudo o que já "
        "descobrimos:**")

    A.lista(doc, [
        "**Representação mais rica** — Bollen (só “calma” funcionou), o seu erro "
        "concentrado no Neutro, o Pos×Neg dando 0,783, e a ideia dos embeddings. "
        "Quatro caminhos apontando para o mesmo lugar.",
        "**Horizonte curto** — Schumaker (20 min), o seu P0 contra P1, e Halousková "
        "e Lyócsa (5 min). Três caminhos apontando para o mesmo lugar.",
    ])

    # ── 7 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "7", "Uma palavra sobre o tom das minhas respostas")

    A.paragrafo(doc,
        "Percebo que venho dando muitas respostas do tipo “esse número não vale”, e "
        "que isso cansa. Então quero ser claro sobre o que essa insistência significa "
        "e o que não significa.")

    A.paragrafo(doc,
        "**Não significa que a sua pesquisa é fraca.** Significa que boa parte da "
        "literatura da área reporta números que não sobrevivem a exame — 13 acertos "
        "em 15 dias, o melhor entre várias configurações, métricas de regressão "
        "apresentadas como acurácia, resultados de validação apresentados como "
        "resultados de teste. Você mesmo cometeu esse último erro na tabela da "
        "ponderação, e nós corrigimos.")

    A.paragrafo(doc,
        "**A sua dissertação é mais rigorosa que a maioria dos trabalhos com que ela "
        "se compara.** Isso tem custo: os seus números são menores. E tem benefício: "
        "eles se sustentam quando alguém puxa o fio. Numa defesa, quem sustenta ganha "
        "de quem impressiona.")

    # ── 8 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "8", "Se você tiver dois minutos para explicar isso")

    A.lista(doc, [
        "“Fui conferir os números altos da minha tabela comparativa, um por um, na "
        "fonte.”",
        "“Os 86,7% do Bollen são 13 acertos em 15 pregões, sobre um índice e não uma "
        "ação — e o resultado foi refutado por Lachanski e Pav em 2017, que "
        "atribuíram a data snooping.”",
        "“Os 71,2% do Schumaker são o preço 20 minutos depois da notícia. É reação, "
        "não previsão do dia seguinte. E é o melhor entre vários esquemas.”",
        "“O Barak eu já repliquei: o stacking deu 53,14%, no baseline. O modelo mais "
        "simples ganhou.”",
        "“Mas tirei duas ideias boas: o Bollen mostrou que das sete dimensões de "
        "humor só a calma previu — positivo/negativo não previu. E o Schumaker "
        "confirma que o sinal vive no intradiário.”",
        "“As duas convergem com o que eu já tinha achado sozinho.”",
    ])

    doc.save(SAIDA)
    print(f"[OK] Documento gerado: {SAIDA}")


if __name__ == "__main__":
    main()
