# -*- coding: utf-8 -*-
# ==============================================================================
#   As seis pesquisas essenciais — 3 de direção, 3 de volatilidade
#   Saída: Mentoria_Emerson_13082026/08_AS_SEIS_ESSENCIAIS.docx
#
#   Critério de seleção: relevância para o nosso contexto (ativo, arquitetura,
#   idioma, alvo) cruzada com a qualidade do resultado reportado.
# ==============================================================================
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(RAIZ / "src" / "comum"))

import abnt_docx as A  # noqa: E402

FONTE = "Elaborado pelo autor (2026)"
SAIDA = AQUI / "08_AS_SEIS_ESSENCIAIS.docx"


def main() -> None:
    doc = A.novo_documento()

    A.capa(
        doc,
        titulo="As seis que importam",
        subtitulo="Três pesquisas sobre direção e três sobre volatilidade — as mais "
                  "próximas do nosso caso e com os melhores resultados",
        autor="Vanderlei Barbosa da Silva",
        orientador="Orientador: Prof. Dr. Julio Cesar Nievola",
        instituicao="PUCPR — Programa de Pós-Graduação em Informática (PPGIa)",
        descricao="Recorte das seis pesquisas selecionadas por dois critérios "
                  "combinados: proximidade do nosso desenho — ativo, arquitetura, "
                  "alvo — e qualidade do resultado reportado. Escrito para ser "
                  "entendido sem conhecimento prévio de aprendizado de máquina. "
                  "Elaborado em 20 de agosto de 2026.",
    )

    # ── 1 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "1", "Como escolhi estas seis")

    A.paragrafo(doc,
        "Das vinte e cinco pesquisas levantadas, dezesseis preveem direção ou "
        "volatilidade. Dessas, escolhi seis por **dois critérios ao mesmo tempo**: "
        "quão perto estão do que eu faço, e quão bom é o resultado que reportam.")

    A.paragrafo(doc,
        "**Ficaram de fora, e é bom saber por quê:** Bollen (refutado em 2017), Barak "
        "(outro mercado, e já repliquei sem êxito), FinBERT-LSTM (prevê o nível do "
        "preço, não a direção) e Li (sem magnitude precisa).")

    A.tabela_abnt(doc, "1", "As seis, em uma tabela",
        ["Alvo", "Pesquisa", "Melhor resultado", "Por que importa para mim"],
        [
            ["VOLAT.", "Halousková e Lyócsa (2025)",
             "vence o HAR em 98,76% das 404 ações; −12,74% de erro; −14,99% nos dias extremos",
             "confirma o meu efeito de cauda; usa FinBERT e HAR como eu"],
            ["VOLAT.", "Hashami e Maldonado (2025)",
             "FastText 0,7136 contra HAR 0,6494; contagem de notícias 0,7054",
             "PETRÓLEO — o meu ativo; código público; prova que embedding vence sentimento"],
            ["VOLAT.", "Bodilsen e Lunde (2025)",
             "notícia macro melhora; da empresa não; ganho maior em prazo longo",
             "revista de primeira linha; gerou o meu melhor resultado ao ser testada"],
            ["DIREÇÃO", "Ruan e Jiang (2025)",
             "supera bases técnicas e lexicais em AUC, F1 e lucro simulado",
             "ARQUITETURA QUASE IDÊNTICA à minha: FinBERT + preço + volatilidade em XGBoost"],
            ["DIREÇÃO", "Nguyen et al. (2015)",
             "ganho de 2,1 a 9,8 pontos percentuais sobre só-preços",
             "É A MINHA RÉGUA: o meu ganho de 4,4 p.p. está dentro dessa faixa"],
            ["DIREÇÃO", "Schumaker e Chen (2009)",
             "71,18% de acurácia direcional",
             "o maior número legítimo de direção — mas em 20 minutos, não no dia seguinte"],
        ], fonte=FONTE)

    # ── 2 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "2", "VOLATILIDADE 1 — Halousková e Lyócsa (2025)")

    A.paragrafo(doc,
        "*Universidade Masaryk (Brno) e Academia Eslovaca de Ciências. PDF baixado e "
        "lido.*", recuo=False)

    A.paragrafo(doc,
        "**O que buscam:** prever o **sacolejo** de 404 ações do S&P 500, usando a "
        "**atenção e o humor do público em relação a dez indicadores macroeconômicos "
        "agendados** — reunião do banco central americano, folha de pagamento, emprego. "
        "Não é notícia de empresa.")

    A.paragrafo(doc,
        "**O que conseguiram: vencem o modelo de referência em 98,76% das ações**, com "
        "redução média de erro de 12,74%. **E o maior ganho, de 14,99%, é nos dias de "
        "variação extrema.**")

    A.paragrafo(doc,
        "**Como fizeram:** FinBERT (o mesmo do meu, na versão inglesa); volatilidade "
        "medida como variância realizada de retornos de **5 minutos** — 78 medições por "
        "dia; onze anos de dados (2010–2021); fontes de sinal: Google Trends, jornais, "
        "Twitter e Wikipédia. **A Wikipédia não serviu para nada**; o banco central foi "
        "o indicador mais importante.")

    A.paragrafo(doc,
        "**Por que importa para mim — duas coisas.** Primeira: **eles confirmam o meu "
        "achado principal.** Eu descobri que o sentimento não move o pregão comum e "
        "importa nos extremos, usando uma ação brasileira e dado diário. Eles chegam ao "
        "mesmo lugar com 404 ações americanas e dado de minuto. **Isso deixa de ser "
        "coincidência minha e vira fato do fenômeno.**")

    A.paragrafo(doc,
        "Segunda: **eles me superam, e eu sei exatamente por quê.** 404 ações contra a "
        "minha uma; medição de 5 em 5 minutos contra a minha diária. **É falta de dado, "
        "não ausência de sinal.**")

    A.paragrafo(doc,
        "**E o detalhe que refina o meu próprio experimento:** o “macro” deles são "
        "**anúncios agendados da economia americana** afetando **ações americanas**. O "
        "meu “macro” é guerra na Ucrânia e OPEP afetando uma ação brasileira. **Por isso "
        "o deles funciona e o meu atrapalha** — e agora eu tenho como explicar isso.")

    # ── 3 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "3", "VOLATILIDADE 2 — Hashami e Maldonado (2025)")

    A.paragrafo(doc,
        "*Universidade de Essex. PDF baixado e lido. Código público no GitHub.*",
        recuo=False)

    A.paragrafo(doc,
        "**Esta é, de longe, a mais importante das seis para mim.** É sobre **petróleo "
        "Brent** — a commodity que move a Petrobras —, usa dez anos de notícias da "
        "Eikon (2014–2024), e traz uma tabela de resultados que responde a uma pergunta "
        "que eu vinha fazendo há meses.")

    A.paragrafo(doc,
        "**O que buscam:** prever a **direção da volatilidade** — se amanhã o preço vai "
        "sacudir **mais ou menos** que hoje. E fazem isso **usando só notícias**, sem "
        "nenhum dado de mercado.")

    A.secao(doc, "3.1", "A tabela que muda a minha pesquisa", nivel=2)

    A.tabela_abnt(doc, "2", "Resultados de Hashami e Maldonado (acurácia)",
        ["Método", "Acurácia", "Bate o HAR?"],
        [
            ["HAR (referência, só histórico de preço)", "0,6494", "—"],
            ["VADER (dicionário)", "0,5777", "não"],
            ["TextBlob (dicionário)", "0,5777", "não"],
            ["FinBERT — como CLASSIFICADOR de sentimento", "0,5368", "NÃO — o pior de todos"],
            ["CrudeBERT (o BERT do petróleo)", "0,6105", "não"],
            ["CONTAGEM de notícias (só contar!)", "0,7054", "SIM"],
            ["GloVe (embedding)", "0,6661", "sim"],
            ["FinBERT — como EMBEDDING", "0,6694", "SIM"],
            ["BERT (embedding)", "0,6743", "sim"],
            ["Gemini (embedding)", "0,6858", "sim"],
            ["LLaMA (embedding)", "0,6890", "sim"],
            ["FastText (embedding)", "0,7136", "SIM — o melhor"],
        ], fonte=FONTE + ". Tabelas 2 e 3 do artigo original.")

    A.paragrafo(doc, "**Três coisas saltam desta tabela.**")

    A.paragrafo(doc,
        "**Primeira, e é a mais importante da minha pesquisa inteira:** olhe as duas "
        "linhas do FinBERT. **É o mesmo modelo.** Usado como **classificador de "
        "sentimento** dá **0,5368** — o pior resultado da tabela, pior até que "
        "dicionários simples. Usado como **embedding** dá **0,6694** — e vence a "
        "referência.")

    A.paragrafo(doc,
        "**Treze pontos percentuais de diferença, no mesmo modelo, só por não passar "
        "pela cabeça de sentimento.** É a comparação controlada que eu precisava. Todos "
        "os defeitos que auditei no meu modelo — viés de 48,5% de negativos, escala "
        "errada do escore, zero dias positivos — estão **na parte que dá 0,5368**. "
        "Nenhum está na parte que dá 0,6694.")

    A.paragrafo(doc,
        "**Segunda: simplesmente CONTAR notícias (0,7054) vence todos os métodos de "
        "sentimento** e vence o HAR com significância estatística confirmada por teste "
        "de McNemar. Ler o tom da notícia funcionou pior que ignorar o tom e só contar "
        "quantas saíram.")

    A.paragrafo(doc,
        "**Terceira: o CrudeBERT — o modelo feito sob medida para petróleo — dá 0,6105 "
        "e ainda perde para o HAR.** Especializar o classificador ajuda um pouco, mas "
        "não resolve. **É exatamente o que eu descobri em nove tentativas.**")

    A.paragrafo(doc,
        "**O que faço com isso:** três coisas, e todas com os dados que já tenho. "
        "Adotar o alvo deles (direção da volatilidade). Testar a contagem de notícias "
        "contra esse alvo. E extrair embeddings do FinBERT-PT-BR em vez de usar o "
        "parecer positivo/negativo.")

    # ── 4 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "4", "VOLATILIDADE 3 — Bodilsen e Lunde (2025)")

    A.paragrafo(doc,
        "*Journal of Applied Econometrics, 40(1):18–36. Texto atrás de assinatura; "
        "dados via resumo.*", recuo=False)

    A.paragrafo(doc,
        "**O que buscam:** a mesma coisa que eu — acrescentar notícias a um modelo de "
        "volatilidade e ver se melhora. Publicado numa das revistas mais respeitadas de "
        "econometria aplicada.")

    A.paragrafo(doc,
        "**O que conseguiram:** duas conclusões. **Notícia da própria empresa não "
        "acrescenta nada.** **Notícia macroeconômica melhora significativamente**, e "
        "mais ainda em **prazos longos**.")

    A.paragrafo(doc,
        "**Por que importa para mim: foi esta pesquisa que gerou o meu melhor "
        "resultado.** Como a conclusão deles descrevia exatamente o meu caso — eu uso "
        "notícia ligada à empresa e medi só a um dia —, fui testar. **E deu o "
        "contrário:**")

    A.tabela_abnt(doc, "3", "O meu teste da hipótese deles (ganho sobre o HAR)",
        ["Que notícias uso", "1 dia", "5 dias", "22 dias"],
        [
            ["EMPRESA", "+1,03%", "+0,37%", "+1,77%"],
            ["MACRO", "−0,33%", "−1,09%", "−1,79%"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**Na PETR4, a notícia da empresa é a melhor e a macro atrapalha de verdade** "
        "— com significância estatística nos dois prazos longos. E o melhor número da "
        "minha pesquisa inteira apareceu aqui: **+1,77% em 22 dias**, faltando pouco "
        "para o critério estatístico.")

    A.paragrafo(doc,
        "**A explicação:** a Petrobras é estatal. O que mexe com o risco dela vem de "
        "dentro — preço de combustível, troca de diretoria, intervenção do governo. Numa "
        "ação comum americana, o peso do macroeconômico é maior. **E a metade da "
        "hipótese deles se confirmou: o melhor prazo é o longo, não o de um dia.**")

    # ── 5 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "5", "DIREÇÃO 1 — Ruan e Jiang (2025)")

    A.paragrafo(doc,
        "*Mathematics, 13(17):2747. Editora bloqueou o acesso; dados via resumo.*",
        recuo=False)

    A.paragrafo(doc,
        "**Esta é a pesquisa cuja arquitetura mais se parece com a minha.** Compare:")

    A.tabela_abnt(doc, "4", "Ruan e Jiang comparados a mim",
        ["Elemento", "Eles", "Eu"],
        [
            ["Encoder", "FinBERT", "FinBERT-PT-BR"],
            ["Atributos", "sentimento + preço + volatilidade", "sentimento + preço + volatilidade"],
            ["Classificador", "XGBoost", "XGBoost"],
            ["Mercado", "S&P 500", "PETR4"],
            ["Período", "2018–2023", "2018–2025"],
            ["Explicabilidade", "SIM (SHAP)", "não tenho"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**O que conseguiram:** superam tanto as bases só-técnicas quanto as baseadas "
        "em dicionário, em AUC, F1 e lucro simulado. E a análise de importância mostra "
        "que **o sentimento do FinBERT responde por 28,6%** da decisão do modelo, e a "
        "volatilidade por 21,4%.")

    A.paragrafo(doc,
        "**Por que importa: é a prova de que a minha arquitetura é a correta.** Um "
        "trabalho de 2025, publicado, usa exatamente o mesmo desenho que eu escolhi. "
        "**Não estou fazendo nada estranho.**")

    A.paragrafo(doc,
        "**O que eles têm e eu não:** o **SHAP**, que abre a caixa-preta e mostra quais "
        "palavras levaram o modelo a decidir. É biblioteca pronta, custa horas de "
        "trabalho, e banca gosta muito. **Acrescentar isso é barato.**")

    A.paragrafo(doc,
        "**Ressalva honesta:** não consegui os números exatos de acurácia — a editora "
        "bloqueou. Antes de citar magnitudes, preciso pegar o texto.")

    # ── 6 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "6", "DIREÇÃO 2 — Nguyen, Shirai e Velcin (2015)")

    A.paragrafo(doc,
        "*Expert Systems with Applications. Texto atrás de assinatura.*", recuo=False)

    A.paragrafo(doc,
        "**O que buscam:** prever a direção de ações americanas com sentimento extraído "
        "**por tópico** — não um sentimento único, mas um por assunto.")

    A.paragrafo(doc,
        "**O que conseguiram: ganho de 2,1 a 9,8 pontos percentuais** sobre um modelo "
        "que usa só preços.")

    A.paragrafo(doc,
        "**Por que importa — e esta é a pesquisa mais útil das seis para a minha "
        "defesa.** Eles não reportam acurácia absoluta; reportam o **ganho**. E é essa "
        "a comparação justa entre estudos, porque a acurácia absoluta depende do "
        "mercado, do ativo e do período, mas o ganho mede a contribuição da notícia.")

    A.paragrafo(doc,
        "**O meu ganho é de 4,4 pontos percentuais. Está dentro da faixa deles.** "
        "Quando alguém disser que os meus 54,5% são baixos, a resposta é: *“a métrica "
        "comparável não é a acurácia, é o ganho sobre um modelo só de preços. A "
        "literatura reporta de 2 a 10 pontos percentuais. O meu é 4,4.”*")

    A.paragrafo(doc,
        "**Ressalva:** já testei a ideia deles de sentimento por tópico — usei os sete "
        "índices por categoria temática — e **piorou** fora da amostra. Está na "
        "Seção 4.d.")

    # ── 7 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "7", "DIREÇÃO 3 — Schumaker e Chen (2009)")

    A.paragrafo(doc,
        "*Information Processing & Management, 45:571–583. Texto atrás de assinatura.*",
        recuo=False)

    A.paragrafo(doc,
        "**O que buscam:** prever o preço de ações do S&P 500 **vinte minutos depois** "
        "de a notícia sair.")

    A.paragrafo(doc,
        "**O que conseguiram: 71,18% de acurácia direcional** e retorno simulado de "
        "8,50%. **É o maior número legítimo de direção do conjunto todo** — os que são "
        "maiores ou foram refutados, ou medem outra coisa.")

    A.paragrafo(doc,
        "**Mas atenção ao que ele mede.** Vinte minutos depois da notícia é **reação**, "
        "não antecipação. E os 71,18% são **o melhor entre vários esquemas** de "
        "particionamento.")

    A.paragrafo(doc,
        "**Por que importa: eu já medi a mesma coisa, sem perceber.** Na minha auditoria "
        "eu separei dois momentos e encontrei isto:")

    A.tabela_abnt(doc, "5", "O meu próprio resultado, que diz a mesma coisa",
        ["Momento", "Positivo", "Neutro", "Negativo"],
        [
            ["Pregão que reage (é o que o Schumaker mede)", "55,0%", "53,2%", "51,6%"],
            ["Dia seguinte (é o que eu tento prever)", "52,5%", "52,4%", "51,5%"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**No momento da reação o sinal existe e é ordenado; no dia seguinte ele "
        "some.** Schumaker mediu a reação com precisão de vinte minutos; eu medi com "
        "precisão de um dia — e vi o mesmo padrão.")

    A.paragrafo(doc,
        "**A lição:** o sinal vive no curtíssimo prazo. **Com Halousková (5 minutos) e "
        "com o meu P0 contra P1, são três apoios independentes para buscar dados "
        "intradiários da PETR4.**")

    # ── 8 ────────────────────────────────────────────────────────────────────
    A.secao(doc, "8", "O que as seis dizem, juntas")

    A.tabela_abnt(doc, "6", "As seis lições, e o que faço com cada uma",
        ["Lição", "De quem vem", "O que faço"],
        [
            ["O efeito é de cauda", "Halousková; e eu",
             "já está na dissertação — agora com apoio externo"],
            ["Embedding vence cabeça de sentimento",
             "Hashami (0,6694 contra 0,5368)", "extrair embeddings do FinBERT-PT-BR"],
            ["Contar notícias vence medir o tom", "Hashami (0,7054)",
             "testar contagem contra a direção da volatilidade"],
            ["Prazo longo é melhor que um dia", "Bodilsen; e o meu teste",
             "varrer horizontes de 10 a 30 dias"],
            ["A minha arquitetura está certa", "Ruan e Jiang",
             "manter — e acrescentar SHAP"],
            ["A régua é o GANHO, não a acurácia", "Nguyen (2 a 10 p.p.)",
             "apresentar sempre os 4,4 p.p."],
        ], fonte=FONTE)

    A.secao(doc, "9", "Se você tiver dois minutos para explicar isso")

    A.lista(doc, [
        "“Separei seis pesquisas: três de volatilidade e três de direção, escolhidas "
        "por serem as mais próximas do meu caso e as de melhor resultado.”",
        "“A mais importante é sobre petróleo — o meu ativo — e tem código público. E "
        "ela traz uma tabela que resolve uma dúvida minha de meses.”",
        "“Nessa tabela, o FinBERT usado como classificador de sentimento dá 0,5368, o "
        "pior de todos. O MESMO FinBERT usado como embedding dá 0,6694 e vence a "
        "referência. Treze pontos de diferença, no mesmo modelo.”",
        "“E simplesmente contar quantas notícias saíram no dia dá 0,7054 — vence todo "
        "método de sentimento.”",
        "“Isso explica os meus nove experimentos fracassados: todos mexiam na parte que "
        "dá 0,5368.”",
        "“Na direção, achei um trabalho de 2025 com arquitetura idêntica à minha — "
        "FinBERT mais preço e volatilidade em XGBoost. Estou no caminho certo; falta-me "
        "a explicabilidade que eles têm.”",
        "“E a régua justa é o ganho sobre um modelo só de preços: a literatura dá de 2 "
        "a 10 pontos percentuais, e o meu é 4,4.”",
    ])

    doc.save(SAIDA)
    print(f"[OK] {SAIDA}")


if __name__ == "__main__":
    main()
