# -*- coding: utf-8 -*-
# ==============================================================================
#   ARTIGO 1 — O relógio da CVM
#   Saída: Artigos/01_ARTIGO_CVM_HORA_OFICIAL.docx
#
#   Formato: artigo completo em português, padrão de revista nacional de
#   finanças. Enxugável para Finance Research Letters (~3.000 palavras) se os
#   orientadores optarem pelo internacional.
# ==============================================================================
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(RAIZ / "src" / "comum"))

import abnt_docx as A  # noqa: E402

FONTE = "Elaborado pelos autores (2026)"
SAIDA = AQUI / "01_ARTIGO_CVM_HORA_OFICIAL.docx"
N = json.loads((RAIZ / "CVM" / "dados" / "numeros_artigo1.json").read_text(encoding="utf-8"))


def main() -> None:
    doc = A.novo_documento()

    A.capa(
        doc,
        titulo="O relógio da CVM",
        subtitulo="Divulgação obrigatória e reação do preço: evidência de 11.161 "
                  "comunicados com hora oficial de entrega",
        autor="Vanderlei Barbosa da Silva · Julio Cesar Nievola",
        orientador="Programa de Pós-Graduação em Informática (PPGIa)",
        instituicao="Pontifícia Universidade Católica do Paraná",
        descricao="Versão de trabalho para apreciação dos orientadores. A autoria e "
                  "a ordem de assinatura estão em aberto; registra-se que a medida de "
                  "volatilidade relativa à semana anterior, empregada na Seção 4.3, "
                  "foi sugerida pelo Prof. Dr. Emerson Cabrera Paraiso, o que pode "
                  "justificar sua inclusão como coautor. Elaborado em 19 de setembro "
                  "de 2026.",
    )

    # ══ RESUMO ═══════════════════════════════════════════════════════════════
    A.secao(doc, "", "Resumo")

    A.paragrafo(doc,
        "A Resolução CVM nº 44/2021 obriga companhias abertas brasileiras a divulgar "
        "todo ato ou fato capaz de influir na cotação de seus valores mobiliários. "
        "Verificamos empiricamente se essa presunção legal se sustenta. O conjunto de "
        f"dados abertos da autarquia registra apenas a data de entrega; recuperamos a "
        f"**hora oficial de {N['n_com_hora']:,} documentos**".replace(",", ".") +
        ", com precisão de segundos, a partir do Protocolo de Entrega emitido pela "
        "própria CVM. Isso permite isolar os comunicados divulgados com o mercado "
        f"fechado — {N['quando']['depois']}% do total — e observar o pregão seguinte, "
        "quando a informação pôde ser negociada pela primeira vez. Sobre "
        f"{N['n_eventos']:,} eventos de {N['n_papeis']} ações da B3 entre 2018 e "
        "2026".replace(",", ".") +
        f", comparados a {N['n_controle']:,} pregões sem divulgação".replace(",", ".") +
        ", encontramos aumento de "
        f"{N['vol']['exc']}% na volatilidade e de {N['qtd']['exc']}% no volume "
        "negociado, ambos com significância inequívoca, e **nenhum efeito sobre a "
        "direção do retorno**. A distinção legal entre Fato Relevante e Comunicado ao "
        f"Mercado corresponde a uma diferença empírica de {N['fr_vs_cm']['volatilidade (sacolejo)']['razao']}"
        " vezes na volatilidade. O achado central, porém, é distributivo: "
        f"**{N['nao_moveu']}% dos comunicados não produzem movimento algum**, e o "
        "efeito médio decorre de uma minoria de eventos. A presunção legal de "
        "relevância é válida em média e falsa na maioria dos casos individuais.",
        recuo=False)

    A.paragrafo(doc,
        "**Palavras-chave:** divulgação obrigatória; fato relevante; estudo de evento; "
        "volatilidade; Comissão de Valores Mobiliários.", recuo=False)

    # ══ 1 INTRODUÇÃO ═════════════════════════════════════════════════════════
    A.secao(doc, "1", "Introdução")

    A.paragrafo(doc,
        "O artigo 2º da Resolução CVM nº 44/2021 define como relevante todo ato ou "
        "fato que possa **influir de modo ponderável** na cotação dos valores "
        "mobiliários de uma companhia aberta, na decisão de investidores de comprar, "
        "vender ou manter esses papéis, ou no exercício de direitos a eles inerentes. "
        "A norma impõe ao Diretor de Relações com Investidores o dever de divulgá-lo, "
        "e submete o descumprimento a sanção administrativa.")

    A.paragrafo(doc,
        "A norma, portanto, incorpora uma **presunção empírica**: o que ela manda "
        "divulgar move preço. Essa presunção é raramente examinada. Quando o é, "
        "costuma sê-lo sobre amostras pequenas, sem grupo de controle, e — "
        "decisivamente — **sem conhecimento da hora em que o documento foi "
        "entregue**.")

    A.paragrafo(doc,
        "A ausência da hora não é detalhe operacional. Um comunicado divulgado às onze "
        "da manhã e um movimento de preço às onze e meia formam uma sequência "
        "ambígua: pode a divulgação ter causado o movimento, ou pode a companhia ter "
        "se manifestado porque o preço já se movia. Um comunicado divulgado às "
        "dezenove horas, com a bolsa fechada, não admite essa ambiguidade. **A ordem "
        "temporal é inequívoca, e a primeira oportunidade de negociação é a abertura "
        "do pregão seguinte.**")

    A.paragrafo(doc,
        "O conjunto de dados abertos mantido pela CVM — a série IPE, de Informações "
        "Periódicas e Eventuais — registra a data de entrega, e apenas a data. O "
        "dicionário oficial do conjunto confirma: o campo `Data_Entrega` é descrito "
        "como *data de entrega/recebimento do documento*, sem qualquer componente "
        "horário.")

    A.paragrafo(doc,
        "**A contribuição metodológica deste trabalho começa aí.** A hora existe, com "
        "precisão de segundos, no Protocolo de Entrega — o recibo que a autarquia "
        "emite para cada documento protocolado e disponibiliza publicamente. "
        f"Recuperamos esse recibo para {N['n_com_hora']:,} dos {N['n_docs_cvm']:,} "
        "documentos".replace(",", ".") +
        " de interesse, em cobertura praticamente integral.")

    A.paragrafo(doc, "O trabalho responde a quatro perguntas:")

    A.lista(doc, [
        "**Quando as companhias divulgam?** A norma recomenda que a divulgação ocorra "
        "fora do horário de negociação; verificamos em que medida isso é observado.",
        "**O carimbo de hora é informativo?** Se o for, a reação deve concentrar-se no "
        "mesmo pregão quando a divulgação é matinal, e no pregão seguinte quando é "
        "noturna.",
        "**A divulgação move o preço?** Separadamente em volatilidade, volume e "
        "direção, contra grupo de controle.",
        "**A distinção legal entre as categorias tem correspondência empírica?** O que "
        "a norma trata como mais relevante move mais?",
    ])

    # ══ 2 REFERENCIAL ════════════════════════════════════════════════════════
    A.secao(doc, "2", "Referencial")

    A.secao(doc, "2.1", "A obrigação de divulgar", nivel=2)

    A.paragrafo(doc,
        "A Resolução CVM nº 44, em vigor desde setembro de 2021 e sucessora da "
        "Instrução CVM nº 358/2002, organiza a divulgação em categorias. Duas "
        "interessam a este trabalho. O **Fato Relevante** é a categoria de maior "
        "peso, reservada ao que a companhia julga capaz de influir na cotação. O "
        "**Comunicado ao Mercado** abriga informação que a companhia entende dever "
        "levar ao conhecimento do público sem atingir aquele patamar.")

    A.paragrafo(doc,
        "**O enquadramento é feito pela própria companhia**, por meio do Diretor de "
        "Relações com Investidores, sob obrigação legal e sob fiscalização da "
        "autarquia. Trata-se, portanto, de **autodeclaração com consequência "
        "jurídica** — não de classificação independente. A distinção importa para a "
        "leitura dos resultados e é retomada na Seção 7.")

    A.paragrafo(doc,
        "O artigo 5º recomenda que a divulgação ocorra **preferencialmente após o "
        "encerramento dos negócios**, ou antes de seu início. A recomendação existe "
        "justamente porque o regulador reconhece o problema de assimetria que a "
        "divulgação intradiária cria.")

    A.secao(doc, "2.2", "Estudo de evento", nivel=2)

    A.paragrafo(doc,
        "O método empregado é o estudo de evento, cuja formulação moderna remonta a "
        "Fama, Fisher, Jensen e Roll (1969) e cujas escolhas de desenho foram "
        "sistematizadas por Brown e Warner (1985) e revisadas por MacKinlay (1997). O "
        "procedimento estima o comportamento normal do ativo em janela anterior ao "
        "evento e mede o desvio observado na janela do evento.")

    A.paragrafo(doc,
        "Adotamos duas particularidades. A primeira é a **linha de base recente**: em "
        "lugar de janela de estimação distante, comparamos o pregão de reação com a "
        "média dos cinco pregões imediatamente anteriores. A justificativa é a "
        "persistência da volatilidade, documentada desde Engle (1982) e explorada de "
        "forma explícita pelo modelo heterogêneo autorregressivo de Corsi (2009): "
        "**bater a média da própria semana anterior é teste mais exigente que bater "
        "uma média de cem dias atrás**, porque a semana anterior já incorpora o regime "
        "corrente.")

    A.paragrafo(doc,
        "A segunda é o **estimador de Parkinson (1980)**, que mede a variação diária "
        "pelo intervalo entre máxima e mínima em vez de pelo fechamento. É "
        "substancialmente mais eficiente que o estimador baseado apenas em "
        "fechamentos, e capta o dia que oscila fortemente e retorna ao ponto de "
        "partida — caso em que o fechamento nada revela.")

    A.secao(doc, "2.3", "O que a literatura recente encontra", nivel=2)

    A.paragrafo(doc,
        "A literatura sobre texto e preço tem convergido para uma assimetria. "
        "Halousková e Lyócsa (2025), em 404 ações do S&P 500, melhoram previsões de "
        "volatilidade em 98,76% dos ativos, com ganho maior nos dias de variação "
        "extrema. Bodilsen e Lunde (2025) reportam melhora na previsão de "
        "volatilidade por analítica de notícias, com ganho crescente no horizonte. "
        "Hashami e Maldonado (2025), sobre o petróleo Brent, encontram que a simples "
        "**contagem** de notícias supera todos os métodos de análise de sentimento "
        "testados.")

    A.paragrafo(doc,
        "Na previsão de direção, os resultados são mais modestos. Nguyen, Shirai e "
        "Velcin (2015) relatam ganhos de 2,1 a 9,8 pontos percentuais sobre modelo "
        "baseado apenas em preços. Ruan e Jiang (2025) obtêm ganho de 7,9 pontos com "
        "arquitetura que combina sentimento e indicadores técnicos. Schumaker e Chen "
        "(2009), medindo reação vinte minutos após a publicação, relatam 71,18% de "
        "acerto direcional — valor que, convém notar, é o melhor entre seis esquemas "
        "de particionamento por eles testados; no particionamento por ação "
        "individual, o desempenho cai para 56,92%.")

    A.paragrafo(doc,
        "**Este trabalho difere dessa literatura em dois pontos.** Não emprega "
        "classificação de sentimento — mede o efeito da divulgação sem ler seu "
        "conteúdo. E dispõe da hora oficial de entrega, o que permite o recorte "
        "temporal que a literatura citada não pôde fazer.")

    # ══ 3 DADOS ══════════════════════════════════════════════════════════════
    A.secao(doc, "3", "Dados")

    A.secao(doc, "3.1", "Os comunicados", nivel=2)

    A.paragrafo(doc,
        "Os documentos provêm da série IPE do portal de dados abertos da CVM "
        "(`dados.cvm.gov.br`), em arquivos anuais. Foram coletados os exercícios de "
        "2018 a 2026, dos quais se retiveram as categorias Fato Relevante e "
        "Comunicado ao Mercado. Cada registro traz o CNPJ e o nome da companhia, a "
        "categoria, a data de entrega, o campo `Assunto` — uma linha descritiva — e o "
        "endereço do documento íntegro.")

    A.secao(doc, "3.2", "A recuperação da hora oficial", nivel=2)

    A.paragrafo(doc,
        "**Esta subseção descreve a principal contribuição metodológica do trabalho.**")

    A.paragrafo(doc,
        "Três rotas foram examinadas. A primeira, e descartada, seria inferir a hora "
        "dos metadados internos do arquivo PDF. **Foi rejeitada por medir a coisa "
        "errada:** o carimbo `ModDate` registra quando a companhia finalizou o "
        "arquivo, não quando a autarquia o recebeu. Em amostra de vinte e cinco "
        "documentos, essa aproximação indicava que 40% das divulgações ocorriam com o "
        f"pregão aberto; o dado oficial mostra {N['quando']['pregao']}%. **Hora "
        "aproximada, num desenho que depende da ordem temporal, é pior que hora "
        "nenhuma.**")

    A.paragrafo(doc,
        "A segunda rota é a tela pública de consulta do sistema RAD, que devolve data "
        "e hora, mas cujo alcance se limita ao exercício corrente — inútil para série "
        "histórica.")

    A.paragrafo(doc,
        "A terceira, adotada, é o **Protocolo de Entrega**: o recibo que a CVM emite "
        "para cada documento protocolado, acessível por método público do próprio "
        "sistema mediante o número sequencial presente no endereço de descarga do "
        "conjunto aberto. O recibo declara, em texto:")

    A.paragrafo(doc,
        "*Protocolo de Entrega — 9512 - PETRÓLEO BRASILEIRO S.A. - PETROBRAS. O "
        "documento foi entregue para CVM e B3. Tipo de Documento: Fato Relevante. "
        "Data do Documento: 03/01/2018. **Data da Entrega: 03/01/2018 07:20:19.** "
        "Versão: 1. Protocolo: 009512IPE030120180104310213-17.*", recuo=False)

    A.paragrafo(doc,
        f"O procedimento recuperou {N['n_com_hora']:,} recibos de {N['n_docs_cvm']:,} "
        "documentos".replace(",", ".") +
        " — cobertura de 99,99%. **A data constante do recibo coincide com a do "
        "conjunto aberto em todos os casos**, o que valida mutuamente as duas fontes.")

    A.secao(doc, "3.3", "Cotações e amostra final", nivel=2)

    A.paragrafo(doc,
        "As companhias foram associadas a papéis negociados na B3 por correspondência "
        "de razão social. Coletaram-se séries diárias de abertura, máxima, mínima, "
        "fechamento e volume, além do Ibovespa. Quatro papéis com histórico "
        "indisponível no provedor foram excluídos; duas companhias cuja fusão "
        "posterior impediria a atribuição correta da série de preços foram igualmente "
        "removidas, por decisão conservadora.")

    A.tabela_abnt(doc, "1", "Composição da amostra",
        ["", "Quantidade"],
        [
            ["documentos da CVM com hora oficial", f"{N['n_com_hora']:,}".replace(",", ".")],
            ["divulgados após o encerramento do pregão", f"{N['quando']['depois']}%"],
            ["eventos com preço disponível e janela completa", f"{N['n_eventos']:,}".replace(",", ".")],
            ["dos quais Fatos Relevantes", f"{N['n_fr']:,}".replace(",", ".")],
            ["dos quais Comunicados ao Mercado", f"{N['n_cm']:,}".replace(",", ".")],
            ["papéis distintos", str(N["n_papeis"])],
            ["período", N["periodo"].replace("/", "/")],
            ["pregões de controle", f"{N['n_controle']:,}".replace(",", ".")],
        ], fonte=FONTE)

    # ══ 4 MÉTODO ═════════════════════════════════════════════════════════════
    A.secao(doc, "4", "Método")

    A.secao(doc, "4.1", "O recorte temporal", nivel=2)

    A.paragrafo(doc,
        "Retêm-se apenas os documentos entregues às 17 horas ou depois. O pregão de "
        "reação é o primeiro pregão subsequente à entrega. Quando a entrega ocorre em "
        "dia sem negociação, o pregão de reação é o primeiro que se abrir.")

    A.paragrafo(doc,
        "O pregão de reação decompõe-se em duas partes, e a distinção é relevante:")

    A.lista(doc, [
        "**o salto de abertura**, dado por $\\ln(A_{d+1} / F_d)$, em que $A$ é a "
        "abertura e $F$ o fechamento — é a reação ao intervalo em que a informação "
        "esteve disponível sem possibilidade de negociação;",
        "**o percurso intradiário**, $\\ln(F_{d+1} / A_{d+1})$, posterior ao momento "
        "em que o mercado já incorporou a informação na abertura.",
    ])

    A.secao(doc, "4.2", "As medidas", nivel=2)

    A.paragrafo(doc,
        "A volatilidade do pregão de reação é estimada por Parkinson (1980):")

    A.paragrafo(doc,
        "$$\\sigma_t = \\sqrt{\\frac{[\\ln(H_t / L_t)]^2}{4\\ln 2}}$$", recuo=False)

    A.paragrafo(doc,
        "em que $H$ e $L$ são a máxima e a mínima do dia. O volume é o número de "
        "ações negociadas. A direção é o sinal do retorno logarítmico.")

    A.secao(doc, "4.3", "A linha de base recente", nivel=2)

    A.paragrafo(doc,
        "Cada medida do pregão de reação é dividida pela média dos cinco pregões "
        "anteriores, **excluídos os dois imediatamente precedentes** — isto é, a "
        "janela $[-6, -2]$. A exclusão é deliberada: havendo vazamento de informação "
        "na véspera, incluí-la na linha de base a inflaria e atenuaria o efeito "
        "medido.")

    A.paragrafo(doc,
        "A robustez a essa escolha é verificada com janelas de duas semanas, de um "
        "mês e com a janela distante convencional (Seção 5.3).")

    A.secao(doc, "4.4", "O grupo de controle e o piso da razão", nivel=2)

    A.paragrafo(doc,
        "**A razão descrita acima não tem valor neutro igual a 1,00, e tratá-la como "
        "se tivesse produz erro material.** A distribuição de uma razão entre uma "
        "observação e a média de observações recentes é assimétrica à direita: um dia "
        "pode exceder a média em múltiplos arbitrários, mas não pode ficar abaixo "
        "dela em proporção equivalente, dado que o piso é zero. Em consequência, a "
        "média da razão excede a unidade mesmo na ausência de qualquer evento.")

    A.paragrafo(doc,
        f"Para determinar esse piso, a mesma razão foi calculada em {N['n_controle']:,} "
        "pregões".replace(",", ".") +
        " dos mesmos papéis e do mesmo período, **nos quais não houve divulgação "
        f"alguma**. O piso é de {N['vol']['sem']:.3f} na volatilidade e "
        f"{N['qtd']['sem']:.3f} no volume.")

    A.paragrafo(doc,
        "**Todos os excessos reportados na Seção 5 são medidos contra esse piso, e não "
        "contra a unidade.** A diferença não é trivial: contra a unidade, o excesso de "
        "volatilidade seria de 13,0% e o de volume de 23,5%; contra o piso, são "
        f"{N['vol']['exc']}% e {N['qtd']['exc']}%.")

    # ══ 5 RESULTADOS ═════════════════════════════════════════════════════════
    A.secao(doc, "5", "Resultados")

    A.secao(doc, "5.1", "Quando as companhias divulgam", nivel=2)

    A.tabela_abnt(doc, "2", "Momento da entrega, pelo recibo oficial",
        ["Faixa horária", "Proporção"],
        [
            ["até 09h59 — antes da abertura", f"{N['quando']['antes']}%"],
            ["10h00 às 16h59 — com o pregão aberto", f"{N['quando']['pregao']}%"],
            ["17h00 em diante — após o encerramento", f"{N['quando']['depois']}%"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        f"**{N['quando']['antes'] + N['quando']['depois']:.1f}% das divulgações ocorrem "
        "fora do horário de negociação**, em conformidade com a recomendação do artigo "
        "5º da Resolução. A observância é elevada, ainda que não integral.")

    A.secao(doc, "5.2", "O carimbo de hora é informativo", nivel=2)

    A.paragrafo(doc,
        "Antes de empregar a hora recuperada, convém demonstrar que ela carrega "
        "informação. A previsão é direta: se o carimbo for fidedigno e o mercado "
        "reagir racionalmente, a divulgação matinal deve concentrar o movimento no "
        "**mesmo** pregão, e a noturna no **seguinte**.")

    h = N["horario"]["grupos"]
    A.tabela_abnt(doc, "3", "Em que pregão se concentra o movimento",
        ["Momento da divulgação", "Casos", "Volatilidade em D0",
         "Volatilidade em D+1", "Predomina"],
        [
            ["até 09h59", f"{h['antes da abertura (até 09h59)']['n']:,}".replace(",", "."),
             f"{h['antes da abertura (até 09h59)']['D0']:.3f}",
             f"{h['antes da abertura (até 09h59)']['D1']:.3f}", "D0"],
            ["10h00–16h59", f"{h['com o pregão aberto (10h–16h59)']['n']:,}".replace(",", "."),
             f"{h['com o pregão aberto (10h–16h59)']['D0']:.3f}",
             f"{h['com o pregão aberto (10h–16h59)']['D1']:.3f}", "D0"],
            ["17h00 em diante", f"{h['após o fechamento (17h em diante)']['n']:,}".replace(",", "."),
             f"{h['após o fechamento (17h em diante)']['D0']:.3f}",
             f"{h['após o fechamento (17h em diante)']['D1']:.3f}", "D+1"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**O padrão previsto verifica-se integralmente.** A diferença entre o grupo "
        f"matinal e o noturno, medida por $(D_0 - D_{{+1}})$, é de "
        f"{N['horario']['teste_decisivo']['dif']:.3f} "
        f"($t = {N['horario']['teste_decisivo']['t']:.2f}$; "
        f"$p = {N['horario']['teste_decisivo']['p']:.1e}$). **A hora recuperada não é "
        "apenas plausível: ela prediz em qual pregão o mercado responde.**")

    A.paragrafo(doc,
        "Registre-se ainda o grupo intermediário: a divulgação feita **com o pregão "
        f"aberto** produz o maior choque da amostra "
        f"({h['com o pregão aberto (10h–16h59)']['D0']:.3f} em D0), ainda que em "
        f"apenas {h['com o pregão aberto (10h–16h59)']['n']} casos. É o momento em que "
        "o mercado não dispõe de intervalo para assimilar a informação — o que "
        "corrobora, por via empírica, a razão de ser da recomendação do artigo 5º.")

    A.secao(doc, "5.3", "Volatilidade e volume", nivel=2)

    A.tabela_abnt(doc, "4", "Pregão de reação contra pregão sem divulgação",
        ["Medida", "Sem divulgação", "Com divulgação", "Excesso", "valor-p"],
        [
            ["volatilidade (Parkinson)", f"{N['vol']['sem']:.3f}", f"{N['vol']['com']:.3f}",
             f"+{N['vol']['exc']}%", f"{N['vol']['p']:.1e}"],
            ["volume negociado", f"{N['qtd']['sem']:.3f}", f"{N['qtd']['com']:.3f}",
             f"+{N['qtd']['exc']}%", f"{N['qtd']['p']:.1e}"],
            ["salto de abertura", f"{N['gap']['sem']*100:.3f}%", f"{N['gap']['com']*100:.3f}%",
             f"+{(N['gap']['com']-N['gap']['sem'])*100:.2f} p.p.", f"{N['gap']['p']:.1e}"],
            ["retorno do pregão (direção)", f"{N['dir']['sem']*100:.3f}%",
             f"{N['dir']['com']*100:.3f}%", "nulo", f"{N['dir']['p']:.3f}"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "Em termos absolutos: a oscilação diária passa de "
        f"{N['concreto']['oscilacao_dia']['sem']}% para "
        f"{N['concreto']['oscilacao_dia']['com']}%, e o giro de "
        f"{N['concreto']['volume']['sem']} para {N['concreto']['volume']['com']} "
        "milhões de ações.")

    A.paragrafo(doc,
        "**O volume é o sinal mais forte, em magnitude próxima ao dobro do da "
        "volatilidade.** O achado converge com Hashami e Maldonado (2025), que no "
        "mercado de petróleo encontram na contagem de notícias — medida de atenção, "
        "não de conteúdo — o preditor mais robusto.")

    A.paragrafo(doc,
        "A robustez à janela de referência é satisfatória: com base de duas semanas, "
        "de um mês ou com a janela distante convencional, a razão de volatilidade "
        "permanece entre 1,20 e 1,23 para Fatos Relevantes, e a de volume entre 1,42 "
        "e 1,49.")

    A.secao(doc, "5.4", "A ausência de efeito direcional", nivel=2)

    A.paragrafo(doc,
        f"O retorno do pregão de reação não difere do de pregões sem divulgação "
        f"($p = {N['dir']['p']:.3f}$). **O resultado não é falha de desenho: é "
        "consequência lógica da categoria empregada.** O rótulo “Fato Relevante” não "
        "possui sinal — não distingue informação favorável de desfavorável. Havendo "
        "fatos relevantes de ambos os tipos, as altas e as baixas compensam-se na "
        "média.")

    A.paragrafo(doc,
        "O salto de abertura, contudo, apresenta excesso pequeno e significativo "
        f"(+{(N['gap']['com']-N['gap']['sem'])*100:.2f} ponto percentual; "
        f"$p = {N['gap']['p']:.1e}$). **Recomenda-se cautela na interpretação**: o "
        "padrão de salto positivo seguido de correção intradiária está presente "
        "também nos pregões sem divulgação, tratando-se, em boa medida, de "
        "regularidade de microestrutura e não de resposta informacional.")

    A.secao(doc, "5.5", "A distinção legal tem correspondência empírica", nivel=2)

    fc = N["fr_vs_cm"]
    A.tabela_abnt(doc, "5", "Fato Relevante contra Comunicado ao Mercado",
        ["Medida", "Fato Relevante", "Comunicado ao Mercado", "Razão", "valor-p"],
        [
            ["excesso de volatilidade",
             f"+{fc['volatilidade (sacolejo)']['exc_fr_pct']:.1f}%",
             f"+{fc['volatilidade (sacolejo)']['exc_cm_pct']:.1f}%",
             f"{fc['volatilidade (sacolejo)']['razao']:.2f}×",
             f"{fc['volatilidade (sacolejo)']['p']:.1e}"],
            ["excesso de volume",
             f"+{fc['volume negociado']['exc_fr_pct']:.1f}%",
             f"+{fc['volume negociado']['exc_cm_pct']:.1f}%",
             f"{fc['volume negociado']['razao']:.2f}×",
             f"{fc['volume negociado']['p']:.1e}"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**A hierarquia normativa reproduz-se no comportamento do preço.** O que a "
        "norma reserva à categoria de maior peso move a volatilidade "
        f"{fc['volatilidade (sacolejo)']['razao']:.1f} vezes mais e o volume "
        f"{fc['volume negociado']['razao']:.1f} vezes mais.")

    A.paragrafo(doc,
        "**O resultado é tanto mais notável quanto se recorde que o enquadramento é "
        "autodeclarado.** Não há classificação independente separando as duas "
        "categorias; há o julgamento da própria companhia, com incentivos que podem "
        "distorcê-lo em ambas as direções. Que a separação empírica sobreviva a esse "
        "ruído sugere que a diferença real seja superior à medida.")

    A.secao(doc, "5.6", "O achado distributivo", nivel=2)

    A.paragrafo(doc,
        "Os resultados anteriores são médias. A distribuição conta história distinta, "
        "e é ela o achado central do trabalho.")

    dpc = N["dist_por_categoria"]
    A.tabela_abnt(doc, "6", "Distribuição da razão de volatilidade",
        ["", "Fato Relevante", "Comunicado ao Mercado"],
        [
            ["mediana — o caso típico", f"{dpc['Fato Relevante']['mediana']:.3f}",
             f"{dpc['Comunicado ao Mercado']['mediana']:.3f}"],
            ["percentil 75", f"{dpc['Fato Relevante']['p75']:.3f}",
             f"{dpc['Comunicado ao Mercado']['p75']:.3f}"],
            ["percentil 90", f"{dpc['Fato Relevante']['p90']:.3f}",
             f"{dpc['Comunicado ao Mercado']['p90']:.3f}"],
            ["percentil 99", f"{dpc['Fato Relevante']['p99']:.3f}",
             f"{dpc['Comunicado ao Mercado']['p99']:.3f}"],
            ["média", f"{dpc['Fato Relevante']['media']:.3f}",
             f"{dpc['Comunicado ao Mercado']['media']:.3f}"],
            ["proporção sem movimento acima do usual",
             f"{dpc['Fato Relevante']['nao_moveu_pct']}%",
             f"{dpc['Comunicado ao Mercado']['nao_moveu_pct']}%"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        f"**O Fato Relevante mediano produz razão de "
        f"{dpc['Fato Relevante']['mediana']:.3f}** — movimento praticamente "
        f"indistinguível do de uma semana comum. **{dpc['Fato Relevante']['nao_moveu_pct']}% "
        "dos Fatos Relevantes não produzem movimento acima do usual**, proporção que "
        f"sobe a {dpc['Comunicado ao Mercado']['nao_moveu_pct']}% entre os Comunicados "
        f"ao Mercado. No conjunto, **{N['nao_moveu']}% das divulgações não movem o "
        "preço.**")

    A.paragrafo(doc,
        "**O excesso médio de 9,6% não decorre de todos os eventos produzirem pequeno "
        "movimento; decorre de uma minoria produzir movimento grande.** A média e a "
        "mediana afastam-se de maneira característica de distribuição de cauda pesada.")

    # ══ 6 DISCUSSÃO ══════════════════════════════════════════════════════════
    A.secao(doc, "6", "Discussão")

    A.paragrafo(doc,
        "**A presunção legal de relevância é válida em média e falsa na maioria dos "
        "casos individuais.** Essa formulação, aparentemente paradoxal, resume os "
        "resultados. O conjunto dos Fatos Relevantes move volatilidade e volume com "
        "significância inequívoca; o Fato Relevante mediano não move nada.")

    A.paragrafo(doc,
        "A consequência prática é imediata para quem pretenda **usar a divulgação "
        "como sinal**. Um sistema que reaja a todo Fato Relevante estará reagindo, na "
        "maioria das vezes, a ruído. O valor informacional concentra-se numa fração "
        "pequena dos eventos, e identificar essa fração *ex ante* é problema aberto "
        "que este trabalho não resolve.")

    A.paragrafo(doc,
        "A ausência de efeito direcional merece leitura cuidadosa. **Não se conclui "
        "daqui que a informação divulgada seja irrelevante para a direção do preço** — "
        "conclui-se que a *categoria* empregada não a distingue. Separar o Fato "
        "Relevante favorável do desfavorável exige leitura do conteúdo, e é exatamente "
        "o ponto em que este trabalho se abstém deliberadamente, por razões "
        "metodológicas: quisemos medir o efeito da divulgação sem introduzir a "
        "incerteza de um classificador de texto.")

    A.paragrafo(doc,
        "Sobre a validação do critério regulatório, cabe nota de prudência "
        "institucional. **O resultado apoia a hierarquia da norma; não apoia a "
        "conclusão de que cada enquadramento individual esteja correto.** Os dados são "
        "compatíveis tanto com companhias que classificam bem quanto com um regime em "
        "que os erros de enquadramento se cancelam no agregado.")

    # ══ 7 LIMITAÇÕES ═════════════════════════════════════════════════════════
    A.secao(doc, "7", "Limitações")

    A.lista(doc, [
        "**Associação, não causalidade.** O desenho de divulgação noturna aproxima-se "
        "de experimento natural, e o grupo de controle é amplo, mas não há "
        "aleatorização: nenhuma companhia é sorteada para divulgar fato relevante.",
        "**Eventos agrupados.** Em 28,8% das noites há mais de um documento da mesma "
        "companhia, o que impede atribuir o movimento a documento específico. Todos os "
        "testes foram replicados sobre o subconjunto de eventos isolados, sem "
        "alteração qualitativa dos resultados.",
        "**Autodeclaração do enquadramento.** Conforme a Seção 2.1, a categoria é "
        "atribuída pela companhia. O efeito esperado é de atenuação, não de inflação, "
        "do contraste medido.",
        "**Cobertura de papéis.** Quatro companhias ficaram sem série de preços e duas "
        "foram excluídas por fusão posterior, o que retira cerca de 15% dos eventos.",
        "**Conteúdo não examinado.** O trabalho mede o efeito da divulgação, não o de "
        "seu teor. A extensão natural é a leitura do documento íntegro, disponível "
        "mas não explorada aqui.",
    ])

    # ══ 8 CONCLUSÃO ══════════════════════════════════════════════════════════
    A.secao(doc, "8", "Conclusão")

    A.paragrafo(doc,
        f"Recuperou-se a hora oficial de entrega de {N['n_com_hora']:,} comunicados "
        "obrigatórios".replace(",", ".") +
        " à Comissão de Valores Mobiliários, informação ausente do conjunto de dados "
        "abertos da autarquia. O recurso viabiliza desenho de estudo de evento em que "
        "a ordem temporal entre divulgação e negociação é inequívoca, e demonstrou-se "
        "que o carimbo recuperado é informativo: prediz em qual pregão o mercado "
        f"responde ($p = {N['horario']['teste_decisivo']['p']:.0e}$).")

    A.paragrafo(doc,
        f"Sobre {N['n_eventos']:,} eventos de {N['n_papeis']} ações".replace(",", ".") +
        f", a divulgação eleva a volatilidade em {N['vol']['exc']}% e o volume em "
        f"{N['qtd']['exc']}% relativamente a pregões sem divulgação, e **não produz "
        "efeito direcional**. A distinção normativa entre Fato Relevante e Comunicado "
        f"ao Mercado corresponde a diferença empírica de "
        f"{fc['volatilidade (sacolejo)']['razao']:.1f} vezes.")

    A.paragrafo(doc,
        f"**O achado central é distributivo: {N['nao_moveu']}% das divulgações "
        "obrigatórias não produzem movimento acima do usual.** A presunção de "
        "relevância que a norma estabelece sustenta-se no agregado e não se sustenta "
        "no caso típico.")

    # ══ REFERÊNCIAS ══════════════════════════════════════════════════════════
    A.secao(doc, "", "Referências")

    for r in [
        "BODILSEN, S.; LUNDE, A. Exploiting news analytics for volatility forecasting. "
        "*Journal of Applied Econometrics*, v. 40, n. 1, p. 18–36, 2025.",
        "BROWN, S. J.; WARNER, J. B. Using daily stock returns: the case of event "
        "studies. *Journal of Financial Economics*, v. 14, n. 1, p. 3–31, 1985.",
        "COMISSÃO DE VALORES MOBILIÁRIOS. **Resolução CVM nº 44, de 23 de agosto de "
        "2021.** Dispõe sobre a divulgação de informações sobre ato ou fato relevante. "
        "Rio de Janeiro: CVM, 2021.",
        "CORSI, F. A simple approximate long-memory model of realized volatility. "
        "*Journal of Financial Econometrics*, v. 7, n. 2, p. 174–196, 2009.",
        "ENGLE, R. F. Autoregressive conditional heteroscedasticity with estimates of "
        "the variance of United Kingdom inflation. *Econometrica*, v. 50, n. 4, "
        "p. 987–1007, 1982.",
        "FAMA, E. F.; FISHER, L.; JENSEN, M. C.; ROLL, R. The adjustment of stock "
        "prices to new information. *International Economic Review*, v. 10, n. 1, "
        "p. 1–21, 1969.",
        "HALOUSKOVÁ, M.; LYÓCSA, Š. **Forecasting U.S. equity market volatility with "
        "attention and sentiment to the economy.** arXiv:2503.19767, 2025.",
        "HASHAMI, R.; MALDONADO, F. **Can news predict the direction of oil price "
        "volatility? A language model approach with SHAP explanations.** "
        "arXiv:2508.20707, 2025.",
        "MACKINLAY, A. C. Event studies in economics and finance. *Journal of Economic "
        "Literature*, v. 35, n. 1, p. 13–39, 1997.",
        "NGUYEN, T. H.; SHIRAI, K.; VELCIN, J. Sentiment analysis on social media for "
        "stock movement prediction. *Expert Systems with Applications*, v. 42, n. 24, "
        "p. 9603–9611, 2015.",
        "PARKINSON, M. The extreme value method for estimating the variance of the "
        "rate of return. *Journal of Business*, v. 53, n. 1, p. 61–65, 1980.",
        "RUAN, L.; JIANG, H. Stock price prediction using FinBERT-enhanced sentiment "
        "with SHAP explainability and differential privacy. *Mathematics*, v. 13, "
        "n. 17, art. 2747, 2025.",
        "SCHUMAKER, R. P.; CHEN, H. A quantitative stock prediction system based on "
        "financial news. *Information Processing & Management*, v. 45, n. 5, "
        "p. 571–583, 2009.",
    ]:
        A.paragrafo(doc, r, recuo=False)

    A.secao(doc, "", "Nota sobre as referências")

    A.paragrafo(doc,
        "As referências de Bodilsen e Lunde, Halousková e Lyócsa, Hashami e Maldonado, "
        "Nguyen *et al.*, Ruan e Jiang e Schumaker e Chen foram verificadas "
        "diretamente na fonte durante a elaboração deste trabalho. **As referências "
        "canônicas de método — Brown e Warner, Corsi, Engle, Fama *et al.*, MacKinlay "
        "e Parkinson — foram arroladas a partir de conhecimento consolidado e devem "
        "ter volume, número e paginação conferidos antes da submissão.**")

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
