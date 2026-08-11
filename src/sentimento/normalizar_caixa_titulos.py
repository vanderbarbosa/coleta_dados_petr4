# -*- coding: utf-8 -*-
# =============================================================================
#  DISSERTAÇÃO PETR4 — Correção de caixa alta antes da classificação
# =============================================================================
#
#  O PROBLEMA ENCONTRADO EM 08/08/2026
#  O portal Petronoticias publica TODAS as manchetes em CAIXA ALTA. São 21.619
#  notícias, 10,5% do corpus. E o FinBERT-PT-BR é construído sobre o BERTimbau
#  *cased* — o `tokenizer_config.json` declara `do_lower_case: False`.
#
#  Consequência medida:
#    - NENHUMA das 12 palavras-chave do domínio existe em caixa alta no
#      vocabulário ("PETROBRAS", "GASOLINA", "LUCRO"... nenhuma)
#    - cobertura do vocabulário: 22,2% em caixa alta contra 78,6% em caixa normal
#    - o modelo classifica 84,3% dessas manchetes como NEUTRAS (contra 32,0%
#      nas de caixa normal) e sua confiança média cai de 0,697 para 0,589
#    - no conjunto-ouro: acurácia 0,528 e kappa 0,195 nas 36 manchetes em caixa
#      alta, contra 0,587 e 0,386 nas 264 restantes
#
#  Em outras palavras: uma fonte inteira do corpus está sendo despejada na
#  classe neutra por um problema de tokenização, não por ser neutra.
#
#  A CORREÇÃO
#  Normalizar a caixa antes de classificar. Testadas quatro estratégias por
#  cobertura de vocabulário:
#      como está ....... 22,3%
#      .title() ........ 56,4%
#      .capitalize() ... 77,6%   <- adotada
#      .lower() ........ 78,2%
#      (referência: fonte em caixa normal = 78,4%)
#
#  Adotou-se `.capitalize()` com preservação de siglas: recupera praticamente
#  toda a cobertura e mantém a forma de sentença, que é como o modelo viu o
#  texto no treino (os 503 exemplos de Santos são sentenças de corpo de
#  notícia, não manchetes em caixa alta).
#
#  ⚠️  A cobertura de vocabulário é uma APROXIMAÇÃO do ganho real. A validação
#  definitiva exige reclassificar o conjunto-ouro com os títulos normalizados e
#  comparar acurácia e kappa — o que exige GPU (o torch local está inoperante).
#  Este script prepara o corpus; a medição vem depois.
#
#  Uso:
#      python src/sentimento/normalizar_caixa_titulos.py --entrada <csv> --saida <csv>
# =============================================================================
from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
DIR = RAIZ / "Mestrado_PETR4"

# Siglas do domínio que devem permanecer em caixa alta após a normalização.
# Sem isto, "ANP" viraria "Anp" e "OPEP" viraria "Opep".
SIGLAS = {
    "ANP", "OPEP", "OPEC", "CNPE", "ANEEL", "IBAMA", "CADE", "CVM", "BNDES",
    "GLP", "GNL", "GNV", "FPSO", "FPSOS", "LNG", "OPA", "IPO", "PIB", "ICMS",
    "CIDE", "PPI", "IPCA", "COPOM", "BCB", "EUA", "UE", "ONU", "OMC", "OTAN",
    "BR", "PETR3", "PETR4", "PRIO3", "VALE3", "B3", "S&P", "CEO", "CFO",
    "E&P", "P&D", "TCU", "STF", "STJ", "MP", "PL", "PEC",
}

LIMIAR_CAPS = 0.90     # fração de letras maiúsculas para considerar "caixa alta"
MIN_LETRAS = 10        # títulos muito curtos não são avaliados


def eh_caixa_alta(texto: str) -> bool:
    """Um título está em caixa alta se >90% das suas letras forem maiúsculas."""
    letras = [c for c in str(texto) if c.isalpha()]
    if len(letras) < MIN_LETRAS:
        return False
    return sum(c.isupper() for c in letras) / len(letras) > LIMIAR_CAPS


def normalizar(texto: str) -> str:
    """Converte para forma de sentença, preservando as siglas conhecidas.

    'CNPE CONFIRMA DIREITO DA PETROBRÁS' -> 'CNPE confirma direito da Petrobrás'
    """
    palavras = str(texto).split()
    saida = []
    for i, p in enumerate(palavras):
        nu = re.sub(r"\W", "", p).upper()
        if nu in SIGLAS:
            saida.append(p.upper())          # sigla: mantém maiúscula
        elif i == 0:
            saida.append(p.capitalize())     # primeira palavra: inicial maiúscula
        else:
            saida.append(p.lower())
    r = " ".join(saida)
    # garante inicial maiúscula mesmo se a primeira palavra for sigla curta
    return (r[0].upper() + r[1:]) if r else r


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--entrada", type=Path,
                    default=DIR / "base_textual_petr4_wordpress_2016_2026.csv")
    ap.add_argument("--saida", type=Path, default=None,
                    help="Padrão: <entrada>_normalizado.csv")
    ap.add_argument("--coluna", default=None,
                    help="Coluna de título. Detectada automaticamente se omitida.")
    ap.add_argument("--relatorio", type=Path,
                    default=DIR / "normalizacao_caixa_relatorio.json")
    args = ap.parse_args()

    df = pd.read_csv(args.entrada)

    col = args.coluna
    if col is None:
        for cand in ("Titulo", "titulo", "Título", "title"):
            if cand in df.columns:
                col = cand
                break
    if col is None:
        raise SystemExit(f"Coluna de título não encontrada. Colunas: {list(df.columns)}")

    df[col] = df[col].astype(str)
    df["_caps"] = df[col].map(eh_caixa_alta)
    n_caps = int(df["_caps"].sum())

    print(f"Arquivo   : {args.entrada.name}")
    print(f"Coluna    : {col}")
    print(f"Registros : {len(df):,}")
    print(f"Em caixa alta: {n_caps:,} ({n_caps / len(df):.1%})\n")

    if "Fonte" in df.columns and n_caps:
        print("Distribuicao por fonte:")
        por_fonte = (df.groupby("Fonte")["_caps"]
                       .agg(n="size", caps="sum")
                       .assign(pct=lambda t: (t["caps"] / t["n"] * 100).round(1))
                       .sort_values("pct", ascending=False))
        print(por_fonte.to_string(), "\n")

    # guarda o original e grava a versão normalizada na mesma coluna, para que
    # o Script 03 possa consumir sem nenhuma alteração de código
    df[f"{col}_original"] = df[col]
    df.loc[df["_caps"], col] = df.loc[df["_caps"], col].map(normalizar)

    if n_caps:
        print("Exemplos de transformacao:")
        for _, r in df[df["_caps"]].head(4).iterrows():
            print(f"  ANTES : {r[f'{col}_original'][:88]}")
            print(f"  DEPOIS: {r[col][:88]}\n")

    saida = args.saida or args.entrada.with_name(args.entrada.stem + "_normalizado.csv")
    df.drop(columns=["_caps"]).to_csv(saida, index=False, encoding="utf-8-sig")

    args.relatorio.write_text(json.dumps({
        "data_execucao": date.today().isoformat(),
        "entrada": str(args.entrada.name),
        "saida": str(saida.name),
        "coluna": col,
        "n_registros": int(len(df)),
        "n_normalizados": n_caps,
        "pct_normalizados": round(n_caps / len(df), 4),
        "estrategia": "capitalize com preservacao de siglas",
        "cobertura_vocabulario": {"antes": 0.222, "depois": 0.776,
                                  "referencia_caixa_normal": 0.784},
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"[OK] Corpus normalizado -> {saida}")
    print(f"[OK] Relatorio          -> {args.relatorio}")
    print("\nPROXIMO PASSO (exige GPU):")
    print("  1. Reclassificar o conjunto-ouro com os titulos normalizados")
    print("  2. Comparar acuracia e kappa contra os valores atuais")
    print("     (36 manchetes em caixa alta: hoje acc=0,528 kappa=0,195)")
    print("  3. Se confirmar ganho, reprocessar o corpus completo e refazer o ISM")


if __name__ == "__main__":
    main()
