# -*- coding: utf-8 -*-
# ==============================================================================
#   Gera a explicação em linguagem comum do filtro de relevância
#   Saída: orientacoes/EXPLICACAO_SIMPLES_FILTRO_RELEVANCIA.docx
#
#   Público: leitor sem formação em aprendizado de máquina nem em estatística.
#   Regra de escrita: nenhum termo técnico aparece sem ser explicado antes,
#   com analogia. Todo número vem acompanhado do que ele significa e do que
#   NÃO significa.
# ==============================================================================
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(RAIZ / "src" / "comum"))

import abnt_docx as A  # noqa: E402

FONTE = "Elaborado pelo autor (2026)"
SAIDA = AQUI / "EXPLICACAO_SIMPLES_FILTRO_RELEVANCIA.docx"


def main() -> None:
    doc = A.novo_documento()

    A.capa(
        doc,
        titulo="A primeira coisa que funcionou",
        subtitulo="Por que escolher melhor as notícias rendeu mais do que "
                  "consertar o programa que as lê",
        autor="Vanderlei Barbosa da Silva",
        orientador="Orientador: Prof. Dr. Julio Cesar Nievola",
        instituicao="PUCPR — Programa de Pós-Graduação em Informática (PPGIa)",
        descricao="Documento escrito para ser entendido sem conhecimento prévio de "
                  "aprendizado de máquina ou de estatística. Todo termo técnico é "
                  "explicado quando aparece pela primeira vez, com analogia. "
                  "Elaborado em 10 de agosto de 2026, após a conclusão dos "
                  "experimentos de filtro de relevância e de previsão de volatilidade.",
    )

    # ── 1 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "1", "A história em uma página")

    A.paragrafo(doc,
        "Tudo começou com uma pergunta **sua**, e vale registrar isso porque a pergunta "
        "estava certa. Você notou que o Lucas Leme, o autor do programa que usamos, "
        "**jogou fora** as notícias que não tinham nada a ver com finanças antes de "
        "treinar o programa dele. E percebeu que nós **não jogamos fora nada**: o nosso "
        "índice usa todas as 205.697 notícias que coletamos. Você perguntou se não "
        "teríamos um resultado melhor se limpássemos a base.")

    A.paragrafo(doc,
        "Testamos. **A resposta é sim — e é a primeira coisa que funcionou em nove "
        "tentativas.** As oito anteriores tentavam consertar o programa que lê as "
        "notícias. Todas falharam. Esta não mexeu no programa: mexeu em **quais "
        "notícias** ele lê. E deu certo.")

    A.paragrafo(doc,
        "Mas o resultado tem um limite, e eu preciso ser honesto sobre ele desde o "
        "começo, porque a banca vai perguntar. O índice ficou **medidamente melhor**. "
        "Só que, quando usamos esse índice melhor para de fato **prever** a "
        "volatilidade do dia seguinte, ele **não bateu** um modelo estatístico simples "
        "que não usa notícia nenhuma. Ficar melhor e ser útil são coisas diferentes, e "
        "este documento explica por quê.")

    A.paragrafo(doc,
        "**Se algum termo não estiver claro, é porque eu falhei em explicá-lo — não "
        "porque você deveria saber.**")

    # ── 2 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "2", "Cinco conceitos, antes de qualquer número")

    A.secao(doc, "2.1", "O que é o “índice de sentimento”", nivel=2)
    A.paragrafo(doc,
        "O programa lê uma manchete e dá uma nota: positiva, negativa ou neutra. "
        "Num dia qualquer chegam, digamos, 90 notícias. O **índice de sentimento do "
        "dia** é simplesmente a **média** dessas 90 notas.")
    A.paragrafo(doc,
        "Pense num **termômetro do humor da imprensa**. Se ele marca um valor bem "
        "negativo, a imprensa daquele dia estava pessimista com a Petrobras. É um "
        "número por dia, e a série toda tem 1.988 dias de pregão.")

    A.secao(doc, "2.2", "O que é “volatilidade”", nivel=2)
    A.paragrafo(doc,
        "Volatilidade é **o tamanho do sacolejo do preço**, não a direção dele. Um dia "
        "em que a ação sobe 5% e um dia em que ela cai 5% têm a **mesma** volatilidade "
        "alta. Um dia em que ela varia 0,2% tem volatilidade baixa, subindo ou caindo.")
    A.paragrafo(doc,
        "É a diferença entre perguntar **“para onde vai?”** e perguntar **“vai balançar "
        "muito?”**. A primeira pergunta é sobre direção. A segunda é sobre risco — e é "
        "ela que interessa a bancos, seguradoras e a quem precifica opções.")
    A.paragrafo(doc,
        "Essa distinção é o eixo da sua dissertação inteira. Já sabemos há tempo que a "
        "**direção** é praticamente imprevisível — chegamos a mostrar que nem um leitor "
        "perfeito melhoraria isso. A esperança sempre esteve na **volatilidade**.")

    A.secao(doc, "2.3", "As categorias das notícias", nivel=2)
    A.paragrafo(doc,
        "Toda notícia que coletamos já vem carimbada com uma categoria, decidida na "
        "coleta pelas palavras que ela contém. Três delas importam aqui:")
    A.lista(doc, [
        "**CAT1 — Empresa**: a notícia fala da Petrobras diretamente. Exemplo: “Petrobras "
        "anuncia reajuste da gasolina”. São 64.882 notícias, 32% do total.",
        "**CAT2 — Mercado de Petróleo**: fala do petróleo, do Brent, da OPEP, mas **não "
        "cita a Petrobras**. Exemplo: “OPEP corta produção em 2 milhões de barris”. "
        "São mais 55.910 notícias.",
        "**As demais**: economia geral, câmbio, política econômica, juros. Exemplo: "
        "“EUA e União Europeia excluem a Rússia do sistema Swift”.",
    ])

    A.secao(doc, "2.4", "O que é “correlação”", nivel=2)
    A.paragrafo(doc,
        "Correlação é um número entre 0 e 1 que mede **o quanto duas coisas andam "
        "juntas**. Zero significa que não têm relação nenhuma. Um significa que andam "
        "perfeitamente juntas.")
    A.paragrafo(doc,
        "Uma comparação para calibrar a expectativa: altura e peso de pessoas têm "
        "correlação em torno de 0,7 — alta. Os números que veremos aqui giram em torno "
        "de **0,15**. Isso é **fraco, mas real**, e é o normal em finanças. Se alguém "
        "encontrasse 0,7 entre notícia e preço, a suspeita correta seria de erro no "
        "cálculo, não de descoberta.")

    A.secao(doc, "2.5", "O que quer dizer “estatisticamente significativo”", nivel=2)
    A.paragrafo(doc,
        "Este é o conceito mais importante do documento, e o mais mal-entendido.")
    A.paragrafo(doc,
        "Imagine que você jogou uma moeda 10 vezes e saiu cara 7 vezes. Isso prova que a "
        "moeda é viciada? Não — 7 em 10 acontece por puro acaso com facilidade. Mas se "
        "você jogasse 10.000 vezes e saísse cara 7.000, aí sim: acaso não produz isso.")
    A.paragrafo(doc,
        "O **valor-p** é exatamente essa medida. Ele responde: **“qual a chance de eu ver "
        "esse resultado por pura sorte, se na verdade não houvesse efeito nenhum?”**")
    A.lista(doc, [
        "**p = 0,001** significa 1 chance em 1.000 de ser sorte. É um resultado sólido.",
        "**p = 0,64** significa 64 chances em 100 de ser sorte. Não vale nada.",
        "A convenção da área é: **abaixo de 0,05 conta como resultado; acima, não conta.**",
    ])
    A.paragrafo(doc,
        "Guarde isso: ao longo do documento, sempre que eu disser que algo “não deu”, "
        "quer dizer que o valor-p ficou acima de 0,05 — ou seja, **o resultado cabe "
        "dentro do acaso**.")

    # ── 3 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "3", "Sua pergunta estava certa, mas tinha uma armadilha")

    A.paragrafo(doc,
        "Antes de mostrar o resultado, preciso desfazer uma confusão — e ela vai virar "
        "um parágrafo da dissertação, porque a banca faria essa pergunta.")

    A.paragrafo(doc,
        "**O filtro do Lucas e o nosso filtro não medem a mesma coisa.**")

    A.tabela_abnt(doc, "1", "Dois filtros com o mesmo nome e critérios diferentes",
        ["", "Filtro do Lucas Leme", "Nosso rótulo de relevância"],
        [
            ["Pergunta que faz",
             "“Isso é notícia de finanças?”",
             "“Isso afeta a PETR4?”"],
            ["O que descarta",
             "Política, esporte, texto sem sentido",
             "Notícia financeira que não toca na empresa"],
            ["Quanto descartou",
             "158 de 661 (23,9%)",
             "189 de 300 (63,0%)"],
            ["“Rússia fora do Swift”",
             "MANTÉM (é notícia financeira)",
             "DESCARTA (não cita a Petrobras)"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "Repare na última linha. A mesma notícia recebe destinos opostos. O critério do "
        "Lucas é **mais frouxo** que o nosso, e por isso ele descartou um quarto da base "
        "enquanto o nosso critério descartaria quase dois terços.")

    A.paragrafo(doc,
        "E há um segundo ponto: **nós já fazemos o filtro do Lucas, só que antes**. "
        "Quando coletamos as notícias, elas passam por uma lista de 152 termos ligados a "
        "petróleo, energia e à empresa. Notícia de futebol nunca entrou na nossa base. "
        "Ou seja, o filtro dele já está aplicado no nosso corpus — feito na porta de "
        "entrada, em vez de depois.")

    A.paragrafo(doc,
        "Por isso a pergunta certa não era “devemos copiar o Lucas?”, e sim: **existe um "
        "corte melhor do que usar tudo?** Foi isso que testamos.")

    # ── 4 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "4", "O experimento: três versões do índice")

    A.paragrafo(doc,
        "Montamos o mesmo índice três vezes, cada vez com um conjunto diferente de "
        "notícias, e medimos qual deles anda mais junto com o sacolejo do dia seguinte.")

    A.tabela_abnt(doc, "2", "Quanto cada versão do índice “anda junto” com a volatilidade",
        ["Versão", "Notícias usadas", "% do total", "Correlação"],
        [
            ["A — todas", "205.697", "100%", "0,1385"],
            ["B — empresa + petróleo", "120.792", "59%", "0,1704"],
            ["C — só empresa", "64.882", "32%", "0,1495"],
        ], fonte=FONTE + ". Correlação com a volatilidade do pregão seguinte, "
                        "1.988 pregões.")

    A.paragrafo(doc,
        "**Leia a tabela assim:** a versão B tem o maior número. Ela subiu de 0,1385 "
        "para 0,1704, o que é **23% mais sinal**. E o valor-p dessa diferença é "
        "**0,0010** — uma chance em mil de ser sorte. **Conta como resultado.**")

    A.paragrafo(doc,
        "Já a versão C, que é a mais “limpa” de todas, ficou **pior que a B**. O "
        "valor-p da C contra a A foi 0,475 — ou seja, quase metade de chance de ser "
        "puro acaso. **Não conta.**")

    A.secao(doc, "4.1", "A lição: existe um ponto de equilíbrio", nivel=2)

    A.paragrafo(doc,
        "Este é o achado que vale a seção da dissertação. **Filtrar ajuda, mas filtrar "
        "demais atrapalha.**")

    A.paragrafo(doc,
        "A explicação é econômica e é simples: **a Petrobras produz petróleo**. Quando a "
        "OPEP corta a produção mundial, o preço do barril sobe, e a ação da Petrobras "
        "reage — mesmo que a manchete não mencione a empresa uma única vez. Jogar essa "
        "notícia fora é jogar informação fora.")

    A.paragrafo(doc,
        "É como julgar o desempenho de uma padaria: olhar só as notícias sobre a padaria "
        "é pouco, porque o preço do trigo determina boa parte do resultado dela. Mas "
        "olhar todas as notícias do mundo também é ruim, porque a maioria não tem "
        "relação nenhuma. **O ponto ótimo é a padaria mais o trigo.**")

    A.secao(doc, "4.2", "Uma descoberta incômoda sobre a rotulagem manual", nivel=2)

    A.paragrafo(doc,
        "Há um detalhe aqui que merece atenção, e que reforça o que o Professor Emerson "
        "já havia levantado sobre a rotulagem.")

    A.paragrafo(doc,
        "Quando você rotulou as 300 manchetes à mão, marcou **54 notícias da categoria "
        "petróleo como “não relevantes para a PETR4”**. Era um julgamento razoável: elas "
        "não citam a empresa. Mas a estatística acaba de mostrar que **essas notícias "
        "carregam sinal** — são justamente elas que fazem a versão B ganhar da versão C.")

    A.paragrafo(doc,
        "Ou seja: **o julgamento humano de relevância e a evidência do mercado não "
        "coincidem.** Isso não é um erro seu. É um achado, e um argumento a mais — de "
        "natureza diferente daquele que já tínhamos — sobre os limites de usar rótulo "
        "manual como padrão de referência.")

    # ── 5 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "5", "O teste decisivo: melhor é a mesma coisa que útil?")

    A.paragrafo(doc,
        "Aqui está a parte mais importante do documento, e a que exige mais cuidado.")

    A.paragrafo(doc,
        "Mostramos que o índice B **anda mais junto** com a volatilidade. Mas andar "
        "junto não é prever. Um termômetro que anda junto com a febre só serve se você "
        "**não tivesse outro jeito melhor** de saber que a pessoa está com febre.")

    A.paragrafo(doc,
        "Então fizemos a pergunta honesta: **o índice B ajuda a prever a volatilidade de "
        "amanhã, além do que já se consegue sem notícia nenhuma?**")

    A.secao(doc, "5.1", "O adversário: um modelo que não lê notícia", nivel=2)

    A.paragrafo(doc,
        "Existe um modelo clássico chamado **HAR** que prevê a volatilidade de amanhã "
        "usando **só o histórico do próprio preço**: a volatilidade de ontem, a média da "
        "última semana e a média do último mês. Nenhum texto, nenhuma notícia.")

    A.paragrafo(doc,
        "Ele funciona porque a volatilidade é **grudenta**: depois de um dia agitado, "
        "vem outro dia agitado; depois de uma semana calma, vem mais calmaria. É como "
        "prever o tempo dizendo “amanhã será parecido com hoje” — parece bobo, mas "
        "acerta muito.")

    A.paragrafo(doc,
        "Escolhi esse adversário **de propósito, porque ele é difícil de bater**. Se eu "
        "tivesse escolhido um adversário fraco, o sentimento ganharia fácil e o "
        "resultado não valeria nada. A banca perguntaria “ganhou de quem?” — e a "
        "resposta precisa ser: do modelo que a literatura considera padrão.")

    A.secao(doc, "5.2", "Como a comparação foi feita sem trapaça", nivel=2)

    A.paragrafo(doc,
        "Três cuidados, e vale conhecê-los porque são exatamente o que dá credibilidade "
        "ao resultado:")
    A.lista(doc, [
        "**O modelo nunca vê o futuro.** Para prever o dia 1.500, ele é reconstruído "
        "usando apenas os dias 1 a 1.499. Depois avança um dia e refaz tudo. São 795 "
        "previsões feitas assim, uma a uma.",
        "**Medimos o erro de duas maneiras diferentes.** Uma delas, chamada QLIKE, é a "
        "preferida em volatilidade porque pune mais duramente quem erra para baixo num "
        "dia turbulento — que é o erro que quebra quem gere risco.",
        "**Testamos se a diferença é real.** O teste de Diebold-Mariano responde se um "
        "modelo erra genuinamente menos que o outro, ou se a diferença cabe no acaso.",
    ])

    A.secao(doc, "5.3", "O resultado", nivel=2)

    A.tabela_abnt(doc, "3", "Erro de previsão da volatilidade em 795 pregões",
        ["Modelo", "Erro (EQM)", "Erro (QLIKE)", "Veredito"],
        [
            ["HAR sozinho — sem notícia", "0,16451", "−7,3852", "referência"],
            ["HAR + índice completo (A)", "0,16546", "−7,3897", "piorou o EQM"],
            ["HAR + índice filtrado (B)", "0,16406", "−7,3891", "melhorou de leve"],
        ], fonte=FONTE + ". Números menores indicam previsão melhor.")

    A.paragrafo(doc,
        "**Olhe as terceiras casas decimais.** O índice filtrado melhorou — mas melhorou "
        "pouquíssimo. E o teste confirmou o que os olhos sugerem: **valor-p de 0,64**. "
        "Ou seja, **essa melhora cabe inteiramente dentro do acaso. Não conta.**")

    A.paragrafo(doc,
        "Testamos ainda se o ganho apareceria pelo menos nos dias mais turbulentos, que "
        "é onde previsão de risco realmente importa. Aparece uma tendência na direção "
        "certa, mas o valor-p foi 0,18. **Também não conta.**")

    A.secao(doc, "5.4", "Duas coisas que DERAM certo, mesmo assim", nivel=2)

    A.paragrafo(doc,
        "Não é um resultado vazio. Duas coisas passaram no teste, e as duas vão para a "
        "dissertação:")

    A.paragrafo(doc,
        "**Primeira: o índice filtrado ganha do índice completo.** Comparando B contra A "
        "diretamente, o valor-p foi **0,0041**. Isso conta. Ou seja, se você **vai** usar "
        "sentimento — e você vai, é o tema da dissertação —, o filtrado é comprovadamente "
        "a melhor escolha.")

    A.paragrafo(doc,
        "**Segunda: o sentimento tem efeito real, e no sentido que a teoria prevê.** "
        "Medindo a relação sobre a série inteira, o índice filtrado tem valor-p de "
        "**0,0002** — duas chances em dez mil de ser acaso. E o sinal é negativo, o que "
        "significa: **quanto mais pessimista a imprensa hoje, maior o sacolejo amanhã.** "
        "É exatamente o comportamento que a literatura de finanças documenta há décadas.")

    A.paragrafo(doc,
        "Note que o índice filtrado tem esse efeito **mais bem medido** que o completo "
        "(0,0002 contra 0,0020), embora use 41% menos notícias. Menos ruído, medida mais "
        "firme.")

    # ── 6 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "6", "Como pode ser real e não ajudar a prever?")

    A.paragrafo(doc,
        "Essa é a pergunta que o Professor Julio ou o Professor Emerson farão, e a "
        "resposta é a parte mais interessante do trabalho.")

    A.paragrafo(doc,
        "A analogia que uso é a do **guarda-chuva na rua**. Se você olhar pela janela e "
        "vir muita gente com guarda-chuva, isso realmente informa sobre a chuva — a "
        "relação é genuína. Mas se você **já tem** um barômetro na parede, os "
        "guarda-chuvas não acrescentam nada: eles só confirmam o que o barômetro já "
        "dizia.")

    A.paragrafo(doc,
        "É exatamente o nosso caso. **Dia turbulento é também dia de noticiário "
        "intenso** — as duas coisas acontecem juntas. Então, quando o modelo HAR olha "
        "para a volatilidade de ontem, ele já está capturando, de forma indireta, boa "
        "parte da informação que as notícias carregam. O sentimento e o histórico de "
        "preço são **fontes redundantes**.")

    A.paragrafo(doc,
        "Isso **não invalida** a sua tese. A tese central da dissertação é que **o "
        "sentimento informa o risco, e não a direção** — e ela continua de pé, sustentada "
        "pelo valor-p de 0,0002 e pelos testes de causalidade que já estavam no "
        "Capítulo 4.")

    A.paragrafo(doc,
        "O que os dados acrescentam é um **limite necessário**: informar não é o mesmo "
        "que melhorar a previsão quando o adversário é um modelo econométrico maduro. "
        "Reconhecer isso é mais valioso, cientificamente, do que vender como ganho "
        "aquilo que os dados não sustentam. É esse tipo de honestidade que distingue "
        "uma dissertação sólida.")

    # ── 7 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "7", "E a direção do preço?")

    A.paragrafo(doc,
        "Também testamos, por completude: rodamos o pipeline inteiro de previsão de "
        "direção com o índice filtrado, mudando **só** o índice e mantendo tudo o mais "
        "igual — mesmo modelo, mesmos parâmetros, mesma divisão dos dados.")

    A.paragrafo(doc,
        "**Não mudou absolutamente nada.** A acurácia ficou em 52,31% nos dois casos. "
        "O teste comparativo deu valor-p de **1,0000** — o valor máximo possível, "
        "indiferença perfeita.")

    A.paragrafo(doc,
        "Isso já era esperado, e confirma por um caminho independente aquilo que o teste "
        "de teto havia mostrado: **o gargalo da direção não é o texto.** É a eficiência "
        "do mercado. A direção diária de uma ação líquida é quase um cara ou coroa, e "
        "nenhuma limpeza de notícia muda isso. Está encerrado esse caminho — e encerrar "
        "um caminho com evidência também é resultado.")

    # ── 8 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "8", "O placar das nove tentativas")

    A.paragrafo(doc,
        "Vale ver o conjunto, porque o padrão que aparece é ele próprio um achado:")

    A.tabela_abnt(doc, "4", "As nove tentativas de melhorar o componente de sentimento",
        ["#", "O que tentamos", "Onde mexia", "Resultado"],
        [
            ["1", "Calibrar o índice (correção de viés)", "no modelo", "não ajudou a prever"],
            ["2", "Abstenção nos casos duvidosos", "no modelo", "falhou"],
            ["3", "Reponderar as classes", "no modelo", "falhou"],
            ["4", "Corrigir as manchetes em CAIXA ALTA", "no modelo", "ganho desprezível"],
            ["5", "Trocar por codificador maior", "no modelo", "falhou"],
            ["6", "Granularidade mais fina", "no modelo", "piorou"],
            ["7", "Comitê de modelos", "no modelo", "piorou"],
            ["8", "Adaptar ao domínio (MLM)", "no modelo", "piorou (p=0,022)"],
            ["9", "FILTRO DE RELEVÂNCIA", "NO CORPUS", "FUNCIONOU (p=0,001)"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**Olhe a coluna do meio.** As oito primeiras tentativas mexiam no **modelo** — "
        "no funcionário que lê as notícias. Todas falharam. A nona mexeu no **material "
        "que ele lê**. Essa funcionou.")

    A.paragrafo(doc,
        "Essa assimetria é um resultado por si só, e é o que a dissertação passa a "
        "afirmar: **em um problema como este, o esforço rende mais na curadoria dos "
        "dados do que no aperfeiçoamento do modelo.** É uma conclusão que contraria a "
        "intuição corrente da área, e é sustentada por nove experimentos documentados.")

    # ── 9 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "9", "O que já foi feito e o que vem agora")

    A.paragrafo(doc, "**Já está pronto e no repositório:**")
    A.lista(doc, [
        "Os três experimentos, com código comentado e resultados salvos em arquivo "
        "(scripts `filtrar_ism_por_relevancia.py`, `07_modelagem_ism_filtrado_petr4.py` "
        "e `08_previsao_volatilidade_ism_filtrado.py`).",
        "A nova seção 4.k da dissertação, com as três tabelas, a discussão e a "
        "delimitação honesta do alcance.",
        "A atualização do Capítulo 5: nova linha na tabela de contribuições, revisão da "
        "limitação sobre as intervenções e uma nova frente de trabalho futuro.",
        "A referência bibliográfica do estimador de Parkinson, que faltava.",
    ])

    A.paragrafo(doc, "**O que proponho como próximo passo:**")
    A.lista(doc, [
        "**Substituir o corte binário por um peso contínuo.** Hoje a notícia entra ou não "
        "entra no índice. Faria mais sentido cada notícia entrar com um **peso** "
        "proporcional à sua relevância — o que evita jogar fora 41% do corpus e "
        "transforma a relevância em quantidade medida, não em rótulo opinativo.",
        "**Aprender esse peso a partir da reação do mercado**, em vez de defini-lo por "
        "lista de palavras. Isso responderia diretamente à objeção do Professor Emerson: "
        "a relevância deixaria de depender do julgamento de um anotador.",
        "**Levar o índice filtrado para as análises de volatilidade que já existem** no "
        "Capítulo 4 — a regressão quantílica e a causalidade de Granger — para verificar "
        "se o ganho de sinal aparece também ali.",
    ])

    A.paragrafo(doc,
        "As três propostas seguem a lição da tabela 4: **mexer no corpus, não no "
        "modelo.**")

    # ── 10 ───────────────────────────────────────────────────────────────────
    A.secao(doc, "10", "Se você tiver dois minutos para explicar isso a alguém")

    A.paragrafo(doc,
        "Um roteiro curto, para a conversa com os orientadores:")

    A.lista(doc, [
        "“Eu notei que a pesquisa de referência descartava notícias irrelevantes e a "
        "nossa não descartava. Testei se isso importava.”",
        "“Importa. Usando só notícias da empresa e do mercado de petróleo, o sinal do "
        "índice sobe 23%, com p = 0,001.”",
        "“Mas há um ponto de equilíbrio: restringir só à Petrobras piora. As notícias do "
        "petróleo importam mesmo sem citar a empresa — ela é produtora.”",
        "“Aí veio a parte honesta: fui testar se isso melhora a previsão de volatilidade "
        "contra o modelo HAR, que não usa notícia. Não melhora de forma significativa.”",
        "“O efeito do sentimento é real e no sentido certo — p = 0,0002 —, mas é "
        "redundante com o histórico de volatilidade, porque dia agitado é dia de muita "
        "notícia.”",
        "“O achado mais forte é outro: em nove tentativas de melhorar o sentimento, as "
        "oito que mexeram no modelo falharam e a única que mexeu na seleção dos dados "
        "funcionou.”",
    ])

    doc.save(SAIDA)
    print(f"[OK] Documento gerado: {SAIDA}")


if __name__ == "__main__":
    main()
