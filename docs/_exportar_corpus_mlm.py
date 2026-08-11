# -*- coding: utf-8 -*-
# =============================================================================
#  Exporta um corpus compacto para a adaptação de domínio por MLM (gap G3)
# =============================================================================
#
#  POR QUE UM ARQUIVO SEPARADO
#  A base completa tem 151 MB — inviável para subir ao Colab a cada sessão.
#  Este script extrai apenas o texto necessário e comprime, resultando em
#  poucos megabytes.
#
#  POR QUE `Título` + `Resumo`, se o experimento 2 mostrou que o `Resumo`
#  ATRAPALHA a classificação?
#  São duas etapas diferentes, e a distinção é importante:
#
#    - CLASSIFICAÇÃO (inferência): usar só `Título`. Medido em 08/08/2026 —
#      acrescentar o `Resumo` derruba a acurácia de 0,580 para 0,530.
#
#    - MLM (adaptação de domínio): usar `Título` + `Resumo`. Aqui não há
#      rótulo, o objetivo é ensinar VOCABULÁRIO e ESTRUTURA ao modelo. Texto
#      mais longo dá mais tokens mascarados por exemplo e mais contexto, o que
#      é estritamente melhor. A mediana sobe de 12 para ~42 palavras — que é
#      justamente o regime dos textos com que Santos treinou (mediana 39).
#
#  Não há contradição: o corpus de pré-treino não precisa ter a mesma forma da
#  entrada de inferência.
#
#  Uso:
#      python docs/_exportar_corpus_mlm.py
# =============================================================================
from __future__ import annotations

import argparse
import gzip
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
DIR = RAIZ / "Mestrado_PETR4"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--entrada", type=Path,
                    default=DIR / "noticias_titulos_normalizados.csv",
                    help="Preferir a versão com os títulos em caixa normalizada")
    ap.add_argument("--saida", type=Path, default=DIR / "corpus_mlm_petr4.csv.gz")
    ap.add_argument("--min-palavras", type=int, default=5,
                    help="Descarta textos curtos demais para treinar MLM")
    args = ap.parse_args()

    if not args.entrada.exists():
        sys.exit(f"Arquivo não encontrado: {args.entrada}\n"
                 f"Rode antes: python src/sentimento/normalizar_caixa_titulos.py")

    cols = pd.read_csv(args.entrada, nrows=0).columns
    col_tit = next((c for c in ("Titulo", "titulo", "Título") if c in cols), None)
    col_res = next((c for c in ("Resumo", "resumo") if c in cols), None)
    if col_tit is None:
        sys.exit(f"Coluna de título não encontrada. Colunas: {list(cols)}")

    usar = [c for c in (col_tit, col_res) if c]
    df = pd.read_csv(args.entrada, usecols=usar)
    print(f"Lidos {len(df):,} registros de {args.entrada.name}")

    tit = df[col_tit].fillna("").astype(str).str.strip()
    if col_res:
        res = df[col_res].fillna("").astype(str).str.strip()
        # junta com ponto final, evitando pontuação duplicada
        texto = (tit.str.rstrip(". ") + ". " + res).str.strip()
        print(f"Usando '{col_tit}' + '{col_res}'")
    else:
        texto = tit
        print(f"Usando apenas '{col_tit}' (coluna de resumo ausente)")

    out = pd.DataFrame({"text": texto})
    out["n_pal"] = out["text"].str.split().str.len()

    antes = len(out)
    out = out[out["n_pal"] >= args.min_palavras]
    out = out.drop_duplicates(subset="text")
    print(f"Após filtro (>= {args.min_palavras} palavras) e deduplicação: "
          f"{len(out):,} ({antes - len(out):,} removidos)")
    print(f"Palavras por texto: mediana={out['n_pal'].median():.0f}  "
          f"média={out['n_pal'].mean():.1f}  p95={out['n_pal'].quantile(.95):.0f}")
    print("(referência: textos de treino de Santos, mediana = 39)")

    with gzip.open(args.saida, "wt", encoding="utf-8", newline="") as fh:
        out[["text"]].to_csv(fh, index=False)

    mb = args.saida.stat().st_size / 1024 / 1024
    print(f"\n[OK] {args.saida.name} — {mb:.1f} MB comprimido")
    print("     Suba este arquivo no Colab (painel de Arquivos, à esquerda).")


if __name__ == "__main__":
    main()
