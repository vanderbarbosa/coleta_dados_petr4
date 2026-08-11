# -*- coding: utf-8 -*-
# =============================================================================
#  Máquina de Comitê para sentimento financeiro PT-BR — gap G7
#  Baseado em Błoch, Santana e Amantino (2026)
# =============================================================================
#
#  ⚠️  ORIGEM: reconstrução. Błoch et al. (2026) não publicaram código. O método
#  foi reconstruído a partir da Seção 4 do artigo, que descreve a arquitetura de
#  Máquina de Comitê e o critério de seleção dos membros:
#
#    "é essencial a seleção de modelos de análise de sentimentos que tenham
#     características distintas e complementares. Os modelos que selecionamos se
#     enquadram nesse requisito, pois um deles — treinado em uma base financeira
#     (Santos; Bianchi; Costa, 2023) — mostra resultados fortemente influenciados
#     pela presença de termos negativos ou positivos, enquanto o segundo —
#     treinado em uma base mais geral com conteúdo em português (Pérez et al.,
#     2021) — analisa mais o contexto em que os termos aparecem."
#
#  ---------------------------------------------------------------------------
#  POR QUE ISTO EXISTE
#  A nossa matriz de confusão contra o conjunto-ouro mostra que a classe NEUTRA
#  é a mais confundida: 58 dos 124 casos neutros (46,8%) foram para os extremos.
#  Essa é exatamente a assinatura de um modelo dominado por léxico — o que a
#  caracterização de Błoch et al. prevê. O comitê acrescenta um membro
#  CONTEXTUAL para corrigir precisamente essa fraqueza.
#
#  HIPÓTESE A REGISTRAR ANTES DE RODAR:
#  se o diagnóstico estiver correto, a regra de ABSTENÇÃO deve produzir o maior
#  ganho na classe Neutra. Confirmar isso é um resultado explicativo, e não
#  apenas uma melhoria numérica.
#
#  NÃO CONSOME ROTULAGEM NOVA — usa o conjunto-ouro de 300 manchetes que já
#  existe. Compatível com a suspensão da rotulagem (mentoria 29/07/2026).
#
#  MELHORIA SOBRE O TRABALHO ORIGINAL: Błoch et al. usaram o comitê mas NÃO
#  mediram o ganho contra os membros isolados. Este script mede.
#
#  Dependências:  pip install transformers pysentimiento torch scikit-learn
# =============================================================================
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (accuracy_score, classification_report,
                             cohen_kappa_score, confusion_matrix, f1_score)

CLASSES = ["Negative", "Neutral", "Positive"]

# FinBERT-PT-BR: id2label = {0: POSITIVE, 1: NEGATIVE, 2: NEUTRAL} — ordem
# contraintuitiva, conferir sempre (ver 01_SANTOS, Seção 7.3)
MAPA_FINBERT = {"POSITIVE": "Positive", "NEGATIVE": "Negative", "NEUTRAL": "Neutral"}
# pysentimiento: POS / NEU / NEG
MAPA_PYSENT = {"POS": "Positive", "NEU": "Neutral", "NEG": "Negative"}


def carregar_membros():
    """Instancia os dois membros do comitê: um léxico-financeiro, um contextual."""
    from pysentimiento import create_analyzer
    from transformers import pipeline

    finbert = pipeline("text-classification", model="lucas-leme/FinBERT-PT-BR",
                       truncation=True, max_length=512, top_k=None)

    # Verificação defensiva: se o config do modelo mudar, falhar alto em vez de
    # inverter o sinal em silêncio
    id2label = {int(k): v for k, v in finbert.model.config.id2label.items()}
    esperado = {0: "POSITIVE", 1: "NEGATIVE", 2: "NEUTRAL"}
    if id2label != esperado:
        raise RuntimeError(f"Mapeamento de rótulos mudou! obtido={id2label}")

    geral = create_analyzer(task="sentiment", lang="pt")
    return finbert, geral


def prob_dict(saida_pipeline) -> dict[str, float]:
    """Converte a saída do pipeline (top_k=None) em {classe canônica: prob}."""
    return {MAPA_FINBERT[d["label"]]: d["score"] for d in saida_pipeline}


def moderar(p_fin: dict, p_ger: dict, regra: str) -> str:
    """Aplica a regra de moderação do comitê.

    Błoch et al. usaram voto simples, mas com apenas dois membros a regra de
    desempate não é detalhada no artigo. Implementamos três variantes para
    comparação — isso é uma melhoria sobre o trabalho original.
    """
    a = max(p_fin, key=p_fin.get)
    b = max(p_ger, key=p_ger.get)

    if a == b:
        return a

    if regra == "voto":
        # empate 1×1 → prevalece o modelo de domínio
        return a
    if regra == "abstencao":
        # discordância → neutro. Conservadora: tende a corrigir o excesso de
        # extremos do membro léxico, que é a nossa fraqueza medida.
        return "Neutral"
    if regra == "media_prob":
        soma = {c: p_fin.get(c, 0.0) + p_ger.get(c, 0.0) for c in CLASSES}
        return max(soma, key=soma.get)
    raise ValueError(f"Regra desconhecida: {regra}")


def avaliar(y_true, y_pred, nome: str) -> dict:
    """Métricas + matriz de confusão, no mesmo formato do nosso relatório."""
    m = {
        "modelo": nome,
        "acuracia": round(float(accuracy_score(y_true, y_pred)), 4),
        "f1_macro": round(float(f1_score(y_true, y_pred, average="macro",
                                         labels=CLASSES, zero_division=0)), 4),
        "kappa": round(float(cohen_kappa_score(y_true, y_pred, labels=CLASSES)), 4),
    }
    cm = confusion_matrix(y_true, y_pred, labels=CLASSES)
    m["matriz_confusao"] = cm.tolist()
    # recall da classe Neutra — a métrica-chave da nossa hipótese
    i_neu = CLASSES.index("Neutral")
    total_neu = cm[i_neu].sum()
    m["recall_neutral"] = round(float(cm[i_neu, i_neu] / total_neu), 4) if total_neu else None
    return m


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--gabarito", type=Path, required=True,
                   help="CSV do conjunto-ouro")
    p.add_argument("--col-texto", default="titulo")
    p.add_argument("--col-rotulo", default="rotulo_humano")
    p.add_argument("--saida", type=Path,
                   default=Path("conjunto_ouro/resultado_comite.json"))
    args = p.parse_args()

    df = pd.read_csv(args.gabarito).dropna(subset=[args.col_texto, args.col_rotulo])
    df = df[df[args.col_rotulo].isin(CLASSES)].reset_index(drop=True)
    textos = df[args.col_texto].astype(str).tolist()
    y_true = df[args.col_rotulo].tolist()
    print(f"Conjunto-ouro: {len(textos)} manchetes")
    print(f"Distribuição : {pd.Series(y_true).value_counts().to_dict()}\n")

    finbert, geral = carregar_membros()

    print("Classificando com o membro léxico-financeiro (FinBERT-PT-BR)...")
    probs_fin = [prob_dict(s) for s in finbert(textos, batch_size=16)]

    print("Classificando com o membro contextual (pysentimiento PT)...")
    probs_ger = [{MAPA_PYSENT[k]: v for k, v in r.probas.items()}
                 for r in geral.predict(textos)]

    resultados = []
    # membros isolados — é a medição que Błoch et al. NÃO fizeram
    resultados.append(avaliar(y_true, [max(p, key=p.get) for p in probs_fin],
                              "FinBERT-PT-BR (isolado)"))
    resultados.append(avaliar(y_true, [max(p, key=p.get) for p in probs_ger],
                              "pysentimiento PT (isolado)"))
    # comitê, nas três regras
    for regra in ("voto", "abstencao", "media_prob"):
        pred = [moderar(a, b, regra) for a, b in zip(probs_fin, probs_ger)]
        resultados.append(avaliar(y_true, pred, f"Comitê ({regra})"))

    print(f"\n{'Modelo':32s} {'Acur.':>7s} {'F1-mac':>7s} {'Kappa':>7s} {'Rec.Neu':>8s}")
    print("-" * 66)
    for r in resultados:
        print(f"{r['modelo']:32s} {r['acuracia']:7.4f} {r['f1_macro']:7.4f} "
              f"{r['kappa']:7.4f} {r['recall_neutral']:8.4f}")

    base = resultados[0]
    melhor = max(resultados[2:], key=lambda r: r["f1_macro"])
    print(f"\nMelhor comitê: {melhor['modelo']}")
    print(f"  Δ F1-macro vs. FinBERT isolado ....... "
          f"{melhor['f1_macro'] - base['f1_macro']:+.4f}")
    print(f"  Δ recall da classe Neutra ............ "
          f"{melhor['recall_neutral'] - base['recall_neutral']:+.4f}")
    print("\n(Confirmar a significância com reconstrucao_santos_bootstrap.py "
          "antes de reportar qualquer superioridade.)")

    args.saida.parent.mkdir(parents=True, exist_ok=True)
    args.saida.write_text(json.dumps({
        "data": date.today().isoformat(),
        "n": len(textos),
        "membros": {"lexico_financeiro": "lucas-leme/FinBERT-PT-BR",
                    "contextual_geral": "pysentimiento/bertweet-pt-sentiment"},
        "referencia_metodo": "Błoch, Santana e Amantino (2026)",
        "classes": CLASSES,
        "resultados": resultados,
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n✓ Salvo em {args.saida}")


if __name__ == "__main__":
    main()
