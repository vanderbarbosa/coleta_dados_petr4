# -*- coding: utf-8 -*-
"""Empacota o projeto para upload no Overleaf.

Inclui apenas o que a compilação precisa: fontes .tex, a classe, a bibliografia,
as figuras e os PDFs institucionais. Exclui backups, caches, arquivos auxiliares
do LaTeX e os próprios zips anteriores.

Uso:  python _gerar_overleaf.py
"""
import os
import sys
import zipfile
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parent
DESTINO = RAIZ.parent / f"Overleaf_PETR4_{date.today().isoformat()}.zip"

# extensões que entram
EXT_OK = {".tex", ".cls", ".bib", ".sty", ".png", ".jpg", ".jpeg", ".pdf", ".eps"}
# nada que casar com isto entra
IGNORAR = {".bak", ".aux", ".log", ".out", ".toc", ".lof", ".lot", ".bbl",
           ".blg", ".synctex", ".gz", ".fls", ".fdb_latexmk", ".zip", ".pyc"}
PASTAS_IGNORADAS = {"__pycache__", ".git", ".ipynb_checkpoints"}
ARQUIVOS_IGNORADOS = {"referencesold.bib", "_gerar_overleaf.py", "_validar_latex.py"}


def deve_incluir(caminho: Path) -> bool:
    if any(p in PASTAS_IGNORADAS for p in caminho.parts):
        return False
    if caminho.name in ARQUIVOS_IGNORADOS:
        return False
    if caminho.suffix.lower() in IGNORAR:
        return False
    if caminho.name.endswith(".bib.bak"):
        return False
    return caminho.suffix.lower() in EXT_OK


def main() -> None:
    arquivos = [p for p in RAIZ.rglob("*") if p.is_file() and deve_incluir(p)]
    arquivos.sort()

    if DESTINO.exists():
        DESTINO.unlink()

    total = 0
    por_tipo: dict[str, int] = {}
    with zipfile.ZipFile(DESTINO, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in arquivos:
            rel = p.relative_to(RAIZ)
            z.write(p, rel)
            total += p.stat().st_size
            por_tipo[p.suffix.lower()] = por_tipo.get(p.suffix.lower(), 0) + 1

    print(f"Arquivos empacotados: {len(arquivos)}")
    for ext, n in sorted(por_tipo.items(), key=lambda kv: -kv[1]):
        print(f"   {ext:8s} {n:4d}")
    print(f"\nTamanho original .. {total / 1024 / 1024:.1f} MB")
    print(f"Tamanho do zip .... {DESTINO.stat().st_size / 1024 / 1024:.1f} MB")
    print(f"\n[OK] {DESTINO}")

    # confere se o essencial entrou
    with zipfile.ZipFile(DESTINO) as z:
        nomes = set(z.namelist())
    essenciais = ["main.tex", "ppgia.cls", "references.bib",
                  "capitulos/4i-adaptacao-dominio.tex",
                  "capitulos/4j-achados-implementacao.tex"]
    print("\nConferência do conteúdo essencial:")
    for e in essenciais:
        marca = "OK" if e in nomes else "*** FALTANDO ***"
        print(f"   {e:44s} {marca}")


if __name__ == "__main__":
    main()
