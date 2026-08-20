# -*- coding: utf-8 -*-
# ==============================================================================
#   O que as pesquisas da área estão buscando e o que conseguiram
#   Saída: Mentoria_Emerson_13082026/04_O_QUE_O_CAMPO_BUSCA.docx
#
#   Público: leitor sem formação em aprendizado de máquina.
# ==============================================================================
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(RAIZ / "src" / "comum"))

import abnt_docx as A  # noqa: E402

FONTE = "Elaborado pelo autor (2026)"
SAIDA = AQUI / "04_O_QUE_O_CAMPO_BUSCA.docx"


def main() -> None:
    doc = A.novo_documento()

    A.capa(
        doc,
        titulo="O que essas pesquisas querem, e o que conseguiram",
        subtitulo="Sete perguntas que a área tenta responder — e onde a minha "
                  "pesquisa se encaixa",
        autor="Vanderlei Barbosa da Silva",
        orientador="Orientador: Prof. Dr. Julio Cesar Nievola",
        instituicao="PUCPR — Programa de Pós-Graduação em Informática (PPGIa)",
        descricao="Documento escrito para ser entendido sem conhecimento prévio de "
                  "aprendizado de máquina. Organiza as 25 pesquisas levantadas não por "
                  "autor, e sim pela PERGUNTA que cada uma tenta responder. "
                  "Elaborado em 20 de agosto de 2026.",
    )

    # ── 1 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "1", "Uma correção, antes de tudo")

    A.paragrafo(doc,
        "Em conversa anterior eu disse que **“quase ninguém tenta prever a direção”**. "
        "**Isso está errado, e preciso desfazer.**")

    A.paragrafo(doc,
        "Prever a direção do preço é, de longe, **o assunto mais concorrido da área "
        "inteira**. A maior parte das pesquisas que li faz exatamente isso. E prever "
        "volatilidade também é campo consolidado, com trabalhos em revistas de "
        "primeira linha.")

    A.paragrafo(doc,
        "**O que é raro não é o alvo — é a combinação.** Poucos trabalhos fazem, ao "
        "mesmo tempo, as quatro coisas que eu faço:")

    A.lista(doc, [
        "prever **direção E volatilidade** no mesmo trabalho (a maioria escolhe uma);",
        "sobre **uma ação individual** (a maioria usa índices ou carteiras de centenas "
        "de papéis);",
        "em **português**, no mercado brasileiro;",
        "com **teste consultado uma única vez** e relato dos resultados negativos.",
    ])

    A.paragrafo(doc,
        "**É a combinação que é rara, não a pergunta.** E convém eu dizer isso com "
        "essas palavras, porque afirmar que “ninguém faz o que eu faço” é o tipo de "
        "frase que a banca derruba com um contraexemplo.")

    # ── 2 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "2", "As sete perguntas que a área tenta responder")

    A.paragrafo(doc,
        "Reorganizei as vinte e cinco pesquisas não por autor, mas pela **pergunta** "
        "que cada uma persegue. Ficam sete grupos.")

    A.secao(doc, "2.1", "Pergunta 1 — “O humor da multidão prevê a bolsa?”", nivel=2)

    A.paragrafo(doc,
        "**Quem faz:** Bollen e colegas (2011), com quase 10 milhões de mensagens do "
        "Twitter.")

    A.paragrafo(doc,
        "**O que queriam:** mostrar que o estado de ânimo coletivo, medido em redes "
        "sociais, antecipa o movimento da bolsa. É a versão mais ambiciosa da ideia.")

    A.paragrafo(doc,
        "**O que conseguiram:** anunciaram 86,7% de acerto e o trabalho virou o mais "
        "citado da área. **Mas não se sustentou.** Em 2017 outros pesquisadores "
        "refizeram a análise com mais dados e não encontraram nada. O acerto era sobre "
        "**15 dias**.")

    A.paragrafo(doc,
        "**O que sobrou de útil:** eles mediram **sete dimensões de humor**, não só "
        "“bom ou ruim”. E só uma — a calma — teve poder preditivo. **Positivo/negativo "
        "não teve.** Isso é uma pista real.")

    A.secao(doc, "2.2", "Pergunta 2 — “Dá para ler a notícia e operar em minutos?”",
            nivel=2)

    A.paragrafo(doc,
        "**Quem faz:** Schumaker e Chen (2009), com o sistema AZFinText.")

    A.paragrafo(doc,
        "**O que queriam:** capturar a reação do mercado **logo depois** que a notícia "
        "sai — questão de minutos, não de dias.")

    A.paragrafo(doc,
        "**O que conseguiram:** 71,2% de acerto na direção do preço **vinte minutos** "
        "após a publicação. É um resultado real, num problema real — só que é um "
        "problema **diferente do meu**. Eles medem a reação; eu tento antecipar o "
        "pregão seguinte.")

    A.secao(doc, "2.3", "Pergunta 3 — “Como construir uma máquina melhor de ler "
                        "texto financeiro?”", nivel=2)

    A.paragrafo(doc,
        "**Quem faz:** Araci (2019), Huang e colegas (2023), Shah e colegas (2022), "
        "CrudeBERT (2023), Santos e colegas (2023) — o meu modelo — e o Financial "
        "PhraseBank (2014).")

    A.paragrafo(doc,
        "**O que queriam:** este grupo **não tenta prever preço nenhum**. Eles "
        "constroem a ferramenta. A pergunta é: como fazer um programa que entenda "
        "linguagem financeira melhor que os anteriores?")

    A.paragrafo(doc,
        "**O que conseguiram: este é o grupo mais bem-sucedido de todos.** Os modelos "
        "atuais superam com folga os métodos antigos de contagem de palavras. É "
        "tecnologia madura e funciona.")

    A.paragrafo(doc,
        "**Detalhe importante para mim:** o sucesso deles é medido em **quão bem leem "
        "o texto**, não em quanto dinheiro isso daria. São coisas separadas — e é "
        "justamente aí que mora a minha frustração: eu tenho uma ferramenta que lê "
        "razoavelmente bem, e mesmo assim a previsão não decola.")

    A.secao(doc, "2.4", "Pergunta 4 — “A notícia melhora a previsão de RISCO?”",
            nivel=2)

    A.paragrafo(doc,
        "**Quem faz:** Bodilsen e Lunde (2025), Halousková e Lyócsa (2025), Mino e "
        "Williamson (2025), Rahimikia e Poon, e um estudo comparativo sobre "
        "criptomoedas.")

    A.paragrafo(doc,
        "**O que queriam:** existe um modelo clássico que prevê o sacolejo do preço "
        "usando **só o histórico do próprio preço** — sem ler nada. A pergunta é: "
        "acrescentar notícias melhora esse modelo?")

    A.paragrafo(doc,
        "**O que conseguiram: resultados modestos, porém reais e repetidos.** Este é o "
        "grupo mais **saudável** da área — os ganhos são pequenos, mas aparecem em "
        "estudos independentes:")

    A.tabela_abnt(doc, "1", "O que cada um conseguiu na previsão de risco",
        ["Pesquisa", "Conseguiu bater o modelo clássico?"],
        [
            ["Halousková e Lyócsa (2025)", "SIM — em 98,76% dos casos, 404 ações"],
            ["Bodilsen e Lunde (2025)", "SIM — com notícia macroeconômica"],
            ["Mino e Williamson (2025)", "não testaram fora da amostra"],
            ["Estudo sobre criptomoedas", "não com modelo simples; sim com modelos mais flexíveis"],
            ["A MINHA pesquisa", "NÃO (p = 0,64)"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**É aqui que eu perco**, e é honesto reconhecer. Mas também é aqui que sei "
        "exatamente o que falta: eles usam centenas de ações e medem o sacolejo de 5 em "
        "5 minutos; eu uso uma ação e meço uma vez por dia.")

    A.secao(doc, "2.5", "Pergunta 5 — “Dá para prever se o risco vai SUBIR ou CAIR?”",
            nivel=2)

    A.paragrafo(doc,
        "**Quem faz:** Hashamia e Maldonado (2025), sobre petróleo.")

    A.paragrafo(doc,
        "**O que queriam:** em vez de perguntar “qual será o tamanho do sacolejo”, "
        "perguntar **“amanhã vai sacudir mais ou menos que hoje?”**. É a pergunta mais "
        "nova do conjunto.")

    A.paragrafo(doc,
        "**O que conseguiram:** dois achados úteis. A **contagem** de notícias funcionou "
        "melhor que medir o sentimento delas. E usar a **compreensão** do texto "
        "funcionou melhor que usar o **parecer** “positivo/negativo”.")

    A.paragrafo(doc,
        "**É o alvo que eu nunca testei**, e é a minha recomendação número um.")

    A.secao(doc, "2.6", "Pergunta 6 — “Juntar preço com notícia bate preço sozinho?”",
            nivel=2)

    A.paragrafo(doc,
        "**Quem faz:** Nguyen e colegas (2015), Li e colegas (2020), Barak e colegas "
        "(2017).")

    A.paragrafo(doc,
        "**O que queriam:** não a acurácia absoluta, e sim o **ganho** que a notícia "
        "acrescenta a um modelo que já usa preço.")

    A.paragrafo(doc,
        "**O que conseguiram:** ganhos de **2 a 10 pontos percentuais** sobre o modelo "
        "só de preços.")

    A.paragrafo(doc,
        "**Esta é a comparação honesta para mim** — e é onde eu me saio bem: o meu "
        "ganho é de **4,4 pontos percentuais**, dentro da faixa da literatura "
        "internacional.")

    A.secao(doc, "2.7", "Pergunta 7 — “O que dá para MEDIR, sem prever nada?”",
            nivel=2)

    A.paragrafo(doc,
        "**Quem faz:** Pinheiro e colegas (índice de sentimento fiscal), Costa Neto e "
        "Anjos (qualidade de relatórios contábeis), Abílio e colegas (extração de "
        "entidades), além dos modelos de ESG e de declarações sobre o futuro.")

    A.paragrafo(doc,
        "**O que queriam:** usar as ferramentas para **construir instrumentos de "
        "medida** — termômetros —, e não para apostar em preço.")

    A.paragrafo(doc,
        "**O que conseguiram:** funcionou. Índices de sentimento fiscal, medidas de "
        "qualidade de divulgação corporativa, classificação ambiental e social. **É a "
        "aplicação mais bem-sucedida e menos explorada.**")

    # ── 3 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "3", "O balanço geral do campo")

    A.paragrafo(doc,
        "Somando tudo, o que a área conseguiu de fato:")

    A.tabela_abnt(doc, "2", "O que funciona e o que não funciona",
        ["Objetivo", "Situação"],
        [
            ["Construir a ferramenta de leitura", "FUNCIONA — tecnologia madura"],
            ["Medir coisas (índices, qualidade)", "FUNCIONA — e é subexplorado"],
            ["Ganho incremental sobre preço", "FUNCIONA — 2 a 10 pontos percentuais"],
            ["Prever RISCO melhor que o clássico", "FUNCIONA, mas pouco e nem sempre"],
            ["Prever DIREÇÃO com alta acurácia", "NÃO — os sucessos não se repetem"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**A frase que resume o campo é esta:** quanto mais perto de “ler e entender”, "
        "mais a área acerta. Quanto mais perto de “adivinhar para onde vai o preço”, "
        "mais ela erra — e mais os resultados espetaculares desaparecem quando alguém "
        "tenta repetir.")

    # ── 4 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "4", "Onde a minha pesquisa se encaixa")

    A.paragrafo(doc,
        "A minha pesquisa está nas perguntas **4** (risco), **6** (ganho incremental) "
        "e um pouco na **7** (medir).")

    A.tabela_abnt(doc, "3", "Como me saio em cada uma",
        ["Pergunta", "Como me saio"],
        [
            ["4 — prever risco melhor que o clássico", "PERCO — não superei (p = 0,64)"],
            ["6 — ganho incremental sobre preço", "VOU BEM — 4,4 p.p., dentro da faixa"],
            ["7 — medir", "VOU BEM — índice diário com marcação temporal precisa"],
            ["5 — direção do risco", "NÃO TESTEI — é a próxima coisa a fazer"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**E há uma coisa que eu faço e quase ninguém faz:** auditar a ferramenta. "
        "Descobri que o modelo classifica 48,5% de tudo como negativo, que o escore de "
        "confiança está numa escala errada, que manchetes em caixa alta o quebram, e "
        "que não existe um único dia, em oito anos, com maioria de notícias positivas.")

    A.paragrafo(doc,
        "**Nenhum dos trabalhos que citam esse modelo reportou nada disso.** É "
        "contribuição minha, e é do tipo que a banca reconhece: não é um número maior, "
        "é saber o que o número significa.")

    # ── 5 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "5", "Se você tiver dois minutos para explicar isso")

    A.lista(doc, [
        "“A área faz sete perguntas diferentes, e vale não confundi-las.”",
        "“Construir a ferramenta de leitura: resolvido, funciona bem.”",
        "“Usar a ferramenta para medir coisas: funciona, e é pouco explorado.”",
        "“Ganho da notícia sobre um modelo só de preços: funciona, 2 a 10 pontos "
        "percentuais. O meu é 4,4 — estou na faixa.”",
        "“Prever risco melhor que o modelo clássico: funciona pouco, e eu não "
        "consegui. Sei por quê: eles usam centenas de ações e dados de minuto a "
        "minuto.”",
        "“Prever direção com acurácia alta: não funciona para ninguém. Os casos "
        "famosos não se repetem quando alguém tenta.”",
        "“E prever se o risco vai subir ou cair é a pergunta mais nova — eu ainda não "
        "testei, e é o meu próximo passo.”",
    ])

    doc.save(SAIDA)
    print(f"[OK] Documento gerado: {SAIDA}")


if __name__ == "__main__":
    main()
