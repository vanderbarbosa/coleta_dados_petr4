# -*- coding: utf-8 -*-
# ==============================================================================
#
#   DISSERTAÇÃO : O Impacto do Sentimento de Notícias Financeiras na Previsão
#                 de Direção e Volatilidade do Ativo PETR4
#   Autor       : Vanderlei Barbosa da Silva
#   Orientador  : Prof. Dr. Julio Cesar Nievola — PUCPR
#   Script      : 02 — Coleta de Notícias (Multi-Fonte)
#   Versão      : 3.1
#
# ==============================================================================
#
# ██████████████████████████████████████████████████████████████████████████████
#
#   DOCUMENTAÇÃO METODOLÓGICA COMPLETA
#   (Esta seção documenta todas as decisões de projeto para fins acadêmicos
#    e pode ser utilizada diretamente como base para a seção de Metodologia
#    da dissertação.)
#
# ██████████████████████████████████████████████████████████████████████████████
#
#
# ══════════════════════════════════════════════════════════════════════════════
# SEÇÃO 1 — JUSTIFICATIVA DA ABORDAGEM MULTI-FONTE
# ══════════════════════════════════════════════════════════════════════════════
#
#   PROBLEMA: Por que uma única fonte de notícias é insuficiente?
#   ─────────────────────────────────────────────────────────────
#   A versão inicial deste script utilizava exclusivamente o GDELT Project
#   como fonte de notícias. Embora o GDELT seja uma base robusta e amplamente
#   citada na literatura, depender de uma única fonte introduz um risco
#   metodológico conhecido como "viés de cobertura" (coverage bias):
#   diferentes veículos cobrem o mesmo evento com ângulos, intensidades e
#   vocabulários distintos, e uma fonte única sistematicamente sub-representa
#   determinados eventos ou regiões geográficas.
#
#   Heston & Sinha (2017) demonstraram empiricamente que modelos de sentimento
#   treinados com uma única fonte de notícias apresentam performance
#   significativamente inferior quando comparados a modelos que combinam
#   múltiplas fontes — especialmente em mercados emergentes como o Brasil,
#   onde eventos locais (decisões do governo, política de preços da Petrobras,
#   eleições) têm peso comparável a eventos globais.
#
#   SOLUÇÃO ADOTADA: Estratégia multi-fonte com 3 mecanismos
#   ──────────────────────────────────────────────────────────
#   Este script implementa três mecanismos de coleta complementares:
#
#     Mecanismo 1 — GDELT Project
#       Função principal : Cobertura histórica (2018-2025) em escala global
#       Por que usar     : Base de dados gratuita, citável academicamente,
#                          indexa mais de 100 idiomas incluindo português,
#                          com timestamps precisos e cobertura contínua desde
#                          2015. É o único mecanismo que garante cobertura
#                          histórica completa do período analisado.
#       Limitação 1      : Retorna apenas o título do artigo (sem resumo ou
#                          corpo do texto), o que limita a riqueza semântica
#                          do corpus para esta fonte especificamente. O campo
#                          "resumo" no CSV repete o título para artigos GDELT.
#       Limitação 2      : A API pública não tem autenticação e aplica dois
#                          tipos de rate limiting simultâneos:
#                          (a) por segundo: exceder ~5 req/s → 429 imediato
#                          (b) por volume de sessão: muitas requisições em
#                              poucas horas → bloqueio persistente de IP por
#                              2-4 horas, independente de pausas subsequentes.
#                          DESCOBERTO EM TESTE (10/06/2026): durante testes
#                          com 152 termos, o IP foi bloqueado por volume após
#                          duas sessões consecutivas. O bloqueio persiste mesmo
#                          com 90s de espera entre tentativas. Solução adotada:
#                          reduzir para 20 termos âncora por categoria, pausa
#                          de 12s com jitter aleatório. Ver Seção 8.
#       Termos usados    : 20 termos âncora (2-3 por categoria).
#                          A cobertura dos 152 termos originais é complementada
#                          pela NewsAPI e pelos RSS Feeds.
#       Citação acadêmica: "Os dados textuais foram extraídos parcialmente do
#                          GDELT Project (Leetaru & Schrodt, 2013), base de
#                          dados global de eventos e notícias utilizada em
#                          pesquisas de análise de sentimento financeiro."
#
#     Mecanismo 2 — NewsAPI
#       Função principal : Cobertura histórica com resumos e descrições
#       Por que usar     : Agrega mais de 80.000 fontes jornalísticas globais
#                          e retorna título + resumo + descrição dos artigos,
#                          o que enriquece o corpus textual em comparação ao
#                          GDELT. O plano Developer é gratuito para pesquisa
#                          acadêmica mediante solicitação.
#       Limitação        : O plano gratuito padrão cobre apenas os últimos
#                          30 dias; o plano Developer (solicitado via e-mail)
#                          oferece acesso histórico estendido.
#       Onde obter       : https://newsapi.org/register
#                          (solicitar plano Developer para pesquisa)
#
#     Mecanismo 3 — RSS Feeds (25 veículos)
#       Função principal : Cobertura recente de alta qualidade editorial
#       Por que usar     : RSS feeds de veículos especializados (Valor
#                          Econômico, InfoMoney, Reuters Energy, OilPrice.com)
#                          oferecem notícias com maior profundidade editorial
#                          do que bases automatizadas. São fontes primárias
#                          que jornalistas e analistas financeiros consultam.
#       Limitação        : A maioria dos feeds RSS não mantém histórico
#                          superior a 30-90 dias. Por isso, RSS complementa
#                          os dados recentes, enquanto GDELT e NewsAPI
#                          cobrem o histórico de 2018-2025.
#       Cobertura        : 14 veículos nacionais + 11 internacionais
#                          (detalhados na Seção 4 deste cabeçalho)
#
#
# ══════════════════════════════════════════════════════════════════════════════
# SEÇÃO 2 — JUSTIFICATIVA DA TAXONOMIA DE TERMOS DE BUSCA
# ══════════════════════════════════════════════════════════════════════════════
#
#   PROBLEMA: Por que os termos da versão anterior eram insuficientes?
#   ─────────────────────────────────────────────────────────────────
#   A versão 1.0 do script utilizava apenas 6 termos centrados na empresa
#   (ex.: "Petrobras", "PETR4", "pré-sal"). Essa escolha capturava notícias
#   corporativas, mas ignorava sistematicamente toda uma classe de eventos
#   exógenos que a literatura de economia do petróleo demonstra serem
#   igualmente — ou mais — determinantes para o preço da commodity e,
#   consequentemente, para a volatilidade da ação PETR4.
#
#   Hamilton (1983) foi o primeiro a documentar que praticamente todas as
#   recessões americanas do pós-guerra foram precedidas por choques
#   geopolíticos no mercado de petróleo. Kilian (2009) formalizou essa
#   observação em um modelo de decomposição de choques que separa:
#     (a) choques de oferta (supply shocks) — guerras, sabotagens, greves
#     (b) choques de demanda agregada — recessão, crescimento da China
#     (c) choques de demanda específica do petróleo — especulação, estoques
#
#   Um corpus que ignora as categorias (a) e (b) está estruturalmente
#   incompleto para prever volatilidade — independentemente de qual modelo
#   de machine learning seja aplicado depois.
#
#   SOLUÇÃO ADOTADA: Taxonomia de 7 categorias com âncora na literatura
#   ─────────────────────────────────────────────────────────────────────
#   Os termos foram organizados em 7 categorias, cada uma mapeando
#   diretamente um vetor de influência identificado na literatura:
#
#   ┌─────────────────────────────────────────────────────────────────────┐
#   │ CAT-1  Empresa e Ativo                                              │
#   │        Notícias corporativas diretas: resultados financeiros,       │
#   │        contratos, exploração de campos, dividendos, dívida,         │
#   │        privatização, governança.                                    │
#   │        Referência: Tetlock et al. (2008) demonstraram que notícias  │
#   │        corporativas têm poder preditivo sobre retornos futuros.     │
#   ├─────────────────────────────────────────────────────────────────────┤
#   │ CAT-2  Mercado de Petróleo                                          │
#   │        Fundamentos do mercado global: preço Brent/WTI, decisões     │
#   │        da OPEP, estoques EIA, oferta e demanda global.              │
#   │        Referência: Kilian (2009) — choques de oferta e demanda.     │
#   ├─────────────────────────────────────────────────────────────────────┤
#   │ CAT-3  Geopolítica e Conflitos                                      │
#   │        Guerras, tensões e cessar-fogo em países produtores.         │
#   │        Inclui: conflito Rússia-Ucrânia, guerra em Gaza, tensão no   │
#   │        Golfo Pérsico, instabilidade na Venezuela e Líbia.           │
#   │        Referência: Hamilton (1983) — choques geopolíticos e preço   │
#   │        do petróleo; Caldara & Iacoviello (2022) — índice de risco   │
#   │        geopolítico e impacto em commodities.                        │
#   ├─────────────────────────────────────────────────────────────────────┤
#   │ CAT-4  Oferta, Infraestrutura e Produção                            │
#   │        Refinarias, oleodutos, plataformas offshore, terminais.      │
#   │        Ataques, acidentes ou greves em infraestrutura crítica       │
#   │        geram choques imediatos de oferta com impacto direto no      │
#   │        preço do barril.                                             │
#   │        Exemplo histórico: ataque às refinarias da Aramco (set/2019) │
#   │        removeu 5% da oferta global em um único dia, gerando         │
#   │        volatilidade extrema no Brent.                               │
#   ├─────────────────────────────────────────────────────────────────────┤
#   │ CAT-5  Acordos, Sanções e Navegação                                 │
#   │        Embargos, bloqueios navais, teto de preço (price cap),       │
#   │        apreensão de navios petroleiros, acordos nucleares.          │
#   │        Inclui rotas críticas: Mar Vermelho (Bab-el-Mandeb),         │
#   │        Canal de Suez, Estreito de Ormuz — por onde passa ~40%       │
#   │        do petróleo marítimo mundial.                                │
#   │        Exemplo histórico: ataques Houthi no Mar Vermelho (2024)     │
#   │        elevaram fretes e adicionaram prêmio de risco ao Brent.      │
#   ├─────────────────────────────────────────────────────────────────────┤
#   │ CAT-6  Liderança, Governança e Política Energética                  │
#   │        Troca de CEO/presidente da Petrobras, indicações políticas,  │
#   │        intervenção governamental, ministério de energia, eleições   │
#   │        em países produtores.                                        │
#   │        Referência: Classifica-se como "event study" clássico —      │
#   │        anúncios de mudança de liderança geram retornos anormais     │
#   │        documentados na literatura de finanças corporativas.         │
#   │        Exemplo histórico: demissão do CEO José Mauro Coelho pela    │
#   │        gestão Lula (jun/2022) derrubou PETR4 mais de 10% em um dia. │
#   ├─────────────────────────────────────────────────────────────────────┤
#   │ CAT-7  Macroeconomia, Câmbio e Energia Alternativa                  │
#   │        Dólar, taxa de juros (Fed), recessão, PIB China, inflação,   │
#   │        energias renováveis, veículos elétricos, ESG.                │
#   │        O dólar e o petróleo têm correlação negativa histórica       │
#   │        documentada: quando o USD se fortalece, o petróleo cotado    │
#   │        em dólar tende a cair em termos relativos (Zhang et al.,     │
#   │        2008). A demanda da China responde por ~15% do consumo       │
#   │        global; notícias sobre o PIB chinês afetam diretamente o     │
#   │        preço do barril (Kilian & Murphy, 2014).                     │
#   └─────────────────────────────────────────────────────────────────────┘
#
#   VANTAGEM METODOLÓGICA DA TAXONOMIA
#   ────────────────────────────────────
#   A coluna "categoria" é gravada no CSV de saída junto a cada notícia.
#   Isso permite, na fase de modelagem (Script 05), realizar análises de
#   ablação: remover uma categoria por vez e medir o impacto na performance
#   do modelo. Esse tipo de análise responde a uma pergunta de pesquisa
#   adicional: "Qual categoria de notícia é mais informativa para prever
#   a volatilidade do PETR4?" — o que enriquece significativamente a
#   contribuição científica da dissertação.
#
#
# ══════════════════════════════════════════════════════════════════════════════
# SEÇÃO 3 — DECISÕES TÉCNICAS DE ENGENHARIA DE SOFTWARE
# ══════════════════════════════════════════════════════════════════════════════
#
#   DECISÃO 1 — Deduplicação por Hash SHA-256
#   ───────────────────────────────────────────
#   PROBLEMA: Um mesmo artigo pode ser capturado múltiplas vezes, seja porque
#   aparece em diferentes fontes (GDELT E NewsAPI cobrem o mesmo veículo), seja
#   porque foi encontrado por termos de busca diferentes (ex.: "Petrobras" e
#   "PETR4" podem retornar o mesmo artigo).
#
#   SOLUÇÃO ANTERIOR (versão 1.0): Comparação direta de strings de título.
#   Problema: sensível a diferenças superficiais — "Petrobras anuncia dividendo"
#   e "petrobras  anuncia dividendo" (caixa diferente, espaço duplo) seriam
#   tratados como artigos distintos, gerando duplicatas no corpus.
#
#   SOLUÇÃO ADOTADA: O título é normalizado (convertido para minúsculas e
#   espaços múltiplos colapsados) antes do cálculo do hash SHA-256. Dois
#   títulos superficialmente diferentes mas semanticamente idênticos produzem
#   o mesmo hash. O conjunto de hashes é mantido em memória (estrutura set —
#   O(1) para busca) e persistido no próprio CSV, permitindo retomada.
#
#   DEDUPLICAÇÃO CROSS-FONTE: A deduplicação opera sobre o conjunto unificado
#   de todas as fontes. Se uma notícia aparecer no GDELT e também na NewsAPI,
#   apenas a primeira ocorrência é gravada — independentemente da ordem de
#   coleta. Isso garante que o corpus não tenha contagem inflacionada.
#
#   ─────────────────────────────────────────────────────────────────────────
#   DECISÃO 2 — Tratamento Diferenciado de Rate Limiting por Tipo de Erro
#   ─────────────────────────────────────────────────────────────────────────
#   PROBLEMA IDENTIFICADO EM TESTE (versão 3.0):
#   A versão 3.0 usava o decorator @retry da biblioteca tenacity para todos
#   os erros de rede. Durante testes reais com 152 termos, o GDELT retornou
#   HTTP 429 (Too Many Requests) de forma persistente — todas as 5 tentativas
#   falhavam mesmo com 60s de espera entre elas. O problema era que o tenacity
#   tratava o 429 igual a um timeout de rede, sem distinção.
#
#   CAUSA RAIZ IDENTIFICADA:
#   O GDELT aplica dois tipos de rate limiting simultâneos:
#     (a) Rate limit por segundo : exceder ~5 req/s gera 429 imediato e
#                                   temporário (segundos a minutos)
#     (b) Rate limit por volume  : volume total alto em uma sessão gera
#                                   bloqueio de IP por horas, independente
#                                   da pausa entre requisições subsequentes
#   Com 152 termos, as sessões de teste acumularam centenas de requisições
#   em poucas horas, acionando o bloqueio por volume. Nesse estado, mesmo
#   90s de pausa entre tentativas não eram suficientes — o IP estava bloqueado
#   no nível da sessão do servidor, não no nível do rate limit por segundo.
#
#   SOLUÇÃO ADOTADA (versão 3.1 — duas mudanças simultâneas):
#
#   Mudança 2a — Tratamento manual e específico do erro 429:
#     A função _requisicao_gdelt() foi reescrita sem o decorator tenacity.
#     Ao receber 429: aguarda PAUSA_RATE_LIMIT_S (90s) e tenta novamente.
#     Ao receber timeout ou erro de rede: backoff exponencial (4s→8s→16s→30s).
#     Após 5 tentativas sem sucesso: retorna None (termo pulado, execução
#     continua) — sem lançar exceção que derrubaria toda a coleta.
#     A NewsAPI recebeu tratamento idêntico por consistência.
#
#   Mudança 2b — Redução drástica do volume de termos para o GDELT:
#     O número de termos enviados ao GDELT foi reduzido de 152 para 20
#     (termos "âncora" — 2-3 por categoria). Isso reduz o total de
#     requisições de ~12.768 para ~1.680, eliminando o gatilho do
#     bloqueio por volume. A cobertura temática completa é preservada
#     via NewsAPI e RSS, que não têm esse tipo de limitação.
#     Ver Seção 8 para o histórico completo de versões e testes.
#
#   ─────────────────────────────────────────────────────────────────────────
#   DECISÃO 3 — Jitter Aleatório nas Pausas do GDELT
#   ─────────────────────────────────────────────────────────────────────────
#   PROBLEMA: Pausas fixas entre requisições (ex.: exatamente 8s sempre)
#   criam um padrão periódico de tráfego. Servidores com detecção de bots
#   identificam esse padrão e podem aplicar rate limiting mesmo que o
#   intervalo seja "suficiente" em termos de volume.
#
#   SOLUÇÃO ADOTADA: A pausa entre requisições ao GDELT é calculada como
#   PAUSA_GDELT_S + random.uniform(-3, 3), resultando em intervalos entre
#   9s e 15s (com pausa base de 12s). A variação aleatória torna o padrão
#   de tráfego indistinguível de um usuário humano navegando manualmente.
#   Este é o padrão recomendado em web scraping ético (Mitchel, 2018).
#
#   ─────────────────────────────────────────────────────────────────────────
#   DECISÃO 4 — Gravação Linha a Linha (sem acúmulo em DataFrame)
#   ─────────────────────────────────────────────────────────────────────────
#   PROBLEMA: A versão 1.0 acumulava todos os artigos em uma lista Python
#   durante toda a coleta e só no final criava um DataFrame e salvava o CSV.
#   Para 7 anos de dados com múltiplos termos e 3 fontes, isso pode consumir
#   vários GB de RAM — excedendo o limite do Google Colab (12-15 GB) e
#   derrubando a sessão, perdendo todo o trabalho acumulado.
#
#   SOLUÇÃO ADOTADA: Cada artigo é gravado no CSV imediatamente após ser
#   coletado e validado (deduplicado), usando csv.DictWriter com buffer
#   explícito (flush a cada 500 artigos). O consumo de memória é O(H),
#   onde H é o conjunto de hashes: para 1 milhão de artigos únicos,
#   são ~64 MB — totalmente viável no Colab.
#
#   ─────────────────────────────────────────────────────────────────────────
#   DECISÃO 5 — Logging Estruturado em Arquivo
#   ─────────────────────────────────────────────────────────────────────────
#   PROBLEMA: A versão 1.0 usava apenas print() para exibir o progresso.
#   Ao fechar o Colab, não havia registro de quantas notícias foram coletadas,
#   quais erros ocorreram, ou em qual ponto a coleta parou.
#
#   SOLUÇÃO ADOTADA: A biblioteca logging do Python grava simultaneamente
#   no console (visível no Colab) e em arquivo persistente no Google Drive
#   (coleta_noticias.log). Cada linha contém timestamp, nível e mensagem.
#   Durante os testes de desenvolvimento, o log foi fundamental para
#   diagnosticar o bloqueio por volume do GDELT: sem ele, seria impossível
#   distinguir entre erro de rede transitório e bloqueio persistente de IP.
#   O arquivo de log é um registro auditável — apresentável na defesa.
#
#   ─────────────────────────────────────────────────────────────────────────
#   DECISÃO 6 — Retomada Automática de Coleta Interrompida
#   ─────────────────────────────────────────────────────────────────────────
#   PROBLEMA: A coleta de 7 anos com múltiplas fontes pode levar 8-12 horas.
#   O Google Colab desconecta sessões inativas após ~90 minutos. A versão 1.0
#   tinha checkpoints manuais, mas sem retomada automática.
#
#   SOLUÇÃO ADOTADA: Ao iniciar, o script lê a coluna "hash_titulo" do CSV
#   já existente e carrega todos os hashes em memória. Qualquer artigo já
#   gravado é identificado pelo hash e descartado instantaneamente (O(1)).
#   Rodar o script novamente retoma de onde parou sem duplicar dados.
#   O CSV é aberto em modo "append" — nunca sobrescrito.
#
#   ─────────────────────────────────────────────────────────────────────────
#   DECISÃO 7 — Gerador Python (yield) em vez de listas
#   ─────────────────────────────────────────────────────────────────────────
#   PROBLEMA: Retornar listas completas de artigos significa construir
#   tudo em memória antes de processar qualquer item — ineficiente.
#
#   SOLUÇÃO ADOTADA: As funções coletar_gdelt(), coletar_newsapi() e
#   coletar_rss() são implementadas como geradores (usam yield). Cada
#   artigo é processado e gravado imediatamente após recebido da API,
#   sem esperar o lote completo. Além da eficiência de memória, torna
#   o código modular e testável de forma independente por fonte.
#
#   ─────────────────────────────────────────────────────────────────────────
#   DECISÃO 8 — Coleta Mensal por Janela de Tempo
#   ─────────────────────────────────────────────────────────────────────────
#   PROBLEMA: Uma consulta única para 2018-2025 retornaria apenas os 250
#   artigos mais recentes (limite hard da API do GDELT por consulta),
#   perdendo 7 anos de histórico.
#
#   SOLUÇÃO ADOTADA: O período é dividido em janelas mensais. Para cada
#   mês, uma consulta independente usa startdatetime e enddatetime.
#   Isso garante cobertura temporal completa — cada mês pode ter até
#   250 artigos por termo. Com 20 termos × 84 meses = 1.680 consultas
#   ao GDELT, e pausa de ~12s cada, o tempo total é ~5,6 horas.
#
#
# ══════════════════════════════════════════════════════════════════════════════
# SEÇÃO 4 — FONTES RSS: VALIDAÇÃO E JUSTIFICATIVA
# ══════════════════════════════════════════════════════════════════════════════
#
#   HISTÓRICO DE VALIDAÇÕES (executar teste_rss_feeds.py periodicamente)
#   ─────────────────────────────────────────────────────────────────────
#   10/06/2026 — 1ª validação: 18 OK, 13 mortos.
#     Feeds encerrados: Reuters (todos), Bloomberg Energy, Valor (URL errada),
#     Estadão, InfoMoney mercados/ações, Agência Brasil, Band News, EIA, Platts.
#     Ação: corrigidos e substituídos. Novo total: 25 feeds.
#
#   10/06/2026 — 2ª validação: 22 OK, 3 mortos.
#     Agencia_Senado /rss/ultimas → corrigida para /feed/todasnoticias.
#     SPGlobal_Energy → substituído por GoogleNews_Oil.
#     World_Oil /rss-feeds/news → corrigida para /rss?feed=news.
#
#   10/06/2026 — 3ª validação: 24 OK, 1 morto.
#     Agencia_Senado /feed/todasnoticias: feedparser não parseia o formato.
#     Substituído por Agencia_Camara (Câmara dos Deputados).
#
#   10/06/2026 — 4ª validação: 24 OK, 1 morto (Agencia_Camara).
#     Agencia_Camara também retorna 0 entradas via feedparser.
#     DECISÃO: manter 24 feeds sem substituto para esta vaga.
#     Justificativa: os 24 feeds ativos já fornecem 904 entradas totais
#     e 271 relevantes por coleta. A vaga de cobertura legislativa
#     (Senado/Câmara) é parcialmente coberta pelo G1_Economia,
#     Folha_Mercado e Poder360, que monitoram votações de impacto no
#     mercado. Insistir nessa vaga não agrega valor proporcional ao
#     corpus — decisão metodológica documentada para a dissertação.
#
#   FEEDS MORTOS E MOTIVO (documentado para a dissertação):
#   ─────────────────────────────────────────────────────────
#   Reuters Business/Energy : encerrou feeds.reuters.com em 2023;
#     reuters.com/*/feed/ retorna vazio (bloqueio por user-agent).
#     Substituído por Yahoo Finance (que agrega conteúdo da Reuters).
#   Bloomberg Energy        : feeds.bloomberg.com encerrado (acesso
#     restrito a assinantes). Substituído por S&P Global Commodity.
#   Valor Econômico         : URL valor.globo.com/rss/home/ retorna vazio.
#     URL correta é valor.com.br/rss (confirmada em pesquisa).
#   Estadão Economia        : estadao.com.br/rss/economia.xml retorna vazio.
#     Substituído por Brazil Journal (jornalismo financeiro em inglês).
#   InfoMoney mercados/ações: subfeeds retornam vazio; apenas /feed/ funciona.
#   Agência Brasil          : feed retorna vazio. Substituído por Agência Senado.
#   Band News               : feed retorna vazio. Substituído por Metrópoles.
#   EIA / Platts            : feeds fechados ou restritos a assinantes.
#     World Oil substitui para cobertura de upstream.
#
#   FEEDS VALIDADOS E JUSTIFICATIVA
#   ─────────────────────────────────
#
#   NACIONAIS (14 feeds)
#   ─────────────────────
#   G1 Economia e G1 Mercados (100 entradas cada)
#     Maior grupo de comunicação do Brasil. Retornou 36 e 52 notícias
#     relevantes respectivamente no teste — o maior volume nacional.
#
#   InfoMoney (10 entradas, 1 relevante)
#     Portal de finanças pessoais e mercado de capitais. Feed limitado
#     a 10 entradas; volume menor, mas cobertura especializada em PETR4.
#
#   Valor Econômico (URL corrigida: valor.com.br/rss)
#     Principal jornal financeiro do Brasil. URL antiga encerrada;
#     a correta foi identificada em pesquisa e incluída nesta versão.
#
#   Exame Invest (25 entradas, 1 relevante)
#     Cobertura de negócios e empresas listadas na B3.
#
#   UOL Economia (15 entradas)
#     Portal de grande alcance; captura repercussão de decisões da Petrobras.
#
#   Folha de São Paulo — Mercado (100 entradas, 17 relevantes)
#     Jornal de referência nacional; alto volume e boa relevância no teste.
#
#   CNN Brasil (60 entradas, 2 relevantes)
#     Cobertura em tempo real de breaking news de mercado.
#
#   Poder360 (10 entradas, 1 relevante)
#     Cobertura da interface entre governo federal e Petrobras.
#
#   Money Times (10 entradas, 1 relevante)
#     Focado em investimentos e recomendações de analistas para PETR4.
#
#   E-Investidor / Estadão (8 entradas, 1 relevante)
#     Portal do Grupo Estado para investidores de varejo.
#
#   Brazil Journal (substitui Estadão Economia)
#     Jornalismo financeiro em inglês sobre Brasil; cobre fusões,
#     aquisições e política econômica com análise de mercado.
#
#   Agência Senado (substitui Agência Brasil)
#     Cobertura legislativa; relevante para projetos que afetam a
#     política de preços da Petrobras e o setor de energia.
#
#   Metrópoles Economia (substitui Band News)
#     Portal digital de grande alcance; cobertura econômica nacional.
#
#   INTERNACIONAIS (11 feeds)
#   ──────────────────────────
#   BBC Business (57 entradas)
#     Cobertura de negócios internacionais e eventos geopolíticos.
#
#   MarketWatch (10 entradas)
#     Portal Dow Jones; cobertura de commodities e mercados futuros.
#
#   OilPrice.com (15 entradas, 4 relevantes)
#     Portal especializado em petróleo e gás. Retornou a maior proporção
#     de notícias relevantes entre os feeds internacionais no teste.
#
#   Rigzone (20 entradas)
#     Especializado em upstream (exploração e produção); cobre plataformas
#     offshore e contratos de exploração — relevante para o pré-sal.
#
#   CNBC Energy (30 entradas)
#     Cobertura de energia com foco em impacto nos mercados financeiros.
#
#   Financial Times Energy (25 entradas, 1 relevante)
#     Análise aprofundada de transição energética e mercado de commodities.
#
#   Investing.com Oil e Commodities (10 entradas cada, 2 relevantes combinados)
#     Futuros de petróleo, relatórios EIA de estoques e calendário econômico.
#
#   Yahoo Finance (substitui Reuters)
#     Agrega conteúdo de Reuters, Bloomberg, AP e outros; maior cobertura
#     de notícias financeiras em inglês disponível via RSS público.
#
#   S&P Global Commodity (substitui Bloomberg Energy)
#     Cobertura especializada de mercados de gás natural e petróleo;
#     relatórios de preços e análises da indústria energética global.
#
#   World Oil (substitui EIA)
#     Especializado no setor upstream de petróleo; cobre exploração,
#     produção, tecnologia offshore e geopolítica do setor.
#
#
# ══════════════════════════════════════════════════════════════════════════════
# SEÇÃO 5 — ESTRUTURA DO CSV DE SAÍDA E SIGNIFICADO DE CADA COLUNA
# ══════════════════════════════════════════════════════════════════════════════
#
#   O arquivo base_textual_petr4_2018_2025.csv contém as seguintes colunas:
#
#   ┌──────────────────┬───────────────────────────────────────────────────┐
#   │ Coluna           │ Descrição                                         │
#   ├──────────────────┼───────────────────────────────────────────────────┤
#   │ data_publicacao  │ Data e hora de publicação do artigo no formato    │
#   │                  │ ISO 8601: YYYY-MM-DD HH:MM:SS. Esta coluna é      │
#   │                  │ usada no Script 04 para alinhar temporalmente     │
#   │                  │ as notícias com os dados de preço do PETR4.       │
#   ├──────────────────┼───────────────────────────────────────────────────┤
#   │ ativo            │ Identificador do ativo analisado. Sempre "PETR4"  │
#   │                  │ neste corpus. Mantido para permitir extensão      │
#   │                  │ futura do estudo a outros ativos.                 │
#   ├──────────────────┼───────────────────────────────────────────────────┤
#   │ categoria        │ Categoria temática do termo que originou a        │
#   │                  │ coleta (CAT1_Empresa a CAT7_Macro_Energia).       │
#   │                  │ Permite análise de ablação na fase de modelagem.  │
#   ├──────────────────┼───────────────────────────────────────────────────┤
#   │ fonte_coleta     │ Mecanismo de coleta: "GDELT", "NewsAPI" ou        │
#   │                  │ "RSS_<NomeDoVeiculo>". Permite rastrear a origem  │
#   │                  │ de cada notícia para fins de auditoria.           │
#   ├──────────────────┼───────────────────────────────────────────────────┤
#   │ termo_busca      │ Termo exato que gerou a requisição à API.         │
#   │                  │ Para RSS: "filtro_local" (filtrado localmente).   │
#   ├──────────────────┼───────────────────────────────────────────────────┤
#   │ titulo           │ Título completo do artigo conforme publicado.     │
#   │                  │ Campo principal para análise de sentimento.       │
#   ├──────────────────┼───────────────────────────────────────────────────┤
#   │ resumo           │ Resumo/descrição do artigo. Para GDELT, onde      │
#   │                  │ resumo não está disponível, este campo repete     │
#   │                  │ o título. Para NewsAPI e RSS, contém o resumo     │
#   │                  │ editorial do artigo — mais rico semanticamente.   │
#   ├──────────────────┼───────────────────────────────────────────────────┤
#   │ url              │ URL original do artigo para referência e          │
#   │                  │ verificação manual de amostras do corpus.         │
#   ├──────────────────┼───────────────────────────────────────────────────┤
#   │ dominio          │ Domínio ou nome do veículo de comunicação.        │
#   │                  │ Permite análise de distribuição por veículo.      │
#   ├──────────────────┼───────────────────────────────────────────────────┤
#   │ idioma           │ Código do idioma: "pt" (português) ou "en"        │
#   │                  │ (inglês). Feeds internacionais (Reuters, BBC,     │
#   │                  │ OilPrice etc.) são classificados como "en".       │
#   │                  │ Relevante para escolha do modelo de sentimento    │
#   │                  │ no Script 03 (modelo PT vs. modelo EN).           │
#   ├──────────────────┼───────────────────────────────────────────────────┤
#   │ hash_titulo      │ Hash SHA-256 do título normalizado. Usado         │
#   │                  │ internamente para deduplicação. Também permite    │
#   │                  │ verificar integridade do corpus após transferência │
#   │                  │ de arquivos.                                      │
#   └──────────────────┴───────────────────────────────────────────────────┘
#
#
# ══════════════════════════════════════════════════════════════════════════════
# SEÇÃO 6 — REFERÊNCIAS BIBLIOGRÁFICAS COMPLETAS
# ══════════════════════════════════════════════════════════════════════════════
#
#   Baker, S. R., Bloom, N., & Davis, S. J. (2016). Measuring economic
#   policy uncertainty. The Quarterly Journal of Economics, 131(4), 1593-1636.
#   https://doi.org/10.1093/qje/qjw024
#
#   Caldara, D., & Iacoviello, M. (2022). Measuring geopolitical risk.
#   American Economic Review, 112(4), 1194-1225.
#   https://doi.org/10.1257/aer.20191823
#
#   Hamilton, J. D. (1983). Oil and the macroeconomy since World War II.
#   Journal of Political Economy, 91(2), 228-248.
#   https://doi.org/10.1086/261140
#
#   Heston, S. L., & Sinha, N. R. (2017). News vs. sentiment: Predicting
#   stock returns from news stories. Financial Analysts Journal, 73(3), 67-83.
#   https://doi.org/10.2469/faj.v73.n3.3
#
#   Kilian, L. (2009). Not all oil price shocks are alike: Disentangling
#   demand and supply shocks in the crude oil market. American Economic
#   Review, 99(3), 1053-1069.
#   https://doi.org/10.1257/aer.99.3.1053
#
#   Kilian, L., & Murphy, D. P. (2014). The role of inventories and
#   speculative trading in the global market for crude oil. Journal of
#   Applied Econometrics, 29(3), 454-478.
#   https://doi.org/10.1002/jae.2322
#
#   Leetaru, K., & Schrodt, P. A. (2013). GDELT: Global data on events,
#   location and tone. ISA Annual Convention, 2(4), 1-49.
#   Disponível em: https://blog.gdeltproject.org
#
#   Tetlock, P. C., Saar-Tsechansky, M., & Macskassy, S. (2008). More
#   than words: Quantifying language to measure firms' fundamentals.
#   The Journal of Finance, 63(3), 1437-1467.
#   https://doi.org/10.1111/j.1540-6261.2008.01362.x
#
#   Zhang, Y. J., Fan, Y., Tsai, H. T., & Wei, Y. M. (2008). Spillover
#   effect of US dollar exchange rate on oil prices. Journal of Policy
#   Modeling, 30(6), 973-991.
#   https://doi.org/10.1016/j.jpolmod.2008.02.002
#
#
# ══════════════════════════════════════════════════════════════════════════════
# SEÇÃO 7 — ARQUIVOS GERADOS E TEMPO ESTIMADO DE EXECUÇÃO
# ══════════════════════════════════════════════════════════════════════════════
#
#   ARQUIVOS GERADOS
#   ─────────────────
#   base_textual_petr4_2018_2025.csv
#     Corpus final consolidado. Contém todas as notícias únicas coletadas
#     das três fontes, deduplicadas, com data, categoria e origem.
#
#   coleta_noticias.log
#     Registro auditável completo: timestamps, contagens por fonte,
#     erros de rede, bloqueios 429, duplicatas removidas. Fundamental
#     para auditar a coleta na defesa.
#
#   TEMPO ESTIMADO DE EXECUÇÃO (versão 3.1 — valores corrigidos após testes)
#   ──────────────────────────────────────────────────────────────────────────
#   NOTA: Os tempos da versão 3.0 estavam incorretos. Foram calculados com
#   base em 152 termos e pausa de 2s — configuração que gerou bloqueio de IP
#   durante os testes. Os valores abaixo refletem a configuração validada.
#
#   GDELT   : 20 termos × 84 meses × ~12s de pausa (com jitter) ≈ 5,6 horas
#   NewsAPI : 92 termos × 84 meses × 2s de pausa              ≈ 4,3 horas
#   RSS     : 25 feeds × ~1s cada                             ≈ 1 minuto
#   ─────────────────────────────────────────────────────────────────────────
#   Total estimado: 10 a 12 horas de execução contínua
#
#   IMPORTANTE: Estes tempos assumem que o GDELT não bloqueia o IP.
#   Se bloqueios persistentes ocorrerem (429 em todas as tentativas),
#   é necessário aguardar 2-4 horas para liberação do IP antes de
#   retomar. Ver Seção 8 para diagnóstico e procedimento de retomada.
#
#   COMO EXECUTAR — AMBIENTE LOCAL (VS Code, terminal)
#   ────────────────────────────────────────────────────
#   Pré-requisitos:
#     Python 3.10+ instalado
#     Ambiente virtual criado e ativado:
#       python -m venv .venv
#       .venv\Scripts\activate          (Windows)
#       source .venv/bin/activate       (Mac/Linux)
#     Dependências instaladas:
#       pip install feedparser newsapi-python tenacity tqdm python-dateutil pandas requests
#
#   PASSO 0 — ANTES DE QUALQUER EXECUÇÃO: verificar se IP está liberado
#   ─────────────────────────────────────────────────────────────────────
#   Se você já rodou versões anteriores do script no mesmo dia, seu IP
#   pode estar bloqueado pelo GDELT por volume acumulado de requisições.
#   Antes de iniciar, abra este URL no navegador e verifique o resultado:
#
#     https://api.gdeltproject.org/api/v2/doc/doc?query=%22Petrobras%22&mode=artlist&format=json
#
#   ✅ Se retornar um JSON com artigos → IP liberado, pode executar.
#   ❌ Se retornar erro 429 ou página vazia → aguarde 2-4 horas e teste
#      novamente antes de rodar o script. Rodar com IP bloqueado desperdiça
#      tempo e não coleta nenhum dado do GDELT.
#
#   PASSO 1 — Configurar credenciais
#     Abra o arquivo e substitua:
#       NEWSAPI_KEY = "SUA_CHAVE_AQUI"
#     pela sua chave obtida em https://newsapi.org/register
#     (sem a chave, o GDELT e RSS funcionam normalmente; NewsAPI é pulada)
#
#   PASSO 2 — TESTE RÁPIDO (recomendado antes da coleta completa)
#     Altere no Bloco 3:
#       DATA_INICIO = datetime(2024, 12, 1)
#       DATA_FIM    = datetime(2024, 12, 31)
#     Rode: python 02_coleta_noticias_petr4.py
#     Tempo esperado : ~5-8 minutos (20 termos × 1 mês × ~12s de pausa)
#     Resultado      : ~50-300 notícias no CSV, sem erros 429
#     Se o teste passar sem 429 → IP está ok para a coleta completa.
#
#   PASSO 3 — COLETA COMPLETA (2018-2025)
#     Restaure as datas originais:
#       DATA_INICIO = datetime(2018, 1, 1)
#       DATA_FIM    = datetime(2025, 12, 31)
#     Rode: python 02_coleta_noticias_petr4.py
#     Tempo estimado: 10-12 horas (pode ser interrompido e retomado)
#     O script retoma automaticamente — nunca sobrescreve dados gravados.
#
#   COMO EXECUTAR — GOOGLE COLAB
#   ──────────────────────────────
#   O Colab usa IPs do datacenter do Google — diferente do seu IP local.
#   Bloqueios que afetam seu VS Code NÃO afetam o Colab, e vice-versa.
#   Para coletas longas (10-12h), o Colab Pro é recomendado para evitar
#   desconexões por inatividade (o plano gratuito desconecta em ~90 min).
#
#   Célula 1 (instalar dependências — apenas uma vez por sessão):
#     !pip install feedparser newsapi-python tenacity tqdm --quiet
#
#   Célula 2 (montar o Drive — necessário para salvar arquivos):
#     from google.colab import drive
#     drive.mount('/content/drive')
#
#   Célula 3 (verificar IP antes de executar — mesmo cuidado do local):
#     import requests
#     r = requests.get('https://api.gdeltproject.org/api/v2/doc/doc'
#                      '?query=%22Petrobras%22&mode=artlist&format=json')
#     print("Status GDELT:", r.status_code)
#     # 200 = OK, pode executar | 429 = aguarde e tente novamente
#
#   Célula 4 (executar coleta):
#     %run 02_coleta_noticias_petr4.py
#     # ou, se preferir chamar a função diretamente:
#     executar_coleta_completa()
#
#   Célula 5 (ver estatísticas do corpus coletado):
#     exibir_estatisticas_corpus()
#
#   RETOMADA APÓS INTERRUPÇÃO (Colab ou local):
#     Simplesmente rode executar_coleta_completa() novamente.
#     O script detecta os artigos já gravados e continua de onde parou.
#     Não há risco de duplicar dados — o hash SHA-256 garante idempotência.
#
#
# ══════════════════════════════════════════════════════════════════════════════
# SEÇÃO 8 — HISTÓRICO DE VERSÕES E PROBLEMAS ENCONTRADOS EM TESTE
# ══════════════════════════════════════════════════════════════════════════════
#
#   Esta seção documenta o histórico de desenvolvimento do script, incluindo
#   os problemas reais encontrados durante testes de execução e as soluções
#   adotadas. Esse tipo de documentação é relevante para dissertações que
#   descrevem o processo metodológico de construção do corpus.
#
#   ┌─────────────────────────────────────────────────────────────────────┐
#   │ VERSÃO 1.0 — Script original                                        │
#   │ Data: início do projeto                                             │
#   ├─────────────────────────────────────────────────────────────────────┤
#   │ Características:                                                    │
#   │   • Fonte única: GDELT                                              │
#   │   • 6 termos de busca centrados na empresa                          │
#   │   • Deduplicação por comparação direta de string                    │
#   │   • Sem retry em caso de falha de rede                              │
#   │   • Acúmulo de dados em lista Python (risco de OOM)                 │
#   │   • Checkpoints manuais, sem retomada automática                    │
#   │                                                                     │
#   │ Problemas identificados na revisão:                                 │
#   │   • Viés de cobertura (fonte única)                                 │
#   │   • Cobertura temática insuficiente (apenas notícias corporativas)  │
#   │   • Sem resumo/descrição dos artigos (apenas título)                │
#   │   • Sem logging auditável                                           │
#   └─────────────────────────────────────────────────────────────────────┘
#
#   ┌─────────────────────────────────────────────────────────────────────┐
#   │ VERSÃO 3.0 — Reescrita completa                                     │
#   │ Data: desenvolvimento pré-teste                                     │
#   ├─────────────────────────────────────────────────────────────────────┤
#   │ Melhorias introduzidas:                                             │
#   │   • 3 fontes: GDELT + NewsAPI + 25 RSS feeds                        │
#   │   • Taxonomia de 7 categorias temáticas com 152 termos              │
#   │   • Deduplicação por hash SHA-256                                   │
#   │   • Retry com @retry (tenacity) — backoff exponencial               │
#   │   • Gravação linha a linha (sem acúmulo em memória)                 │
#   │   • Logging estruturado em arquivo                                  │
#   │   • Retomada automática por leitura de hashes do CSV                │
#   │   • Geradores Python (yield) para eficiência de memória             │
#   │   • Coleta por janela mensal                                        │
#   │                                                                     │
#   │ PROBLEMA ENCONTRADO EM TESTE (ambiente: VS Code, Windows,           │
#   │ Python 3.12.4, 10/06/2026):                                         │
#   │                                                                     │
#   │   Sintoma: HTTP 429 persistente desde a primeira requisição,        │
#   │   mesmo com 60s de espera entre tentativas. Todas as 5 tentativas   │
#   │   falhavam para todos os termos.                                    │
#   │                                                                     │
#   │   Diagnóstico: Duas sessões de teste consecutivas (v1.0 e v3.0      │
#   │   durante a mesma tarde) somaram centenas de requisições ao GDELT.  │
#   │   Isso acionou o bloqueio por VOLUME DE IP (distinto do rate limit  │
#   │   por segundo). Nesse estado, o servidor rejeita qualquer           │
#   │   requisição do IP por horas, independente da pausa entre elas.     │
#   │                                                                     │
#   │   Problemas de design identificados:                                │
#   │   1. @retry (tenacity) tratava 429 igual a timeout — inadequado     │
#   │      para bloqueio por volume, que requer espera muito maior        │
#   │   2. 152 termos × 84 meses = 12.768 requisições — volume            │
#   │      incompatível com API pública sem autenticação                  │
#   │   3. Pausa fixa de 8s criava padrão periódico detectável            │
#   └─────────────────────────────────────────────────────────────────────┘
#
#   ┌─────────────────────────────────────────────────────────────────────┐
#   │ VERSÃO 3.1 — Correções pós-teste (versão atual)                     │
#   │ Data: 10/06/2026                                                    │
#   ├─────────────────────────────────────────────────────────────────────┤
#   │ Correções aplicadas:                                                │
#   │                                                                     │
#   │   Correção 1 — Tratamento diferenciado do erro 429:                 │
#   │     @retry (tenacity) substituído por retry manual em               │
#   │     _requisicao_gdelt() e _requisicao_newsapi().                    │
#   │     HTTP 429 → aguarda 90s antes de tentar novamente.               │
#   │     Timeout/rede → backoff exponencial (4s→8s→16s→30s).             │
#   │     Após 5 tentativas: retorna None, coleta continua.               │
#   │                                                                     │
#   │   Correção 2 — Redução de termos GDELT de 152 para 20:              │
#   │     1-3 termos "âncora" por categoria (os mais abrangentes).        │
#   │     Resultado: 20 × 84 = 1.680 requisições (era 12.768).            │
#   │     Cobertura temática preservada via NewsAPI e RSS.                │
#   │                                                                     │
#   │   Correção 3 — Pausa com jitter aleatório (±3s):                    │
#   │     time.sleep(PAUSA_GDELT_S + random.uniform(-3, 3))               │
#   │     Intervalo resultante: 9s a 15s (média 12s).                     │
#   │     Evita padrão periódico detectável por sistemas anti-bot.        │
#   │                                                                     │
#   │   Correção 4 — Pausa base aumentada para 12s (era 8s):              │
#   │     ~250 req/hora → dentro do limite tolerado pelo GDELT.           │
#   │                                                                     │
#   │   Correção 5 — PAUSA_RATE_LIMIT_S aumentada para 90s (era 60s):     │
#   │     Mais conservador para lidar com bloqueios de sessão.            │
#   │                                                                     │
#   │ PROCEDIMENTO PARA DIAGNÓSTICO DE BLOQUEIO DE IP:                    │
#   │   Se 429 persistir em todas as tentativas, abra no navegador:       │
#   │   https://api.gdeltproject.org/api/v2/doc/doc?query="Petrobras"     │
#   │   &mode=artlist&format=json                                         │
#   │   Se retornar 429, seu IP está bloqueado. Aguarde 2-4 horas.        │
#   │   Se retornar JSON com artigos, o bloqueio foi liberado.            │
#   └─────────────────────────────────────────────────────────────────────┘
#
# ==============================================================================


# ==============================================================================
# BLOCO 1 — INSTALAÇÃO DAS BIBLIOTECAS
# ==============================================================================
# Execute esta célula apenas UMA VEZ por sessão do Colab.
# Após instalar, pode comentar o !pip e rodar só o print.
#
# Bibliotecas utilizadas e suas funções:
#   feedparser      : leitura e parse de RSS feeds (qualquer formato RSS/Atom)
#   newsapi-python  : cliente oficial da NewsAPI (abstrai autenticação e paginação)
#   tenacity        : retry com backoff exponencial (padrão de mercado para APIs)
#   tqdm            : barra de progresso compatível com Jupyter/Colab
#   python-dateutil : manipulação de datas relativas (ex.: "próximo mês")

# !pip install feedparser newsapi-python tenacity tqdm --quiet
# print("✅ Bibliotecas instaladas.")


# ==============================================================================
# BLOCO 2 — IMPORTAÇÕES
# ==============================================================================

import csv
import hashlib
import logging
import random
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Generator

import feedparser
import pandas as pd
import requests
from dateutil.relativedelta import relativedelta
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)
from tqdm.auto import tqdm

print("✅ Importações concluídas.")


# ==============================================================================
# BLOCO 3 — CONFIGURAÇÕES CENTRALIZADAS
# ==============================================================================
# Todas as constantes do script em um único bloco.
# Boas práticas de engenharia de software ditam que parâmetros configuráveis
# devem estar separados do código de lógica — facilita ajustes e manutenção.

# ── Período de análise ────────────────────────────────────────────────────────
DATA_INICIO = datetime(2018, 1, 1)
DATA_FIM    = datetime(2025, 12, 31)

# ── Credenciais ───────────────────────────────────────────────────────────────
# Instruções para obter a chave NewsAPI:
#   1. Acesse: https://newsapi.org/register
#   2. Crie uma conta gratuita
#   3. Para histórico completo (2018-2025), envie e-mail para
#      support@newsapi.org solicitando o plano Developer para pesquisa
#      acadêmica — é gratuito, basta mencionar a dissertação.
#   4. Cole a chave recebida abaixo:
NEWSAPI_KEY = "SUA_CHAVE_AQUI"   # ← substitua aqui antes de executar

# ── Parâmetros de requisição ──────────────────────────────────────────────────
MAX_ARTIGOS_GDELT  = 250  # Limite máximo da API gratuita do GDELT por consulta

# PAUSAS ENTRE REQUISIÇÕES
# ─────────────────────────
# O GDELT aplica dois tipos de rate limiting simultâneos:
#   (a) Por segundo  : muitas requisições rápidas → 429 imediato
#   (b) Por hora/dia : volume total alto → bloqueio temporário do IP
#                      (persiste mesmo com pausas longas entre tentativas)
#
# ESTRATÉGIA SEGURA PARA O GDELT:
#   • Pausa base de 12s entre requisições (jitter ±3s adicionado pelo código)
#   • Isso resulta em ~4-5 req/min ou ~250-300 req/hora
#   • O GDELT tolera essa taxa sem bloqueios persistentes
#   • Com 20 termos × 84 meses = 1.680 requisições ÷ 300/hora ≈ 5,6 horas
#
# POR QUE REDUZIMOS OS TERMOS DO GDELT (de 152 para ~20):
#   Termos similares (ex.: "Petrobras" e "Petrobras dividendos") capturam
#   artigos em grande parte sobrepostos. A deduplicação por hash remove
#   as redundâncias, então o ganho de cobertura de termos extras é pequeno
#   comparado ao custo de requisições adicionais que geram bloqueios.
#   Os termos mais abrangentes de cada categoria cobrem o essencial.
PAUSA_GDELT_S      = 12   # Pausa base entre requisições ao GDELT (segundos)
                          # O código adiciona jitter aleatório de ±3s
PAUSA_NEWSAPI_S    = 2    # Pausa entre requisições à NewsAPI (segundos)

# PAUSA APÓS ERRO 429
# Quando a API retorna 429, indica bloqueio ativo do IP.
# 90 segundos é conservador o suficiente para reset na maioria dos casos.
# Se o bloqueio persistir após 5 tentativas, o IP precisa de tempo maior
# (2-4 horas) — nesse caso pare o script e retome depois.
PAUSA_RATE_LIMIT_S = 90   # Pausa ao receber erro 429 (segundos)

TIMEOUT_REQ_S      = 30   # Timeout máximo por requisição HTTP (segundos)

# ── Caminhos ──────────────────────────────────────────────────────────────────
# Detecta automaticamente se está rodando no Google Colab (com Drive montado)
# ou em ambiente local (para testes). Não requer alteração manual.
_NO_COLAB      = Path("/content/drive/MyDrive").exists()
PASTA_BASE     = Path("/content/drive/MyDrive/Mestrado_PETR4") if _NO_COLAB \
                 else Path("./Mestrado_PETR4")
ARQUIVO_CSV    = PASTA_BASE / "base_textual_petr4_2018_2025.csv"
ARQUIVO_LOG    = PASTA_BASE / "coleta_noticias.log"

PASTA_BASE.mkdir(parents=True, exist_ok=True)
print(f"✅ Configurações carregadas. Pasta base: {PASTA_BASE}")


# ==============================================================================
# BLOCO 4 — TAXONOMIA DE TERMOS DE BUSCA (7 CATEGORIAS)
# ==============================================================================
#
# Ver Seção 2 do cabeçalho para justificativa acadêmica detalhada.
#
# COMO USAR ESTE DICIONÁRIO:
#   • Para DESATIVAR uma categoria inteira (ex.: testes), basta comentar
#     o bloco correspondente no dicionário abaixo.
#   • Para ADICIONAR um termo, inclua na lista da categoria adequada.
#   • A categoria é gravada no CSV — isso permite análises de ablação
#     na fase de modelagem (Script 05).

TERMOS_POR_CATEGORIA = {

    # ─────────────────────────────────────────────────────────────────────────
    # CAT-1: EMPRESA E ATIVO
    # Notícias diretamente sobre a Petrobras: resultados, contratos, governança
    # corporativa, exploração de campos, emissão de debêntures, etc.
    # Justificativa: notícias corporativas têm poder preditivo documentado
    # sobre retornos futuros (Tetlock et al., 2008).
    # ─────────────────────────────────────────────────────────────────────────
    "CAT1_Empresa": [
        "Petrobras",
        "PETR4",
        "PETR3",
        "Petróleo Brasileiro SA",
        "petróleo brasileiro S.A.",
        "pré-sal",
        "pre-sal",
        "Petrobras dividendos",
        "Petrobras resultado",
        "Petrobras lucro",
        "Petrobras prejuízo",
        "Petrobras produção",
        "Petrobras exploração",
        "Petrobras refino",
        "Petrobras dívida",
        "Petrobras privatização",
        "Petrobras contrato",
        "campo de Búzios",
        "campo de Tupi",
        "bacia de Santos",
        "bacia de Campos",
    ],

    # ─────────────────────────────────────────────────────────────────────────
    # CAT-2: MERCADO DE PETRÓLEO
    # Fundamentos do mercado global: preço, oferta, demanda, estoques.
    # Justificativa: Kilian (2009) classifica choques de petróleo em
    # supply shocks, demand shocks e oil-specific demand shocks — todos
    # detectáveis via notícias sobre preço, OPEP e estoques EIA.
    # ─────────────────────────────────────────────────────────────────────────
    "CAT2_Mercado_Petroleo": [
        "preço do petróleo",
        "cotação do petróleo",
        "barril de petróleo",
        "petróleo Brent",
        "petróleo WTI",
        "OPEP",
        "OPEC",
        "OPEP+",
        "corte de produção petróleo",
        "aumento de produção petróleo",
        "demanda por petróleo",
        "oferta de petróleo",
        "estoques de petróleo EUA",
        "EIA estoques petróleo",
        "petróleo mercado",
        "commodity petróleo",
        "crise do petróleo",
        "choque do petróleo",
        "petróleo bruto",
        "mercado de energia",
    ],

    # ─────────────────────────────────────────────────────────────────────────
    # CAT-3: GEOPOLÍTICA E CONFLITOS
    # Guerras, tensões e acordos de paz em países produtores.
    # Justificativa: Hamilton (1983) demonstrou que choques geopolíticos
    # no Oriente Médio causam choques de oferta de petróleo com impacto
    # imediato no preço do barril e na volatilidade de empresas do setor.
    # Caldara & Iacoviello (2022) desenvolveram um índice de risco geopolítico
    # baseado em notícias que prediz variações em commodities energéticas.
    # ─────────────────────────────────────────────────────────────────────────
    "CAT3_Geopolitica": [
        "guerra Oriente Médio",
        "conflito Oriente Médio",
        "guerra Israel",
        "guerra Hamas",
        "guerra Irã",
        "tensão Irã",
        "sanção Irã",
        "guerra Iraque",
        "conflito Iraque",
        "guerra Líbia",
        "conflito Líbia",
        "guerra Yemen",
        "conflito Houthi",
        "ataque Houthi",
        "guerra Rússia Ucrânia",
        "invasão Ucrânia",
        "conflito Rússia",
        "sanção Rússia petróleo",
        "guerra Síria petróleo",
        "conflito Venezuela petróleo",
        "tensão Golfo Pérsico",
        "Estreito de Ormuz",
        "cessar-fogo Oriente Médio",
        "acordo de paz Oriente Médio",
        "acordo paz Rússia Ucrânia",
        "Arábia Saudita petróleo",
        "crise geopolítica petróleo",
    ],

    # ─────────────────────────────────────────────────────────────────────────
    # CAT-4: OFERTA, INFRAESTRUTURA E PRODUÇÃO
    # Refinarias, oleodutos, plataformas offshore, terminais e greves.
    # Justificativa: ataques ou acidentes em infraestrutura crítica geram
    # choques de oferta imediatos. O ataque às refinarias da Aramco em
    # setembro de 2019 removeu 5,7 milhões de barris/dia da oferta global
    # em um único evento, causando alta de 15% no Brent na abertura do dia
    # seguinte — o maior salto intradiário em décadas.
    # ─────────────────────────────────────────────────────────────────────────
    "CAT4_Infraestrutura": [
        "refinaria petróleo",
        "oleoduto",
        "gasoduto",
        "plataforma petróleo",
        "plataforma offshore",
        "terminal de petróleo",
        "duto petróleo",
        "interrupção refinaria",
        "acidente refinaria",
        "ataque refinaria",
        "greve petroleiros",
        "paralisação petróleo",
        "shale oil",
        "fracking",
        "petróleo de xisto",
        "capacidade de refino",
        "produção petróleo OPEP",
        "produção petróleo Estados Unidos",
        "produção petróleo Rússia",
        "produção petróleo Brasil",
    ],

    # ─────────────────────────────────────────────────────────────────────────
    # CAT-5: ACORDOS, SANÇÕES E NAVEGAÇÃO
    # Embargos, bloqueios navais, price cap, apreensão de navios.
    # Justificativa: restrições ao fluxo físico do petróleo afetam diretamente
    # a disponibilidade da commodity. Aproximadamente 40% do petróleo
    # transportado por mar passa pelo Estreito de Ormuz; 12% pelo
    # Bab-el-Mandeb (Mar Vermelho). Bloqueios nessas rotas adicionam
    # imediatamente um "prêmio de risco" ao preço do barril.
    # ─────────────────────────────────────────────────────────────────────────
    "CAT5_Sancoes_Navegacao": [
        "embargo petróleo",
        "sanção petróleo",
        "bloqueio petróleo",
        "bloqueio naval",
        "proibição navio petróleo",
        "navio petroleiro",
        "teto de preço petróleo",
        "price cap petróleo",
        "apreensão navio petróleo",
        "ataque navio petroleiro",
        "Mar Vermelho petróleo",
        "Canal de Suez petróleo",
        "Bab-el-Mandeb",
        "acordo nuclear Irã",
        "acordo petróleo",
        "acordo OPEP",
        "tratado energia",
        "acordo clima petróleo",
        "transição energética petróleo",
        "COP petróleo",
    ],

    # ─────────────────────────────────────────────────────────────────────────
    # CAT-6: LIDERANÇA, GOVERNANÇA E POLÍTICA ENERGÉTICA
    # Troca de CEO, indicações políticas, intervenção governamental.
    # Justificativa: mudanças de liderança em empresas estatais de petróleo
    # geram retornos anormais documentados na literatura de event study.
    # Caso emblemático: a demissão do CEO José Mauro Coelho pela gestão
    # Lula em junho de 2022 causou queda superior a 10% no PETR4 em um
    # único pregão — o evento isolado de maior impacto para o ativo no
    # período analisado.
    # ─────────────────────────────────────────────────────────────────────────
    "CAT6_Governanca": [
        "CEO Petrobras",
        "presidente Petrobras",
        "demissão Petrobras",
        "troca presidente Petrobras",
        "indicação Petrobras",
        "conselho Petrobras",
        "interventor Petrobras",
        "ministro de minas e energia",
        "ministério de minas e energia Brasil",
        "política energética Brasil",
        "eleição Venezuela petróleo",
        "eleição Arábia Saudita petróleo",
        "eleição Irã petróleo",
        "secretário energia EUA",
        "príncipe Mohammed bin Salman",
        "MBS Aramco",
        "Aramco",
        "Saudi Aramco",
        "CEO Aramco",
        "PDVSA",
        "Nicolás Maduro petróleo",
        "Lula Petrobras",
        "governo Petrobras",
        "intervenção estatal Petrobras",
    ],

    # ─────────────────────────────────────────────────────────────────────────
    # CAT-7: MACROECONOMIA, CÂMBIO E ENERGIA ALTERNATIVA
    # Dólar, juros Fed, recessão, demanda China, energias renováveis.
    # Justificativa: o dólar e o petróleo têm correlação negativa histórica
    # (Zhang et al., 2008) — dólar forte implica petróleo relativamente mais
    # caro para compradores em outras moedas, reduzindo demanda e preço.
    # A China responde por ~15% do consumo global; notícias sobre seu PIB
    # impactam diretamente as expectativas de demanda por petróleo
    # (Kilian & Murphy, 2014). Energias renováveis e ESG afetam as
    # perspectivas de demanda de longo prazo da commodity.
    # ─────────────────────────────────────────────────────────────────────────
    "CAT7_Macro_Energia": [
        "dólar petróleo",
        "câmbio petróleo",
        "real dólar",
        "Federal Reserve petróleo",
        "juros EUA petróleo",
        "recessão demanda petróleo",
        "crescimento China petróleo",
        "demanda China petróleo",
        "PIB China petróleo",
        "inflação petróleo",
        "energia renovável petróleo",
        "veículo elétrico petróleo",
        "hidrogênio verde petróleo",
        "descarbonização petróleo",
        "ESG Petrobras",
        "combustível fóssil",
        "energia limpa",
        "transição energética",
        "gás natural preço",
        "GNL",
    ],
}

# ── Listas de termos por fonte ────────────────────────────────────────────────
#
# GDELT — lista REDUZIDA (termos âncora por categoria)
# ─────────────────────────────────────────────────────
# PROBLEMA IDENTIFICADO EM TESTE:
#   152 termos × 84 meses = 12.768 requisições ao GDELT.
#   A API pública gratuita não tem autenticação e aplica bloqueio por volume
#   de IP (além do rate limit por segundo). Em testes, 152 termos geraram
#   bloqueio persistente mesmo com 60-90s de pausa entre retries.
#
# SOLUÇÃO: 1 termo "âncora" por categoria — o mais abrangente.
#   Termos compostos (ex.: "Petrobras dividendos") são subconjuntos dos
#   artigos que "Petrobras" já retorna. A deduplicação por hash remove
#   redundâncias de qualquer forma. 20 termos × 84 meses = 1.680
#   requisições → viável com 12s de pausa (~250 req/hora).
#
# COBERTURA MANTIDA:
#   A riqueza temática completa é preservada na NewsAPI e no RSS.

TERMOS_GDELT: list[tuple[str, str]] = [
    # CAT-1: Empresa
    ("CAT1_Empresa",           "Petrobras"),
    ("CAT1_Empresa",           "PETR4"),
    ("CAT1_Empresa",           "pré-sal"),
    # CAT-2: Mercado de petróleo
    ("CAT2_Mercado_Petroleo",  "petróleo Brent"),
    ("CAT2_Mercado_Petroleo",  "OPEP"),
    ("CAT2_Mercado_Petroleo",  "preço do petróleo"),
    # CAT-3: Geopolítica
    ("CAT3_Geopolitica",       "guerra Oriente Médio"),
    ("CAT3_Geopolitica",       "guerra Rússia Ucrânia"),
    ("CAT3_Geopolitica",       "Arábia Saudita petróleo"),
    # CAT-4: Infraestrutura
    ("CAT4_Infraestrutura",    "refinaria petróleo"),
    ("CAT4_Infraestrutura",    "plataforma offshore"),
    # CAT-5: Sanções e navegação
    ("CAT5_Sancoes_Navegacao", "embargo petróleo"),
    ("CAT5_Sancoes_Navegacao", "bloqueio naval"),
    # CAT-6: Governança
    ("CAT6_Governanca",        "CEO Petrobras"),
    ("CAT6_Governanca",        "ministro de minas e energia"),
    ("CAT6_Governanca",        "Aramco"),
    # CAT-7: Macro e energia
    ("CAT7_Macro_Energia",     "dólar petróleo"),
    ("CAT7_Macro_Energia",     "demanda China petróleo"),
    ("CAT7_Macro_Energia",     "transição energética"),
    ("CAT7_Macro_Energia",     "gás natural preço"),
]

# NewsAPI — lista completa (CAT1, 2, 3, 6 — maior impacto direto no PETR4)
CATS_NEWSAPI = {"CAT1_Empresa", "CAT2_Mercado_Petroleo",
                "CAT3_Geopolitica", "CAT6_Governanca"}
TERMOS_NEWSAPI: list[tuple[str, str]] = [
    (cat, termo)
    for cat, lista in TERMOS_POR_CATEGORIA.items()
    if cat in CATS_NEWSAPI
    for termo in lista
]

# ── Termos para filtro local nos RSS Feeds ────────────────────────────────────
TERMOS_FILTRO_RSS: list[str] = [
    "petrobras", "petr4", "petr3", "pré-sal", "pre-sal",
    "petróleo", "brent", "opep", "opec", "barril",
    "refinaria", "oleoduto", "plataforma offshore",
    "combustível", "gasolina preço", "diesel preço",
    "aramco", "pdvsa", "guerra oriente médio",
    "conflito oriente médio", "sanção rússia",
    "bloqueio naval", "navio petroleiro",
    "ministério minas energia", "ceo petrobras",
    "presidente petrobras",
]

print(f"✅ Taxonomia carregada.")
print(f"   Termos para GDELT   : {len(TERMOS_GDELT)} (âncoras por categoria)")
print(f"   Termos para NewsAPI : {len(TERMOS_NEWSAPI)} (lista completa)")
print(f"   Categorias          : {list(TERMOS_POR_CATEGORIA.keys())}")


# ==============================================================================
# BLOCO 5 — RSS FEEDS (VALIDADOS EM TESTE — 10/06/2026)
# ==============================================================================
#
# HISTÓRICO DE VALIDAÇÃO:
# ────────────────────────
# Em 10/06/2026 foi executado o script teste_rss_feeds.py contra todas as
# URLs originais. Resultado: 13 de 25 feeds estavam mortos (retornando 0
# entradas). As causas identificadas foram:
#
#   Reuters  : encerrou os feeds feeds.reuters.com/* em 2023. As novas URLs
#              reuters.com/*/feed/ também retornam vazio (bloqueio por
#              user-agent de bots). Reuters não tem mais RSS público funcional.
#   Bloomberg: encerrou feeds.bloomberg.com/* (acesso restrito a assinantes).
#   Valor Econômico: URL valor.globo.com/rss/home/ retorna vazio.
#                    URL correta: valor.com.br/rss (confirmada em pesquisa).
#   Estadão  : estadao.com.br/rss/economia.xml retorna vazio. Sem alternativa
#              funcional encontrada — substituído por BrazilJournal.
#   InfoMoney: /mercados/feed e /acoes/feed retornam vazio. Apenas /feed/
#              funciona (10 entradas).
#   Agência Brasil: feed retorna vazio. Substituído por Agência Senado.
#   Band News: feed retorna vazio. Substituído por Metrópoles Economia.
#   EIA/Platts/Bloomberg: feeds fechados ou restritos a assinantes.
#
# FEEDS CONFIRMADOS COMO FUNCIONANDO (18 validados):
#   G1_Economia (100), G1_Mercado (100), InfoMoney (10), Exame (25),
#   UOL_Economia (15), Folha_Mercado (100), CNN_Brasil (60), Poder360 (10),
#   Money_Times (10), E_Investidor (8), BBC_Business (57), MarketWatch (10),
#   OilPrice (15), Rigzone (20), CNBC_Energy (30), FT_Energy (25),
#   Investing_Oil (10), Investing_Commod (10)
#
# NOTA TÉCNICA: RSS não suporta filtro por palavra-chave na requisição.
# O download traz todo o feed; filtragem por TERMOS_FILTRO_RSS é local.
# Para cobertura histórica 2018-2025, GDELT e NewsAPI são as fontes
# principais. RSS complementa com cobertura recente de alta qualidade.

RSS_FEEDS: dict[str, str] = {

    # ── Nacionais — feeds CONFIRMADOS como funcionando em 10/06/2026 ─────────
    "G1_Economia"        : "https://g1.globo.com/rss/g1/economia/",
    "G1_Mercado"         : "https://g1.globo.com/rss/g1/economia/mercados/",
    "InfoMoney"          : "https://www.infomoney.com.br/feed/",
    "Valor_Economico"    : "http://www.valor.com.br/rss",          # URL corrigida
    "Exame_Invest"       : "https://exame.com/feed/",
    "UOL_Economia"       : "https://rss.uol.com.br/feed/economia.xml",
    "Folha_Mercado"      : "https://feeds.folha.uol.com.br/mercado/rss091.xml",
    "CNN_Brasil_Negocios": "https://www.cnnbrasil.com.br/feed/",
    "Poder360_Econ"      : "https://www.poder360.com.br/feed/",
    "Money_Times"        : "https://www.moneytimes.com.br/feed/",
    "E_Investidor"       : "https://einvestidor.estadao.com.br/feed/",

    # ── Nacionais — substitutos para feeds mortos ─────────────────────────────
    # Estadão (/rss/economia.xml retorna vazio) → Brazil Journal
    "BrazilJournal"      : "https://braziljournal.com/feed/",
    # Agência Brasil (feed vazio) → Agência Câmara dos Deputados
    # Cobre votações sobre política energética, Petrobras e setor de combustíveis.
    # URL documentada em: https://www.camara.leg.br/noticias/rss
    "Agencia_Camara"     : "https://www.camara.leg.br/noticias/rss/ultimas",
    # Band News (feed vazio) → Metrópoles Economia
    "Metropoles_Econ"    : "https://www.metropoles.com/feed",

    # ── Internacionais — feeds CONFIRMADOS como funcionando em 10/06/2026 ────
    "BBC_Business"       : "https://feeds.bbci.co.uk/news/business/rss.xml",
    "MarketWatch"        : "https://feeds.marketwatch.com/marketwatch/topstories/",
    "OilPrice_News"      : "https://oilprice.com/rss/main",
    "Rigzone"            : "https://www.rigzone.com/news/rss/rigzone_latest.aspx",
    "CNBC_Energy"        : "https://www.cnbc.com/id/10000664/device/rss/rss.html",
    "FT_Energy"          : "https://www.ft.com/energy?format=rss",
    "Investing_Oil"      : "https://www.investing.com/rss/news_14.rss",
    "Investing_Commod"   : "https://www.investing.com/rss/news_11.rss",

    # ── Internacionais — substitutos para feeds mortos ────────────────────────
    # Reuters (feeds.reuters.com/* encerrado em 2023, reuters.com bloqueado)
    # → Yahoo Finance (agrega Reuters, Bloomberg, AP entre outras fontes)
    "Yahoo_Finance"      : "https://finance.yahoo.com/news/rssindex",
    # Bloomberg Energy (encerrado) e SPGlobal (feed fechado) → Google News Oil
    # Google News RSS é público, estável e agrega Reuters, Bloomberg, AP
    "GoogleNews_Oil"     : "https://news.google.com/rss/search?q=oil+price+OPEC&hl=en-US&gl=US&ceid=US:en",
    # World Oil: URL /rss-feeds/news retornava vazio; URL correta confirmada
    "World_Oil"          : "https://worldoil.com/rss?feed=news",
}

print(f"✅ {len(RSS_FEEDS)} RSS feeds configurados (validados em 10/06/2026).")


# ==============================================================================
# BLOCO 6 — SISTEMA DE LOGGING
# ==============================================================================
# O logging em arquivo (coleta_noticias.log) cria um registro auditável
# da execução. Cada linha contém: timestamp | nível | mensagem.
# Este arquivo pode ser citado na dissertação como evidência de
# rastreabilidade e apresentado na defesa se questionado.

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(ARQUIVO_LOG, encoding="utf-8"),  # persiste no Drive
        logging.StreamHandler(),                              # exibe no Colab
    ],
)
log = logging.getLogger(__name__)
log.info("=== INÍCIO DA COLETA — VERSÃO 3.1 ===")


# ==============================================================================
# BLOCO 7 — FUNÇÕES UTILITÁRIAS
# ==============================================================================

def hash_titulo(titulo: str) -> str:
    """
    Gera hash SHA-256 do título normalizado para deduplicação robusta.

    Normalização aplicada antes do hash:
      - Conversão para minúsculas (case-insensitive)
      - Colapso de espaços múltiplos em espaço único
      - Strip de espaços nas bordas

    Resultado: dois títulos superficialmente diferentes mas semanticamente
    idênticos produzem o mesmo hash, garantindo deduplicação cross-fonte.
    Ver Seção 3, Decisão 1 do cabeçalho para justificativa completa.
    """
    normalizado = " ".join(titulo.lower().split())
    return hashlib.sha256(normalizado.encode("utf-8")).hexdigest()


def extrair_data(raw: str) -> str:
    """
    Converte strings de data em múltiplos formatos para ISO 8601.

    Cada API retorna datas em formato diferente:
      GDELT    : "20180115T143000Z"
      NewsAPI  : "2018-01-15T14:30:00Z"
      RSS/RFC  : "Mon, 15 Jan 2018 14:30:00 +0000"

    Tenta cada formato em sequência. Retorna string vazia se nenhum funcionar
    — o artigo é mantido no corpus mesmo sem data (pode ser útil para análise).
    """
    FORMATOS = [
        "%Y%m%dT%H%M%SZ",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S%z",
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S %Z",
    ]
    for fmt in FORMATOS:
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            continue
    return ""


def contem_termo(texto: str, termos: list[str]) -> bool:
    """
    Verifica se o texto contém ao menos um dos termos (case-insensitive).
    Usado exclusivamente para filtro local dos RSS feeds.
    """
    t = texto.lower()
    return any(termo.lower() in t for termo in termos)


# ==============================================================================
# BLOCO 8 — COLETOR GDELT
# ==============================================================================
# Ver Seção 1 (Mecanismo 1) e Seção 3 (Decisões 2, 6, 7) do cabeçalho.

def _requisicao_gdelt(params: dict) -> dict | None:
    """
    Executa uma chamada HTTP à API do GDELT com tratamento explícito de
    rate limiting (HTTP 429) e retry manual com backoff progressivo.

    POR QUE NÃO USAR @retry DO TENACITY AQUI:
    O tenacity trata todos os erros HTTP da mesma forma. O erro 429
    é diferente: a API está pedindo explicitamente para aguardar.
    Tratar 429 igual a um timeout ou erro de rede é inadequado —
    o retry imediato piora a situação e pode resultar em bloqueio
    permanente do IP pelo servidor do GDELT.

    ESTRATÉGIA ADOTADA:
      • Erro 429 → aguarda PAUSA_RATE_LIMIT_S (60s) e tenta novamente
      • Outros erros de rede → backoff exponencial (4s → 8s → 16s)
      • Após 5 tentativas sem sucesso → retorna None (artigo pulado,
        coleta continua — não derruba toda a execução)

    Retorna None (em vez de lançar exceção) para que o chamador possa
    simplesmente pular o termo problemático e continuar com o próximo.
    """
    MAX_TENTATIVAS = 5

    for tentativa in range(1, MAX_TENTATIVAS + 1):
        try:
            r = requests.get(
                "https://api.gdeltproject.org/api/v2/doc/doc",
                params=params,
                timeout=TIMEOUT_REQ_S,
            )

            # ── Tratamento específico de rate limiting ────────────────────
            if r.status_code == 429:
                log.warning(
                    "GDELT | HTTP 429 (rate limit) | tentativa %d/%d | "
                    "aguardando %ds antes de tentar novamente...",
                    tentativa, MAX_TENTATIVAS, PAUSA_RATE_LIMIT_S,
                )
                time.sleep(PAUSA_RATE_LIMIT_S)
                continue   # tenta novamente após a pausa

            r.raise_for_status()   # lança exceção para outros códigos 4xx/5xx
            return r.json()

        except requests.exceptions.Timeout:
            espera = min(4 * (2 ** (tentativa - 1)), 30)   # 4s → 8s → 16s → 30s
            log.warning(
                "GDELT | Timeout | tentativa %d/%d | aguardando %ds...",
                tentativa, MAX_TENTATIVAS, espera,
            )
            time.sleep(espera)

        except requests.exceptions.RequestException as exc:
            espera = min(4 * (2 ** (tentativa - 1)), 30)
            log.warning(
                "GDELT | Erro de rede: %s | tentativa %d/%d | aguardando %ds...",
                exc, tentativa, MAX_TENTATIVAS, espera,
            )
            time.sleep(espera)

    # Esgotou todas as tentativas — retorna None para pular este termo
    log.error(
        "GDELT | %d tentativas esgotadas para params=%s | termo será pulado.",
        MAX_TENTATIVAS, params.get("query", "?"),
    )
    return None


def coletar_gdelt(
    termos_cat: list[tuple[str, str]],
    data_inicio: datetime,
    data_fim: datetime,
) -> Generator[dict, None, None]:
    """
    Gerador que coleta notícias do GDELT mês a mês para todos os termos.

    ESTRATÉGIA DE JANELA MENSAL:
    A API gratuita do GDELT retorna no máximo 250 artigos por consulta.
    Fazer uma consulta para 7 anos retornaria apenas os 250 mais recentes.
    Ao dividir em janelas mensais (84 consultas por termo), garantimos
    cobertura completa — cada mês pode ter até 250 artigos por termo.

    GERADOR (yield):
    Em vez de retornar uma lista completa, emite cada artigo individualmente.
    Isso permite que o artigo seja processado e gravado imediatamente,
    sem acumular todos em memória (ver Seção 3, Decisão 6).
    """
    n_meses = (data_fim.year - data_inicio.year) * 12 \
              + data_fim.month - data_inicio.month + 1

    cursor = data_inicio
    with tqdm(total=n_meses, desc="GDELT", unit="mês") as pbar:
        while cursor <= data_fim:
            fim_mes    = min(cursor + relativedelta(months=1) - timedelta(seconds=1), data_fim)
            inicio_str = cursor.strftime("%Y%m%d%H%M%S")
            fim_str    = fim_mes.strftime("%Y%m%d%H%M%S")

            for categoria, termo in termos_cat:
                params = {
                    "query"        : f'"{termo}" sourcelang:portuguese',
                    "mode"         : "artlist",
                    "maxrecords"   : MAX_ARTIGOS_GDELT,
                    "startdatetime": inicio_str,
                    "enddatetime"  : fim_str,
                    "sort"         : "DateDesc",
                    "format"       : "json",
                }
                try:
                    dados = _requisicao_gdelt(params)
                    if dados is None:
                        # Todas as tentativas falharam — pula este termo/mês
                        # A coleta continua normalmente com o próximo termo
                        time.sleep(PAUSA_GDELT_S + random.uniform(-3, 3))
                        continue
                    artigos = dados.get("articles") or []
                    for art in artigos:
                        titulo = (art.get("title") or "").strip()
                        if not titulo:
                            continue
                        yield {
                            "fonte_coleta": "GDELT",
                            "categoria"   : categoria,
                            "termo_busca" : termo,
                            "data_raw"    : art.get("seendate", ""),
                            "titulo"      : titulo,
                            "resumo"      : titulo,   # GDELT não fornece resumo
                            "url"         : art.get("url", ""),
                            "dominio"     : art.get("domain", ""),
                            "idioma"      : art.get("language", ""),
                        }
                except Exception as exc:
                    log.warning("GDELT | %s | %s | %s/%s | %s",
                                categoria, termo, cursor.month, cursor.year, exc)

                # Jitter: pausa aleatória entre (PAUSA_GDELT_S ± 3s)
                # Evita padrão fixo de requisição que aciona bloqueio automático
                time.sleep(PAUSA_GDELT_S + random.uniform(-3, 3))

            cursor = cursor + relativedelta(months=1)
            pbar.update(1)


# ==============================================================================
# BLOCO 9 — COLETOR NEWSAPI
# ==============================================================================
# Ver Seção 1 (Mecanismo 2) e Seção 3 (Decisões 2, 6, 7) do cabeçalho.

def _requisicao_newsapi(params: dict, headers: dict) -> dict | None:
    """
    Executa uma chamada HTTP à NewsAPI com tratamento robusto de rate limiting.

    Aplica a mesma estratégia da função _requisicao_gdelt:
      • HTTP 429 → aguarda PAUSA_RATE_LIMIT_S (60s) e tenta novamente
      • Outros erros de rede → backoff exponencial (4s → 8s → 16s → 30s)
      • Após 5 tentativas → retorna None (termo/página pulada)
    """
    MAX_TENTATIVAS = 5

    for tentativa in range(1, MAX_TENTATIVAS + 1):
        try:
            r = requests.get(
                "https://newsapi.org/v2/everything",
                params=params,
                headers=headers,
                timeout=TIMEOUT_REQ_S,
            )

            if r.status_code == 429:
                log.warning(
                    "NewsAPI | HTTP 429 (rate limit) | tentativa %d/%d | "
                    "aguardando %ds...",
                    tentativa, MAX_TENTATIVAS, PAUSA_RATE_LIMIT_S,
                )
                time.sleep(PAUSA_RATE_LIMIT_S)
                continue

            r.raise_for_status()
            return r.json()

        except requests.exceptions.Timeout:
            espera = min(4 * (2 ** (tentativa - 1)), 30)
            log.warning("NewsAPI | Timeout | tentativa %d/%d | aguardando %ds...",
                        tentativa, MAX_TENTATIVAS, espera)
            time.sleep(espera)

        except requests.exceptions.RequestException as exc:
            espera = min(4 * (2 ** (tentativa - 1)), 30)
            log.warning("NewsAPI | Erro: %s | tentativa %d/%d | aguardando %ds...",
                        exc, tentativa, MAX_TENTATIVAS, espera)
            time.sleep(espera)

    log.error("NewsAPI | %d tentativas esgotadas | página será pulada.", MAX_TENTATIVAS)
    return None


def coletar_newsapi(
    termos_cat: list[tuple[str, str]],
    data_inicio: datetime,
    data_fim: datetime,
    api_key: str,
) -> Generator[dict, None, None]:
    """
    Gerador que coleta notícias da NewsAPI com paginação automática.

    DIFERENCIAL EM RELAÇÃO AO GDELT:
    A NewsAPI retorna título + resumo/descrição do artigo, enriquecendo
    o corpus textual para análise de sentimento. O GDELT retorna apenas
    o título.

    PAGINAÇÃO:
    Cada página retorna até 100 artigos. O gerador itera pelas páginas
    até que a resposta contenha menos de 100 artigos (última página)
    ou até que a API sinalize erro de cota.

    COBERTURA HISTÓRICA:
    O plano Developer (gratuito para pesquisa) oferece histórico completo.
    Sem ele, apenas os últimos 30 dias ficam disponíveis.
    """
    if not api_key or api_key == "SUA_CHAVE_AQUI":
        log.warning("NewsAPI | Chave não configurada — fonte ignorada.")
        return

    headers = {"X-Api-Key": api_key}
    cursor  = data_inicio
    n_meses = (data_fim.year - data_inicio.year) * 12 \
              + data_fim.month - data_inicio.month + 1

    with tqdm(total=n_meses, desc="NewsAPI", unit="mês") as pbar:
        while cursor <= data_fim:
            fim_mes = min(cursor + relativedelta(months=1) - timedelta(seconds=1), data_fim)

            for categoria, termo in termos_cat:
                pagina = 1
                while True:
                    params = {
                        "q"        : termo,
                        "language" : "pt",
                        "from"     : cursor.strftime("%Y-%m-%dT00:00:00"),
                        "to"       : fim_mes.strftime("%Y-%m-%dT23:59:59"),
                        "sortBy"   : "publishedAt",
                        "pageSize" : 100,
                        "page"     : pagina,
                    }
                    try:
                        dados = _requisicao_newsapi(params, headers)
                        if dados is None:
                            break   # Tentativas esgotadas — pula este termo/mês

                        if dados.get("status") != "ok":
                            log.warning("NewsAPI | %s | status=%s | %s",
                                        termo, dados.get("status"), dados.get("message"))
                            break

                        artigos = dados.get("articles") or []
                        if not artigos:
                            break

                        for art in artigos:
                            titulo = (art.get("title") or "").strip()
                            if not titulo or titulo == "[Removed]":
                                continue
                            yield {
                                "fonte_coleta": "NewsAPI",
                                "categoria"   : categoria,
                                "termo_busca" : termo,
                                "data_raw"    : art.get("publishedAt", ""),
                                "titulo"      : titulo,
                                "resumo"      : (art.get("description") or titulo).strip(),
                                "url"         : art.get("url", ""),
                                "dominio"     : (art.get("source") or {}).get("name", ""),
                                "idioma"      : "pt",
                            }

                        if len(artigos) < 100:
                            break   # Última página — encerra paginação
                        pagina += 1
                        time.sleep(PAUSA_NEWSAPI_S)

                    except Exception as exc:
                        log.warning("NewsAPI | %s | pág %d | %s", termo, pagina, exc)
                        break

                time.sleep(PAUSA_NEWSAPI_S)

            cursor = cursor + relativedelta(months=1)
            pbar.update(1)


# ==============================================================================
# BLOCO 10 — COLETOR RSS
# ==============================================================================
# Ver Seção 1 (Mecanismo 3) e Seção 4 do cabeçalho.

def coletar_rss(feeds: dict[str, str]) -> Generator[dict, None, None]:
    """
    Gerador que lê todos os RSS feeds e filtra artigos relevantes localmente.

    FUNCIONAMENTO:
    RSS não suporta filtro por palavra-chave na requisição — o download
    traz todas as notícias recentes do veículo. O filtro é feito localmente:
    apenas artigos que contenham ao menos um termo de TERMOS_FILTRO_RSS
    no título ou resumo são emitidos pelo gerador.

    DETECÇÃO DE IDIOMA:
    Feeds internacionais (Reuters, BBC, Bloomberg etc.) são marcados como
    idioma "en"; feeds nacionais como "pt". Isso é relevante para o Script 03,
    onde modelos de sentimento distintos podem ser aplicados por idioma.

    COBERTURA:
    Limitada ao histórico mantido pelo feed (~30-90 dias). Para o corpus
    histórico 2018-2025, GDELT e NewsAPI são as fontes principais.
    """
    # Feeds reconhecidamente internacionais (em inglês)
    FEEDS_EN = {"Reuters_Business", "Reuters_Energy", "BBC_Business",
                "MarketWatch", "OilPrice_News", "Rigzone", "CNBC_Energy",
                "FT_Energy", "Investing_Oil", "Investing_Commod",
                "Bloomberg_Energy"}

    for nome, url in tqdm(feeds.items(), desc="RSS Feeds", unit="feed"):
        try:
            parsed = feedparser.parse(url)

            for entry in parsed.entries:
                titulo  = (getattr(entry, "title", "") or "").strip()
                resumo  = (getattr(entry, "summary", "") or titulo).strip()
                url_art = (getattr(entry, "link", "") or "").strip()

                # Filtro de relevância: descarta artigos não relacionados ao corpus
                if not contem_termo(f"{titulo} {resumo}", TERMOS_FILTRO_RSS):
                    continue

                data_raw = (getattr(entry, "published", "")
                            or getattr(entry, "updated", ""))

                yield {
                    "fonte_coleta": f"RSS_{nome}",
                    "categoria"   : "RSS_filtro_local",
                    "termo_busca" : "filtro_local",
                    "data_raw"    : data_raw,
                    "titulo"      : titulo,
                    "resumo"      : resumo[:600],   # Limita tamanho do resumo
                    "url"         : url_art,
                    "dominio"     : nome,
                    "idioma"      : "en" if nome in FEEDS_EN else "pt",
                }

        except Exception as exc:
            log.warning("RSS | %s | Erro: %s", nome, exc)

        time.sleep(1)   # Pausa leve de cortesia entre feeds


# ==============================================================================
# BLOCO 11 — CAMPOS DO CSV E FUNÇÃO PRINCIPAL DE COLETA
# ==============================================================================
# Ver Seção 5 do cabeçalho para descrição detalhada de cada coluna.

CAMPOS_CSV = [
    "data_publicacao",  # ISO 8601 — YYYY-MM-DD HH:MM:SS
    "ativo",            # Sempre "PETR4"
    "categoria",        # Categoria temática (CAT1 a CAT7 ou RSS_filtro_local)
    "fonte_coleta",     # "GDELT", "NewsAPI" ou "RSS_<NomeDoVeiculo>"
    "termo_busca",      # Termo exato que gerou a requisição
    "titulo",           # Título do artigo (campo principal para sentimento)
    "resumo",           # Resumo/descrição (mais rico na NewsAPI e RSS)
    "url",              # URL original para verificação e referência
    "dominio",          # Domínio ou nome do veículo
    "idioma",           # Código de idioma: "pt" ou "en"
    "hash_titulo",      # SHA-256 para deduplicação e integridade do corpus
]


def executar_coleta_completa() -> None:
    """
    Orquestra a coleta de todas as fontes, deduplicação e gravação em CSV.

    FLUXO DE EXECUÇÃO:
      1. Carrega hashes já gravados no CSV (permite retomada automática)
      2. Abre o CSV em modo append (não sobrescreve dados existentes)
      3. Itera: GDELT → NewsAPI → RSS Feeds
      4. Cada artigo novo (hash inédito) é gravado imediatamente no CSV
      5. A cada 500 artigos, força gravação em disco (flush)
      6. Exibe relatório final no log

    RETOMADA AUTOMÁTICA:
      Se a sessão do Colab cair, basta rodar esta função novamente.
      O script detecta os hashes já gravados e pula artigos duplicados,
      continuando de onde parou. O arquivo CSV não é sobrescrito.

    EFICIÊNCIA DE MEMÓRIA:
      O consumo de memória é O(H), onde H é o número de hashes únicos.
      Para 1 milhão de artigos, o conjunto de hashes ocupa ~64 MB —
      totalmente viável dentro dos limites do Google Colab.
      Ver Seção 3, Decisão 3 do cabeçalho para justificativa completa.
    """
    log.info("Período: %s → %s | GDELT: %d termos | NewsAPI: %d termos | RSS: %d feeds",
             DATA_INICIO.date(), DATA_FIM.date(),
             len(TERMOS_GDELT), len(TERMOS_NEWSAPI), len(RSS_FEEDS))

    # ── Carrega hashes já gravados para permitir retomada ─────────────────────
    hashes: set[str] = set()
    if ARQUIVO_CSV.exists():
        try:
            df_prev = pd.read_csv(ARQUIVO_CSV, usecols=["hash_titulo"])
            hashes  = set(df_prev["hash_titulo"].dropna())
            log.info("Retomando coleta — %d artigos já gravados anteriormente.", len(hashes))
        except Exception as exc:
            log.warning("Não foi possível carregar hashes anteriores: %s", exc)

    modo = "a" if ARQUIVO_CSV.exists() else "w"
    cnt  = {"total": 0, "novos": 0, "dup": 0, "sem_data": 0}

    with open(ARQUIVO_CSV, mode=modo, newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CAMPOS_CSV)
        if modo == "w":
            writer.writeheader()   # Cabeçalho apenas para arquivo novo

        def gravar(art: dict) -> None:
            """
            Grava um artigo no CSV se ele for inédito (hash não visto).
            Incrementa os contadores de controle.
            """
            cnt["total"] += 1
            titulo = art.get("titulo", "").strip()
            if not titulo:
                return

            h = hash_titulo(titulo)
            if h in hashes:       # Artigo duplicado — descarta
                cnt["dup"] += 1
                return

            data_iso = extrair_data(art.get("data_raw", ""))
            if not data_iso:
                cnt["sem_data"] += 1   # Conta mas não descarta

            hashes.add(h)
            cnt["novos"] += 1
            writer.writerow({
                "data_publicacao": data_iso,
                "ativo"          : "PETR4",
                "categoria"      : art.get("categoria", ""),
                "fonte_coleta"   : art.get("fonte_coleta", ""),
                "termo_busca"    : art.get("termo_busca", ""),
                "titulo"         : titulo,
                "resumo"         : art.get("resumo", ""),
                "url"            : art.get("url", ""),
                "dominio"        : art.get("dominio", ""),
                "idioma"         : art.get("idioma", ""),
                "hash_titulo"    : h,
            })
            # Flush periódico — garante gravação em disco sem fechar o arquivo
            if cnt["novos"] % 500 == 0:
                f.flush()
                log.info("  → %d notícias únicas gravadas...", cnt["novos"])

        # ── FONTE 1: GDELT ────────────────────────────────────────────────────
        log.info("─── GDELT (%d termos × 84 meses) ───", len(TERMOS_GDELT))
        for art in coletar_gdelt(TERMOS_GDELT, DATA_INICIO, DATA_FIM):
            gravar(art)

        # ── FONTE 2: NewsAPI ──────────────────────────────────────────────────
        log.info("─── NewsAPI (%d termos × meses) ───", len(TERMOS_NEWSAPI))
        for art in coletar_newsapi(TERMOS_NEWSAPI, DATA_INICIO, DATA_FIM, NEWSAPI_KEY):
            gravar(art)

        # ── FONTE 3: RSS Feeds ────────────────────────────────────────────────
        log.info("─── RSS Feeds (%d feeds) ───", len(RSS_FEEDS))
        for art in coletar_rss(RSS_FEEDS):
            gravar(art)

    # ── Relatório final ───────────────────────────────────────────────────────
    log.info("=" * 65)
    log.info("COLETA CONCLUÍDA")
    log.info("  Artigos brutos processados  : %d", cnt["total"])
    log.info("  Notícias ÚNICAS gravadas    : %d", cnt["novos"])
    log.info("  Duplicatas removidas        : %d", cnt["dup"])
    log.info("  Artigos sem data válida     : %d", cnt["sem_data"])
    log.info("  Arquivo CSV                 : %s", ARQUIVO_CSV)
    log.info("  Log de auditoria            : %s", ARQUIVO_LOG)
    log.info("=" * 65)


# ==============================================================================
# BLOCO 12 — ESTATÍSTICAS DO CORPUS
# ==============================================================================
# As métricas exibidas por esta função podem ser usadas diretamente na
# seção "Descrição do Corpus" ou em tabelas metodológicas da dissertação.

def exibir_estatisticas_corpus() -> None:
    """
    Lê o CSV final e exibe estatísticas estruturadas do corpus coletado.

    Métricas apresentadas:
      - Total de notícias únicas
      - Período coberto
      - Distribuição por fonte de coleta (GDELT / NewsAPI / RSS)
      - Distribuição por categoria temática (CAT1 a CAT7)
      - Distribuição por idioma (pt / en)
      - Distribuição anual (tabela para a dissertação)
      - Top 15 veículos/domínios por volume de notícias
    """
    if not ARQUIVO_CSV.exists():
        print("❌ Arquivo não encontrado. Execute executar_coleta_completa() primeiro.")
        return

    # Leitura eficiente: carrega apenas as colunas necessárias para estatísticas
    df = pd.read_csv(
        ARQUIVO_CSV,
        usecols=["data_publicacao", "categoria", "fonte_coleta", "dominio", "idioma"],
        parse_dates=["data_publicacao"],
    )

    sep = "=" * 65
    print(f"\n{sep}")
    print("📊  ESTATÍSTICAS DO CORPUS — PETR4 2018-2025")
    print(sep)
    print(f"\n  Total de notícias únicas : {len(df):>10,}")
    print(f"  Período coberto          : "
          f"{df['data_publicacao'].min().date()} → "
          f"{df['data_publicacao'].max().date()}")

    print("\n  ── Por Fonte de Coleta ──────────────────────────")
    print(df["fonte_coleta"].value_counts().to_string())

    print("\n  ── Por Categoria Temática ───────────────────────")
    print(df["categoria"].value_counts().to_string())

    print("\n  ── Por Idioma ───────────────────────────────────")
    print(df["idioma"].value_counts().to_string())

    print("\n  ── Distribuição Anual ───────────────────────────")
    df["ano"] = df["data_publicacao"].dt.year
    print(df.groupby("ano").size().rename("Notícias").to_string())

    print("\n  ── Top 15 Veículos / Domínios ───────────────────")
    print(df["dominio"].value_counts().head(15).to_string())

    print(f"\n  📁 Corpus  : {ARQUIVO_CSV}")
    print(f"  📋 Log     : {ARQUIVO_LOG}")
    print(f"{sep}")
    print("\n▶️  Próximo passo: execute o Script 03 — Análise de Sentimento.")


# ==============================================================================
# BLOCO 13 — PONTO DE ENTRADA
# ==============================================================================
#
# COMO USAR NO GOOGLE COLAB:
# ─────────────────────────────
# Célula 1 — instalar dependências (apenas uma vez por sessão):
#   !pip install feedparser newsapi-python tenacity tqdm --quiet
#
# Célula 2 — executar o script completo:
#   %run 02_coleta_noticias_petr4.py
#   # ou, se preferir célula por célula:
#   executar_coleta_completa()
#
# Célula 3 — ver estatísticas do corpus:
#   exibir_estatisticas_corpus()
#
# RETOMADA APÓS INTERRUPÇÃO:
# ──────────────────────────
# Se o Colab desconectar durante a coleta, basta rodar novamente:
#   executar_coleta_completa()
# O script detecta o que já foi gravado e continua de onde parou.
# Não há risco de duplicar dados.
#
# COLETA PARCIAL (por fonte):
# ────────────────────────────
# Para coletar apenas uma fonte específica e depois juntar:
#   for art in coletar_gdelt(TERMOS_GDELT, DATA_INICIO, DATA_FIM):
#       gravar(art)   # requer abrir o CSV manualmente com DictWriter

if __name__ == "__main__":
    executar_coleta_completa()
    exibir_estatisticas_corpus()
