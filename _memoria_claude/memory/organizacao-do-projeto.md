---
name: organizacao-do-projeto
description: como o repositório está organizado — pastas de Artigo e de Mentoria — e como restaurar esta memória noutra máquina
metadata:
  type: project
---

Em 20/09/2026 o repositório foi reorganizado a pedido do Vanderlei, que precisa
estudar o material de outra máquina e apresentar aos orientadores.

**Estrutura:**
- `Artigos/Artigo_N_.../` — um diretório por artigo, com `00_LEIA-ME.md`, o texto,
  `fontes/`, `dados/` e `codigo/`. As propostas comparadas ficam em
  `Artigos/00_TRES_PROPOSTAS.docx`; os PDFs das pesquisas citadas em
  `Artigos/_fontes_bibliograficas/`.
- `Mentorias/AAAA-MM-DD_Professores/` — um diretório por reunião, com `00_LEIA-ME.md`
  contendo o que foi pedido, o que foi feito em linguagem simples, e os artefatos.
- `Painel/` — o painel interativo e `00_COMO_APRESENTAR.md`, com roteiro de sete
  minutos.
- `_memoria_claude/` — **esta memória, versionada**.

**A memória é portátil.** Ela vive fora do repositório, em
`~/.claude/projects/<nome-derivado-do-caminho>/memory`, e não vem no clone. Por isso:

    python _memoria_claude/restaurar_memoria.py            # ao abrir noutra máquina
    python _memoria_claude/restaurar_memoria.py --salvar   # ao fim da sessão

O script **procura** a pasta em vez de adivinhar a convenção de nome — a primeira
versão errou ao supor `.lower()` e manter `_`, quando o Claude preserva a
capitalização e troca `_` por `-`.

Dois scripts reconstroem tudo, e são idempotentes: `_organizar_projeto.py` (copia,
não move) e `_gerar_indices.py` (reescreve os LEIA-ME).

Ver [[artigo-1-relogio-da-cvm]] e [[cvm-estudo-de-evento]].
