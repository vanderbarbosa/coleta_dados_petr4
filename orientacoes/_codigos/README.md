# Códigos — originais de terceiros e reconstruções

Cada arquivo declara no cabeçalho se é **código original de terceiro** ou **reconstrução**.
Nenhuma reconstrução é apresentada como se fosse dos autores originais.

---

## Reconstruções (código próprio, a partir da descrição publicada)

| Arquivo | Reconstrói | Gap | Consome rótulo? | Onde rodar |
|---|---|---|---|---|
| [`reconstrucao_santos_etapa1_mlm.py`](reconstrucao_santos_etapa1_mlm.py) | Santos (2023), Etapa 1 — adaptação de domínio por MLM | **G3** | ❌ **Não** | Colab GPU |
| [`reconstrucao_santos_etapa2_sentimento.py`](reconstrucao_santos_etapa2_sentimento.py) | Santos (2023), Etapa 2 — *gradual unfreezing* | G3 | ⚠️ Sim | Colab GPU |
| [`reconstrucao_santos_bootstrap.py`](reconstrucao_santos_bootstrap.py) | Santos (2022), Seção 4.2.4 — *bootstrap* + IC + teste Z | **G12** | ❌ Não | Local (CPU) |
| [`comite_sentimento_petr4.py`](comite_sentimento_petr4.py) | Błoch et al. (2026) — máquina de comitê | **G7** | ❌ Não | Local/Colab |
| [`llm_vs_encoder_conjunto_ouro.py`](llm_vs_encoder_conjunto_ouro.py) | Teles e Figueiredo (2025), replicado em PT-BR | **G6** | ❌ Não | Local (API) |
| [`avaliacao_temporal_drift.py`](avaliacao_temporal_drift.py) | Imai et al. (2024) — diagnóstico de *concept drift* | **G4** | Parcial | Local/Colab |

> **Nenhum dos seis exige rotulagem nova.** Todos usam o conjunto-ouro de 300 manchetes que já
> existe, ou dispensam gabarito por completo (MLM e perplexidade). São compatíveis com a
> suspensão da rotulagem determinada na mentoria de 29/07/2026.

---

## Código original de terceiro

| Arquivo | Origem | Licença |
|---|---|---|
| `prio3_README.md` | [jp-alves/prio3-sentiment](https://github.com/jp-alves/prio3-sentiment) | ver `LICENSE` no repositório |
| `prio3_environment.yaml` | idem | idem |
| `prio3_src_collect_scrap_news.py` | idem — coleta GNews mês a mês | idem |
| `prio3_src_clean_clean_news.py` | idem — limpeza, filtro, dedup por hash MD5 | idem |
| `prio3_src_nlp_sentiment.py` | idem — FinBERT-PT-BR + fallback VADER | idem |
| `prio3_src_nlp_apply_sentiment.py` | idem — aplicação em lote | idem |
| `prio3_src_nlp_text_preprocess.py` | idem — lematização spaCy | idem |
| `prio3_analysis_merge.py` | idem — agregação diária, fuso, retornos D0–D90 | idem |

Ver o documento [`../resumos_pesquisas/07_JPALVES_2025_PRIO3.md`](../resumos_pesquisas/07_JPALVES_2025_PRIO3.md).

**Repositório adicional, não baixado por ser grande (PDFs):**
[`rsabilio/NerEval-BrazilianCorporateTranscripts`](https://github.com/rsabilio/NerEval-BrazilianCorporateTranscripts)
— corpus **BraFiNER** de *earnings calls* de bancos brasileiros, licença **MIT**. Interessa o
*notebook* `0-transcripts/extract-and-preprocess.ipynb` (pipeline `pdfplumber → NLTK → sentenças`).

---

## Ordem de execução sugerida

```bash
# ── Antes de 10/08 — nada disto consome rotulagem ────────────────────────────

# 1. G12 · significância da tabela de encoders (~2 h, CPU)
python reconstrucao_santos_bootstrap.py \
    --predicoes ../../Mestrado_PETR4/conjunto_ouro/predicoes_encoders.csv \
    --col-verdade rotulo_humano \
    --modelos pred_finbert pred_bertimbau_large pred_albertina

# 2. G7 · comitê de modelos (~3 h)
python comite_sentimento_petr4.py \
    --gabarito ../../Mestrado_PETR4/conjunto_ouro/gabarito_ampliacao.csv

# 3. G6 · LLM × encoder (~4 h; exige ANTHROPIC_API_KEY ou GOOGLE_API_KEY)
python llm_vs_encoder_conjunto_ouro.py \
    --gabarito ../../Mestrado_PETR4/conjunto_ouro/gabarito_ampliacao.csv \
    --provedor gemini --repeticoes 3

# 4. G3 · adaptação de domínio por MLM (Colab, 6–10 h) — a frente principal
python reconstrucao_santos_etapa1_mlm.py \
    --corpus ../../Mestrado_PETR4/base_textual_petr4_wordpress_2016_2026.csv \
    --coluna titulo --modelo finbert --saida modelos/finbert-petr4
python reconstrucao_santos_etapa1_mlm.py \
    --corpus ... --modelo bertimbau-large --saida modelos/bertimbau-petr4

# ── Depois de 10/08 ──────────────────────────────────────────────────────────

# 5. G4 · diagnóstico de concept drift
python avaliacao_temporal_drift.py \
    --gabarito ../../Mestrado_PETR4/conjunto_ouro/gabarito_ampliacao.csv \
    --corpus ../../Mestrado_PETR4/base_textual_petr4_wordpress_2016_2026.csv

# 6. G3 (parte 2) · reavaliar encoders com o protocolo correto
python reconstrucao_santos_etapa2_sentimento.py \
    --gabarito ../../Mestrado_PETR4/conjunto_ouro/gabarito_ampliacao.csv \
    --modelo modelos/finbert-petr4
```

> ⚠️ **Confirmar os nomes das colunas antes de rodar.** Os valores padrão (`titulo`,
> `rotulo_humano`, `data_publicacao`, `pred_finbert`) são suposições baseadas na estrutura do
> repositório; conferir contra os CSVs reais de `Mestrado_PETR4/conjunto_ouro/`.

> ⚠️ **O PyTorch local está inoperante** (`WinError 1114` / `c10.dll`) — falha pré-existente,
> verificada isoladamente. Os scripts 2, 4, 5 e 6 dependem de `torch`. Preferir o **Google
> Colab**, que é o ambiente para o qual a maior parte do pipeline já foi escrita.

---

## Dependências

```bash
pip install transformers datasets torch scikit-learn pandas numpy scipy
pip install pysentimiento                    # comitê (G7)
pip install anthropic google-generativeai    # LLM (G6) — só o provedor escolhido
```

Nesta máquina o `pip` exige `--trusted-host pypi.org --trusted-host files.pythonhosted.org`
(erro de certificado SSL).

---

## Nota sobre a autoria das reconstruções

O código de treinamento do FinBERT-PT-BR **não foi publicado** — verificado em 04/08/2026 no
GitHub pessoal do autor (22 repositórios), na organização `turing-usp` (81 repositórios) e no
repositório HuggingFace (10 arquivos, só pesos e *tokenizer*). O mesmo vale para Błoch et al.
(2026), Imai et al. (2024) e Teles e Figueiredo (2025).

As reconstruções foram escritas a partir dos hiperparâmetros e descrições publicados nos
artigos, e **não reproduzem código proprietário**. Ao reportar resultados obtidos com elas na
dissertação, descrever como *"implementação própria do protocolo descrito por [autor]"*, e
nunca como replicação exata — porque não é possível verificar se é.
