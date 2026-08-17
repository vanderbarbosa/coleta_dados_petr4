# -*- coding: utf-8 -*-
# ==============================================================================
#   Gera a explicação em linguagem comum da avaliação do NotebookLM
#   Saída: orientacoes/EXPLICACAO_SIMPLES_AVALIACAO_NOTEBOOKLM.docx
#
#   Público: leitor sem formação em aprendizado de máquina nem em estatística.
# ==============================================================================
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(RAIZ / "src" / "comum"))

import abnt_docx as A  # noqa: E402

FONTE = "Elaborado pelo autor (2026)"
SAIDA = AQUI / "EXPLICACAO_SIMPLES_AVALIACAO_NOTEBOOKLM.docx"


def main() -> None:
    doc = A.novo_documento()

    A.capa(
        doc,
        titulo="O que o NotebookLM acertou e o que errou",
        subtitulo="Uma conferência do levantamento — e a correção que ele "
                  "acabou provocando na dissertação",
        autor="Vanderlei Barbosa da Silva",
        orientador="Orientador: Prof. Dr. Julio Cesar Nievola",
        instituicao="PUCPR — Programa de Pós-Graduação em Informática (PPGIa)",
        descricao="Documento escrito para ser entendido sem conhecimento prévio de "
                  "aprendizado de máquina ou de estatística. Todo termo técnico é "
                  "explicado quando aparece pela primeira vez, com analogia. "
                  "Elaborado em 17 de agosto de 2026.",
    )

    # ── 1 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "1", "O resumo, em uma página")

    A.paragrafo(doc,
        "Você me mandou o levantamento do NotebookLM e eu fui conferir tudo, número "
        "por número. O balanço é este:")

    A.lista(doc, [
        "**Ele achou duas pesquisas novas** que usam o FinBERT-PT-BR e que nós não "
        "tínhamos. São reais — verifiquei as duas. Isso tem valor.",
        "**E revelou um jeito de usar o modelo que não tínhamos pensado**, que pode "
        "contornar todos os problemas que enfrentamos. Essa é a melhor parte.",
        "**Mas ele leu uma versão ANTIGA da sua dissertação.** Por isso, boa parte do "
        "que ele “recomenda” é o seu próprio texto sendo devolvido para você — e às "
        "vezes numa versão que a gente já corrigiu.",
        "**E cometeu dois erros de fato**, um deles importante.",
    ])

    A.paragrafo(doc,
        "**E teve uma consequência inesperada:** ao insistir num ponto, ele me fez "
        "reconferir uma afirmação da dissertação — e descobri que ela estava errada. "
        "Já corrigi. Explico na seção 5.")

    # ── 2 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "2", "O problema de fundo: ele leu um PDF velho")

    A.paragrafo(doc,
        "Este é o ponto que você precisa entender antes de levar qualquer coisa ao "
        "Professor Emerson, porque é constrangedor apresentar como “descoberta” algo "
        "que já está escrito no seu próprio trabalho.")

    A.paragrafo(doc,
        "Veja o que ele apresenta como recomendações:")

    A.tabela_abnt(doc, "1", "As “recomendações” e o que elas realmente são",
        ["O que ele recomenda", "Situação real"],
        [
            ["Rotular 500–1000 e ajustar o BERTimbau-large",
             "Era uma frase da dissertação QUE NÓS REMOVEMOS"],
            ["Criar zona morta nos retornos",
             "Já está no seu texto, como proposta futura"],
            ["Filtro de relevância",
             "Já está no seu texto — e já foi superado"],
            ["Regressão quantílica com pesos",
             "Já implementada e reportada"],
            ["Manter o modelo parcimonioso",
             "Já é a sua conclusão"],
            ["Regra das 17h",
             "Já implementada desde a coleta"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**Repare na primeira linha.** Ele recomenda rotular mais manchetes e ajustar "
        "um modelo maior, dizendo que “o autor conclui” isso. Só que **nós apagamos "
        "essa frase da dissertação** — porque o experimento G3 depois mostrou que "
        "ajustar o modelo **piora** o desempenho, com significância estatística.")

    A.paragrafo(doc,
        "Ou seja: ele está recomendando exatamente aquilo que testamos e que falhou. "
        "Não por má-fé — ele só não tinha como saber, porque leu o PDF de antes.")

    A.paragrafo(doc,
        "**Ação prática: reenvie o PDF atualizado antes de qualquer nova consulta.**")

    # ── 3 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "3", "Os dois erros de fato")

    A.secao(doc, "3.1", "Erro pequeno: 1,6 milhão contra 1,4 milhão", nivel=2)

    A.paragrafo(doc,
        "Ele diz que o Lucas Leme treinou o modelo com **1,6 milhão** de sentenças. "
        "A sua dissertação diz **1,4 milhão** de textos.")

    A.paragrafo(doc,
        "Fui à fonte original — a página oficial do modelo, escrita pelo próprio "
        "autor. Ela diz: *“treinado com mais de 1,4 milhão de textos”*. **O número da "
        "sua dissertação está certo.** Ele pegou o 1,6 de uma monografia de terceiros, "
        "que é fonte de segunda mão.")

    A.secao(doc, "3.2", "Erro importante: ele diz que o escore é softmax. Não é.",
            nivel=2)

    A.paragrafo(doc,
        "Aqui preciso explicar dois nomes, porque a diferença entre eles é o erro.")

    A.paragrafo(doc,
        "Quando o programa lê uma manchete, ele produz três notas internas — uma para "
        "“positivo”, uma para “negativo”, uma para “neutro”. Depois precisa "
        "transformar essas notas em algo parecido com uma probabilidade. Há duas "
        "receitas para isso:")

    A.lista(doc, [
        "**Softmax** — a receita correta quando as opções são **exclusivas** (a "
        "notícia é positiva OU negativa OU neutra, nunca duas). Ela força as três "
        "probabilidades a somarem 100%.",
        "**Sigmoide** — a receita para quando as opções **podem coexistir** (uma "
        "notícia poderia ser, ao mesmo tempo, sobre política E sobre economia). Cada "
        "opção recebe uma nota independente, e elas não somam 100%.",
    ])

    A.paragrafo(doc,
        "É a diferença entre **dividir um bolo entre três pessoas** (as fatias somam o "
        "bolo inteiro — softmax) e **dar uma nota de 0 a 10 para três filmes "
        "diferentes** (as notas são independentes — sigmoide).")

    A.paragrafo(doc,
        "O NotebookLM afirmou, com ênfase, que o seu escore é softmax. **Provei que "
        "não é, com uma conta que não admite discussão.**")

    A.paragrafo(doc,
        "**O raciocínio:** se você divide um bolo entre três pessoas, a maior fatia "
        "tem que ser de pelo menos um terço — é impossível que a maior de três partes "
        "seja menor que a média. Então, num softmax de três classes, **a nota "
        "vencedora nunca pode ficar abaixo de 0,3333.**")

    A.tabela_abnt(doc, "2", "A prova aritmética",
        ["Medida", "Valor"],
        [
            ["Menor escore no nosso corpus", "0,2845"],
            ["Piso matemático do softmax", "0,3333"],
            ["Quantos escores ficam ABAIXO do piso", "397"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**397 manchetes têm escore abaixo do que o softmax permite.** Portanto não é "
        "softmax. É sigmoide — exatamente como já tínhamos documentado na Seção 4.j, "
        "por outro caminho.")

    # ── 4 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "4", "O que ele trouxe de bom — e é bom mesmo")

    A.secao(doc, "4.1", "Duas pesquisas novas, ambas verificadas", nivel=2)

    A.lista(doc, [
        "**Pinheiro, Muinhos e Fernandes** — construíram um índice de sentimento "
        "FISCAL a partir de jornais e do Broadcast, de 2008 a 2022, e mediram o efeito "
        "na curva de juros brasileira.",
        "**Costa Neto e Anjos (USP/FIPECAFI)** — analisaram 25.804 notas explicativas "
        "de 1.152 empresas na CVM, medindo o quanto os relatórios são repetitivos, "
        "completos e densos.",
    ])

    A.secao(doc, "4.2", "A melhor descoberta: um jeito de contornar o problema todo",
            nivel=2)

    A.paragrafo(doc,
        "Esta é a parte que faz o levantamento ter valido a pena, e ela passou "
        "despercebida no meio do resto.")

    A.paragrafo(doc,
        "**As duas pesquisas usam o FinBERT-PT-BR de um jeito diferente do nosso.** "
        "Elas não usam a resposta “positivo/negativo/neutro”. Elas usam os "
        "**embeddings**.")

    A.paragrafo(doc,
        "**O que é isso, com uma analogia.** Lembra do funcionário que lê notícias? "
        "Ele tem duas partes:")

    A.lista(doc, [
        "**A compreensão** — ele leu milhões de textos financeiros e formou um "
        "entendimento profundo do assunto. Isso é o *embedding*: um resumo numérico "
        "do que ele entendeu do texto.",
        "**O parecer final** — ele resume tudo isso numa única palavra: “positivo”, "
        "“negativo” ou “neutro”. Isso é a cabeça de sentimento.",
    ])

    A.paragrafo(doc,
        "**Agora repare onde estão TODOS os nossos problemas:**")

    A.tabela_abnt(doc, "3", "Onde ficam os nossos problemas",
        ["Problema", "Está na compreensão ou no parecer?"],
        [
            ["Viés: marca 48,5% como negativo", "no PARECER"],
            ["Teto de 0,58 de acerto", "no PARECER"],
            ["Escala errada (sigmoide)", "no PARECER"],
            ["Zero dias de maioria positiva", "no PARECER"],
            ["90% dos erros na classe Neutra", "no PARECER"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**Todos. Sem exceção.** Nenhum deles está na compreensão — que é justamente "
        "a parte que foi treinada com 1,4 milhão de textos financeiros e que é a mais "
        "bem-feita do modelo.")

    A.paragrafo(doc,
        "É como ter um analista brilhante que entende profundamente de mercado, mas "
        "que, quando você pede uma resposta em uma palavra só, responde “ruim” quase "
        "sempre. **A falha está na hora de resumir, não no entendimento.** E nós "
        "passamos nove experimentos tentando consertar o resumo, quando poderíamos "
        "usar o entendimento diretamente.")

    A.paragrafo(doc,
        "**É uma linha nova, barata, e que não tenta consertar o que resistiu a nove "
        "tentativas — simplesmente não passa por ali.**")

    # ── 5 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "5", "A correção que essa conversa provocou na dissertação")

    A.paragrafo(doc,
        "O NotebookLM insistiu num ponto: que o segredo do seu resultado está em "
        "**ponderar pela confiança** — dar mais peso às manchetes que o modelo "
        "classificou com mais certeza. Ele citou a sua própria tabela: 54,93% com "
        "ponderação contra 50,30% sem.")

    A.paragrafo(doc,
        "Como eu tinha acabado de provar que a confiança está na escala errada, isso "
        "virou urgente: **se a ponderação carrega o resultado, e o peso está errado, "
        "então o resultado está comprometido.** Fui medir.")

    A.secao(doc, "5.1", "O que a medição mostrou", nivel=2)

    A.paragrafo(doc,
        "Refiz o teste no **mesmo recorte** que a medição original usou, comparando "
        "quatro jeitos de montar o índice:")

    A.tabela_abnt(doc, "4", "Reexame das quatro construções do índice",
        ["Como monta o índice", "Acerto na validação", "Acerto no TESTE"],
        [
            ["Ponderando pela confiança", "56,64%", "50,31%"],
            ["Polaridade pura (+1, 0, −1)", "53,85%", "53,88%"],
            ["Só as de alta confiança", "53,50%", "53,04%"],
            ["Saldo de votos", "53,85%", "53,88%"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**Três coisas saltam da tabela, e as três contrariam o que estava escrito.**")

    A.paragrafo(doc,
        "**Primeira: ponderar PIORA.** 50,31% contra 53,88%. Três pontos e meio a "
        "menos, não a mais.")

    A.paragrafo(doc,
        "**Segunda, e esta explica tudo:** olhe as duas colunas da variante ponderada. "
        "Ela tem **o melhor resultado na validação (56,64%) e o pior no teste "
        "(50,31%)**.")

    A.paragrafo(doc,
        "Isso tem nome e é o erro mais comum da área. **Validação** é onde você testa "
        "várias configurações e escolhe a melhor. **Teste** é a prova final, feita uma "
        "vez só. Quando algo vai muito bem na validação e mal no teste, significa que "
        "você **escolheu aquilo porque deu sorte na validação** — não porque é bom.")

    A.paragrafo(doc,
        "É como escolher o melhor jogador vendo só o treino. No treino ele brilha; no "
        "jogo, não. **O 54,93% da sua tabela é, muito provavelmente, um número de "
        "treino apresentado como se fosse de jogo.**")

    A.paragrafo(doc,
        "**Terceira: duas linhas da tabela são a mesma conta.** “Polaridade pura” e "
        "“saldo de votos” dão resultados idênticos — e **têm que dar**, porque são "
        "algebricamente a mesma coisa. Somar +1 e −1 e dividir pelo total é "
        "exatamente igual a fazer (positivas − negativas) ÷ total. A tabela original "
        "dava 54,53% e 50,30% para elas. **Isso não pode acontecer.** Não consegui "
        "descobrir de onde veio a diferença, porque o código daquela suíte não ficou "
        "guardado no repositório.")

    A.secao(doc, "5.2", "As duas boas notícias que vieram junto", nivel=2)

    A.paragrafo(doc,
        "**Primeira: a escala errada não estraga nada.** As séries com e sem "
        "ponderação são praticamente a mesma coisa — correlacionam a **0,9903**. A "
        "ponderação quase não muda nada, então o fato de o peso estar na escala "
        "errada tem consequência desprezível. **Aquele item que estava pendente — "
        "recalcular tudo com softmax numa GPU — deixa de ser prioridade.**")

    A.paragrafo(doc,
        "**Segunda: isso reforça o padrão que já conhecemos.** Compare os ganhos:")

    A.tabela_abnt(doc, "5", "O que rende, e o quanto",
        ["Intervenção", "Onde mexe", "Ganho no sinal"],
        [
            ["Filtro de relevância", "em QUAIS notícias entram", "+23%"],
            ["Ponderação por confiança", "em COMO agregar", "+6%"],
            ["Oito ajustes no classificador", "no MODELO", "nada"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**Quanto mais perto do corpus, maior o ganho. Quanto mais perto do modelo, "
        "menor.** É a mesma lição, agora com um terceiro ponto de apoio.")

    # ── 6 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "6", "Um alerta sobre originalidade")

    A.paragrafo(doc,
        "O NotebookLM afirma que **nenhuma pesquisa faz o que você faz**. Isso é "
        "verdade para a literatura em português — mas **não em inglês.**")

    A.paragrafo(doc,
        "No levantamento anterior encontramos dois trabalhos com desenho equivalente: "
        "Halousková e Lyócsa (2025), com FinBERT e HAR sobre 404 ações, e Mino e "
        "Williamson (2025), com BERT e GARCH(1,1) t-Student — o mesmo modelo do seu "
        "Script 04.")

    A.paragrafo(doc,
        "**Reivindique originalidade com esse cuidado:** original *para o mercado "
        "brasileiro e para um ativo individual em português*. Se disser “ninguém fez "
        "isso”, a banca pode apresentar o contraexemplo — e aí a defesa fica difícil.")

    # ── 7 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "7", "O que levar para a próxima orientação")

    A.paragrafo(doc, "**Leve:**")
    A.lista(doc, [
        "As duas pesquisas novas.",
        "**A ideia de usar os embeddings em vez da cabeça de sentimento** — é a "
        "melhor coisa que saiu daqui.",
        "**A revisão da ponderação por confiança.** Encontrar e corrigir um erro no "
        "próprio trabalho é sinal de maturidade científica, não de fraqueza. Bancas "
        "valorizam isso.",
    ])

    A.paragrafo(doc, "**Não leve:**")
    A.lista(doc, [
        "A lista de recomendações que já estão na sua dissertação. O Professor "
        "Emerson vai reconhecer o seu próprio texto.",
    ])

    A.paragrafo(doc, "**Sobre a ferramenta:**")
    A.paragrafo(doc,
        "O NotebookLM lê bem e organiza bem. Mas não confere contas, e não distingue "
        "o que é **conclusão** de uma pesquisa do que é **proposta de trabalho "
        "futuro** — por isso devolveu as suas próprias ideias como se fossem "
        "descobertas. Use como um bom resumidor, e **confira todo número antes de "
        "citar**. E reenvie o PDF atualizado.")

    # ── 8 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "8", "Se você tiver dois minutos para explicar isso")

    A.lista(doc, [
        "“Usei o NotebookLM para varrer as fontes que citam o FinBERT-PT-BR. Achei "
        "duas pesquisas novas que eu não tinha.”",
        "“Mas ele leu um PDF antigo, então metade das recomendações era o meu próprio "
        "texto voltando — inclusive uma frase que eu já tinha removido por estar "
        "errada.”",
        "“E ele afirmou que o escore do modelo é softmax. Provei que não é: 397 "
        "manchetes têm escore abaixo de 0,3333, que é o mínimo matemático de um "
        "softmax de três classes.”",
        "“A melhor descoberta foi outra: essas duas pesquisas usam o modelo como "
        "extrator de embeddings, não como classificador. E todos os meus problemas "
        "estão no classificador, nenhum nos embeddings.”",
        "“E a conversa me fez reconferir uma afirmação minha sobre ponderação por "
        "confiança. Estava errada — ponderar piora, não melhora. Já corrigi na "
        "dissertação, com uma seção nova.”",
    ])

    doc.save(SAIDA)
    print(f"[OK] Documento gerado: {SAIDA}")


if __name__ == "__main__":
    main()
