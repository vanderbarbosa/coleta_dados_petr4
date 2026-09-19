# -*- coding: utf-8 -*-
# ==============================================================================
#   Três propostas de artigo, para os orientadores escolherem
#   Saída: Artigos/00_TRES_PROPOSTAS.docx
# ==============================================================================
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(RAIZ / "src" / "comum"))

import abnt_docx as A  # noqa: E402

FONTE = "Elaborado pelo autor (2026)"
SAIDA = AQUI / "00_TRES_PROPOSTAS.docx"


def main() -> None:
    doc = A.novo_documento()

    A.capa(
        doc,
        titulo="Três artigos possíveis",
        subtitulo="Propostas para o seminário de novembro e a submissão de "
                  "dezembro — com o que já está pronto, o que falta, e uma "
                  "avaliação franca de prazo",
        autor="Vanderlei Barbosa da Silva",
        orientador="Orientador: Prof. Dr. Julio Cesar Nievola",
        instituicao="PUCPR — Programa de Pós-Graduação em Informática (PPGIa)",
        descricao="Documento para decisão dos orientadores. Apresenta três artigos "
                  "com perguntas de pesquisa distintas, literaturas distintas e "
                  "públicos distintos, construídos sobre resultados já obtidos. "
                  "Elaborado em 19 de setembro de 2026.",
    )

    # ── 0 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "1", "Antes das propostas: o prazo")

    A.paragrafo(doc,
        "Hoje é 19 de setembro. O seminário é em novembro e a submissão em "
        "dezembro. **São dez semanas, e nesse mesmo período preciso fechar a "
        "dissertação.**")

    A.paragrafo(doc,
        "**Três artigos terminados nesse prazo não é realista, e prefiro dizer isso "
        "agora.** O que considero alcançável, e já é bastante:")

    A.lista(doc, [
        "**um artigo pronto para submeter** — texto final, revisado, formatado para o "
        "veículo;",
        "**dois em rascunho avançado** — estrutura completa, resultados prontos, "
        "faltando revisão fina e adequação ao veículo.",
    ])

    A.paragrafo(doc,
        "Os senhores escolhem qual vai primeiro. Os outros dois ficam engatilhados "
        "para o início de 2027, quando a dissertação já estiver defendida e houver "
        "fôlego para a revisão por pares.")

    A.paragrafo(doc,
        "**Uma observação de método sobre a escolha:** os três artigos abaixo foram "
        "pensados para **não serem fatias do mesmo estudo**. Perguntas diferentes, "
        "literaturas diferentes, públicos diferentes. Publicar três recortes de um "
        "mesmo trabalho é prática que os avaliadores reconhecem e punem — e "
        "enfraqueceria a própria dissertação.")

    # ── ARTIGO 1 ─────────────────────────────────────────────────────────────
    A.secao(doc, "2", "Artigo 1 — O relógio da CVM")

    A.paragrafo(doc,
        "**Título de trabalho:** *Fato relevante move preço? Evidência de 11.161 "
        "comunicados da CVM com carimbo oficial de hora*", recuo=False)

    A.secao(doc, "2.1", "A pergunta", nivel=2)

    A.paragrafo(doc,
        "A Resolução CVM nº 44 obriga a companhia a divulgar todo fato **capaz de "
        "influir na cotação**. A pergunta empírica é simples e nunca foi respondida "
        "com este rigor no mercado brasileiro: **esses fatos influem mesmo?**")

    A.secao(doc, "2.2", "A contribuição — o que ninguém tem", nivel=2)

    A.paragrafo(doc,
        "**O conjunto aberto da CVM traz apenas a DATA de entrega, sem hora.** Sem a "
        "hora, não se sabe se o documento saiu com o mercado aberto ou fechado — e "
        "sem isso não há como afirmar o que veio antes, a notícia ou o movimento.")

    A.paragrafo(doc,
        "**Recuperamos a hora oficial de 20.419 documentos**, com precisão de "
        "segundos, a partir do Protocolo de Entrega — o recibo que a própria CVM "
        "emite. **É um ativo de dados que não existe publicamente**, e é ele que "
        "viabiliza o desenho do artigo.")

    A.secao(doc, "2.3", "Os achados", nivel=2)

    A.tabela_abnt(doc, "1", "O que já está medido e testado",
        ["Achado", "Número", "Significância"],
        [
            ["divulgação fora do horário de pregão", "94,6%", "descritivo"],
            ["o mercado reage em D0 se a divulgação foi de manhã, em D+1 se foi de "
             "noite", "diferença de 0,79", "p = 3 × 10⁻²³"],
            ["volatilidade acima do controle", "+9,6%", "p = 7 × 10⁻⁵⁵"],
            ["volume acima do controle", "+16,5%", "p = 4 × 10⁻⁶²"],
            ["Fato Relevante contra Comunicado ao Mercado", "2,6 vezes mais",
             "p = 7 × 10⁻¹⁸"],
            ["comunicados que NÃO movem o preço", "59,0%", "descritivo"],
            ["retorno anormal médio (direção)", "nulo", "p = 0,89"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**A tese do artigo:** o fato relevante move o **risco**, não a **direção**. "
        "E move de forma **concentrada** — a maioria dos comunicados não produz "
        "movimento algum; o efeito médio vem de uma minoria.")

    A.paragrafo(doc,
        "**O resultado que mais deve interessar a um avaliador brasileiro:** a "
        "distinção legal entre as duas categorias tem correspondência empírica. O que "
        "a norma chama de mais relevante mexe **2,6 vezes mais**. É validação do "
        "critério do regulador, e é resultado publicável por si só.")

    A.secao(doc, "2.4", "Onde submeter", nivel=2)

    A.tabela_abnt(doc, "2", "Veículos, em ordem de preferência",
        ["Veículo", "Formato", "Por quê"],
        [
            ["Finance Research Letters", "artigo curto, ~3.000 palavras",
             "feito para um achado limpo; revisão rápida; indexado"],
            ["Revista Brasileira de Finanças", "completo, português",
             "público que conhece a CVM; fluxo contínuo"],
            ["Revista Contabilidade & Finanças (USP)", "completo",
             "estrato alto; o tema de divulgação societária é do escopo"],
            ["Emerging Markets Review", "completo, inglês",
             "se optarem por internacional com mais fôlego"],
        ], fonte=FONTE)

    A.secao(doc, "2.5", "Estado e risco", nivel=2)

    A.paragrafo(doc,
        "**Pronto: cerca de 80%.** Todos os resultados estão calculados, testados e "
        "com grupo de controle. **Falta escrever** e montar a revisão de literatura.")

    A.paragrafo(doc,
        "**Risco baixo.** Não depende de aprendizado de máquina nenhum — é finanças "
        "empírica com dado novo, amostra grande e controle bem construído. Um "
        "avaliador de finanças tem pouco por onde atacar o método.")

    A.paragrafo(doc,
        "**É a minha recomendação para ser o primeiro.**")

    # ── ARTIGO 2 ─────────────────────────────────────────────────────────────
    A.secao(doc, "3", "Artigo 2 — A auditoria do classificador")

    A.paragrafo(doc,
        "**Título de trabalho:** *O que um classificador de sentimento financeiro em "
        "português não enxerga: auditoria do FinBERT-PT-BR contra pareceres de casas "
        "de análise*", recuo=False)

    A.secao(doc, "3.1", "A pergunta", nivel=2)

    A.paragrafo(doc,
        "O FinBERT-PT-BR é **o** modelo de sentimento financeiro em português. É "
        "usado como componente por muita gente, e quase sempre sem auditoria. "
        "**Ele faz o que se espera dele?**")

    A.secao(doc, "3.2", "A contribuição", nivel=2)

    A.paragrafo(doc,
        "Uma auditoria sistemática, com **referência externa independente**: 224 "
        "notícias em que **trinta casas de análise** declararam publicamente se o "
        "fato era favorável ou desfavorável à companhia. O gabarito não é nosso — é "
        "de profissionais que respondem pelo que assinam.")

    A.secao(doc, "3.3", "Os achados", nivel=2)

    A.lista(doc, [
        "**Viés estrutural contra a classe positiva:** 48,5% do corpus é rotulado "
        "negativo e **não existe um único pregão, em oito anos, com maioria de "
        "notícias positivas**.",
        "**Contra o gabarito profissional:** o modelo enxerga 21,9% de positivas onde "
        "as casas de análise enxergam 84,8%. Concordância de 29,0%, com kappa de "
        "0,075 — praticamente o acaso.",
        "**Um defeito de configuração que corrompe qualquer uso padrão:** o "
        "`problem_type` declarado faz a biblioteca aplicar sigmoide em vez de "
        "softmax. O rótulo sai certo, o escore de confiança sai em escala errada — e "
        "quem usa a pipeline padrão não percebe.",
        "**O modelo é *cased* e quebra com caixa alta:** 21.619 manchetes do corpus "
        "estão inteiramente em maiúsculas.",
        "**Nove tentativas de melhoria, oito fracassaram.** Só o filtro de relevância "
        "funcionou. Mexer no corpus funciona; mexer no modelo, não.",
        "**Em texto regulatório o problema muda de forma:** nos 20.419 comunicados da "
        "CVM, 79,2% saem neutros.",
    ])

    A.paragrafo(doc,
        "**A recomendação que fecha o artigo** vem ancorada em evidência externa "
        "controlada: Hashami e Maldonado (2025) mostram que o **mesmo** FinBERT rende "
        "0,5368 quando usado como classificador de sentimento e **0,6694** quando "
        "usado como extrator de *embeddings*. **Todos os defeitos que auditamos estão "
        "na cabeça de sentimento; nenhum está nos embeddings.**")

    A.secao(doc, "3.4", "Onde submeter", nivel=2)

    A.tabela_abnt(doc, "3", "Veículos",
        ["Veículo", "Por quê"],
        [
            ["PROPOR — Computational Processing of Portuguese",
             "o público exato; artefato em português sob escrutínio"],
            ["STIL — Symposium in Information and Human Language Technology",
             "comunidade brasileira de PLN"],
            ["BRACIS", "abrangente, aceita trabalho crítico e de reprodutibilidade"],
            ["LREC", "se o foco for o recurso e o gabarito construído"],
        ], fonte=FONTE)

    A.secao(doc, "3.5", "Estado e risco", nivel=2)

    A.paragrafo(doc,
        "**Pronto: cerca de 70%.** Todas as análises existem. **Falta uma coisa "
        "concreta e inadiável: auditar à mão os 224 pareceres.** A planilha está "
        "montada com as colunas em branco; é trabalho de umas duas horas, e sem ele o "
        "número principal do artigo fica preliminar.")

    A.paragrafo(doc,
        "**Risco médio, e é preciso ser franco sobre ele.** É um artigo de resultado "
        "negativo, e resultado negativo custa mais a publicar. **Mas é exatamente o "
        "tipo de trabalho que a comunidade reclama que falta**, e a auditoria vem com "
        "gabarito profissional independente — o que a coloca acima da crítica de ser "
        "apenas opinião do autor.")

    A.paragrafo(doc,
        "**Cuidado editorial:** o artigo precisa ser escrito sem tom de ataque ao "
        "trabalho de Santos, Bianchi e Costa (2023). O enquadramento correto é o de "
        "**estudo de limites de aplicabilidade** — o modelo deles foi treinado para "
        "uma tarefa e está sendo cobrado por outra.")

    # ── ARTIGO 3 ─────────────────────────────────────────────────────────────
    A.secao(doc, "4", "Artigo 3 — As armadilhas da medição")

    A.paragrafo(doc,
        "**Título de trabalho:** *Quatro armadilhas de medição em estudos de evento "
        "com dados textuais, e como corrigi-las*", recuo=False)

    A.secao(doc, "4.1", "A pergunta", nivel=2)

    A.paragrafo(doc,
        "Este artigo nasceu de erros que **eu mesmo cometi e corrigi** ao longo desta "
        "pesquisa. Cada um deles inverteria ou inflaria uma conclusão, e nenhum é "
        "óbvio. A pergunta: **quanto a escolha de medida muda o resultado publicado?**")

    A.secao(doc, "4.2", "As quatro armadilhas, com o efeito quantificado", nivel=2)

    A.tabela_abnt(doc, "4", "Cada armadilha, o erro que produz e a correção",
        ["Armadilha", "O que acontece", "Efeito no resultado"],
        [
            ["O piso da razão não é 1,00",
             "a razão entre o dia e a média da semana anterior já vale 1,031 sem "
             "evento algum, por assimetria da distribuição",
             "anunciaríamos +21,9% em vez de +9,6%"],
            ["A regra ingênua vira constante",
             "com classificador enviesado, somar o sentimento da noite prevê a mesma "
             "classe em 99,0% dos dias",
             "acurácia de 47,8% — abaixo do acaso; a correção leva a 53,8%"],
            ["A composição da amostra infla o efeito bruto",
             "as empresas que publicam já são as mais negociadas; a semana ANTERIOR "
             "ao comunicado já tem volume 53% acima do normal",
             "volume anunciaria +71,8% em vez de +16,5%"],
            ["Eventos agrupados não são atribuíveis",
             "28,8% das noites têm mais de um comunicado da mesma empresa",
             "o movimento não pode ser creditado a um documento específico"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**O que torna o artigo publicável não é apontar as armadilhas — é "
        "quantificá-las.** Cada linha da tabela tem o número errado e o número certo, "
        "medidos sobre a mesma base de 11.161 eventos e 105.896 pregões de controle.")

    A.secao(doc, "4.3", "Onde submeter", nivel=2)

    A.paragrafo(doc,
        "É um artigo de método, e o gênero natural é a **nota de pesquisa**. "
        "Candidatos: *Finance Research Letters* (que publica notas metodológicas), "
        "*Journal of Empirical Finance*, ou um veículo brasileiro de métodos "
        "quantitativos.")

    A.secao(doc, "4.4", "Estado e risco", nivel=2)

    A.paragrafo(doc,
        "**Pronto: cerca de 85% — é o mais barato de escrever.** Todas as análises "
        "existem, porque cada armadilha foi descoberta e corrigida no curso do "
        "trabalho.")

    A.paragrafo(doc,
        "**Risco baixo, ambição modesta.** Nota metodológica não é artigo de grande "
        "impacto. **Mas tem uma virtude estratégica:** publicado antes ou junto com o "
        "Artigo 1, ele demonstra domínio de método e torna o outro mais difícil de "
        "atacar.")

    A.paragrafo(doc,
        "**Alternativa para esta terceira vaga**, caso os senhores prefiram algo mais "
        "ambicioso: o **confronto entre fontes textuais** — notícia de portal contra "
        "comunicado oficial. A pergunta é nova e o achado é interessante (o comunicado "
        "da CVM não prevê direção pelo texto, mas indica em qual noite vale a pena ler "
        "o jornal). **O problema é que o resultado está no limite da significância** "
        "(p = 0,041) e apoiado em 402 noites. É a opção de maior retorno e maior "
        "risco.")

    # ── 5 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "5", "Como os três se separam")

    A.tabela_abnt(doc, "5", "Nenhum é fatia do outro",
        ["", "Artigo 1", "Artigo 2", "Artigo 3"],
        [
            ["Pergunta", "o fato relevante move o preço?",
             "o classificador faz o que promete?", "a medida muda a conclusão?"],
            ["Campo", "finanças empírica", "processamento de linguagem",
             "método quantitativo"],
            ["Dado central", "hora oficial da CVM", "224 pareceres de analistas",
             "as mesmas bases, medidas de dois jeitos"],
            ["Usa aprendizado de máquina?", "NÃO", "é o objeto", "não centralmente"],
            ["Público", "economista, regulador, gestor", "pesquisador de PLN",
             "quem faz estudo de evento"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**O Artigo 1 não depende do classificador** — é a sua maior virtude. Se a "
        "crítica ao FinBERT-PT-BR (Artigo 2) estiver certa, o Artigo 1 continua de pé, "
        "porque ele nunca usou sentimento. **Os dois se sustentam separadamente.**")

    # ── 6 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "6", "O que recomendo")

    A.lista(doc, [
        "**Escrever o Artigo 1 primeiro e submetê-lo em dezembro.** É o mais completo, "
        "o de menor risco, e o único que traz um ativo de dados inédito.",
        "**Levar o Artigo 3 a rascunho avançado em paralelo** — é barato, porque as "
        "análises já existem, e fortalece o Artigo 1.",
        "**Deixar o Artigo 2 para janeiro**, e usar dezembro para a única coisa que "
        "ele ainda exige: a auditoria manual dos 224 pareceres.",
        "**Apresentar os três no seminário de novembro** como o programa de publicação "
        "da pesquisa, e não como três promessas para dezembro.",
    ])

    A.paragrafo(doc,
        "**E uma sugestão sobre o seminário:** o painel interativo que construímos "
        "mostra um fato relevante real e o que aconteceu com o preço, passo a passo. "
        "**Vale abri-lo na apresentação** — comunica em trinta segundos o que uma "
        "tabela leva cinco minutos para explicar.")

    A.secao(doc, "7", "O que preciso dos senhores para começar")

    A.lista(doc, [
        "**Qual artigo vai primeiro** — a minha recomendação é o 1, mas a decisão é "
        "dos senhores.",
        "**Português ou inglês** — muda o veículo e o esforço. O Artigo 1 em inglês "
        "abre *Finance Research Letters*; em português, as revistas nacionais.",
        "**Coautoria** — quem assina, em que ordem, e se algum dos senhores quer "
        "conduzir a interlocução com o veículo.",
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
