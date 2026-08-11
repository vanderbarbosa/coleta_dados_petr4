# -*- coding: utf-8 -*-
# ==============================================================================
#   Texto em registro ACADÊMICO do experimento de adaptação de domínio,
#   pronto para ser revisado, adaptado e incorporado à dissertação.
#
#   Saída: orientacoes/TEXTO_DISSERTACAO_ADAPTACAO_DOMINIO.docx
#
#   Registro: impessoal, ABNT, terceira pessoa — convenção da área no Brasil.
#   Sem analogias e sem didatismo: o público é a banca.
# ==============================================================================
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(RAIZ / "src" / "comum"))

import abnt_docx as A  # noqa: E402

FONTE = "Elaborado pelo autor (2026)"
SAIDA = AQUI / "TEXTO_DISSERTACAO_ADAPTACAO_DOMINIO.docx"


def main() -> None:
    doc = A.novo_documento()

    A.capa(
        doc,
        titulo="Adaptação de domínio do classificador de sentimento",
        subtitulo="Texto em registro acadêmico, para incorporação à dissertação",
        autor="Vanderlei Barbosa da Silva",
        orientador="Orientador: Prof. Dr. Julio Cesar Nievola",
        instituicao="PUCPR — Programa de Pós-Graduação em Informática (PPGIa)",
        descricao="Redação das seções de método, resultados e discussão referentes ao "
                  "experimento de adaptação de domínio conduzido em agosto de 2026. O "
                  "texto está em registro acadêmico e deve ser revisado e ajustado ao "
                  "estilo dos demais capítulos antes da incorporação definitiva.",
    )

    # ── Nota de uso ──────────────────────────────────────────────────────────
    A.secao(doc, "1", "Nota sobre o uso deste texto")
    A.paragrafo(doc,
        "As seções que seguem estão redigidas no registro impessoal usual da área e "
        "numeradas de forma independente, para facilitar a realocação nos capítulos "
        "correspondentes da dissertação. A numeração das tabelas deve ser ajustada à "
        "sequência do capítulo de destino.")
    A.paragrafo(doc,
        "Recomenda-se revisar o texto e ajustá-lo ao estilo já estabelecido nos demais "
        "capítulos, sobretudo quanto ao uso de primeira pessoa do plural ou de construções "
        "impessoais, que devem ser uniformes ao longo do trabalho.")

    # ── MÉTODO ───────────────────────────────────────────────────────────────
    A.secao(doc, "2", "Método — adaptação de domínio e desenho experimental")

    A.secao(doc, "2.1", "Motivação", nivel=2)
    A.paragrafo(doc,
        "A avaliação do FinBERT-PT-BR contra o conjunto-ouro construído para esta pesquisa "
        "resultou em acurácia de 0,580 e coeficiente kappa de Cohen de 0,371, valores "
        "inferiores aos 0,760 e 0,730 de F1-Score relatados por Santos, Bianchi e Costa "
        "(2023). A decomposição do erro indicou que a discrepância não decorre da "
        "dificuldade intrínseca dos casos avaliados nem do recorte por ativo único, mas "
        "concentra-se na fronteira da classe neutra: descartada essa classe, a discriminação "
        "entre as classes positiva e negativa atinge acurácia de 0,783 e kappa de 0,565.")
    A.paragrafo(doc,
        "Duas evidências apontaram para uma incompatibilidade de representação, e não de "
        "calibração. A primeira é a distribuição de classes: no conjunto de treinamento "
        "original a classe neutra correspondia a 27,8% dos exemplos, ao passo que no corpus "
        "desta pesquisa ela representa 41,3% — configuração compatível com deslocamento de "
        "prior. A segunda é o insucesso de intervenções de pós-processamento: nem a "
        "atribuição da classe neutra por limiar de confiança nem a reponderação pelas "
        "probabilidades a priori recuperaram desempenho relevante.")
    A.paragrafo(doc,
        "Diante disso, adotou-se a hipótese de que a adaptação do modelo de linguagem ao "
        "subdomínio de interesse poderia melhorar a representação e, por consequência, a "
        "classificação. A hipótese encontra respaldo no próprio trabalho de referência, em "
        "que o pré-treinamento continuado sobre 1,4 milhão de textos financeiros reduziu a "
        "perplexidade de 1,51 para 1,24, e nas direções de pesquisa futura ali apontadas, "
        "que incluem explicitamente a aplicação da metodologia a setores específicos da "
        "bolsa de valores.")

    A.secao(doc, "2.2", "Corpus e procedimento de adaptação", nivel=2)
    A.paragrafo(doc,
        "O corpus de adaptação foi constituído pelas 205.697 notícias coletadas para esta "
        "pesquisa, referentes ao período de 2018 a 2026. Cada registro foi formado pela "
        "concatenação do título e do resumo, resultando em textos com mediana de 39 "
        "palavras — extensão equivalente à dos exemplos empregados no treinamento original, "
        "cuja mediana é igualmente de 39 palavras. Reservaram-se 10.000 textos para "
        "avaliação, não utilizados no ajuste.")
    A.paragrafo(doc,
        "O procedimento replicou os hiperparâmetros descritos por Santos, Bianchi e Costa "
        "(2023): modelagem de linguagem mascarada com probabilidade de ocultação de 15%, "
        "conforme Devlin et al. (2018), taxa de aprendizado de 2 × 10⁻⁵, seguindo a "
        "recomendação de Sun et al. (2019), e duas épocas de treinamento. O comprimento "
        "máximo de sequência foi fixado em 128 tokens, suficiente para acomodar a "
        "distribuição observada. A avaliação empregou a perplexidade (CHEN; BEEFERMAN; "
        "ROSENFELD, 1998), métrica intrínseca que dispensa anotação humana.")
    A.paragrafo(doc,
        "Registre-se uma limitação do ponto de partida. O repositório público disponibiliza "
        "apenas o classificador de sentimento, cuja arquitetura declarada é "
        "BertForSequenceClassification; o modelo de linguagem que o antecede não foi "
        "publicado. A adaptação partiu, portanto, do classificador, com reinicialização da "
        "camada de predição de tokens.")

    A.secao(doc, "2.3", "Desenho experimental e controle", nivel=2)
    A.paragrafo(doc,
        "A comparação direta entre o modelo publicado e o modelo adaptado é confundida por "
        "uma diferença no volume de supervisão: o primeiro foi ajustado sobre os 503 textos "
        "anotados por Santos, Bianchi e Costa (2023) com validação cruzada, ao passo que o "
        "segundo utilizou 352 desses textos, com os demais reservados para validação. "
        "Eventual queda de desempenho poderia, assim, ser atribuída indistintamente à "
        "adaptação ou à redução do conjunto de treinamento.")
    A.paragrafo(doc,
        "Para dissociar os dois efeitos, introduziu-se uma terceira condição experimental, "
        "idêntica à segunda em tudo exceto na adaptação. As três condições avaliadas foram:")
    A.tabela_abnt(doc, 1, "Condições experimentais",
        ["Condição", "Adaptação de domínio", "Exemplos de ajuste fino"],
        [
            ["A — modelo publicado", "Não", "503, com validação cruzada"],
            ["B — modelo adaptado", "Sim", "352"],
            ["C — controle", "Não", "352, mesmo protocolo de B"],
        ], fonte=FONTE)
    A.paragrafo(doc,
        "As condições B e C compartilham a mesma partição dos dados, obtida com semente "
        "fixa, o mesmo protocolo de ajuste fino — descongelamento gradual das camadas de "
        "codificação, taxa de aprendizado de 5 × 10⁻⁶ e onze épocas, conforme Santos, "
        "Bianchi e Costa (2023) — e a mesma avaliação. O contraste entre B e C isola, "
        "portanto, o efeito da adaptação de domínio.")
    A.paragrafo(doc,
        "A significância estatística das diferenças foi estimada por reamostragem *bootstrap* "
        "(EFRON, 1992) com 10.000 repetições, calculando-se a diferença entre condições na "
        "mesma reamostra, procedimento adequado à comparação de modelos avaliados sobre os "
        "mesmos itens.")

    # ── RESULTADOS ───────────────────────────────────────────────────────────
    A.secao(doc, "3", "Resultados")

    A.secao(doc, "3.1", "Efeito sobre a modelagem de linguagem", nivel=2)
    A.paragrafo(doc,
        "A adaptação reduziu substancialmente a perplexidade sobre o subconjunto reservado. "
        "Como referência válida adotou-se o BERTimbau (SOUZA; NOGUEIRA; LOTUFO, 2020), que "
        "dispõe de camada de predição de tokens treinada, avaliado sobre o mesmo subconjunto.")
    A.tabela_abnt(doc, 2, "Perplexidade sobre 10.000 textos não utilizados no ajuste",
        ["Modelo", "Perplexidade"],
        [["BERTimbau", "7,195"],
         ["Modelo adaptado ao subdomínio", "3,669"],
         ["Redução", "49,0%"]],
        fonte=FONTE)
    A.paragrafo(doc,
        "A redução de 49,0% indica que o procedimento cumpriu o objetivo declarado: o modelo "
        "passou a representar melhor a distribuição lexical do subdomínio. Ressalve-se que os "
        "valores absolutos não são comparáveis aos relatados por Santos, Bianchi e Costa "
        "(2023), obtidos sobre corpus distinto.")

    A.secao(doc, "3.2", "Efeito sobre a classificação", nivel=2)
    A.paragrafo(doc,
        "O ganho na modelagem de linguagem não se converteu em ganho na tarefa a jusante. Ao "
        "contrário, observou-se degradação.")
    A.tabela_abnt(doc, 3, "Desempenho no conjunto-ouro (n = 300)",
        ["Condição", "Acurácia", "F1-macro", "IC 95% do F1", "Kappa"],
        [
            ["A — modelo publicado", "0,580", "0,579", "[0,521 ; 0,634]", "0,371"],
            ["B — modelo adaptado", "0,547", "0,528", "[0,470 ; 0,584]", "0,309"],
            ["C — controle", "0,590", "0,584", "[0,527 ; 0,638]", "0,378"],
        ], fonte=FONTE)
    A.tabela_abnt(doc, 4, "Comparações pareadas por bootstrap (10.000 reamostras)",
        ["Contraste", "Δ F1-macro", "IC 95%", "p-valor", "Significância"],
        [
            ["C − B (efeito da adaptação)", "+0,056", "[+0,008 ; +0,106]", "0,022",
             "**significativa**"],
            ["C − A (protocolo próprio × publicado)", "+0,005", "[−0,023 ; +0,032]", "0,692",
             "não significativa"],
            ["A − B", "+0,051", "[+0,001 ; +0,102]", "0,048", "significativa"],
        ], fonte=FONTE)
    A.paragrafo(doc,
        "O contraste entre as condições C e B é estatisticamente significativo ao nível de 5%: "
        "a adaptação de domínio degradou o desempenho de classificação em 0,056 de F1-macro. "
        "O contraste entre C e A, por sua vez, não é significativo, o que indica que o "
        "protocolo de ajuste fino aqui implementado reproduz o desempenho do modelo publicado "
        "utilizando menor volume de supervisão — resultado que valida a implementação e "
        "confere confiabilidade ao contraste principal.")

    A.secao(doc, "3.3", "Localização do efeito", nivel=2)
    A.paragrafo(doc,
        "A análise por classe revela que a degradação não se distribui uniformemente.")
    A.tabela_abnt(doc, 5, "Revocação por classe",
        ["Classe", "A", "B", "C", "B − C"],
        [["Negativa", "0,750", "0,750", "0,713", "+0,037"],
         ["Neutra", "0,532", "0,621", "0,621", "0,000"],
         ["**Positiva**", "0,500", "**0,281**", "**0,448**", "**−0,167**"]],
        fonte=FONTE)
    A.paragrafo(doc,
        "A revocação da classe positiva reduz-se de 0,448 na condição de controle para 0,281 "
        "na condição adaptada, enquanto as classes negativa e neutra permanecem "
        "essencialmente inalteradas. A degradação, portanto, é específica à classe positiva — "
        "que já constituía a categoria de pior desempenho antes da intervenção.")

    # ── DISCUSSÃO ────────────────────────────────────────────────────────────
    A.secao(doc, "4", "Discussão")
    A.paragrafo(doc,
        "Os resultados configuram um caso de esquecimento catastrófico. O pré-treinamento "
        "continuado sobre o corpus do subdomínio sobrescreveu parte da representação "
        "específica da tarefa de classificação de sentimento, instalada no corpo do modelo "
        "durante o ajuste fino original, e os 352 exemplos supervisionados empregados na "
        "reconstituição não foram suficientes para recuperá-la.")
    A.paragrafo(doc,
        "O fenômeno é reconhecido na literatura de aprendizado por transferência e motivou, "
        "no trabalho de referência, a adoção do descongelamento gradual das camadas de "
        "codificação. Cumpre observar que essa técnica foi aqui empregada e ainda assim não "
        "preveniu a degradação, o que sugere que o esquecimento ocorreu durante a etapa de "
        "modelagem de linguagem, e não durante o ajuste supervisionado subsequente.")
    A.paragrafo(doc,
        "A concentração do efeito na classe positiva admite interpretação coerente com o "
        "domínio. O corpus de adaptação é composto majoritariamente por notícias de tom "
        "informativo ou negativo, refletindo o perfil editorial da cobertura do setor no "
        "período; o pré-treinamento continuado sobre essa distribuição tende a reforçar "
        "regularidades lexicais associadas a esses registros, em detrimento da sensibilidade "
        "aos marcadores de valência positiva, já escassos no material original.")
    A.paragrafo(doc,
        "A leitura conjunta dos dois resultados constitui a principal contribuição deste "
        "experimento: **a melhoria da modelagem de linguagem, medida por redução de 49,0% na "
        "perplexidade, foi acompanhada de degradação estatisticamente significativa da tarefa "
        "a jusante.** O achado qualifica a recomendação, corrente na literatura, de que a "
        "adaptação de domínio constitua etapa padrão em aplicações especializadas — ao menos "
        "quando o ponto de partida já é um modelo ajustado à tarefa e o volume de supervisão "
        "disponível para reconstituição é reduzido.")

    # ── LIMITAÇÕES ───────────────────────────────────────────────────────────
    A.secao(doc, "5", "Limitações")
    A.lista(doc, [
        "**Ponto de partida.** A adaptação partiu do classificador publicado, e não do modelo "
        "de linguagem que o antecede, indisponível publicamente. A camada de predição de "
        "tokens foi reinicializada, o que introduz uma etapa de reaprendizagem não presente "
        "no procedimento original.",
        "**Volume de supervisão.** As condições B e C dispuseram de 352 exemplos anotados, "
        "contra os 503 empregados na condição A. Embora o contraste entre C e A não seja "
        "significativo, não se pode excluir que volume superior de supervisão permitisse "
        "recuperar a representação perdida.",
        "**Dimensão do conjunto de avaliação.** Com 300 itens, o intervalo de confiança do "
        "F1-macro tem amplitude aproximada de 0,11, o que limita a detecção de diferenças "
        "inferiores a cinco pontos percentuais.",
        "**Anotador único.** O conjunto-ouro foi anotado por um único avaliador, sem segunda "
        "anotação e, por conseguinte, sem métrica de concordância. As medidas reportadas "
        "expressam a distância entre o classificador e esse avaliador, e não entre o "
        "classificador e um padrão validado.",
        "**Uma única configuração de hiperparâmetros.** Testou-se uma combinação de taxa de "
        "aprendizado, número de épocas e probabilidade de mascaramento, replicada do trabalho "
        "de referência. Configurações mais conservadoras poderiam mitigar o esquecimento.",
    ])

    # ── REFERÊNCIAS ──────────────────────────────────────────────────────────
    A.referencias(doc, "6", [
        "CHEN, S. F.; BEEFERMAN, D.; ROSENFELD, R. Evaluation metrics for language models. "
        "1998.",

        "DEVLIN, J.; CHANG, M.-W.; LEE, K.; TOUTANOVA, K. BERT: pre-training of deep "
        "bidirectional transformers for language understanding. arXiv:1810.04805, 2018.",

        "EFRON, B. Bootstrap methods: another look at the jackknife. In: Breakthroughs in "
        "statistics. New York: Springer, 1992. p. 569-593.",

        "SANTOS, L. L.; BIANCHI, R. A. C.; COSTA, A. H. R. FinBERT-PT-BR: análise de "
        "sentimentos de textos em português do mercado financeiro. In: BRAZILIAN WORKSHOP ON "
        "ARTIFICIAL INTELLIGENCE IN FINANCE (BWAIF), 2., 2023. Anais [...]. Porto Alegre: "
        "SBC, 2023. p. 144-155.",

        "SOUZA, F.; NOGUEIRA, R.; LOTUFO, R. BERTimbau: pretrained BERT models for Brazilian "
        "Portuguese. In: BRAZILIAN CONFERENCE ON INTELLIGENT SYSTEMS, 2020. p. 403-417.",

        "SUN, C.; QIU, X.; XU, Y.; HUANG, X. How to fine-tune BERT for text classification? "
        "In: CHINA NATIONAL CONFERENCE ON CHINESE COMPUTATIONAL LINGUISTICS, 2019. "
        "p. 194-206.",
    ])

    doc.save(SAIDA)
    print(f"OK -> {SAIDA.name}")


if __name__ == "__main__":
    main()
