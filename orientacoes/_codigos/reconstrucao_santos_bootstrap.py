# -*- coding: utf-8 -*-
# =============================================================================
#  RECONSTRUÇÃO — validação estatística de Santos (monografia, Seção 4.2.4)
#  Bootstrap + intervalos de confiança + teste Z entre modelos
# =============================================================================
#
#  ⚠️  ORIGEM: reconstrução. O código original não foi publicado. Escrito a
#  partir da descrição da monografia:
#
#    "Visando avaliar o intervalo de confiança das métricas dos modelos de
#     classificação de texto, foi utilizado o método bootstrapping [Efron,
#     1992]. (...) Com um intervalo de confiança de 80% é possível afirmar que
#     o modelo FinBERT PT BR é o melhor (...) visto que o intervalo de
#     confiança da acurácia e do F1-Score não se sobrepõe aos dos outros
#     modelos. (...) Então foram construídas distribuições empíricas da
#     acurácia e f1 score de todos os modelos, e com um teste Z foi possível
#     realizar o teste (...) o p-valor é numericamente igual a 0."
#
#  ---------------------------------------------------------------------------
#  POR QUE ISTO EXISTE (gap G12)
#  A nossa tabela conjunto_ouro/resultado_encoders_petr4.csv reporta:
#      BERTimbau large   −1,67 pp   (dp 5,52)
#      BERTimbau base    −5,33 pp   (dp 8,41)
#      Albertina-100M   −16,00 pp   (dp 2,67)
#  ...SEM nenhum teste de significância. Com n = 300, a diferença de −1,67 pp
#  é quase certamente indistinguível de zero. Levar essa tabela à banca sem
#  intervalo de confiança é convidar a crítica.
#
#  Custo estimado: ~2 horas, incluindo a redação da seção.
#  NÃO consome rotulagem nova — usa as predições que já temos.
# =============================================================================
from __future__ import annotations

import argparse
import json
from datetime import date
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import accuracy_score, cohen_kappa_score, f1_score

N_REAMOSTRAS = 10_000
IC = 80  # Santos usou intervalo de confiança de 80%

METRICAS = {
    "acuracia": accuracy_score,
    "f1_macro": lambda a, b: f1_score(a, b, average="macro"),
    "kappa": cohen_kappa_score,
}


def bootstrap_metrica(y_true: np.ndarray, y_pred: np.ndarray, metrica,
                      n_reamostras: int = N_REAMOSTRAS, seed: int = 42) -> np.ndarray:
    """Distribuição empírica da métrica por reamostragem com reposição.

    Efron (1992). Reamostra os PARES (verdadeiro, predito) com reposição e
    recalcula a métrica em cada reamostra, produzindo a distribuição empírica
    a partir da qual se extraem intervalos de confiança e testes.
    """
    rng = np.random.default_rng(seed)
    n = len(y_true)
    saida = np.empty(n_reamostras)
    for i in range(n_reamostras):
        idx = rng.integers(0, n, n)
        # reamostras degeneradas (uma só classe) quebram kappa e f1 — descarta
        if len(np.unique(y_true[idx])) < 2:
            saida[i] = np.nan
            continue
        saida[i] = metrica(y_true[idx], y_pred[idx])
    return saida[~np.isnan(saida)]


def teste_z(dist_a: np.ndarray, dist_b: np.ndarray) -> tuple[float, float]:
    """Teste Z sobre duas distribuições empíricas reamostradas.

    Pelo teorema do limite central, as estatísticas reamostradas tendem à
    gaussiana, o que autoriza o teste Z sobre a distribuição empírica.
        H0: não existe diferença estatística entre as métricas dos modelos
        H1: existe diferença
    """
    z = (dist_a.mean() - dist_b.mean()) / np.sqrt(dist_a.var() + dist_b.var())
    p = 2 * (1 - stats.norm.cdf(abs(z)))
    return float(z), float(p)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--predicoes", type=Path, required=True,
                   help="CSV com uma coluna de rótulo humano e uma coluna de "
                        "predição por modelo comparado")
    p.add_argument("--col-verdade", default="rotulo_humano")
    p.add_argument("--modelos", nargs="+", required=True,
                   help="Nomes das colunas de predição (ex.: pred_finbert "
                        "pred_bertimbau_large pred_albertina)")
    p.add_argument("--saida", type=Path,
                   default=Path("conjunto_ouro/bootstrap_encoders.json"))
    args = p.parse_args()

    df = pd.read_csv(args.predicoes).dropna(subset=[args.col_verdade, *args.modelos])
    y_true = df[args.col_verdade].to_numpy()
    print(f"n = {len(df)} itens avaliados\n")

    resultados: dict = {"data": date.today().isoformat(), "n": len(df),
                        "n_reamostras": N_REAMOSTRAS, "ic": IC, "modelos": {}}
    distribuicoes: dict = {}

    # ─── Intervalos de confiança por modelo ─────────────────────────────────
    for nome_metrica, fn in METRICAS.items():
        print(f"── {nome_metrica} ──")
        for modelo in args.modelos:
            dist = bootstrap_metrica(y_true, df[modelo].to_numpy(), fn)
            distribuicoes[(nome_metrica, modelo)] = dist
            inf, sup = np.percentile(dist, [(100 - IC) / 2, 100 - (100 - IC) / 2])
            print(f"  {modelo:28s} {dist.mean():.4f}  "
                  f"IC{IC}% = [{inf:.4f}, {sup:.4f}]")
            resultados["modelos"].setdefault(modelo, {})[nome_metrica] = {
                "media": round(float(dist.mean()), 4),
                "ic_inf": round(float(inf), 4),
                "ic_sup": round(float(sup), 4),
            }
        print()

    # ─── Testes Z par a par ─────────────────────────────────────────────────
    resultados["testes_z"] = []
    print("── Testes Z (H0: não há diferença) ──")
    for nome_metrica in METRICAS:
        for a, b in combinations(args.modelos, 2):
            z, pval = teste_z(distribuicoes[(nome_metrica, a)],
                              distribuicoes[(nome_metrica, b)])
            sobrepoe = not (
                resultados["modelos"][a][nome_metrica]["ic_sup"]
                < resultados["modelos"][b][nome_metrica]["ic_inf"]
                or resultados["modelos"][b][nome_metrica]["ic_sup"]
                < resultados["modelos"][a][nome_metrica]["ic_inf"])
            veredito = ("DIFERENÇA NÃO SIGNIFICATIVA" if pval >= 0.05
                        else "diferença significativa")
            print(f"  [{nome_metrica:9s}] {a} × {b}: z={z:+.3f} p={pval:.4g} "
                  f"| ICs {'SE SOBREPÕEM' if sobrepoe else 'não se sobrepõem'} "
                  f"→ {veredito}")
            resultados["testes_z"].append({
                "metrica": nome_metrica, "modelo_a": a, "modelo_b": b,
                "z": round(z, 4), "p_valor": float(pval),
                "ics_se_sobrepoem": bool(sobrepoe),
                "significativo_5pct": bool(pval < 0.05),
            })

    args.saida.parent.mkdir(parents=True, exist_ok=True)
    args.saida.write_text(json.dumps(resultados, indent=2, ensure_ascii=False),
                          encoding="utf-8")
    print(f"\n✓ Salvo em {args.saida}")
    print("\nComo reportar na dissertação: seguir Santos (2022, Seção 4.2.4) — "
          f"informar média, IC{IC}% e o p-valor do teste Z, e afirmar "
          "superioridade APENAS quando os intervalos não se sobrepuserem.")


if __name__ == "__main__":
    main()
