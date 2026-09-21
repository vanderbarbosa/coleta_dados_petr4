# -*- coding: utf-8 -*-
# ==============================================================================
#   DIAGNÓSTICO DO MODELO — o que o texto realmente acrescenta
#
#   O script 16 mostrou as notas de cada braço. Faltam três coisas que decidem
#   se o resultado significa alguma coisa:
#
#   1. A AUC do texto (0,624) está mesmo acima de 0,5, ou é ruído? Intervalo
#      de confiança por reamostragem.
#   2. O que acontece NA PRÁTICA quando o modelo aponta uma noite de risco?
#      A AUC é abstrata; o ganho no decil de maior probabilidade não é.
#   3. Quais colunas o modelo de fato usou — o encoder entrou ou foi ignorado?
#
#   Saída: dados/diagnostico_ml.json
# ==============================================================================
from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score

warnings.filterwarnings("ignore")

AQUI = Path(__file__).resolve().parent
DADOS = AQUI / "dados"
N_PCA, TESTE, MIN_TREINO = 16, 250, 500
RNG = np.random.default_rng(42)


def roda(d: pd.DataFrame, cols: list[str], alvo: str, emb: list[str]):
    """Devolve (real, probabilidade) fora da amostra, e a importância média."""
    d = d[d[alvo].notna()].reset_index(drop=True)
    usa = [c for c in cols if c in d.columns]
    real, prob, imps = [], [], []
    ini = MIN_TREINO
    while ini < len(d):
        fim = min(ini + TESTE, len(d))
        tr, te = d.iloc[:ini], d.iloc[ini:fim]
        if te.empty or tr[alvo].nunique() < 2:
            ini = fim
            continue
        Xtr, Xte = tr[usa].copy(), te[usa].copy()
        nomes = list(usa)
        if emb:
            p = PCA(n_components=min(N_PCA, len(emb), len(tr) - 1),
                    random_state=42).fit(tr[emb].fillna(0.0).values)
            for i, v in enumerate(p.transform(tr[emb].fillna(0.0).values).T):
                Xtr[f"pc{i}"] = v
            for i, v in enumerate(p.transform(te[emb].fillna(0.0).values).T):
                Xte[f"pc{i}"] = v
            nomes += [f"pc{i}" for i in range(p.n_components_)]
        med = Xtr.median(numeric_only=True)
        Xtr, Xte = Xtr.fillna(med).fillna(0.0), Xte.fillna(med).fillna(0.0)
        m = RandomForestClassifier(n_estimators=400, min_samples_leaf=20,
                                   max_features="sqrt", random_state=42,
                                   n_jobs=-1).fit(Xtr, tr[alvo].astype(int))
        real += list(te[alvo].astype(int))
        prob += list(m.predict_proba(Xte)[:, 1])
        imps.append(pd.Series(m.feature_importances_, index=nomes))
        ini = fim
    return np.array(real), np.array(prob), pd.concat(imps, axis=1).mean(axis=1)


def auc_ic(y, p, b=2000) -> dict:
    """Intervalo de confiança da AUC por reamostragem."""
    a = roc_auc_score(y, p)
    n = len(y)
    bs = []
    for _ in range(b):
        i = RNG.integers(0, n, n)
        if len(np.unique(y[i])) < 2:
            continue
        bs.append(roc_auc_score(y[i], p[i]))
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return {"auc": round(float(a), 4), "ic95": [round(float(lo), 4), round(float(hi), 4)],
            "acima_de_0.5": bool(lo > 0.5)}


def lift(y, p, frac=0.10) -> dict:
    """Se o modelo apontar as noites de maior risco, quantas acerta?"""
    k = max(int(len(p) * frac), 20)
    top = np.argsort(-p)[:k]
    taxa, base = y[top].mean(), y.mean()
    return {"noites_apontadas": int(k), "taxa_no_topo": round(float(taxa), 4),
            "taxa_base": round(float(base), 4),
            "lift": round(float(taxa / base), 3) if base else None}


def main() -> None:
    d = pd.read_csv(DADOS / "painel_ml.csv", parse_dates=["Data"])
    C = {p: [c for c in d.columns if c.startswith(p)]
         for p in ["m_", "nt_", "cv_", "emb"]}

    BRACOS = {
        "só mercado (sem texto)": (C["m_"], []),
        "só texto (notícia + CVM + embedding)": (C["nt_"] + C["cv_"], C["emb"]),
        "mercado + texto + embedding": (C["m_"] + C["nt_"] + C["cv_"], C["emb"]),
    }

    print("=" * 88)
    print("  DIAGNÓSTICO — DIA EXCEPCIONAL (os 10% de pregões mais agitados)")
    print("=" * 88)

    res, guardados = {}, {}
    for nome, (cols, emb) in BRACOS.items():
        y, p, imp = roda(d, cols, "alvo_ext", emb)
        guardados[nome] = (y, p)
        res[nome] = {**auc_ic(y, p), "lift_top10": lift(y, p),
                     "n": int(len(y))}
        a = res[nome]
        L = a["lift_top10"]
        print(f"\n  {nome}")
        print(f"    AUC ....................... {a['auc']:.3f}  "
              f"(IC 95%: {a['ic95'][0]:.3f} a {a['ic95'][1]:.3f})"
              + ("  ACIMA DO ACASO" if a["acima_de_0.5"] else "  NAO PASSA"))
        print(f"    nas {L['noites_apontadas']} noites de maior risco apontadas:")
        print(f"      dias excepcionais ....... {L['taxa_no_topo']:.1%}  "
              f"(base {L['taxa_base']:.1%})   ganho de {L['lift']:.2f}x")
        if nome.startswith("mercado + texto"):
            res[nome]["importancias"] = {
                "mercado": round(float(imp[[i for i in imp.index
                                            if i.startswith("m_")]].sum()), 4),
                "notícia": round(float(imp[[i for i in imp.index
                                            if i.startswith("nt_")]].sum()), 4),
                "CVM (rótulos)": round(float(imp[[i for i in imp.index
                                                  if i.startswith("cv_")]].sum()), 4),
                "embedding": round(float(imp[[i for i in imp.index
                                              if i.startswith("pc")]].sum()), 4),
            }
            print("\n    de onde o modelo tirou a decisão:")
            for k, v in sorted(res[nome]["importancias"].items(),
                               key=lambda kv: -kv[1]):
                print(f"      {k:<18} {v:>6.1%}")
            print("\n    as 12 colunas mais usadas:")
            for k, v in imp.sort_values(ascending=False).head(12).items():
                print(f"      {k:<28} {v:>6.2%}")
            res[nome]["top_colunas"] = {str(k): round(float(v), 5)
                                        for k, v in imp.sort_values(
                                            ascending=False).head(15).items()}

    # ── o texto acrescenta ao mercado? diferença de AUC, com reamostragem ────
    ym, pm = guardados["só mercado (sem texto)"]
    yt, pt = guardados["mercado + texto + embedding"]
    dif = [roc_auc_score(yt[i], pt[i]) - roc_auc_score(ym[i], pm[i])
           for i in (RNG.integers(0, len(ym), len(ym)) for _ in range(2000))
           if len(np.unique(ym[i])) > 1]
    lo, hi = np.percentile(dif, [2.5, 97.5])
    res["texto_acrescenta_ao_mercado"] = {
        "diferenca_auc": round(float(np.mean(dif)), 4),
        "ic95": [round(float(lo), 4), round(float(hi), 4)],
        "acrescenta": bool(lo > 0)}
    print("\n" + "=" * 88)
    print("  O TEXTO ACRESCENTA AO QUE O PREÇO JÁ DIZIA?")
    print("=" * 88)
    print(f"\n  diferença de AUC: {np.mean(dif):+.4f}  "
          f"(IC 95%: {lo:+.4f} a {hi:+.4f})")
    print("  " + ("ACRESCENTA" if lo > 0 else
                  "NÃO ACRESCENTA — o intervalo inclui o zero"))

    (DADOS / "diagnostico_ml.json").write_text(
        json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n  gravado: dados/diagnostico_ml.json")


if __name__ == "__main__":
    main()
