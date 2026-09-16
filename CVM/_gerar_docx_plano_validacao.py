# -*- coding: utf-8 -*-
# ==============================================================================
#   Plano de execução — validação reversa: publicação da CVM x pregão seguinte
#   Pedido dos orientadores na mentoria de setembro/2026
#   Saída: CVM/02_PLANO_VALIDACAO.docx
# ==============================================================================
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(RAIZ / "src" / "comum"))

import abnt_docx as A  # noqa: E402

FONTE = "Elaborado pelo autor (2026)"
SAIDA = AQUI / "02_PLANO_VALIDACAO.docx"


def main() -> None:
    doc = A.novo_documento()

    A.capa(
        doc,
        titulo="Engenharia reversa da notícia",
        subtitulo="Plano de execução: a publicação da CVM divulgada após o "
                  "fechamento prevê o que o preço faz no pregão seguinte?",
        autor="Vanderlei Barbosa da Silva",
        orientador="Orientador: Prof. Dr. Julio Cesar Nievola",
        instituicao="PUCPR — Programa de Pós-Graduação em Informática (PPGIa)",
        descricao="Plano detalhado de execução, elaborado antes de rodar qualquer "
                  "experimento, em resposta ao pedido dos orientadores na mentoria de "
                  "setembro de 2026. Registra o desenho, as previsões, as lacunas de "
                  "dados e os riscos, para que o resultado possa ser julgado contra o "
                  "que foi combinado de antemão. Elaborado em 16 de setembro de 2026.",
    )

    # ── 1 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "1", "O pedido, com as minhas palavras")

    A.paragrafo(doc,
        "Temos duas coisas guardadas de forma independente: **a publicação** — com "
        "data, hora oficial e classificação — e **o que o preço fez depois**. O "
        "exercício é confrontar as duas.")

    A.paragrafo(doc,
        "**O recorte é o que dá força ao desenho:** analisar apenas o que foi divulgado "
        "**após o fechamento do pregão**, e observar o **pregão seguinte**. A "
        "informação chega com o mercado fechado; ninguém pode negociar sobre ela até a "
        "abertura seguinte. **É o experimento natural mais limpo disponível para esta "
        "pergunta.**")

    A.paragrafo(doc, "E são duas rodadas, na ordem pedida:")

    A.lista(doc, [
        "**Rodada A — só com a classificação que já vem na publicação.** A CVM organiza "
        "os documentos em categorias, e duas nos interessam: *Fato Relevante* e "
        "*Comunicado ao Mercado*.",
        "**Rodada B — com a classificação que nós produzimos.** O FinBERT-PT-BR lê o "
        "texto e diz se é positivo, negativo ou neutro.",
        "**E a comparação entre as duas**, que é o objetivo final.",
    ])

    # ── 2 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "2", "A distinção que decide o desenho")

    A.paragrafo(doc,
        "**Antes de escrever uma linha de código, é preciso fixar uma coisa: as duas "
        "rodadas não respondem à mesma pergunta.**")

    A.tabela_abnt(doc, "1", "O que cada classificação é capaz de dizer",
        ["", "Rodada A — CVM", "Rodada B — nossa"],
        [
            ["O que o rótulo informa", "que algo aconteceu", "se foi bom ou ruim"],
            ["O rótulo tem sinal?", "NÃO", "SIM"],
            ["Pode testar magnitude (volatilidade, volume)?", "sim", "sim"],
            ["Pode testar DIREÇÃO (subiu ou desceu)?", "NÃO", "SIM"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**O rótulo “Fato Relevante” não distingue notícia boa de notícia ruim.** Ele "
        "diz que o fato é capaz de influir na cotação — para cima ou para baixo, "
        "indiferentemente.")

    A.paragrafo(doc,
        "**Consequência prática, e registro-a agora para que ninguém se surpreenda "
        "depois:** se testarmos direção na Rodada A, o resultado **tem de dar zero por "
        "construção**. As altas e as baixas se cancelam na média. **Isso já aconteceu** "
        "no estudo agregado que rodei em agosto: retorno anormal médio de −0,041%, com "
        "valor-p de 0,64.")

    A.paragrafo(doc,
        "**Isso não é defeito do pedido dos senhores — é justamente o que torna a "
        "comparação valiosa.** A Rodada A estabelece o piso: houve impacto? A Rodada B "
        "testa se nós conseguimos dizer **para que lado**. **É nesse segundo ponto que "
        "a contribuição desta dissertação vive ou morre.**")

    # ── 3 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "3", "Sobre a palavra “causou”")

    A.paragrafo(doc,
        "Os senhores pediram para verificar se a notícia **causou** mudança no preço. "
        "Convém ser exato sobre o que o método entrega.")

    A.paragrafo(doc,
        "**Um estudo de evento mede associação**, sob a hipótese de que nenhuma outra "
        "informação relevante chegou naquela janela. Não estabelece causa no sentido "
        "estrito, porque não há grupo aleatorizado — ninguém sorteia quais empresas "
        "publicam fato relevante.")

    A.paragrafo(doc,
        "**Mas o recorte escolhido pelos senhores é o que mais se aproxima disso.** A "
        "notícia chega com o mercado fechado, e o preço só pode responder na abertura "
        "seguinte. **A ordem temporal fica inequívoca.** O que ainda pode contaminar: "
        "notícia da madrugada, mercados externos, preço do petróleo.")

    A.paragrafo(doc, "**Três controles que proponho, e que atacam isso:**")

    A.lista(doc, [
        "**descontar o Ibovespa** de cada retorno, pelo modelo de mercado — já fazemos;",
        "**grupo de controle**: os mesmos papéis, em noites **sem** comunicado nenhum. "
        "Se a diferença aparecer só nas noites com publicação, o argumento fica forte;",
        "**descartar noites contaminadas** — quando a empresa publicou mais de um "
        "documento, ou quando o Ibovespa se moveu acima de um limiar.",
    ])

    # ── 4 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "4", "O ganho técnico que o recorte abre")

    A.paragrafo(doc,
        "Para notícia divulgada após o fechamento, a reação se reparte em dois pedaços "
        "que hoje estão misturados no nosso dado:")

    A.tabela_abnt(doc, "2", "Decomposição do pregão seguinte",
        ["Pedaço", "Como se calcula", "O que mede"],
        [
            ["Gap de abertura",
             "ln(Abertura de d+1 ÷ Fechamento de d)",
             "a reação PURA à notícia da noite"],
            ["Intradiário",
             "ln(Fechamento de d+1 ÷ Abertura de d+1)",
             "o que veio DEPOIS da abertura"],
            ["Pregão inteiro",
             "ln(Fechamento de d+1 ÷ Fechamento de d)",
             "os dois somados — é o que usávamos"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**O gap de abertura é a medida mais limpa que existe para o desenho pedido.** "
        "Notícia que sai às 19h só pode ser precificada na abertura do dia seguinte; "
        "tudo o que aparece no gap é atribuível ao intervalo em que ela foi a novidade.")

    A.paragrafo(doc,
        "**E abre um teste de falsificação valioso:** se o efeito estiver no gap, a "
        "história se sustenta. **Se estiver no intradiário e não no gap, alguma outra "
        "coisa moveu o preço** — e é melhor descobrirmos isso do que publicarmos um "
        "resultado frágil.")

    # ── 5 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "5", "O que falta antes de executar")

    A.paragrafo(doc,
        "Conferi a base hoje. **Há três lacunas**, e duas delas bloqueiam o desenho "
        "como foi pedido.")

    A.tabela_abnt(doc, "3", "Lacunas identificadas",
        ["O que falta", "Situação atual", "Bloqueia?", "Custo"],
        [
            ["Hora oficial dos Comunicados ao Mercado",
             "5.628 de 5.628 Fatos Relevantes têm; 0 de 14.793 Comunicados",
             "SIM — sem ela não há grupo de comparação sob o mesmo filtro",
             "~4 h, em segundo plano"],
            ["Volume, Abertura, Máxima e Mínima",
             "só temos o Fechamento",
             "SIM — os senhores pediram volume, e o gap exige a Abertura",
             "~15 min"],
            ["Classificação FinBERT dos textos da CVM",
             "nunca foi rodada",
             "só a Rodada B",
             "~1 h no Colab"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**Sobre a terceira:** o PyTorch está quebrado nesta máquina, e por isso a "
        "classificação terá de rodar no Colab. A coleta e toda a análise estatística "
        "rodam aqui.")

    # ── 6 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "6", "Tamanho do experimento")

    A.paragrafo(doc,
        "Dimensionei com o que já está em mãos, para os senhores saberem de antemão "
        "com quantos casos vamos trabalhar:")

    A.tabela_abnt(doc, "4", "Eventos disponíveis",
        ["", "Quantidade"],
        [
            ["Fatos Relevantes com hora oficial", "5.628"],
            ["... divulgados APÓS O FECHAMENTO (17h ou depois)", "3.850  (68,4%)"],
            ["papéis distintos", "62"],
            ["período", "jan/2018 a ago/2026"],
            ["PETR4, isoladamente", "375"],
            ["projeção com os Comunicados incluídos", "cerca de 14.000"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**Os papéis com mais eventos após o fechamento:** PETR4 (375), ELET3 (206), "
        "CCRO3 (151), OIBR3 (147), VALE3 (128), VBBR3 (123), BBAS3 (113), PRIO3 (109).")

    # ── 7 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "7", "O plano, fase a fase")

    A.secao(doc, "7.1", "Fase 0 — fechar as lacunas", nivel=2)

    A.lista(doc, [
        "**0.1** Coletar a hora oficial dos 14.793 Comunicados ao Mercado, pelo mesmo "
        "Protocolo de Entrega já usado nos Fatos Relevantes. Retomável, em segundo "
        "plano.",
        "**0.2** Recoletar os preços dos 54 papéis com **Abertura, Máxima, Mínima, "
        "Fechamento e Volume**.",
        "**0.3** Classificar os 20.421 textos com o FinBERT-PT-BR, no Colab, guardando "
        "rótulo e escore.",
    ])

    A.secao(doc, "7.2", "Fase 1 — montar a base do experimento", nivel=2)

    A.lista(doc, [
        "**1.1** Filtrar: apenas documentos entregues **a partir das 17h**, com pregão "
        "seguinte disponível.",
        "**1.2** Para cada evento, calcular o **gap de abertura**, o **retorno "
        "intradiário**, o **retorno do pregão inteiro**, a **volatilidade de "
        "Parkinson** do dia seguinte (que usa máxima e mínima) e o **volume anormal**.",
        "**1.3** Montar o **grupo de controle**: os mesmos papéis, em noites sem "
        "comunicado nenhum, casadas por período.",
        "**1.4** Marcar as **noites contaminadas** — mais de um documento da mesma "
        "empresa, ou Ibovespa muito agitado —, para rodar com e sem elas.",
    ])

    A.secao(doc, "7.3", "Fase 2 — Rodada A, só com a classificação da CVM", nivel=2)

    A.lista(doc, [
        "**2.1 Volume anormal em d+1**: Fato Relevante contra Comunicado ao Mercado "
        "contra controle.",
        "**2.2 Volatilidade em d+1**, pela mesma comparação de três grupos.",
        "**2.3 Tamanho do gap de abertura**, idem.",
        "**2.4 Direção**: rodar, mostrar que dá perto de zero, **e explicar por que "
        "tinha de dar** — é a demonstração de que a Rodada B é necessária.",
        "**2.5 Casos ilustrativos**: os vinte maiores choques, com empresa, data, hora, "
        "texto do comunicado e o que o preço fez. **É a tabela que os senhores pediram "
        "como exemplo — “no dia x foi publicado...”.**",
    ])

    A.secao(doc, "7.4", "Fase 3 — Rodada B, com a nossa classificação", nivel=2)

    A.lista(doc, [
        "**3.1 Direção com sinal** — notícia classificada como negativa produz retorno "
        "negativo no pregão seguinte? **Este é o teste central de toda a dissertação.**",
        "**3.2 Taxa de acerto direcional** no gap de abertura, com teste binomial "
        "contra o acaso e contra a classe majoritária.",
        "**3.3 Volatilidade e volume por classe de sentimento.**",
        "**3.4** O sentimento acrescenta **algo além** da categoria da CVM? Regressão "
        "com as duas variáveis juntas.",
    ])

    A.secao(doc, "7.5", "Fase 4 — a comparação", nivel=2)

    A.lista(doc, [
        "**4.1** Tabela lado a lado: o que cada rodada conseguiu e não conseguiu.",
        "**4.2** O que a categoria da CVM captura que o sentimento não captura, e o "
        "contrário.",
        "**4.3** Modelo conjunto, usando as duas informações.",
    ])

    A.secao(doc, "7.6", "Fase 5 — entrega", nivel=2)

    A.lista(doc, [
        "**5.1** CSV **caso a caso** — uma linha por evento, com texto, classificação, "
        "hora, e tudo o que o preço fez. É a engenharia reversa auditável, que permite "
        "a qualquer pessoa conferir um caso na mão.",
        "**5.2** Documento com os resultados.",
        "**5.3** Planilha de apoio para a apresentação.",
    ])

    # ── 8 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "8", "O que eu espero encontrar — registrado antes de rodar")

    A.paragrafo(doc,
        "**Registro as previsões agora, de antemão.** Se acertar, o desenho ganha "
        "credibilidade; se errar, fica documentado que não foi ajuste posterior.")

    A.tabela_abnt(doc, "5", "Previsões",
        ["Teste", "O que espero", "Confiança"],
        [
            ["Rodada A — volume anormal em d+1", "efeito FORTE", "alta"],
            ["Rodada A — volatilidade em d+1", "efeito forte, já medido em agosto", "alta"],
            ["Rodada A — direção", "ZERO, por construção", "altíssima"],
            ["Rodada A — Fato Relevante mexe mais que Comunicado", "sim", "alta"],
            ["Rodada B — direção com sinal", "FRACO ou nulo", "média"],
            ["Efeito concentrado na cauda, não no caso típico", "sim", "alta"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**Sobre a previsão desconfortável — a da Rodada B — devo ser franco.** Duas "
        "coisas que já sabemos apontam para um resultado fraco. Primeira: o nosso "
        "classificador tem viés contra a classe positiva; diante de 224 notícias que "
        "casas de análise consideraram favoráveis à Petrobras, ele enxergou 21,9% de "
        "positivas contra os 84,8% dos analistas. Segunda: a direção deu perto do acaso "
        "em todos os testes que já fizemos.")

    A.paragrafo(doc,
        "**E ainda assim vale rodar**, por três razões: nunca testamos direção com o "
        "recorte limpo de “após o fechamento contra o gap de abertura”; o corpus da CVM "
        "é de qualidade muito superior ao de manchetes de portal; e **um resultado nulo "
        "aqui, com este desenho, é uma conclusão publicável** — é a demonstração de que "
        "o problema não está no dado, e sim na tarefa.")

    A.paragrafo(doc,
        "**A minha aposta de onde virá o resultado mais forte é o VOLUME**, e não o "
        "preço. Volume anormal é a medida clássica de chegada de informação, e Hashami "
        "e Maldonado (2025) mostraram, no petróleo, que a simples contagem de notícias "
        "superou todos os métodos de sentimento.")

    # ── 9 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "9", "Riscos")

    A.tabela_abnt(doc, "6", "O que pode dar errado",
        ["Risco", "Tratamento"],
        [
            ["Noite com mais de um comunicado da mesma empresa",
             "marcar e rodar com e sem esses casos"],
            ["Choque de mercado na mesma noite (pandemia, eleição)",
             "descontar o Ibovespa; sinalizar dias de Ibovespa extremo"],
            ["Papel pouco líquido — gap sem negociação real",
             "exigir volume mínimo no período de estimação"],
            ["Resultado e balanço divulgados junto com o comunicado",
             "separar por Tipo e Espécie, que a base já traz"],
            ["Autodeclaração da categoria pela própria companhia",
             "já registrado como limitação; embaça os grupos e trabalha CONTRA nós"],
            ["Texto do Assunto é curto (47 caracteres em média)",
             "se a Rodada B falhar, testar com o PDF completo antes de concluir"],
        ], fonte=FONTE)

    # ── 10 ───────────────────────────────────────────────────────────────────
    A.secao(doc, "10", "Duas decisões que peço aos senhores")

    A.lista(doc, [
        "**Vale gastar as 4 horas de coleta da hora dos Comunicados ao Mercado?** A "
        "minha recomendação é sim: sem isso, o grupo de comparação fica sem o mesmo "
        "filtro de horário, e a comparação perde o rigor. Roda em segundo plano, sem "
        "atrapalhar o resto.",
        "**Trabalhamos com os 54 papéis ou só com a PETR4?** Recomendo **os 54, com um "
        "recorte da PETR4 em separado** — os 54 dão o poder estatístico que nos falta "
        "em relação à literatura, e a PETR4 mantém o fio da dissertação.",
    ])

    A.secao(doc, "11", "Em quatro frases")

    A.lista(doc, [
        "“Pego só o que a empresa publicou depois que o mercado fechou, e olho o que o "
        "preço fez na abertura seguinte — quando ninguém pôde negociar antes.”",
        "“Primeiro uso só o rótulo que já vem da CVM, que diz que algo aconteceu mas "
        "não diz se é bom ou ruim. Ele só pode testar o tamanho do movimento.”",
        "“Depois uso o meu classificador, que diz o lado. Só ele pode testar a "
        "direção — e é aí que a minha contribuição se prova ou não.”",
        "“E registro antes de rodar o que espero achar, inclusive que a direção "
        "provavelmente vai falhar, para que o resultado não pareça ajustado depois.”",
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
