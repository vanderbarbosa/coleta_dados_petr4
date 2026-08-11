# -*- coding: utf-8 -*-
# ==============================================================================
#   Gera a versão ABNT (.docx) da resposta às orientações da mentoria de
#   29/07/2026 com o Prof. Dr. Emerson Cabrera Paraiso.
#
#   Entrada conceitual : orientacoes/orientacoes.txt (7 orientações)
#   Fontes primárias   : _artigo_bwaif_24960.pdf, _monografia_texto.txt,
#                        _teles2025.pdf, HuggingFace Hub API, OpenAlex,
#                        Semantic Scholar
#   Saída              : RESPOSTA_ORIENTACOES_2026-08-10.docx
#
#   Reaproveita src/comum/abnt_docx.py (NBR 14724/6023/6024/10520).
# ==============================================================================
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(RAIZ / "src" / "comum"))

import abnt_docx as A  # noqa: E402

FONTE_AUTOR = "Elaborado pelo autor (2026)"
SAIDA = AQUI / "RESPOSTA_ORIENTACOES_2026-08-10.docx"


def main() -> None:
    doc = A.novo_documento()

    # ─── Capa ────────────────────────────────────────────────────────────────
    A.capa(
        doc,
        titulo="Resposta às orientações da mentoria de 29 de julho de 2026",
        subtitulo="Levantamento sobre o FinBERT-PT-BR, encoders alternativos e "
                  "literatura correlata",
        autor="Vanderlei Barbosa da Silva",
        orientador="Orientador: Prof. Dr. Julio Cesar Nievola",
        instituicao="PUCPR — Programa de Pós-Graduação em Informática (PPGIa)",
        descricao="Documento elaborado em atendimento às sete orientações registradas "
                  "pelo Prof. Dr. Emerson Cabrera Paraiso na mentoria de 29 de julho de "
                  "2026, para apresentação na mentoria de 10 de agosto de 2026. "
                  "Vincula-se à dissertação “O Impacto do Sentimento de Notícias "
                  "Financeiras na Previsão de Direção e Volatilidade do Ativo PETR4”.",
    )

    # ─── 1 Nota metodológica ─────────────────────────────────────────────────
    A.secao(doc, "1", "Nota metodológica e delimitação de escopo")
    A.paragrafo(doc,
        "Este documento responde, item a item, às sete orientações registradas no arquivo "
        "orientacoes.txt. Todas as afirmações foram obtidas de fontes primárias: o PDF "
        "integral do artigo publicado nos Anais do BWAIF, o PDF integral da monografia do "
        "autor do modelo, os arquivos de configuração do repositório HuggingFace e as APIs "
        "bibliográficas OpenAlex e Semantic Scholar. Os arquivos-fonte permanecem na pasta "
        "orientacoes/, de modo que qualquer afirmação possa ser reconferida sem nova coleta.")
    A.paragrafo(doc,
        "Três limitações precisam ser declaradas, por afetarem a completude de partes "
        "específicas da entrega.")
    A.lista(doc, [
        "**O vídeo da mentoria não foi transcrito.** O arquivo monitoria_Emerson_2026-07-29.mp4 "
        "(227 MB) não pôde ser processado nesta máquina: não há ffmpeg instalado e a instalação "
        "de um transcritor automático esbarrou em falha pré-existente da biblioteca PyTorch "
        "(Seção 9.3). O trabalho foi conduzido a partir de orientacoes.txt, descrito pelo "
        "mestrando como o compilado das orientações. Recomenda-se conferir se o vídeo contém "
        "orientação adicional não registrada no arquivo de texto.",
        "**A lista integral das citações do Google Scholar não pôde ser extraída.** O endereço "
        "indicado na orientação n. 7 informa “12 resultados”, mas responde com CAPTCHA a "
        "qualquer acesso automatizado. A Seção 8 apresenta sete trabalhos citantes integralmente "
        "verificados por OpenAlex e Semantic Scholar. A diferença é esperada: o Google Scholar "
        "indexa trabalhos de conclusão de curso, dissertações em repositórios institucionais e "
        "preprints que as bases com DOI não cobrem.",
        "**Separação entre evidência e recomendação.** As Seções 2 a 8 relatam o que a literatura "
        "diz. As Seções 9 e 10 são recomendações de autoria própria, derivadas do cruzamento "
        "entre essa literatura e o estado atual dos dados e do código da pesquisa.",
    ])

    A.secao(doc, "1.1", "Sobre a suspensão da rotulagem manual", nivel=2)
    A.paragrafo(doc,
        "A orientação de suspender a rotulagem manual encontra respaldo direto na literatura "
        "examinada, e por uma razão mais precisa do que a inicialmente formulada. O argumento "
        "apresentado na mentoria foi o da qualificação do anotador: a rotulagem de sentimento "
        "financeiro exigiria um especialista em finanças para produzir rótulos com validade de "
        "construto.")
    A.paragrafo(doc,
        "A monografia de Santos (2022, Seção 4.2.3) mostra que o próprio autor do FinBERT-PT-BR "
        "não empregou especialistas em finanças. Empregou “três pessoas, sendo duas com formação "
        "em engenharia e uma com formação em linguística”. O que garantiu a qualidade do gabarito "
        "não foi a formação dos anotadores, mas três controles metodológicos: uma definição "
        "operacional de rótulo ancorada em consequência econômica; dupla anotação de todo texto, "
        "com descarte agressivo do que não obteve concordância — dos 1.000 textos anotados, 497 "
        "(49,7%) foram descartados; e medição formal de concordância por percentual e por "
        "Krippendorff’s alpha, com 90,4% e alfa igual a 0,88.")
    A.citacao_longa(doc,
        "Classifique a notícia considerando se o texto implicaria em uma rentabilidade Positiva, "
        "Negativa ou Neutra. “Não se aplica” para textos não relacionados a finanças, de políticos "
        "ou sem sentido.",
        "Santos (2022, p. 42)")
    A.paragrafo(doc,
        "Isso reposiciona a orientação de forma construtiva. O problema do nosso gabarito não é "
        "necessariamente quem rotula, mas a ausência dos três controles acima. O conjunto-ouro "
        "atual tem 300 manchetes rotuladas por um único anotador, sem segunda anotação e, "
        "portanto, sem qualquer métrica de concordância — o que impede afirmar que o gabarito é "
        "confiável e, por consequência, invalida o seu uso como referência para escolher entre "
        "encoders. Esse é um argumento mais forte para suspender a rotulagem na forma atual do "
        "que o argumento da qualificação, e é o que se recomenda levar à mentoria de 10 de agosto.")

    # ─── 2 Sumário executivo ─────────────────────────────────────────────────
    A.secao(doc, "2", "Sumário executivo")
    A.tabela_abnt(doc, 1, "Sete conclusões do levantamento",
        ["N.", "Conclusão"],
        [
            ["1", "O artigo indicado na orientação n. 5 é o próprio artigo do FinBERT-PT-BR "
                  "(SANTOS; BIANCHI; COSTA, 2023). As orientações 5 e 6 tratam do mesmo trabalho, "
                  "visto como artigo e como artefato publicado."],
            ["2", "O FinBERT-PT-BR foi treinado e validado sobre notícias gerais de mercado, com "
                  "acurácia de 0,76 e F1 de 0,73. O nosso uso — manchetes de um ativo específico — "
                  "é uma transferência de domínio não testada pelo autor, o que explica os 58% "
                  "medidos contra o conjunto-ouro."],
            ["3", "Nenhum dos trabalhos citantes verificados aplicou o FinBERT-PT-BR à tarefa "
                  "financeira para a qual foi construído. Apenas um o executou, e fora do domínio "
                  "financeiro (documentos históricos). Trata-se de lacuna favorável à dissertação."],
            ["4", "Os três testes de encoder realizados (BERTimbau base, BERTimbau large e "
                  "Albertina-100M) foram inconclusivos por defeito de protocolo, não por "
                  "inferioridade dos modelos: 300 exemplos, 3 épocas, sem adaptação de domínio e "
                  "sem gradual unfreezing."],
            ["5", "O caminho de maior relação custo-benefício não é trocar de encoder, mas "
                  "replicar a primeira etapa de Santos: adaptação de domínio por masked language "
                  "modeling sobre o corpus de aproximadamente 205 mil notícias. Sendo "
                  "self-supervised, não consome rótulo algum — é compatível com a suspensão da "
                  "rotulagem."],
            ["6", "O config.json publicado do FinBERT-PT-BR contém label2id inconsistente com o "
                  "id2label. O Script 03 possui mapeamento de contingência invertido em relação ao "
                  "modelo real. Hoje esse caminho não é acionado, mas constitui risco de "
                  "reprodutibilidade."],
            ["7", "O ambiente Python local está com o PyTorch inoperante (falha de carregamento de "
                  "DLL). Nenhum experimento de encoder pode ser executado nesta máquina antes da "
                  "correção."],
        ], fonte=FONTE_AUTOR)

    # ─── 3 Tarefa 1 ──────────────────────────────────────────────────────────
    A.secao(doc, "3", "Orientação 1 — o BERT financeiro em pesquisas diversas")
    A.paragrafo(doc,
        "A ideia de um BERT financeiro nasce da constatação que Araci (2019) formalizou: modelos "
        "de linguagem de propósito geral erram sistematicamente em textos financeiros porque o "
        "vocabulário do domínio inverte polaridades. Termos como “queda do dólar”, “corte de "
        "juros”, “provisão” ou “alavancagem” têm carga que depende do contexto financeiro, e não "
        "da conotação usual da palavra. Araci propôs partir de um BERT genérico e continuar o "
        "pré-treinamento sobre corpus financeiro antes do ajuste para a tarefa final.")
    A.paragrafo(doc,
        "Essa receita de duas etapas — adaptação de domínio por modelagem de linguagem mascarada, "
        "seguida de ajuste fino supervisionado — é a coluna vertebral de toda a família, e é "
        "exatamente a receita que Santos, Bianchi e Costa (2023) transportam para o português "
        "brasileiro.")

    A.secao(doc, "3.1", "O uso pelo próprio autor", nivel=2)
    A.tabela_abnt(doc, 2, "Aplicações do FinBERT-PT-BR pelo próprio autor",
        ["Tarefa", "Como foi feita", "Resultado"],
        [
            ["Modelagem de linguagem",
             "Fine-tuning do BERTimbau com 1.428.867 sentenças; 2 épocas em 11 h; lr 2e-5; "
             "máscara 15%; 2× Nvidia T4",
             "Perplexidade 1,24 contra 1,51 do BERTimbau"],
            ["Classificação de sentimento",
             "Gradual unfreezing das 11 camadas; lr 5e-6; 11 épocas; validação cruzada 5-fold",
             "Acurácia 0,76 e F1 0,73"],
            ["Índice de sentimento",
             "Índice = (Pos − Neg) / (Pos + Neu + Neg) em janela [t−k, t]",
             "Aderência qualitativa a oito eventos econômicos brasileiros"],
            ["Estratégia de investimento",
             "Seleção mensal das ações com maior correlação negativa com o índice",
             "683% acumulados em 8 anos contra 254% do Ibovespa"],
            ["Relação macroeconômica (só na monografia)",
             "Correlação entre índice de sentimento e inflação; regressão linear com fatores",
             "Relação documentada nas Figuras 18 e Tabela 5"],
        ], fonte="Elaborado pelo autor (2026) a partir de Santos, Bianchi e Costa (2023) e Santos (2022)")

    A.secao(doc, "3.2", "Rigor estatístico a replicar", nivel=2)
    A.paragrafo(doc,
        "Um ponto da monografia ausente do artigo e diretamente aproveitável: Santos não se "
        "contentou com a comparação pontual de acurácias. Aplicou bootstrapping (EFRON, 1992) "
        "sobre o conjunto de teste para estimar intervalos de confiança de acurácia e F1, "
        "verificou que os intervalos de 80% do FinBERT-PT-BR não se sobrepõem aos dos "
        "concorrentes, e construiu um teste Z sobre a distribuição empírica reamostrada, obtendo "
        "p-valor numericamente igual a zero.")
    A.paragrafo(doc,
        "Isso responde antecipadamente a uma crítica previsível da banca sobre a nossa tabela de "
        "comparação de encoders, que hoje reporta diferenças de −1,67, −5,33 e −16,00 pontos "
        "percentuais sem qualquer teste de significância. Com n igual a 300 e desvios-padrão "
        "entre 2,7 e 8,4 pontos, a diferença de −1,67 pontos do BERTimbau large é seguramente "
        "indistinguível de zero. **Recomenda-se adotar o protocolo de bootstrap antes de levar "
        "essa tabela à banca.**")

    A.secao(doc, "3.3", "Outros usos de BERT financeiro na literatura", nivel=2)
    A.lista(doc, [
        "**Hiew et al. (2019)** — combinam índice de sentimento construído com BERT e um LSTM "
        "para prever retorno de ações; é a referência de onde Santos extrai a fórmula do índice.",
        "**Abílio, Coelho e Silva (2024)** — reconhecimento de entidades nomeadas em transcrições "
        "de earnings calls de bancos brasileiros. Modelos BERT superam consistentemente os T5, e "
        "o BERTimbau monolíngue supera o PTT5. Registram que os modelos generativos alteraram "
        "valores monetários e percentuais nas sentenças geradas.",
        "**Januário et al. (2022)** — análise de sentimento aplicada a notícias do mercado de "
        "ações brasileiro; trabalho da literatura nacional mais próximo do nosso objeto.",
    ])

    # ─── 4 Tarefa 2 ──────────────────────────────────────────────────────────
    A.secao(doc, "4", "Orientação 2 — como os trabalhos utilizaram o FinBERT-PT-BR")
    A.paragrafo(doc,
        "**Seção corrigida em 3 de agosto de 2026, após a leitura integral dos textos.** A redação "
        "original afirmava que nenhum trabalho havia reutilizado o modelo; a verificação nos textos "
        "completos mostrou que um deles o executou. A análise citação por citação, com os trechos "
        "literais transcritos, está no documento CITACOES_E_GAPS_2026-08-10.")
    A.paragrafo(doc,
        "**Dos sete trabalhos citantes verificados, apenas um executou o FinBERT-PT-BR — e fora do "
        "domínio financeiro.** Błoch, Santana e Amantino (2026) o utilizaram numa máquina de comitê, "
        "combinado com o pysentimiento, para analisar correspondência colonial portuguesa dos "
        "séculos XVII e XVIII. **Nenhum trabalho o aplicou à tarefa financeira para a qual foi "
        "construído.**")
    A.paragrafo(doc,
        "Nos seis restantes, o padrão de citação é conceitual ou de delimitação: o trabalho de "
        "Santos é invocado para definir análise de sentimento, para sustentar a escassez de "
        "trabalhos em português, para posicionar o modelo numa taxonomia, ou para que o autor diga "
        "em que o próprio trabalho difere dele — e não para ser executado.")
    A.paragrafo(doc,
        "O caso mais ilustrativo é Teles e Figueiredo (2025). Apesar de ser um artigo brasileiro, "
        "de análise de sentimento, de notícias, de mercado financeiro, e de citar Santos et al. "
        "(2023) duas vezes na introdução, o trabalho não inclui o FinBERT-PT-BR entre os modelos "
        "avaliados. Compara SVM, Random Forest e MLP contra Gemma, DeBERTa, DeBERTaV3, "
        "XLM-RoBERTa, BART e Gemini, e o faz sobre três conjuntos de dados em inglês.")
    A.paragrafo(doc,
        "Isso caracteriza lacuna de literatura verificável e defensável em banca: o FinBERT-PT-BR "
        "é um artefato com 177.384 downloads mensais no HuggingFace, mas com adoção acadêmica "
        "documentada quase nula na tarefa para a qual foi construído. Esta dissertação é, pelo "
        "que o levantamento alcança, um dos primeiros trabalhos a aplicá-lo a um ativo específico "
        "da B3 com validação contra gabarito humano e avaliação de impacto sobre previsão de "
        "direção e volatilidade.")
    A.paragrafo(doc,
        "A afirmação está limitada aos trabalhos verificáveis. Os cinco trabalhos que o Google "
        "Scholar contabiliza e que as bases com DOI não indexam podem conter uso aplicado; o "
        "procedimento para fechar essa verificação consta da Seção 8.3 e deve ser executado antes "
        "de a afirmação entrar na versão final da dissertação.")

    # ─── 5 Tarefa 3 ──────────────────────────────────────────────────────────
    A.secao(doc, "5", "Orientação 3 — há outro encoder BERT melhor para a pesquisa?")
    A.secao(doc, "5.1", "O que já foi testado, e por que os testes não decidem", nivel=2)
    A.tabela_abnt(doc, 3, "Resultados dos encoders testados contra o conjunto-ouro (n = 300)",
        ["Encoder", "Acurácia (%)", "± dp", "F1-macro (%)", "Kappa", "Δ (p.p.)"],
        [
            ["FinBERT-PT-BR (linha de base)", "58,00", "4,88", "57,63", "0,370", "—"],
            ["BERTimbau large", "56,33", "5,52", "54,26", "0,330", "−1,67"],
            ["BERTimbau base", "52,67", "8,41", "48,14", "0,261", "−5,33"],
            ["Albertina-100M PT-BR", "42,00–45,67", "2,67–6,20", "25,20–29,17", "0,033–0,095", "−12,33 a −16,00"],
        ],
        fonte="Elaborado pelo autor (2026) a partir de conjunto_ouro/resultado_encoders_petr4.csv "
              "e experimentos_encoder/")
    A.paragrafo(doc,
        "Esses números não sustentam a conclusão de que o FinBERT-PT-BR é o melhor encoder. "
        "Sustentam apenas que, sob o protocolo empregado, os concorrentes não convergiram. As "
        "razões são identificáveis e todas corrigíveis.")
    A.lista(doc, [
        "**Volume de rótulos insuficiente.** Trezentos exemplos divididos em cinco folds deixam "
        "cerca de 240 exemplos de treino por fold, aproximadamente 80 por classe. Santos usou 503 "
        "e obteve convergência porque partiu de modelo de linguagem já adaptado ao domínio.",
        "**Épocas insuficientes.** Foram usadas 3 épocas; Santos usou 11.",
        "**Ausência de gradual unfreezing.** O log do experimento mostra a assinatura clássica do "
        "colapso para a classe majoritária: nos folds 2, 3 e 5 o kappa foi exatamente 0,000 e o "
        "F1-macro ficou entre 25% e 29%.",
        "**Taxa de aprendizado provavelmente inadequada.** Santos usa lr igual a 5e-6 na etapa de "
        "sentimento, uma ordem de grandeza abaixo do usual, justamente para evitar o esquecimento "
        "catastrófico.",
        "**Comparação assimétrica.** O FinBERT-PT-BR entra já treinado para sentimento financeiro; "
        "os concorrentes entram como encoders crus, com cabeça de classificação inicializada "
        "aleatoriamente. Não é comparação entre encoders, e sim entre um modelo pronto e três "
        "modelos treinados do zero com poucos dados.",
        "**Porte inadequado.** Foi testado o Albertina 100M, a menor variante da família. As "
        "variantes competitivas são a de 900M e a de 1,5 bilhão de parâmetros.",
    ])
    A.paragrafo(doc,
        "**Conclusão da orientação 3:** ainda não se sabe se há encoder melhor, porque o protocolo "
        "aplicado até aqui não é capaz de responder à pergunta.")

    A.secao(doc, "5.2", "Panorama dos encoders candidatos", nivel=2)
    A.tabela_abnt(doc, 4, "Encoders candidatos (dados verificados no HuggingFace em 3 ago. 2026)",
        ["Modelo", "Arquitetura", "Porte", "Downloads/mês", "Situação"],
        [
            ["lucas-leme/FinBERT-PT-BR", "BERT + cabeça de sentimento", "110M", "177.384", "Em uso"],
            ["neuralmind/bert-base-portuguese-cased", "BERT", "110M", "502.821", "Testado"],
            ["neuralmind/bert-large-portuguese-cased", "BERT", "335M", "1.702.587", "Testado"],
            ["PORTULAN/albertina-100m-ptbr", "DeBERTa", "100M", "828", "Testado (porte inadequado)"],
            ["PORTULAN/albertina-900m-ptbr", "DeBERTa-v2", "900M", "357", "Candidato"],
            ["PORTULAN/albertina-1b5-ptbr", "DeBERTa-v2", "1,5B", "14", "Candidato (custo alto)"],
            ["ricardoz/BERTugues-base-portuguese-cased", "BERT", "110M", "355", "Candidato"],
            ["sagui-nlp/debertinha-ptbr-xsmall", "DeBERTa-v2", "~40M", "689", "Candidato leve"],
            ["turing-usp/FinBertPTBR", "BERT", "110M", "47", "Não usar — depreciado"],
            ["microsoft/mdeberta-v3-base", "DeBERTa-v3 multilíngue", "280M", "4.290.788", "Controle multilíngue"],
            ["FacebookAI/xlm-roberta-large", "XLM-R", "550M", "7.787.512", "Linha de base multilíngue"],
            ["eliasjacob/ModernBERT-large-portuguese", "ModernBERT", "395M", "5", "Experimental — não recomendado"],
        ], fonte="Elaborado pelo autor (2026) a partir da HuggingFace Hub API")

    A.secao(doc, "5.3", "Observação sobre o turing-usp/FinBertPTBR", nivel=2)
    A.paragrafo(doc,
        "O modelo turing-usp/FinBertPTBR, que consta como candidato no registro de projeto, é o "
        "antecessor descontinuado do modelo já utilizado. O próprio model card traz o aviso em "
        "destaque.")
    A.citacao_longa(doc,
        "FinBertPTBR : Financial Bert PT BR (Depreciated model) — Newer version available on "
        "https://huggingface.co/lucas-leme/FinBERT-PT-BR",
        "Model card de turing-usp/FinBertPTBR (2023)")
    A.paragrafo(doc,
        "Entre os autores listados está Lucas Leme, ao lado de Vinicius Carmo, Julia Pocciotti e "
        "Luísa Heise — os mesmos nomes que aparecem nos agradecimentos da monografia de 2022. "
        "Trata-se de trabalho anterior do grupo Turing USP, do qual o FinBERT-PT-BR é a evolução "
        "direta. Deve ser retirado da lista de candidatos e, se citado, citado como antecedente "
        "histórico.")

    A.secao(doc, "5.4", "Recomendação", nivel=2)
    A.paragrafo(doc,
        "A recomendação não é trocar de encoder. É replicar a etapa que Santos executou e que foi "
        "omitida nos nossos experimentos: **adaptação de domínio por masked language modeling** — "
        "continuar o pré-treinamento, com máscara de 15% e lr igual a 2e-5, de um encoder sobre o "
        "corpus de aproximadamente 205 mil notícias de PETR4, e só então ajustar a cabeça de "
        "sentimento.")
    A.lista(doc, [
        "**É self-supervised: não consome um único rótulo.** É integralmente compatível com a "
        "suspensão da rotulagem manual e é a única linha de trabalho substantiva que pode avançar "
        "sob essa restrição.",
        "**É a etapa de maior ganho documentado.** Foi ela que levou a perplexidade de 1,51 para "
        "1,24 e que viabilizou a convergência do classificador com apenas 503 rótulos.",
        "**É auditável sem gabarito.** A perplexidade é métrica intrínseca, medida em holdout de "
        "notícias não vistas, produzindo resultado reportável à banca sem depender do conjunto-ouro.",
        "**Especializa o domínio duas vezes.** Santos adaptou ao mercado financeiro brasileiro em "
        "geral; adaptaríamos ao subdomínio Petrobras, petróleo e estatais, onde estão os termos "
        "que mais interessam à pesquisa.",
    ])
    A.paragrafo(doc,
        "Ordem de prioridade sugerida: (1) MLM de domínio sobre lucas-leme/FinBERT-PT-BR; (2) MLM "
        "de domínio sobre bert-large-portuguese-cased, replicando a receita completa de Santos em "
        "porte maior; (3) Albertina 900M somente se (1) e (2) forem executados e o orçamento "
        "computacional permitir, jamais o 100M novamente; (4) mdeberta-v3-base como linha de base "
        "multilíngue de controle.")

    # ─── 6 Tarefa 4 ──────────────────────────────────────────────────────────
    A.secao(doc, "6", "Orientação 4 — há trabalhos com o mesmo objetivo?")
    A.paragrafo(doc,
        "O objeto desta dissertação tem quatro elementos simultâneos: português brasileiro; ativo "
        "único da B3; previsão de direção e de volatilidade; e fusão de sentimento com modelo "
        "econométrico (GARCH) e aprendizado de máquina. O mapeamento abaixo mostra onde cada "
        "trabalho para.")
    A.tabela_abnt(doc, 5, "Comparação com trabalhos correlatos",
        ["Trabalho", "PT-BR", "Ativo único", "Direção", "Volatilidade", "Fusão GARCH+ML"],
        [
            ["Santos, Bianchi e Costa (2023)", "Sim", "Não", "Não", "Não", "Não"],
            ["Teles e Figueiredo (2025)", "Não", "Não", "Não", "Não", "Não"],
            ["Januário et al. (2022)", "Sim", "Não", "Parcial", "Não", "Não"],
            ["Abílio, Coelho e Silva (2024)", "Sim", "Não", "Não", "Não", "Não"],
            ["Hiew et al. (2019)", "Não", "Não", "Sim", "Não", "Não"],
            ["Imai et al. (2024)", "Sim", "—", "Não", "Não", "Não"],
            ["Reichert e Perlin (2025)", "Parcial", "Não", "Não", "Não", "Não"],
            ["Esta dissertação", "Sim", "PETR4", "Sim", "Sim", "Sim"],
        ], fonte=FONTE_AUTOR)
    A.paragrafo(doc,
        "**Nenhum dos trabalhos examinados prevê volatilidade.** Todos operam sobre direção, "
        "retorno ou estratégia de carteira. Isso converge com o achado já registrado na revisão da "
        "banca de julho de 2026: a previsão de direção fica próxima do acaso, e o ganho real do "
        "sentimento está na volatilidade. O que era resultado empírico isolado passa a ter "
        "respaldo de lacuna de literatura — a direção fica próxima do acaso em toda a literatura, "
        "e é por isso que os trabalhos migram para carteira, índice agregado ou comparação de "
        "classificadores, e não para o ativo isolado.")
    A.paragrafo(doc,
        "**Recomendação editorial:** a volatilidade deve deixar de ser tratada como resultado "
        "secundário e passar a ser a contribuição principal da dissertação, com a direção "
        "reposicionada como resultado negativo devidamente reportado.")

    # ─── 7 Tarefa 5 ──────────────────────────────────────────────────────────
    A.secao(doc, "7", "Orientação 5 — artigo SBC/BWAIF n. 24960")
    A.paragrafo(doc,
        "**Constatação preliminar: o artigo do link é o artigo do FinBERT-PT-BR**, isto é, o "
        "trabalho que fundamenta o modelo já utilizado no Script 03 da pipeline.")

    A.secao(doc, "7.1", "Resumo do artigo", nivel=2)
    A.citacao_longa(doc,
        "SANTOS, L. L.; BIANCHI, R. A. C.; COSTA, A. H. R. FinBERT-PT-BR: Análise de Sentimentos "
        "de Textos em Português do Mercado Financeiro. In: BRAZILIAN WORKSHOP ON ARTIFICIAL "
        "INTELLIGENCE IN FINANCE (BWAIF), 2., 2023. Anais [...]. Porto Alegre: SBC, 2023. "
        "p. 144-155. DOI: 10.5753/bwaif.2023.231151.",
        "Referência completa (NBR 6023)")
    A.paragrafo(doc,
        "Afiliações: Escola Politécnica da USP (Santos e Costa) e Centro Universitário FEI "
        "(Bianchi). Fomento: CNPq, processo n. 310085/2020-9. O objetivo declarado é apresentar um "
        "modelo de linguagem do estado da arte para o mercado financeiro em português do Brasil e, "
        "a partir dele, um classificador de sentimento, demonstrando que este viabiliza a "
        "construção de sinais para análise e estratégias de investimento.")
    A.paragrafo(doc,
        "**Nota terminológica de consequência prática.** O artigo distingue dois artefatos: "
        "FinBERT-PT-BR é o modelo de linguagem adaptado ao domínio, e SentFinBERT-PT-BR é o "
        "classificador de sentimento derivado dele. O repositório HuggingFace publica um único "
        "artefato, sob o nome FinBERT-PT-BR, que é na verdade o SentFinBERT-PT-BR — a arquitetura "
        "declarada no config.json é BertForSequenceClassification, com três rótulos. O modelo de "
        "linguagem puro não foi publicado. As implicações constam da Seção 7.4.")
    A.paragrafo(doc,
        "**Etapa 1 — modelo de linguagem.** Coleta por web scraping com Scrapy sobre Valor "
        "Econômico, Exame e InfoMoney, totalizando 2,7 milhões de sentenças entre 2006 e 2022 e "
        "130 milhões de palavras. Após limpeza por expressões regulares restaram 1,6 milhão de "
        "sentenças; após filtro de 512 tokens, 1.428.867. Treinamento em PyTorch e HuggingFace, "
        "partindo dos pesos do BERTimbau, no Kaggle com 30 GB de RAM e duas GPU Nvidia T4, batch "
        "size 16, duas épocas em onze horas, lr 2e-5 e máscara de 15%. Avaliação por perplexidade "
        "em amostra de 100 mil sentenças não vistas: 1,24 contra 1,51 do BERTimbau.")
    A.paragrafo(doc,
        "**Etapa 2 — classificador de sentimento.** Anotação por três pessoas, cada texto anotado "
        "por ao menos duas, com as categorias positivo, negativo, neutro e “não se aplica”. De "
        "1.000 textos anotados, 497 foram descartados, restando 503: 160 positivos, 203 negativos "
        "e 140 neutros. Concordância percentual de 90,4% e Krippendorff’s alpha de 0,88. "
        "Treinamento com gradual unfreezing das onze camadas de encoder, lr 5e-6, onze épocas e "
        "validação cruzada com cinco divisões sobre 70% da base, com teste nos 30% restantes.")
    A.tabela_abnt(doc, 6, "Resultados dos modelos de classificação de texto",
        ["Modelo", "Acurácia", "F1-Score"],
        [
            ["Random Forest com TF-IDF", "0,45", "0,35"],
            ["FinBERT (EN) sobre texto traduzido", "0,67", "0,67"],
            ["Sent-BERTimbau", "0,67", "0,63"],
            ["SentFinBERT-PT-BR", "0,76", "0,73"],
        ], fonte="Santos, Bianchi e Costa (2023, Tabela 3)")
    A.paragrafo(doc,
        "As aplicações demonstradas são o índice de sentimento, validado qualitativamente contra "
        "oito eventos da economia brasileira, e a estratégia “apostando contra o sentimento”, com "
        "683% de retorno acumulado em oito anos contra 254% do Ibovespa. Todos os trabalhos "
        "futuros propostos pelo autor apontam para o que esta dissertação faz: base maior e mais "
        "específica para o modelo de linguagem, mais textos rotulados com concordância alta, "
        "aprimoramento do cálculo do índice, aplicação da metodologia a setores específicos da "
        "bolsa, e relação do índice com dados macroeconômicos.")

    A.secao(doc, "7.2", "Relação com a pesquisa e o que podemos usar", nivel=2)
    A.tabela_abnt(doc, 7, "Elementos diretamente aproveitáveis, em ordem de valor",
        ["N.", "O que aproveitar", "Onde aplicar"],
        [
            ["1", "Receita completa de adaptação de domínio (MLM, máscara 15%, lr 2e-5, filtro de "
                  "512 tokens, perplexidade)", "Novo experimento sobre o corpus de ~205 mil notícias"],
            ["2", "Protocolo de ajuste fino (gradual unfreezing, lr 5e-6, 11 épocas, CV 5-fold)",
             "Corrigir os experimentos de encoder hoje inconclusivos"],
            ["3", "Protocolo de anotação em seis etapas (monografia, Seção 2.3.1)",
             "Refundar o conjunto-ouro quando a rotulagem for retomada"],
            ["4", "Categoria “não se aplica” e descarte por discordância",
             "O gabarito já registra relevância; falta a categoria de descarte"],
            ["5", "Krippendorff’s alpha e percentual de concordância",
             "Métrica hoje inexistente e que a banca cobrará"],
            ["6", "Bootstrapping e teste Z sobre distribuição empírica",
             "Dar significância estatística à tabela de comparação de encoders"],
            ["7", "Fórmula do índice de sentimento", "Comparar formalmente com o ISM e documentar a escolha"],
            ["8", "Modelagem de tópicos e zero-shot para pré-selecionar textos",
             "Reduzir o custo da rotulagem quando ela for retomada"],
            ["9", "Validação qualitativa contra eventos econômicos", "Replicar o rigor da Figura 3 do artigo"],
            ["10", "Benchmark declarado de 0,76 e 0,73", "Contraste explícito com os 58% medidos"],
        ], fonte=FONTE_AUTOR)

    A.secao(doc, "7.3", "Sobre a diferença entre 0,76 e 0,58", nivel=2)
    A.paragrafo(doc,
        "A diferença entre a acurácia declarada pelo autor e a medida contra o conjunto-ouro "
        "(0,58, kappa 0,371) não indica erro de implementação. Indica transferência de domínio não "
        "testada pelo autor, por três razões conjugadas: a unidade textual é distinta — Santos "
        "avaliou sentenças de notícia, avaliamos manchetes, mais curtas e mais ambíguas; o escopo "
        "é distinto — Santos avaliou notícias gerais de mercado, avaliamos notícias de um ativo "
        "específico, em que a polaridade frequentemente depende de conhecimento contextual sobre a "
        "empresa; e o gabarito é distinto — o de Santos passou por dupla anotação com descarte de "
        "49,7% dos casos, o nosso não.")
    A.paragrafo(doc,
        "Trata-se de contribuição publicável: documentar a degradação de desempenho de um modelo "
        "de sentimento financeiro em português quando transferido de notícias gerais para um ativo "
        "específico. Recomenda-se elevá-la à condição de resultado da dissertação, e não tratá-la "
        "como limitação a ser justificada.")

    A.secao(doc, "7.4", "Resumo compilado das referências do artigo", nivel=2)
    A.paragrafo(doc,
        "A lista de referências do artigo contém 28 entradas. Todas foram catalogadas segundo os "
        "oito campos solicitados na orientação 5.C — referência, encoders e tecnologias, objetivo, "
        "resultados, aplicação, relação com a pesquisa, o que aproveitar e data. A tabela integral "
        "está no arquivo referencias_artigo_bwaif_24960.csv, acompanhada de três referências "
        "adicionais presentes somente na monografia e diretamente acionáveis no contexto atual. "
        "A versão narrativa completa, com comentário por referência, consta do documento "
        "RESPOSTA_ORIENTACOES_2026-08-10.md, Seção 7.3.")
    A.tabela_abnt(doc, 8, "Balanço da análise das 28 referências do artigo",
        ["Grau de relação", "Qtd.", "Referências"],
        [
            ["Muito alta", "4", "Hiew et al. (2019); Januário et al. (2022); Artstein e Poesio "
                                "(2008); Krippendorff (2018)"],
            ["Alta", "11", "Devlin et al. (2018); Souza et al. (2020); Araci (2019); Sun et al. "
                           "(2019); Man et al. (2019); Tan et al. (2023); Bollen et al. (2011); "
                           "Pagolu et al. (2016); Lo (2004); Medeiros e Borges (2019); de Souza "
                           "et al. (2021)"],
            ["Média-alta / média", "8", "Vaswani et al. (2017); Chen et al. (1998); Pang e Lee "
                                        "(2004); Liu (2012); Kordonis et al. (2016); Kraaijeveld "
                                        "e De Smedt (2020); Junjie e Mengoni (2020); Ardia et al. "
                                        "(2015)"],
            ["Baixa", "5", "Manning e Schütze (1999); Otabek e Choi (2022); Silva (2018); Pereira "
                           "(2019); Xavier et al. (2020)"],
            ["Exclusivas da monografia", "3", "Poursabzi-Sangdeh e Boyd-Graber (2015); Alcoforado "
                                              "et al. (2022); Efron (1992)"],
        ], fonte=FONTE_AUTOR)
    A.paragrafo(doc,
        "Quinze referências, isto é, 54% do total, têm relação alta ou muito alta com a "
        "dissertação. Recomenda-se incorporar ao referencial teórico, prioritariamente, as quatro "
        "de relação muito alta e as três exclusivas da monografia.")
    A.paragrafo(doc,
        "**Alerta de referenciação.** Consta do registro de projeto um plano de enriquecimento "
        "capítulo a capítulo “usando a tese da Silva (2018)”. A Silva (2018) citada por Santos é "
        "sobre percepção de corrupção no Twitter e muito provavelmente não é a mesma obra. "
        "Recomenda-se conferir a referência completa antes de qualquer citação cruzada, sob pena "
        "de erro na versão final.")

    # ─── 8 Tarefa 6 e 7 ──────────────────────────────────────────────────────
    A.secao(doc, "8", "Orientações 6 e 7 — repositório HuggingFace e trabalhos citantes")
    A.secao(doc, "8.1", "Ficha técnica do modelo", nivel=2)
    A.tabela_abnt(doc, 9, "Ficha técnica de lucas-leme/FinBERT-PT-BR (verificada em 3 ago. 2026)",
        ["Atributo", "Valor"],
        [
            ["Arquitetura", "BertForSequenceClassification"],
            ["Camadas ocultas", "12"],
            ["Dimensão oculta", "768"],
            ["Vocabulário", "29.794 tokens"],
            ["Posições máximas", "512 tokens"],
            ["Parâmetros (estimados)", "~110 milhões"],
            ["Idioma", "pt"],
            ["Licença", "Apache 2.0"],
            ["Downloads no último mês", "177.384"],
            ["Likes / discussões", "30 / 7"],
            ["Última modificação", "13 fev. 2024"],
        ], fonte="Elaborado pelo autor (2026) a partir da HuggingFace Hub API")
    A.paragrafo(doc,
        "O repositório contém dez arquivos, sem qualquer artefato oculto ou dado de treinamento. "
        "Três observações operacionais decorrem disso. Primeira: não há model.safetensors — o "
        "modelo é distribuído apenas como pytorch_model.bin, em formato pickle, o que afeta a "
        "reprodutibilidade em ambientes mais novos e deve ser documentado no capítulo de método. "
        "Segunda: não há dados de treinamento — o corpus de 1,4 milhão de textos e os 503 textos "
        "rotulados não foram publicados, o que impede replicação direta e reforça a originalidade "
        "do nosso conjunto-ouro. Terceira: as duas imagens presentes correspondem às Figuras 3 do "
        "artigo e 18 da monografia e, sob licença Apache 2.0, podem ser reproduzidas na "
        "dissertação com a devida atribuição.")

    A.secao(doc, "8.2", "Achado crítico: inconsistência no mapeamento de rótulos", nivel=2)
    A.quadro_codigo(doc, 1, "Trecho do config.json publicado do FinBERT-PT-BR",
        '"id2label": { "0": "POSITIVE", "1": "NEGATIVE", "2": "NEUTRAL" },\n'
        '"label2id": { "LABEL_0": 0, "LABEL_1": 1, "LABEL_2": 2 }',
        fonte="huggingface.co/lucas-leme/FinBERT-PT-BR/raw/main/config.json (acesso em 3 ago. 2026)")
    A.paragrafo(doc,
        "O id2label está correto e é o que a pipeline da biblioteca transformers utiliza — por "
        "isso a nossa pipeline funciona hoje. Mas o label2id não é o inverso do id2label: em vez "
        "de mapear POSITIVE para 0, mapeia LABEL_0 para 0. É um defeito do artefato publicado.")
    A.paragrafo(doc,
        "Isso importa porque a ordem dos rótulos é contraintuitiva. Em quase todos os modelos de "
        "sentimento de três classes a convenção é 0 para negativo, 1 para neutro e 2 para "
        "positivo. Aqui é o oposto: 0 é POSITIVE, 1 é NEGATIVE e 2 é NEUTRAL. Qualquer código que "
        "assuma a convenção usual inverterá completamente o sinal do índice de sentimento — erro "
        "que não gera exceção e que, portanto, passaria despercebido até a análise dos resultados. "
        "A consequência para o nosso código consta da Seção 9.2.")

    A.secao(doc, "8.3", "Trabalhos citantes verificados", nivel=2)
    A.tabela_abnt(doc, 10, "Síntese dos sete trabalhos citantes verificados",
        ["Trabalho", "Data", "Usou o encoder?", "Encoder/tecnologia própria", "Devo usar?"],
        [
            ["Teles e Figueiredo", "10/2025", "Não (citação conceitual)",
             "Gemini, DeBERTa, Gemma, BART, XLM-R, SVM, RF, MLP", "Sim — experimento com LLM"],
            ["Abílio, Coelho e Silva", "03/2024", "Não", "BERTimbau, PTT5, mBERT, mT5",
             "Sim — sustenta encoder monolíngue"],
            ["Imai et al. (PUCPR)", "12/2024", "Não", "SentenceBERT + Adaptive Random Forest",
             "Sim — concept drift"],
            ["Reichert e Perlin", "12/2025", "Não", "ChatGPT para dicionários",
             "Sim — linha de base léxica"],
            ["Alves et al.", "07/2024", "Não", "—", "Não"],
            ["Tanaka et al.", "02/2026", "Não (citação provavelmente imprecisa)", "RF, XGBoost, SVC, SHAP", "Pontual — SHAP"],
            ["Błoch, Santana e Amantino", "04/2026", "SIM — em máquina de comitê, fora do domínio financeiro", "FinBERT-PT-BR + pysentimiento", "Sim — comitê de modelos"],
        ], fonte="Elaborado pelo autor (2026) a partir de OpenAlex e Semantic Scholar")
    A.paragrafo(doc,
        "Dois padrões merecem registro. Primeiro, nenhum trabalho reaplicou o FinBERT-PT-BR na "
        "tarefa para a qual foi criado — a lacuna documentada na Seção 4. Segundo, as citações "
        "mais recentes migram para modelos de linguagem generativos, sinal de tendência da área "
        "que a dissertação precisa endereçar explicitamente, ainda que seja para justificar, com "
        "dados, por que manteve um encoder especializado.")
    A.paragrafo(doc,
        "Destaque institucional: Jean Paul Barddal e Alceu de Souza Britto Jr., coautores de Imai "
        "et al. (2024), são pesquisadores do PPGIa da PUCPR. O trabalho avalia o impacto de "
        "atualizar periodicamente modelos de linguagem em fluxo de notícias brasileiras, "
        "concluindo que o ajuste fino anual com amostra reduzida supera o modelo estático na "
        "maioria dos anos analisados. Endereça diretamente uma vulnerabilidade não tratada desta "
        "dissertação: emprega-se um modelo congelado em fevereiro de 2024 sobre corpus que vai de "
        "2018 a 2026. **Recomenda-se citar o trabalho e considerar consulta direta aos autores.**")
    A.paragrafo(doc,
        "Para fechar a lista de doze citações antes da versão final: abrir manualmente, em "
        "navegador logado, o endereço da orientação n. 7 e exportar as entradas em BibTeX; "
        "confrontar com os sete títulos verificados e isolar os restantes; e verificar, em cada "
        "um, apenas se o FinBERT-PT-BR foi de fato executado, e não somente citado, e se há "
        "previsão de ativo. Só isso altera as conclusões das Seções 4 e 6.")

    # ─── 9 Achados operacionais ──────────────────────────────────────────────
    A.secao(doc, "9", "Achados operacionais sobre o próprio código e dados")
    A.paragrafo(doc,
        "Esta seção não foi solicitada nas orientações. Resulta do cruzamento entre a literatura "
        "examinada e o estado atual do repositório, e contém três achados que afetam decisões "
        "imediatas.")

    A.secao(doc, "9.1", "O conjunto-ouro precisa ser refundado, não ampliado", nivel=2)
    A.tabela_abnt(doc, 11, "Controles metodológicos: Santos (2022) e o conjunto-ouro atual",
        ["Controle", "Santos (2022)", "Conjunto-ouro atual"],
        [
            ["Número de anotadores", "3 (cada texto por ao menos 2)", "1"],
            ["Categoria “não se aplica”", "Sim", "Parcial (há marcação de relevância)"],
            ["Descarte por discordância", "Sim — 49,7% descartados", "Impossível (não há 2.ª anotação)"],
            ["Percentual de concordância", "90,4%", "Não calculável"],
            ["Krippendorff’s alpha", "0,88", "Não calculável"],
        ], fonte=FONTE_AUTOR)
    A.paragrafo(doc,
        "A consequência é decisiva: sem segunda anotação não existe métrica de concordância; sem "
        "métrica de concordância não é possível afirmar que o gabarito é confiável; e sem gabarito "
        "confiável, os 58% não medem o FinBERT-PT-BR — medem a distância entre o FinBERT-PT-BR e "
        "um anotador único não calibrado. O kappa de 0,371 é ambíguo entre “o modelo erra” e “o "
        "gabarito é ruidoso”, e nada no desenho atual permite separar as duas hipóteses.")
    A.paragrafo(doc,
        "Isso fundamenta tecnicamente a orientação recebida. **Ampliar o gabarito de 300 para 600 "
        "manchetes nas condições atuais não resolveria nada** — dobraria o volume mantendo o mesmo "
        "defeito estrutural. Se e quando a rotulagem for retomada, a prioridade é a dupla anotação "
        "de um subconjunto, e não mais volume.")

    A.secao(doc, "9.2", "Mapeamento de rótulos invertido no Script 03", nivel=2)
    A.quadro_codigo(doc, 2, "Trecho de 03_analise_sentimento_bertimbau_petr4.py (linhas 312-317)",
        "if L in ('POSITIVE', 'POSITIVO', 'POS', 'LABEL_2'):\n"
        "    polaridade, label = +1, 'Positive'\n"
        "elif L in ('NEGATIVE', 'NEGATIVO', 'NEG', 'LABEL_0'):\n"
        "    polaridade, label = -1, 'Negative'\n"
        "else:  # NEUTRAL / NEUTRO / LABEL_1\n"
        "    polaridade, label = 0, 'Neutral'",
        fonte=FONTE_AUTOR)
    A.paragrafo(doc,
        "Confrontando com o id2label real do modelo, o mapeamento de contingência está invertido: "
        "LABEL_0 é POSITIVE no FinBERT-PT-BR, mas o código o trata como negativo; e LABEL_2 é "
        "NEUTRAL, mas o código o trata como positivo.")
    A.paragrafo(doc,
        "**Situação atual: sem impacto nos resultados já produzidos.** O config.json traz o "
        "id2label correto, de modo que a pipeline retorna as cadeias POSITIVE, NEGATIVE e NEUTRAL "
        "e o caminho LABEL_* nunca é acionado. Todos os resultados obtidos até aqui estão corretos. "
        "O risco está no futuro: basta uma mudança de versão da biblioteca, um carregamento por "
        "caminho alternativo ou o uso de outro modelo cujo config não traga id2label para o "
        "caminho de contingência ser acionado — e então todo o sinal do índice de sentimento se "
        "inverte silenciosamente, sem erro e sem aviso. Recomenda-se restringir o mapeamento ao "
        "modelo efetivamente carregado, ou eliminá-lo e falhar explicitamente diante de rótulo "
        "desconhecido.")

    A.secao(doc, "9.3", "O ambiente Python local está com o PyTorch inoperante", nivel=2)
    A.quadro_codigo(doc, 3, "Erro observado ao importar a biblioteca PyTorch",
        "OSError: [WinError 1114] Uma rotina de inicializacao da biblioteca de vinculo\n"
        "dinamico (DLL) falhou. Error loading \"...\\site-packages\\torch\\lib\\c10.dll\"\n"
        "or one of its dependencies.",
        fonte=FONTE_AUTOR)
    A.paragrafo(doc,
        "A falha é pré-existente, verificada isoladamente e sem qualquer pacote adicional "
        "instalado. O torch 2.12.1 está registrado no ambiente, mas não carrega. Como os "
        "experimentos de encoder de julho rodaram em CPU, algo mudou no ambiente desde então. "
        "Nenhum experimento de encoder ou de sentimento pode ser executado nesta máquina até a "
        "correção. As causas mais prováveis são, em ordem: ausência ou desatualização do Microsoft "
        "Visual C++ Redistributable; conflito de libiomp5md.dll entre a MKL do Anaconda e a do "
        "PyTorch; ou incompatibilidade entre as versões de torch e numpy instaladas.")
    A.paragrafo(doc,
        "Dado que o plano da Seção 10 envolve modelagem de linguagem mascarada sobre "
        "aproximadamente 205 mil textos, a solução mais rápida e adequada não é depurar o ambiente "
        "local, mas usar o Google Colab — ambiente para o qual a maior parte da pipeline já foi "
        "escrita e do mesmo tipo daquele utilizado por Santos.")

    # ─── 10 Plano de ação ────────────────────────────────────────────────────
    A.secao(doc, "10", "Plano de ação recomendado até 10 de agosto de 2026")
    A.paragrafo(doc,
        "A ordenação obedece a dois critérios: não depender de rotulagem manual, respeitando a "
        "orientação recebida, e produzir resultado apresentável em uma semana.")
    A.tabela_abnt(doc, 12, "Prioridade 1 — ações executáveis até 10 de agosto",
        ["N.", "Ação", "Por quê", "Esforço", "Depende de rótulo?"],
        [
            ["1.1", "MLM de domínio sobre FinBERT-PT-BR e sobre bert-large-portuguese-cased, com "
                    "as ~205 mil notícias; máscara 15%, lr 2e-5, 2 épocas, filtro de 512 tokens; "
                    "métrica de perplexidade em holdout de 10 mil textos",
             "Replica a etapa de maior ganho de Santos (1,51 → 1,24) e produz resultado "
             "quantitativo sem gabarito", "Colab, 6–10 h", "Não"],
            ["1.2", "Classificar o conjunto-ouro com um LLM via prompt, usando a instrução literal "
                    "de Santos, e comparar com o FinBERT-PT-BR e com o rótulo humano",
             "Testa em português a tese de Teles e Figueiredo (2025) e preenche a lacuna que "
             "aquele artigo deixa", "~4 h", "Não"],
            ["1.3", "Bootstrap e intervalos de confiança sobre resultado_encoders_petr4.csv",
             "Sem isso a tabela de encoders não sustenta conclusão; provavelmente mostrará que o "
             "BERTimbau large não difere do FinBERT-PT-BR", "~2 h", "Não"],
            ["1.4", "Corrigir o ambiente ou migrar os experimentos para o Colab",
             "Bloqueia 1.1 e 1.3", "1–3 h", "Não"],
        ], fonte=FONTE_AUTOR)
    A.tabela_abnt(doc, 13, "Prioridade 2 — redação, sem custo computacional",
        ["N.", "Ação"],
        [
            ["2.1", "Incorporar ao referencial as quatro referências de relação muito alta e as "
                    "três exclusivas da monografia"],
            ["2.2", "Escrever a subseção “Lacuna de literatura” com o achado da Seção 4: 177 mil "
                    "downloads mensais e adoção acadêmica aplicada praticamente nula"],
            ["2.3", "Reposicionar a volatilidade como contribuição principal e a direção como "
                    "resultado negativo reportado"],
            ["2.4", "Escrever a subseção “Transferência de domínio”: por que 0,76 vira 0,58"],
            ["2.5", "Declarar formalmente a limitação de concept drift, com apoio em Imai et al. "
                    "(2024)"],
            ["2.6", "Documentar no capítulo de método: licença Apache 2.0, ficha técnica, ausência "
                    "de safetensors e o limite de 512 tokens como justificativa do uso de manchetes"],
            ["2.7", "Conferir a referência “Silva (2018)” do plano de enriquecimento, para "
                    "descartar confusão com a Silva (2018) citada por Santos"],
        ], fonte=FONTE_AUTOR)
    A.tabela_abnt(doc, 14, "Prioridade 3 — quando a rotulagem for retomada",
        ["N.", "Ação"],
        [
            ["3.1", "Dupla anotação de um subconjunto de 100 a 150 manchetes das 300 já rotuladas, "
                    "com cálculo do Krippendorff’s alpha — menor intervenção que torna o gabarito "
                    "defensável, e mais valiosa do que ampliar para 600 sob o protocolo atual"],
            ["3.2", "Adotar a definição operacional literal de Santos e a categoria “não se "
                    "aplica”, com descarte por discordância"],
            ["3.3", "Aplicar modelagem de tópicos ou zero-shot para pré-selecionar textos "
                    "representativos e sugerir classe ao anotador, reduzindo custo e mitigando a "
                    "falta de especialização em finanças"],
            ["3.4", "Retreinar os encoders com o protocolo completo — gradual unfreezing, lr 5e-6, "
                    "11 épocas e validação cruzada com cinco divisões"],
        ], fonte=FONTE_AUTOR)

    A.secao(doc, "10.1", "Sugestão de pauta para a mentoria de 10 de agosto", nivel=2)
    A.lista(doc, [
        "Apresentar o achado da Seção 9.1 — a rotulagem tem problema estrutural anterior ao da "
        "qualificação do anotador, e a suspensão está tecnicamente correta também por essa razão.",
        "Apresentar os resultados de 1.1 e 1.2 como as frentes que avançam sem rotulagem.",
        "Apresentar a lacuna de literatura da Seção 4 e propor o reposicionamento da volatilidade "
        "como contribuição principal.",
        "Consultar sobre aproximação com o Prof. Jean Paul Barddal, do PPGIa da PUCPR, a respeito "
        "de concept drift no corpus.",
    ])

    # ─── 11 Referências ──────────────────────────────────────────────────────
    A.referencias(doc, "11", [
        "ABÍLIO, R.; COELHO, G. P.; SILVA, A. D. Evaluating Named Entity Recognition: a "
        "comparative analysis of mono- and multilingual transformer models on a novel Brazilian "
        "corporate earnings call transcripts dataset. Applied Soft Computing, 2024. "
        "DOI: 10.1016/j.asoc.2024.112158.",

        "ALCOFORADO, A. et al. ZeroBERTo: leveraging zero-shot text classification by topic "
        "modeling. arXiv:2201.01337, 2022.",

        "ALVES, M. A. R. et al. Sentimentos em Cena: uma análise dos comentários em trailers de "
        "filmes da Netflix Brasil no YouTube. In: BraSNAM, 13., 2024. Anais [...]. Porto Alegre: "
        "SBC, 2024. DOI: 10.5753/brasnam.2024.2974.",

        "ARACI, D. FinBERT: financial sentiment analysis with pre-trained language models. "
        "arXiv:1908.10063, 2019.",

        "ARTSTEIN, R.; POESIO, M. Inter-coder agreement for computational linguistics. "
        "Computational Linguistics, v. 34, n. 4, p. 555-596, 2008.",

        "BŁOCH, A.; SANTANA, C.; AMANTINO, M. Os jesuítas e a Era do Algoritmo: uma introdução à "
        "análise de sentimentos da correspondência colonial ultramarina portuguesa. Estudos "
        "Ibero-Americanos, 2026. DOI: 10.15448/1980-864x.2026.1.46315.",

        "BOLLEN, J.; MAO, H.; ZENG, X. Twitter mood predicts the stock market. Journal of "
        "Computational Science, v. 2, n. 1, p. 1-8, 2011.",

        "DEVLIN, J. et al. BERT: pre-training of deep bidirectional transformers for language "
        "understanding. arXiv:1810.04805, 2018.",

        "EFRON, B. Bootstrap methods: another look at the jackknife. In: Breakthroughs in "
        "statistics. New York: Springer, 1992. p. 569-593.",

        "HIEW, J. Z. G. et al. BERT-based financial sentiment index and LSTM-based stock return "
        "predictability. arXiv:1906.09024, 2019.",

        "IMAI, B. Y. L. et al. Is it fine to tune? Evaluating SentenceBERT fine-tuning for "
        "Brazilian Portuguese text stream classification. In: IEEE INTERNATIONAL CONFERENCE ON BIG "
        "DATA, 2024. DOI: 10.1109/BigData62323.2024.10825456.",

        "JANUÁRIO, B. A. et al. Sentiment analysis applied to news from the Brazilian stock "
        "market. IEEE Latin America Transactions, v. 20, n. 3, p. 512-518, 2022.",

        "KRIPPENDORFF, K. Content analysis: an introduction to its methodology. 4. ed. Thousand "
        "Oaks: Sage, 2018.",

        "LO, A. W. The adaptive markets hypothesis. The Journal of Portfolio Management, v. 30, "
        "n. 5, p. 15-29, 2004.",

        "POURSABZI-SANGDEH, F.; BOYD-GRABER, J. Speeding document annotation with topic models. "
        "In: NAACL STUDENT RESEARCH WORKSHOP, 2015. p. 126-132.",

        "REICHERT, M. H.; PERLIN, M. S. Using ChatGPT for creating multi-language finance related "
        "sentiment dictionaries. Computational Economics, 2025. DOI: 10.1007/s10614-025-11233-3.",

        "SANTOS, L. L. FinBERT-PT-BR: análise de sentimentos de textos em português referentes ao "
        "mercado financeiro. 2022. Trabalho de Conclusão de Curso (Engenharia de Computação) — "
        "Escola Politécnica, Universidade de São Paulo, São Paulo, 2022.",

        "SANTOS, L. L.; BIANCHI, R. A. C.; COSTA, A. H. R. FinBERT-PT-BR: análise de sentimentos "
        "de textos em português do mercado financeiro. In: BRAZILIAN WORKSHOP ON ARTIFICIAL "
        "INTELLIGENCE IN FINANCE (BWAIF), 2., 2023. Anais [...]. Porto Alegre: SBC, 2023. "
        "p. 144-155. DOI: 10.5753/bwaif.2023.231151.",

        "SOUZA, F.; NOGUEIRA, R.; LOTUFO, R. BERTimbau: pretrained BERT models for Brazilian "
        "Portuguese. In: BRAZILIAN CONFERENCE ON INTELLIGENT SYSTEMS, 2020. p. 403-417.",

        "SUN, C. et al. How to fine-tune BERT for text classification? In: CHINA NATIONAL "
        "CONFERENCE ON CHINESE COMPUTATIONAL LINGUISTICS, 2019. p. 194-206.",

        "TANAKA, S. A. et al. A machine learning-driven CRM approach for identifying member churn "
        "in a Brazilian agro-industrial cooperative: a practical case study. Algorithms, v. 19, "
        "n. 3, 2026. DOI: 10.3390/a19030180.",

        "TELES, L. E. P.; FIGUEIREDO, C. M. S. Comparing LLMs for sentiment analysis in financial "
        "market news. arXiv:2510.15929, 2025.",
    ])

    doc.save(SAIDA)
    print(f"OK -> {SAIDA.name}")


if __name__ == "__main__":
    main()
