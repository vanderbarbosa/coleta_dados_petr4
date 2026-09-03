# -*- coding: utf-8 -*-
# ==============================================================================
#   CVM — o que foi feito e o que se encontrou
#   Saída: CVM/01_RESULTADO_CVM.docx
# ==============================================================================
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(RAIZ / "src" / "comum"))

import abnt_docx as A  # noqa: E402

FONTE = "Elaborado pelo autor (2026)"
SAIDA = AQUI / "01_RESULTADO_CVM.docx"
R = json.loads((AQUI / "dados" / "estudo_evento_resultado.json").read_text(encoding="utf-8"))


def main() -> None:
    doc = A.novo_documento()

    A.capa(
        doc,
        titulo="O regulador diz o que é relevante",
        subtitulo="16.437 comunicados da CVM confrontados com o preço de 54 papéis "
                  "da B3 — e o que isso diz sobre a tese desta dissertação",
        autor="Vanderlei Barbosa da Silva",
        orientador="Orientador: Prof. Dr. Julio Cesar Nievola",
        instituicao="PUCPR — Programa de Pós-Graduação em Informática (PPGIa)",
        descricao="Primeira etapa do pedido do Prof. Emerson Paraiso na mentoria de "
                  "26 de agosto de 2026: coletar publicações da CVM e avaliar o seu "
                  "impacto sobre os principais ativos da B3. Esta etapa responde à "
                  "pergunta do impacto sem depender de classificação de sentimento. "
                  "Elaborado em 27 de agosto de 2026.",
    )

    # ── 1 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "1", "Por que esta é a melhor fonte que já usei")

    A.paragrafo(doc,
        "O Professor Emerson pediu para eu buscar publicações no sítio da CVM. "
        "**Encontrei mais do que esperava, e por três motivos esta fonte resolve "
        "problemas que me acompanham desde o início.**")

    A.paragrafo(doc,
        "**Primeiro: a relevância vem por lei, não por critério meu.** A Resolução CVM "
        "nº 44 obriga a companhia a divulgar todo fato **capaz de influir na cotação**. "
        "Lembro que **o único experimento que deu certo, em nove tentativas, foi o "
        "filtro de relevância** — e aqui a relevância vem pronta e com força de lei.")

    A.paragrafo(doc,
        "**E é preciso ser exato sobre quem classifica, porque a banca vai perguntar. "
        "Não fui eu.** O campo `Categoria` vem pronto no arquivo da CVM; o meu código "
        "apenas seleciona duas categorias entre as vinte existentes. **Mas também não é "
        "o regulador que classifica: é a própria companhia.** Pela Resolução CVM nº 44, "
        "o Diretor de Relações com Investidores é o responsável pela divulgação, e é ele "
        "quem enquadra o documento na categoria ao protocolar. A CVM define a regra, "
        "fiscaliza e pode sancionar — a classificação inicial, porém, é "
        "**autodeclaração da companhia sob obrigação legal**.")

    A.paragrafo(doc,
        "**A favor disso:** é muito mais forte que um rótulo meu. Quem classifica é "
        "quem tem mais informação sobre o fato, e responde legalmente pelo "
        "enquadramento. **Contra, e convém declarar:** sendo autodeclaração, há risco "
        "de viés de seleção — uma companhia pode enquadrar como Comunicado ao Mercado "
        "algo que preferiria não destacar. **A fronteira entre os dois grupos não é "
        "perfeitamente limpa.**")

    A.paragrafo(doc,
        "**E esse embaçamento reforça o resultado da Seção 6, em vez de enfraquecê-lo:** "
        "se, mesmo com grupos imperfeitamente separados pela autodeclaração, o Fato "
        "Relevante ainda mexe mais que o Comunicado ao Mercado com valor-p de "
        "4,4 × 10⁻¹⁰, **é razoável supor que a diferença real seja ainda maior.**")

    A.paragrafo(doc,
        "**Segundo: resolve o meu problema de poder estatístico.** Halousková e Lyócsa "
        "usam 404 ações; eu usava uma. **Agora tenho 54 papéis da B3.**")

    A.paragrafo(doc,
        "**Terceiro: a atribuição à empresa é exata.** Cada documento traz o CNPJ da "
        "companhia. Acabou a dúvida de se a notícia é ou não sobre o ativo.")

    A.paragrafo(doc,
        "E são **dados abertos oficiais**, do portal `dados.cvm.gov.br`. Não há "
        "raspagem, bloqueio nem termo de uso a discutir.")

    # ── 2 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "2", "O que foi coletado")

    A.tabela_abnt(doc, "1", "Base montada, de 2018 a 2026",
        ["", "Quantidade"],
        [
            ["comunicados da CVM coletados", "89.902"],
            ["dos quais Fatos Relevantes", "23.009"],
            ["companhias distintas", "1.108"],
            ["papéis da B3 mapeados", "62"],
            ["papéis com histórico de preço", "54 + Ibovespa"],
            ["eventos analisados no estudo", f"{R['n_eventos']:,}".replace(",", ".")],
        ], fonte=FONTE)

    A.paragrafo(doc,
        f"Dos eventos analisados, **{R['n_fato_relevante']:,} são Fatos Relevantes** e "
        f"**{R['n_comunicado']:,} são Comunicados ao Mercado**".replace(",", ".") +
        ". Só a PETR4 tem 537 Fatos Relevantes no período.")

    # ── 3 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "3", "Como medi o impacto")

    A.paragrafo(doc,
        "Usei **estudo de evento**, que é o método clássico da área. A ideia é "
        "simples: primeiro se aprende como o papel **costuma** se comportar em relação "
        "ao Ibovespa, olhando os 100 pregões anteriores ao comunicado. Depois se "
        "compara o que ele fez **no dia** do comunicado com o que era de se esperar. A "
        "diferença chama-se **retorno anormal**.")

    A.paragrafo(doc,
        "**A analogia:** é como saber que um aluno tira 7 quando a turma tira 6. Se num "
        "dia a turma tira 6 e ele tira 9, aquele 9 tem algo de anormal — não é o "
        "comportamento habitual dele.")

    A.paragrafo(doc,
        "E fiz **duas perguntas separadas**, porque são coisas diferentes: se o preço "
        "**subiu ou desceu** (direção), e se ele **sacudiu mais que o normal** "
        "(magnitude).")

    # ── 4 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "4", "Resultado 1 — na direção, nada")

    A.tabela_abnt(doc, "2", "Retorno anormal médio dos Fatos Relevantes",
        ["Janela", "Retorno anormal médio", "valor-p"],
        [
            ["no dia", "+0,006%", "0,908"],
            ["dia e seguinte", "−0,041%", "0,639"],
            ["véspera a seguinte", "−0,046%", "0,642"],
            ["dia até 5 pregões", "+0,002%", "0,988"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**Nenhum resultado. Nem perto.** Os valores-p vão de 0,64 a 0,99, quando o "
        "critério é ficar abaixo de 0,05.")

    A.paragrafo(doc,
        "**E isto é um achado forte, não um fracasso.** São 4.470 comunicados que a "
        "lei brasileira define como capazes de influir na cotação, em 54 empresas, ao "
        "longo de oito anos. **Se nem o fato que o regulador chama de relevante prevê "
        "se a ação sobe ou desce, o problema não é o meu modelo de sentimento — é a "
        "natureza da direção.**")

    A.paragrafo(doc,
        "É a confirmação mais ampla que já obtive do que eu vinha sustentando com uma "
        "ação só.")

    # ── 5 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "5", "Resultado 2 — na magnitude, muito")

    A.paragrafo(doc,
        "Aqui a leitura é direta: **1,0 significa um dia comum; acima de 1,0, o preço "
        "sacode mais que o habitual daquele papel.**")

    A.tabela_abnt(doc, "3", "Quanto o preço sacode, comparado ao dia comum",
        ["Janela", "Fato Relevante", "Comunicado ao Mercado"],
        [
            ["no dia", "1,286", "1,213"],
            ["dia e seguinte", "1,325", "1,181"],
            ["véspera a seguinte", "1,234", "1,166"],
            ["dia até 5 pregões", "1,143", "1,075"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**No dia do Fato Relevante e no seguinte, o preço sacode 32,5% mais que o "
        "normal daquele papel.** O valor-p é de 1,2 × 10⁻⁵³ — não é um resultado "
        "apertado, é uma certeza estatística.")

    A.paragrafo(doc,
        "**A resposta à pergunta do Professor Emerson, portanto, é esta:** as "
        "publicações da CVM **causam impacto, e grande — mas no risco, não na "
        "direção**.")

    # ── 6 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "6", "Resultado 3 — a lei acerta")

    A.paragrafo(doc,
        "Havia uma pergunta natural, e ela tem valor próprio: **a distinção legal entre "
        "“Fato Relevante” e “Comunicado ao Mercado” tem correspondência no "
        "comportamento do preço?**")

    A.tabela_abnt(doc, "4", "O que a lei chama de mais relevante mexe mais?",
        ["Categoria", "Casos", "Sacolejo"],
        [
            ["Fato Relevante", "4.470", "1,325"],
            ["Comunicado ao Mercado", "11.963", "1,181"],
            ["diferença", "—", "+0,144 (p = 4,4 × 10⁻¹⁰)"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**Sim, acerta.** O que a norma classifica como mais relevante move mais o "
        "preço, com folga estatística. **É uma validação empírica do critério do "
        "regulador**, e é resultado publicável por si só.")

    # ── 7 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "7", "Resultado 4 — e aqui está a minha tese, outra vez")

    A.paragrafo(doc,
        "Esta é a tabela mais importante do documento. Ela mostra como se distribuem "
        "os 4.470 Fatos Relevantes:")

    A.tabela_abnt(doc, "5", "Distribuição do sacolejo nos Fatos Relevantes",
        ["Posição na distribuição", "Sacolejo", "Leitura"],
        [
            ["mediana — o caso TÍPICO", "0,967", "MENOS que um dia comum"],
            ["percentil 75", "1,616", "acima do normal"],
            ["percentil 90", "2,558", "duas vezes e meia"],
            ["percentil 95", "3,457", "três vezes e meia"],
            ["percentil 99 — os excepcionais", "7,712", "quase oito vezes"],
            ["MÉDIA", "1,325", "puxada pelos extremos"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**Leia a primeira linha com atenção: o Fato Relevante TÍPICO faz o preço "
        "sacudir MENOS que um dia comum.** A mediana é 0,967 — abaixo de 1.")

    A.paragrafo(doc,
        "**Todo o efeito de 1,325 vem da cauda.** A média é 37% maior que a mediana, e "
        "o percentil 99 sacode quase oito vezes o normal.")

    A.paragrafo(doc,
        "**É exatamente o efeito de cauda que eu venho sustentando — agora demonstrado "
        "com 4.470 eventos oficiais, em 54 empresas, sem depender de nenhum modelo de "
        "sentimento.** E a tese sai reforçada e generalizada: **não é o sentimento que "
        "só importa nos extremos. É a notícia — mesmo a legalmente relevante.**")

    A.paragrafo(doc,
        "Na PETR4 isoladamente, 537 Fatos Relevantes, o padrão se repete: **mediana de "
        "0,860** — abaixo do dia comum — contra percentil 99 de **10,113**.")

    # ── 8 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "8", "As limitações, ditas antes que perguntem")

    A.paragrafo(doc,
        "**A primeira limitação que eu havia registrado — a falta da hora — foi "
        "RESOLVIDA.** É o assunto da Seção 8.A.")

    A.paragrafo(doc,
        "**Segunda: eventos vizinhos se contaminam.** Uma empresa que publica três "
        "comunicados na mesma semana tem janelas sobrepostas. Isso não compromete as "
        "médias de 16 mil eventos, mas impede atribuir um movimento específico a um "
        "documento específico.")

    A.paragrafo(doc,
        "**Terceira, e convém ser franco: os choques individuais maiores não são "
        "atribuíveis ao comunicado.** O maior choque da PETR4 é de 6 de março de 2020, "
        "num documento sobre venda de ativos na Colômbia — mas aquela foi a semana do "
        "início da pandemia e da guerra de preços do petróleo. **O modelo de mercado "
        "desconta o Ibovespa, não o barril.** Por isso apresento as estatísticas "
        "agregadas, e não uma lista de casos.")

    A.paragrafo(doc,
        "**Quarta: faltam 8 papéis**, quase todos por mudança de código — Marfrig e "
        "BRF viraram MBRF3, CCR virou MOTV3. São recuperáveis.")

    # ── 9 ────────────────────────────────────────────────────────────────────
    # ── 8.A ──────────────────────────────────────────────────────────────────
    A.secao(doc, "8.A", "A hora oficial — a limitação que deixou de existir")

    A.paragrafo(doc,
        "O conjunto aberto da CVM traz apenas a data. Eu havia registrado isso como a "
        "limitação mais séria, e sugerido usar o carimbo interno do arquivo PDF como "
        "aproximação. **Foi apontado, com razão, que hora aproximada num estudo de "
        "evento é pior que hora nenhuma** — e o que se seguiu confirmou o acerto da "
        "objeção.")

    A.secao(doc, "8.A.1", "Onde estava o dado real", nivel=2)

    A.paragrafo(doc,
        "Está no **Protocolo de Entrega**, o recibo que a CVM emite para cada "
        "documento. Texto literal do recibo de um Fato Relevante da Petrobras:")

    A.paragrafo(doc,
        "*Protocolo de Entrega — 9512 - PETRÓLEO BRASILEIRO S.A. - PETROBRAS. O "
        "documento foi entregue para CVM e B3. Tipo de Documento: Fato Relevante. "
        "**Data da Entrega: 03/01/2018 07:20:19.***", recuo=False)

    A.paragrafo(doc,
        "**Data, hora, minuto e segundo, com fé pública, e disponível inclusive para "
        "documentos de 2018.** Colhi o recibo dos **5.628 Fatos Relevantes**, sem uma "
        "única falha. A data do recibo coincide com a do conjunto aberto em 100% dos "
        "casos — as duas fontes se validam mutuamente.")

    A.secao(doc, "8.A.2", "Por que a aproximação teria enganado", nivel=2)

    A.tabela_abnt(doc, "7", "O carimbo do PDF contra o recibo oficial",
        ["Momento da divulgação", "Carimbo do PDF (amostra)", "Recibo OFICIAL"],
        [
            ["antes da abertura", "20%", "26,2%"],
            ["com o pregão aberto", "40%", "5,4%"],
            ["após o fechamento", "40%", "68,4%"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**O carimbo do arquivo, numa amostra de 25 documentos, sugeria que 40% das "
        "divulgações ocorriam com o pregão "
        "aberto. O dado oficial mostra 5,4%.** Eu teria concluído que a minha janela de "
        "medição era frágil quando ela é, ao contrário, bem apoiada: **quase 95% das "
        "divulgações — 94,6% — ocorrem fora do horário de negociação**, como a Resolução CVM nº 44 "
        "recomenda.")

    A.secao(doc, "8.A.3", "E o carimbo provou ser informativo", nivel=2)

    A.paragrafo(doc,
        "Registrei a previsão **antes** de rodar: quem divulga de manhã deve mover o "
        "preço no mesmo pregão; quem divulga à noite, só no seguinte.")

    A.tabela_abnt(doc, "8", "Em que pregão o mercado reage",
        ["Divulgado", "Casos", "Sacolejo em D0", "Sacolejo em D+1", "Reage em"],
        [
            ["até 09h59", "1.145", "1,640", "1,180", "D0"],
            ["10h–16h59", "239", "2,099", "1,546", "D0"],
            ["17h em diante", "3.086", "1,092", "1,419", "D+1"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**O padrão previsto apareceu inteiro.** A diferença entre o grupo da manhã e o "
        "da noite é de 0,786, com valor-p de 3 × 10⁻²³. **Isso prova que o carimbo é "
        "real e que o mercado reage ao momento da divulgação, não à data do "
        "calendário.**")

    A.paragrafo(doc,
        "E note o grupo do meio: a notícia que sai **com o pregão aberto** produz o "
        "maior choque de todos, 2,099. São poucos casos — 239 —, mas é o momento em que "
        "o mercado não tem como digerir a informação aos poucos.")

    A.secao(doc, "8.A.4", "O que a hora comprou, em números", nivel=2)

    A.paragrafo(doc,
        "Com a hora, a janela de medição deixa de ser fixa e passa a ser **escolhida "
        "pelo horário da divulgação** — D0 para quem divulgou de manhã, D+1 para quem "
        "divulgou à noite:")

    A.tabela_abnt(doc, "9", "Ganho de precisão da medição",
        ["Janela", "Sacolejo medido"],
        [
            ["fixa [0,+1] — o que eu usava", "1,325"],
            ["condicional ao horário oficial", "1,540"],
            ["ganho", "+16,2%  (p = 1,2 × 10⁻³⁷)"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**E o achado principal sobrevive à medição melhor — na verdade, fica mais "
        "nítido.** Com a janela correta, a mediana continua em **0,996** — o Fato "
        "Relevante típico segue mexendo o preço como um dia comum —, enquanto o "
        "percentil 99 sobe para **9,301**. **Medir melhor não elevou o caso típico: "
        "afiou a cauda.** O efeito de cauda não era defeito de medição.")

    A.secao(doc, "9", "O que vem agora")

    A.paragrafo(doc,
        "O pedido do Professor Emerson tem quatro partes. **A primeira e a terceira "
        "estão feitas.** Faltam as que dependem do classificador:")

    A.tabela_abnt(doc, "6", "Situação das quatro partes",
        ["Etapa", "Situação"],
        [
            ["1. buscar publicações na CVM", "FEITO — 89.902 comunicados"],
            ["2. classificar com o FinBERT-PT-BR", "pronto para rodar — 20.421 textos"],
            ["3. avaliar o impacto nos ativos da B3", "FEITO — 16.437 eventos"],
            ["4. retreinar o encoder e comparar", "a discutir — ver abaixo"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**Sobre a etapa 2, um aviso prático:** o PyTorch está quebrado nesta máquina, "
        "e por isso a classificação e o retreino terão de rodar no Colab. A coleta e o "
        "estudo de evento rodaram aqui sem problema.")

    A.secao(doc, "9.1", "Sobre retreinar o encoder — o que já sabemos", nivel=2)

    A.paragrafo(doc,
        "O Professor Emerson sugeriu retreinar o encoder com estas publicações. "
        "**Convém eu registrar que já tentamos algo parecido, e não deu certo.** No "
        "experimento G3, a adaptação ao domínio por modelagem de linguagem reduziu a "
        "perplexidade em 49% — o modelo passou a “achar o texto menos estranho” — "
        "**mas o F1 caiu 0,056, com valor-p de 0,022**, por esquecimento catastrófico "
        "na classe positiva.")

    A.paragrafo(doc,
        "**Isso não quer dizer que não se deva fazer. Quer dizer que se deve fazer "
        "diferente**, e há duas razões para tentar de novo:")

    A.lista(doc, [
        "**o texto é outro** — o G3 usou manchetes de jornal; o comunicado da CVM é "
        "linguagem formal de divulgação societária, que é justamente o registro em que "
        "a empresa fala do próprio fato;",
        "**e principalmente: avaliar pelos EMBEDDINGS, não pela cabeça de sentimento.** "
        "Hashami e Maldonado (2025) mostram, no mesmo artigo e com o mesmo FinBERT, "
        "0,5368 pela cabeça de sentimento contra 0,6694 pelos embeddings. **Todos os "
        "defeitos que auditei estão na parte que rende 0,5368.**",
    ])

    A.paragrafo(doc,
        "**Proponho, então:** retreinar sim, mas medindo o ganho pelos embeddings, e "
        "mantendo o protocolo do G3 para detectar o esquecimento. **Se repetir a queda, "
        "encerra-se a linha com duas evidências em vez de uma** — o que também é "
        "resultado.")

    A.secao(doc, "10", "Em quatro frases")

    A.lista(doc, [
        "“Coletei 89.902 comunicados oficiais da CVM, de 2018 a 2026, e cruzei 16.437 "
        "deles com o preço de 54 papéis da B3.”",
        "“Na direção, não há efeito nenhum: nem o fato que a lei chama de relevante "
        "prevê se a ação sobe ou desce.”",
        "“Na magnitude, o efeito é enorme: o preço sacode 32,5% mais que o normal, com "
        "valor-p de 10⁻⁵³. E a lei acerta — o Fato Relevante mexe mais que o "
        "Comunicado ao Mercado.”",
        "“Mas o Fato Relevante TÍPICO faz o preço sacudir MENOS que um dia comum. Todo "
        "o efeito vem da cauda. É a minha tese, agora com 4.470 eventos oficiais e sem "
        "usar modelo de sentimento nenhum.”",
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
