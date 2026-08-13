# -*- coding: utf-8 -*-
# ==============================================================================
#   Gera a explicação em linguagem comum do levantamento de encoders em inglês
#   Saída: orientacoes/EXPLICACAO_SIMPLES_ENCODERS_INGLES.docx
#
#   Origem: mentoria de 13/08/2026 com o Prof. Emerson Cabrera Paraiso.
#   Público: leitor sem formação em aprendizado de máquina nem em estatística.
# ==============================================================================
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(RAIZ / "src" / "comum"))

import abnt_docx as A  # noqa: E402

FONTE = "Elaborado pelo autor (2026)"
SAIDA = AQUI / "EXPLICACAO_SIMPLES_ENCODERS_INGLES.docx"


def main() -> None:
    doc = A.novo_documento()

    A.capa(
        doc,
        titulo="O que o mundo em inglês já descobriu",
        subtitulo="Encoders financeiros, quem os cita, para que servem — "
                  "e o que isso muda na nossa pesquisa",
        autor="Vanderlei Barbosa da Silva",
        orientador="Orientador: Prof. Dr. Julio Cesar Nievola",
        instituicao="PUCPR — Programa de Pós-Graduação em Informática (PPGIa)",
        descricao="Documento escrito para ser entendido sem conhecimento prévio de "
                  "aprendizado de máquina ou de estatística. Todo termo técnico é "
                  "explicado quando aparece pela primeira vez, com analogia. "
                  "Elaborado em 13 de agosto de 2026, atendendo às três tarefas "
                  "determinadas pelo Prof. Dr. Emerson Cabrera Paraiso na mentoria "
                  "da mesma data.",
    )

    # ── 1 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "1", "A notícia mais importante deste documento")

    A.paragrafo(doc,
        "Antes de qualquer detalhe, o achado que muda o tom da sua defesa.")

    A.paragrafo(doc,
        "Nós vínhamos tratando o nosso desempenho de **0,58** como um problema — algo "
        "que precisava ser consertado, e que resistiu a nove tentativas de conserto. "
        "Havia sempre a suspeita de que a culpa fosse do português, ou do modelo "
        "brasileiro ter sido treinado com poucos dados.")

    A.paragrafo(doc,
        "**Não é nada disso.** Encontrei um estudo de 2025 que pegou o FinBERT "
        "**inglês** — o modelo com 4,5 milhões de downloads por mês, treinado com "
        "bilhões de palavras, publicado em revista de primeira linha — e o aplicou a "
        "manchetes de um setor específico, sem ajuste. Resultado:")

    A.tabela_abnt(doc, "1", "O nosso número comparado ao do modelo em inglês",
        ["Modelo", "Situação", "Desempenho (F1)"],
        [
            ["FinBERT inglês", "manchetes setoriais, sem ajuste", "0,555"],
            ["FinBERT-PT-BR (o nosso)", "manchetes da PETR4, sem ajuste", "0,579"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**O nosso é ligeiramente MELHOR.** Não pior — melhor.")

    A.paragrafo(doc,
        "Isso significa que o teto de 0,58 **não é falha do português, nem do modelo "
        "brasileiro, nem de escolha errada de arquitetura.** É simplesmente o que "
        "acontece com qualquer modelo desse tipo quando aplicado a um recorte "
        "específico sem treinamento adicional. **É o comportamento esperado.**")

    A.paragrafo(doc,
        "Você passou meses achando que tinha um problema. Você tinha um resultado "
        "normal, e agora tem a evidência externa para provar isso.")

    # ── 2 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "2", "Tarefa 1 — qual é o BERT financeiro em inglês")

    A.paragrafo(doc,
        "Antes de responder, uma explicação rápida do que é um **encoder**, porque a "
        "palavra vai aparecer o tempo todo.")

    A.secao(doc, "2.1", "O que é um encoder, com uma analogia", nivel=2)

    A.paragrafo(doc,
        "Pense num **funcionário que você contrata para ler notícias**. Ele passou por "
        "duas formações:")

    A.lista(doc, [
        "**Formação geral** — aprendeu a língua: gramática, vocabulário, como as "
        "palavras se combinam. É o BERT comum.",
        "**Especialização** — depois, leu milhões de textos de finanças até ficar "
        "fluente no jargão. Aprendeu que “alavancagem” não tem a ver com alavancas e "
        "que “posição vendida” não é sobre vender. Isso é o **FinBERT**.",
    ])

    A.paragrafo(doc,
        "**Encoder** é o nome técnico desse funcionário. Ele não decora respostas: "
        "aprendeu um jeito de ler e formar opinião.")

    A.secao(doc, "2.2", "A resposta: existem DOIS, e isso confunde muita gente", nivel=2)

    A.paragrafo(doc,
        "Este é um detalhe que vale mencionar na banca, porque mostra domínio da "
        "literatura: **há dois modelos diferentes com o mesmo nome “FinBERT”**, de "
        "grupos diferentes. Muitos artigos escrevem só “FinBERT” sem dizer qual, o que "
        "torna o texto ambíguo.")

    A.tabela_abnt(doc, "2", "Os dois FinBERT em inglês",
        ["", "FinBERT de Araci (2019)", "FinBERT de Yang e Huang (2020)"],
        [
            ["Origem", "Universidade de Amsterdã", "HKUST, Hong Kong"],
            ["Natureza", "dissertação de mestrado", "artigo em revista de ponta"],
            ["Treinado com", "1,8 milhão de notícias", "4,9 bilhões de palavras"],
            ["Downloads/mês", "4.459.091", "704.839"],
            ["Citações", "778", "não recuperado"],
        ], fonte=FONTE + ". Consulta em 13/08/2026.")

    A.paragrafo(doc,
        "**Dois detalhes que valem ouro para você:**")

    A.paragrafo(doc,
        "**Primeiro:** o modelo mais baixado do mundo inteiro na área — 4,5 milhões de "
        "downloads por mês — nasceu como **uma dissertação de mestrado**. Exatamente o "
        "que você está escrevendo. Vale lembrar disso quando bater o desânimo.")

    A.paragrafo(doc,
        "**Segundo, e este é técnico mas importante:** o modelo inglês converte todo "
        "texto para minúsculas antes de ler. Por isso ele é **imune** àquele problema "
        "das 21.619 manchetes em CAIXA ALTA que descobrimos quebrando o modelo "
        "brasileiro. O autor do modelo em inglês tomou uma decisão de projeto que o "
        "autor brasileiro não copiou. **Isso é um achado nosso, e é publicável.**")

    # ── 3 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "3", "Tarefa 2 — quem cita esses modelos")

    A.paragrafo(doc,
        "Muita gente. Mas em vez de listar centenas de nomes, separei os **dois "
        "trabalhos que fazem exatamente o que você faz**. Eles são muito mais úteis "
        "que uma lista.")

    A.secao(doc, "3.1", "O trabalho que faz o mesmo e CONSEGUE o que não conseguimos",
            nivel=2)

    A.paragrafo(doc,
        "Halousková e Lyócsa (2025) usam FinBERT para extrair sentimento e o modelo "
        "HAR como adversário — **exatamente o desenho da nossa Seção 4.k**. Só que:")

    A.lista(doc, [
        "Eles **superam o HAR em 98,76% dos casos**, com melhora média de 12,74%.",
        "Nós **não superamos** (p = 0,64).",
    ])

    A.paragrafo(doc,
        "Isso incomoda, e é para incomodar. Mas fui atrás do porquê, e as diferenças "
        "são concretas — não é que eles tenham um segredo:")

    A.tabela_abnt(doc, "3", "Por que eles conseguem e nós não",
        ["O que muda", "Eles", "Nós", "Dá para corrigir?"],
        [
            ["Quantos ativos", "404 ações", "1 ação", "SIM"],
            ["Medida do sacolejo", "de 5 em 5 minutos", "1 vez por dia", "só com dados intradiários"],
            ["Como combinam", "métodos sofisticados", "soma simples", "SIM, é só código"],
            ["Fontes de sinal", "notícias + Google + Twitter", "só notícias", "em parte"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**A leitura honesta:** o nosso resultado negativo pode não significar “o "
        "sentimento não serve”. Pode significar **“não temos dados suficientes para "
        "detectar”** — uma ação só, medida grosseira, combinação simples.")

    A.paragrafo(doc,
        "É como tentar ouvir um sussurro numa rua movimentada. O sussurro existe; "
        "faltam condições para captá-lo. **E é exatamente por isso que o Professor "
        "Emerson mandou abrir o leque para vários ativos — ele estava certo.**")

    A.secao(doc, "3.2", "E o mesmo trabalho CONFIRMA o nosso maior achado", nivel=2)

    A.paragrafo(doc,
        "Aqui vem a melhor parte. Lembra do efeito de cauda — a descoberta de que o "
        "sentimento **não move o pregão comum, mas importa nos extremos**?")

    A.paragrafo(doc,
        "**Eles acharam a mesma coisa.** O ganho deles é maior justamente nos dias de "
        "variação extrema: **14,99%**, contra 12,74% na média.")

    A.paragrafo(doc,
        "Pense no peso disso. Nós descobrimos aquilo em **uma ação brasileira**, com "
        "dados diários. Eles descobriram em **404 ações americanas**, com dados de 5 em "
        "5 minutos, outro idioma, outro método estatístico. **Chegamos ao mesmo lugar "
        "por caminhos completamente independentes.**")

    A.paragrafo(doc,
        "Quando isso acontece na ciência, o achado deixa de ser “uma coisa que "
        "encontramos” e passa a ser **um fato do fenômeno**.")

    A.secao(doc, "3.3", "O trabalho que faz o mesmo e PARA antes de nós", nivel=2)

    A.paragrafo(doc,
        "Mino e Williamson (2025) usam BERT com GARCH(1,1) t-Student — **o mesmo "
        "modelo, item por item, do seu Script 04**. E olhe o resultado deles ao lado "
        "do nosso:")

    A.tabela_abnt(doc, "4", "O coeficiente do sentimento em dois mercados",
        ["Estudo", "Mercado", "Coeficiente", "Valor-p"],
        [
            ["Mino e Williamson (2025)", "S&P 500 (EUA)", "−0,2275", "0,0016"],
            ["Nossa dissertação", "PETR4 (Brasil)", "−0,2924", "0,0002"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**Praticamente o mesmo número.** Dois países, dois idiomas, dois modelos de "
        "leitura diferentes, dois períodos diferentes — e a mesma medida: sentimento "
        "mais pessimista hoje, mais sacolejo amanhã, com força em torno de −0,25.")

    A.paragrafo(doc,
        "Isso prova que o seu número **não é coincidência do mercado brasileiro**. É "
        "uma medida real do fenômeno.")

    A.paragrafo(doc,
        "**E agora o ponto que você deve usar na defesa.** Olhe o que eles NÃO fizeram:")

    A.lista(doc, [
        "**Não testaram fora da amostra.** Eles só mediram a relação nos dados que "
        "usaram para montar o modelo — o equivalente a conferir a prova com o gabarito "
        "na mão. Nós fizemos 795 previsões de verdade, sem espiar o futuro.",
        "**Não separaram dias de crise de dias normais.** Declararam isso como "
        "limitação. Nós fizemos, e foi daí que saiu o efeito de cauda.",
        "**Usaram 105 dias.** Nós usamos 1.988 pregões.",
    ])

    A.paragrafo(doc,
        "**Eles param exatamente onde nós continuamos.** E se tivéssemos parado ali, "
        "teríamos anunciado sucesso — e estaríamos errados, porque foi ao continuar "
        "que descobrimos que aquilo não vira previsão de verdade.")

    A.paragrafo(doc,
        "**Isso é uma contribuição da sua dissertação, e você deve dizê-la em voz "
        "alta:** você avaliou com mais rigor que trabalhos publicados na mesma linha, "
        "e por isso encontrou um limite que eles não encontraram.")

    # ── 4 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "4", "Tarefa 3 — para que as pessoas usam esses modelos")

    A.paragrafo(doc,
        "Encontrei **nove famílias de aplicação**. A lista completa está no documento "
        "técnico; aqui vão as que interessam a você.")

    A.tabela_abnt(doc, "5", "As nove famílias de aplicação",
        ["#", "Para que usam", "Serve para nós?"],
        [
            ["1", "Sentimento de notícias e relatórios", "é o que já fazemos"],
            ["2", "Previsão de volatilidade", "SIM — é o eixo central"],
            ["3", "Previsão de preço e direção", "com ressalva (ver adiante)"],
            ["4", "Separar notícia de passado e de futuro", "SIM — a melhor ideia"],
            ["5", "Classificação ESG (ambiental e social)", "fora do escopo"],
            ["6", "Montagem de carteira de investimento", "trabalho futuro"],
            ["7", "Comunicados de bancos centrais", "fora do escopo"],
            ["8", "Outros mercados: títulos, cripto, setores", "SIM — abrir o leque"],
            ["9", "Explicar por que o modelo decidiu", "SIM — barato e bonito"],
        ], fonte=FONTE)

    A.secao(doc, "4.1", "A melhor ideia que este levantamento produziu", nivel=2)

    A.paragrafo(doc,
        "Existe um modelo especializado em **separar notícia que conta o passado de "
        "notícia que projeta o futuro**. Chama-se `finbert-fls`.")

    A.paragrafo(doc,
        "Pare e pense no que isso significa para nós. A nossa Seção 4.l descobriu que "
        "**o sentimento acompanha o mercado em vez de antecipá-lo** — o sinal é limpo "
        "no mesmo dia e some no dia seguinte. A explicação que demos foi: boa parte "
        "disso é o jornal **narrando** o que já aconteceu.")

    A.paragrafo(doc,
        "**Se essa explicação estiver certa, então separar as notícias que falam do "
        "futuro deveria concentrar o sinal que sobra.**")

    A.paragrafo(doc,
        "É a mesma lógica do filtro de relevância, que foi a única coisa que funcionou "
        "em nove tentativas: **mexer em quais notícias entram no índice funciona; "
        "mexer no modelo não funciona.** E dá para testar sem depender do modelo em "
        "inglês — basta identificar as manchetes com verbo no futuro, com “deve”, "
        "“prevê”, “projeta”, “espera-se”.")

    A.paragrafo(doc,
        "**Custo baixo, hipótese clara, ligada a dois achados que já temos.** É a minha "
        "recomendação número um.")

    A.secao(doc, "4.2", "Cuidado com os artigos que anunciam 95% de acerto", nivel=2)

    A.paragrafo(doc,
        "Você vai esbarrar em artigos afirmando “acurácia de 95,5%” na previsão de "
        "ações, e vai se perguntar por que o nosso dá 52%. **A comparação é falsa, e "
        "você precisa saber explicar isso.**")

    A.paragrafo(doc,
        "Existem duas perguntas completamente diferentes:")

    A.lista(doc, [
        "**“Qual será o preço amanhã?”** — pergunta fácil. A resposta “mais ou menos o "
        "mesmo de hoje” já acerta com 2% de erro, porque preço de ação não dá saltos "
        "todo dia. Qualquer modelo parece genial.",
        "**“A ação vai subir ou cair amanhã?”** — pergunta difícil. É quase cara ou "
        "coroa, e é o que nós medimos.",
    ])

    A.paragrafo(doc,
        "É a diferença entre acertar que **amanhã vai fazer mais ou menos a mesma "
        "temperatura de hoje** (fácil, quase sempre certo) e acertar se **vai fazer "
        "mais calor ou mais frio** (difícil, quase meio a meio).")

    A.paragrafo(doc,
        "Aquele artigo dos 95% relata erro percentual de 4,5% — métrica de **preço**, "
        "não de direção. Os 95% são simplesmente 100% menos 4,5%.")

    A.paragrafo(doc,
        "**Ressalva de honestidade:** não consegui abrir o texto completo (o arquivo "
        "veio ilegível e a outra versão bloqueou o acesso). A conclusão acima é uma "
        "**dedução** a partir das métricas que eles declaram, e não uma verificação "
        "direta. É uma dedução forte — ninguém que classifique direção reporta erro "
        "percentual de preço — mas antes de escrever isso na dissertação, é preciso "
        "abrir o artigo e confirmar.")

    # ── 5 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "5", "A resposta definitiva à pergunta do Professor Emerson "
                      "sobre rotulagem")

    A.paragrafo(doc,
        "Em julho ele disse que a rotulagem, para valer, precisaria ser feita por "
        "**especialistas em finanças**, e suspendeu o trabalho. Agora eu tenho o "
        "documento que responde isso com precisão.")

    A.paragrafo(doc,
        "O conjunto de dados sobre o qual **os dois FinBERT ingleses são treinados** "
        "chama-se *Financial PhraseBank*. Foi montado assim:")

    A.tabela_abnt(doc, "6", "O padrão-ouro internacional comparado ao nosso",
        ["", "Financial PhraseBank", "Nosso conjunto-ouro"],
        [
            ["Itens", "4.846 sentenças", "300 manchetes"],
            ["Quem rotulou", "16 pessoas de finanças", "1 pessoa (você)"],
            ["Rótulos por item", "5 a 8", "1"],
            ["Mede concordância?", "sim, em 4 níveis", "não tem como"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**Três conclusões, e a terceira é a que importa.**")

    A.paragrafo(doc,
        "**Primeira: o Professor Emerson estava certo.** O padrão internacional usa, "
        "sim, gente com formação em finanças. Isso está documentado e você pode citar.")

    A.paragrafo(doc,
        "**Segunda: a barra é mais baixa do que parece.** Os 16 não eram operadores de "
        "mercado veteranos — eram **13 mestrandos** em finanças, contabilidade e "
        "economia, mais 3 pesquisadores. O critério é “formação adequada em mercados "
        "financeiros”. **Isso é alcançável na PUCPR.**")

    A.paragrafo(doc,
        "**Terceira, e a mais importante: o problema maior não é a formação, é a "
        "repetição.** A diferença decisiva não é “especialista contra leigo”. É **5 a 8 "
        "pessoas rotulando o mesmo item, contra 1**. Sem repetição não dá para medir "
        "concordância; sem concordância não dá para saber se o erro é do modelo ou do "
        "anotador.")

    A.paragrafo(doc,
        "Um dado que ilustra bem: **mesmo entre os 16 especialistas, só 47% das frases "
        "tiveram acordo unânime.** Menos da metade. A tarefa é ambígua por natureza — "
        "e isso é um consolo legítimo sobre os seus 0,58.")

    A.secao(doc, "5.1", "O que eu proponho, se a rotulagem for retomada", nivel=2)

    A.lista(doc, [
        "**Não rotular mais manchetes. Rotular as MESMAS 300 com 3 pessoas.** Três "
        "opiniões por manchete já permitem calcular concordância.",
        "**Recrutar mestrandos de finanças, economia ou contabilidade** — exatamente o "
        "perfil que Malo e colegas usaram, e que dá para declarar na dissertação.",
        "**Usar a mesma pergunta que eles usaram:** “como esta informação poderia "
        "afetar o preço da ação mencionada?” É o que a sua coluna de direção esperada "
        "já registra.",
    ])

    A.paragrafo(doc,
        "**Mas preciso ser honesto sobre o que isso NÃO vai resolver.** O teste de "
        "teto que fizemos mostrou que um leitor **perfeito** melhoraria a previsão de "
        "direção em apenas 1,2 ponto percentual. **Rotular melhor não vai melhorar a "
        "previsão.** O valor é outro: permitir dizer com rigor se o 0,58 é culpa do "
        "modelo ou do anotador. Hoje não dá para saber, e essa dúvida é uma "
        "fragilidade real da dissertação.")

    # ── 6 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "6", "Cinco coisas nossas que a literatura confirmou")

    A.paragrafo(doc,
        "Este levantamento não só cobrou — validou. Cinco achados seus têm agora "
        "respaldo externo independente:")

    A.tabela_abnt(doc, "7", "Nossos achados e suas confirmações externas",
        ["O que descobrimos", "Quem confirmou, independentemente"],
        [
            ["O efeito é de cauda", "404 ações do S&P 500: maior ganho nos dias extremos"],
            ["Coeficiente ≈ −0,29", "S&P 500 com o mesmo GARCH: −0,2275"],
            ["90% dos erros são no Neutro", "resolver o neutro é o diferencial do modelo bom"],
            ["LLM perde para o encoder", "FinBERT 83% supera todos os LLMs em ESG"],
            ["Degradação ao mudar de domínio", "FinBERT inglês cai a 0,555 em setor específico"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**Cinco achados que pareciam idiossincrasias nossas são, na verdade, "
        "alinhados ao estado da arte internacional.** Isso muda a força da sua defesa.")

    # ── 7 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "7", "O que proponho fazer agora")

    A.paragrafo(doc, "**Custo quase zero — só escrever, dias:**")
    A.lista(doc, [
        "Levar as cinco confirmações externas para os Capítulos 4 e 5.",
        "Reescrever a limitação da Seção 4.k: em vez de “o sentimento não supera o "
        "HAR”, dizer “não conseguimos detectar superação com medida diária e uma ação, "
        "enquanto a literatura detecta com medida de 5 minutos e 404 ações”.",
        "Reescrever a conclusão do experimento G3: 350 exemplos pioram, mas 1.500 "
        "levam de 0,555 a 0,707 na literatura. **Não é que ajustar não funcione — é que "
        "350 não bastam.**",
        "Registrar a armadilha dos 95% como crítica metodológica à literatura.",
    ])

    A.paragrafo(doc, "**Custo baixo — só código, dias:**")
    A.lista(doc, [
        "Testar os métodos de combinação sofisticados que eles usam, sobre os dados "
        "que já temos.",
        "**Testar o filtro de notícias que falam do futuro.** Minha recomendação "
        "número um.",
    ])

    A.paragrafo(doc, "**Custo médio — semanas:**")
    A.lista(doc, [
        "**Replicar tudo para cinco a dez ações da B3.** É o que o Professor Emerson "
        "pediu, e é o que mais aumenta a chance de detectar o sinal. Com uma predição "
        "testável embutida: se o efeito é de cauda, ações mais voláteis devem mostrar "
        "efeito maior.",
    ])

    # ── 8 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "8", "Se você tiver dois minutos para explicar isso")

    A.lista(doc, [
        "“Fui atrás dos encoders financeiros em inglês. Existem dois FinBERT "
        "diferentes com o mesmo nome, um com 4,5 milhões de downloads por mês.”",
        "“E descobri o principal: o modelo inglês, aplicado a manchetes setoriais sem "
        "ajuste, dá 0,555. O nosso dá 0,579. **O nosso é melhor.** O teto de 0,58 não é "
        "problema do português — é o comportamento normal desses modelos.”",
        "“Achei dois trabalhos que fazem exatamente o que eu faço. Um deles supera o "
        "HAR, e eu não superei — mas eles usam 404 ações e dados de 5 em 5 minutos, "
        "contra a minha ação única e dados diários.”",
        "“E esse mesmo trabalho confirma o meu efeito de cauda: o ganho deles é maior "
        "nos dias de variação extrema. Cheguei ao mesmo lugar com uma ação brasileira.”",
        "“O outro trabalho usa o mesmo GARCH que eu e acha coeficiente −0,2275; o meu é "
        "−0,2924. Quase idêntico. Mas eles não testam fora da amostra e eu testo — eles "
        "param onde eu continuo.”",
        "“Sobre a rotulagem: o padrão internacional usa 16 pessoas com formação em "
        "finanças e 5 a 8 rótulos por frase. O Professor Emerson estava certo. Mas eram "
        "mestrandos, não veteranos — e o problema maior é a repetição, não a formação.”",
    ])

    doc.save(SAIDA)
    print(f"[OK] Documento gerado: {SAIDA}")


if __name__ == "__main__":
    main()
