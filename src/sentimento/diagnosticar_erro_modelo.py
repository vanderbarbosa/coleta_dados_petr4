# -*- coding: utf-8 -*-
# =============================================================================
#  DISSERTAÇÃO PETR4 — De onde vem o erro do classificador?
# =============================================================================
#
#  A PERGUNTA
#  Se todos os trabalhos usam o FinBERT-PT-BR sem alterá-lo, por que o nosso
#  desempenho (0,58 / kappa 0,371) parece baixo?
#
#  Este script decompõe o erro em fatores mensuráveis, em vez de especular.
#  Cada bloco testa uma hipótese concreta sobre a origem da diferença entre os
#  0,76 relatados por Santos (2023) e os 0,58 que medimos.
#
#  HIPÓTESES TESTADAS
#    H1. "Santos descartou os casos difíceis"    -> filtrar por confiança
#    H2. "O problema é o recorte por ativo"      -> comparar relevantes/não
#    H3. "Algumas categorias são intratáveis"    -> quebrar por categoria
#    H4. "O problema é a fronteira do NEUTRO"    -> avaliar só polaridade
#    H5. "Manchete longa confunde o modelo"      -> quebrar por comprimento
#    H6. "O modelo sabe que não sabe"            -> calibração da confiança
#    H7. "Mudou a distribuição de classes"       -> prior shift vs. Santos
#
#  Uso:
#      python src/sentimento/diagnosticar_erro_modelo.py
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
MAPA = {"Positivo": "Positive", "Negativo": "Negative", "Neutro": "Neutral"}

# Distribuição da base de treino de Santos (2023): 160 pos, 203 neg, 140 neu
TREINO_SANTOS = {"Positive": 160, "Negative": 203, "Neutral": 140}


def metricas(sub: pd.DataFrame) -> dict | None:
    """Acurácia, F1-macro e kappa de um recorte. None se for pequeno demais."""
    if len(sub) < 15:
        return None
    y, p = sub["humano"], sub["predito"]
    return {
        "n": int(len(sub)),
        "acuracia": round(float(accuracy_score(y, p)), 4),
        "f1_macro": round(float(f1_score(y, p, average="macro",
                                         labels=CLASSES, zero_division=0)), 4),
        "kappa": round(float(cohen_kappa_score(y, p, labels=CLASSES)), 4),
    }


def linha(rotulo: str, m: dict | None) -> None:
    if m is None:
        print(f"  {rotulo:34s} (n < 15, omitido)")
        return
    print(f"  {rotulo:34s} n={m['n']:3d}  acc={m['acuracia']:.3f}  "
          f"F1={m['f1_macro']:.3f}  kappa={m['kappa']:+.3f}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--saida", type=Path, default=DIR / "diagnostico_erro_modelo.json")
    args = ap.parse_args()

    h = pd.read_excel(DIR / "conjunto_ouro" / "conjunto_ouro_para_rotular.xlsx",
                      sheet_name="Rotular")
    m = pd.read_csv(DIR / "conjunto_ouro" / "conjunto_ouro_gabarito_modelo.csv")
    d = h.merge(m[["ID_OURO", "Label_Sentimento", "Score_Confianca"]], on="ID_OURO")
    d["humano"] = d["Sentimento_Humano"].map(MAPA)
    d = d.rename(columns={"Label_Sentimento": "predito"})
    d = d.dropna(subset=["humano", "predito"])
    d["acertou"] = d["humano"] == d["predito"]
    d["n_pal"] = d["Título"].astype(str).str.split().str.len()

    rel: dict = {"data_execucao": date.today().isoformat(), "n": int(len(d))}

    # ── referências ──────────────────────────────────────────────────────────
    base_maioria = d["humano"].value_counts().iloc[0] / len(d)
    geral = metricas(d)
    print("=" * 76)
    print("REFERENCIAS")
    print("=" * 76)
    linha("nosso resultado (300 manchetes)", geral)
    print(f"  {'acaso (3 classes)':34s}      acc=0.333")
    print(f"  {'baseline: sempre a classe maior':34s}      acc={base_maioria:.3f}"
          f"   (Neutral, {d['humano'].value_counts().iloc[0]}/{len(d)})")
    print(f"  {'Santos (2023), noticias gerais':34s}      acc=0.760  F1=0.730")
    print(f"\n  >>> ganho sobre o baseline de maioria: "
          f"{geral['acuracia'] - base_maioria:+.3f}")
    rel["referencias"] = {"geral": geral, "baseline_maioria": round(base_maioria, 4),
                          "acaso": 0.333, "santos_2023": {"acuracia": 0.76, "f1": 0.73}}

    # ── H1 ───────────────────────────────────────────────────────────────────
    print("\n" + "=" * 76)
    print("H1. Santos descartou 49,7% dos casos por discordancia — o filtro explica?")
    print("=" * 76)
    rel["h1_confianca"] = {}
    for c in ["Alta", "Média", "Baixa"]:
        mm = metricas(d[d["Confianca_Rotulador"] == c])
        linha(f"confianca do anotador = {c}", mm)
        rel["h1_confianca"][c] = mm
    alta = metricas(d[d["Confianca_Rotulador"] == "Alta"])
    print(f"\n  >>> ganho ao manter so os faceis: "
          f"{alta['acuracia'] - geral['acuracia']:+.3f}  -> NAO explica a diferenca.")

    # ── H2 ───────────────────────────────────────────────────────────────────
    print("\n" + "=" * 76)
    print("H2. O recorte por ativo unico explica?")
    print("=" * 76)
    rel["h2_relevancia"] = {}
    for r in ["Sim", "Não"]:
        mm = metricas(d[d["Relevante_PETR4"] == r])
        linha(f"relevante para PETR4 = {r}", mm)
        rel["h2_relevancia"][r] = mm
    print("\n  >>> praticamente identicas -> NAO explica a diferenca.")

    # ── H3 ───────────────────────────────────────────────────────────────────
    print("\n" + "=" * 76)
    print("H3. Alguma categoria e especialmente dificil?")
    print("=" * 76)
    rel["h3_categoria"] = {}
    for cat, g in sorted(d.groupby("Categoria"),
                         key=lambda kv: -(metricas(kv[1])["acuracia"]
                                          if metricas(kv[1]) else 0)):
        mm = metricas(g)
        linha(cat, mm)
        if mm:
            rel["h3_categoria"][cat] = mm
    print("\n  >>> a dispersao entre categorias e grande: geopolitica e o pior caso.")

    # ── H4 ───────────────────────────────────────────────────────────────────
    print("\n" + "=" * 76)
    print("H4. O problema e a fronteira do NEUTRO?")
    print("=" * 76)
    print("\n  Recall por classe verdadeira:")
    rel["h4_por_classe"] = {}
    for c in CLASSES:
        sub = d[d["humano"] == c]
        rec = float((sub["predito"] == c).mean())
        pred = d[d["predito"] == c]
        prec = float((pred["humano"] == c).mean()) if len(pred) else np.nan
        print(f"    {c:10s} n={len(sub):3d}  recall={rec:.3f}   precision={prec:.3f}")
        rel["h4_por_classe"][c] = {"n": int(len(sub)), "recall": round(rec, 4),
                                   "precision": round(prec, 4)}

    pol = d[(d["humano"] != "Neutral") & (d["predito"] != "Neutral")]
    acc_pol = float(accuracy_score(pol["humano"], pol["predito"]))
    k_pol = float(cohen_kappa_score(pol["humano"], pol["predito"],
                                    labels=["Negative", "Positive"]))
    print(f"\n  Descartando o NEUTRO dos dois lados (so Positivo x Negativo):")
    print(f"    n={len(pol)}  acc={acc_pol:.3f}  kappa={k_pol:+.3f}")
    print(f"\n  >>> salto de {geral['acuracia']:.3f} para {acc_pol:.3f} "
          f"({acc_pol - geral['acuracia']:+.3f}).")
    print("  >>> O modelo distingue POSITIVO de NEGATIVO razoavelmente bem.")
    print("  >>> O que ele nao consegue e decidir se algo e NEUTRO.")
    rel["h4_polaridade"] = {"n": int(len(pol)), "acuracia": round(acc_pol, 4),
                            "kappa": round(k_pol, 4)}

    erros = d[~d["acertou"]]
    env = erros.groupby(["humano", "predito"]).size().sort_values(ascending=False)
    com_neutro = int(sum(v for (a, b), v in env.items()
                         if "Neutral" in (a, b)))
    print(f"\n  Dos {len(erros)} erros, {com_neutro} ({com_neutro / len(erros):.0%}) "
          f"envolvem a classe Neutral.")
    print("  Principais confusoes:")
    for (a, b), v in env.head(4).items():
        print(f"    humano={a:9s} -> modelo={b:9s}  {v:3d}")
    rel["h4_erros"] = {"total": int(len(erros)), "envolvendo_neutral": com_neutro}

    # ── H5 ───────────────────────────────────────────────────────────────────
    print("\n" + "=" * 76)
    print("H5. Manchete longa atrapalha?")
    print("=" * 76)
    faixas = pd.cut(d["n_pal"], [0, 8, 11, 14, 100])
    tab = d.groupby(faixas, observed=True)["acertou"].agg(["size", "mean"]).round(3)
    print()
    print(tab.to_string())
    print(f"\n  mediana de palavras por manchete: {d['n_pal'].median():.0f}")
    print("  >>> ha degradacao com o comprimento, mas pode ser confundida com o")
    print("  >>> tema: manchetes longas tendem a tratar assuntos mais complexos.")
    rel["h5_comprimento"] = {str(k): {"n": int(v["size"]), "acuracia": float(v["mean"])}
                             for k, v in tab.iterrows()}

    # ── H6 ───────────────────────────────────────────────────────────────────
    print("\n" + "=" * 76)
    print("H6. O modelo sabe que nao sabe? (calibracao da confianca)")
    print("=" * 76)
    fx = pd.cut(d["Score_Confianca"], [0, .6, .8, .9, 1.0])
    tabc = d.groupby(fx, observed=True)["acertou"].agg(["size", "mean"]).round(3)
    print()
    print(tabc.to_string())
    print(f"\n  Score_Confianca: media={d['Score_Confianca'].mean():.3f}  "
          f"mediana={d['Score_Confianca'].median():.3f}  "
          f"maximo={d['Score_Confianca'].max():.3f}")
    acima90 = int((d["Score_Confianca"] > 0.9).sum())
    print(f"  Manchetes com confianca > 0,90: {acima90} de {len(d)}")
    print("  >>> a confianca DISCRIMINA (baixa confianca = mais erro), o que e bom:")
    print("  >>> da para usar limiar. Mas o modelo quase nunca fica muito confiante")
    print("  >>> neste dominio — sinal de incompatibilidade, nao de aleatoriedade.")
    rel["h6_calibracao"] = {
        "media": round(float(d["Score_Confianca"].mean()), 4),
        "mediana": round(float(d["Score_Confianca"].median()), 4),
        "maximo": round(float(d["Score_Confianca"].max()), 4),
        "n_acima_090": acima90,
        "faixas": {str(k): {"n": int(v["size"]), "acuracia": float(v["mean"])}
                   for k, v in tabc.iterrows()},
    }

    # ── H7 ───────────────────────────────────────────────────────────────────
    print("\n" + "=" * 76)
    print("H7. A distribuicao de classes mudou? (prior shift)")
    print("=" * 76)
    tot_s = sum(TREINO_SANTOS.values())
    nossa = d["humano"].value_counts()
    predita = d["predito"].value_counts()
    print(f"\n  {'classe':<12}{'treino Santos':>16}{'nossa realidade':>18}{'o modelo prediz':>18}")
    rel["h7_prior_shift"] = {}
    for c in CLASSES:
        ps, pn, pp = TREINO_SANTOS[c] / tot_s, nossa[c] / len(d), predita.get(c, 0) / len(d)
        print(f"  {c:<12}{ps:>15.1%}{pn:>18.1%}{pp:>18.1%}")
        rel["h7_prior_shift"][c] = {"treino_santos": round(ps, 4),
                                    "nossa_realidade": round(pn, 4),
                                    "modelo_prediz": round(pp, 4)}
    print("\n  >>> No treino de Santos, NEUTRO era a MENOR classe (27,8%).")
    print("  >>> Na nossa realidade, NEUTRO e a MAIOR (41,3%).")
    print("  >>> O modelo aprendeu a ser decidido; nosso corpus pede prudencia.")
    print("  >>> Isto e prior shift — e e exatamente o que a correcao ACC trata")
    print("  >>> (ver calibrar_ism_com_gabarito.py).")

    args.saida.write_text(json.dumps(rel, indent=2, ensure_ascii=False, default=float),
                          encoding="utf-8")
    print(f"\n[OK] Salvo em {args.saida}")


if __name__ == "__main__":
    main()
