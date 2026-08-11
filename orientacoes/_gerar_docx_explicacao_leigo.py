# -*- coding: utf-8 -*-
# ==============================================================================
#   Gera a explicação em linguagem comum do experimento G3 (adaptação de domínio)
#   Saída: orientacoes/EXPLICACAO_SIMPLES_EXPERIMENTO_G3.docx
#
#   Público: leitor sem formação em aprendizado de máquina.
#   Regra de escrita: nenhum termo técnico aparece sem ser explicado antes,
#   com analogia. Todo número vem acompanhado do que ele significa.
# ==============================================================================
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(RAIZ / "src" / "comum"))

import abnt_docx as A  # noqa: E402

FONTE = "Elaborado pelo autor (2026)"
SAIDA = AQUI / "EXPLICACAO_SIMPLES_EXPERIMENTO_G3.docx"


def main() -> None:
    doc = A.novo_documento()

    A.capa(
        doc,
        titulo="O experimento da adaptação de domínio, explicado",
        subtitulo="O que foi feito, por que foi feito e o que descobrimos — "
                  "em linguagem comum",
        autor="Vanderlei Barbosa da Silva",
        orientador="Orientador: Prof. Dr. Julio Cesar Nievola",
        instituicao="PUCPR — Programa de Pós-Graduação em Informática (PPGIa)",
        descricao="Documento escrito para ser entendido sem conhecimento prévio de "
                  "aprendizado de máquina. Todo termo técnico é explicado quando "
                  "aparece pela primeira vez, com analogia. Elaborado em 10 de agosto "
                  "de 2026, após a conclusão do experimento no Google Colab.",
    )

    # ── 1 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "1", "A história em uma página")
    A.paragrafo(doc,
        "A sua pesquisa usa um programa de computador chamado **FinBERT-PT-BR**. Esse "
        "programa lê a manchete de uma notícia e responde uma coisa só: **essa notícia soa "
        "boa, ruim ou indiferente para o mercado financeiro?**")
    A.paragrafo(doc,
        "Você mediu o quanto ele acerta. Para isso, pegou 300 manchetes sobre a Petrobras e "
        "classificou você mesmo, à mão. Depois comparou as suas respostas com as dele. "
        "**Ele acertou 58 de cada 100.**")
    A.paragrafo(doc,
        "Cinquenta e oito por cento parece pouco. Passamos semanas tentando descobrir por quê, "
        "e tentando melhorar. Fizemos oito tentativas diferentes. **Nenhuma funcionou.**")
    A.paragrafo(doc,
        "A oitava tentativa — a que acabamos de rodar — era a mais promissora de todas. E ela "
        "não só falhou: ela **piorou** o programa. Mas falhou de um jeito interessante, que "
        "explica muita coisa e que rende uma seção da sua dissertação.")
    A.paragrafo(doc,
        "**Este documento conta essa história do início.** Se algum termo não estiver claro, é "
        "porque eu falhei em explicá-lo — não porque você deveria saber.")

    # ── 2 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "2", "As peças do quebra-cabeça")
    A.paragrafo(doc,
        "Antes do experimento, sete conceitos. Cada um com uma comparação do dia a dia.")

    A.secao(doc, "2.1", "O que é o “modelo”", nivel=2)
    A.paragrafo(doc,
        "Pense num **funcionário que você contratou para ler notícias**. Ele não decora "
        "respostas: ele aprendeu um jeito de ler e formar opinião. Esse funcionário é o que a "
        "área chama de **modelo**.")
    A.paragrafo(doc,
        "Esse funcionário tem duas partes, e a distinção vai importar mais adiante:")
    A.lista(doc, [
        "**A formação dele** — saber português, saber o vocabulário de finanças, entender que "
        "“alta do petróleo” e “queda do petróleo” são coisas opostas. É a maior parte do que "
        "ele é.",
        "**A função dele** — pegar tudo o que entendeu e dar uma nota: boa, ruim ou "
        "indiferente. É uma camada fina, por cima da formação.",
    ])
    A.paragrafo(doc,
        "Na área, a formação é chamada de **corpo** do modelo, e a função é chamada de "
        "**cabeça**. Trocando a cabeça e mantendo o corpo, o mesmo funcionário passa a fazer "
        "outra tarefa — sem precisar reaprender português.")

    A.secao(doc, "2.2", "O que é “treinar”", nivel=2)
    A.paragrafo(doc,
        "**Treinar é mostrar exemplos com a resposta certa, muitas vezes, até a pessoa pegar o "
        "jeito.** Como ensinar alguém a corrigir provas: você mostra cem provas já corrigidas, "
        "ele observa o critério, e depois consegue corrigir sozinho.")
    A.paragrafo(doc,
        "O autor do FinBERT-PT-BR, Lucas Leme, treinou o programa dele em duas etapas. Primeiro "
        "**a formação**: fez o programa ler 1,4 milhão de notícias financeiras, para absorver o "
        "vocabulário. Depois **a função**: mostrou 503 notícias já classificadas por três "
        "pessoas, para ele aprender a dar a nota.")

    A.secao(doc, "2.3", "O que é o “gabarito” (ou conjunto-ouro)", nivel=2)
    A.paragrafo(doc,
        "É a sua **prova corrigida à mão**. Você pegou 300 manchetes e escreveu, para cada uma, "
        "se era positiva, negativa ou neutra. Sem isso não haveria como saber se o programa "
        "acerta — você estaria confiando na palavra do autor dele.")
    A.paragrafo(doc,
        "Na área isso se chama **conjunto-ouro**: o padrão contra o qual tudo é medido. É o seu "
        "termômetro.")

    A.secao(doc, "2.4", "As três notas: acurácia, F1 e kappa", nivel=2)
    A.paragrafo(doc,
        "Existem três formas de dar nota ao programa, e cada uma corrige um defeito da anterior.")
    A.tabela_abnt(doc, 1, "As três medidas de desempenho",
        ["Medida", "O que é", "Por que existe"],
        [
            ["**Acurácia**", "Quantas ele acertou de cada 100",
             "É a mais simples e intuitiva — mas engana, ver abaixo"],
            ["**F1-macro**", "A nota média considerando as três respostas separadamente",
             "Corrige a armadilha da acurácia"],
            ["**Kappa**", "Quanto ele acertou ALÉM do que acertaria chutando",
             "Desconta a sorte"],
        ], fonte=FONTE)
    A.paragrafo(doc,
        "**A armadilha da acurácia.** Imagine que 90 das suas 100 manchetes fossem neutras. Um "
        "programa preguiçoso que responde “neutro” para tudo, sem nem ler, acertaria 90. "
        "Acurácia de 90% — e ele é completamente inútil. O **F1-macro** existe para pegar esse "
        "truque: ele confere se o programa vai bem nas três respostas, e não só na mais comum.")
    A.paragrafo(doc,
        "**Por que o kappa.** Numa prova de três alternativas, quem chuta acerta uma em cada "
        "três, ou 33%. Então acertar 58% não é 58% de mérito — parte veio de sorte. O kappa "
        "desconta isso: **0 significa “só sorte” e 1 significa “perfeito”**. O nosso é 0,37, "
        "que na escala usada na área é chamado de concordância *razoável*.")

    A.secao(doc, "2.5", "O que é “perplexidade”", nivel=2)
    A.paragrafo(doc,
        "Esta é a medida menos intuitiva das que aparecem aqui, e vale um minuto.")
    A.paragrafo(doc,
        "Pegue uma frase e **cubra uma palavra com o dedo**. Peça para o programa adivinhar qual "
        "é. Se ele ficar em dúvida entre sete palavras possíveis, dizemos que a **perplexidade "
        "é 7**. Se ficar em dúvida entre 3,7, a perplexidade é 3,7.")
    A.paragrafo(doc,
        "**Quanto MENOR, melhor** — significa que ele conhece bem o assunto e hesita pouco. É "
        "como a diferença entre um leigo e um especialista tentando completar a frase "
        "“a Petrobras anunciou a venda de uma…”. O especialista hesita entre poucas opções; o "
        "leigo, entre muitas.")
    A.paragrafo(doc,
        "**A grande vantagem da perplexidade:** ela **não precisa do seu gabarito**. O próprio "
        "texto é a resposta — a palavra que você cobriu está ali. Por isso ela pôde ser medida "
        "mesmo com a rotulagem suspensa pelo Prof. Emerson.")

    A.secao(doc, "2.6", "O que é “adaptação de domínio”", nivel=2)
    A.paragrafo(doc,
        "É a ideia que testamos nesta etapa, e é simples: **mandar o funcionário fazer um "
        "estágio de imersão no seu assunto.**")
    A.paragrafo(doc,
        "Na prática: pegamos as **205 mil notícias** que você coletou sobre Petrobras, petróleo "
        "e estatais, cobrimos palavras ao acaso e mandamos o programa adivinhar, milhares de "
        "vezes. A intenção era que ele absorvesse o vocabulário do seu setor — pré-sal, barril, "
        "paridade de importação, dividendo extraordinário.")
    A.paragrafo(doc,
        "**Esse estágio não precisa de professor.** A resposta certa é a própria palavra que "
        "foi coberta. Por isso ele era compatível com a suspensão da rotulagem — e por isso era "
        "a nossa aposta mais forte.")

    A.secao(doc, "2.7", "O que é “bootstrap”, “intervalo de confiança” e “p-valor”", nivel=2)
    A.paragrafo(doc,
        "Você mediu 58% em **300** manchetes. Mas e se tivesse sorteado **outras** 300? Daria "
        "58% de novo, ou 54%, ou 62%? Essa dúvida é legítima e tem nome.")
    A.paragrafo(doc,
        "**É a mesma lógica da margem de erro de pesquisa eleitoral.** Quando dizem “40% dos "
        "votos, dois pontos para mais ou para menos”, estão reconhecendo que entrevistaram uma "
        "amostra, não a população inteira.")
    A.paragrafo(doc,
        "O **bootstrap** é a técnica que calcula essa margem: o computador sorteia as suas 300 "
        "manchetes com repetição, dez mil vezes, e refaz a conta em cada sorteio. No fim você "
        "tem uma faixa em vez de um número — o **intervalo de confiança de 95%**, que é a faixa "
        "onde o valor verdadeiro provavelmente está.")
    A.paragrafo(doc,
        "E o **p-valor** responde a uma pergunta específica: *“qual a chance de essa diferença "
        "ter aparecido por puro acaso?”* Um p-valor de 0,02 quer dizer **2% de chance de ser "
        "coincidência** — ou seja, provavelmente é real. Por convenção, abaixo de 0,05 a área "
        "aceita o resultado como **significativo**.")

    # ── 3 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "3", "O experimento: o que fizemos e por quê")
    A.paragrafo(doc,
        "A pergunta era direta: **o estágio de imersão melhora o programa?**")
    A.paragrafo(doc,
        "Parece que bastaria comparar duas coisas — o programa antes e o programa depois do "
        "estágio. Mas há uma armadilha, e ela quase estragou o experimento.")

    A.secao(doc, "3.1", "A armadilha que quase nos pegou", nivel=2)
    A.paragrafo(doc,
        "O programa original do Lucas foi treinado com **503** notícias classificadas. O nosso, "
        "depois do estágio, foi treinado com **352** — porque separamos uma parte para conferir "
        "o aprendizado.")
    A.paragrafo(doc,
        "Então, quando o nosso saiu pior, havia **duas explicações possíveis** e nenhuma forma "
        "de distinguir:")
    A.lista(doc, [
        "O estágio de imersão atrapalhou; **ou**",
        "Ele simplesmente estudou com menos exemplos (352 em vez de 503).",
    ])
    A.paragrafo(doc,
        "**Isso se chama confundimento**: duas causas misturadas, impossível saber de qual veio "
        "o efeito. Um resultado assim não pode ser reportado — a banca desmontaria em um minuto.")

    A.secao(doc, "3.2", "A solução: o terceiro programa", nivel=2)
    A.paragrafo(doc,
        "Foi por isso que pedi para você rodar mais um notebook. Ele criou um **terceiro** "
        "programa, que chamamos de **C**:")
    A.tabela_abnt(doc, 2, "Os três programas comparados",
        ["", "Fez o estágio de imersão?", "Estudou com quantos exemplos?"],
        [
            ["**A** — o original do Lucas", "Não (no nosso assunto)", "503"],
            ["**B** — o nosso, adaptado", "**Sim**", "352"],
            ["**C** — o controle", "Não", "**352**"],
        ], fonte=FONTE)
    A.paragrafo(doc,
        "**C é a peça-chave.** Ele estudou com os mesmos 352 exemplos que B, do mesmo jeito, na "
        "mesma ordem — a **única** diferença é que C não fez o estágio de imersão.")
    A.paragrafo(doc,
        "Assim, comparar **B com C** isola o efeito do estágio, porque tudo o mais é idêntico. "
        "É o mesmo raciocínio de um teste de remédio: para saber se o remédio funciona, você "
        "precisa de um grupo que recebeu o remédio e outro **igual em tudo** que não recebeu.")

    # ── 4 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "4", "O que aconteceu")
    A.tabela_abnt(doc, 3, "Resultado dos três programas nas suas 300 manchetes",
        ["Programa", "Acertos em 100", "F1-macro", "Kappa"],
        [
            ["A — original do Lucas", "58,0", "0,579", "0,371"],
            ["**B — com o estágio**", "**54,7**", "**0,528**", "0,309"],
            ["**C — sem o estágio**", "**59,0**", "**0,584**", "0,378"],
        ], fonte=FONTE)
    A.paragrafo(doc,
        "**C ficou melhor que B.** O programa que NÃO fez o estágio de imersão saiu-se melhor do "
        "que o que fez — com exatamente os mesmos exemplos de estudo.")

    A.secao(doc, "4.1", "Isso pode ser coincidência?", nivel=2)
    A.paragrafo(doc,
        "Foi exatamente essa a pergunta que o bootstrap respondeu. Rodamos as dez mil "
        "simulações:")
    A.tabela_abnt(doc, 4, "A diferença é real ou é acaso?",
        ["Comparação", "Diferença", "Faixa provável", "Chance de ser acaso", "Conclusão"],
        [
            ["**C contra B** (efeito do estágio)", "**+0,056**", "de +0,008 a +0,106",
             "**2%**", "**É real**"],
            ["C contra A (nosso método × o do Lucas)", "+0,005", "de −0,023 a +0,032",
             "69%", "É acaso"],
        ], fonte=FONTE)
    A.paragrafo(doc,
        "**Primeira linha:** 2% de chance de ser coincidência. **O estágio de imersão realmente "
        "piorou o programa.**")
    A.paragrafo(doc,
        "**Segunda linha, e ela é uma boa notícia:** o nosso método de treino deu praticamente o "
        "mesmo resultado que o do Lucas, usando menos exemplos. Isso prova que **implementamos "
        "corretamente** o procedimento dele — e é o que torna a primeira linha confiável. Se "
        "tivéssemos errado a implementação, nenhuma comparação valeria.")

    A.secao(doc, "4.2", "Onde exatamente o estrago aconteceu", nivel=2)
    A.paragrafo(doc,
        "Olhando resposta por resposta, o dano tem endereço. A tabela abaixo mostra, de cada "
        "100 manchetes de cada tipo, quantas o programa identificou corretamente:")
    A.tabela_abnt(doc, 5, "Acerto por tipo de notícia (de cada 100)",
        ["Tipo de manchete", "A original", "B com estágio", "C sem estágio", "Efeito"],
        [
            ["Negativa", "75", "75", "71", "sem mudança"],
            ["Neutra", "53", "62", "62", "sem mudança"],
            ["**Positiva**", "50", "**28**", "**45**", "**despencou**"],
        ], fonte=FONTE)
    A.paragrafo(doc,
        "**O estágio destruiu a capacidade de reconhecer notícia boa.** De cada 100 manchetes "
        "positivas, o programa sem estágio identifica 45; o programa com estágio identifica "
        "apenas 28. As outras duas categorias ficaram praticamente iguais.")

    A.secao(doc, "4.3", "E a parte surpreendente", nivel=2)
    A.paragrafo(doc,
        "Aqui está o achado que faz este experimento valer a pena. Medimos também a "
        "**perplexidade** — lembra, aquela de cobrir a palavra e ver se ele adivinha:")
    A.tabela_abnt(doc, 6, "Perplexidade nas notícias que ele nunca tinha visto",
        ["Programa", "Perplexidade", "Leitura"],
        [
            ["BERTimbau (leitor de português geral)", "7,195",
             "hesita entre ~7 palavras"],
            ["**O nosso, depois do estágio**", "**3,669**",
             "**hesita entre ~3,7 palavras**"],
        ], fonte=FONTE)
    A.paragrafo(doc,
        "**O estágio funcionou.** O programa ficou quase **duas vezes melhor** em entender o "
        "vocabulário das suas notícias. Ele realmente aprendeu a linguagem do setor.")
    A.paragrafo(doc, "**E mesmo assim piorou na tarefa.**")

    # ── 5 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "5", "Por que isso aconteceu")
    A.paragrafo(doc,
        "A explicação tem nome na área — **esquecimento catastrófico** — e uma analogia direta.")
    A.citacao_longa(doc,
        "Imagine um funcionário do atendimento ao cliente que classifica reclamações como "
        "graves, leves ou irrelevantes. Ele faz isso bem. Você então o manda para um curso "
        "intensivo de seis meses sobre o vocabulário técnico do setor. Ele volta falando com "
        "fluência sobre pré-sal, paridade de importação e margem de refino. Mas, de tanto se "
        "concentrar em vocabulário, perdeu a prática de julgar a gravidade — e agora erra "
        "classificações que antes acertava.",
        "A analogia do que aconteceu com o modelo")
    A.paragrafo(doc,
        "Foi isso, literalmente. O estágio de imersão **sobrescreveu** parte do que o programa "
        "havia aprendido sobre dar notas. Os 352 exemplos que mostramos depois não foram "
        "suficientes para ele recuperar a prática — especialmente para reconhecer notícia boa, "
        "que já era a categoria em que ele era mais fraco.")
    A.paragrafo(doc,
        "**Em uma frase:** melhorar a leitura piorou o julgamento.")

    # ── 6 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "6", "Por que um resultado negativo é um bom resultado")
    A.paragrafo(doc,
        "É natural sentir que oito tentativas sem melhoria significam tempo perdido. Não "
        "significam, e vale explicar por quê.")
    A.paragrafo(doc,
        "**Primeiro: ninguém mais mediu.** Dos trabalhos que usam esse mesmo programa, nenhum "
        "verificou se ele acerta. Todos simplesmente aplicam e confiam. Você é o único, junto "
        "com o autor, que tem número.")
    A.paragrafo(doc,
        "**Segundo: este achado específico é publicável.** A frase *“a adaptação de domínio "
        "melhorou o modelo de linguagem em 49% e ainda assim degradou a classificação de forma "
        "estatisticamente significativa”* é uma contribuição — com perplexidade, F1, intervalo "
        "de confiança e p-valor para sustentar. Não é opinião; é medição.")
    A.paragrafo(doc,
        "**Terceiro: oito hipóteses testadas e rejeitadas viram uma seção de dissertação.** E "
        "uma seção dessas demonstra rigor melhor do que qualquer melhoria alegada sem teste. "
        "Bancas desconfiam de trabalhos em que tudo deu certo.")
    A.paragrafo(doc,
        "**Quarto, e mais prático: agora você sabe onde NÃO investir o tempo que resta.** Sem "
        "esses testes, você poderia passar os próximos seis meses tentando melhorar o "
        "classificador, sem saber que ele já está perto do limite.")

    # ── 7 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "7", "O que fazer agora")
    A.paragrafo(doc,
        "A linha de tentar melhorar o classificador está encerrada. Foram oito tentativas, "
        "todas medidas. Três coisas vêm a seguir.")
    A.tabela_abnt(doc, 7, "Os próximos passos",
        ["Ordem", "O que fazer", "Por quê"],
        [
            ["1.º", "**Corrigir a escala do índice de sentimento**",
             "Descobrimos que o programa vinha reportando a “confiança” dele numa escala "
             "errada, por causa de um defeito na configuração publicada. Os acertos e erros "
             "estão certos; só o número da confiança está fora de escala — e o seu índice usa "
             "esse número"],
            ["2.º", "**Refazer as contas de volatilidade** com o índice corrigido",
             "É o eixo principal da sua dissertação, e precisa rodar sobre o índice certo"],
            ["3.º", "**Escrever**",
             "É o que está atrasado. O material já está todo produzido; falta transpor para o "
             "texto da dissertação"],
        ], fonte=FONTE)
    A.paragrafo(doc,
        "O primeiro item é o script que vou preparar em seguida. Os outros dois são o trabalho "
        "que resta até a defesa.")

    # ── 8 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "8", "Resumo de uma página")
    A.tabela_abnt(doc, 8, "Tudo o que este documento contou",
        ["Pergunta", "Resposta"],
        [
            ["O que testamos?",
             "Se mandar o programa “estagiar” nas suas 205 mil notícias o deixaria melhor"],
            ["Por que precisamos de três programas?",
             "Para separar o efeito do estágio do efeito de ter estudado com menos exemplos"],
            ["O estágio funcionou?",
             "**Sim para a leitura** (ficou 2× melhor em entender o vocabulário) e "
             "**não para a tarefa** (piorou em dar notas)"],
            ["Isso é coincidência?",
             "Não. Apenas 2% de chance de ser acaso"],
            ["Onde foi o estrago?",
             "Na identificação de notícia **positiva**: de 45 acertos em 100 caiu para 28"],
            ["Por quê?",
             "Esquecimento catastrófico — aprender o vocabulário sobrescreveu parte do que ele "
             "sabia sobre julgar"],
            ["Foi tempo perdido?",
             "Não. É achado publicável, e delimita onde não investir o tempo restante"],
            ["E agora?",
             "Corrigir a escala do índice, refazer a volatilidade e escrever"],
        ], fonte=FONTE)

    A.secao(doc, "9", "Glossário rápido")
    A.tabela_abnt(doc, 9, "Os termos que aparecem nos outros documentos",
        ["Termo", "Em linguagem comum"],
        [
            ["Modelo / encoder", "O programa que lê a notícia e dá a nota"],
            ["Corpo do modelo", "A “formação” dele: português e vocabulário financeiro"],
            ["Cabeça do modelo", "A “função” dele: transformar o que entendeu numa nota"],
            ["Treinar / ajuste fino", "Mostrar exemplos com a resposta certa até ele pegar o jeito"],
            ["Conjunto-ouro / gabarito", "Suas 300 manchetes classificadas à mão"],
            ["Acurácia", "Quantos acertos em cada 100"],
            ["F1-macro", "Nota que confere se ele vai bem nas três categorias, não só na mais comum"],
            ["Kappa", "Acerto descontada a sorte. 0 = só sorte, 1 = perfeito"],
            ["Perplexidade", "Entre quantas palavras ele hesita ao completar uma frase. Menor é melhor"],
            ["Adaptação de domínio / MLM", "O “estágio de imersão” nas notícias do seu setor"],
            ["Bootstrap", "Simulação que calcula a margem de erro, como em pesquisa eleitoral"],
            ["Intervalo de confiança", "A faixa onde o valor verdadeiro provavelmente está"],
            ["p-valor", "Chance de a diferença ser coincidência. Abaixo de 0,05 = provavelmente real"],
            ["Significativo", "A diferença é grande o bastante para não ser atribuída ao acaso"],
            ["Esquecimento catastrófico", "Aprender uma coisa nova apagou parte do que já sabia"],
            ["Confundimento", "Duas causas misturadas, impossível saber de qual veio o efeito"],
            ["Índice de sentimento (ISM)", "O termômetro diário do humor das notícias sobre a PETR4"],
        ], fonte=FONTE)

    doc.save(SAIDA)
    print(f"OK -> {SAIDA.name}")


if __name__ == "__main__":
    main()
