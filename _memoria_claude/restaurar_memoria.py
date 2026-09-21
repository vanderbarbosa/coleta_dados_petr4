# -*- coding: utf-8 -*-
# ==============================================================================
#   Restaura a memória do Claude ao abrir o projeto em outra máquina
#
#   A memória fica FORA do repositório, num diretório do Claude ligado ao
#   caminho do projeto. Ao clonar em máquina nova, ela não vem junto — e o
#   assistente começa sem saber nada da pesquisa.
#
#   Este script copia a memória versionada de volta para o lugar certo.
#
#   COMO USAR, na máquina nova:
#       python _memoria_claude/restaurar_memoria.py
#
#   E o caminho inverso, para versionar o que foi aprendido depois:
#       python _memoria_claude/restaurar_memoria.py --salvar
# ==============================================================================
from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path

AQUI = Path(__file__).resolve().parent
COPIA = AQUI / "memory"


def candidatos(proj: Path) -> list[str]:
    """Nomes possíveis da pasta, segundo as convenções já observadas."""
    s = str(proj)
    base = s.replace(":", "-").replace("\\", "-").replace("/", "-")
    return [
        base.replace("_", "-"),                    # convenção observada
        base[0].lower() + base[1:].replace("_", "-"),
        base,
        base.lower(),
        base.lower().replace("_", "-"),
    ]


def destino_claude(criar_se_faltar: bool = False) -> Path | None:
    """Onde o Claude guarda a memória deste projeto NESTA máquina.

    Não adivinha a convenção de nome: procura a pasta existente. Só cai no
    palpite quando nenhuma existe e é preciso criar uma.
    """
    raiz = Path(os.environ.get("USERPROFILE") or Path.home()) / ".claude" / "projects"
    proj = AQUI.parent.parent                     # .../base_textual
    nomes = candidatos(proj)

    # 1) o nome exato, em qualquer das variantes
    for nome in nomes:
        alvo = raiz / nome / "memory"
        if alvo.exists():
            return alvo

    # 2) busca tolerante: a pasta cujo nome tenha as mesmas partes
    if raiz.exists():
        partes = {p.lower() for p in proj.parts if p and ":" not in p}
        for d in raiz.iterdir():
            if not d.is_dir():
                continue
            n = d.name.lower().replace("_", "-")
            if all(p.replace("_", "-") in n for p in partes):
                return d / "memory"

    return (raiz / nomes[0] / "memory") if criar_se_faltar else None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--salvar", action="store_true",
                    help="copia da máquina para o repositório, em vez do contrário")
    a = ap.parse_args()

    dest = destino_claude(criar_se_faltar=not a.salvar)
    print("=" * 74)
    print("  MEMÓRIA DA PESQUISA")
    print("=" * 74)
    print(f"  no repositório : {COPIA}")
    print(f"  nesta máquina  : {dest}")

    if a.salvar:
        if dest is None or not dest.exists():
            raise SystemExit(f"\n  Não há memória em {dest}. Nada a salvar.")
        COPIA.mkdir(parents=True, exist_ok=True)
        shutil.copytree(dest, COPIA, dirs_exist_ok=True)
        n = len(list(COPIA.glob("*.md")))
        print(f"\n  SALVO: {n} arquivos da máquina para o repositório.")
        print("  Não esqueça de dar commit.")
        return

    if not COPIA.exists():
        raise SystemExit(f"\n  Não encontrei {COPIA}.")
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copytree(COPIA, dest, dirs_exist_ok=True)
    n = len(list(dest.glob("*.md")))
    print(f"\n  RESTAURADO: {n} arquivos de memória.")
    print("  Abra o Claude Code nesta pasta e ele já saberá da pesquisa.")


if __name__ == "__main__":
    main()
