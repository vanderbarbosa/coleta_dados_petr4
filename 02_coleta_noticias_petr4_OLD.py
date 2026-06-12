# -*- coding: utf-8 -*-
# ==============================================================================
#
#   DISSERTAÇÃO : O Impacto do Sentimento de Notícias Financeiras na Previsão
#                 de Direção e Volatilidade do Ativo PETR4
#   Autor       : Vanderlei Barbosa da Silva
#   Orientador  : Prof. Dr. Julio Cesar Nievola — PUCPR
#   Script      : 02 — Coleta de Notícias (Multi-Fonte)
#   Versão      : 3.0
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
#       Limitação        : Retorna apenas o título do artigo (sem resumo ou
#                          corpo do texto), o que limita a riqueza semântica
#                          do corpus para esta fonte especificamente.
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
#   │        Ataques, acidentes ou greves em infraestrutura crítica        │
#   │        geram choques imediatos de oferta com impacto direto no       │
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
#   │        anúncios de mudança de liderança geram retornos anormais      │
#   │        documentados na literatura de finanças corporativas.         │
#   │        Exemplo histórico: demissão do CEO José Mauro Coelho pela    │
#   │        gestão Lula (jun/2022) derrubou PETR4 mais de 10% em um dia. │
#   ├─────────────────────────────────────────────────────────────────────┤
#   │ CAT-7  Macroeconomia, Câmbio e Energia Alternativa                  │
#   │        Dólar, taxa de juros (Fed), recessão, PIB China, inflação,   │
#   │        energias renováveis, veículos elétricos, ESG.                │
#   │        O dólar e o petróleo têm correlação negativa histórica        │
#   │        documentada: quando o USD se fortalece, o petróleo cotado     │
#   │        em dólar tende a cair em termos relativos (Zhang et al.,     │
#   │        2008). A demanda da China responde por ~15% do consumo        │
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
#   DECISÃO 2 — Retry com Backoff Exponencial (biblioteca tenacity)
#   ─────────────────────────────────────────────────────────────────────────
#   PROBLEMA: APIs públicas gratuitas (GDELT, NewsAPI) têm limites de taxa
#   (rate limits) e instabilidade ocasional. A versão 1.0 simplesmente
#   abandonava a requisição em caso de falha (exceto TimeoutError), o que
#   significava perda silenciosa de dados sem qualquer notificação.
#
#   SOLUÇÃO ADOTADA: O decorator @retry da biblioteca tenacity implementa
#   o padrão "exponential backoff with jitter":
#     - Tentativa 1: imediata
#     - Tentativa 2: aguarda 4 segundos
#     - Tentativa 3: aguarda 8 segundos (dobra a cada tentativa, até 30s)
#   Após 3 tentativas sem sucesso, o erro é registrado no log e a requisição
#   é pulada (não derruba a execução completa).
#   Este padrão é o recomendado pelas próprias documentações do GDELT e
#   NewsAPI para uso em scripts de coleta de longa duração.
#
#   ─────────────────────────────────────────────────────────────────────────
#   DECISÃO 3 — Gravação Linha a Linha (sem acúmulo em DataFrame)
#   ─────────────────────────────────────────────────────────────────────────
#   PROBLEMA: A versão 1.0 acumulava todos os artigos em uma lista Python
#   durante toda a coleta e só no final criava um DataFrame e salvava o CSV.
#   Para 7 anos de dados com ~100 termos e 3 fontes, isso pode facilmente
#   consumir vários GB de RAM — excedendo o limite do Google Colab (12-15 GB)
#   e derrubando a sessão, perdendo todo o trabalho.
#
#   SOLUÇÃO ADOTADA: Cada artigo é gravado no CSV imediatamente após ser
#   coletado e validado (deduplicado), usando um csv.DictWriter com buffer
#   explícito. O arquivo é mantido aberto durante toda a coleta e descarregado
#   (flush) a cada 500 artigos. Isso mantém o consumo de memória em O(H),
#   onde H é apenas o conjunto de hashes (strings de 64 bytes cada):
#   para 1 milhão de artigos únicos, são ~64 MB — totalmente viável no Colab.
#
#   ─────────────────────────────────────────────────────────────────────────
#   DECISÃO 4 — Logging Estruturado em Arquivo
#   ─────────────────────────────────────────────────────────────────────────
#   PROBLEMA: A versão 1.0 usava apenas print() para exibir o progresso.
#   Isso significa que ao fechar o Colab, não há registro de quantas notícias
#   foram coletadas, quais erros ocorreram, ou em qual ponto a coleta parou.
#
#   SOLUÇÃO ADOTADA: A biblioteca logging do Python grava simultaneamente
#   no console (visível no Colab) e em um arquivo de log persistente no
#   Google Drive (coleta_noticias.log). Cada linha de log contém:
#     - Timestamp preciso (YYYY-MM-DD HH:MM:SS)
#     - Nível do evento (INFO, WARNING, ERROR)
#     - Mensagem descritiva
#   O arquivo de log é um registro auditável da coleta — pode ser citado na
#   dissertação como evidência de rastreabilidade e reprodutibilidade, e
#   apresentado na defesa se a banca questionar a integridade dos dados.
#
#   ─────────────────────────────────────────────────────────────────────────
#   DECISÃO 5 — Retomada Automática de Coleta Interrompida
#   ─────────────────────────────────────────────────────────────────────────
#   PROBLEMA: A coleta de 7 anos × ~100 termos × 3 fontes pode levar 6-12
#   horas. O Google Colab desconecta sessões inativas após ~90 minutos.
#   A versão 1.0 tinha checkpoints manuais por arquivo, mas sem mecanismo
#   de retomada automática — ao reiniciar, era necessário editar manualmente
#   o ponto de partida.
#
#   SOLUÇÃO ADOTADA: Ao iniciar, o script lê a coluna "hash_titulo" do CSV
#   já existente e carrega todos os hashes em um set em memória. Nas coletas
#   subsequentes, qualquer artigo já gravado é identificado pelo hash e
#   descartado instantaneamente (O(1)). Isso significa que rodar o script
#   novamente após uma interrupção simplesmente retoma de onde parou, sem
#   duplicar dados já gravados. O arquivo CSV é aberto em modo "append".
#
#   ─────────────────────────────────────────────────────────────────────────
#   DECISÃO 6 — Gerador Python (yield) em vez de listas
#   ─────────────────────────────────────────────────────────────────────────
#   PROBLEMA: Retornar listas de artigos de cada função significa construir
#   toda a lista em memória antes de processar qualquer item — ineficiente.
#
#   SOLUÇÃO ADOTADA: As funções de coleta (coletar_gdelt, coletar_newsapi,
#   coletar_rss) são implementadas como geradores Python (usam yield em vez
#   de return). Isso significa que cada artigo é processado e gravado
#   imediatamente após ser recebido da API, sem esperar que todos os artigos
#   do lote sejam coletados. Além da eficiência de memória, essa abordagem
#   torna o código mais modular e testável.
#
#   ─────────────────────────────────────────────────────────────────────────
#   DECISÃO 7 — Coleta Mensal por Janela (em vez de consulta única)
#   ─────────────────────────────────────────────────────────────────────────
#   PROBLEMA: Fazer uma única consulta para o período 2018-2025 retornaria
#   apenas os 250 artigos mais recentes (limite da API do GDELT), perdendo
#   anos de dados históricos.
#
#   SOLUÇÃO ADOTADA: O período é dividido em janelas mensais. Para cada mês,
#   uma consulta independente é feita com os parâmetros startdatetime e
#   enddatetime. Isso multiplica o número de consultas por ~84 (7 anos × 12
#   meses) mas garante cobertura temporal completa — cada mês pode ter até
#   250 artigos por termo, para cada um dos ~100 termos.
#
#
# ══════════════════════════════════════════════════════════════════════════════
# SEÇÃO 4 — JUSTIFICATIVA DAS FONTES RSS
# ══════════════════════════════════════════════════════════════════════════════
#
#   Os 25 feeds RSS foram selecionados com base em dois critérios:
#   (1) relevância temática para o mercado de petróleo e ações brasileiras
#   (2) credibilidade editorial reconhecida
#
#   VEÍCULOS NACIONAIS (14 feeds)
#   ───────────────────────────────
#   G1 Economia e G1 Mercados (Globo)
#     Maior grupo de comunicação do Brasil; cobertura ampla de política
#     econômica, câmbio e decisões governamentais que afetam a Petrobras.
#
#   InfoMoney
#     Portal especializado em finanças pessoais e mercado de capitais.
#     Cobertura detalhada do PETR4, análises de analistas, recomendações.
#
#   Valor Econômico
#     Jornal de referência do mercado financeiro brasileiro. Leitura
#     obrigatória de gestores de fundos e analistas de sell-side.
#
#   Exame (seção Invest)
#     Cobertura de negócios e mercado financeiro, com foco em empresas
#     listadas na B3.
#
#   UOL Economia
#     Portal de grande alcance; captura notícias de economia para
#     público amplo, incluindo repercussão de decisões da Petrobras.
#
#   Folha de São Paulo (Mercado)
#     Jornal de referência nacional; seção Mercado cobre câmbio, bolsa
#     e macroeconomia com profundidade.
#
#   Estadão Economia e E-Investidor (Estadão)
#     Cobertura econômica do Grupo Estado, incluindo análises de
#     profissionais do mercado financeiro.
#
#   CNN Brasil Negócios
#     Cobertura em tempo real de mercados, com foco em breaking news
#     que movimentam o Ibovespa.
#
#   Agência Brasil (EBC)
#     Agência estatal de notícias; cobre decisões do governo federal
#     relacionadas à política energética e à Petrobras.
#
#   Band News Economia
#     Cobertura econômica em rádio e web; captura notícias de impacto
#     imediato sobre preços de combustíveis e câmbio.
#
#   Poder360
#     Portal especializado em política e poder; cobre a interface entre
#     governo federal e gestão da Petrobras.
#
#   Money Times
#     Portal focado em investimentos e mercado financeiro; cobertura
#     de resultados e recomendações de analistas para PETR4.
#
#   VEÍCULOS INTERNACIONAIS (11 feeds)
#   ─────────────────────────────────────
#   Reuters Business e Reuters Energy
#     Maior agência de notícias financeiras do mundo. Cobertura em
#     tempo real de OPEP, preço do Brent/WTI e geopolítica do petróleo.
#     Referência primária para qualquer evento que mova o mercado de
#     commodities globalmente.
#
#   BBC Business
#     Cobertura de negócios internacionais com alcance global; captura
#     eventos geopolíticos que afetam o mercado de energia.
#
#   MarketWatch
#     Portal financeiro do Grupo Dow Jones; cobertura de commodities,
#     petróleo e mercados futuros com dados em tempo real.
#
#   OilPrice.com
#     Portal especializado exclusivamente no mercado de petróleo e gás.
#     Cobre OPEP, shale oil, fracking, infraestrutura e geopolítica
#     do petróleo com profundidade que veículos generalistas não oferecem.
#     Considerado uma das referências mais completas do setor.
#
#   Rigzone
#     Plataforma especializada no setor de upstream de petróleo e gás
#     (exploração e produção). Cobre plataformas offshore, licitações
#     de campos e contratos de exploração — relevante para o pré-sal.
#
#   CNBC Energy
#     Canal de negócios americano; cobertura de energia com foco em
#     impacto nos mercados financeiros norte-americanos e globais.
#
#   Financial Times Energy
#     Jornal financeiro britânico de referência global; cobertura de
#     transição energética, ESG e mercado de commodities com análise
#     aprofundada de longo prazo.
#
#   Investing.com (Oil e Commodities)
#     Portal de dados financeiros com cobertura de futuros de petróleo,
#     relatórios EIA de estoques e calendário econômico de eventos que
#     movimentam o mercado de commodities.
#
#   Bloomberg Energy
#     Agência de notícias financeiras líder mundial; cobertura premium
#     de mercados de energia, fusões e aquisições no setor de petróleo.
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
#   │                  │ neste corpus. Mantido para permitir extensão       │
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
#   │                  │ resumo não está disponível, este campo repete      │
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
#     das três fontes, deduplicas, com data, categoria e origem identificadas.
#
#   coleta_noticias.log
#     Registro auditável completo da execução: timestamps de início/fim,
#     contagem por fonte, erros de rede, quantidade de duplicatas removidas.
#
#   TEMPO ESTIMADO DE EXECUÇÃO
#   ───────────────────────────
#   A estimativa depende da velocidade de rede e da carga das APIs no momento:
#
#   GDELT   : ~100 termos × 84 meses × 2s de pausa = ~4,7 horas
#   NewsAPI : ~50 termos × 84 meses × 2s de pausa  = ~2,3 horas
#   RSS     : 25 feeds × ~1s cada = ~1 minuto
#   ─────────────────────────────────────────────────────────────
#   Total estimado: 7 a 10 horas de execução contínua
#
#   ESTRATÉGIA RECOMENDADA PARA O COLAB
#   ─────────────────────────────────────
#   O Google Colab desconecta sessões inativas. Para uma coleta de 7-10 horas,
#   recomenda-se:
#   1. Usar o Colab Pro (ou manter interação periódica com a sessão)
#   2. Rodar em partes: primeiro GDELT, salvar; depois NewsAPI, salvar; etc.
#   3. Confiar no mecanismo de retomada automática: ao reiniciar, o script
#      continua de onde parou sem reprocessar dados já gravados.
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
#DATA_INICIO = datetime(2018, 1, 1)
#DATA_FIM    = datetime(2025, 12, 31)
DATA_INICIO = datetime(2024, 1, 1)
DATA_FIM    = datetime(2024, 1, 31)

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
MAX_ARTIGOS_GDELT = 250   # Limite máximo da API gratuita do GDELT por consulta
PAUSA_REQ_S       = 2     # Pausa de cortesia entre chamadas (segundos)
                          # Reduzir abaixo de 1s pode resultar em bloqueio da API
TIMEOUT_REQ_S     = 30    # Timeout máximo por requisição HTTP (segundos)

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

# ── Listas planas derivadas da taxonomia ─────────────────────────────────────
# GDELT recebe todos os termos de todas as categorias.
# NewsAPI recebe um subconjunto (CAT1, CAT2, CAT3, CAT6) para economizar
# cota diária da API — estas são as categorias de maior impacto direto.
# A categoria de origem é preservada como metadado em cada artigo coletado.

TERMOS_GDELT: list[tuple[str, str]] = [
    (cat, termo)
    for cat, lista in TERMOS_POR_CATEGORIA.items()
    for termo in lista
]

CATS_NEWSAPI = {"CAT1_Empresa", "CAT2_Mercado_Petroleo",
                "CAT3_Geopolitica", "CAT6_Governanca"}
TERMOS_NEWSAPI: list[tuple[str, str]] = [
    (cat, termo)
    for cat, lista in TERMOS_POR_CATEGORIA.items()
    if cat in CATS_NEWSAPI
    for termo in lista
]

# ── Termos para filtro local nos RSS Feeds ────────────────────────────────────
# RSS retorna o feed completo do veículo (todas as notícias, não só petróleo).
# Este conjunto de termos filtra localmente apenas artigos relevantes.
# São termos curtos e de alta precisão para minimizar falsos positivos.
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
print(f"   Termos para GDELT   : {len(TERMOS_GDELT)}")
print(f"   Termos para NewsAPI : {len(TERMOS_NEWSAPI)}")
print(f"   Categorias          : {list(TERMOS_POR_CATEGORIA.keys())}")


# ==============================================================================
# BLOCO 5 — RSS FEEDS (14 NACIONAIS + 11 INTERNACIONAIS)
# ==============================================================================
#
# Ver Seção 4 do cabeçalho para justificativa detalhada de cada veículo.
#
# NOTA TÉCNICA: RSS feeds não suportam filtro por período ou palavra-chave
# na requisição. O download sempre traz o feed completo (todas as notícias
# recentes do veículo). O filtro por relevância é feito localmente pelo
# script após o download, usando TERMOS_FILTRO_RSS.
# Para dados históricos (2018-2025), use GDELT e NewsAPI.
# RSS complementa com cobertura recente de alta qualidade editorial.

RSS_FEEDS: dict[str, str] = {

    # ── Nacionais — cobertura do mercado financeiro e político brasileiro ─────
    "G1_Economia"        : "https://g1.globo.com/rss/g1/economia/",
    "G1_Mercado"         : "https://g1.globo.com/rss/g1/economia/mercados/",
    "InfoMoney"          : "https://www.infomoney.com.br/feed/",
    "Valor_Economico"    : "https://valor.globo.com/rss/home/",
    "Exame_Invest"       : "https://exame.com/feed/",
    "UOL_Economia"       : "https://rss.uol.com.br/feed/economia.xml",
    "Folha_Mercado"      : "https://feeds.folha.uol.com.br/mercado/rss091.xml",
    "Estadao_Economia"   : "https://www.estadao.com.br/rss/economia.xml",
    "CNN_Brasil_Negocios": "https://www.cnnbrasil.com.br/feed/",
    "Agencia_Brasil"     : "https://agenciabrasil.ebc.com.br/rss/economia/feed.rss",
    "Band_News_Econ"     : "https://www.band.uol.com.br/rss/economia",
    "Poder360_Econ"      : "https://www.poder360.com.br/feed/",
    "Money_Times"        : "https://www.moneytimes.com.br/feed/",
    "E_Investidor"       : "https://einvestidor.estadao.com.br/feed/",

    # ── Internacionais — cobertura global de energia e commodities ────────────
    "Reuters_Business"   : "https://feeds.reuters.com/reuters/businessNews",
    "Reuters_Energy"     : "https://feeds.reuters.com/reuters/energy",
    "BBC_Business"       : "https://feeds.bbci.co.uk/news/business/rss.xml",
    "MarketWatch"        : "https://feeds.marketwatch.com/marketwatch/topstories/",
    "OilPrice_News"      : "https://oilprice.com/rss/main",
    "Rigzone"            : "https://www.rigzone.com/news/rss/rigzone_latest.aspx",
    "CNBC_Energy"        : "https://www.cnbc.com/id/10000664/device/rss/rss.html",
    "FT_Energy"          : "https://www.ft.com/energy?format=rss",
    "Investing_Oil"      : "https://www.investing.com/rss/news_14.rss",
    "Investing_Commod"   : "https://www.investing.com/rss/news_11.rss",
    "Bloomberg_Energy"   : "https://feeds.bloomberg.com/energy/news.rss",
}

print(f"✅ {len(RSS_FEEDS)} RSS feeds configurados.")


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
log.info("=== INÍCIO DA COLETA — VERSÃO 3.0 ===")


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

@retry(
    stop=stop_after_attempt(3),           # máximo 3 tentativas
    wait=wait_exponential(multiplier=1, min=4, max=30),  # 4s → 8s → 16s
    retry=retry_if_exception_type(requests.RequestException),
    reraise=True,   # propaga o erro após esgotar as tentativas
)
def _requisicao_gdelt(params: dict) -> dict:
    """
    Executa uma chamada HTTP à API do GDELT com retry automático.
    O decorator @retry (tenacity) implementa backoff exponencial:
    falha → espera 4s → tenta → espera 8s → tenta → espera 16s → desiste.
    """
    r = requests.get(
        "https://api.gdeltproject.org/api/v2/doc/doc",
        params=params,
        timeout=TIMEOUT_REQ_S,
    )
    r.raise_for_status()   # lança exceção para códigos HTTP 4xx/5xx
    return r.json()


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
                    dados   = _requisicao_gdelt(params)
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

                time.sleep(PAUSA_REQ_S)

            cursor = cursor + relativedelta(months=1)
            pbar.update(1)


# ==============================================================================
# BLOCO 9 — COLETOR NEWSAPI
# ==============================================================================
# Ver Seção 1 (Mecanismo 2) e Seção 3 (Decisões 2, 6, 7) do cabeçalho.

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=30),
    retry=retry_if_exception_type(requests.RequestException),
    reraise=True,
)
def _requisicao_newsapi(params: dict, headers: dict) -> dict:
    """Chamada HTTP à NewsAPI com retry automático (mesma lógica do GDELT)."""
    r = requests.get(
        "https://newsapi.org/v2/everything",
        params=params,
        headers=headers,
        timeout=TIMEOUT_REQ_S,
    )
    r.raise_for_status()
    return r.json()


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
                        time.sleep(PAUSA_REQ_S)

                    except Exception as exc:
                        log.warning("NewsAPI | %s | pág %d | %s", termo, pagina, exc)
                        break

                time.sleep(PAUSA_REQ_S)

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
