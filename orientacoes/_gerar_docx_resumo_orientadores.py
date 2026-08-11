# -*- coding: utf-8 -*-
# ==============================================================================
#   Resumo curto e em linguagem comum, para o mestrando entender e EXPLICAR
#   verbalmente ao orientador e ao co-orientador.
#
#   Saída: orientacoes/RESUMO_PARA_EXPLICAR_AOS_ORIENTADORES.docx
#
#   Não é documento de leitura para os professores — é a "cola" do mestrando.
#   Formato: o que dizer, na ordem, com as frases prontas e as respostas às
#   perguntas prováveis.
# ==============================================================================
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(RAIZ / "src" / "comum"))

import abnt_docx as A  # noqa: E402

FONTE = "Elaborado pelo autor (2026)"
SAIDA = AQUI / "RESUMO_PARA_EXPLICAR_AOS_ORIENTADORES.docx"


def main() -> None:
    doc = A.novo_documento()

    A.capa(
        doc,
        titulo="O que dizer aos orientadores",
        subtitulo="Resumo em linguagem comum, com as frases prontas e as "
                  "respostas às perguntas prováveis",
        autor="Vanderlei Barbosa da Silva",
        orientador="Orientador: Prof. Dr. Julio Cesar Nievola · "
                   "Co-orientador: Prof. Dr. Emerson Cabrera Paraiso",
        instituicao="PUCPR — Programa de Pós-Graduação em Informática (PPGIa)",
        descricao="Documento de apoio pessoal, não destinado a leitura pelos "
                  "professores. Reúne, em linguagem comum, o que foi feito e o que "
                  "foi descoberto, organizado na ordem em que convém apresentar, com "
                  "as respostas preparadas para as perguntas mais prováveis.",
    )

    # ── 1 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "1", "Se você tiver dois minutos, diga isto")
    A.citacao_longa(doc,
        "Medi o quanto o modelo de sentimento acerta no nosso corpus e encontrei 58%. "
        "Investiguei a causa e testei oito formas de melhorar. Nenhuma funcionou, e a última "
        "delas produziu um achado interessante: adaptar o modelo ao nosso vocabulário o "
        "tornou duas vezes melhor em entender os textos, e ao mesmo tempo pior em "
        "classificá-los. É um caso de esquecimento catastrófico, e está medido com "
        "significância estatística. Com isso encerro a linha de melhoria do classificador e "
        "passo a concentrar o esforço na previsão de volatilidade e na redação.",
        "A síntese, se houver pouco tempo")

    # ── 2 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "2", "Se tiver dez minutos, siga esta ordem")

    A.secao(doc, "2.1", "Primeiro: por que 58% não é o escândalo que parece", nivel=2)
    A.paragrafo(doc,
        "Comece desarmando a leitura de que o número é ruim. São três pontos, nesta ordem:")
    A.lista(doc, [
        "**Ninguém mais mediu.** Os outros trabalhos que usam esse mesmo modelo simplesmente "
        "o aplicam e confiam. Nós somos os únicos, junto com o autor, que temos número.",
        "**Chutando, acertaria 33%.** E respondendo sempre a categoria mais comum, 41%. "
        "Nossos 58% estão dezessete pontos acima disso.",
        "**O erro é concentrado num lugar só.** Separar notícia boa de notícia ruim o modelo "
        "faz com 78% de acerto. O que ele não consegue é decidir quando a notícia é neutra.",
    ])

    A.secao(doc, "2.2", "Segundo: o que testamos e por quê", nivel=2)
    A.paragrafo(doc,
        "A ideia era simples: o modelo foi treinado com notícias financeiras em geral, e nós "
        "o usamos em notícias de Petrobras e petróleo. Fazia sentido dar a ele um período de "
        "imersão no nosso vocabulário antes de usá-lo.")
    A.paragrafo(doc,
        "**A frase para explicar como funciona:** *cobrimos palavras ao acaso nas nossas 205 "
        "mil notícias e mandamos o modelo adivinhar quais eram, milhares de vezes. Ele aprende "
        "o vocabulário sozinho, sem precisar de ninguém corrigindo — a resposta certa é a "
        "própria palavra que foi coberta.*")
    A.paragrafo(doc,
        "Vale destacar esse ponto ao Prof. Emerson: **esse experimento não consome rotulagem "
        "humana**, e por isso pôde avançar mesmo com a rotulagem suspensa.")

    A.secao(doc, "2.3", "Terceiro: por que precisamos de três modelos", nivel=2)
    A.paragrafo(doc,
        "Aqui está o ponto metodológico que mais impressiona, e vale explicar com calma.")
    A.paragrafo(doc,
        "O modelo original foi treinado com 503 exemplos corrigidos. O nosso, com 352. "
        "Quando o nosso saiu pior, havia **duas explicações possíveis** e nenhum jeito de "
        "distinguir: ou a imersão atrapalhou, ou ele apenas estudou com menos exemplos.")
    A.paragrafo(doc,
        "**A frase para explicar:** *é o mesmo problema de um teste de remédio. Se o grupo que "
        "tomou o remédio também dormiu mais, não dá para saber o que causou a melhora. É "
        "preciso um grupo igual em tudo, que só não tenha tomado o remédio.*")
    A.paragrafo(doc,
        "Foi o que fizemos: criamos um terceiro modelo, **sem a imersão, com os mesmos 352 "
        "exemplos, mesmo procedimento**. Comparar esse terceiro com o segundo isola o efeito "
        "da imersão.")

    A.secao(doc, "2.4", "Quarto: o resultado", nivel=2)
    A.tabela_abnt(doc, 1, "O que aconteceu",
        ["", "Fez a imersão?", "Acertos em 100"],
        [["Modelo original do autor", "Não", "58"],
         ["**Nosso, com imersão**", "**Sim**", "**55**"],
         ["**Controle, sem imersão**", "**Não**", "**59**"]],
        fonte=FONTE)
    A.paragrafo(doc,
        "**O modelo que não fez a imersão saiu-se melhor.** E a diferença tem apenas 2% de "
        "chance de ser coincidência — ou seja, é real.")
    A.paragrafo(doc,
        "**Mas o mais interessante:** a imersão *funcionou* para o que ela se propunha. O "
        "modelo ficou **duas vezes melhor** em entender o vocabulário das nossas notícias. Ele "
        "aprendeu a linguagem do setor — e mesmo assim piorou em dar as notas.")

    A.secao(doc, "2.5", "Quinto: a explicação", nivel=2)
    A.citacao_longa(doc,
        "É como mandar um funcionário do atendimento, que classifica reclamações como graves "
        "ou leves, para um curso intensivo de vocabulário técnico do setor. Ele volta falando "
        "com fluência sobre pré-sal e margem de refino — e perdeu a prática de julgar a "
        "gravidade. Aprender o vocabulário sobrescreveu parte do que ele sabia sobre julgar.",
        "A analogia para explicar o esquecimento catastrófico")
    A.paragrafo(doc,
        "E o estrago tem endereço preciso: **a capacidade de reconhecer notícia boa.** De cada "
        "100 manchetes positivas, o modelo sem imersão identifica 45; com a imersão, apenas "
        "28. Notícia ruim e notícia neutra ficaram iguais.")

    # ── 3 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "3", "As perguntas que eles provavelmente farão")
    A.tabela_abnt(doc, 2, "Perguntas prováveis e respostas preparadas",
        ["Se perguntarem", "Responda"],
        [
            ["“Então foi tempo perdido?”",
             "Não. Primeiro, é achado publicável: melhorar a compreensão do texto piorou a "
             "tarefa, com medição e significância. Segundo, agora sei onde não investir o "
             "tempo que resta"],
            ["“Por que não tenta mais uma coisa?”",
             "Foram oito tentativas, todas medidas. A última era a de melhor fundamentação "
             "teórica. O padrão é consistente: o classificador está perto do limite prático "
             "nesta tarefa"],
            ["“58% não invalida a pesquisa?”",
             "Não, por duas razões. O eixo da dissertação é volatilidade, não classificação "
             "de sentimento. E o erro de medida no índice torna o efeito estimado um piso — "
             "o efeito real é maior"],
            ["“Como você sabe que a diferença não é sorte?”",
             "Reamostrei os dados dez mil vezes e recalculei. A diferença aparece em 98% das "
             "reamostragens. É a mesma lógica da margem de erro de pesquisa eleitoral"],
            ["“Isso serve para a dissertação?”",
             "Sim, como seção de método e resultados. As oito hipóteses testadas e rejeitadas "
             "formam uma seção que demonstra rigor — bancas desconfiam de trabalhos em que "
             "tudo deu certo"],
            ["“E a rotulagem, retoma?”",
             "Não por enquanto. Doze dos treze caminhos que mapeei não dependem dela. Quando "
             "retomar, a prioridade é dupla anotação de 100 a 150 das que já existem, não mais "
             "volume"],
        ], fonte=FONTE)

    # ── 4 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "4", "Os termos, caso alguém use e você precise acompanhar")
    A.tabela_abnt(doc, 3, "Tradução rápida",
        ["Se ouvir", "Quer dizer"],
        [
            ["Acurácia", "Quantos acertos em cada 100"],
            ["F1-macro", "Nota que confere se vai bem nas três categorias, não só na mais comum"],
            ["Kappa", "Acerto descontada a sorte. Zero é sorte pura, um é perfeito"],
            ["Perplexidade", "Entre quantas palavras o modelo hesita ao completar uma frase. "
                             "Menor é melhor"],
            ["Adaptação de domínio", "O período de imersão no vocabulário do nosso setor"],
            ["Esquecimento catastrófico", "Aprender uma coisa nova apagou parte do que já sabia"],
            ["Bootstrap", "Simulação que calcula a margem de erro, como em pesquisa eleitoral"],
            ["p-valor", "Chance de o resultado ser coincidência. Abaixo de 0,05 é aceito como real"],
            ["Confundimento", "Duas causas misturadas, impossível saber de qual veio o efeito"],
            ["Conjunto-ouro", "As 300 manchetes que classifiquei à mão"],
        ], fonte=FONTE)

    # ── 5 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "5", "Como fechar a conversa")
    A.paragrafo(doc,
        "Encerre propondo, e não pedindo autorização. Três frases:")
    A.lista(doc, [
        "**“Encerro a linha de melhoria do classificador.”** Oito tentativas medidas bastam "
        "para justificar.",
        "**“Passo a corrigir a escala do índice de sentimento e a refazer as contas de "
        "volatilidade.”** Há um defeito na configuração do modelo publicado que afeta a escala "
        "do nosso índice; já está identificado e o conserto está pronto.",
        "**“E concentro o resto do tempo na redação.”** É o que está atrasado, e o material já "
        "está todo produzido.",
    ])
    A.paragrafo(doc,
        "Se o Prof. Emerson perguntar sobre a rotulagem, a resposta curta é que ela continua "
        "suspensa, que isso não travou nada, e que quando for retomada o problema a resolver "
        "não é volume — é a ausência de segunda anotação.")

    doc.save(SAIDA)
    print(f"OK -> {SAIDA.name}")


if __name__ == "__main__":
    main()
