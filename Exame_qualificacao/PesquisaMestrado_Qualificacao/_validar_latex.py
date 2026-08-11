# -*- coding: utf-8 -*-
"""Verificação de integridade do projeto LaTeX antes de compilar no Overleaf.

Confere três coisas que quebram a compilação ou geram '??' no PDF:
  1. toda \\cite tem entrada correspondente no references.bib
  2. toda \\ref aponta para um \\label que existe
  3. chaves e ambientes estão balanceados nos arquivos

Uso:  python _validar_latex.py
"""
import glob
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

RAIZ = os.path.dirname(os.path.abspath(__file__))
os.chdir(RAIZ)

PAT_ENTRADA = re.compile(r"^@\w+\s*\{\s*([^,\s]+)", re.M)
PAT_CITE = re.compile(r"\\cite[a-zA-Z]*\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}")
PAT_REF = re.compile(r"\\(?:auto)?ref\s*\{([^}]+)\}")
PAT_LABEL = re.compile(r"\\label\s*\{([^}]+)\}")
# o pacote listings declara o rótulo dentro das opções: [..., label=lst:foo]
PAT_LABEL_LST = re.compile(r"label\s*=\s*([A-Za-z0-9:._-]+)")
PAT_BEGIN = re.compile(r"\\begin\s*\{")
PAT_END = re.compile(r"\\end\s*\{")


def ler(caminho):
    with open(caminho, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def main():
    arquivos = sorted(glob.glob("capitulos/*.tex") + glob.glob("apendices/*.tex")
                      + glob.glob("frontmatter/*.tex") + ["main.tex"])
    print(f"Arquivos .tex analisados: {len(arquivos)}\n")

    # ── 1. citações ──────────────────────────────────────────────────────────
    chaves_bib = set(PAT_ENTRADA.findall(ler("references.bib")))
    usadas, faltando = set(), {}
    for f in arquivos:
        texto = ler(f)
        for grupo in PAT_CITE.findall(texto):
            for chave in (x.strip() for x in grupo.split(",")):
                if not chave:
                    continue
                usadas.add(chave)
                if chave not in chaves_bib:
                    faltando.setdefault(os.path.basename(f), set()).add(chave)
    print(f"[1] Entradas no references.bib .... {len(chaves_bib)}")
    print(f"    Citações distintas usadas ..... {len(usadas)}")
    if faltando:
        print("    *** CITAÇÕES SEM ENTRADA NO BIB ***")
        for f, ks in faltando.items():
            print(f"        {f}: {sorted(ks)}")
    else:
        print("    Todas as citações têm entrada .. OK")

    nao_usadas = chaves_bib - usadas
    print(f"    Entradas no bib não citadas .... {len(nao_usadas)} "
          "(não impede a compilação)")

    # ── 2. referências cruzadas ──────────────────────────────────────────────
    labels = set()
    for f in arquivos:
        conteudo = ler(f)
        labels |= set(PAT_LABEL.findall(conteudo))
        labels |= set(PAT_LABEL_LST.findall(conteudo))
    quebradas = {}
    for f in arquivos:
        for r in PAT_REF.findall(ler(f)):
            if r not in labels:
                quebradas.setdefault(os.path.basename(f), set()).add(r)
    print(f"\n[2] Labels definidos ............. {len(labels)}")
    if quebradas:
        print("    *** REFERÊNCIAS QUEBRADAS (virariam '??' no PDF) ***")
        for f, rs in quebradas.items():
            print(f"        {f}: {sorted(rs)}")
    else:
        print("    Todas as \\ref resolvem ........ OK")

    # ── 3. balanceamento ─────────────────────────────────────────────────────
    print("\n[3] Balanceamento por arquivo:")
    problemas = 0
    for f in arquivos:
        t = ler(f)
        ab, fc = t.count("{"), t.count("}")
        beg, end = len(PAT_BEGIN.findall(t)), len(PAT_END.findall(t))
        ok_ch = ab == fc
        ok_env = beg == end
        if not (ok_ch and ok_env):
            problemas += 1
            print(f"    *** {f}: chaves {ab}/{fc} | begin/end {beg}/{end}")
    if not problemas:
        print("    Todos balanceados ............. OK")

    # ── resumo ───────────────────────────────────────────────────────────────
    erros = bool(faltando) + bool(quebradas) + bool(problemas)
    print("\n" + "=" * 62)
    print("PRONTO PARA COMPILAR" if not erros else f"*** {erros} TIPO(S) DE PROBLEMA ***")
    print("=" * 62)
    return 0 if not erros else 1


if __name__ == "__main__":
    sys.exit(main())
