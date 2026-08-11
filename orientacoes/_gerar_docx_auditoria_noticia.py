# -*- coding: utf-8 -*-
# ==============================================================================
#   Gera a explicação em linguagem comum da auditoria notícia a notícia
#   Saída: orientacoes/EXPLICACAO_SIMPLES_AUDITORIA_NOTICIA.docx
#
#   Público: leitor sem formação em aprendizado de máquina nem em estatística.
#   Regra de escrita: nenhum termo técnico aparece sem ser explicado antes,
#   com analogia. Todo número vem acompanhado do que significa e do que NÃO
#   significa.
# ==============================================================================
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(RAIZ / "src" / "comum"))

import abnt_docx as A  # noqa: E402

FONTE = "Elaborado pelo autor (2026)"
SAIDA = AQUI / "EXPLICACAO_SIMPLES_AUDITORIA_NOTICIA.docx"


def main() -> None:
    doc = A.novo_documento()

    A.capa(
        doc,
        titulo="A conferência que faltava",
        subtitulo="Notícia por notícia, o sentimento acertou o pregão seguinte? "
                  "E o que a resposta revelou sobre toda a pesquisa",
        autor="Vanderlei Barbosa da Silva",
        orientador="Orientador: Prof. Dr. Julio Cesar Nievola",
        instituicao="PUCPR — Programa de Pós-Graduação em Informática (PPGIa)",
        descricao="Documento escrito para ser entendido sem conhecimento prévio de "
                  "aprendizado de máquina ou de estatística. Todo termo técnico é "
                  "explicado quando aparece pela primeira vez, com analogia. "
                  "Elaborado em 10 de agosto de 2026, a partir da auditoria direta "
                  "das 205.697 notícias contra os 1.989 pregões da PETR4.",
    )

    # ── 1 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "1", "A história em uma página")

    A.paragrafo(doc,
        "Você fez uma observação que era, na verdade, uma cobrança justa: **temos as "
        "notícias, temos os preços, e nunca conferimos diretamente se o sentimento "
        "acertou o pregão do dia seguinte.** Estava certo. Tudo que a dissertação "
        "media até agora passava por um modelo no meio do caminho.")

    A.paragrafo(doc,
        "Conferi. Notícia por notícia, todas as 205.697, contra todos os 1.989 dias de "
        "pregão. E o resultado mudou a forma de contar a história da pesquisa.")

    A.paragrafo(doc, "Três descobertas, em ordem de importância:")

    A.lista(doc, [
        "**O sentimento acompanha o mercado muito mais do que o antecede.** No mesmo "
        "dia da notícia o sinal é limpo e ordenado; no dia seguinte ele quase "
        "desaparece. Boa parte do que parecia previsão era jornalismo descrevendo o "
        "que já tinha acontecido.",
        "**A regra ingênua perde feio.** Apostar na alta depois de notícia positiva e "
        "na baixa depois de negativa acerta 47,6% — pior que o mercado (52,8%) e pior "
        "que cara ou coroa.",
        "**O efeito do sentimento é de CAUDA.** Ele existe nos dias excepcionais e "
        "some no dia comum. E essa descoberta **unifica** vários resultados soltos da "
        "sua dissertação numa frase só.",
    ])

    A.paragrafo(doc,
        "A terceira é a mais valiosa, e é o motivo pelo qual este trabalho valeu a "
        "pena. **Se algum termo não estiver claro, é porque eu falhei em explicá-lo — "
        "não porque você deveria saber.**")

    # ── 2 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "2", "Dois cuidados sem os quais o resultado seria mentira")

    A.secao(doc, "2.1", "Cuidado 1: qual pregão a notícia pode afetar", nivel=2)

    A.paragrafo(doc,
        "Este é o cuidado mais importante de todos, e é fácil de entender com um "
        "exemplo.")

    A.paragrafo(doc,
        "Imagine uma notícia publicada às **16h de uma terça** dizendo “Petrobras "
        "despenca com anúncio do governo”. Se eu conferir essa notícia contra o "
        "fechamento da própria terça, vou encontrar um acerto perfeito. Mas isso não é "
        "previsão — **é o jornal descrevendo o que já aconteceu.** Seria trapaça "
        "contar isso como acerto.")

    A.paragrafo(doc,
        "Agora imagine a mesma notícia publicada às **18h**, depois do fechamento. Aí "
        "ela só pode afetar a quarta-feira. Isso sim é previsão legítima.")

    A.paragrafo(doc,
        "Por isso separei tudo em dois momentos, e a comparação entre eles virou o "
        "achado principal:")

    A.lista(doc, [
        "**P0 — o pregão que reage.** Para notícia da manhã, é o mesmo dia. Mistura "
        "reação e previsão. Serve de diagnóstico, **não** de prova.",
        "**P1 — o pregão seguinte.** Vem depois da notícia em todos os casos, sem "
        "exceção. **É a prova.**",
    ])

    A.paragrafo(doc,
        "Do total, 54.259 notícias (26%) saíram depois das 17h e tiveram o pregão de "
        "referência deslocado. E o programa trata fim de semana e feriado: notícia de "
        "sábado vai para a segunda, nunca para a sexta anterior.")

    A.secao(doc, "2.2", "Cuidado 2: 205 mil notícias, mas só 1.989 dias", nivel=2)

    A.paragrafo(doc,
        "Num dia agitado saem 200 notícias, todas apontando para o mesmo pregão. Se eu "
        "contar “acerto” 200 vezes, estou contando **um único evento** duzentas vezes.")

    A.paragrafo(doc,
        "É como perguntar a opinião de 200 pessoas de uma mesma família e apresentar "
        "isso como uma pesquisa com 200 entrevistados. O número parece grande, mas a "
        "informação real é de **uma família só**.")

    A.paragrafo(doc,
        "Esse erro tem nome — **pseudorreplicação** — e ele infla os testes de forma "
        "brutal. Por isso reporto duas taxas: uma **por notícia** (só para descrever) "
        "e uma **por pregão** (a única sobre a qual faço teste estatístico). Foi um "
        "erro que eu mesmo cometi na primeira versão deste teste e tive de corrigir.")

    # ── 3 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "3", "Descoberta 1: o sentimento acompanha, não antecipa")

    A.paragrafo(doc,
        "Esta é a tabela mais importante do documento. Ela mostra, sem modelo nenhum "
        "no meio, o que aconteceu com a ação depois de cada tipo de notícia.")

    A.paragrafo(doc,
        "**Referência para comparar:** no período todo, a PETR4 subiu em **52,78%** "
        "dos pregões. Qualquer número perto disso não significa nada.")

    A.tabela_abnt(doc, "1", "O que aconteceu depois de cada tipo de notícia",
        ["Momento", "Sentimento", "Notícias", "A ação subiu", "Retorno médio"],
        [
            ["P0 — mesmo dia", "Positivo", "28.755", "55,0%", "+0,239%"],
            ["P0 — mesmo dia", "Neutro", "77.214", "53,2%", "+0,094%"],
            ["P0 — mesmo dia", "Negativo", "99.728", "51,6%", "−0,041%"],
            ["P1 — dia seguinte", "Positivo", "28.755", "52,5%", "+0,098%"],
            ["P1 — dia seguinte", "Neutro", "77.214", "52,4%", "+0,108%"],
            ["P1 — dia seguinte", "Negativo", "99.728", "51,5%", "+0,079%"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**Leia a metade de cima primeiro.** Ela é bonita: 55,0% → 53,2% → 51,6%, "
        "descendo certinho. E o retorno médio até **muda de sinal** — positivo depois "
        "de notícia boa, negativo depois de notícia ruim. O sentimento separa os dias, "
        "e separa na direção certa.")

    A.paragrafo(doc,
        "**Agora a metade de baixo.** A ordem some. Positivo (52,5%) e Neutro (52,4%) "
        "ficam praticamente iguais — um décimo de ponto de diferença. E todos os três "
        "grudam perto dos 52,78% da referência, ou seja, **perto de nada**.")

    A.paragrafo(doc,
        "**O que isso quer dizer, em português:** o sinal que aparecia no mesmo dia era, "
        "em boa parte, a imprensa **narrando** um movimento em curso. Quando exijo que "
        "a notícia venha antes do pregão, o sinal evapora.")

    A.paragrafo(doc,
        "Não é um resultado ruim de se ter — é um resultado **honesto** de se ter. "
        "Muita pesquisa da área não faz essa separação e reporta o número da metade de "
        "cima como se fosse previsão.")

    # ── 4 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "4", "Descoberta 2: a regra ingênua perde para o mercado")

    A.paragrafo(doc,
        "Testei a regra mais óbvia que alguém tiraria do sentimento: **notícia boa, "
        "aposta na alta; notícia ruim, aposta na baixa; notícia neutra, não aposta.**")

    A.tabela_abnt(doc, "2", "Desempenho da regra ingênua (referência: 52,78%)",
        ["Momento", "Por notícia", "Por pregão", "Veredito"],
        [
            ["P0 — mesmo dia", "49,89%", "47,69%", "perde, p < 0,0001"],
            ["P1 — dia seguinte", "49,38%", "47,59%", "perde, p < 0,0001"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**47,6% é ruim de dois jeitos.** É cinco pontos abaixo do mercado (52,78%) e "
        "está abaixo até de cara ou coroa (50%). O intervalo de confiança vai de 45,4% "
        "a 49,8% — nem a ponta de cima chega aos 50%.")

    A.secao(doc, "4.1", "Por que perde? Não é magia, é aritmética", nivel=2)

    A.paragrafo(doc,
        "A explicação é a combinação de duas coisas que já sabíamos separadamente:")

    A.lista(doc, [
        "**O programa é pessimista demais.** Ele marca 48,5% das notícias como "
        "negativas e só 14,0% como positivas. Isso já estava documentado — é o viés de "
        "87% que medimos meses atrás.",
        "**A ação subiu mais do que caiu** no período: 52,78% dos dias.",
    ])

    A.paragrafo(doc,
        "Junte os dois: a regra aposta na **baixa** quase sempre, num papel que "
        "**subiu** na maior parte do tempo. **Ela perde por construção, não por falta "
        "de informação no texto.**")

    A.paragrafo(doc,
        "É como um termômetro descalibrado que marca 3 graus a menos: ele até pode "
        "sentir quando esquenta e quando esfria, mas se você usar o número cru para "
        "decidir se leva casaco, vai errar sempre para o mesmo lado.")

    A.secao(doc, "4.2", "“Mas o Capítulo 4 diz 54,5%. Isso é contradição?”", nivel=2)

    A.paragrafo(doc,
        "**Não, e é importante você saber responder isso**, porque a banca vai "
        "perguntar.")

    A.paragrafo(doc,
        "São duas coisas diferentes. Os 47,6% vêm de uma **regra fixa** aplicada ao "
        "rótulo cru de cada notícia. Os 54,5% vêm de um **modelo treinado** que combina "
        "o índice de sentimento com o retorno e a volatilidade dos dias anteriores, e "
        "que **aprendeu**, olhando o passado, a **ponderar** o sentimento em vez de "
        "obedecê-lo ao pé da letra.")

    A.paragrafo(doc,
        "A comparação entre os dois números, na verdade, **valoriza** a sua "
        "metodologia: ela mostra que o texto sozinho é inútil para direção, e que o "
        "ganho vem justamente da etapa de aprendizado que você construiu.")

    A.secao(doc, "4.3", "Procurei uma saída em todo lugar. Não tem.", nivel=2)

    A.paragrafo(doc,
        "Antes de aceitar o resultado, fatiei os dados de três formas para ver se "
        "algum pedaço funcionava:")

    A.lista(doc, [
        "**Por categoria:** de 48,09% (Governança) a 50,01% (Mercado de Petróleo). "
        "Todas abaixo da referência.",
        "**Por horário:** as notícias de depois das 17h — em tese as melhores, porque "
        "o mercado ainda não as viu — deram 49,52%, contra 49,33% das outras. "
        "Praticamente igual.",
        "**Por confiança do programa:** aqui veio a surpresa desagradável.",
    ])

    A.paragrafo(doc,
        "**A confiança funciona ao contrário.** Eu esperava que, quando o programa "
        "estivesse mais seguro, ele acertasse mais. É o oposto: 50,18% quando ele está "
        "menos seguro, caindo direto até 48,83% quando está mais seguro. A tendência é "
        "pequena, mas é real (p = 0,0020).")

    A.paragrafo(doc,
        "**Ou seja: o programa erra mais justamente quando está mais convicto.** Isso "
        "conversa com aquele defeito que achamos no código publicado — o número de "
        "confiança que ele devolve é calculado por uma fórmula errada (sigmoide em vez "
        "de softmax). Duas evidências independentes apontando para o mesmo problema.")

    # ── 5 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "5", "Uma constatação que me surpreendeu")

    A.paragrafo(doc,
        "Ao agrupar os dias pelo sentimento predominante, esbarrei em algo que eu não "
        "esperava e que precisa entrar na dissertação como limitação:")

    A.tabela_abnt(doc, "3", "Sentimento predominante dos 1.989 pregões",
        ["Sentimento do dia", "Pregões"],
        [
            ["Negativo", "1.488"],
            ["Neutro", "457"],
            ["Positivo", "ZERO"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**Em quase oito anos, não existe um único dia em que as notícias positivas "
        "tenham sido maioria.** Nem um. E o índice de sentimento diário é negativo em "
        "**100%** dos pregões.")

    A.paragrafo(doc,
        "Isso tem uma consequência séria e você precisa declará-la: **a pesquisa nunca "
        "observa o que acontece depois de um dia de imprensa realmente otimista** — não "
        "porque esses dias não existam no mundo, mas porque o programa não os produz. "
        "Tudo o que medimos são variações de **grau de pessimismo**.")

    A.paragrafo(doc,
        "É honestidade obrigatória, e também um alerta útil para quem vier depois: "
        "qualquer pesquisa que use esse programa para montar um índice ao longo do "
        "tempo deveria conferir isso antes.")

    # ── 6 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "6", "Descoberta 3: o efeito é de cauda — e isso muda tudo")

    A.paragrafo(doc,
        "Aqui está a parte que faz este trabalho valer a pena.")

    A.paragrafo(doc,
        "Ao testar a volatilidade por dia, encontrei o sinal na direção certa — dias "
        "pessimistas são seguidos de 4,8% mais sacolejo — **mas sem significância** "
        "(p = 0,210). Só que o outro script tinha achado uma correlação **claramente "
        "significativa**. Dois resultados aparentemente brigando.")

    A.paragrafo(doc,
        "**Não brigam. E entender por quê foi a descoberta.**")

    A.tabela_abnt(doc, "4", "Quatro medidas da MESMA relação, nos MESMOS 1.989 pregões",
        ["Medida", "Valor", "Deu?", "O que ela enxerga"],
        [
            ["Correlação de Pearson", "−0,1309", "SIM (p<0,0001)", "leva em conta o tamanho"],
            ["Correlação de Spearman", "−0,0268", "NÃO (p=0,237)", "só a ordem dos dias"],
            ["Razão entre as MÉDIAS", "1,237×", "—", "sensível aos extremos"],
            ["Razão entre as MEDIANAS", "1,048×", "—", "o dia típico"],
        ], fonte=FONTE)

    A.secao(doc, "6.1", "O que essa tabela está dizendo", nivel=2)

    A.paragrafo(doc,
        "As duas correlações medem a mesma relação, mas de formas diferentes. **Pearson "
        "leva em conta o tamanho** dos números. **Spearman joga fora os tamanhos** e "
        "olha só a ordem — quem foi o dia mais pessimista, o segundo mais, e assim por "
        "diante.")

    A.paragrafo(doc,
        "Pearson encontra a relação. Spearman não encontra. **Quando isso acontece, a "
        "conclusão é sempre a mesma: a relação está nos casos extremos.**")

    A.paragrafo(doc,
        "A comparação de médias e medianas confirma pelo mesmo caminho. A razão entre "
        "**médias** é 1,237 — os dias pessimistas têm 24% mais volatilidade. Mas a razão "
        "entre **medianas**, que descreve o dia comum, é só 1,048 — 5%. **Cinco vezes "
        "menor.**")

    A.paragrafo(doc,
        "Uma analogia. Se você comparar a **renda média** de dois bairros, pode "
        "encontrar uma diferença enorme por causa de dois moradores milionários. Se "
        "comparar a **renda mediana** — a do morador do meio — a diferença some. É "
        "exatamente o mesmo fenômeno: **a diferença existe, mas está concentrada em "
        "poucos casos excepcionais.**")

    A.secao(doc, "6.2", "Por que isso é bom para a sua dissertação", nivel=2)

    A.paragrafo(doc,
        "Porque **você já tinha achado exatamente isso, por outro caminho, e não tinha "
        "percebido que era a mesma coisa.**")

    A.paragrafo(doc,
        "A regressão quantílica do Capítulo 4 mostrou que o sentimento tem efeito forte "
        "(+542 pontos-base) nos **5% piores dias** e efeito **zero** nos dias bons. "
        "Aquilo era sobre o **retorno**. Isto aqui é sobre a **volatilidade**. Métodos "
        "diferentes, dados tratados de formas diferentes — **e os dois apontam para a "
        "mesma região da distribuição: os extremos.**")

    A.paragrafo(doc,
        "Quando duas análises independentes chegam ao mesmo lugar, o achado ganha uma "
        "solidez que nenhuma das duas teria sozinha. E permite escrever, numa frase só, "
        "o que a dissertação vinha dizendo em pedaços:")

    A.citacao_longa(doc,
        "O sentimento das notícias não move o pregão comum; ele importa nos extremos.",
        "Síntese dos resultados desta pesquisa")

    A.paragrafo(doc,
        "**Essa frase é a sua tese.** Ela explica de uma vez: por que a direção não "
        "funciona (a maioria dos dias é comum), por que a média dava significância "
        "marginal (a média dilui o extremo no comum), por que a regressão quantílica "
        "funcionou tão bem (ela olha direto para a cauda) e por que o sentimento não "
        "bate o HAR na previsão do dia a dia (o dia a dia é justamente onde ele não "
        "atua).")

    # ── 7 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "7", "Testei se dava para transformar isso em decisão. Não dá.")

    A.paragrafo(doc,
        "Última verificação, a mais prática de todas: dá para usar o sentimento para "
        "**avisar** que amanhã será um dia agitado?")

    A.paragrafo(doc,
        "Montei o alarme mais simples possível: marcar como “dia agitado” os 30% de "
        "dias mais pessimistas. O limite foi calculado **só com os dados antigos**, e "
        "testado nos dias mais recentes — sem espiar o futuro.")

    A.lista(doc, [
        "**Alarme pelo pessimismo do índice:** acerta em 32,2% das vezes que dispara. "
        "Marcar dias no chute acertaria 34,4%. **O alarme é pior que o chute** "
        "(p = 0,491).",
        "**Alarme pelo volume de notícias** (a ideia de que muita notícia = dia "
        "agitado): também não funciona (p = 0,222).",
    ])

    A.paragrafo(doc,
        "Coerente com tudo o resto: o efeito é **real mas de cauda**, e um alarme "
        "precisa funcionar no dia a dia para ter valor. **Real e útil são coisas "
        "diferentes** — este documento inteiro é sobre essa distinção.")

    # ── 8 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "8", "O que mudou na dissertação")

    A.paragrafo(doc,
        "Nenhum resultado anterior foi invalidado. O que mudou foi a **interpretação**, "
        "que ficou mais unificada e mais defensável:")

    A.lista(doc, [
        "**Seção nova (4.l)** no Capítulo 4, com as quatro tabelas e a auditoria "
        "completa.",
        "**Capítulo 5:** duas linhas novas na tabela de contribuições, um parágrafo "
        "sobre o efeito de cauda e uma limitação nova (a ausência de dias positivos).",
        "**A tese central ganhou uma formulação mais precisa.** Antes: “o sentimento "
        "informa risco, não direção”. Agora: “o sentimento não move o pregão comum; "
        "ele importa nos extremos” — que é mais forte, porque **explica** os "
        "resultados anteriores em vez de apenas somar-se a eles.",
    ])

    A.paragrafo(doc,
        "E um ponto para você defender com tranquilidade: **esta seção não tem um "
        "único resultado favorável, e é por isso que ela é boa.** Ela delimita, com "
        "números que qualquer um pode conferir na planilha, o que o sentimento textual "
        "pode e não pode entregar. Banca reconhece esse tipo de rigor.")

    # ── 9 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "9", "Se você tiver dois minutos para explicar isso")

    A.lista(doc, [
        "“Fui conferir direto, sem modelo no meio: notícia por notícia, contra o "
        "pregão seguinte. 205 mil notícias, 1.989 pregões.”",
        "“Separei o mesmo dia do dia seguinte, porque notícia da tarde descreve o que "
        "já aconteceu. No mesmo dia o sinal é limpo; no dia seguinte ele some.”",
        "“A regra ingênua acerta 47,6%, contra 52,8% do mercado. Perde porque o "
        "programa é pessimista demais e o papel subiu no período — é aritmética do "
        "viés, não falta de informação.”",
        "“Descobri que não existe um único dia, em oito anos, com maioria de notícias "
        "positivas. Isso vira limitação declarada.”",
        "“E o principal: Pearson acha a relação com a volatilidade, Spearman não acha. "
        "Isso quer dizer que o efeito está nos extremos, não no dia comum.”",
        "“Que é exatamente o que a regressão quantílica já tinha mostrado para o "
        "retorno. Dois métodos independentes, mesma conclusão: o sentimento importa "
        "nos extremos.”",
    ])

    doc.save(SAIDA)
    print(f"[OK] Documento gerado: {SAIDA}")


if __name__ == "__main__":
    main()
