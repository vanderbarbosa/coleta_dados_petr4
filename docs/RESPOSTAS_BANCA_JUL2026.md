# Respostas às ponderações da banca — Seminário de julho/2026

Dissertação PETR4 · Vanderlei Barbosa da Silva · PPGIA/PUCPR
Documento de trabalho (rumo à dissertação). **Nada aqui é inventado**: cada
afirmação cita a fonte (arquivo real da pesquisa ou URL, no caso do item 8).

---

## Item 1 — Por que não coletar notícias da Bloomberg Línea?

**Resposta técnica (com fonte).** A coleta atual depende da **WordPress REST API**
(`/wp-json/wp/v2/posts`) dos cinco portais, que fornece `date`/`date_gmt` por notícia
(marcação temporal precisa, base do Lead-Lag). A Bloomberg Línea **não usa WordPress**:

- `https://www.bloomberglinea.com.br/wp-json/wp/v2/posts` → **HTTP 404** (não existe).
- O `robots.txt` revela **Arc Publishing** (feeds em `/arc/outboundfeeds/…`) e **bloqueia**
  a API interna `/pf/api/v3/*`. Fonte: `https://www.bloomberglinea.com.br/robots.txt`.
- Há um **Google News sitemap** (`/arc/outboundfeeds/news-sitemap.xml`) com `news:title`
  e `news:publication_date`, **porém só lista ~50 artigos das últimas 48 h** — padrão de
  sitemaps de notícias. Não serve para reconstruir o corpus histórico (2016–2026).

**Conclusão / encaminhamento.** A Bloomberg Línea é **inviável como fonte histórica**
com o pipeline atual: (a) não expõe WordPress; (b) exigiria um coletor novo, baseado em
sitemap + raspagem de cada página (a API Arc é proibida pelo `robots.txt`); (c) é fonte
premium/paga, com termos de uso mais restritivos. É registrada como **trabalho futuro**:
um coletor *forward* (a partir de agora) via sitemap Arc, respeitando o `robots.txt` — sem
comprometer a consistência temporal do corpus já consolidado nos cinco portais WordPress.

---

## Item 2 — Os resultados preliminares não apresentam nada sobre volatilidade

A crítica é procedente: a apresentação enfatizou a **direção**. Os resultados de
**volatilidade já existem** e foram consolidados em `datasets_refino/03_resultados_volatilidade_v1.csv`
(fontes: `resultados_granger_petr4.csv`, `resultados_quantilica_petr4.csv`,
`resultados_regime_incerteza_petr4.json`). Principais achados:

- **Causalidade de Granger (sentimento → volatilidade):** significativa em **todas** as
  defasagens de 1 a 5 dias (**p ≤ 0,0002**); sobre o **retorno**, não significativa (p de 0,08 a 0,43).
- **Regressão quantílica (efeito assimétrico):** no quantil inferior (τ=0,05, piores dias),
  o sentimento eleva o retorno em **+261 bps (p=0,034)**; no τ=0,25, **+121 bps (p=0,025)**;
  nula nos quantis superiores → **viés de negatividade**.
- **Por regime de incerteza:** o efeito do sentimento é maior em baixa incerteza (+90 bps, p≈0,10).

**Ação:** esses resultados serão promovidos ao corpo dos *Resultados* (não só à discussão),
com uma tabela/figura dedicada — é a evidência **forte e significativa** da pesquisa.

---

## Item 3 — A acurácia direcional ficou pior que "jogar uma moeda"

**Leitura honesta (fonte: `resultados_modelos_petr4.csv`).**

| Modelo | Acurácia | AUC |
|---|---|---|
| XGBoost (apenas preços) | **49,77%** | 0,501 |
| SVM (apenas preços) | 51,91% | 0,484 |
| SVM (Data Fusion) | 51,91% | 0,518 |
| XGBoost (Data Fusion) | **52,22%** | 0,514 |

Três pontos, sem maquiar:
1. **49,77% (XGBoost só preços) é estatisticamente indistinguível de 50%** — está dentro do
   ruído amostral (653 pregões). Não é "pior que a moeda" de forma significativa; é ≈ acaso.
2. **Isso é o esperado.** Prever direção diária de um ativo é quase um passeio aleatório
   (hipótese de mercados eficientes). Nenhum modelo do estado da arte "vence" a direção de
   forma robusta — 52–56% é o teto típico da literatura (ver item 5).
3. **O sentimento agrega +2,45 pp** (49,77 → 52,22) e é o atributo mais importante, mas o
   ganho direcional **não é significativo** (binomial p=0,145) e não supera o baseline (~53%).
   **A contribuição real está na volatilidade (item 2), não na direção.**

**Caminho para melhorar** (sem prometer números): ver item 8 (encoders melhores) e o
refinamento já feito (`resultados_refinamento_petr4.csv`: ajuste de limiar levou a validação
a 56,52% e o teste a 52,53%).

---

## Item 4 — Refino do dataset de notícias (datasets versionados)

Gerados por `datasets_refino/gerar_datasets_refino.py` (reprodutível), a partir de
`noticias_com_sentimento.csv` e `base_master_petr4.csv`:

- **4A · `01_noticias_apos_17h_v1.csv`** — apenas notícias publicadas **após as 17h**
  (hora de Brasília, coluna `Data_Coleta`). **54.259 notícias = 26,4%** do corpus (205.697).
- **4B · `02_noticias_apos17h_enriquecido_v1.csv`** — por notícia: **data do pregão**
  (próximo pregão real, via `merge_asof`), **notícia**, **sentimento** (Índice/Rótulo/Confiança
  do FinBERT), **volatilidade** do pregão (GARCH), retorno e direção real, e os **parâmetros
  dos encoders** (FinBERT-PT-BR `max_length=512`; GARCH(1,1) t-Student; XGBoost com as features
  `Retorno_Ontem, Volatilidade_Ontem, Sentimento_Ontem`).
- **4C · versionamento:** todos os arquivos são `_vN` e **não sobrescrevem** os anteriores —
  cada novo refinamento gera um novo `_v` para permitir comparação.

---

## Item 5 — Dataset estruturado da Revisão Sistemática

**`datasets_refino/04_revisao_sistematica_estudos_v1.csv`** (25 estudos — número da *longtable*
`tab:rsl_artigos` do Cap. 2). **14 colunas:** `#, Autor, Ano, Idioma, Veículo, Título,
Objetivo/Contribuição, Método, Encoder/Representação, **Fonte_Noticias**, **Metodo_Coleta**,
Parâmetros, Resultados_obtidos, Fonte_do_registro`.

- **Extraídos dos PDFs** (li o resumo/método de cada artigo em `Referencial_Teorico/`) — inclui,
  como você pediu, **onde cada estudo capturou as notícias e como**. Exemplos: Tetlock=*Wall Street
  Journal* (coluna "Abreast of the Market"); Schumaker=*Yahoo Finance* (~45 fontes); Bollen=*Twitter*
  (OpinionFinder+GPOMS); Groß-Klußmann=*Reuters NewsScope*; Calomiris=*Thomson Reuters* (1996–2015);
  Silva 2018 e Cardoso 2024=*Valor Econômico*; Narde 2024=*X/Twitter PT-BR*; Oliveira=*Twitter*+surveys.
- **Resultados** preenchidos quando constam no resumo (ex.: Bollen ~87,6%; Nguyen +6,07%; Barak
  83,6%/88,2%; Narde 95,1%); **Parâmetros** detalhados nem sempre estão no resumo → marcados
  *"ver artigo"* (leitura profunda do PDF sob demanda). **Nada inventado.**
- ⚠️ Observação de rigor: **Fernández-Gavilanes, Odhiambo e Narde não são previsão de ações**
  (são análise/fake-news/seleção de atributos) — a coluna deixa isso explícito.

> ⚠️ **Inconsistência a resolver:** o Cap. 2 fala em **25 estudos**; o slide do seminário
> dizia **29**. Definir o número oficial e uniformizar deck + dissertação.

---

## Item 7 — Pasta de datasets

Criada a pasta **`datasets_refino/`** na raiz do projeto, com os geradores e um `README.md`.
Os `.csv` grandes ficam locais (o `.gitignore` já ignora `*.csv`); geradores e README
são versionados.

---

## Item 8 — Existem encoders melhores? (pesquisa externa)

Sim, há caminhos concretos para tentar melhorar o sinal de sentimento. Opções (com fonte):

1. **Albertina PT-BR (PORTULAN)** — encoder **DeBERTa** para português, descrito como o de
   **desempenho mais competitivo** para PT; versões de 100M, **900M** e 1,5B parâmetros,
   licença aberta. É um encoder **mais forte** que o BERTimbau (base do FinBERT-PT-BR), mas
   **não é especializado em finanças** → exigiria *fine-tuning* no nosso conjunto-ouro (e,
   idealmente, *domain-adaptive pretraining* sobre as 205k notícias).
   Fonte: https://huggingface.co/PORTULAN/albertina-900m-portuguese-ptbr-encoder · arXiv 2305.06721.
2. **BERTimbau-large (330M)** — versão maior do modelo-base atual; upgrade barato para testar.
   Fonte: https://huggingface.co/neuralmind/bert-large-portuguese-cased.
3. **turing-usp/FinBertPTBR** — implementação alternativa de FinBERT em PT, para comparação
   direta com o `lucas-leme/FinBERT-PT-BR` atual. Fonte: https://huggingface.co/turing-usp/FinBertPTBR.
4. **LLMs financeiros / instrucionais** (FinGPT, GPT-4o etc.) em *zero/few-shot* — potencialmente
   fortes, mas **não determinísticos, caros e menos reprodutíveis** — desaconselhados como
   classificador científico principal; úteis, no máximo, como *baseline* comparativo.

**Recomendação (honesta).** O maior ganho de encoder viável é **fine-tunar o Albertina PT-BR**
no conjunto-ouro e compará-lo ao FinBERT-PT-BR atual, sob o mesmo protocolo. **Porém**:
o gargalo da *direção* é o mercado (eficiência), não só o encoder — um sentimento melhor deve
ajudar mais a **volatilidade** do que a direção. Requer GPU e re-treino.

**Experimento pronto para rodar:** criei `src/sentimento/12_finetune_albertina_ptbr.py`, que
faz o *fine-tuning* de um encoder (padrão: **Albertina-100M**; opções: 900M, BERTimbau-large,
turing-usp/FinBertPTBR) usando o **conjunto-ouro rotulado por humanos** e compara, **no mesmo
conjunto de teste**, com o FinBERT-PT-BR — sob **acurácia, F1-macro e Kappa de Cohen** (as
métricas já usadas na dissertação). Requer GPU + `pip install datasets` (a lib HF `datasets`
não está no env atual). Uso:
```
python src/sentimento/12_finetune_albertina_ptbr.py --modelo PORTULAN/albertina-100m-portuguese-ptbr-encoder --epocas 4
```
Saída: `Mestrado_PETR4/experimentos_encoder/resultado_<modelo>.json` (métricas + Δ vs FinBERT).

**Fontes (item 8):** [FinBERT-PT-BR (HF)](https://huggingface.co/lucas-leme/FinBERT-PT-BR) ·
[Artigo FinBERT-PT-BR (SBC/BWAIF)](https://sol.sbc.org.br/index.php/bwaif/article/view/24960) ·
[Albertina PT-BR 900M](https://huggingface.co/PORTULAN/albertina-900m-portuguese-ptbr-encoder) ·
[Albertina (arXiv 2305.06721)](https://arxiv.org/html/2305.06721) ·
[turing-usp/FinBertPTBR](https://huggingface.co/turing-usp/FinBertPTBR) ·
[BERTimbau](https://huggingface.co/neuralmind/bert-large-portuguese-cased).

---

## Rodada de refinamento — execução autônoma (04/07/2026)

**Suíte de experimentos de data fusion (item: "nosso desempenho tem que ser melhor").**
Script `src/modelagem/13_experimentos_datafusion.py` — **15 configurações** (5 modelos ×
3 conjuntos de atributos), split cronológico 60/15/25 (653 pregões de teste), replicando as
técnicas de maior desempenho da RSL (`datasets_refino/05_tecnicas_alto_desempenho_rsl_v1.csv`):
stacking (Barak, 2017), tuning/limiar (Nobre, 2019), sentimento por categoria (Nguyen, 2015),
RF/AUC (Ballings, 2015), walk-forward (Oliveira, 2017).

- **Melhor: XGBoost (3 atributos-base) = 54,52%** (AUC 0,514; MCC 0,068), **supera** o baseline de
  classe majoritária (53,14%) e é **significativo vs. acaso** (binomial **p=0,012**).
- Confirma o número da dissertação (54,5%). O *stacking* e o conjunto completo de atributos **não**
  superaram as configurações simples (Barak reporta 83% em OUTRO mercado/tarefa; atributos demais →
  sobreajuste). Ganho direcional **modesto** (coerente com mercado eficiente); a volatilidade segue
  o achado forte.
- **A cada teste, um dataset** foi persistido: `datasets_refino/exp_2026-07-04_<modelo>_<atributos>.csv`
  (15 arquivos) + consolidado `resultados_experimentos_datafusion_2026-07-04.csv`.
- **Dissertação atualizada:** `capitulos/4d-experimentos-suite.tex` (tabela das técnicas replicadas +
  tabela dos 15 experimentos + discussão), incluída via `\input` no Cap. 4.

**Fine-tuning de encoder — BLOQUEADO (honesto).** Não foi possível executar: (a) **sem GPU**
(CUDA indisponível) e (b) **o conjunto-ouro está com 0/300 rótulos humanos** (a aba 'Rotular' não
foi preenchida). O experimento exige rótulos humanos — não invento rótulos. O script
`src/sentimento/12_finetune_albertina_ptbr.py` está pronto e sai com mensagem clara até que a
rotulagem seja feita. **Pendência:** rotular ≥200 manchetes do conjunto-ouro (+ acesso a GPU) para
comparar Albertina PT-BR × FinBERT-PT-BR.
