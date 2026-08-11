# -*- coding: utf-8 -*-
# ==============================================================================
#   Gera a versão ABNT (.docx) do diagnóstico de desempenho.
#
#   Responde a duas perguntas:
#     1. Por que o desempenho parece baixo, se todos usam o encoder sem alterá-lo?
#     2. O que exatamente está baixo — a classificação da notícia, o índice de
#        sentimento ou a direção do preço?
#
#   Todos os números vêm de scripts executáveis em src/sentimento/ e dos JSON
#   correspondentes em Mestrado_PETR4/. Nada foi estimado ou arredondado à mão.
# ==============================================================================
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(RAIZ / "src" / "comum"))

import abnt_docx as A  # noqa: E402

FONTE = "Elaborado pelo autor (2026)"
SAIDA = AQUI / "DIAGNOSTICO_DESEMPENHO_PETR4.docx"


def main() -> None:
    doc = A.novo_documento()

    A.capa(
        doc,
        titulo="Diagnóstico de desempenho do classificador de sentimento",
        subtitulo="O que está baixo, por quê, e o que adianta melhorar",
        autor="Vanderlei Barbosa da Silva",
        orientador="Orientador: Prof. Dr. Julio Cesar Nievola",
        instituicao="PUCPR — Programa de Pós-Graduação em Informática (PPGIa)",
        descricao="Documento elaborado em 8 de agosto de 2026, em resposta a duas "
                  "perguntas: por que o desempenho do FinBERT-PT-BR no corpus da "
                  "dissertação parece baixo, se os demais trabalhos o utilizam sem "
                  "alteração; e o que exatamente está baixo — a classificação da "
                  "notícia, o índice de sentimento ou a previsão de direção do preço. "
                  "Todos os resultados são reproduzíveis pelos scripts indicados.",
    )

    # ─── 1 Síntese ───────────────────────────────────────────────────────────
    A.secao(doc, "1", "Síntese")
    A.paragrafo(doc,
        "As duas perguntas têm a mesma raiz: a suposição de que existe um único número "
        "que resume o desempenho da pesquisa. Não existe. Há **três camadas encadeadas**, "
        "cada uma com métrica própria, e o diagnóstico só faz sentido quando elas são "
        "separadas.")
    A.tabela_abnt(doc, 1, "As três camadas e o veredito de cada uma",
        ["Camada", "O que mede", "Resultado medido", "Veredito"],
        [
            ["1. Classificação da notícia",
             "Acurácia do FinBERT-PT-BR contra gabarito humano (n = 300)",
             "0,580 · F1 0,579 · kappa 0,371", "**MEDIANA** — e o erro é localizado"],
            ["2. Índice de sentimento (ISM)",
             "Agregação diária/mensal das classificações",
             "Viés de 87% no nível (−0,345 contra −0,044 calibrado)",
             "**NÃO é baixo — é DESLOCADO**, e já foi corrigido"],
            ["3. Direção do preço",
             "Previsão de alta/baixa da PETR4",
             "49,7% com o modelo; 52,8% do baseline ingênuo",
             "**ESTE é o que está de fato baixo**"],
        ], fonte=FONTE)
    A.paragrafo(doc,
        "E há um quarto resultado, decorrente do teste do teto (Seção 6), que reordena as "
        "prioridades da dissertação: **melhorar o classificador é inútil para a direção e "
        "promissor para a volatilidade**.")

    # ─── 2 Premissa ──────────────────────────────────────────────────────────
    A.secao(doc, "2", "A premissa: baixo em relação a quê?")
    A.paragrafo(doc,
        "A pergunta pressupõe que os demais trabalhos obtêm resultados melhores. "
        "**Não obtêm — eles não medem.** A verificação foi feita trabalho a trabalho.")
    A.tabela_abnt(doc, 2, "Quem usa o FinBERT-PT-BR e quem o valida",
        ["Trabalho", "Usa o modelo?", "Mede a acurácia?"],
        [
            ["jp-alves/prio3-sentiment (PRIO3)", "Sim", "Não — nenhum gabarito"],
            ["Analise-de-Sentimento-IC (ICMC/USP)", "Sim", "Não — nenhum gabarito"],
            ["IagoErrera/scrap-fin", "Sim", "Não — nenhum gabarito"],
            ["Błoch, Santana e Amantino (2026)", "Sim",
             "Comparou com historiador, mas não publicou métricas"],
            ["Teles e Figueiredo (2025)", "Não avaliou o modelo", "—"],
            ["Abílio, Coelho e Silva (2024)", "Não (tarefa de NER)", "—"],
            ["Santos, Bianchi e Costa (2023)", "Criou o modelo",
             "Sim — 0,76, no conjunto de teste dos próprios autores"],
            ["Esta dissertação", "Sim", "**Sim — 0,58, medido**"],
        ], fonte=FONTE)
    A.paragrafo(doc,
        "**Existem apenas duas medições publicadas do FinBERT-PT-BR: a do próprio autor e a "
        "desta dissertação.** Os demais trabalhos aplicam o modelo pressupondo que ele "
        "funciona. Não há, portanto, um “desempenho dos outros” contra o qual estejamos "
        "abaixo. A pergunta correta não é por que somos piores, e sim por que a nossa "
        "medição difere da que o autor reporta.")

    A.secao(doc, "2.1", "Os 0,58 são ruins em termos absolutos?", nivel=2)
    A.tabela_abnt(doc, 3, "Referências de comparação para a acurácia",
        ["Referência", "Acurácia"],
        [
            ["Acaso (três classes)", "0,333"],
            ["Baseline: sempre a classe mais frequente (Neutral, 124/300)", "0,413"],
            ["**FinBERT-PT-BR no corpus da dissertação**", "**0,580**"],
            ["Santos (2023), notícias gerais de mercado", "0,760"],
        ], fonte=FONTE)
    A.paragrafo(doc,
        "O ganho sobre o baseline de maioria é de **16,7 pontos percentuais**, e o kappa de "
        "0,371 corresponde a concordância razoável na escala de Landis e Koch. O modelo está "
        "capturando estrutura real. O que exige explicação é a distância para os 0,76.")

    # ─── 3 O que não explica ─────────────────────────────────────────────────
    A.secao(doc, "3", "O que NÃO explica a diferença")
    A.paragrafo(doc,
        "Duas hipóteses plausíveis foram testadas e descartadas. O registro delas importa: "
        "sem eliminá-las, qualquer explicação seria especulação.")

    A.secao(doc, "3.1", "Hipótese 1 — Santos descartou os casos difíceis", nivel=2)
    A.paragrafo(doc,
        "Santos descartou **497 de 1.000 textos (49,7%)** — os classificados como “não se "
        "aplica” ou sem concordância entre anotadores. O conjunto de teste dele é, por "
        "construção, o subconjunto de notícias que **têm** sentimento claro. Era a explicação "
        "mais óbvia. Testou-se com a coluna de confiança do anotador como aproximação.")
    A.tabela_abnt(doc, 4, "Desempenho por confiança declarada do anotador",
        ["Recorte", "n", "Acurácia", "F1-macro", "Kappa"],
        [
            ["Todos", "300", "0,580", "0,579", "0,371"],
            ["Somente confiança “Alta”", "233", "**0,597**", "0,595", "0,393"],
            ["Confiança “Média”", "57", "0,526", "0,521", "0,284"],
        ], fonte=FONTE)
    A.paragrafo(doc,
        "**O ganho é de apenas 1,7 ponto percentual.** Reter somente os casos fáceis quase não "
        "altera o resultado. A hipótese não se sustenta. Registre-se a ressalva: a aproximação "
        "não é idêntica ao filtro de Santos, que descartou por **discordância entre dois "
        "anotadores**, enquanto aqui há apenas a autoavaliação de um.")

    A.secao(doc, "3.2", "Hipótese 2 — o recorte por ativo único", nivel=2)
    A.tabela_abnt(doc, 5, "Desempenho por relevância da notícia ao ativo",
        ["Recorte", "n", "Acurácia", "Kappa"],
        [
            ["Relevante para a PETR4", "111", "0,586", "0,378"],
            ["Não relevante", "189", "0,577", "0,358"],
        ], fonte=FONTE)
    A.paragrafo(doc,
        "**Diferença de 0,9 ponto percentual.** O modelo erra igualmente em notícias sobre a "
        "Petrobras e em notícias gerais do setor. A hipótese não se sustenta isoladamente.")

    # ─── 4 O que explica ─────────────────────────────────────────────────────
    A.secao(doc, "4", "O que EXPLICA a diferença")
    A.secao(doc, "4.1", "É a fronteira da classe neutra", nivel=2)
    A.tabela_abnt(doc, 6, "Revocação e precisão por classe",
        ["Classe verdadeira", "n", "Revocação", "Precisão"],
        [
            ["Negative", "80", "**0,750**", "0,531"],
            ["Neutral", "124", "0,532", "0,635"],
            ["Positive", "96", "**0,500**", "0,578"],
        ], fonte=FONTE)
    A.paragrafo(doc, "O teste decisivo consiste em descartar a classe neutra dos dois lados:")
    A.tabela_abnt(doc, 7, "Desempenho com e sem a classe neutra",
        ["Tarefa", "n", "Acurácia", "Kappa"],
        [
            ["Três classes (configuração atual)", "300", "0,580", "0,371"],
            ["**Somente Positivo × Negativo**", "138", "**0,783**", "**0,565**"],
        ], fonte=FONTE)
    A.paragrafo(doc,
        "**O modelo distingue positivo de negativo com 78,3% de acurácia. O que ele não "
        "consegue é decidir se uma manchete é neutra.** A estrutura dos erros confirma: dos "
        "126 erros, **113 (90%) envolvem a classe Neutral** em alguma das pontas.")
    A.tabela_abnt(doc, 8, "Principais confusões",
        ["Rótulo humano", "Predição do modelo", "Casos"],
        [["Neutral", "Negative", "32"], ["Positive", "Neutral", "27"],
         ["Neutral", "Positive", "26"], ["Positive", "Negative", "21"]],
        fonte=FONTE)

    A.secao(doc, "4.2", "A causa estrutural: mudança de prior", nivel=2)
    A.tabela_abnt(doc, 9, "Distribuição de classes: treino, realidade e predição",
        ["Classe", "Treino de Santos", "Nossa realidade", "O modelo prediz"],
        [
            ["Negative", "**40,4%**", "26,7%", "37,7%"],
            ["Neutral", "**27,8%** (a menor)", "**41,3%** (a maior)", "34,7%"],
            ["Positive", "31,8%", "32,0%", "27,7%"],
        ], fonte=FONTE)
    A.paragrafo(doc,
        "**No conjunto de treino de Santos, “neutro” era a classe mais rara; no corpus desta "
        "dissertação, é a mais comum.** É consequência direta do processo de anotação: ao "
        "descartar metade dos casos, inclusive os “não se aplica”, foram removidas justamente "
        "as notícias que não dizem nada. O modelo foi treinado num universo em que quase toda "
        "notícia tem carga informacional, e é aplicado a um universo em que a maioria não tem. "
        "Ele permanece decidido, e por isso erra para os extremos.")
    A.paragrafo(doc,
        "As predições do modelo (37,7% de negativas) situam-se **entre** o prior de treino "
        "(40,4%) e a realidade observada (26,7%), muito mais próximas do treino. É a "
        "assinatura clássica de mudança de prior — e é exatamente o que a correção por "
        "*Adjusted Classify and Count* trata no agregado.")

    A.secao(doc, "4.3", "Evidências de apoio", nivel=2)
    A.tabela_abnt(doc, 10, "Calibração da confiança do modelo",
        ["Faixa de confiança", "n", "Acurácia"],
        [["Até 0,60", "92 (31%)", "**0,424**"], ["0,60 a 0,80", "140", "0,650"],
         ["0,80 a 0,90", "68", "0,647"], ["Acima de 0,90", "**0**", "—"]],
        fonte=FONTE)
    A.paragrafo(doc,
        "A confiança máxima observada nas 300 manchetes é **0,856**, e **nenhuma** ultrapassa "
        "0,90. Num problema de três classes, um modelo confiante produziria muitos casos acima "
        "de 0,95. Este nunca chega lá — sinal de incompatibilidade de domínio, e não de "
        "aleatoriedade. Há aí, porém, uma boa notícia: a confiança **discrimina**, e portanto "
        "serve como indicador de qualidade item a item.")
    A.tabela_abnt(doc, 11, "Desempenho por categoria da taxonomia",
        ["Categoria", "n", "Acurácia", "Kappa"],
        [["CAT6_Governanca", "15", "0,733", "0,559"],
         ["CAT2_Mercado_Petroleo", "79", "0,646", "0,468"],
         ["CAT7_Macro_Energia", "43", "0,605", "0,393"],
         ["CAT1_Empresa", "98", "0,571", "0,362"],
         ["**CAT3_Geopolitica**", "54", "**0,481**", "**0,216**"]],
        fonte=FONTE)
    A.paragrafo(doc,
        "Geopolítica é o pior caso, e isso é coerente: é onde a inversão “notícia ruim é boa "
        "para a produtora de petróleo” se manifesta com mais força, e é justamente o "
        "vocabulário que um modelo de mercado geral não domina.")

    # ─── 5 Consertos ─────────────────────────────────────────────────────────
    A.secao(doc, "5", "Os consertos de pós-processamento não funcionam")
    A.paragrafo(doc,
        "Antes de justificar intervenções custosas, testaram-se dois pós-processamentos "
        "óbvios e baratos.")
    A.tabela_abnt(doc, 12, "Conserto 1 — confiança baixa convertida em Neutral",
        ["Limiar", "Acurácia", "F1-macro", "Kappa", "Revocação do neutro"],
        [["sem conserto", "0,580", "0,579", "0,371", "0,532"],
         ["abaixo de 0,65", "**0,587**", "0,563", "0,360", "0,750"],
         ["abaixo de 0,80", "0,497", "0,422", "0,186", "0,847"]],
        fonte=FONTE)
    A.paragrafo(doc,
        "Ganha-se 0,7 ponto percentual de acurácia, mas o **F1-macro cai** de 0,579 para 0,563 "
        "e o **kappa cai** de 0,371 para 0,360. Sobe a revocação do neutro às custas das outras "
        "duas classes. Não compensa.")
    A.paragrafo(doc,
        "O **conserto 2**, de reponderação pelo prior real, piora todas as métricas (acurácia "
        "0,573, F1 0,571, kappa 0,354). Registre-se, porém, que **esse teste é inconclusivo**: "
        "a reponderação correta exige a distribuição *softmax* completa, e o Script 03 grava "
        "apenas o rótulo de maior probabilidade e sua confiança. A aproximação empregada pode "
        "ser a causa da piora, e a conclusão depende de re-execução com os *logits* salvos.")
    A.paragrafo(doc,
        "**A leitura desse resultado negativo é o que há de mais útil no diagnóstico.** Se "
        "ajustar a saída não resolve, o problema não está na **calibração** — está na "
        "**representação**. O modelo genuinamente não separa, no espaço de atributos que "
        "aprendeu, manchete neutra de manchete carregada neste domínio.")

    # ─── 6 O teto ────────────────────────────────────────────────────────────
    A.secao(doc, "6", "O teste do teto: o que adianta melhorar o classificador?")
    A.paragrafo(doc,
        "O conjunto-ouro permite um experimento que normalmente não é possível. O rótulo "
        "humano funciona como um **classificador perfeito por construção** — é o limite "
        "superior do que qualquer encoder poderia atingir neste corpus. Basta executar a mesma "
        "regra de decisão duas vezes, uma com o sentimento do modelo e outra com o humano. A "
        "diferença é exatamente o ganho máximo disponível.")
    A.tabela_abnt(doc, 13, "Previsão de direção: modelo contra teto teórico",
        ["Fonte do sentimento", "n (pregões)", "Taxa de acerto", "p-valor", "IC 95%"],
        [["Modelo (acurácia 0,58)", "183", "49,7%", "1,000", "[42,3% ; 57,2%]"],
         ["**Humano (teto teórico)**", "165", "**50,9%**", "0,876", "[43,0% ; 58,8%]"],
         ["Baseline “sempre alta” no período", "—", "52,8%", "—", "—"]],
        fonte=FONTE)
    A.paragrafo(doc,
        "**O ganho de um classificador perfeito na previsão de direção é de 1,2 ponto "
        "percentual — e ambos ficam abaixo do baseline ingênuo de “sempre alta”.** O gargalo "
        "da direção não é o classificador. Nenhuma melhoria no encoder resolveria isso.")
    A.tabela_abnt(doc, 14, "Volatilidade: mediana do |retorno| em D+1",
        ["Fonte do sentimento", "Após notícia negativa", "Após notícia positiva", "Razão", "p-valor"],
        [["Modelo", "1,0802% (n=113)", "1,1193% (n=83)", "0,97×", "0,502"],
         ["**Humano (teto)**", "**1,2051% (n=80)**", "1,0002% (n=96)", "**1,20×**", "**0,098**"]],
        fonte=FONTE)
    A.paragrafo(doc,
        "**Aqui o quadro se inverte.** Com o rótulo do modelo o sinal não aparece (p = 0,502). "
        "Com o rótulo humano ele aparece, na direção esperada e com magnitude relevante — "
        "notícias negativas são seguidas de movimento 20% maior. **Ressalva obrigatória: "
        "p = 0,098 não é significativo ao nível de 5%; trata-se de tendência, não de "
        "resultado.** Mas o contraste entre 0,502 e 0,098 sugere que o ruído do classificador "
        "está apagando um sinal que existe.")
    A.paragrafo(doc,
        "**Consequência para a dissertação:** os investimentos em comitê de modelos e em "
        "adaptação de domínio devem ser justificados pelo eixo da **volatilidade**, e não pela "
        "promessa de melhorar a previsão de direção — que, pelo teste do teto, não ocorreria.")

    # ─── 7 Camada 2 ──────────────────────────────────────────────────────────
    A.secao(doc, "7", "A camada intermediária: o índice de sentimento")
    A.paragrafo(doc,
        "O índice não está **baixo** — está **deslocado**, o que é um problema diferente e "
        "corrigível. A correção por *Adjusted Classify and Count* (FORMAN, 2008) usa a matriz "
        "de confusão medida no gabarito para recuperar as proporções verdadeiras de classe.")
    A.tabela_abnt(doc, 15, "Índice de sentimento antes e depois da calibração",
        ["", "Bruto", "Calibrado", "Diferença"],
        [["Proporção Negative", "48,5%", "31,2%", "−17,3 pp"],
         ["Proporção Neutral", "37,5%", "41,9%", "+4,4 pp"],
         ["Proporção Positive", "14,0%", "26,8%", "+12,9 pp"],
         ["**ISM**", "**−0,3450**", "**−0,0439**", "**+0,3011**"]],
        fonte=FONTE)
    A.paragrafo(doc,
        "O viés corresponde a **87% do valor bruto**, e o intervalo de confiança de 95% obtido "
        "por reamostragem do gabarito — de −0,2250 a +0,1857 — **não contém** o valor bruto, o "
        "que torna o viés estatisticamente distinguível de zero. Na série mensal, **49 dos 96 "
        "meses trocam de sinal**. A conclusão substantiva é que **o corpus de notícias sobre a "
        "Petrobras não é predominantemente negativo: a negatividade era artefato do "
        "classificador**.")
    A.paragrafo(doc,
        "Registre-se que a calibração **não melhora a correlação com a volatilidade nem com o "
        "retorno**, porque a correlação entre a série bruta e a calibrada é 0,973 — a correção "
        "desloca sobretudo o nível, e correlação é invariante a deslocamento de nível. A "
        "calibração conserta a **interpretação** do índice, não o seu **poder preditivo**.")

    # ─── 8 Conclusão ─────────────────────────────────────────────────────────
    A.secao(doc, "8", "Conclusão e reordenação de prioridades")
    A.tabela_abnt(doc, 16, "Resposta consolidada",
        ["Pergunta", "Resposta"],
        [
            ["A classificação da notícia está baixa?",
             "Mediana. 0,580 contra baseline de 0,413. E o erro é localizado: 90% envolvem a "
             "classe neutra; Positivo × Negativo atinge 0,783"],
            ["O índice de sentimento está baixo?",
             "Não — está deslocado em 87%, e a correção já foi implementada e validada"],
            ["A direção do preço está baixa?",
             "**Sim, e é o que de fato está baixo.** 49,7% com o modelo, 50,9% com rótulo "
             "perfeito, 46,7% com a aposta declarada do anotador humano — todos abaixo do "
             "baseline de 52,8%"],
            ["Melhorar o classificador resolve?",
             "Para a direção, não (ganho de 1,2 pp). Para a volatilidade, provavelmente sim "
             "(o sinal aparece com rótulo perfeito e some com o do modelo)"],
        ], fonte=FONTE)
    A.paragrafo(doc, "**A ordem de prioridade que decorre do diagnóstico:**")
    A.lista(doc, [
        "**Reposicionar a dissertação no eixo da volatilidade** e reportar a direção como "
        "resultado negativo devidamente medido — com o respaldo de que o teto humano também "
        "fica no acaso.",
        "**Investir em comitê de modelos e adaptação de domínio**, justificando-os pela "
        "volatilidade, e não pela direção.",
        "**Re-executar o Script 03 gravando os *logits***, o que torna conclusivo o teste de "
        "reponderação e viabiliza a combinação de probabilidades no comitê.",
        "**Reportar desempenho por categoria**, e não apenas o agregado — a dispersão entre "
        "0,481 (geopolítica) e 0,733 (governança) é informativa por si só.",
    ])

    # ─── 9 Reprodutibilidade ─────────────────────────────────────────────────
    A.secao(doc, "9", "Reprodutibilidade")
    A.tabela_abnt(doc, 17, "Scripts e saídas que sustentam cada número",
        ["Script", "Saída", "Seções"],
        [["src/sentimento/diagnosticar_erro_modelo.py",
          "diagnostico_erro_modelo.json", "2, 3, 4"],
         ["src/sentimento/testar_consertos_baratos.py",
          "consertos_baratos.json", "5"],
         ["src/sentimento/testar_teto_do_classificador.py",
          "teto_do_classificador.json", "6"],
         ["src/sentimento/calibrar_ism_com_gabarito.py",
          "ism_calibrado_petr4.csv · calibracao_ism_relatorio.json", "7"],
         ["src/sentimento/avaliar_ganho_calibracao.py",
          "ganho_calibracao_ism.json", "7"],
         ["src/sentimento/validar_rotulos_contra_mercado.py",
          "validacao_rotulos_contra_mercado.json", "8"]],
        fonte=FONTE)

    A.referencias(doc, "10", [
        "FORMAN, G. Quantifying counts and costs via classification. Data Mining and "
        "Knowledge Discovery, v. 17, n. 2, p. 164-206, 2008.",

        "BŁOCH, A.; SANTANA, C.; AMANTINO, M. Os jesuítas e a Era do Algoritmo: uma "
        "introdução à análise de sentimentos da correspondência colonial ultramarina "
        "portuguesa. Estudos Ibero-Americanos, v. 52, n. 1, p. 1-23, 2026.",

        "LANDIS, J. R.; KOCH, G. G. The measurement of observer agreement for categorical "
        "data. Biometrics, v. 33, n. 1, p. 159-174, 1977.",

        "SAERENS, M.; LATINNE, P.; DECAESTECKER, C. Adjusting the outputs of a classifier to "
        "new a priori probabilities: a simple procedure. Neural Computation, v. 14, n. 1, "
        "p. 21-41, 2002.",

        "SANTOS, L. L. FinBERT-PT-BR: análise de sentimentos de textos em português "
        "referentes ao mercado financeiro. 2022. Trabalho de Conclusão de Curso (Engenharia "
        "de Computação) — Escola Politécnica, USP, São Paulo, 2022.",

        "SANTOS, L. L.; BIANCHI, R. A. C.; COSTA, A. H. R. FinBERT-PT-BR: análise de "
        "sentimentos de textos em português do mercado financeiro. In: BWAIF, 2., 2023. "
        "Anais [...]. Porto Alegre: SBC, 2023. p. 144-155.",

        "TELES, L. E. P.; FIGUEIREDO, C. M. S. Comparing LLMs for sentiment analysis in "
        "financial market news. arXiv:2510.15929, 2025.",
    ])

    doc.save(SAIDA)
    print(f"OK -> {SAIDA.name}")


if __name__ == "__main__":
    main()
