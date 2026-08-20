# -*- coding: utf-8 -*-
# ==============================================================================
#   Roteiro curto para a reunião — só previsão de direção e volatilidade
#   Saída: Mentoria_Emerson_13082026/06_ROTEIRO_DA_REUNIAO.docx
# ==============================================================================
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(RAIZ / "src" / "comum"))

import abnt_docx as A  # noqa: E402

FONTE = "Elaborado pelo autor (2026)"
SAIDA = AQUI / "06_ROTEIRO_DA_REUNIAO.docx"


def main() -> None:
    doc = A.novo_documento()

    A.capa(
        doc,
        titulo="Quem tenta prever direção e volatilidade",
        subtitulo="Dezesseis pesquisas, o que buscam, o que conseguiram e com que "
                  "ferramenta — roteiro objetivo para a reunião",
        autor="Vanderlei Barbosa da Silva",
        orientador="Orientador: Prof. Dr. Julio Cesar Nievola",
        instituicao="PUCPR — Programa de Pós-Graduação em Informática (PPGIa)",
        descricao="Recorte estrito: apenas pesquisas cujo objetivo é prever a direção "
                  "ou a volatilidade do preço de um ativo ou índice. Ficam de fora os "
                  "trabalhos que apenas constroem ferramentas de leitura ou constroem "
                  "índices de medida. Elaborado em 20 de agosto de 2026.",
    )

    A.secao(doc, "1", "A resposta em cinco linhas")

    A.lista(doc, [
        "**Volatilidade:** dois trabalhos superam o modelo de referência e nós não. "
        "Mas eles usam **404 ações** e dados **de 5 em 5 minutos**; nós, **uma ação** "
        "e dado **diário**.",
        "**Direção:** ninguém prevê bem. Os números altos são de **15 dias** (Bollen), "
        "de **20 minutos** (Schumaker), do **nível do preço** (FinBERT-LSTM) ou de "
        "**outro mercado** (Barak).",
        "**A comparação legítima** não é a acurácia absoluta: é o **ganho** que a "
        "notícia acrescenta a um modelo só de preços. A literatura reporta **2 a 10 "
        "pontos percentuais**. **O nosso é 4,4. Estamos na faixa.**",
        "**A ferramenta convergiu:** quase todos usam **FinBERT** ou variante. Não é "
        "aí que está a diferença de desempenho.",
        "**Há um alvo novo** que ninguém no Brasil testou: prever se a volatilidade "
        "vai **subir ou descer**, em vez do tamanho dela.",
    ])

    A.secao(doc, "2", "Volatilidade — quem tenta e o que conseguiu")

    A.tabela_abnt(doc, "1", "Previsão de volatilidade",
        ["Pesquisa", "Ferramenta", "Resultado", "Bate a referência?"],
        [
            ["Halousková e Lyócsa (2025)", "FinBERT + HAR, 404 ações",
             "−12,74% de erro; 14,99% nos dias extremos", "SIM — 98,76% dos casos"],
            ["Bodilsen e Lunde (2025)", "notícias + família HAR",
             "notícia macro melhora; da empresa não", "SIM"],
            ["Mino e Williamson (2025)", "BERT + GARCH(1,1)-t",
             "coeficiente −0,2275 (p=0,0016)", "não testaram fora da amostra"],
            ["Rahimikia e Poon (2021)", "embeddings, sem sentimento",
             "usa a compreensão, não o parecer", "parcial"],
            ["Horserace cripto (2024)", "HAR contra LightGBM e LSTM",
             "sentimento só ajuda com modelo flexível", "só com ML"],
            ["Silva (2018)", "sentimento + GARCH + quantílica",
             "linear dá R² negativo; quantílica ganha", "só quantílico"],
            ["A NOSSA (2026)", "FinBERT-PT-BR + HAR + GARCH",
             "coef. −0,2924 (p=0,0002); melhor: empresa em 22 dias, +1,77%", "NÃO (p=0,64)"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**O que dizer:** “Perco na previsão de volatilidade, e sei exatamente por "
        "quê. Halousková e Lyócsa usam 404 ações e medem o sacolejo de 5 em 5 minutos; "
        "eu uso uma ação e meço uma vez por dia. Isso é falta de dado, não ausência de "
        "sinal — o meu coeficiente é significativo, com magnitude igual à do estudo "
        "americano.”")

    A.secao(doc, "3", "Direção — quem tenta e o que conseguiu")

    A.tabela_abnt(doc, "2", "Previsão de direção",
        ["Pesquisa", "Ferramenta", "Número anunciado", "O que o número realmente é"],
        [
            ["Bollen et al. (2011)", "dicionários de humor",
             "86,7%", "13 acertos em 15 pregões — REFUTADO em 2017"],
            ["Schumaker e Chen (2009)", "saco de palavras + SVM",
             "71,2%", "preço 20 MINUTOS depois; melhor entre esquemas"],
            ["Barak et al. (2017)", "ensembles",
             "83,6%", "Teerã, outra tarefa; já replicado: deu 53,14%"],
            ["FinBERT-LSTM (2022–24)", "FinBERT + LSTM",
             "0,955", "é 1 − MAPE: prevê o NÍVEL do preço, não a direção"],
            ["Nguyen et al. (2015)", "sentimento por tópico",
             "ganho de 2 a 10 p.p.", "ganho sobre só-preços — comparação válida"],
            ["Li et al. (2020)", "fusão profunda",
             "supera as bases", "corrobora a nossa arquitetura"],
            ["FinBERT + SHAP (2025)", "FinBERT + árvores",
             "supera bases técnicas", "desenho próximo ao nosso"],
            ["A NOSSA (2026)", "FinBERT-PT-BR + XGBoost",
             "54,5%", "ganho de 4,4 p.p. sobre só-preços (p=0,012)"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**O que dizer:** “Na direção, ninguém acerta de verdade. O número mais citado "
        "da área são treze acertos em quinze dias, e foi refutado. Os outros medem "
        "coisas diferentes: reação em vinte minutos, ou o nível do preço, que é "
        "trivial de prever. A comparação honesta é o ganho sobre um modelo só de "
        "preços — e nisso eu estou dentro da faixa da literatura.”")

    A.secao(doc, "4", "Os encoders — todos usam a mesma coisa")

    A.tabela_abnt(doc, "3", "Que ferramenta cada um usa para ler",
        ["Geração", "Ferramenta", "Quem usa"],
        [
            ["Dicionário (2009–2011)", "OpinionFinder, GPOMS, saco de palavras",
             "Bollen, Schumaker"],
            ["Aprendizado clássico (2015–2017)", "TSLDA, ensembles",
             "Nguyen, Barak"],
            ["Transformers (2020–2025)", "FinBERT e variantes",
             "Halousková, Mino, Hashamia, FinBERT-LSTM, FinBERT+SHAP"],
            ["Especializados (2023–2025)", "CrudeBERT (petróleo), FinBERT-PT-BR",
             "Hashamia; A NOSSA"],
            ["Embeddings (2021–2025)", "FastText, embedding próprio",
             "Rahimikia, Hashamia"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**O que dizer:** “A ferramenta convergiu — praticamente todo mundo usa "
        "FinBERT ou variante, inclusive eu. **A diferença de desempenho não está no "
        "encoder**; está em quantos ativos, com que frequência de dado e com que "
        "método de combinação.”")

    A.paragrafo(doc,
        "E há um sinal que aparece em duas pesquisas independentes: **usar os "
        "*embeddings*** — a compreensão bruta do texto — **funciona melhor que usar o "
        "parecer “positivo/negativo”**. É caminho que ainda não testei.")

    A.secao(doc, "5", "O que proponho fazer")

    A.tabela_abnt(doc, "4", "As quatro ações mais baratas",
        ["#", "O que fazer", "De onde veio", "Custo"],
        [
            ["1", "Prever a DIREÇÃO da volatilidade (sobe ou desce)",
             "Hashamia e Maldonado (2025)", "baixo"],
            ["2", "Adotar recorte EMPRESA e varrer prazos de 10 a 30 dias",
             "experimento próprio", "muito baixo"],
            ["3", "Replicar para 5 a 10 ações da B3",
             "Halousková e Lyócsa (2025)", "médio"],
            ["4", "Buscar dados intradiários da PETR4",
             "3 fontes independentes", "alto"],
        ], fonte=FONTE)

    A.secao(doc, "6", "Duas coisas a declarar antes que perguntem")

    A.lista(doc, [
        "**O número 54,93% sai.** É acurácia de validação, não de teste. No teste "
        "ponderar dá 50,31%, contra 53,88% sem ponderar. **O número correto é 54,5%.**",
        "**Originalidade com precisão:** prever direção é o assunto mais concorrido da "
        "área. O que é raro é a **combinação** — direção e volatilidade juntas, sobre "
        "uma ação individual, em português, com teste consultado uma vez só.",
    ])

    A.secao(doc, "7", "Roteiro de dois minutos")

    A.lista(doc, [
        "“Levantei dezesseis pesquisas que preveem direção ou volatilidade. Estão na "
        "planilha, com alvo, mercado, encoder, volume de notícias e resultado.”",
        "“Na volatilidade, dois superam o modelo de referência e eu não — mas usam 404 "
        "ações e dados de 5 minutos, contra a minha ação única e dado diário.”",
        "“Na direção, ninguém acerta. O 86,7% mais citado da área são 13 acertos em 15 "
        "dias, e foi refutado em 2017.”",
        "“A comparação justa é o ganho sobre um modelo só de preços: a literatura dá "
        "de 2 a 10 pontos percentuais, e o meu é 4,4.”",
        "“Todos usam FinBERT ou variante — a diferença não está no encoder, está na "
        "quantidade de ativos e na frequência do dado.”",
        "“E encontrei um alvo novo: prever se a volatilidade sobe ou desce. Tem código "
        "público, é sobre petróleo, e eu nunca testei. É o meu próximo passo.”",
    ])

    doc.save(SAIDA)
    print(f"[OK] {SAIDA}")


if __name__ == "__main__":
    main()
