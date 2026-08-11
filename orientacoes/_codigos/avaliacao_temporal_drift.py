# -*- coding: utf-8 -*-
# =============================================================================
#  Diagnóstico de CONCEPT DRIFT no sentimento — gap G4
#  Inspirado em Imai et al. (2024), IEEE Big Data — PPGIa/PUCPR
# =============================================================================
#
#  ⚠️  ORIGEM: código próprio. Imai et al. (2024) não publicaram código e o
#  texto integral está atrás do paywall do IEEE Xplore.
#
#  O PROBLEMA QUE ISTO DIAGNOSTICA
#  Usamos o FinBERT-PT-BR congelado em 13/02/2024 para classificar notícias de
#  2018 a 2026. As notícias de 2025-2026 sobre a Petrobras contêm vocabulário
#  que o modelo nunca viu — mudanças na política de preços, novo ciclo de
#  dividendos, Margem Equatorial, novo plano estratégico.
#
#  Imai et al. (2024) citam Santos justamente para dizer que ele "não respeita
#  a ordem temporal", e demonstram que o ajuste fino periódico com amostra
#  reduzida de textos recentes supera o modelo estático na maioria dos anos.
#
#  ATENUANTE A REGISTRAR: o nosso split treino/validação/teste é TEMPORAL
#  (Script 02c) e o Script 05 usa walk-forward. O que não respeita a ordem
#  temporal é apenas a ETAPA DE SENTIMENTO, em que um modelo estático é
#  aplicado a todo o período. Fazer essa distinção explicitamente evita que a
#  crítica pareça mais ampla do que é.
#
#  DOIS DIAGNÓSTICOS INDEPENDENTES
#    (A) COM gabarito ..... acurácia/kappa por período contra o conjunto-ouro
#    (B) SEM gabarito ..... perplexidade por ano sobre o corpus completo
#        → (B) é self-supervised e vale mesmo com a rotulagem suspensa
#
#  ⚠️  RESSALVA ESTATÍSTICA SOBRE (A): com 300 manchetes em 9 anos, cada ano
#  tem ~33 itens — pouco para conclusão robusta. Por isso o padrão é agrupar em
#  DOIS BLOCOS (até 2023 × 2024-2026), o que dá ~150 itens cada. O modo anual
#  fica disponível via --por-ano, mas com IC por bootstrap obrigatório.
# =============================================================================
from __future__ import annotations

import argparse
import json
import math
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, cohen_kappa_score, f1_score

CLASSES = ["Negative", "Neutral", "Positive"]
# O modelo foi publicado/congelado em 13/02/2024 — é a fronteira natural
CORTE_CONGELAMENTO = 2024


def ic_bootstrap(y_true, y_pred, metrica, n=2000, seed=42):
    """IC de 80% por bootstrap — obrigatório com amostras pequenas."""
    rng = np.random.default_rng(seed)
    y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
    vals = []
    for _ in range(n):
        idx = rng.integers(0, len(y_true), len(y_true))
        if len(np.unique(y_true[idx])) < 2:
            continue
        vals.append(metrica(y_true[idx], y_pred[idx]))
    if not vals:
        return None, None
    return tuple(round(float(v), 4) for v in np.percentile(vals, [10, 90]))


def diagnostico_com_gabarito(df, col_ano, col_true, col_pred, por_ano=False):
    """(A) Acurácia e kappa por período — exige gabarito humano."""
    if por_ano:
        grupos = [(str(a), g) for a, g in df.groupby(col_ano)]
    else:
        antes = df[df[col_ano] < CORTE_CONGELAMENTO]
        depois = df[df[col_ano] >= CORTE_CONGELAMENTO]
        grupos = [(f"até {CORTE_CONGELAMENTO - 1}", antes),
                  (f"{CORTE_CONGELAMENTO}+", depois)]

    linhas = []
    for rotulo, g in grupos:
        if len(g) < 10:
            print(f"  ⚠️  {rotulo}: n={len(g)} — pequeno demais, ignorado")
            continue
        yt, yp = g[col_true].to_numpy(), g[col_pred].to_numpy()
        acc = accuracy_score(yt, yp)
        kap = cohen_kappa_score(yt, yp, labels=CLASSES)
        f1m = f1_score(yt, yp, average="macro", labels=CLASSES, zero_division=0)
        ic_i, ic_s = ic_bootstrap(yt, yp, accuracy_score)
        linhas.append({
            "periodo": rotulo, "n": int(len(g)),
            "acuracia": round(float(acc), 4),
            "acuracia_ic80": [ic_i, ic_s],
            "f1_macro": round(float(f1m), 4),
            "kappa": round(float(kap), 4),
        })
        print(f"  {rotulo:14s} n={len(g):4d}  acc={acc:.4f} "
              f"IC80=[{ic_i}, {ic_s}]  F1={f1m:.4f}  κ={kap:.4f}")
    return linhas


def diagnostico_sem_gabarito(corpus_csv, col_texto, col_data, modelo_dir,
                             n_por_ano=1500):
    """(B) Perplexidade por ano — NÃO exige rótulo humano.

    Se a perplexidade subir nos anos recentes, há semantic shift: o vocabulário
    das notícias afastou-se daquele que o modelo viu no pré-treino. É evidência
    de drift obtida de forma inteiramente self-supervised.
    """
    import torch
    from transformers import AutoModelForMaskedLM, AutoTokenizer

    tok = AutoTokenizer.from_pretrained(modelo_dir)
    mdl = AutoModelForMaskedLM.from_pretrained(modelo_dir)
    mdl.eval()
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    mdl.to(dev)

    df = pd.read_csv(corpus_csv).dropna(subset=[col_texto, col_data])
    df["ano"] = pd.to_datetime(df[col_data], errors="coerce").dt.year
    df = df.dropna(subset=["ano"])

    linhas = []
    for ano, g in df.groupby("ano"):
        amostra = g[col_texto].astype(str).head(n_por_ano).tolist()
        perdas = []
        with torch.no_grad():
            for i in range(0, len(amostra), 16):
                lote = tok(amostra[i:i + 16], truncation=True, max_length=512,
                           padding=True, return_tensors="pt").to(dev)
                # rótulos = entrada → loss de MLM sobre os tokens mascarados
                perdas.append(mdl(**lote, labels=lote["input_ids"]).loss.item())
        ppl = math.exp(float(np.mean(perdas)))
        linhas.append({"ano": int(ano), "n": len(amostra),
                       "perplexidade": round(ppl, 4)})
        print(f"  {int(ano)}  n={len(amostra):5d}  perplexidade={ppl:.4f}")
    return linhas


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--gabarito", type=Path,
                   help="CSV do conjunto-ouro com rótulo humano e predição")
    p.add_argument("--col-data", default="data_publicacao")
    p.add_argument("--col-true", default="rotulo_humano")
    p.add_argument("--col-pred", default="pred_finbert")
    p.add_argument("--por-ano", action="store_true",
                   help="Quebra por ano em vez de dois blocos. Cuidado: ~33 "
                        "itens por ano é pouco para conclusão robusta.")
    p.add_argument("--corpus", type=Path,
                   help="CSV do corpus completo, para o diagnóstico (B)")
    p.add_argument("--col-texto", default="titulo")
    p.add_argument("--modelo", default="lucas-leme/FinBERT-PT-BR")
    p.add_argument("--saida", type=Path,
                   default=Path("Mestrado_PETR4/diagnostico_drift.json"))
    args = p.parse_args()

    resultado = {"data": date.today().isoformat(), "modelo": args.modelo,
                 "corte_congelamento": CORTE_CONGELAMENTO,
                 "referencia": "Imai et al. (2024), IEEE Big Data"}

    if args.gabarito:
        print("(A) Desempenho por período, contra o gabarito humano")
        df = pd.read_csv(args.gabarito).dropna(
            subset=[args.col_true, args.col_pred, args.col_data])
        df["ano"] = pd.to_datetime(df[args.col_data], errors="coerce").dt.year
        df = df.dropna(subset=["ano"])
        df["ano"] = df["ano"].astype(int)
        resultado["com_gabarito"] = diagnostico_com_gabarito(
            df, "ano", args.col_true, args.col_pred, args.por_ano)

    if args.corpus:
        print("\n(B) Perplexidade por ano — sem gabarito")
        resultado["sem_gabarito"] = diagnostico_sem_gabarito(
            args.corpus, args.col_texto, args.col_data, args.modelo)

    args.saida.parent.mkdir(parents=True, exist_ok=True)
    args.saida.write_text(json.dumps(resultado, indent=2, ensure_ascii=False),
                          encoding="utf-8")
    print(f"\n✓ Salvo em {args.saida}")
    print("\nCOMO INTERPRETAR:")
    print("  (A) queda de acurácia/kappa a partir de 2024 → indício de drift,")
    print("      MAS só é conclusivo se os ICs de 80% NÃO se sobrepuserem.")
    print("  (B) aumento de perplexidade nos anos recentes → semantic shift,")
    print("      evidência independente de gabarito.")
    print("\n  Se nenhum dos dois aparecer, isso também é resultado: significa")
    print("  que o drift não é material no nosso corpus, e a limitação pode ser")
    print("  declarada como testada e descartada — o que é ainda melhor.")


if __name__ == "__main__":
    main()
