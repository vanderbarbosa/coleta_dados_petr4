# -*- coding: utf-8 -*-
# ==============================================================================
#   Resultado do E2 — o que levar à mentoria
#   Saída: Rotulagem_Especialistas/02_RESULTADO_PARA_A_MENTORIA.docx
# ==============================================================================
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(RAIZ / "src" / "comum"))

import abnt_docx as A  # noqa: E402

FONTE = "Elaborado pelo autor (2026)"
SAIDA = AQUI / "02_RESULTADO_PARA_A_MENTORIA.docx"
R = json.loads((AQUI / "_v2_resultado.json").read_text(encoding="utf-8"))


def main() -> None:
    doc = A.novo_documento()

    A.capa(
        doc,
        titulo="Os especialistas já rotularam",
        subtitulo="224 notícias em que uma casa de análise declarou publicamente se o "
                  "fato era bom ou ruim para a Petrobras — e o que o nosso modelo "
                  "disse das mesmas notícias",
        autor="Vanderlei Barbosa da Silva",
        orientador="Orientador: Prof. Dr. Julio Cesar Nievola",
        instituicao="PUCPR — Programa de Pós-Graduação em Informática (PPGIa)",
        descricao="Resposta ao pedido dos Profs. Emerson Paraiso e Julio Nievola de "
                  "obter rótulos por via distinta da rotulagem manual. Resultado "
                  "preliminar, pendente de auditoria manual da planilha que acompanha "
                  "este documento. Elaborado em 26 de agosto de 2026.",
    )

    # ── 1 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "1", "O que foi feito, em um parágrafo")

    A.paragrafo(doc,
        "Os senhores pediram para eu procurar especialistas que publiquem se a notícia "
        "é boa ou ruim para a Petrobras. **Antes de sair coletando na internet, fui "
        "olhar o nosso próprio corpus — e eles já estavam lá.** Casas de análise "
        "publicam o parecer, e a imprensa reproduz na própria manchete. O exemplo "
        "abaixo é literal, do nosso corpus:")

    A.paragrafo(doc,
        "*“Guide: reajuste do preço do GLP é positivo para a Petrobras”* — Money Times, "
        "4 de junho de 2020.", recuo=False)

    A.paragrafo(doc,
        "**Extraí 224 casos como esse, de 30 casas de análise diferentes, entre 2018 e "
        "2025.** E comparei o parecer de cada especialista com o rótulo que o nosso "
        "FinBERT-PT-BR deu à mesma notícia.")

    # ── 2 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "2", "O conjunto obtido")

    A.tabela_abnt(doc, "1", "Como se chegou aos 224 casos",
        ["Etapa", "Notícias"],
        [
            ["corpus completo", f"{R['corpus']:,}".replace(",", ".")],
            ["Petrobras mencionada NO TÍTULO", f"{R['petrobras_no_titulo']:,}".replace(",", ".")],
            ["... e uma casa de análise citada", f"{R['com_casa_de_analise']:,}".replace(",", ".")],
            ["... com veredicto explícito e sem ambiguidade", str(R['conjunto_limpo'])],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**Composição:** 30 casas distintas — BTG (25 casos), XP (22), Itaú BBA (15), "
        "Credit Suisse (11), UBS (11), Bradesco BBI (9), Santander (9), JPMorgan (7), "
        "Bank of America (6), Safra (5), além de Fitch, Moody's e S&P. Fontes: Money "
        "Times (133), InfoMoney (69), Exame (19), Poder360 (3). **Distribuição "
        "equilibrada entre 2018 e 2025**, de 14 a 35 casos por ano.")

    # ── 3 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "3", "O resultado")

    A.paragrafo(doc,
        "**O nosso modelo concorda com o especialista em 29,0% dos casos.** O kappa de "
        "Cohen é de **0,075** — uma medida que vale 0 quando a concordância é a que se "
        "esperaria do puro acaso, e 1 quando é perfeita. **Estamos praticamente no "
        "acaso.**")

    A.paragrafo(doc, "**Mas o número global esconde o essencial. Veja por classe:**")

    A.tabela_abnt(doc, "2", "Concordância, separada pelo que o especialista disse",
        ["O especialista disse", "Casos", "O nosso modelo concordou"],
        [
            ["POSITIVO", "190", "24,2%"],
            ["NEGATIVO", "27", "63,0%"],
            ["NEUTRO", "7", "28,6%"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**Quando o especialista diz que a notícia é RUIM, nós concordamos em quase "
        "dois terços das vezes. Quando ele diz que é BOA, concordamos em um quarto.**")

    A.secao(doc, "3.1", "Para onde vão os positivos que perdemos", nivel=2)

    A.tabela_abnt(doc, "3", "Das 190 notícias que o especialista chamou de positivas",
        ["O nosso modelo classificou como", "Quantas"],
        [
            ["Neutro", "106"],
            ["Positivo (acerto)", "46"],
            ["Negativo", "38"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**O modelo não chama de negativo o que é positivo — ele se cala.** Manda mais "
        "da metade para “neutro”. E em 38 casos inverte o sinal por completo.")

    A.secao(doc, "3.2", "As mesmas notícias, vistas pelos dois", nivel=2)

    A.tabela_abnt(doc, "4", "Distribuição sobre exatamente o mesmo conjunto",
        ["", "Positivo", "Neutro", "Negativo"],
        [
            ["Especialistas humanos", "84,8%", "3,1%", "12,1%"],
            ["FinBERT-PT-BR", "21,9%", "52,7%", "25,4%"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**Esta é a tabela que resume tudo.** Diante das mesmas 224 notícias, analistas "
        "profissionais enxergam 84,8% como favoráveis à Petrobras. O nosso modelo "
        "enxerga 21,9%.")

    A.paragrafo(doc,
        "**E isto confirma, com referência externa e profissional, o que a auditoria "
        "interna já apontava:** o modelo tem viés contra a classe positiva. Nós já "
        "sabíamos que ele rotula 48,5% de tudo como negativo e que **não existe um "
        "único pregão, em oito anos, com maioria de notícias positivas**. **Agora "
        "temos quem contradiga isso: trinta casas de análise.**")

    # ── 4 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "4", "As ressalvas — e são sérias")

    A.paragrafo(doc,
        "**Este número é preliminar. Não deve ser citado como resultado final antes da "
        "auditoria manual.** Digo isso porque a primeira versão do meu extrator "
        "produziu 488 casos, e ao conferir à mão encontrei erros graves:")

    A.lista(doc, [
        "*“XP atualiza Top Picks com Metal Leve **no lugar de** Petrobras”* — é "
        "**remoção** da carteira, e eu havia marcado como positivo;",
        "*“Santander **tira** Petrobras da carteira e recomenda 8 ações para comprar”* "
        "— mesma inversão;",
        "*“Credit Suisse tem aposta acima da média para **BR Distribuidora**”* — o "
        "parecer nem era sobre a Petrobras.",
    ])

    A.paragrafo(doc,
        "**Corrigi as três falhas** exigindo que a Petrobras esteja no título, que o "
        "veredicto esteja a menos de 110 caracteres da menção a ela, e descartando "
        "casos com verbo de remoção ou ressalva do tipo “mas não”. **E o resultado mal "
        "se moveu:**")

    A.tabela_abnt(doc, "5", "O achado é estável às correções",
        ["Versão", "Casos", "Concordância"],
        [
            ["v1 — sem controle", "488", "26,8%"],
            ["v2 — com proximidade e remoção", "233", "29,6%"],
            ["v2 — mais o descarte de matérias-resumo", "224", "29,0%"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**Ainda assim, restam três ressalvas que peço para registrar:**")

    A.paragrafo(doc,
        "**Primeira — a amostra é enviesada para o positivo, e em parte isso é real.** "
        "84,8% de pareceres favoráveis não descreve o noticiário; descreve o que as "
        "casas de análise publicam. É fato conhecido em finanças que a análise de "
        "venda — a *sell-side* — é estruturalmente otimista. **Portanto este conjunto "
        "não serve para estimar a proporção de notícias boas e más no mundo.** Serve "
        "para o que se propõe: verificar se o nosso modelo reconhece um positivo quando "
        "um profissional declara um.")

    A.paragrafo(doc,
        "**Segunda, e é a mais importante conceitualmente — não estamos medindo "
        "exatamente a mesma coisa.** O especialista diz *“isso é bom para a ação”*, que "
        "é um juízo de investimento. O FinBERT diz *“este texto tem tom positivo”*, que "
        "é um juízo linguístico. São parentes, não gêmeos. Uma manchete como *“XP eleva "
        "preço-alvo da Petrobras”* é factual no tom e favorável no juízo.")

    A.paragrafo(doc,
        "**Mas repare que essa ressalva, longe de enfraquecer o achado, é o achado.** "
        "Se o que move o preço é o juízo de investimento, e o nosso artefato mede tom "
        "linguístico, **então ele está medindo a coisa errada** — e isso explica, de uma "
        "vez, por que nove tentativas de melhorar o classificador falharam.")

    A.paragrafo(doc,
        "**Terceira — resta erro de extração.** Estimo algo entre 5% e 15%, concentrado "
        "em manchetes que citam várias empresas. **Por isso a planilha de auditoria "
        "acompanha este documento, com duas colunas em branco para conferência.**")

    # ── 5 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "5", "O que isto resolve, e o que não resolve")

    A.tabela_abnt(doc, "6", "Situação",
        ["Pergunta", "Resposta"],
        [
            ["Existem especialistas que rotulam notícia da Petrobras?",
             "SIM — 224 casos, 30 casas, 8 anos"],
            ["Dá para usar como gabarito?",
             "SIM, após auditoria manual da planilha"],
            ["O nosso modelo concorda com eles?",
             "NÃO — 29,0%, kappa 0,075"],
            ["Onde está a falha?",
             "na classe POSITIVA: 24,2% de concordância, contra 63,0% na negativa"],
            ["Isso valida a previsão de preço?",
             "NÃO — é outro experimento (o E1 do protocolo), ainda por fazer"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**O que não fiz, e explico por quê:** não usei o preço para conferir se o "
        "parecer do especialista se confirmou. Isso é a segunda metade do pedido dos "
        "senhores, e é um experimento separado — o E1 do protocolo. **Misturar os dois "
        "seria erro:** se o especialista diz “notícia ruim” e a ação sobe, isso não "
        "torna o rótulo errado; apenas mostra que naquele pregão outra coisa pesou "
        "mais. E nós já demonstramos que é isso o que ocorre na maioria dos dias.")

    # ── 6 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "6", "O que peço e o que proponho")

    A.lista(doc, [
        "**Auditar a planilha** `_v2_para_auditoria.csv` — 224 linhas, duas colunas em "
        "branco. Uma hora de trabalho fecha o número.",
        "**Rodar o E1** — confrontar as previsões dos analistas com o preço observado. "
        "É a outra metade do pedido, e responde de frente à crítica de que 54,5% é "
        "pouco.",
        "**Reprocessar o corpus com os embeddings**, e não com a cabeça de sentimento. "
        "Hashami e Maldonado (2025) mostram, no mesmo artigo e com o mesmo FinBERT, "
        "0,5368 pela cabeça de sentimento contra 0,6694 pelos embeddings. **Este "
        "experimento indica onde está o nosso 0,5368.**",
    ])

    A.secao(doc, "7", "Em três frases, se o tempo for curto")

    A.lista(doc, [
        "“Achei 224 notícias em que uma casa de análise disse publicamente se o fato "
        "era bom ou ruim para a Petrobras — de trinta casas, ao longo de oito anos. E "
        "elas já estavam dentro do meu corpus.”",
        "“O meu modelo concorda com esses profissionais em 29% dos casos. Quando eles "
        "dizem que a notícia é ruim, concordo em 63%. Quando dizem que é boa, em 24%.”",
        "“Nas mesmas notícias, os analistas veem 84,8% de positivas e o meu modelo vê "
        "21,9%. É a confirmação externa do viés que eu já suspeitava — e explica por "
        "que nove tentativas de consertar o classificador não deram em nada.”",
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
