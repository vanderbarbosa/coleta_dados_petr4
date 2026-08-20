# -*- coding: utf-8 -*-
# ==============================================================================
#   Ficha de leitura de cada pesquisa de previsão, no mesmo formato de perguntas
#   Saída: Mentoria_Emerson_13082026/07_FICHAS_UMA_A_UMA.docx
#
#   Formato fixo, sete perguntas por pesquisa — as mesmas que o Vanderlei fez.
# ==============================================================================
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(RAIZ / "src" / "comum"))

import abnt_docx as A  # noqa: E402

SAIDA = AQUI / "07_FICHAS_UMA_A_UMA.docx"

# (titulo, [(pergunta, resposta), ...])
FICHAS = [
 ("Halousková e Lyócsa (2025) — volatilidade de 404 ações", "PDF baixado", [
  ("Busca notícias?",
   "**Sim** — e mais que isso: usa quatro fontes. Artigos de jornal, Twitter, buscas no "
   "Google e visitas à Wikipédia."),
  ("Prevê direção ou volatilidade?",
   "**VOLATILIDADE, só.** Nunca tentam prever direção."),
  ("Qual é o número principal e o que ele mede?",
   "Não é acurácia — é **redução de erro**: −12,74% em média, e **−14,99% nos dias de "
   "variação extrema**. Superam a referência em 98,76% das 404 ações."),
  ("Foi refutada?",
   "**Não.** Nenhuma contestação publicada."),
  ("Qual o tamanho do teste?",
   "**Onze anos** — de 10/03/2010 a 24/02/2021, com no mínimo 2.750 pregões por ação, "
   "em 404 ações do S&P 500."),
  ("Que encoder usa?",
   "**FinBERT do Araci (2019)** — a mesma linhagem do nosso FinBERT-PT-BR. Volatilidade "
   "medida por variância realizada de retornos de **5 minutos** (78 pontos por dia)."),
  ("Vale comparar com a nossa?",
   "**Sim, e eles nos superam.** Mas há um detalhe decisivo: o sentimento deles é sobre "
   "**dez indicadores macroeconômicos agendados** — reunião do FOMC, folha de pagamento, "
   "emprego —, não sobre notícia de empresa. Reforça a nossa Seção 4.o: o “macro” deles é "
   "macro doméstica agendada dos EUA para ações dos EUA; o nosso é geopolítica "
   "internacional não agendada."),
 ]),

 ("Bollen, Mao e Zeng (2011) — direção do índice DJIA", "PDF baixado", [
  ("Busca notícias?",
   "**Não exatamente.** Usa **tuítes** — 9.853.498 mensagens do Twitter —, não notícias "
   "de jornal."),
  ("Prevê direção ou volatilidade?",
   "**DIREÇÃO**, e de um **índice** (o Dow Jones), não de uma ação individual."),
  ("Qual é o número principal e o que ele mede?",
   "**86,7% de acurácia na DIREÇÃO.** Não tem nada a ver com volatilidade."),
  ("Foi refutada?",
   "**Sim.** Lachanski e Pav (2017), na *Econ Journal Watch*, refizeram a análise e "
   "estenderam a série para incluir 2007. **O efeito sumiu.** Diagnóstico: eles testaram "
   "**sete dimensões de humor** em várias defasagens e reportaram a que deu certo. "
   "Testando bastante, alguma acerta por acaso — chama-se garimpagem de dados."),
  ("Qual o tamanho do teste?",
   "**Quinze pregões.** Treinaram de 28/02 a 28/11/2008 e testaram de 01 a 19/12/2008. "
   "**13 acertos ÷ 15 dias = 86,7%.** E por que só 15? Porque era o que sobrava: os "
   "dados de Twitter iam até 19/12/2008, e quase tudo foi para o treino."),
  ("Que encoder usa?",
   "**Nenhum.** É de 2011, anterior ao BERT. Usa dois dicionários de palavras: "
   "OpinionFinder (positivo/negativo) e GPOMS (sete dimensões de humor)."),
  ("Vale comparar com a nossa?",
   "**Não.** Quinze dias de teste contra os nossos 497; índice contra ação individual; "
   "e não replicou. **O que sobra de útil:** das sete dimensões de humor, só a **calma** "
   "previu. Positivo/negativo — que é a nossa medida — **não previu**."),
 ]),

 ("Bodilsen e Lunde (2025) — volatilidade de ações dos EUA", "não baixado (Wiley)", [
  ("Busca notícias?", "**Sim** — analítica de notícias comercial."),
  ("Prevê direção ou volatilidade?", "**VOLATILIDADE**, em vários horizontes."),
  ("Qual é o número principal?",
   "Não reportam acurácia. Reportam que **notícia macroeconômica melhora "
   "significativamente** as previsões, e **notícia da empresa não acrescenta nada** ao "
   "que a volatilidade passada já contém. O ganho é maior em **horizontes longos**."),
  ("Foi refutada?", "**Não.** Publicado no *Journal of Applied Econometrics*, periódico "
   "de primeira linha em econometria aplicada."),
  ("Qual o tamanho do teste?", "Não recuperado — o texto está atrás de assinatura."),
  ("Que encoder usa?", "Analítica de notícias comercial, não um encoder aberto."),
  ("Vale comparar com a nossa?",
   "**Sim, e nos superam.** Foi a partir deles que rodamos o experimento da Seção 4.o — "
   "e **na PETR4 a conclusão inverte-se**: aqui a notícia da empresa ajuda (+1,77% em 22 "
   "dias) e a macro **atrapalha** de forma significativa. Explicação: a PETR4 é estatal, "
   "e o nosso “macro” é geopolítica internacional, não macro doméstica."),
 ]),

 ("Mino e Williamson (2025) — volatilidade do S&P 500", "PDF baixado", [
  ("Busca notícias?", "**Sim** — mais de 10.000 manchetes de 100 fontes dos EUA."),
  ("Prevê direção ou volatilidade?", "**VOLATILIDADE.**"),
  ("Qual é o número principal?",
   "O **coeficiente do sentimento: −0,2275**, com valor-p de 0,0016. O sinal negativo "
   "significa: sentimento mais pessimista hoje, mais volatilidade amanhã. **O nosso é "
   "−0,2924, com p = 0,0002 — praticamente igual.**"),
  ("Foi refutada?", "**Não.**"),
  ("Qual o tamanho do teste?",
   "**105 dias** — de janeiro a julho de 2024. Contra os nossos 1.988 pregões."),
  ("Que encoder usa?",
   "BERT genérico ajustado ao domínio financeiro. Modelo de volatilidade: **GARCH(1,1) "
   "com distribuição t-Student — exatamente o mesmo do nosso Script 04.**"),
  ("Vale comparar com a nossa?",
   "**Sim — e aqui NÓS levamos vantagem.** Eles **não avaliam fora da amostra** (é como "
   "conferir a prova com o gabarito na mão) e **não separam períodos de crise dos "
   "normais**, o que declaram como limitação. Nós fazemos as duas coisas. **Eles param "
   "onde nós continuamos.**"),
 ]),

 ("Hashamia e Maldonado (2025) — direção da volatilidade do petróleo", "PDF baixado", [
  ("Busca notícias?", "**Sim** — 592.858 manchetes da Reuters, de 2014 a 2023."),
  ("Prevê direção ou volatilidade?",
   "**As duas coisas ao mesmo tempo, e é aí que está a novidade:** preveem a **DIREÇÃO "
   "DA VOLATILIDADE** — se amanhã o preço vai sacudir **mais ou menos** que hoje. Não é "
   "direção do preço nem tamanho do sacolejo. É uma terceira pergunta."),
  ("Qual é o número principal?",
   "Os números de acurácia não estavam legíveis no PDF. Mas dois achados vieram claros: "
   "**a contagem de notícias superou as medidas de sentimento**, e **o FastText superou "
   "as cabeças de sentimento**."),
  ("Foi refutada?", "**Não.** É de 2025."),
  ("Qual o tamanho do teste?",
   "Nove anos, com estratificação em quatro regimes: pré-COVID, pandemia, pós-pandemia e "
   "guerra na Ucrânia."),
  ("Que encoder usa?",
   "Testam muitos: VADER, TextBlob, **FinBERT**, **CrudeBERT** (o BERT do petróleo); e "
   "os embeddings GloVe, FastText, BERT, Gemini e LLaMA. Referência: HAR. Teste: McNemar."),
  ("Vale comparar com a nossa?",
   "**É a pesquisa mais próxima da nossa de todas** — mesma commodity que move a PETR4, "
   "escala parecida de corpus, **e o código é público**. **O alvo deles é a nossa "
   "prioridade número 1.**"),
 ]),

 ("Rahimikia e Poon (2021) — volatilidade com embeddings", "PDF baixado", [
  ("Busca notícias?", "**Sim.**"),
  ("Prevê direção ou volatilidade?", "**VOLATILIDADE realizada.**"),
  ("Qual é o número principal?",
   "Não recuperado em detalhe. O ponto do trabalho é **usar embeddings financeiros "
   "próprios em vez de uma cabeça de sentimento**."),
  ("Foi refutada?", "**Não.**"),
  ("Qual o tamanho do teste?", "Não recuperado."),
  ("Que encoder usa?",
   "Um **embedding financeiro construído por eles**, sem classificação de sentimento."),
  ("Vale comparar com a nossa?",
   "**Sim, como caminho.** É a quarta fonte independente indicando que usar a "
   "**compreensão** do texto funciona melhor que usar o **parecer** positivo/negativo. "
   "Lembre: todos os defeitos que achamos no nosso modelo estão na cabeça de sentimento, "
   "nenhum nos embeddings."),
 ]),

 ("Schumaker e Chen (2009) — preço 20 minutos após a notícia", "não baixado (Elsevier)", [
  ("Busca notícias?", "**Sim** — 9.211 notícias e 10,2 milhões de cotações."),
  ("Prevê direção ou volatilidade?",
   "**DIREÇÃO do preço** — mas **vinte minutos depois** de a notícia sair."),
  ("Qual é o número principal?",
   "**71,18% de acurácia direcional**, e retorno simulado de 8,50%. **É o melhor entre "
   "vários esquemas** de particionamento do corpus."),
  ("Foi refutada?", "**Não** — mas mede outra coisa."),
  ("Qual o tamanho do teste?", "**Cinco semanas** de dados."),
  ("Que encoder usa?",
   "**Nenhum** — é de 2009. Saco de palavras, sintagmas nominais e entidades nomeadas, "
   "com uma variante de máquina de vetores de suporte."),
  ("Vale comparar com a nossa?",
   "**Não.** Vinte minutos após a notícia é **reação**, não previsão do pregão seguinte. "
   "É exatamente o nosso horizonte P0, e não o P1. **A lição útil:** o sinal vive no "
   "curtíssimo prazo — terceiro apoio para buscar dados intradiários da PETR4."),
 ]),

 ("Barak, Arjmand e Ortobelli (2017) — retorno e risco em Teerã", "não baixado (Elsevier)", [
  ("Busca notícias?",
   "**Não centralmente.** Trabalham com indicadores de mercado e fundamentos, com "
   "combinação de vários modelos."),
  ("Prevê direção ou volatilidade?", "**Retorno e risco** — não a direção diária a "
   "partir de notícias."),
  ("Qual é o número principal?",
   "**Até 83,6% (retorno) e 88,2% (risco)** — o **máximo entre várias configurações**."),
  ("Foi refutada?", "**Não** — mas o mercado é outro."),
  ("Qual o tamanho do teste?", "Não recuperado."),
  ("Que encoder usa?",
   "**Nenhum.** Ensembles: bagging, boosting, AdaBoost e um meta-classificador."),
  ("Vale comparar com a nossa?",
   "**Não, e já sabemos por experiência própria.** Bolsa de Teerã é menos líquida que a "
   "B3. E **já replicamos a técnica deles** na Seção 4.d: o empilhamento rendeu 53,14%, "
   "52,99% e 53,14% — todos no patamar da classe majoritária. O XGBoost simples com três "
   "atributos deu 54,52% e ganhou de todos."),
 ]),

 ("Nguyen, Shirai e Velcin (2015) — direção de ações dos EUA",
  "não baixado (Elsevier)", [
  ("Busca notícias?", "**Sim**, e também redes sociais."),
  ("Prevê direção ou volatilidade?", "**DIREÇÃO** de ações."),
  ("Qual é o número principal?",
   "**Ganho de 2,1 a 9,8 pontos percentuais** sobre a linha de base que usa só preços."),
  ("Foi refutada?", "**Não.**"),
  ("Qual o tamanho do teste?", "Não recuperado."),
  ("Que encoder usa?",
   "**Nenhum** — usa TSLDA, um método de sentimento **por tópico**."),
  ("Vale comparar com a nossa?",
   "**Sim — É A COMPARAÇÃO MAIS HONESTA DE TODAS.** Eles não reportam acurácia absoluta, "
   "e sim o **ganho** que a notícia acrescenta. **O nosso ganho é de 4,4 pontos "
   "percentuais: está dentro da faixa deles.** Registre-se que já testamos sentimento por "
   "categoria temática, à maneira deles, e **piorou** fora da amostra."),
 ]),

 ("Li et al. (2020) — tendência do preço em Hong Kong", "não baixado (Elsevier)", [
  ("Busca notícias?", "**Sim.**"),
  ("Prevê direção ou volatilidade?", "**Tendência do preço** — é direção."),
  ("Qual é o número principal?",
   "Reportam que superam as linhas de base ao fundir preços e sentimento, sem magnitude "
   "precisa na nossa tabela."),
  ("Foi refutada?", "**Não.**"),
  ("Qual o tamanho do teste?", "Não recuperado."),
  ("Que encoder usa?", "Fusão sequencial em aprendizado profundo."),
  ("Vale comparar com a nossa?",
   "**Parcialmente.** Corrobora a arquitetura de fusão que adotamos — juntar preço, "
   "risco e sentimento numa mesma matriz. A fusão sequencial profunda fica como trabalho "
   "futuro."),
 ]),

 ("Família FinBERT-LSTM (2022–2024) — preço do NASDAQ", "PDFs baixados", [
  ("Busca notícias?", "**Sim** — notícias da Benzinga."),
  ("Prevê direção ou volatilidade?",
   "**NENHUM DOS DOIS.** Preveem o **nível do preço** — quanto vai valer a ação amanhã "
   "em reais e centavos."),
  ("Qual é o número principal?",
   "Anunciam **“acurácia de 0,955”**. Mas reportam **MAE e MAPE**, que são métricas de "
   "**regressão**, com MAPE de 0,045. **Os 0,955 são simplesmente 1 − 0,045.**"),
  ("Foi refutada?", "**Não formalmente** — mas o número é enganoso."),
  ("Qual o tamanho do teste?", "Não recuperado."),
  ("Que encoder usa?", "**FinBERT** acoplado a uma rede LSTM."),
  ("Vale comparar com a nossa?",
   "**Não, e este é o caso mais importante de não confundir.** Prever o **nível** do "
   "preço é trivial: basta responder “o mesmo de hoje” e você acerta com 2% de erro, "
   "porque preço de ação não dá saltos todo dia. Prever a **direção** é o problema "
   "difícil. **Comparar 0,955 com os nossos 54,5% seria erro grosseiro.** Ressalva de "
   "honestidade: não consegui ler o texto integral, então essa é uma dedução a partir das "
   "métricas declaradas — forte, mas a conferir."),
 ]),

 ("FinBERT com SHAP (2025) — direção do S&P 500", "não baixado (MDPI bloqueou)", [
  ("Busca notícias?", "**Sim** — manchetes financeiras."),
  ("Prevê direção ou volatilidade?", "**DIREÇÃO** do preço."),
  ("Qual é o número principal?",
   "Reportam superar linhas de base técnicas e lexicais em várias ações do S&P 500, de "
   "2018 a 2023. Magnitude não recuperada."),
  ("Foi refutada?", "**Não.**"),
  ("Qual o tamanho do teste?", "Seis anos, várias ações."),
  ("Que encoder usa?",
   "**FinBERT** com árvores impulsionadas por gradiente. Acrescentam **SHAP** para "
   "explicar cada decisão do modelo."),
  ("Vale comparar com a nossa?",
   "**Sim — o desenho é quase o nosso**: sentimento somado a atributos de preço e "
   "volatilidade, alimentando uma árvore. **O que eles têm e nós não é a "
   "explicabilidade** — mostrar quais palavras levaram o modelo a decidir. É barato de "
   "acrescentar e a banca gosta."),
 ]),

 ("Horserace de criptomoedas (2024) — volatilidade de cripto",
  "não baixado (Springer)", [
  ("Busca notícias?", "**Sim**, além de indicadores de sentimento de mercado."),
  ("Prevê direção ou volatilidade?", "**VOLATILIDADE.**"),
  ("Qual é o número principal?",
   "**O sentimento NÃO melhora o modelo HAR linear.** Mas melhora com modelos flexíveis "
   "— LightGBM, XGBoost e LSTM."),
  ("Foi refutada?", "**Não.**"),
  ("Qual o tamanho do teste?", "Não recuperado."),
  ("Que encoder usa?", "Indicadores de sentimento de mercado."),
  ("Vale comparar com a nossa?",
   "**Sim, e traz uma hipótese que nos interessa muito.** Nós acrescentamos o sentimento "
   "ao HAR de forma **linear** e não funcionou. Eles mostram que, no caso deles, o efeito "
   "só aparece com modelos que capturam **não linearidade**. **Talvez o nosso resultado "
   "nulo seja de forma funcional, e não de ausência de sinal.** Vale testar."),
 ]),

 ("Silva (2018) — retorno e volatilidade do IBOVESPA", "não baixado (tese)", [
  ("Busca notícias?", "**Sim** — notícias financeiras brasileiras."),
  ("Prevê direção ou volatilidade?", "**As duas** — retorno e volatilidade."),
  ("Qual é o número principal?",
   "**Sentimento linear isolado: R² fora da amostra NEGATIVO** — pior que não usar "
   "modelo nenhum. **O ganho vem da combinação quantílica com pesos variáveis.**"),
  ("Foi refutada?", "**Não.**"),
  ("Qual o tamanho do teste?", "Não recuperado."),
  ("Que encoder usa?", "Análise de sentimento, GARCH e regressão quantílica."),
  ("Vale comparar com a nossa?",
   "**Sim — é a nossa base metodológica.** Já replicamos: a quantílica ponderada rendeu "
   "**+10,9% de R² fora da amostra**. A nossa contribuição é **estender do índice "
   "agregado para um ativo individual**. Note o paralelo: o R² negativo dele com "
   "sentimento linear é o mesmo tipo de resultado do nosso, e reforça a hipótese da "
   "forma funcional."),
 ]),

 ("A NOSSA — Silva (2026), PETR4", "—", [
  ("Busca notícias?", "**Sim** — 205.697 manchetes de cinco portais, de 2018 a 2025."),
  ("Prevê direção ou volatilidade?",
   "**As duas**, no mesmo trabalho — o que é raro."),
  ("Qual é o número principal?",
   "**Direção: 54,5%**, com **ganho de 4,4 pontos percentuais** sobre o modelo só de "
   "preços (p = 0,012). **Volatilidade: coeficiente −0,2924** (p = 0,0002), mas **não "
   "superamos o HAR** (p = 0,64). Melhor recorte: notícia da empresa em 22 dias, +1,77% "
   "(p = 0,0574)."),
  ("Foi refutada?", "**Não** — e nos auditamos a nós mesmos, o que é raro."),
  ("Qual o tamanho do teste?",
   "**497 pregões** no teste de direção; **1.988 pregões** na análise de volatilidade."),
  ("Que encoder usa?",
   "**FinBERT-PT-BR** (Santos et al., 2023), com XGBoost, SVM, GARCH(1,1)-t, HAR e "
   "regressão quantílica."),
  ("O que temos que os outros não têm?",
   "**A auditoria do artefato.** Descobrimos que o modelo rotula 48,5% de tudo como "
   "negativo, que o escore de confiança está em escala errada, que manchetes em caixa "
   "alta o quebram, e que **não existe um único dia, em oito anos, com maioria de "
   "notícias positivas**. **Nenhum dos trabalhos que citam esse modelo reportou nada "
   "disso.**"),
 ]),
]


def main() -> None:
    doc = A.novo_documento()

    A.capa(
        doc,
        titulo="Cada pesquisa, uma a uma",
        subtitulo="As mesmas sete perguntas para cada trabalho de previsão",
        autor="Vanderlei Barbosa da Silva",
        orientador="Orientador: Prof. Dr. Julio Cesar Nievola",
        instituicao="PUCPR — Programa de Pós-Graduação em Informática (PPGIa)",
        descricao="Ficha de leitura de cada pesquisa que tenta prever direção ou "
                  "volatilidade, no mesmo formato de perguntas: busca notícias? prevê o "
                  "quê? qual o número e o que ele mede? foi refutada? qual o tamanho do "
                  "teste? que encoder usa? vale comparar com a nossa? Os PDFs das "
                  "pesquisas de acesso aberto estão na subpasta pesquisas_pdf. "
                  "Elaborado em 20 de agosto de 2026.",
    )

    A.secao(doc, "0", "Antes de começar: duas pesquisas que se confundem")

    A.paragrafo(doc,
        "Vale fixar isto, porque a confusão é fácil e custa caro numa banca:")

    A.tabela_abnt(doc, "1", "Halousková e Bollen são trabalhos completamente diferentes",
        ["", "Halousková e Lyócsa (2025)", "Bollen et al. (2011)"],
        [
            ["Prevê", "VOLATILIDADE", "DIREÇÃO"],
            ["Ativo", "404 ações do S&P 500", "índice DJIA"],
            ["Teste", "11 anos (2010–2021)", "15 PREGÕES"],
            ["Número", "−12,74% de erro", "86,7% de acerto"],
            ["Foi refutada?", "NÃO", "SIM, em 2017"],
        ], fonte="Elaborado pelo autor (2026)")

    A.paragrafo(doc,
        "**Os 15 pregões, os 86,7% e a refutação são todos do Bollen.** E os 86,7% do "
        "Bollen são de **direção**, não de volatilidade.")

    for i, (titulo, situacao_pdf, perguntas) in enumerate(FICHAS, start=1):
        A.secao(doc, str(i), titulo)
        A.paragrafo(doc, f"*Situação do texto: {situacao_pdf}.*", recuo=False)
        for p, r in perguntas:
            A.paragrafo(doc, f"**{p}** {r}")

    A.secao(doc, str(len(FICHAS) + 1), "Como usar estas fichas")

    A.paragrafo(doc,
        "Se o Professor Emerson perguntar por qualquer uma das pesquisas, a resposta "
        "está nas sete perguntas. As três que mais importam guardar de cor:")

    A.lista(doc, [
        "**Halousková e Lyócsa** — volatilidade, 404 ações, 11 anos, **nos supera**, "
        "não foi refutada. O sentimento deles é sobre **indicadores macro agendados**.",
        "**Bollen** — direção, índice, **15 pregões**, 86,7%, **refutado em 2017**.",
        "**Nguyen** — a comparação honesta: **ganho de 2 a 10 pontos percentuais** sobre "
        "só-preços. **O nosso é 4,4. Estamos na faixa.**",
    ])

    doc.save(SAIDA)
    print(f"[OK] {SAIDA}")
    print(f"     {len(FICHAS)} fichas, 7 perguntas cada")


if __name__ == "__main__":
    main()
