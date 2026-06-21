# PETR4 — Sentimento de Notícias na Previsão de Direção e Volatilidade

> **Dissertação de Mestrado** — O Impacto do Sentimento de Notícias Financeiras na Previsão de Direção e Volatilidade do Ativo PETR4
> **Autor:** Vanderlei Barbosa da Silva · **Orientador:** Prof. Dr. Julio Cesar Nievola
> **Instituição:** PUCPR — Mestrado em Informática · **Período analisado:** 2018–2025

---

## 📌 Visão Geral

Este repositório contém o pipeline computacional completo da dissertação. O objetivo é testar se o **sentimento extraído de notícias financeiras** (via NLP) melhora a previsão da **direção** (alta/baixa) e da **volatilidade** do ativo **PETR4**, quando combinado (*Data Fusion*) com modelos econométricos (GARCH) e de *machine learning* (SVM e XGBoost).

O fluxo é organizado em **4 scripts sequenciais**. Cada script consome a saída do anterior — **execute sempre na ordem**:

```
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│ Script 01│ → │ Script 02│ → │ Script 03│ → │ Script 04│
│ Financeiro│   │ Notícias │   │Sentimento│   │  GARCH + │
│  (yfinance)│   │ (GDELT…) │   │BERTimbau │   │ SVM/XGB  │
└──────────┘   └──────────┘   └──────────┘   └──────────┘
```

A maioria dos scripts foi escrita para rodar no **Google Colab** (montam o Google Drive em `/content/drive/MyDrive/Mestrado_PETR4/`). O script de coleta multi-fonte ([02_coleta_noticias_petr4.py](obsoleto/02_coleta_noticias_petr4.py)) detecta automaticamente se está no Colab ou em ambiente local.

---

## 🗂️ Estrutura do Repositório

```
.
├── src/
│   ├── coleta/        01 (financeiro), 02b (WordPress), 02c (base + split)
│   ├── sentimento/    03 (BERTimbau/XLM-R + ISM)
│   ├── modelagem/     04 (GARCH + SVM/XGBoost + ablação)
│   └── comum/         abnt_docx.py (formatação ABNT reutilizável)
├── docs/
│   ├── geradores/     gerar_documentacao_dissertacao.py
│   ├── saida/         *.docx gerados (gitignored)
│   ├── DOCUMENTACAO_BASES.md, GUIA_DE_EXECUCAO.md
├── obsoleto/          versões antigas desativadas (GDELT, NewsAPI, RSS)
├── Mestrado_PETR4/    dados — saídas de cada script (gitignored)
├── Referencial_Teorico/   29 PDFs do referencial (gitignored)
├── Exame_qualificacao/    materiais da banca (gitignored)
└── README.md
```

| Script | Papel |
|--------|-------|
| [src/coleta/01_coleta_dados_financeiros_petr4.py](src/coleta/01_coleta_dados_financeiros_petr4.py) | **Script 01** — preços da PETR4 (yfinance) e Log-Retorno |
| [src/coleta/02b_coleta_noticias_wordpress_petr4.py](src/coleta/02b_coleta_noticias_wordpress_petr4.py) | ⭐ **Script 02b** — coleta via WordPress REST API (5 portais), com **hora exata** e **taxonomia de 7 categorias** |
| [src/coleta/02c_preparar_base_treino_teste_validacao.py](src/coleta/02c_preparar_base_treino_teste_validacao.py) | **Script 02c** — base **tratada** (filtragem leve) + **split treino/validação/teste (60/15/25)**; base bruta intacta |
| [src/sentimento/03_analise_sentimento_bertimbau_petr4.py](src/sentimento/03_analise_sentimento_bertimbau_petr4.py) | **Script 03** — análise de sentimento (NLP) e Índice de Sentimento da Mídia (ISM) |
| [src/modelagem/04_modelagem_garch_svm_xgboost_petr4.py](src/modelagem/04_modelagem_garch_svm_xgboost_petr4.py) | **Script 04** — testes estatísticos, GARCH(1,1), Data Fusion, modelos e ablação |
| [src/comum/abnt_docx.py](src/comum/abnt_docx.py) | Módulo reutilizável de formatação **ABNT** (NBR 14724/6023/6024/10520) |
| [src/comum/taxonomia.py](src/comum/taxonomia.py) | Fonte **única** dos 152 termos (7 categorias) e dos critérios de filtragem — garante completude nas tabelas dos documentos |
| [docs/geradores/](docs/geradores/) | Geradores dos documentos Word **ABNT**, um por etapa: Etapa 1 (engenharia de dados), Etapa 2 (financeira), Etapa 3 (sentimento), Etapa 4 (modelagem). Saída em `docs/saida/` |
| [docs/DOCUMENTACAO_BASES.md](docs/DOCUMENTACAO_BASES.md) · [docs/GUIA_DE_EXECUCAO.md](docs/GUIA_DE_EXECUCAO.md) | Documentação das bases e guia de execução (Colab) |
| [obsoleto/](obsoleto/) | Coletores antigos **desativados** (GDELT, multi-fonte, RSS) — ver [obsoleto/LEIA-ME.md](obsoleto/LEIA-ME.md) |

---

## 🔧 Pré-requisitos (execução LOCAL)

Todo o pipeline roda **localmente** (sem Colab). Recomenda-se um **ambiente conda dedicado** — o PyTorch (Script 03) instala de forma confiável via conda, evitando o erro `WinError 1114` do build do PyPI no Windows/Anaconda.

```bash
# 1) Criar o ambiente com Python + PyTorch (CPU) via conda
conda create -n petr4 -y -c pytorch -c conda-forge python=3.11 pytorch cpuonly

# 2) Instalar as demais dependências no ambiente
conda run -n petr4 pip install -r requirements.txt
#   (transformers fica em 4.x para carregar pesos .bin com torch CPU 2.5)

# 3) Rodar qualquer script com o Python do ambiente
conda run -n petr4 python src/coleta/01_coleta_dados_financeiros_petr4.py
```

**Redes com proxy/SSL (corporativo):** a interceptação de SSL exige ajustes já embutidos:
- `pip` → adicionar `--trusted-host pypi.org --trusted-host files.pythonhosted.org`;
- `conda` → `conda config --set ssl_verify false`;
- **Script 01** (Yahoo) → flag `VERIFY_SSL = False` (sessão própria + retry de rate limit);
- **Script 03** (Hugging Face) → flag `VERIFY_SSL_HF = False` (desabilita verificação no download do modelo).

> 💡 Em CPU, o Script 03 sobre as 205 mil notícias leva **horas**. Use a variável de ambiente `LIMITE_NOTICIAS=300` para um teste rápido (valida o pipeline ponta a ponta).

---

## ▶️ Como Executar (resumo)

> Detalhes completos, prints esperados e tabela de erros comuns estão em **[GUIA_DE_EXECUCAO.md](docs/GUIA_DE_EXECUCAO.md)**.

### Script 01 — Coleta Financeira `(~3 min)`
Baixa a série diária da PETR4 (B3) via **yfinance** e calcula o Log-Retorno `Rt = ln(Pt / Pt-1)`.
**Gera:** `base_financeira_petr4.csv`

### Script 02 — Coleta de Notícias `(simples: ~25–45 min · multi-fonte: 10–12 h)`
Coleta notícias sobre Petrobras/PETR4 (2018–2025). Duas opções:
- **Simples** ([02_coleta_noticias_gdelt_petr4.py](obsoleto/02_coleta_noticias_gdelt_petr4.py)): apenas GDELT, janelas mensais, ideal para Colab.
- **Multi-fonte v3.1** ([02_coleta_noticias_petr4.py](obsoleto/02_coleta_noticias_petr4.py)): GDELT + NewsAPI + 25 RSS feeds, com taxonomia de 7 categorias temáticas, deduplicação por hash SHA-256, gravação linha a linha, logging auditável (`coleta_noticias.log`) e **retomada automática** (basta rodar de novo).

> ℹ️ **NewsAPI desativada por padrão** (`USAR_NEWSAPI = False`). O plano gratuito só cobre os **últimos ~30 dias** (confirmado em teste: requisições a datas de 2018 retornam HTTP 426). Como todo o recorte da pesquisa (2018–2025) é mais antigo que isso, a NewsAPI gratuita não acrescenta notícias ao corpus — a cobertura histórica vem do GDELT e dos RSS. Para reativar com um plano que tenha histórico estendido, troque a flag para `True` (instruções no Bloco 3 do script).

> ⚠️ **Atenção ao GDELT:** a API pública bloqueia o IP por volume de requisições (HTTP 429 persistente). Antes de coletas longas, valide o IP abrindo no navegador:
> `https://api.gdeltproject.org/api/v2/doc/doc?query=%22Petrobras%22&mode=artlist&format=json`
> Se retornar 429, aguarde 2–4 h. Rode antes [teste_rss_feeds.py](obsoleto/teste_rss_feeds.py) para conferir os feeds.

**Gera:** `base_textual_petr4_2018_2025.csv`

### ⭐ Script 02b — Coleta via WordPress REST API `(recomendado)`
Fonte **recomendada** desde jun/2026, após a banca (Prof. Emerson) exigir **hora exata de publicação** (timestamp) para validar a causalidade Lead-Lag com o GARCH(1,1) — exigência que a antiga lib `GoogleNews` não atendia (mascarava a hora). Os grandes portais financeiros brasileiros rodam em WordPress e expõem a API REST pública `/wp-json/wp/v2/posts`, que devolve JSON com título, resumo, link e o campo `date` **no horário de Brasília** (+ `date_gmt` em UTC).
- **5 portais**: InfoMoney, Exame, Money Times, Petronotícias, Poder360.
- **Taxonomia de 7 categorias / 152 termos** (idêntica à do Script 02) — cada notícia gravada com sua `categoria`, habilitando a **análise de ablação** no Script 04.
- **Coleta híbrida**: termos raros via paginação full-range; termos de alto volume via janela mensal (evita o teto de offset da API).
- Gratuito, sem Selenium, sem bloqueio anti-bot, com deduplicação por hash e retomada automática.
- Metodologicamente alinhado à rota Cardoso & Nakane (2024) — coleta direta do portal com timestamp.

**Gera:** `base_textual_petr4_wordpress_2018_2025.csv` (consumido automaticamente pelo Script 03).

### Script 02c — Preparação: Base Tratada + Split Treino/Validação/Teste
A partir da base bruta (que **permanece intacta**, jamais recoletada), gera as bases derivadas para a modelagem:
- **Base tratada** (`base_textual_petr4_tratada.csv`): **filtragem leve** (limpeza de qualidade) — remove apenas notícias degeneradas (título vazio, com menos de 15 caracteres ou marcadores de remoção). **Não** há filtro temático, então **todas as 7 categorias são preservadas** (mantém a base adequada para a ablação). Na prática, retém ~100% do corpus (só ~19 linhas removidas).
- **Split temporal 60/15/25** treino/validação/teste, **estratificado por ano** (todos os anos nos três conjuntos) e **cronológico dentro do ano** (sem embaralhar → sem *data leakage*), por **dias inteiros** (um dia nunca é dividido). Grava a coluna `conjunto` e o mapa `definicao_split_temporal.csv` (Data → conjunto) para uso consistente no Script 04.
- **Documentação** completa das bases (original + tratada + split) em **[DOCUMENTACAO_BASES.md](docs/DOCUMENTACAO_BASES.md)**, gerada automaticamente com os números reais.

### Script 03 — Análise de Sentimento `(GPU: ~15–30 min · CPU: 2–4 h)`
Classifica cada notícia em Positivo/Neutro/Negativo usando o modelo multilíngue `cardiffnlp/twitter-xlm-roberta-base-sentiment` (referido como "BERTimbau" na dissertação). Calcula o **Índice de Sentimento da Mídia (ISM)** — média diária de `polaridade × confiança` — com **alinhamento temporal**: notícias publicadas após o fechamento da B3 (17h) são atribuídas ao próximo pregão, evitando *data leakage*. Detecta o schema do corpus automaticamente (02b ou GDELT) e, quando há coluna `categoria`, gera também um **ISM por categoria** para a análise de ablação.
**Gera:** `indice_sentimento_petr4.csv`, `noticias_com_sentimento.csv` e (se houver categorias) `indice_sentimento_categorias_petr4.csv`

### Script 04 — Modelagem `(~10–20 min)`
Núcleo da dissertação:
1. **Testes estatísticos** — Jarque-Bera (normalidade), ADF (estacionariedade), ARCH-LM (heterocedasticidade).
2. **GARCH(1,1)** com distribuição t-Student → volatilidade condicional.
3. **Data Fusion** — combina `Retorno(t-1)` + `Volatilidade GARCH(t-1)` + `Sentimento ISM(t-1)`.
4. **4 modelos** — SVM e XGBoost, *com* e *sem* sentimento (baseline).
5. **Split treino/validação/teste 60/15/25** cronológico (sem *data leakage*): treino ajusta, validação seleciona hiperparâmetros, teste é avaliado uma única vez. Protocolo configurável (`PROTOCOLO_SPLIT`): `cronologico` (padrão) ou `estratificado` (lê `definicao_split_temporal.csv`).
6. **Análise de ablação por categoria** *(quando há ISM por categoria do Script 02b/03)* — treina o modelo completo com as 7 categorias e remove uma por vez, medindo a queda de acurácia. A maior queda indica a categoria de notícia mais informativa para prever a direção do PETR4.

**Gera:** `resultados_modelos_petr4.csv` (Tabela 4.3), `base_master_petr4.csv`, `grafico_volatilidade_garch.png`, `grafico_dispersao_sentimento_volatilidade.png`, `relatorio_testes_estatisticos.txt` e (se houver categorias) `resultados_ablacao_categorias_petr4.csv` + `grafico_ablacao_categorias.png`.

**Variável-alvo:** `1` se o Log-Retorno do dia *t+1* for positivo (alta), `0` caso contrário (baixa).

---

## 📊 Saídas e Onde São Usadas na Dissertação

| Arquivo gerado | Uso na dissertação |
|----------------|--------------------|
| `base_financeira_petr4.csv` | Base de preços + Log-Retorno (Script 01) |
| `base_textual_petr4_wordpress_2018_2025.csv` | Corpus de notícias com timestamp + categoria (Script 02b) |
| `indice_sentimento_petr4.csv` | ISM diário, entrada do Script 04 |
| `indice_sentimento_categorias_petr4.csv` | ISM por categoria — entrada da análise de ablação |
| `resultados_modelos_petr4.csv` | **Tabela 4.3** — desempenho dos classificadores |
| `resultados_ablacao_categorias_petr4.csv` | Tabela de ablação — categoria mais informativa |
| `grafico_volatilidade_garch.png` | **Figura 4.2** — volatilidade condicional |
| `grafico_dispersao_sentimento_volatilidade.png` | **Figura 4.4** — sentimento vs. volatilidade |
| `grafico_ablacao_categorias.png` | Figura da ablação — importância por categoria |
| `relatorio_testes_estatisticos.txt` | **Seção 4.3** — testes estatísticos |
| `base_master_petr4.csv` | Base consolidada para análises futuras |

---

## 📚 Notas Metodológicas

- **Por que Log-Retorno?** Garante aditividade temporal e aproxima a série da estacionariedade (requisito do GARCH e dos modelos de ML).
- **Por que GARCH(1,1)?** Justificado pelo teste ARCH-LM, que confirma heterocedasticidade condicional (volatilidade não constante / *volatility clusters*).
- **Por que abordagem multi-fonte de notícias?** Evitar o *viés de cobertura* de uma única fonte (Heston & Sinha, 2017). A taxonomia de 7 categorias (empresa, mercado de petróleo, geopolítica, infraestrutura, sanções/navegação, liderança/política, macroeconomia) ancora-se em Hamilton (1983), Kilian (2009), Caldara & Iacoviello (2022), entre outros — ver o cabeçalho de [02_coleta_noticias_petr4.py](obsoleto/02_coleta_noticias_petr4.py) para a documentação completa e as referências.
- **Por que a hora exata importa (timestamp)?** Sem o horário de publicação não é possível garantir o alinhamento Lead-Lag — uma notícia das 20h (mercado fechado) só pode impactar o pregão seguinte. Capturar o timestamp real (Script 02b) é o que torna válida a prova de causalidade com o GARCH(1,1). Rota metodológica análoga a Cardoso & Nakane (2024).
- **O que é a análise de ablação?** Remover uma categoria de notícia por vez e medir a queda de desempenho do modelo. A maior queda revela a categoria mais informativa para prever o PETR4 — uma contribuição científica adicional possibilitada pela taxonomia.
- **Como citar o GDELT:** Leetaru, K.; Schrodt, P. A. *GDELT: Global data on events, location, and tone, 1979–2012.* ISA Annual Convention, 2013.

---

## 🩹 Erros Comuns

| Erro | Causa | Solução |
|------|-------|---------|
| `FileNotFoundError` no Script 04 | Scripts anteriores não rodaram | Execute na ordem 01 → 02 → 03 → 04 |
| `0 notícias` / HTTP 429 no Script 02 | API GDELT sobrecarregada ou IP bloqueado | Aguarde 2–4 h; valide o IP no navegador |
| `CUDA out of memory` no Script 03 | GPU sem memória | Reduza `TAMANHO_LOTE` de 32 para 16 |
| Script 03 muito lento | GPU não ativada | Ative a GPU (T4) no Colab |
