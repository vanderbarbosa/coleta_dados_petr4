# -*- coding: utf-8 -*-
# ==============================================================================
#   14 — GUIA: como ler os números da pesquisa
#   Documento didático, com ilustrações, para preparar a defesa dos resultados.
# ==============================================================================
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
sys.path.insert(0, str(RAIZ / "src" / "comum"))
import abnt_docx as A  # noqa: E402

FIG = AQUI / "figuras"
D = RAIZ / "CVM" / "dados"
FONTE = "Elaborado pelo autor (2026)"
P = json.loads((D / "pesquisa_com_cvm.json").read_text(encoding="utf-8"))
DIAG = json.loads((D / "diagnostico_ml.json").read_text(encoding="utf-8"))


def main():
    doc = A.novo_documento()
    A.capa(doc,
        titulo="Como ler os números desta pesquisa",
        subtitulo="Acurácia, AUC, linha de base e valor-p — com exemplos, "
                  "ilustrações e as metas que devemos perseguir",
        autor="Vanderlei Barbosa da Silva",
        orientador="Orientador: Prof. Dr. Julio Cesar Nievola",
        instituicao="PUCPR — Programa de Pós-Graduação em Informática (PPGIa)",
        descricao="Guia de leitura preparado para sustentar a discussão dos "
                  "resultados com a orientação. Não introduz resultado novo: "
                  "explica como interpretar os que já existem, e define contra "
                  "que referência cada um deve ser julgado. Elaborado em 21 de "
                  "setembro de 2026.",
    )

    # ══════════════════════════════════════════════════════════════════════════
    A.secao(doc, "1", "A pergunta que organiza tudo")

    A.paragrafo(doc,
        "Há uma única pergunta por trás de toda métrica desta pesquisa, e vale a "
        "pena enunciá-la antes de qualquer fórmula:")

    A.citacao_longa(doc,
        "Este modelo sabe alguma coisa que eu já não saberia sem ele?",
        "A pergunta que toda métrica tenta responder")

    A.paragrafo(doc,
        "Repare que a pergunta **não** é *“o modelo acerta muito?”*. Um modelo "
        "pode acertar muitíssimo e não saber nada — e esse caso não é raro nem "
        "exótico: **acontece exatamente no nosso alvo de dia excepcional**, como "
        "a próxima seção mostra.")

    A.paragrafo(doc,
        "Por isso, em todas as tabelas da pesquisa, a acurácia **nunca aparece "
        "sozinha**. Ao lado dela vêm sempre três companhias: a linha de base, o "
        "ganho sobre ela, e um valor-p. Quem lê só a primeira coluna lê errado.")

    # ══════════════════════════════════════════════════════════════════════════
    A.secao(doc, "2", "Acurácia e AUC não são a mesma coisa")

    A.paragrafo(doc, "**Acurácia** responde: *de todos os palpites, quantos acertei?* "
        "O modelo precisa se comprometer — dizer “alta” ou “baixa” — e conta-se "
        "o placar.")

    A.paragrafo(doc, "**AUC** responde outra coisa: *pego um pregão que de fato foi "
        "agitado e um que foi calmo, ao acaso; com que frequência o modelo deu "
        "nota maior ao agitado?* Aqui o modelo não precisa decidir nada — basta "
        "**ordenar**.")

    A.paragrafo(doc,
        "A figura a seguir mostra os mesmos vinte pregões julgados por dois "
        "modelos. **O modelo que acerta mais é o pior dos dois.**")

    A.figura_abnt(doc, "1",
        "Dois modelos sobre os mesmos vinte pregões: o que acerta mais não sabe nada",
        str(FIG / "fig1_acuracia_vs_auc.png"), largura_cm=16, fonte=FONTE)

    A.paragrafo(doc,
        "O **Modelo A** responde “calmo” para tudo. Como pregões agitados são "
        "raros, ele acerta 85% das vezes. **E é inútil:** nunca aponta um pregão "
        "agitado, que é justamente o que se queria descobrir. A AUC dele é 0,50 "
        "— o mesmo de cara ou coroa.")

    A.paragrafo(doc,
        "O **Modelo B** acerta menos, 80%, mas **ordena bem**: as três barras "
        "laranja estão entre as notas mais altas. A AUC dá 0,94. É este que "
        "serve.")

    A.paragrafo(doc,
        "A diferença fica mais clara quando se olha a distribuição das notas. "
        "**A acurácia depende de onde você põe o corte. A AUC não depende do "
        "corte — ela mede o quanto as duas populações estão separadas.**")

    A.figura_abnt(doc, "2",
        "A AUC mede a separação entre as duas distribuições, não a posição do corte",
        str(FIG / "fig2_o_que_a_auc_mede.png"), largura_cm=16, fonte=FONTE)

    A.tabela_abnt(doc, "1", "As duas métricas, lado a lado",
        ["", "Acurácia", "AUC"],
        [["o que responde", "quantos acertei", "sei distinguir um caso do outro"],
         ["precisa de um corte?", "sim, em geral 0,50", "não"],
         ["engana quando...", "uma classe é muito mais comum", "raramente engana"],
         ["o valor do acaso", "a classe majoritária", "0,500"],
         ["abaixo do acaso significa", "pior que o palpite fixo",
          "ordena ao contrário"]],
        fonte=FONTE)

    # ══════════════════════════════════════════════════════════════════════════
    A.secao(doc, "3", "As duas armadilhas, nos nossos próprios números")

    A.paragrafo(doc,
        "Isto não é teoria. As duas armadilhas aparecem nos resultados desta "
        "pesquisa, uma em cada direção.")

    A.secao(doc, "3.1", "Acurácia alta, modelo inútil", nivel=2)

    A.paragrafo(doc,
        "No alvo “dia excepcional”, apenas **6,3%** dos pregões são excepcionais. "
        "Um modelo que responda **“não vai ser excepcional” sempre** acerta "
        "**93,7%**.")

    A.paragrafo(doc,
        f"O nosso modelo de mercado obteve acurácia de **93,6% — pior que o "
        f"palpite fixo** — e AUC de "
        f"**{DIAG['só mercado (sem texto)']['auc']:.3f}**".replace(".", ",") +
        ". Pela acurácia, perdeu. Pela AUC, é claramente bom. **A AUC estava "
        "certa**, e a figura seguinte mostra por quê.")

    A.figura_abnt(doc, "3",
        "O que a AUC significa na prática, com os dados reais da pesquisa",
        str(FIG / "fig4_ganho_por_faixa.png"), largura_cm=16, fonte=FONTE)

    A.paragrafo(doc,
        "Ordenando os pregões pela nota de risco do modelo, **os 10% apontados "
        "como mais arriscados concentram 28,8% dos dias excepcionais**, contra "
        "6,3% da base. E a metade mais calma concentra apenas 1,4%. **Isso é "
        "informação real**, e a acurácia não a enxergava.")

    A.secao(doc, "3.2", "Acurácia boa, ordenação ao contrário", nivel=2)

    m = P["direcao"]["Data Fusion + CVM  [NOVO]"]["SVM-RBF"]
    A.paragrafo(doc,
        f"No alvo direção, o SVM com Data Fusion mais CVM acertou "
        f"**{m['acuracia']:.2%}**".replace(".", ",") +
        f", acima da classe majoritária de {P['majoritaria_teste']:.2%}".replace(".", ",") +
        f". Mas a AUC deu **{m['auc']:.3f} — abaixo de 0,500**.".replace(".", ","))

    A.paragrafo(doc,
        "**Traduzindo:** aquele modelo acertou o placar por ter chutado “alta” na "
        "proporção certa, **não por saber distinguir um pregão do outro**. Se "
        "você sortear um pregão de alta e um de baixa, ele dá nota maior ao de "
        "baixa mais vezes do que ao de alta. É uma bússola que aponta "
        "levemente para o sul.")

    A.paragrafo(doc,
        "**É por isso que esse número não deve ser apresentado como conquista.** "
        "Se a banca perguntar, a resposta honesta é a de cima.")

    # ══════════════════════════════════════════════════════════════════════════
    A.secao(doc, "4", "A linha de base: contra quem comparar")

    A.paragrafo(doc,
        "Nenhum número significa nada isoladamente. **O que significa é a "
        "distância até a referência certa** — e a referência muda conforme o "
        "alvo.")

    A.figura_abnt(doc, "4",
        "Direção do pregão seguinte: o adversário é a linha vermelha, não o zero",
        str(FIG / "fig5_direcao_linhas_base.png"), largura_cm=16, fonte=FONTE)

    A.paragrafo(doc,
        "A linha vermelha é a **classe majoritária**: o resultado de quem "
        "responde “sempre alta”, sem ler nada. **Nenhuma barra a supera de forma "
        "confiável.** A linha cinza, de 50%, é o acaso da hipótese de mercados "
        "eficientes — bater essa é fácil e não prova coisa alguma quando a classe "
        "majoritária está acima dela.")

    A.paragrafo(doc,
        "**Este é o erro de leitura mais comum nesta área**, e convém saber "
        "apontá-lo: o valor-p binomial compara com **50%**. Com 53,14% dos "
        "pregões sendo de alta, um modelo pode passar no teste binomial e ainda "
        "assim ser **pior que não fazer nada**.")

    # ══════════════════════════════════════════════════════════════════════════
    A.secao(doc, "5", "O valor-p, sem mistério")

    A.paragrafo(doc,
        "O valor-p responde a uma pergunta estreita e específica: **“se não "
        "houvesse efeito nenhum, com que frequência o acaso produziria um "
        "resultado ao menos tão forte quanto este?”**")

    A.tabela_abnt(doc, "2", "Como ler um valor-p",
        ["valor-p", "Leitura", "O que dizer na banca"],
        [["menor que 0,01", "muito difícil de atribuir ao acaso",
          "“o resultado se sustenta”"],
         ["entre 0,01 e 0,05", "improvável, mas possível",
          "“passa no teste usual”"],
         ["entre 0,05 e 0,10", "sugestivo, não conclusivo",
          "“há indício, não há prova”"],
         ["acima de 0,10", "o acaso explicaria",
          "“não podemos afirmar nada”"]],
        fonte=FONTE)

    A.paragrafo(doc,
        "Três advertências que evitam constrangimento:")

    A.lista(doc, [
        "**valor-p alto não prova que não há efeito** — prova apenas que a "
        "amostra não foi suficiente para detectá-lo. É o nosso caso na hipótese "
        "da CVM como filtro, que precisaria de ~15.200 noites e tem 393;",
        "**valor-p baixo não mede tamanho de efeito.** Um efeito minúsculo fica "
        "significativo se a amostra for enorme. Por isso reportamos sempre o "
        "ganho em pontos percentuais ao lado do valor-p;",
        "**testar muitas hipóteses infla o valor-p.** Se eu testar vinte coisas, "
        "uma delas dará p < 0,05 por puro acaso. É por isso que registramos "
        "quantos alvos foram testados antes de chegar ao que funcionou.",
    ])

    # ══════════════════════════════════════════════════════════════════════════
    A.secao(doc, "6", "O teste de McNemar, que é o que realmente decide")

    A.paragrafo(doc,
        "Quando a pergunta é **“esta fonte nova acrescenta?”**, comparar duas "
        "acurácias é insuficiente — os dois modelos podem acertar o mesmo número "
        "de pregões e ainda assim acertar pregões **diferentes**.")

    A.paragrafo(doc,
        "O McNemar resolve isso. Ele **joga fora todos os pregões em que os dois "
        "modelos concordam** e olha apenas onde discordam: quantas vezes o novo "
        "acertou onde o antigo errou, contra o inverso.")

    A.tabela_abnt(doc, "3", "O McNemar aplicado às nossas fontes",
        ["Pergunta", "Ganhou", "Perdeu", "valor-p", "Resposta"],
        [["a notícia acrescenta sobre o preço? (XGBoost)", "88", "65", "0,0750",
          "quase, mas não"],
         ["a CVM acrescenta sobre a notícia? (SVM)", "37", "25", "0,1619", "não"],
         ["a CVM acrescenta sobre a notícia? (XGBoost)", "64", "77", "0,3122", "não"],
         ["o embedding acrescenta? (SVM)", "27", "55", "0,0026", "PIORA"]],
        fonte=FONTE)

    A.paragrafo(doc,
        "**Leia a última linha com atenção**, porque ela é contraintuitiva: o "
        "embedding tem valor-p de 0,0026, que é “significativo” — mas "
        "significativamente **pior**. Ganhou 27 e perdeu 55. **Significância não "
        "é sinônimo de boa notícia.**")

    # ══════════════════════════════════════════════════════════════════════════
    A.secao(doc, "7", "Volatilidade se mede de outro jeito")

    A.paragrafo(doc,
        "Para volatilidade, acurácia é a métrica errada — não se está "
        "classificando, e sim estimando uma quantidade. A pesquisa usa duas "
        "medidas de erro e uma referência.")

    A.tabela_abnt(doc, "4", "As medidas da volatilidade",
        ["Medida", "O que é", "Queremos que seja"],
        [["MAE", "erro absoluto médio da previsão", "o menor possível"],
         ["RMSE", "como o MAE, mas pune mais os erros grandes", "o menor possível"],
         ["R²-OS vs HAR", "quanto o modelo reduz o erro do HAR de Corsi",
          "positivo, e quanto maior melhor"],
         ["o HAR de Corsi", "a volatilidade explicada pelas suas próprias "
          "médias de 1, 5 e 22 dias", "é o adversário, não o troféu"]],
        fonte=FONTE)

    A.paragrafo(doc,
        "**Por que o HAR é o adversário certo:** volatilidade é grudenta. Depois "
        "de uma semana agitada vem outra agitada. Qualquer modelo que não bata a "
        "própria memória da série não está acrescentando nada. É o mesmo "
        "princípio da “média da semana anterior” que o Prof. Emerson sugeriu para "
        "o estudo de evento — **comparar com o passado recente, não com uma média "
        "distante.**")

    A.paragrafo(doc,
        "Uma consequência a ter na ponta da língua: quando eu digo que o "
        "histórico de preço prevê a volatilidade melhor que o texto, **isso não é "
        "descoberta minha — é o HAR**, a linha de base que o Capítulo 3 já "
        "adota. O achado real é outro: **o texto não reduz o erro dessa "
        "referência.**")

    # ══════════════════════════════════════════════════════════════════════════
    A.secao(doc, "8", "As metas: o que devemos perseguir")

    A.paragrafo(doc,
        "Uma pergunta legítima é *“qual número seria bom?”*. A resposta depende "
        "do alvo, e **não é “perto de 1”**.")

    A.figura_abnt(doc, "5",
        "As metas realistas de cada alvo, e onde a pesquisa está hoje",
        str(FIG / "fig6_o_que_buscar.png"), largura_cm=16, fonte=FONTE)

    A.paragrafo(doc,
        "**Acurácia perto de 1 em direção de ação é sinal de erro, não de "
        "qualidade.** Se o mercado fosse assim previsível, a informação seria "
        "explorada e o ganho desapareceria. Quando aparece um número alto, "
        "quase sempre é uma destas três coisas:")

    A.tabela_abnt(doc, "5", "De onde vêm os números altos que se vê na literatura",
        ["Causa", "Exemplo"],
        [["vazamento de informação",
          "alguma coluna carrega dado do próprio dia que se quer prever"],
         ["amostra minúscula",
          "os 86,7% de Bollen eram 13 acertos em 15 dias — e foram refutados"],
         ["alvo desbalanceado",
          "responder “não” sempre, no nosso alvo de dia excepcional, dá 93,7%"]],
        fonte=FONTE)

    A.paragrafo(doc,
        "**E a regra de que “AUC boa é acima de 0,7” vem da medicina e não se "
        "aplica à direção de ações.** O próprio referencial da pesquisa registra "
        "que o FinBERT em inglês fica em 0,555 em situação equivalente. O que "
        "vale é outra coisa: **o intervalo de confiança da AUC exclui o 0,50?**")

    A.tabela_abnt(doc, "6", "As AUC desta pesquisa, com intervalo de confiança",
        ["Modelo", "AUC", "Intervalo de 95%", "Veredito"],
        [["texto (notícia + CVM + embedding)",
          f"{DIAG['só texto (notícia + CVM + embedding)']['auc']:.3f}".replace(".", ","),
          f"{DIAG['só texto (notícia + CVM + embedding)']['ic95'][0]:.3f} a "
          f"{DIAG['só texto (notícia + CVM + embedding)']['ic95'][1]:.3f}".replace(".", ","),
          "passa — há sinal"],
         ["histórico de preço (o HAR)",
          f"{DIAG['só mercado (sem texto)']['auc']:.3f}".replace(".", ","),
          f"{DIAG['só mercado (sem texto)']['ic95'][0]:.3f} a "
          f"{DIAG['só mercado (sem texto)']['ic95'][1]:.3f}".replace(".", ","),
          "passa, e é forte"],
         ["direção, qualquer braço", "0,49 a 0,52", "cruza o 0,50", "não passa"]],
        fonte=FONTE)

    A.paragrafo(doc,
        "**A AUC de 0,624 do texto é um resultado legítimo**, ainda que longe de "
        "0,7. E a de 0,794 do mercado é alta não por mérito do modelo, mas porque "
        "prever que amanhã será agitado depois de uma semana agitada é fácil.")

    # ══════════════════════════════════════════════════════════════════════════
    A.secao(doc, "9", "Um roteiro para ler qualquer tabela desta pesquisa")

    A.paragrafo(doc, "Na ordem, e sem pular etapas:")

    A.lista(doc, [
        "**Qual é a linha de base?** Classe majoritária para direção; HAR para "
        "volatilidade; a taxa da base para eventos raros.",
        "**Qual a distância até ela, em pontos?** Não a acurácia absoluta — a "
        "distância.",
        "**Essa distância cabe dentro do erro-padrão?** Com 653 pregões, o "
        "erro-padrão de uma proporção é ~1,95 ponto. Vantagem de 1,2 ponto não "
        "é vantagem.",
        "**A AUC concorda com a acurácia?** Se discordarem, acredite na AUC.",
        "**O teste certo passou?** Binomial para “supera o acaso”; **McNemar "
        "para “esta fonte acrescenta”**.",
        "**Quantas hipóteses foram testadas antes desta?** Se foram muitas, "
        "desconfie da que deu certo.",
    ])

    A.secao(doc, "10", "As três frases para levar à mentoria")

    A.lista(doc, [
        "“Acurácia responde quantos acertei; AUC responde se eu sei distinguir "
        "um caso do outro. Quando as duas discordam, a AUC é a que diz a "
        "verdade sobre haver informação ali.”",
        "“Nenhum número isolado significa nada. O que significa é a distância "
        "até a linha de base certa, e se essa distância passa num teste.”",
        "“Em direção de ação, acurácia perto de 1 é sinal de bug. A meta "
        "realista é 55 a 58 por cento, e passar no McNemar.”",
    ])

    doc.save(AQUI / "14_GUIA_Como_ler_os_numeros.docx")
    print("  [OK] 14_GUIA_Como_ler_os_numeros.docx")


if __name__ == "__main__":
    main()
