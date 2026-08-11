# -*- coding: utf-8 -*-
# =============================================================================
#  DISSERTAÇÃO PETR4 — A adaptação de domínio ajuda ou atrapalha? (gap G3)
# =============================================================================
#
#  O EXPERIMENTO
#  Três variantes do mesmo classificador, avaliadas no mesmo conjunto-ouro de
#  300 manchetes:
#
#    A — FinBERT-PT-BR publicado        503 rótulos, validação cruzada (Santos)
#    B — FinBERT + MLM no nosso corpus  352 rótulos, gradual unfreezing
#    C — FinBERT SEM adaptação          352 rótulos, MESMO protocolo de B
#
#  C é o controle que isola o efeito da adaptação: B e C treinaram com os mesmos
#  352 exemplos, mesma semente, mesmo protocolo. A única diferença é o MLM.
#
#  RESULTADO (10/08/2026)
#    C - B = +0,0563 em F1-macro, IC95% [+0,0084, +0,1056], p = 0,0216
#    -> a adaptação de domínio DEGRADOU a classificação, de forma significativa
#
#    Perplexidade no mesmo holdout de 10 mil textos:
#      BERTimbau (cabeça de MLM treinada) .... 7,1950
#      FinBERT adaptado ao nosso corpus ...... 3,6694
#    -> a adaptação FUNCIONOU como modelo de linguagem (perplexidade ~metade)
#
#  A leitura conjunta é o achado: **melhorar o modelo de linguagem piorou a
#  tarefa a jusante.** É esquecimento catastrófico, e o dano se concentra na
#  classe Positiva (recall 0,448 -> 0,281).
#
#  Uso:
#      python src/sentimento/comparar_adaptacao_dominio.py
# =============================================================================
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, cohen_kappa_score, f1_score

RAIZ = Path(__file__).resolve().parents[2]
DIR = RAIZ / "Mestrado_PETR4"
CLASSES = ["Negative", "Neutral", "Positive"]
N_BOOT = 10_000

# perplexidades medidas no Colab, no mesmo holdout (10 mil textos, seed 42)
PPL = {"BERTimbau (cabeca MLM treinada)": 7.1950,
       "FinBERT adaptado ao PETR4": 3.6694}


def f1_macro(y, p):
    return f1_score(y, p, average="macro", labels=CLASSES, zero_division=0)


def bootstrap(y, p, fn, n=N_BOOT, seed=42):
    rng = np.random.default_rng(seed)
    y, p = np.asarray(y), np.asarray(p)
    out = []
    for _ in range(n):
        i = rng.integers(0, len(y), len(y))
        if len(np.unique(y[i])) < 2:
            continue
        out.append(fn(y[i], p[i]))
    return np.array(out)


def bootstrap_pareado(y, p1, p2, fn, n=N_BOOT, seed=42):
    """Diferença calculada na MESMA reamostra — é o teste correto para
    comparar dois modelos avaliados sobre os mesmos itens."""
    rng = np.random.default_rng(seed)
    y, p1, p2 = np.asarray(y), np.asarray(p1), np.asarray(p2)
    difs = []
    for _ in range(n):
        i = rng.integers(0, len(y), len(y))
        if len(np.unique(y[i])) < 2:
            continue
        difs.append(fn(y[i], p1[i]) - fn(y[i], p2[i]))
    return np.array(difs)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--controle", type=Path, default=DIR / "g3_controle_predicoes.csv")
    ap.add_argument("--adaptado", type=Path, default=DIR / "g3_predicoes.csv")
    ap.add_argument("--saida", type=Path, default=DIR / "comparacao_adaptacao_dominio.json")
    args = ap.parse_args()

    a = pd.read_csv(args.controle)
    b = pd.read_csv(args.adaptado)
    d = a.merge(b[["id", "pred_B"]], on="id").rename(columns={"finbert_base": "pred_A"})
    y = d["humano"].values
    print(f"n = {len(d)} manchetes\n")

    rotulos = {"A": "A - publicado (503 rotulos, CV)",
               "B": "B - adaptado por MLM (352 rotulos)",
               "C": "C - SEM adaptacao (352 rotulos)"}

    res = {"data_execucao": date.today().isoformat(), "n": int(len(d)),
           "n_bootstrap": N_BOOT, "perplexidade": PPL, "modelos": {}}

    print("=" * 74)
    print("DESEMPENHO com IC 95% por bootstrap")
    print("=" * 74)
    dist = {}
    for m in "ABC":
        p = d[f"pred_{m}"].values
        dist[m] = bootstrap(y, p, f1_macro)
        lo, hi = np.percentile(dist[m], [2.5, 97.5])
        info = {
            "acuracia": round(float(accuracy_score(y, p)), 4),
            "f1_macro": round(float(f1_macro(y, p)), 4),
            "kappa": round(float(cohen_kappa_score(y, p, labels=CLASSES)), 4),
            "f1_ic95": [round(float(lo), 4), round(float(hi), 4)],
        }
        res["modelos"][m] = {"rotulo": rotulos[m], **info}
        print(f"  {rotulos[m]:36s} acc={info['acuracia']:.4f}  "
              f"F1={info['f1_macro']:.4f}  IC95=[{lo:.4f}, {hi:.4f}]  "
              f"kappa={info['kappa']:+.4f}")

    print("\n" + "=" * 74)
    print("TESTES PAREADOS (diferenca na mesma reamostra)")
    print("=" * 74)
    comparacoes = [("C", "B", "efeito da ADAPTACAO"),
                   ("C", "A", "nosso protocolo x publicado"),
                   ("A", "B", "publicado x adaptado")]
    res["testes"] = []
    for x, z, desc in comparacoes:
        difs = bootstrap_pareado(y, d[f"pred_{x}"].values, d[f"pred_{z}"].values, f1_macro)
        lo, hi = np.percentile(difs, [2.5, 97.5])
        pval = 2 * min((difs <= 0).mean(), (difs >= 0).mean())
        sig = lo > 0 or hi < 0
        print(f"  {x} - {z}  ({desc:28s}) {difs.mean():+.4f}  "
              f"IC95=[{lo:+.4f}, {hi:+.4f}]  p={pval:.4f}  "
              f"-> {'SIGNIFICATIVA' if sig else 'nao significativa'}")
        res["testes"].append({
            "comparacao": f"{x}-{z}", "descricao": desc,
            "delta_f1": round(float(difs.mean()), 4),
            "ic95": [round(float(lo), 4), round(float(hi), 4)],
            "p_valor": round(float(pval), 4), "significativa": bool(sig)})

    print("\n" + "=" * 74)
    print("RECALL POR CLASSE - onde a adaptacao fez o estrago")
    print("=" * 74)
    print(f"  {'classe':12s}{'A':>10s}{'B':>10s}{'C':>10s}{'B - C':>10s}")
    res["recall_por_classe"] = {}
    for c in CLASSES:
        m = d["humano"] == c
        r = {k: float((d.loc[m, f"pred_{k}"] == c).mean()) for k in "ABC"}
        res["recall_por_classe"][c] = {k: round(v, 4) for k, v in r.items()}
        print(f"  {c:12s}{r['A']:>10.3f}{r['B']:>10.3f}{r['C']:>10.3f}"
              f"{r['B']-r['C']:>+10.3f}")

    print("\n" + "=" * 74)
    print("PERPLEXIDADE no mesmo holdout (10 mil textos, seed 42)")
    print("=" * 74)
    for k, v in PPL.items():
        print(f"  {k:40s} {v:.4f}")
    print(f"  {'reducao':40s} {(PPL['BERTimbau (cabeca MLM treinada)'] - PPL['FinBERT adaptado ao PETR4']) / PPL['BERTimbau (cabeca MLM treinada)']:.1%}")

    print("\n" + "=" * 74)
    print("CONCLUSAO")
    print("=" * 74)
    print("""
A adaptacao de dominio por MLM:
  - FUNCIONOU como modelo de linguagem  -> perplexidade 7,195 -> 3,669 (-49%)
  - DEGRADOU a classificacao            -> F1-macro -0,056, p = 0,022

O dano concentra-se na classe POSITIVA: recall cai de 0,448 (C) para 0,281 (B).
E esquecimento catastrofico: o treino de MLM sobre o corpus apagou parte da
representacao especifica de sentimento que o ajuste fino de Santos havia
instalado no corpo do modelo, e 352 rotulos nao bastaram para recuperar.

Nota metodologica relevante: C - A nao e significativa (p = 0,69). Ou seja, o
nosso protocolo de ajuste fino REPRODUZ o modelo publicado usando apenas 352
rotulos - o que valida a implementacao e torna a comparacao B x C confiavel.
""")

    args.saida.write_text(json.dumps(res, indent=2, ensure_ascii=False),
                          encoding="utf-8")
    print(f"[OK] Salvo em {args.saida}")


if __name__ == "__main__":
    main()
