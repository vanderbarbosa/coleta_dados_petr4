# -*- coding: utf-8 -*-
# ==============================================================================
#   Glossário — todos os termos que aparecem nos documentos, explicados
#   Saída: Mentoria_Emerson_13082026/10_GLOSSARIO.docx
#
#   Cada verbete tem: o que é, a analogia, por que importa para nós, e o nosso
#   número quando houver.
# ==============================================================================
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(RAIZ / "src" / "comum"))

import abnt_docx as A  # noqa: E402

FONTE = "Elaborado pelo autor (2026)"
SAIDA = AQUI / "10_GLOSSARIO.docx"


def verbete(doc, num, termo, blocos):
    A.secao(doc, num, termo)
    for rotulo, texto in blocos:
        A.paragrafo(doc, f"**{rotulo}** {texto}")


def main() -> None:
    doc = A.novo_documento()

    A.capa(
        doc,
        titulo="Glossário de bolso",
        subtitulo="Os termos que aparecem nos documentos, explicados com analogia — "
                  "e o nosso número em cada um",
        autor="Vanderlei Barbosa da Silva",
        orientador="Orientador: Prof. Dr. Julio Cesar Nievola",
        instituicao="PUCPR — Programa de Pós-Graduação em Informática (PPGIa)",
        descricao="Documento de consulta rápida. Cada verbete traz o que o termo "
                  "significa, uma analogia do dia a dia, por que importa para esta "
                  "pesquisa e o nosso número quando houver. Elaborado em 20 de agosto "
                  "de 2026.",
    )

    A.secao(doc, "0", "Os quatro termos que mais aparecem")

    A.tabela_abnt(doc, "1", "Resumo de bolso",
        ["Termo", "Em uma frase"],
        [
            ["HAR", "modelo que prevê o sacolejo usando SÓ o histórico do preço, sem ler nada"],
            ["Vencer o HAR", "seu modelo com notícias errar MENOS que esse modelo sem notícias"],
            ["Efeito de cauda", "o sentimento só faz diferença nos dias extremos, não no dia comum"],
            ["Valor-p", "a chance de o resultado ser sorte; abaixo de 0,05 conta, acima não"],
        ], fonte=FONTE)

    verbete(doc, "1", "HAR — o modelo que não lê nada", [
        ("O que é:",
         "um modelo que prevê a volatilidade de amanhã usando **apenas o histórico do "
         "próprio preço**. Olha três coisas: quanto sacudiu **ontem**, a média das "
         "**últimas 5 sessões** e a média das **últimas 22 sessões**. E responde: "
         "“amanhã vai ser parecido com isso”."),
        ("A analogia:",
         "é como prever o tempo dizendo *“amanhã vai ser parecido com hoje e com esta "
         "semana”*. Parece preguiçoso, mas acerta muito — porque o clima vem em blocos, "
         "e a volatilidade também."),
        ("Por que funciona:",
         "volatilidade é **grudenta**. Depois de um dia agitado vem outro agitado; "
         "depois de uma semana calma, mais calmaria. Não é aleatório, vem em ondas."),
        ("Por que três janelas:",
         "porque o mercado tem gente de horizontes diferentes — o operador do dia, o "
         "gestor da semana, o fundo que pensa no mês. Cada um reage a uma média."),
        ("Por que escolhi ele como adversário:",
         "**de propósito, porque é difícil de bater.** Se eu escolhesse um adversário "
         "fraco, o sentimento ganharia fácil e o resultado não valeria nada. A banca "
         "perguntaria “ganhou de quem?”."),
    ])

    verbete(doc, "2", "Vencer o HAR", [
        ("O que é:",
         "**errar menos que ele.** Não é acurácia em porcentagem — é **erro de "
         "previsão**. Você prevê 795 dias, mede o quanto errou, e compara com o quanto "
         "o HAR errou nos mesmos 795 dias."),
        ("Por que essa é a prova que importa:",
         "porque o HAR **não lê nada**. Se eu coleto 205 mil notícias, rodo um modelo de "
         "linguagem, monto um índice diário — e mesmo assim não erro menos que um modelo "
         "que só olha o preço passado —, então **todo esse trabalho com texto não "
         "acrescentou nada**. O histórico do preço já dizia a mesma coisa."),
        ("O nosso número:",
         "**não vencemos** (valor-p de 0,64). Halousková e Lyócsa vencem em **399 das "
         "404 ações** que testaram, com erro 12,74% menor."),
        ("Mas atenção — a diferença é explicável:",
         "eles usam **404 ações** e medem o sacolejo **de 5 em 5 minutos**; eu uso "
         "**uma ação** e meço **uma vez por dia**. É falta de dado, não ausência de "
         "sinal."),
    ])

    verbete(doc, "3", "Efeito de cauda", [
        ("O que é:",
         "imagine enfileirar os meus 1.988 pregões pelo tamanho do movimento do preço, "
         "do mais parado ao mais violento. No **meio** ficam a maioria — dias comuns, "
         "oscilação pequena. Nas **duas pontas** ficam os raros — o dia de pânico, o dia "
         "de disparada. Essas pontas são as **caudas**. **“Efeito de cauda” significa "
         "que o sentimento só faz diferença nas pontas.**"),
        ("A analogia:",
         "é como comparar a renda de dois bairros. A **média** pode dar diferença enorme "
         "por causa de dois moradores milionários. A **mediana** — o morador do meio — "
         "mostra que os bairros são parecidos. **A diferença existe, mas está "
         "concentrada em pouquíssimos casos.**"),
        ("Como provei:",
         "medindo a relação de duas maneiras. **Pearson** leva em conta o tamanho dos "
         "números e **achou** (−0,1309, valor-p abaixo de 0,0001). **Spearman** joga "
         "fora os tamanhos e só olha a ordem, e **não achou** (−0,0268, valor-p de "
         "0,237). **Quando um acha e o outro não, a relação está nos extremos.**"),
        ("Confirmei por outro caminho:",
         "comparando o terço de dias mais pessimistas com o terço menos pessimista, a "
         "razão entre as **médias** é 1,237 — 24% mais volatilidade. Mas entre as "
         "**medianas** é só 1,048 — 5%. **Cinco vezes menor.**"),
        ("E de fora:",
         "Halousková e Lyócsa têm ganho de 12,74% na média, mas de **14,99% nos dias de "
         "variação extrema**. Mesma conclusão, com 404 ações americanas."),
        ("Por que é a minha tese:",
         "porque explica tudo de uma vez. **O sentimento não move o pregão comum; ele "
         "importa nos extremos.** Isso explica por que a direção não funciona (a maioria "
         "dos dias é comum), por que a média dava resultado fraco, e por que não venço o "
         "HAR no dia a dia."),
    ])

    verbete(doc, "4", "Direção contra volatilidade", [
        ("Direção:",
         "para onde o preço vai — **sobe ou desce**."),
        ("Volatilidade:",
         "o **tamanho do sacolejo**, sem olhar o lado. Um dia que sobe 5% e um que cai "
         "5% têm a **mesma** volatilidade, alta. Um dia que varia 0,2% tem volatilidade "
         "baixa, subindo ou caindo."),
        ("A analogia:",
         "é a diferença entre perguntar **“para onde vai?”** e **“vai balançar muito?”**. "
         "A primeira é sobre direção; a segunda é sobre risco — e é ela que interessa a "
         "bancos, seguradoras e quem precifica seguros de preço."),
        ("Por que importa:",
         "**a direção é praticamente imprevisível** — provei que nem um leitor perfeito "
         "melhoraria. A esperança sempre esteve na volatilidade."),
    ])

    verbete(doc, "5", "Valor-p e “significativo”", [
        ("O que é:",
         "o valor-p responde **“qual a chance de eu ver esse resultado por pura sorte, "
         "se na verdade não houvesse efeito nenhum?”**"),
        ("A analogia:",
         "você jogou uma moeda 10 vezes e deu cara 7. Isso prova que a moeda é viciada? "
         "Não — 7 em 10 acontece por acaso com facilidade. Mas se jogasse 10.000 vezes e "
         "desse cara 7.000, aí sim."),
        ("A régua:",
         "**abaixo de 0,05 conta como resultado; acima, não conta.** Um valor-p de 0,001 "
         "significa 1 chance em 1.000 de ser sorte. Um de 0,64 significa 64 em 100."),
    ])

    verbete(doc, "6", "Validação contra teste — e por que confundi-los engana", [
        ("Validação:",
         "onde você experimenta várias configurações e **escolhe a melhor**."),
        ("Teste:",
         "a prova final, feita **uma vez só**, com a configuração já escolhida."),
        ("A analogia:",
         "validação é o **treino**; teste é o **jogo**. Escolher o melhor jogador vendo "
         "só o treino é receita para decepção."),
        ("Por que isso me pegou:",
         "o número **54,93%** que circulava na minha tabela era de **validação**. No "
         "teste, aquela mesma configuração dá **50,31%**, contra 53,88% da opção mais "
         "simples. **O número correto a apresentar é 54,5%.**"),
        ("Como reconhecer o problema:",
         "quando algo vai muito bem na validação e mal no teste. No meu caso: 56,64% "
         "contra 50,31% — queda de mais de seis pontos. **É a assinatura clássica.**"),
    ])

    verbete(doc, "7", "Fora da amostra", [
        ("O que é:",
         "avaliar o modelo em dados que ele **nunca viu** durante o treinamento."),
        ("A analogia:",
         "é a diferença entre corrigir a prova **com o gabarito na mão** e corrigir "
         "**depois de entregue**. Só a segunda vale."),
        ("Por que importa aqui:",
         "**Mino e Williamson (2025) não fazem isso** — só medem dentro da amostra. Eu "
         "faço, com 795 previsões, cada uma usando apenas o passado. **Eles param onde "
         "eu continuo** — e foi ao continuar que descobri que a relação não vira "
         "previsão."),
    ])

    verbete(doc, "8", "Embedding contra cabeça de sentimento", [
        ("O modelo tem duas partes:",
         "**a compreensão** — ele leu 1,4 milhão de textos financeiros e formou um "
         "entendimento, que vira um resumo numérico chamado **embedding**. E **o "
         "parecer** — ele espreme tudo isso numa palavra só: positivo, negativo ou "
         "neutro. Isso é a **cabeça de sentimento**."),
        ("A analogia:",
         "é um analista brilhante que entende profundamente de mercado, mas que, quando "
         "você pede resposta em uma palavra, responde “ruim” quase sempre. **A falha "
         "está na hora de resumir, não no entendimento.**"),
        ("Por que isso é o achado mais importante:",
         "**todos** os defeitos que auditei estão na cabeça de sentimento — viés de "
         "48,5% de negativos, escore em escala errada, zero pregões de maioria positiva. "
         "**Nenhum** afeta os embeddings."),
        ("A prova, num único artigo:",
         "Hashami e Maldonado testaram o **mesmo FinBERT** das duas formas. Como "
         "classificador de sentimento: **0,5368** — o pior da tabela deles. Como "
         "embedding: **0,6694** — vence a referência. **Treze pontos de diferença, no "
         "mesmo modelo.**"),
    ])

    verbete(doc, "9", "Acurácia contra ganho — a régua certa", [
        ("Acurácia:",
         "de cada 100 pregões, em quantos o modelo acertou. **O problema:** depende do "
         "mercado, do ativo e do período. Comparar entre estudos é enganoso."),
        ("Ganho:",
         "quanto o modelo **com notícias** acerta a mais que o mesmo modelo **sem "
         "notícias**. **Isso sim é comparável**, porque mede a contribuição do texto."),
        ("A analogia:",
         "comparar notas de alunos de escolas diferentes não diz nada. Comparar **quanto "
         "cada um melhorou** depois da aula particular, sim."),
        ("O nosso número:",
         "**ganho de 4,4 pontos percentuais.** A literatura reporta de **2 a 10** "
         "(Nguyen et al., 2015). **Estamos na faixa.** Quando disserem que 54,5% é "
         "pouco, é essa a resposta."),
    ])

    verbete(doc, "10", "Os testes estatísticos que uso", [
        ("Teste binomial:",
         "responde “esse acerto poderia ser sorte?”. Usei para a acurácia direcional."),
        ("McNemar:",
         "compara **dois modelos nos mesmos dias**, olhando só onde eles discordam. "
         "Usei para comparar o índice filtrado com o completo."),
        ("Diebold-Mariano:",
         "responde se um modelo **erra genuinamente menos** que o outro, ou se a "
         "diferença cabe no acaso. É o teste de “vencer o HAR”."),
        ("Bootstrap:",
         "reembaralha os dados milhares de vezes para ver se o resultado se sustenta. "
         "**A analogia:** é refazer a pesquisa 10.000 vezes com sorteios diferentes dos "
         "mesmos dias, e ver se a conclusão muda."),
    ])

    verbete(doc, "11", "Termos de volatilidade", [
        ("Volatilidade realizada:",
         "medir o sacolejo somando os movimentos **dentro do dia**. Halousková usa "
         "pedaços de 5 minutos — 78 medições por dia."),
        ("Estimador de Parkinson:",
         "medir o sacolejo pela **máxima e a mínima** do dia, em vez de só o "
         "fechamento. É o que eu uso, por não ter dado intradiário. **É cerca de cinco "
         "vezes melhor que usar só o fechamento — mas muito pior que os 5 minutos "
         "deles.**"),
        ("GARCH:",
         "modelo clássico que estima a volatilidade reconhecendo que ela vem em ondas. "
         "Uso a versão com **distribuição t-Student**, que admite dias extremos mais "
         "frequentes que o normal — apropriado para a PETR4, cuja curtose é 28,24 "
         "contra 3 da distribuição normal."),
        ("Regressão quantílica:",
         "em vez de medir o efeito **médio**, mede o efeito em cada faixa da "
         "distribuição separadamente. **Foi ela que revelou o efeito de cauda pelo lado "
         "do retorno:** +542 pontos-base nos 5% piores dias, e zero nos dias bons."),
    ])

    A.secao(doc, "12", "Se travar na reunião")

    A.paragrafo(doc,
        "Três frases que resolvem a maioria das perguntas:")

    A.lista(doc, [
        "**Sobre o HAR:** “É um modelo que prevê o sacolejo usando só o histórico do "
        "preço, sem ler nada. Escolhi como adversário de propósito, porque é difícil de "
        "bater — se eu escolhesse um fraco, o resultado não valeria nada.”",
        "**Sobre o efeito de cauda:** “O sentimento não move o pregão comum; ele importa "
        "nos dias extremos. Provei com duas medidas de correlação: uma que enxerga "
        "tamanho acha a relação, e uma que só enxerga ordem não acha. E um estudo com "
        "404 ações americanas chegou ao mesmo lugar.”",
        "**Sobre os meus 54,5%:** “A comparação justa entre estudos não é a acurácia "
        "absoluta, e sim o ganho que a notícia acrescenta a um modelo só de preços. A "
        "literatura dá de 2 a 10 pontos percentuais. O meu é 4,4.”",
    ])

    doc.save(SAIDA)
    print(f"[OK] {SAIDA}")


if __name__ == "__main__":
    main()
