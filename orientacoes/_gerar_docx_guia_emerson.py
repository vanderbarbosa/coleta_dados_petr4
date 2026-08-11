# -*- coding: utf-8 -*-
# ==============================================================================
#   Guia completo do que o Prof. Emerson pediu — para LER, ENTENDER e EXPLICAR
#   Saída: orientacoes/GUIA_COMPLETO_PEDIDOS_EMERSON.docx
#
#   Reúne: as 7 orientações de 29/07/2026 + as 2 perguntas feitas na mesma
#   mentoria. Para cada item: o que ele pediu, o que encontramos, e como
#   explicar em linguagem comum.
# ==============================================================================
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(RAIZ / "src" / "comum"))

import abnt_docx as A  # noqa: E402

FONTE = "Elaborado pelo autor (2026)"
SAIDA = AQUI / "GUIA_COMPLETO_PEDIDOS_EMERSON.docx"


def main() -> None:
    doc = A.novo_documento()

    A.capa(
        doc,
        titulo="Tudo o que foi pedido pelo Prof. Emerson",
        subtitulo="As sete orientações e as duas perguntas — o que foi pedido, "
                  "o que encontramos e como explicar",
        autor="Vanderlei Barbosa da Silva",
        orientador="Co-orientador: Prof. Dr. Emerson Cabrera Paraiso",
        instituicao="PUCPR — Programa de Pós-Graduação em Informática (PPGIa)",
        descricao="Consolidação de tudo o que foi solicitado na mentoria de 29 de "
                  "julho de 2026. Cada item traz o pedido original, a resposta "
                  "encontrada e uma versão em linguagem comum para apresentação "
                  "verbal. Documento de leitura e preparação.",
    )

    # ── Mapa ─────────────────────────────────────────────────────────────────
    A.secao(doc, "1", "O que foi pedido, em uma tabela")
    A.tabela_abnt(doc, 1, "Os nove itens da mentoria de 29/07/2026",
        ["N.º", "O que ele pediu", "Situação"],
        [
            ["1", "Buscar como o BERT financeiro é usado em pesquisas", "Respondido"],
            ["2", "Identificar como os artigos utilizaram o FinBERT-PT-BR", "Respondido"],
            ["3", "Verificar se há outro encoder melhor", "Respondido e testado"],
            ["4", "Verificar se algum trabalho faz o mesmo que nós", "Respondido"],
            ["5", "Ler o artigo do link e resumir suas referências", "Respondido"],
            ["6", "Estudar o repositório do autor no Hugging Face", "Respondido"],
            ["7", "Analisar os trabalhos que citam o autor", "Respondido (7 de 12)"],
            ["8", "Pergunta: a rotulagem precisa de especialista em finanças?", "Respondida"],
            ["9", "Pergunta: como usaria na prática as notícias rotuladas?", "Respondida"],
        ], fonte=FONTE)
    A.paragrafo(doc,
        "Os itens 1 a 7 vieram por escrito, no arquivo de orientações. Os itens 8 e 9 foram "
        "perguntas feitas durante a conversa, e são as mais difíceis das nove.")

    # ── Itens 1 e 2 ──────────────────────────────────────────────────────────
    A.secao(doc, "2", "Itens 1 e 2 — como o modelo é usado nas pesquisas")
    A.paragrafo(doc,
        "**O que ele pediu:** levantar como esse tipo de modelo vem sendo usado em pesquisas, "
        "inclusive pelo próprio autor, e identificar de que forma os artigos utilizaram o "
        "FinBERT-PT-BR.")
    A.paragrafo(doc,
        "**O que encontramos, e foi uma surpresa:** de sete trabalhos que citam o autor, "
        "**apenas um chegou a executar o modelo** — e fora de finanças, num estudo de "
        "documentos históricos do século XVIII. Os outros seis citam o trabalho, mas não usam "
        "o modelo.")
    A.paragrafo(doc,
        "**Como explicar:** *o modelo tem 177 mil downloads por mês, o que mostra que é muito "
        "usado na prática. Mas, na literatura acadêmica, quase ninguém o aplica de fato à "
        "tarefa para a qual ele foi criado, e ninguém verifica se ele acerta. É uma lacuna "
        "clara, e a nossa pesquisa a preenche.*")
    A.paragrafo(doc,
        "**Por que isso é bom para você:** transforma o que parecia uma escolha comum — usar "
        "um modelo de prateleira — em contribuição. Somos os únicos, junto com o autor, a "
        "medir o desempenho dele.")

    # ── Item 3 ───────────────────────────────────────────────────────────────
    A.secao(doc, "3", "Item 3 — existe um modelo melhor?")
    A.paragrafo(doc,
        "**O que ele pediu:** verificar se há outro modelo, além do que usamos, que seria "
        "melhor para a pesquisa.")
    A.paragrafo(doc,
        "**O que fizemos:** levantamos doze candidatos e testamos os principais. Nenhum "
        "superou o que já usamos. Testamos ainda oito formas diferentes de melhorar o modelo "
        "atual, incluindo a adaptação ao nosso vocabulário e um modelo de linguagem "
        "generativo. **Nenhuma funcionou.**")
    A.paragrafo(doc,
        "**Como explicar:** *testei doze modelos alternativos e oito formas de melhorar o "
        "atual. Nenhuma rendeu ganho, e a mais promissora chegou a piorar. Isso indica que o "
        "modelo está perto do limite prático nesta tarefa, e que o esforço restante rende mais "
        "em outro lugar.*")
    A.paragrafo(doc,
        "**Um cuidado ao falar:** não diga que “os outros modelos são piores”. Diga que "
        "**nenhum se mostrou melhor nas condições testadas** — é mais preciso e mais defensável.")

    # ── Item 4 ───────────────────────────────────────────────────────────────
    A.secao(doc, "4", "Item 4 — alguém já faz o que fazemos?")
    A.paragrafo(doc,
        "**O que ele pediu:** verificar se algum desses trabalhos tenta fazer o mesmo que a "
        "nossa pesquisa.")
    A.paragrafo(doc,
        "**A resposta é não**, e o motivo é específico. Nossa pesquisa junta quatro coisas ao "
        "mesmo tempo: português, um ativo único, previsão de direção **e de volatilidade**, e "
        "combinação com modelos econométricos.")
    A.tabela_abnt(doc, 2, "A coluna que ninguém preenche",
        ["Trabalho", "Prevê volatilidade?"],
        [["Santos, Bianchi e Costa (2023)", "Não"],
         ["Januário et al. (2022)", "Não"],
         ["Hiew et al. (2019)", "Não"],
         ["Teles e Figueiredo (2025)", "Não"],
         ["Abílio, Coelho e Silva (2024)", "Não"],
         ["**Esta dissertação**", "**Sim**"]],
        fonte=FONTE)
    A.paragrafo(doc,
        "**Como explicar:** *nenhum dos trabalhos que encontrei prevê volatilidade. Todos "
        "param na direção do preço — e a direção fica próxima do acaso em todos eles, "
        "inclusive no nosso. A volatilidade é onde o sentimento parece ter conteúdo, e é onde "
        "a nossa contribuição está.*")

    # ── Item 5 ───────────────────────────────────────────────────────────────
    A.secao(doc, "5", "Item 5 — o artigo do link e suas referências")
    A.paragrafo(doc,
        "**O que ele pediu:** ler o artigo indicado, resumir, verificar a relação com a nossa "
        "pesquisa e resumir **todas** as referências citadas nele, com oito informações para "
        "cada uma.")
    A.paragrafo(doc,
        "**Primeira descoberta:** o artigo do link **é o artigo do próprio FinBERT-PT-BR**, ou "
        "seja, o trabalho que fundamenta o modelo que já usamos. Os itens 5 e 6 tratam do mesmo "
        "trabalho, visto de dois ângulos.")
    A.paragrafo(doc,
        "**O que foi entregue:** as 28 referências do artigo catalogadas com os oito campos "
        "pedidos, mais três referências que só aparecem na monografia do autor e que são "
        "diretamente úteis. Quinze delas — mais da metade — têm relação alta ou muito alta com "
        "a nossa pesquisa.")
    A.paragrafo(doc,
        "**O que aproveitamos de mais concreto:** a receita completa de treinamento do autor, "
        "com todos os números; o protocolo de anotação em seis etapas; e o método estatístico "
        "que ele usou para provar que o modelo dele era melhor que os concorrentes — método "
        "que passamos a usar também.")

    # ── Item 6 ───────────────────────────────────────────────────────────────
    A.secao(doc, "6", "Item 6 — o repositório do autor")
    A.paragrafo(doc,
        "**O que ele pediu:** estudar tudo o que há no repositório do autor e ver o que "
        "podemos aproveitar.")
    A.paragrafo(doc,
        "**O que encontramos de mais importante — três coisas:**")
    A.lista(doc, [
        "**A base de 503 notícias classificadas à mão está publicada.** Foi anotada por três "
        "pessoas, e é material de qualidade muito superior ao nosso, que tem um anotador só. "
        "Passamos a usá-la.",
        "**O código de treinamento não foi publicado.** Procurei em quatro lugares "
        "diferentes. Escrevi por conta própria uma versão a partir da descrição do artigo.",
        "**Há um defeito na configuração publicada do modelo.** Um campo está escrito de forma "
        "errada, o que faz o programa reportar a confiança dele numa escala incorreta. As "
        "notas estão certas; só o número da confiança está fora de escala — e o nosso índice "
        "usa esse número.",
    ])
    A.paragrafo(doc,
        "**Como explicar o defeito:** *o modelo diz a nota e o quanto confia nela. A nota está "
        "certa. A confiança está numa escala errada, por um campo mal preenchido na "
        "configuração publicada. Como o nosso índice multiplica a nota pela confiança, "
        "precisamos recalcular. O sinal e a ordem dos dias não mudam; só a magnitude.*")
    A.paragrafo(doc,
        "Vale mencionar que entramos em contato com o autor, que respondeu, e que "
        "comunicaremos esse defeito a ele — é contribuição concreta ao trabalho dele.")

    # ── Item 7 ───────────────────────────────────────────────────────────────
    A.secao(doc, "7", "Item 7 — os trabalhos que citam o autor")
    A.paragrafo(doc,
        "**O que ele pediu:** verificar os doze trabalhos que citam o autor — se usaram o "
        "modelo, como, com que resultado, e se devemos usar algum deles.")
    A.paragrafo(doc,
        "**O que foi possível:** sete dos doze foram verificados integralmente. A plataforma "
        "que lista as citações bloqueia consultas automáticas, e os cinco restantes são "
        "provavelmente trabalhos de conclusão e dissertações que as bases com registro formal "
        "não indexam. **Isso está declarado como limitação**, e o procedimento para completar "
        "manualmente está descrito.")
    A.paragrafo(doc,
        "**Os três que mais interessam:**")
    A.lista(doc, [
        "**Um trabalho de História Digital** usou o modelo combinado com outro, e descreveu "
        "uma característica dele que explica os nossos erros: ele se guia muito pelas palavras "
        "carregadas e pouco pelo contexto.",
        "**Um trabalho publicado em periódico de alto impacto** mostra que modelos treinados "
        "só em português superam os multilíngues em textos financeiros — o que sustenta a "
        "nossa escolha.",
        "**Um trabalho do nosso próprio programa, o PPGIa da PUCPR**, sobre o problema de "
        "modelos que envelhecem. Ele nos atinge diretamente: usamos um modelo congelado em "
        "fevereiro de 2024 para classificar notícias até 2026.",
    ])
    A.paragrafo(doc,
        "**Sugestão de pauta:** propor consulta ao Prof. Jean Paul Barddal, autor do terceiro "
        "trabalho e professor do nosso programa.")

    # ── Item 8 ───────────────────────────────────────────────────────────────
    A.secao(doc, "8", "Item 8 — a rotulagem precisa de especialista em finanças?")
    A.paragrafo(doc,
        "Esta é a primeira das duas perguntas difíceis, e a resposta tem três partes.")

    A.secao(doc, "8.1", "Primeiro: o gabarito tem quatro perguntas, não uma", nivel=2)
    A.tabela_abnt(doc, 3, "As quatro colunas do gabarito e o que cada uma exige",
        ["Coluna", "O que pergunta", "Exige finanças?"],
        [
            ["Sentimento", "O tom da notícia é bom, ruim ou neutro?", "**Não**"],
            ["Relevância", "Essa notícia afeta a Petrobras?", "Um pouco"],
            ["**Direção**", "**O preço vai subir ou cair?**", "**Sim, muito**"],
            ["Confiança", "O quanto você tem certeza?", "Não"],
        ], fonte=FONTE)
    A.paragrafo(doc,
        "**A observação dele se aplica com força a uma das quatro colunas.** E, revelador: "
        "**você deixou 80% dessa coluna em branco**, marcando “indefinida”. Você mesmo já "
        "havia reconhecido que não sabia responder.")

    A.secao(doc, "8.2", "Segundo: testei a observação dele contra o mercado", nivel=2)
    A.paragrafo(doc,
        "Nos 60 casos em que você arriscou dizer se o preço subiria ou cairia, comparei com o "
        "que de fato aconteceu na bolsa no pregão seguinte.")
    A.tabela_abnt(doc, 4, "O acerto da aposta humana",
        ["", "Acerto"],
        [["Sua aposta", "**46,7%**"],
         ["Responder “sobe” sempre, sem ler nada", "52,8%"]],
        fonte=FONTE)
    A.paragrafo(doc,
        "**Ele tem razão nessa coluna.** Mas há uma ressalva importante que você deve fazer "
        "espontaneamente: com apenas 60 casos, a margem de erro é grande. **O teste não prova "
        "que um especialista acertaria mais** — prova que a pergunta é testável.")

    A.secao(doc, "8.3", "Terceiro: o problema maior é outro, e ninguém tinha levantado",
            nivel=2)
    A.paragrafo(doc,
        "O autor do modelo **não usou especialistas em finanças**. Usou dois engenheiros e uma "
        "linguista. O que garantiu a qualidade do trabalho dele foram três cuidados que **o "
        "nosso gabarito não tem**: cada texto foi classificado por duas pessoas, os casos em "
        "que elas discordaram foram descartados — quase metade do total —, e a concordância "
        "entre elas foi medida formalmente.")
    A.paragrafo(doc,
        "**Como explicar:** *o senhor tem razão, e eu testei: a coluna que exige finanças "
        "acertou abaixo do acaso. Mas ao investigar encontrei um problema anterior e maior: o "
        "nosso gabarito tem um anotador só. Sem uma segunda opinião não há como medir "
        "confiabilidade — e sem isso os 58% não medem o modelo, medem a distância entre o "
        "modelo e uma pessoa não calibrada.*")
    A.paragrafo(doc,
        "**A proposta a apresentar:** o especialista entra como **árbitro de cerca de 55 "
        "casos**, e não como anotador dos 300. E a coluna que exige finanças é **aposentada** e "
        "substituída pelo retorno real da ação — que é público, objetivo e não precisa de "
        "anotador nenhum.")

    # ── Item 9 ───────────────────────────────────────────────────────────────
    A.secao(doc, "9", "Item 9 — como usar na prática as notícias rotuladas?")
    A.paragrafo(doc,
        "A segunda pergunta difícil, e a resposta começa desfazendo um mal-entendido.")
    A.paragrafo(doc,
        "**As 300 notícias não treinam nada.** Trezentos exemplos não ensinam um programa "
        "desse porte — o autor precisou de 503 **e** de uma etapa anterior com 1,4 milhão de "
        "textos. Quando tentamos treinar com 300, o programa simplesmente passou a responder "
        "sempre a mesma coisa.")
    A.paragrafo(doc,
        "**O gabarito é um instrumento de medida.** Como um termômetro aferido: ele não "
        "esquenta nada, mas sem ele nenhuma leitura significa coisa alguma.")
    A.paragrafo(doc, "Ele tem cinco usos concretos:")
    A.tabela_abnt(doc, 5, "Para que servem as 300 notícias classificadas",
        ["Uso", "O que permite"],
        [
            ["**1. Medir**",
             "Sem ele, reportaríamos os 76% do autor como se fossem nossos. Com ele, sabemos "
             "que no nosso caso são 58%"],
            ["**2. Escolher**",
             "Toda comparação entre alternativas precisa de um árbitro. Sem gabarito, escolher "
             "entre modelos vira questão de gosto"],
            ["**3. Diagnosticar**",
             "Ele não disse só “58%”. Disse onde o erro está: na categoria neutra, com 90% dos "
             "erros"],
            ["**4. Corrigir o índice**",
             "É o uso mais prático — explicado logo abaixo"],
            ["**5. Defender o resultado**",
             "Sabendo o tamanho do erro de medida, o efeito que estimamos é um piso: o efeito "
             "real é maior"],
        ], fonte=FONTE)

    A.secao(doc, "9.1", "O uso número 4, que é o melhor argumento", nivel=2)
    A.paragrafo(doc,
        "Este é o ponto que responde à pergunta dele de forma mais convincente, porque mostra "
        "300 notícias agindo sobre oito anos de dados.")
    A.paragrafo(doc,
        "Nosso índice de sentimento é, no fundo, uma contagem: quantas notícias foram "
        "positivas, quantas negativas, quantas neutras. Descobrimos que o programa erra de "
        "forma **sistemática** — ele empurra notícias neutras para os extremos. Logo a contagem "
        "está torta, e o índice está torto **todos os dias**.")
    A.paragrafo(doc,
        "**As 300 notícias classificadas permitem medir exatamente o tamanho e a direção desse "
        "erro — e corrigi-lo na série inteira.**")
    A.tabela_abnt(doc, 6, "O efeito da correção sobre as 205.697 notícias",
        ["", "Sem correção", "Com correção"],
        [["Notícias negativas", "48,5%", "31,2%"],
         ["Notícias positivas", "14,0%", "26,8%"],
         ["**Índice do período**", "**−0,345**", "**−0,044**"]],
        fonte=FONTE)
    A.paragrafo(doc,
        "**Como explicar:** *as 300 notícias não treinam o modelo — elas calibram o "
        "instrumento. Medindo o erro sistemático nelas, consigo corrigir a contagem nas 205 "
        "mil. É um conjunto pequeno ajustando a escala de uma série de oito anos.*")
    A.paragrafo(doc,
        "**E a conclusão que sai disso é substantiva:** o corpus de notícias sobre a Petrobras "
        "**não é predominantemente negativo**, como parecia. Ele é praticamente neutro. A "
        "negatividade era defeito do programa, não característica dos dados.")
    A.paragrafo(doc,
        "**Uma honestidade a manter:** essa correção **não melhora a previsão**. Testei. Ela "
        "conserta a interpretação do índice, não o poder preditivo. Dizer isso "
        "espontaneamente vale mais do que omitir.")

    # ── Fechamento ───────────────────────────────────────────────────────────
    A.secao(doc, "10", "Como fechar")
    A.paragrafo(doc,
        "Se você conseguir apresentar apenas quatro coisas, que sejam estas:")
    A.lista(doc, [
        "**A lacuna encontrada:** 177 mil downloads por mês, e quase nenhuma validação "
        "acadêmica. Somos os únicos, junto com o autor, a medir.",
        "**A resposta à pergunta dele sobre a rotulagem:** ele tem razão numa das quatro "
        "colunas, e testei isso contra o mercado. Mas o problema maior é a ausência de segunda "
        "anotação, que ninguém tinha levantado.",
        "**A resposta sobre o uso prático:** o gabarito é instrumento de medida e de "
        "calibração, não base de treino. E ele revelou que o corpus não é negativo — a "
        "negatividade era defeito do programa.",
        "**A conclusão do trabalho técnico:** oito tentativas de melhorar o classificador, "
        "todas medidas, nenhuma bem-sucedida. Encerro essa linha e passo à volatilidade e à "
        "redação.",
    ])
    A.paragrafo(doc,
        "E, se houver espaço, mencione que quer conversar com o Prof. Barddal sobre o problema "
        "dos modelos que envelhecem. É colaboração interna e de baixo custo.")

    doc.save(SAIDA)
    print(f"OK -> {SAIDA.name}")


if __name__ == "__main__":
    main()
