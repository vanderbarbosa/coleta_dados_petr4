# -*- coding: utf-8 -*-
# ==============================================================================
#   A terceira parte do pedido de 16/09: combinar as fontes
#   Gera o documento completo e o resumido.
# ==============================================================================
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
sys.path.insert(0, str(RAIZ / "src" / "comum"))

import abnt_docx as A  # noqa: E402

FONTE = "Elaborado pelo autor (2026)"
N = json.loads((RAIZ / "CVM" / "dados" / "numeros_confronto.json").read_text(encoding="utf-8"))
C, F, CO = N["confronto"], N["filtro"], N["cobertura"]
RI, RC = N["regra_ingenua"], N["regra_corrigida"]


def completo() -> None:
    doc = A.novo_documento()
    A.capa(
        doc,
        titulo="Juntar as duas fontes acrescenta alguma coisa?",
        subtitulo="Notícia de portal, comunicado da CVM, e as duas somadas na "
                  "previsão do pregão seguinte",
        autor="Vanderlei Barbosa da Silva",
        orientador="Orientador: Prof. Dr. Julio Cesar Nievola",
        instituicao="PUCPR — Programa de Pós-Graduação em Informática (PPGIa)",
        descricao="Terceira parte do pedido feito na mentoria de 16 de setembro de "
                  "2026 pelos Profs. Emerson Paraiso e Julio Nievola. As duas "
                  "primeiras partes estão nos documentos 01 e 02 desta mesma pasta. "
                  "Elaborado em 20 de setembro de 2026.",
    )

    A.secao(doc, "1", "O que foi pedido, e por que demorou")

    A.paragrafo(doc,
        "Os senhores pediram três coisas na mentoria de 16 de setembro. As duas "
        "primeiras estão nos documentos anteriores desta pasta: aplicar o "
        "classificador aos comunicados da CVM e avaliar o impacto no pregão seguinte. "
        "A terceira é esta: **juntar os comunicados da CVM com as notícias de portal "
        "que já coletávamos, e ver se a combinação acrescenta algo.**")

    A.paragrafo(doc,
        "Ela ficou por último porque exigiu refazer o desenho duas vezes. Convém "
        "contar isso, porque o primeiro resultado foi ruim por culpa da minha regra, "
        "não dos dados.")

    A.secao(doc, "2", "Como o confronto foi montado")

    A.paragrafo(doc,
        "Três exigências foram postas antes de qualquer cálculo, para que a "
        "comparação não favorecesse uma das fontes por acidente.")

    A.paragrafo(doc,
        "**A mesma janela.** Conta o que foi publicado entre o fechamento de um "
        "pregão e a abertura do seguinte. As duas fontes enxergam exatamente o mesmo "
        "intervalo de tempo.")

    A.paragrafo(doc,
        "**Os mesmos dias.** Notícia de portal existe em quase toda noite; comunicado "
        "da CVM, não. Comparar a acurácia de um em dois mil dias com a do outro em "
        "novecentos não diz nada. O confronto principal roda apenas nos dias em que "
        "as duas fontes existem.")

    A.paragrafo(doc,
        "**A mesma regra e o mesmo adversário.** Saldo de sentimento positivo prevê "
        "alta, negativo prevê baixa. E tudo é comparado contra a classe majoritária — "
        "quem não lê nada e sempre chuta o lado mais frequente.")

    A.tabela_abnt(doc, "1", "Cobertura, em pregões da PETR4",
        ["", "Pregões"],
        [
            ["analisados no período " + N["periodo"], f"{CO['pregoes']:,}".replace(",", ".")],
            ["com ao menos uma notícia na noite",
             f"{CO['com_noticia']:,}".replace(",", ".") +
             f"  ({CO['com_noticia']/CO['pregoes']:.0%})"],
            ["com ao menos um comunicado da CVM",
             f"{CO['com_cvm']:,}".replace(",", ".") +
             f"  ({CO['com_cvm']/CO['pregoes']:.0%})"],
            ["com as DUAS fontes", f"{CO['com_ambos']:,}".replace(",", ".")],
            ["com Fato Relevante", f"{CO['com_fr']:,}".replace(",", ".")],
        ], fonte=FONTE)

    A.secao(doc, "3", "A primeira tentativa, e por que ela falhou")

    A.paragrafo(doc,
        "A regra inicial era a óbvia: somar o sentimento da noite. Mais notícias "
        "positivas que negativas, aposta em alta; o contrário, aposta em baixa.")

    A.paragrafo(doc,
        f"**Ela previu BAIXA em {RI['preve_baixa_pct']}% das noites.**")

    A.paragrafo(doc,
        "O motivo é conhecido desta pesquisa e está documentado desde a auditoria do "
        "classificador: ele rotula quase metade do corpus como negativo, e apenas 14% "
        "como positivo. Somar uma noite inteira, nessas condições, quase nunca produz "
        "saldo positivo.")

    A.paragrafo(doc,
        "O resultado foi uma acurácia de "
        f"{RI['acuracia']}%, contra {RI['majoritaria']}% de quem não lê nada. **Abaixo "
        "do acaso.** Mas o diagnóstico importa mais que o número: **uma regra que diz "
        "a mesma coisa em 99% dos casos não é previsão, é constante.** Ela não estava "
        "errando; ela não estava dizendo nada.")

    A.paragrafo(doc,
        "Inverter o sinal também não resolveria: daria 52,2%, ainda abaixo dos 52,5% "
        "do palpite fixo. Não havia sinal escondido para aproveitar.")

    A.secao(doc, "4", "A correção")

    A.paragrafo(doc,
        "A pergunta estava mal formulada. Num corpus sistematicamente negativo, "
        "perguntar *“houve mais positivas que negativas?”* não separa nada. A pergunta "
        "que separa é outra: **“esta noite foi mais negativa que o habitual?”**")

    A.paragrafo(doc,
        "Passamos a comparar o saldo da noite com a média móvel dos sessenta pregões "
        "anteriores. A média usa apenas o passado, de modo que nenhum dia enxerga o "
        "próprio futuro.")

    A.paragrafo(doc,
        f"O efeito foi imediato. As previsões passaram a se distribuir de forma "
        f"equilibrada — {RC['preve_alta_pct']}% de ALTA, contra os 1,0% de antes.")

    A.secao(doc, "5", "O resultado")

    A.tabela_abnt(doc, "2", "Só os dias em que as duas fontes existem",
        ["Fonte de texto", "Noites", "Acertou", "Palpite fixo", "Ganho", "valor-p"],
        [
            ["notícia de portal", f"{C['inter_dev_news']['n']:,}".replace(",", "."),
             f"{C['inter_dev_news']['acuracia']:.1%}",
             f"{C['inter_dev_news']['maj']:.1%}",
             f"{C['inter_dev_news']['ganho_pp']:+.2f} p.p.",
             f"{C['inter_dev_news']['p']:.4f}"],
            ["comunicado da CVM", f"{C['inter_dev_cvm']['n']:,}".replace(",", "."),
             f"{C['inter_dev_cvm']['acuracia']:.1%}",
             f"{C['inter_dev_cvm']['maj']:.1%}",
             f"{C['inter_dev_cvm']['ganho_pp']:+.2f} p.p.",
             f"{C['inter_dev_cvm']['p']:.4f}"],
            ["as duas somadas", f"{C['inter_dev_ambos']['n']:,}".replace(",", "."),
             f"{C['inter_dev_ambos']['acuracia']:.1%}",
             f"{C['inter_dev_ambos']['maj']:.1%}",
             f"{C['inter_dev_ambos']['ganho_pp']:+.2f} p.p.",
             f"{C['inter_dev_ambos']['p']:.4f}"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**A notícia de portal funciona. O comunicado da CVM, sozinho, não prevê "
        "direção.**")

    A.paragrafo(doc,
        "Esse segundo achado não surpreende quem leu o documento anterior. O texto dos "
        "comunicados da CVM é curto e burocrático — quarenta e sete caracteres em "
        "média, mais parecido com etiqueta de arquivo do que com prosa. Setenta e nove "
        "por cento saem classificados como neutros. Não há de onde extrair direção.")

    A.secao(doc, "5.1", "Mas nas noites de Fato Relevante muda", nivel=2)

    A.tabela_abnt(doc, "3", "Só as noites com Fato Relevante",
        ["Fonte de texto", "Noites", "Acertou", "Palpite fixo", "Ganho", "valor-p"],
        [
            ["notícia de portal", f"{C['fatorel_dev_news']['n']:,}".replace(",", "."),
             f"{C['fatorel_dev_news']['acuracia']:.1%}",
             f"{C['fatorel_dev_news']['maj']:.1%}",
             f"{C['fatorel_dev_news']['ganho_pp']:+.2f} p.p.",
             f"{C['fatorel_dev_news']['p']:.4f}"],
            ["comunicado da CVM", f"{C['fatorel_dev_cvm']['n']:,}".replace(",", "."),
             f"{C['fatorel_dev_cvm']['acuracia']:.1%}",
             f"{C['fatorel_dev_cvm']['maj']:.1%}",
             f"{C['fatorel_dev_cvm']['ganho_pp']:+.2f} p.p.",
             f"{C['fatorel_dev_cvm']['p']:.4f}"],
            ["AS DUAS SOMADAS", f"{C['fatorel_dev_ambos']['n']:,}".replace(",", "."),
             f"{C['fatorel_dev_ambos']['acuracia']:.1%}",
             f"{C['fatorel_dev_ambos']['maj']:.1%}",
             f"{C['fatorel_dev_ambos']['ganho_pp']:+.2f} p.p.",
             f"{C['fatorel_dev_ambos']['p']:.4f}"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**Este é o melhor resultado direcional de toda a pesquisa.** Somando as duas "
        f"fontes nas noites de Fato Relevante, o acerto é de "
        f"{C['fatorel_dev_ambos']['acuracia']:.1%} contra "
        f"{C['fatorel_dev_ambos']['maj']:.1%} de quem não lê nada — "
        f"{C['fatorel_dev_ambos']['ganho_pp']:+.2f} pontos percentuais.")

    A.paragrafo(doc,
        "E há um detalhe que merece atenção. **A notícia sozinha, nessas mesmas "
        f"noites, não passa no teste** (valor-p de {C['fatorel_dev_news']['p']:.3f}). "
        "**Só a combinação passa.** A contribuição da CVM é pequena mas é o que leva o "
        "resultado ao outro lado da linha.")

    A.secao(doc, "6", "A hipótese que isso levanta")

    A.paragrafo(doc,
        "Se o comunicado da CVM não prevê direção pelo seu texto, mas a combinação "
        "funciona justamente nas noites em que ele existe, então **o que a CVM "
        "acrescenta não é o conteúdo. É a indicação de qual noite importa.**")

    A.paragrafo(doc,
        "Para testar, fixamos a regra usando apenas as notícias de portal e variamos "
        "somente o tipo de noite.")

    A.tabela_abnt(doc, "4", "Mesma regra de notícia, tipos de noite diferentes",
        ["Tipo de noite", "Noites", "Acertou", "Ganho sobre o palpite fixo"],
        [
            ["sem comunicado nenhum",
             f"{F['noite SEM comunicado nenhum']['n']:,}".replace(",", "."),
             f"{F['noite SEM comunicado nenhum']['acuracia']:.1%}",
             f"{F['noite SEM comunicado nenhum']['ganho_pp']:+.2f} p.p."],
            ["com Comunicado ao Mercado",
             f"{F['noite com Comunicado, sem Fato Relevante']['n']:,}".replace(",", "."),
             f"{F['noite com Comunicado, sem Fato Relevante']['acuracia']:.1%}",
             f"{F['noite com Comunicado, sem Fato Relevante']['ganho_pp']:+.2f} p.p."],
            ["com FATO RELEVANTE",
             f"{F['noite com FATO RELEVANTE']['n']:,}".replace(",", "."),
             f"{F['noite com FATO RELEVANTE']['acuracia']:.1%}",
             f"{F['noite com FATO RELEVANTE']['ganho_pp']:+.2f} p.p."],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "O ganho sobe de "
        f"{F['noite SEM comunicado nenhum']['ganho_pp']:+.2f} para "
        f"{F['noite com FATO RELEVANTE']['ganho_pp']:+.2f} pontos conforme a noite "
        "fica mais importante. **A ordem é exatamente a que a tese desta pesquisa "
        "prevê:** ler o texto compensa onde o evento é grande.")

    A.paragrafo(doc,
        "**E aqui é preciso parar e ser honesto.** A diferença entre as noites de "
        f"Fato Relevante e as demais é de {F['teste_filtro']['dif_pp']:+.2f} pontos, "
        f"com valor-p de {F['teste_filtro']['p']:.2f}. **Não passa no teste "
        "estatístico.**")

    A.paragrafo(doc,
        "Fiz a conta de quantos casos seriam necessários para decidir: **cerca de "
        "quinze mil noites por grupo**, com poder de 80%. Temos trezentas e noventa e "
        "três. Estendendo para VALE3, ITUB4 e BBAS3 — coleta já concluída — chega-se a "
        "seiscentas e vinte e seis, que continuam sendo vinte e quatro vezes menos do "
        "que o necessário.")

    A.paragrafo(doc,
        "**Registro isso como hipótese, não como achado.** O padrão é coerente, a "
        "ordem é a prevista, e a explicação faz sentido. Mas com esses números não há "
        "como distinguir isso do acaso, e apresentá-lo como resultado seria "
        "impróprio.")

    A.secao(doc, "7", "O que aprendemos, e o que fica")

    A.paragrafo(doc,
        "**Três conclusões se sustentam:**")

    A.paragrafo(doc,
        "A notícia de portal prevê direção melhor que o comunicado oficial. Parece "
        "contraintuitivo — o comunicado é a fonte primária —, mas o motivo é de "
        "linguagem: o comunicado descreve o fato em termos administrativos; a notícia "
        "já traz a interpretação.")

    A.paragrafo(doc,
        "Juntar as duas fontes produz o melhor resultado da pesquisa, e apenas nas "
        "noites de Fato Relevante.")

    A.paragrafo(doc,
        "E a correção da regra importou mais que a escolha da fonte. **A diferença "
        "entre perguntar “houve positivas?” e “esta noite foi pior que o habitual?” "
        "valeu seis pontos percentuais** — mais do que qualquer ganho obtido por "
        "trocar de fonte, de modelo ou de ativo em toda a pesquisa.")

    A.secao(doc, "8", "Limitações")

    A.lista(doc, [
        "**Um único ativo.** Todos os números são da PETR4. A coleta para VALE3, "
        "ITUB4 e BBAS3 está concluída, mas falta classificar e reprocessar.",
        "**A hipótese do filtro segue em aberto**, e pelo cálculo de poder ela não "
        "será resolvida com a extensão a mais três ativos.",
        "**O ganho é pequeno.** Mesmo o melhor resultado, de 55,2%, está a três "
        "pontos e meio do palpite trivial. Não é sistema de negociação; é evidência "
        "de que há sinal.",
        "**A janela de sessenta pregões foi escolhida por conveniência** e não "
        "submetida a teste de sensibilidade. Convém fazê-lo antes de publicar.",
    ])

    doc.save(AQUI / "05_Combinar_as_fontes_COMPLETO.docx")
    print("  [OK] 05_Combinar_as_fontes_COMPLETO.docx")


def resumido() -> None:
    doc = A.novo_documento()
    A.capa(
        doc,
        titulo="Juntar jornal com comunicado oficial ajuda?",
        subtitulo="A terceira parte do pedido de 16 de setembro, em linguagem comum",
        autor="Vanderlei Barbosa da Silva",
        orientador="Orientador: Prof. Dr. Julio Cesar Nievola",
        instituicao="PUCPR — Programa de Pós-Graduação em Informática (PPGIa)",
        descricao="Versão resumida, para leitura em cinco minutos. O detalhamento "
                  "está no documento 05. Elaborado em 20 de setembro de 2026.",
    )

    A.secao(doc, "1", "A pergunta")

    A.paragrafo(doc,
        "Temos duas fontes de texto sobre a Petrobras. **O jornal** — notícias dos "
        "portais financeiros. E **o comunicado oficial** que a empresa entrega à CVM.")

    A.paragrafo(doc,
        "Qual das duas prevê melhor se a ação vai subir ou descer no dia seguinte? E "
        "juntar as duas adianta alguma coisa?")

    A.secao(doc, "2", "A primeira tentativa deu errado, e vale contar por quê")

    A.paragrafo(doc,
        "A ideia inicial era simples: contar as notícias boas e as ruins da noite. Se "
        "houvesse mais boas, apostar que a ação sobe.")

    A.paragrafo(doc,
        f"**O programa apostou em queda em {RI['preve_baixa_pct']}% das noites.**")

    A.paragrafo(doc,
        "Ou seja: ele dava sempre a mesma resposta. **Isso não é previsão, é uma "
        "constante.** E acertava "
        f"{RI['acuracia']}%, menos que os {RI['majoritaria']}% de quem chutasse sempre "
        "para o mesmo lado sem ler nada.")

    A.paragrafo(doc,
        "A causa já era conhecida: o programa que lê os textos enxerga quase tudo como "
        "negativo. Somar uma noite inteira, com um leitor assim, nunca dá saldo "
        "positivo.")

    A.secao(doc, "3", "A correção")

    A.paragrafo(doc,
        "**A pergunta estava errada.** Se o leitor vê tudo como ruim, não adianta "
        "perguntar *“teve notícia boa?”*. A pergunta certa é:")

    A.paragrafo(doc,
        "**“Esta noite foi PIOR que o normal dessa ação?”**", recuo=False)

    A.paragrafo(doc,
        "Passamos a comparar cada noite com a média dos sessenta pregões anteriores. "
        "As previsões se equilibraram na hora — metade para cada lado.")

    A.secao(doc, "4", "O resultado")

    A.tabela_abnt(doc, "1", "Nos dias em que as duas fontes existem",
        ["Quem faz a previsão", "Acertou", "Quem não lê nada", "Vale?"],
        [
            ["só o jornal", f"{C['inter_dev_news']['acuracia']:.1%}",
             f"{C['inter_dev_news']['maj']:.1%}", "SIM"],
            ["só o comunicado da CVM", f"{C['inter_dev_cvm']['acuracia']:.1%}",
             f"{C['inter_dev_cvm']['maj']:.1%}", "não"],
            ["os dois juntos", f"{C['inter_dev_ambos']['acuracia']:.1%}",
             f"{C['inter_dev_ambos']['maj']:.1%}", "SIM"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**O jornal funciona. O comunicado oficial, sozinho, não.**")

    A.paragrafo(doc,
        "A explicação é de linguagem. O comunicado da CVM diz *“Alteração na Diretoria "
        "Executiva”* — descreve o fato, sem opinião. O jornal diz o que aquilo "
        "significa. **Quem tem opinião é o jornal.**")

    A.secao(doc, "5", "Mas nas noites de Fato Relevante muda")

    A.tabela_abnt(doc, "2", "Só quando houve Fato Relevante",
        ["Quem faz a previsão", "Acertou", "Quem não lê nada", "Vantagem"],
        [
            ["só o jornal", f"{C['fatorel_dev_news']['acuracia']:.1%}",
             f"{C['fatorel_dev_news']['maj']:.1%}",
             f"{C['fatorel_dev_news']['ganho_pp']:+.1f} pontos"],
            ["só o comunicado", f"{C['fatorel_dev_cvm']['acuracia']:.1%}",
             f"{C['fatorel_dev_cvm']['maj']:.1%}",
             f"{C['fatorel_dev_cvm']['ganho_pp']:+.1f} pontos"],
            ["OS DOIS JUNTOS", f"{C['fatorel_dev_ambos']['acuracia']:.1%}",
             f"{C['fatorel_dev_ambos']['maj']:.1%}",
             f"{C['fatorel_dev_ambos']['ganho_pp']:+.1f} pontos"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**É o melhor resultado de direção de toda a pesquisa.** E repare: o jornal "
        "sozinho, nessas mesmas noites, não passa no teste estatístico. **Só a "
        "combinação passa.**")

    A.secao(doc, "6", "A ideia que isso sugere")

    A.paragrafo(doc,
        "Se o comunicado da CVM não prevê nada sozinho, mas a combinação só funciona "
        "nas noites em que ele existe, então **ele não serve como texto. Serve como "
        "aviso.**")

    A.paragrafo(doc,
        "**Ele diz em qual noite vale a pena ler o jornal com atenção.**")

    A.tabela_abnt(doc, "3", "A mesma leitura do jornal, em noites diferentes",
        ["Tipo de noite", "Vantagem do jornal"],
        [
            ["sem comunicado nenhum",
             f"{F['noite SEM comunicado nenhum']['ganho_pp']:+.2f} pontos"],
            ["com Comunicado ao Mercado",
             f"{F['noite com Comunicado, sem Fato Relevante']['ganho_pp']:+.2f} pontos"],
            ["com FATO RELEVANTE",
             f"{F['noite com FATO RELEVANTE']['ganho_pp']:+.2f} pontos"],
        ], fonte=FONTE)

    A.paragrafo(doc,
        "**A vantagem triplica conforme a noite fica importante.**")

    A.paragrafo(doc,
        "**Mas isto ainda não é um resultado, e não pretendo apresentá-lo como se "
        "fosse.** A diferença não passa no teste estatístico — a chance de ser "
        f"coincidência é de {F['teste_filtro']['p']:.0%}. Para decidir, seriam "
        "precisas cerca de quinze mil noites de Fato Relevante. Temos trezentas e "
        "noventa e três.")

    A.secao(doc, "7", "Em quatro frases")

    A.lista(doc, [
        "“A minha primeira regra dava sempre a mesma resposta — apostava em queda em "
        "99% das noites. Não errava: não dizia nada.”",
        "“Corrigi perguntando se a noite foi pior que o normal daquela ação, em vez de "
        "perguntar se teve notícia boa. Isso sozinho valeu seis pontos.”",
        "“O jornal prevê melhor que o comunicado oficial, porque o comunicado descreve "
        "o fato e o jornal já traz a interpretação.”",
        "“E o melhor resultado da pesquisa é juntar os dois nas noites de Fato "
        f"Relevante: {C['fatorel_dev_ambos']['acuracia']:.1%} contra "
        f"{C['fatorel_dev_ambos']['maj']:.1%} de quem não lê nada.”",
    ])

    doc.save(AQUI / "06_Combinar_as_fontes_RESUMIDO.docx")
    print("  [OK] 06_Combinar_as_fontes_RESUMIDO.docx")


if __name__ == "__main__":
    completo()
    resumido()
