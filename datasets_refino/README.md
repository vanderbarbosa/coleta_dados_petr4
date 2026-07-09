# Datasets — refino pedido pela banca (jul/2026)

Datasets derivados **apenas de dados reais** da pesquisa (sem valores inventados).
Os `.csv` grandes ficam locais (o `.gitignore` ignora `*.csv`); os geradores e este
README são versionados. Regenere com os scripts abaixo.

## Arquivos

| Arquivo | Conteúdo | Gerador | Fonte |
|---|---|---|---|
| `01_noticias_apos_17h_vN.csv` | Notícias publicadas **após 17h** (Lead-Lag). 54.259 = 26,4% do corpus. | `gerar_datasets_refino.py` | `noticias_com_sentimento.csv` |
| `02_noticias_apos17h_enriquecido_vN.csv` | Por notícia: pregão, notícia, **sentimento (FinBERT)**, **volatilidade (GARCH)**, retorno, direção real e **parâmetros dos encoders**. | idem | `noticias_com_sentimento.csv` + `base_master_petr4.csv` + `modelo_meta.json` |
| `03_resultados_volatilidade_vN.csv` | Resultados de **volatilidade** (Granger, quantílica, regime). | idem | `resultados_granger/quantilica/regime` |
| `04_revisao_sistematica_estudos_vN.csv` | **RSL**: 25 estudos (título, ano, idioma, método, encoder…). Parâmetros/resultados por estudo = extrair dos PDFs. | `gerar_rsl_dataset.py` | Referencial Cap.2 + `references.bib` |

## Como regenerar
```bash
python datasets_refino/gerar_datasets_refino.py    # 01, 02, 03
python datasets_refino/gerar_rsl_dataset.py         # 04
```

## Versionamento (item 4C)
Cada execução cria um novo `_vN` sem apagar os anteriores — para comparar refinamentos.

Ver `docs/RESPOSTAS_BANCA_JUL2026.md` para o contexto de cada item.
