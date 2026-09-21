---
name: dissertacao-latex-overleaf
description: "Onde vive o LaTeX da dissertação, como empacotar para o Overleaf e a armadilha do .gitignore que engole capítulos novos"
metadata: 
  node_type: memory
  type: project
  originSessionId: 08181b53-ca1d-41ae-a256-cc9d79527860
  modified: 2026-08-11T00:58:23.960Z
---

O texto da dissertação é um projeto LaTeX em `coleta_dados_petr4/Exame_qualificacao/PesquisaMestrado_Qualificacao/`, com a classe `ppgia.cls` (template do PPGIa/PUCPR, de autoria do **Jean Paul Barddal**).

**Estrutura:** `main.tex` inclui `capitulos/1-introducao` a `5-conclusao` + apêndices A, B, D. O `4-resultados.tex` faz `\input` das subseções `4d` a `4j` no fim do arquivo.

⚠️ **ARMADILHA: `Exame_qualificacao/` está no `.gitignore`.** Os `.tex` antigos aparecem no `git status` só porque foram commitados **antes** da regra. **Qualquer capítulo NOVO precisa de `git add -f`** ou é silenciosamente perdido.

**Ferramentas criadas (na raiz do projeto LaTeX):**
- `_validar_latex.py` — confere se toda `\cite` tem entrada no bib, se toda `\ref` resolve e se chaves/ambientes batem. **Rodar antes de cada envio ao Overleaf.**
- `_gerar_overleaf.py` — empacota em zip (só .tex/.cls/.bib/figuras; exclui backups, auxiliares e zips antigos). Saída em `Exame_qualificacao/Overleaf_PETR4_<data>.zip` (~28 MB).

**Estado em 10/08/2026:** `\tipodocumento{msc}` (dissertação final, era `pdm`). 100 entradas no bib, 97 citações, 77 labels, tudo resolve.

**Números que precisam bater em toda a dissertação** (conferidos):
- acurácia da fusão **54,5%** · linha de base **50,1%** (⚠️ o resumo dizia 50,9%, estava **errado**)
- kappa do sentimento **0,371** · acurácia do sentimento **58,0%** (=0,580)
- corpus **205.697** notícias

**Capítulos novos escritos:** `4i-adaptacao-dominio.tex` (o experimento G3 com o controle) e `4j-achados-implementacao.tex` (caixa alta + sigmoide).

**Commit:** branch `revisao/dissertacao-final-adaptacao-dominio`, empurrada para o GitHub. **Ainda NÃO mesclada na main** — falta abrir o PR ou fazer merge local.

Ver [[g3-adaptacao-esquecimento]], [[bug-problem-type-sigmoide]] e [[padrao-documentacao-dissertacao]].
