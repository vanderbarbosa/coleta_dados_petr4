# -*- coding: utf-8 -*-
# ==============================================================================
#   Explicação completa, do zero — para apresentar aos orientadores
#   Saída: CVM/04_EXPLICACAO_COMPLETA.docx
#
#   Escrito para ser lido por quem não acompanhou nada do processo. Cada termo
#   técnico aparece com analogia na primeira vez.
# ==============================================================================
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(RAIZ / "src" / "comum"))

import abnt_docx as A  # noqa: E402

FONTE = "Elaborado pelo autor (2026)"
SAIDA = AQUI / "04_EXPLICACAO_COMPLETA.docx"


def main() -> None:
    doc = A.novo_documento()

    A.capa(
        doc,
        titulo="O que foi feito, do começo ao fim",
        subtitulo="Explicação completa do experimento com os comunicados da CVM — "
                  "escrita para ser entendida sem conhecimento prévio",
        autor="Vanderlei Barbosa da Silva",
        orientador="Orientador: Prof. Dr. Julio Cesar Nievola",
        instituicao="PUCPR — Programa de Pós-Graduação em Informática (PPGIa)",
        descricao="Documento de apoio à reunião com os orientadores. Explica cada "
                  "etapa do experimento e cada resultado em linguagem comum, com "
                  "analogia para todo termo técnico na primeira vez em que aparece. "
                  "Acompanha a planilha 05_PAINEL_RESULTADOS.xlsx. Elaborado em 17 de "
                  "setembro de 2026.",
    )

    # ── 1 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "1", "A pergunta, em uma frase")

    A.paragrafo(doc,
        "**Quando uma empresa publica uma notícia importante, o preço da ação dela se "
        "mexe no dia seguinte? E dá para saber, lendo a notícia, se vai subir ou "
        "descer?**")

    A.paragrafo(doc,
        "São duas perguntas, e elas são bem diferentes uma da outra. A primeira é "
        "**“mexeu?”**. A segunda é **“para que lado?”**. Guardar essa diferença é o que "
        "faz o resto do documento fazer sentido.")

    # ── 2 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "2", "De onde vieram as notícias")

    A.paragrafo(doc,
        "A **CVM** — Comissão de Valores Mobiliários — é o órgão do governo que "
        "fiscaliza a bolsa. **Pense nela como o cartório do mercado de capitais:** toda "
        "empresa que tem ação negociada é obrigada a registrar ali qualquer fato "
        "importante sobre si mesma.")

    A.paragrafo(doc,
        "Esse registro tem nome e tem lei. A **Resolução CVM nº 44** manda a empresa "
        "divulgar todo fato **capaz de influir na cotação** da ação. Quando a empresa "
        "protocola um documento desses, ela escolhe em qual gaveta ele entra. Duas "
        "gavetas nos interessam:")

    A.tabela_abnt(doc, "1", "As duas gavetas que usamos",
        ["Gaveta", "O que é", "Peso"],
        [
            ["Fato Relevante",
             "algo que a empresa declara ser capaz de mexer no preço da ação",
             "o mais forte que existe"],
            ["Comunicado ao Mercado",
             "informação que a empresa acha que o mercado deve saber",
             "um degrau abaixo"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**Quem decide em qual gaveta o documento entra é a própria empresa** — o "
        "Diretor de Relações com Investidores —, sob obrigação legal e sob fiscalização "
        "da CVM. **Não fui eu quem classificou nada, e nem a CVM:** o rótulo já vem "
        "pronto no arquivo, e eu apenas separei essas duas gavetas das outras dezoito.")

    A.paragrafo(doc,
        "**Por que isso é bom para a pesquisa:** durante meses eu tentei descobrir "
        "quais notícias eram relevantes. Aqui a relevância **já vem declarada, com "
        "força de lei, por quem conhece o fato por dentro.**")

    A.secao(doc, "2.1", "Quanto foi coletado", nivel=2)

    A.tabela_abnt(doc, "2", "A base",
        ["", "Quantidade"],
        [
            ["documentos baixados da CVM, de 2018 a 2026", "89.902"],
            ["destes, Fatos Relevantes", "23.009"],
            ["empresas distintas", "1.108"],
            ["empresas que consegui ligar a um papel da B3", "62"],
            ["papéis com histórico de preço", "57"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "São **dados abertos oficiais**, baixados do portal `dados.cvm.gov.br`. Não há "
        "raspagem de sítio, não há bloqueio, não há termo de uso a discutir.")

    # ── 3 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "3", "A parte esperta: só a notícia da noite")

    A.paragrafo(doc,
        "Aqui está a ideia que dá força a tudo, e foi sugestão dos senhores.")

    A.paragrafo(doc,
        "**O problema de estudar notícia e preço é saber quem veio primeiro.** Se a "
        "notícia sai às 11h da manhã e a ação cai às 11h30, foi a notícia que derrubou? "
        "Ou o preço já estava caindo e a empresa correu para explicar?")

    A.paragrafo(doc,
        "**A solução: usar só o que foi publicado depois que o mercado fechou.**")

    A.paragrafo(doc,
        "**A analogia:** é como trancar todo mundo do lado de fora do estádio, colocar "
        "a notícia no telão, e só então abrir os portões. **Ninguém pôde reagir antes.** "
        "O que acontecer na abertura do dia seguinte só pode ser resposta àquilo.")

    A.paragrafo(doc,
        "Para fazer esse recorte eu precisava da **hora exata** da publicação — e "
        "aí apareceu um problema.")

    A.secao(doc, "3.1", "O trabalho de conseguir a hora", nivel=2)

    A.paragrafo(doc,
        "O arquivo aberto da CVM traz **só a data**, sem hora. Sem hora, não há como "
        "separar o que saiu de manhã do que saiu de noite.")

    A.paragrafo(doc,
        "A primeira ideia foi usar o carimbo interno do arquivo PDF — a hora em que o "
        "documento foi salvo. **Foi descartada**, e com razão: aquele carimbo diz quando "
        "a **empresa** fechou o arquivo, não quando a **CVM** recebeu. Seria hora "
        "aproximada, e hora aproximada num estudo desses é pior que hora nenhuma.")

    A.paragrafo(doc,
        "**A hora verdadeira está no Protocolo de Entrega** — o recibo que a CVM emite "
        "para cada documento. É este o texto do recibo, literal:")

    A.paragrafo(doc,
        "*Protocolo de Entrega — 9512 - PETRÓLEO BRASILEIRO S.A. - PETROBRAS. O "
        "documento foi entregue para CVM e B3. Tipo de Documento: Fato Relevante. "
        "**Data da Entrega: 03/01/2018 07:20:19.***", recuo=False)

    A.paragrafo(doc,
        "**Data, hora, minuto e segundo, com fé pública.** Foram baixados os recibos "
        "de TODOS os 20.419 documentos, um a um. Cobertura de 100%. A data do recibo "
        "bate com a do arquivo aberto em 100% dos casos.")

    A.paragrafo(doc,
        "**E a decisão de recusar a hora aproximada evitou um erro real:** o carimbo do "
        "PDF sugeria que 40% das publicações saíam com o pregão aberto. **O dado oficial "
        "mostra 5,4%.** Eu teria concluído que o desenho era frágil quando ele é, na "
        "verdade, bem apoiado.")

    A.tabela_abnt(doc, "3", "Quando as empresas publicam, segundo o recibo oficial",
        ["Momento", "Proporção"],
        [
            ["até as 9h59 — antes de o mercado abrir", "26,2%"],
            ["das 10h às 16h59 — com o pregão aberto", "5,4%"],
            ["das 17h em diante — depois do fechamento", "68,4%"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**Quase 95% das publicações acontecem fora do horário de negociação** — que é "
        "exatamente o que a Resolução CVM nº 44 recomenda. **E é da noite que vem o "
        "material do experimento: 11.161 casos.**")

    # ── 4 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "4", "As três réguas: o que significa “mexeu”")

    A.paragrafo(doc,
        "“O preço se mexeu” pode querer dizer três coisas diferentes. Medi as três "
        "separadamente.")

    A.secao(doc, "4.1", "Régua 1 — o sacolejo (volatilidade)", nivel=2)

    A.paragrafo(doc,
        "**Volatilidade é o tamanho do balanço do preço, sem olhar para que lado.** Um "
        "dia em que a ação sobe 5% e um dia em que ela cai 5% têm a **mesma** "
        "volatilidade: alta. Um dia em que ela varia 0,2% tem volatilidade baixa.")

    A.paragrafo(doc,
        "**A analogia:** é a diferença entre perguntar *“para onde o barco foi?”* e "
        "*“o mar estava agitado?”*. A volatilidade é a segunda pergunta.")

    A.paragrafo(doc,
        "**Como medi:** pelo **intervalo percorrido no dia** — a distância entre a "
        "máxima e a mínima. É melhor que olhar só o fechamento, porque um dia pode "
        "subir 8%, cair 8% e fechar no mesmo lugar. Olhando só o fechamento, esse dia "
        "pareceria calmo; olhando o intervalo, aparece o que de fato foi.")

    A.secao(doc, "4.2", "Régua 2 — quantas ações trocaram de mão (volume)", nivel=2)

    A.paragrafo(doc,
        "**Volume é quantas ações foram negociadas no dia.** Se num dia comum trocam de "
        "mão um milhão de ações e no dia seguinte à notícia trocam três milhões, algo "
        "chamou a atenção.")

    A.paragrafo(doc,
        "**A analogia:** é a lotação do estádio. O placar pode terminar empatado, mas "
        "se foi muito mais gente que o normal, algo importante estava em jogo.")

    A.secao(doc, "4.3", "Régua 3 — para que lado (direção)", nivel=2)

    A.paragrafo(doc,
        "**Direção é simplesmente se o preço subiu ou desceu.** É a pergunta mais fácil "
        "de entender e, de longe, a mais difícil de acertar.")

    A.paragrafo(doc,
        "Dentro dela, separei duas partes do dia seguinte, e essa separação é "
        "importante:")

    A.tabela_abnt(doc, "4", "O pregão seguinte, partido em dois",
        ["Pedaço", "O que é", "O que mede"],
        [
            ["o salto da abertura",
             "a diferença entre o preço de abertura e o fechamento da véspera",
             "a reação PURA à notícia da noite"],
            ["o resto do dia",
             "da abertura até o fechamento",
             "o que veio DEPOIS que o mercado já sabia"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**O salto da abertura é a medida mais limpa que existe aqui.** A notícia saiu "
        "às 19h; a primeira oportunidade de negociar sobre ela é a abertura do dia "
        "seguinte. Tudo que aparecer nesse salto é atribuível ao intervalo em que "
        "aquela notícia foi a novidade.")

    # ── 5 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "5", "O detalhe que quase me fez errar")

    A.paragrafo(doc,
        "O Prof. Emerson sugeriu comparar a volatilidade do dia seguinte com a **média "
        "da semana anterior**, em vez de uma média distante. **A sugestão está certa, e "
        "é mais exigente do que o que eu tinha planejado.**")

    A.paragrafo(doc,
        "**Por quê:** volatilidade é grudenta. Depois de uma semana agitada vem outra "
        "agitada; depois de uma semana calma, mais calmaria. Então **bater a média da "
        "própria semana anterior é muito mais difícil** que bater uma média de cem dias "
        "atrás, que já não tem nada a ver com o momento.")

    A.paragrafo(doc,
        "Fiz um cuidado a mais: **deixei de fora os dois dias imediatamente "
        "anteriores.** Se alguém soubesse da notícia antes e já estivesse negociando, a "
        "véspera estaria agitada — e incluí-la inflaria a base de comparação, "
        "escondendo o efeito.")

    A.secao(doc, "5.1", "E o erro que eu ia cometer", nivel=2)

    A.paragrafo(doc,
        "A conta é uma divisão: **a volatilidade do dia seguinte dividida pela média da "
        "semana anterior.** Se der 1,00, o dia foi igual à semana. Se der 1,50, foi 50% "
        "mais agitado.")

    A.paragrafo(doc,
        "**Eu ia comparar contra 1,00 — e isso está errado.** Fui medir a mesma divisão "
        "em **110 mil pregões em que não houve comunicado nenhum**, e ela já dá "
        "**1,034** na volatilidade e **1,065** no volume.")

    A.paragrafo(doc,
        "**Por que dá mais que 1 sem motivo nenhum:** porque um dia pode ser cinco "
        "vezes mais agitado que a média, mas nunca pode ser cinco vezes menos — o piso "
        "é zero. Os dias agitados puxam a média para cima, e os calmos não puxam para "
        "baixo na mesma proporção.")

    A.paragrafo(doc,
        "**A analogia:** é como medir altura só a partir do chão. Ninguém tem altura "
        "negativa, então a média sempre fica acima do ponto de partida.")

    A.paragrafo(doc,
        "**Consequência prática: o piso não é 1,00, é 1,034.** Sem esse controle eu "
        "teria anunciado 9,7% de excesso de volatilidade e 16,7% de volume sem "
        "desconto do piso. **Os números certos, já descontados, são 9,8% e 16,8%.**")

    # ── 6 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "6", "Resultado 1 — sim, a notícia mexe. No risco.")

    A.tabela_abnt(doc, "5", "O pregão seguinte, comparado a um pregão sem comunicado",
        ["Régua", "Dia sem comunicado", "Dia depois da notícia", "Excesso", "Chance de ser sorte"],
        [
            ["Sacolejo (volatilidade)", "1,031", "1,130", "+9,6%", "7 em 10⁵⁵"],
            ["VOLUME negociado", "1,060", "1,235", "+16,5%", "4 em 10⁶²"],
            ["Salto da abertura", "0,077%", "0,161%", "+0,08 ponto", "menos de 1 em 1.000"],
            ["Resto do dia", "−0,065%", "−0,166%", "−0,10 ponto", "1 em 1.000"],
            ["DIREÇÃO no dia todo", "0,011%", "0,006%", "quase zero", "89 em 100"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**Como ler a última coluna:** ela responde *“qual a chance de eu estar vendo "
        "isso por pura sorte?”*. Quanto menor, mais confiável. O critério da área é "
        "ficar abaixo de 5 em 100.")

    A.paragrafo(doc,
        "**A resposta à pergunta dos senhores é sim: a publicação mexe no pregão "
        "seguinte** — e nas duas primeiras réguas o resultado é de uma certeza quase "
        "absoluta.")

    A.paragrafo(doc,
        "**O volume é o sinal mais forte, quase o dobro da volatilidade.** Eu havia "
        "previsto isso por escrito antes de rodar o experimento.")

    A.paragrafo(doc,
        "**E a direção deu zero — 92 chances em 100 de ser sorte.** Isso não é falha do "
        "experimento: **é consequência lógica do rótulo.** “Fato Relevante” não diz se "
        "a notícia é boa ou ruim; diz só que é importante. Como há fatos relevantes "
        "bons e ruins, as altas e as baixas se cancelam na média. **Era o resultado "
        "obrigatório — e é a razão de existir a segunda rodada.**")

    # ── 7 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "7", "Resultado 2 — metade não mexe nada")

    A.paragrafo(doc,
        "Este é o resultado que eu levaria se só pudesse levar um.")

    A.tabela_abnt(doc, "6", "O que aconteceu em cada um dos 11.161 casos",
        ["No dia seguinte à notícia...", "Casos", "Proporção"],
        [
            ["MEXEU MUITO — o dobro do normal ou mais", "1.642", "14,7%"],
            ["mexeu — 30% acima do normal ou mais", "2.900", "26,0%"],
            ["ficou dentro do normal", "4.599", "41,2%"],
            ["ficou MAIS PARADO que o normal", "1.991", "17,8%"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**40,7% mexeram. 59,3% não mexeram — ou até ficaram mais parados que um dia "
        "comum.**")

    A.paragrafo(doc,
        "**Leia isso com atenção, porque é contraintuitivo:** são documentos que a "
        "própria empresa declarou, sob obrigação legal, serem capazes de influir na "
        "cotação. **E mais da metade não influiu em nada.**")

    A.paragrafo(doc,
        "**O efeito médio não vem de todos os casos um pouquinho. Vem de uma "
        "minoria de casos com muita força.** É o que venho chamando de **efeito de "
        "cauda** ao longo de toda a dissertação — e aqui ele aparece de novo, agora com "
        "documentos oficiais e sem depender de nenhum modelo de inteligência "
        "artificial.")

    A.secao(doc, "7.1", "Três casos para ver de perto", nivel=2)

    A.lista(doc, [
        "**OIBR3 — 7 de novembro de 2025, às 19h31.** *“Manifestação sobre a "
        "Continuidade do Grupo Oi”*. No pregão seguinte a ação **caiu 44,2%**, com "
        "sacolejo de 4,9 vezes e volume de 5,7 vezes a média da semana.",
        "**OIBR3 — 30 de setembro de 2025, às 23h08.** *“Decisão Judicial — Suspensão "
        "de Obrigações e Afastamento da Gestão”*. **Caiu 28,1%**, com volume de "
        "**15,1 vezes** o normal.",
        "**CVCB3 — 15 de janeiro de 2026, às 20h51.** *“Plano de sucessão da "
        "Companhia”*. **Caiu 11,4%.**",
    ])

    A.paragrafo(doc,
        "**A planilha traz os 11.161, um por linha** — empresa, data, hora, texto do "
        "comunicado, sacolejo, volume, direção e tamanho do movimento. Qualquer um "
        "desses casos pode ser conferido à mão.")

    # ── 8 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "8", "Resultado 3 — a nossa leitura acerta o lado?")

    A.paragrafo(doc,
        "Agora a segunda rodada. Aqui entra o **FinBERT-PT-BR**, que é o programa que "
        "lê o texto e diz se ele é positivo, negativo ou neutro.")

    A.paragrafo(doc,
        "**O que é esse programa, em linguagem comum:** é um leitor que estudou 1,4 "
        "milhão de textos financeiros em português e aprendeu a reconhecer o tom. Você "
        "dá uma frase e ele devolve uma palavra: bom, ruim ou neutro.")

    A.paragrafo(doc,
        "**A regra de acerto foi declarada por escrito antes de rodar**, para não haver "
        "ajuste posterior: se ele disser **positivo**, acerta quando o preço **sobe**; "
        "se disser **negativo**, acerta quando o preço **cai**; se disser **neutro**, "
        "não está fazendo previsão nenhuma e fica de fora da conta.")

    A.secao(doc, "8.1", "O que ele achou dos textos", nivel=2)

    A.tabela_abnt(doc, "7", "Como o programa classificou os 20.421 comunicados",
        ["Classificação", "Quantidade", "Proporção"],
        [
            ["Neutro", "16.182", "79,2%"],
            ["Negativo", "2.354", "11,5%"],
            ["Positivo", "1.885", "9,2%"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**Quase 80% neutros.** E isso tem uma explicação simples: os textos da CVM são "
        "**linhas de assunto burocráticas**, com 47 caracteres em média. Coisas como "
        "*“Venda de Ativo”* ou *“Alteração na Diretoria Executiva”*. **Não são frases "
        "com opinião; são etiquetas.** O programa foi treinado para ler notícia, e "
        "etiqueta de arquivo é outro animal.")

    A.secao(doc, "8.2", "A taxa de acerto", nivel=2)

    A.tabela_abnt(doc, "8", "Acurácia na direção do pregão seguinte",
        ["Alvo", "Casos", "Acertou", "Palpite preguiçoso", "Ganho"],
        [
            ["o salto da abertura", "636", "54,7%", "57,4%", "PERDE por 2,7 pontos"],
            ["o pregão inteiro", "636", "55,0%", "50,2%", "GANHA por 4,9 pontos"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**Preciso explicar o que é “palpite preguiçoso”, porque é a comparação que "
        "importa e é a que a banca vai cobrar.**")

    A.paragrafo(doc,
        "Imagine alguém que não lê notícia nenhuma e sempre chuta o mesmo lado — "
        "sempre “vai subir”. Se as ações sobem em 57% dos dias, esse preguiçoso acerta "
        "57% **sem fazer esforço nenhum**. **Qualquer modelo que acerte menos que isso "
        "não está servindo para nada**, por mais sofisticado que seja.")

    A.paragrafo(doc, "**Então os dois resultados dizem coisas opostas:**")

    A.lista(doc, [
        "**No salto da abertura, nós perdemos do preguiçoso.** A abertura sobe em 57,4% "
        "das vezes; nós acertamos 54,7%. **Somos melhores que cara ou coroa, e piores "
        "que o chute fixo.** Convém dizer isso antes que perguntem.",
        "**No pregão inteiro, nós ganhamos: 55,0% contra 50,2%, quase 5 pontos de "
        "vantagem.** Aqui o preguiçoso não tem vantagem nenhuma, porque o dia inteiro "
        "sobe e desce quase na mesma proporção — e é aí que ler a notícia passa a valer.",
    ])

    A.paragrafo(doc,
        "**E há uma coincidência que vale mencionar:** o resultado principal da "
        "dissertação, feito na PETR4 com manchetes de jornal, dá **+4,4 pontos**. Este "
        "aqui, feito com comunicados oficiais em 57 papéis diferentes, dá **+4,9**. "
        "**Dois caminhos independentes chegando ao mesmo lugar** — e ambos dentro da "
        "faixa de 2 a 10 pontos que a literatura internacional relata.")

    A.secao(doc, "8.3", "E aqui está o achado mais interessante da rodada", nivel=2)

    A.tabela_abnt(doc, "9", "O que aconteceu com o preço, por classificação",
        ["O programa disse que era...", "Casos", "O preço fez, em média"],
        [
            ["Positivo", "303", "+0,014%  (nada)"],
            ["Neutro", "2.939", "+0,028%  (nada)"],
            ["NEGATIVO", "477", "−0,353%"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**O que o programa chama de ruim é seguido de queda de 0,35%. O que ele chama "
        "de bom não é seguido de nada.**")

    A.paragrafo(doc,
        "**O sinal existe, mas mora quase todo de um lado só: o lado ruim.**")

    A.paragrafo(doc,
        "**E isso não é novidade — é a confirmação de algo que já tínhamos "
        "documentado.** Em 224 notícias que trinta casas de análise consideraram "
        "favoráveis à Petrobras, esse mesmo programa enxergou apenas 21,9% como "
        "positivas. **Ele reconhece o ruim; não reconhece o bom.**")

    A.paragrafo(doc,
        "Na PETR4 isso fica gritante: de 432 comunicados classificados, **100 foram "
        "negativos e apenas 14 positivos.**")

    # ── 8.4 ──────────────────────────────────────────────────────────────────
    A.secao(doc, "8.4", "E o achado que só apareceu com a base completa", nivel=2)

    A.paragrafo(doc,
        "**Quando somei os Comunicados ao Mercado aos Fatos Relevantes, o acerto da "
        "nossa leitura despencou.** Fui investigar, e o motivo é esclarecedor:")

    A.tabela_abnt(doc, "10", "A nossa leitura funciona onde?",
        ["Em que tipo de documento", "Casos", "Acertou", "Palpite fixo", "Ganho", "Vale?"],
        [
            ["Só FATO RELEVANTE", "700", "54,3%", "51,7%", "+2,6 pontos", "SIM"],
            ["Só Comunicado ao Mercado", "1.636", "51,0%", "50,6%", "+0,4 ponto", "não"],
            ["Os dois juntos", "2.336", "52,0%", "50,9%", "+1,1 ponto", "não"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**A nossa leitura só acrescenta valor no documento mais forte.** No Fato "
        "Relevante ela ganha 2,6 pontos de quem não lê nada, e o resultado passa no "
        "teste estatístico. **No Comunicado ao Mercado ela não ganha absolutamente "
        "nada — zero.**")

    A.paragrafo(doc,
        "**Isso é coerente com tudo o mais, e reforça a tese em vez de enfraquecê-la.** "
        "O Comunicado ao Mercado mexe pouco no preço; onde quase não há movimento, não "
        "há o que prever. **Ler o texto só compensa quando o evento é grande** — que é "
        "exatamente o efeito de cauda dito de outra maneira.")

    A.paragrafo(doc,
        "**E é honesto registrar:** quando juntei tudo, o resultado deixou de ser "
        "significativo. **O número que se deve reportar é o do Fato Relevante — 2,6 "
        "pontos —, e sempre dizendo que nos Comunicados não funciona.**")

    # ── 9 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "9", "Juntando tudo")

    A.tabela_abnt(doc, "10", "O que cada classificação consegue e o que não consegue",
        ["", "O rótulo da CVM", "A nossa leitura"],
        [
            ["Diz que algo aconteceu?", "SIM, e muito bem", "não é o forte dela"],
            ["Diz se foi bom ou ruim?", "NÃO — não tem esse dado", "SIM, mas só o ruim"],
            ["Acerta o sacolejo?", "+18,2% no Fato Relevante", "não distingue"],
            ["Acerta o volume?", "+36,3% no Fato Relevante", "não distingue"],
            ["Acerta a direção?", "impossível", "+2,6 pontos, só no Fato Relevante"],
            ["Custo", "zero — já vem pronto", "precisa rodar o programa"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**As duas se completam e nenhuma substitui a outra.** O rótulo da CVM é "
        "imbatível para dizer que houve informação relevante, e é de graça. **A nossa "
        "leitura é a única capaz de apontar o lado** — e mesmo assim só um deles.")

    # ── 10 ───────────────────────────────────────────────────────────────────
    A.secao(doc, "10", "O que ainda não está resolvido")

    A.lista(doc, [
        "**O texto é curto e burocrático.** Quarenta e sete caracteres em média, e "
        "**26% se repetem**. *“Notícia divulgada na mídia”* aparece 397 vezes. **Nenhum "
        "programa acerta o tom de um texto que não diz nada.** O documento completo em "
        "PDF existe e é o caminho natural para melhorar.",
        "**741 casos (21,6%) têm mais de um comunicado na mesma noite.** Quando isso "
        "acontece, não dá para dizer qual documento causou o movimento. Rodei tudo "
        "também só com os 2.694 casos isolados, e os resultados se mantiveram.",
        "**Faltam 4 papéis** — Eletrobras, Embraer, Azul e Gol —, o que tira 14,8% dos "
        "eventos. Foi falha do provedor de cotações, não de método.",
        "**A comparação entre as duas gavetas ainda está incompleta:** a hora oficial "
        "dos Comunicados ao Mercado está sendo coletada e hoje cobre cerca de um terço.",
        "**Sobre a palavra “causou”:** o desenho é o mais limpo possível, mas continua "
        "sendo observação, não experimento de laboratório. Ninguém sorteia quais "
        "empresas publicam fato relevante. **É associação muito bem medida.**",
    ])

    # ── 11 ───────────────────────────────────────────────────────────────────
    A.secao(doc, "11", "As perguntas que provavelmente virão")

    A.lista(doc, [
        "**“Você classificou as notícias como relevantes?”** Não. O rótulo vem pronto "
        "do arquivo da CVM, e quem o atribui é a própria empresa, sob obrigação legal.",
        "**“Como sabe que foi a notícia que moveu o preço?”** Não sei com certeza "
        "absoluta. Mas a notícia saiu com o mercado fechado, e comparei com 110 mil "
        "pregões sem notícia nenhuma. É o mais perto de um experimento que se consegue "
        "com dado de mercado.",
        "**“55% de acerto não é muito baixo?”** A comparação justa não é contra 100%, é "
        "contra quem não lê nada. O chute fixo acerta 50,2%; nós acertamos 55,0%. E a "
        "literatura internacional relata ganhos de 2 a 10 pontos — o nosso é 4,9.",
        "**“Por que a direção deu zero na primeira rodada?”** Porque o rótulo da CVM "
        "não tem lado. Ele diz que a notícia é importante, não se é boa ou ruim. Era "
        "matematicamente obrigatório dar zero.",
        "**“O programa é bom?”** Ele é bom para reconhecer notícia ruim e cego para "
        "notícia boa. Isso está medido e documentado, e é uma limitação conhecida do "
        "modelo, não um erro de operação.",
    ])

    A.secao(doc, "12", "Se o tempo apertar, cinco frases")

    A.lista(doc, [
        "“Peguei 11.161 comunicados que as empresas entregaram à CVM depois que o "
        "mercado fechou, com hora oficial, e olhei o que aconteceu no pregão seguinte.”",
        "“Nos Fatos Relevantes o volume negociou 36% acima do normal e o sacolejo 18% "
        "acima — "
        "comparando com 110 mil pregões em que não houve comunicado nenhum.”",
        "“Mas 59% não moveram nada. O efeito vem de uma minoria "
        "de casos — e isso confirma a tese central da minha dissertação.”",
        "“O rótulo da CVM não prevê direção, porque não diz se a notícia é boa ou "
        "ruim. A minha leitura prevê — mas SÓ nos Fatos Relevantes, onde ganha 2,6 "
        "pontos de quem não lê nada. Nos Comunicados ao Mercado ela não ganha nada.”",
        "“E o sinal mora quase todo na notícia ruim: o que o programa chama de ruim é "
        "seguido de queda de 0,35%; o que ele chama de bom não é seguido de nada.”",
    ])

    try:
        doc.save(SAIDA)
        destino = SAIDA
    except PermissionError:
        destino = SAIDA.with_name(SAIDA.stem + "_ATUALIZADO.docx")
        doc.save(destino)
        print("  [aviso] original aberto no Word; gravado ao lado.")
    print(f"[OK] {destino}")


if __name__ == "__main__":
    main()
