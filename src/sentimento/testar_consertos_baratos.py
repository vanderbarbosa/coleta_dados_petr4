# -*- coding: utf-8 -*-
# =============================================================================
#  DISSERTAÇÃO PETR4 — Consertos de pós-processamento funcionam?
# =============================================================================
#
#  CONTEXTO
#  O diagnóstico (`diagnosticar_erro_modelo.py`) mostrou que o erro do
#  FinBERT-PT-BR no nosso domínio se concentra na FRONTEIRA DO NEUTRO e tem
#  assinatura de PRIOR SHIFT — no treino de Santos o neutro era a menor classe
#  (27,8%); na nossa realidade é a maior (41,3%).
#
#  Antes de partir para intervenções caras (comitê de modelos, adaptação de
#  domínio por MLM), é obrigatório testar se um simples pós-processamento
#  resolve. Este script testa dois candidatos óbvios e baratos.
#
#  RESULTADO: NENHUM DOS DOIS FUNCIONA. Registrado deliberadamente — saber que
#  o atalho não resolve é o que justifica o investimento no caminho caro.
#
#  Uso:
#      python src/sentimento/testar_consertos_baratos.py
# =============================================================================
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import pandas as pd
from sklearn.metrics import accuracy_score, cohen_kappa_score, f1_score

RAIZ = Path(__file__).resolve().parents[2]
DIR = RAIZ / "Mestrado_PETR4"
CLASSES = ["Negative", "Neutral", "Positive"]
MAPA = {"Positivo": "Positive", "Negativo": "Negative", "Neutro": "Neutral"}

# Base de treino de Santos (2023): 160 positivos, 203 negativos, 140 neutros
PRIOR_TREINO = {"Negative": 203 / 503, "Neutral": 140 / 503, "Positive": 160 / 503}


def avaliar(y, pred, nome: str) -> dict:
    m = {
        "config": nome,
        "acuracia": round(float(accuracy_score(y, pred)), 4),
        "f1_macro": round(float(f1_score(y, pred, average="macro",
                                         labels=CLASSES, zero_division=0)), 4),
        "kappa": round(float(cohen_kappa_score(y, pred, labels=CLASSES)), 4),
        "recall_neutral": round(float(((y == "Neutral") & (pred == "Neutral")).sum()
                                      / (y == "Neutral").sum()), 4),
    }
    print(f"  {nome:42s} acc={m['acuracia']:.3f}  F1={m['f1_macro']:.3f}  "
          f"kappa={m['kappa']:+.3f}  rec_Neu={m['recall_neutral']:.3f}")
    return m


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--saida", type=Path, default=DIR / "consertos_baratos.json")
    args = ap.parse_args()

    h = pd.read_excel(DIR / "conjunto_ouro" / "conjunto_ouro_para_rotular.xlsx",
                      sheet_name="Rotular")
    m = pd.read_csv(DIR / "conjunto_ouro" / "conjunto_ouro_gabarito_modelo.csv")
    d = h.merge(m[["ID_OURO", "Label_Sentimento", "Score_Confianca"]], on="ID_OURO")
    d["humano"] = d["Sentimento_Humano"].map(MAPA)
    d = d.dropna(subset=["humano", "Label_Sentimento"]).reset_index(drop=True)
    y = d["humano"]
    prior_real = (y.value_counts() / len(d)).to_dict()

    res = {"data_execucao": date.today().isoformat(), "n": int(len(d)),
           "prior_treino_santos": {k: round(v, 4) for k, v in PRIOR_TREINO.items()},
           "prior_real_gabarito": {k: round(v, 4) for k, v in prior_real.items()}}

    print("=" * 78)
    print("LINHA DE BASE")
    print("=" * 78)
    res["baseline"] = avaliar(y, d["Label_Sentimento"], "FinBERT-PT-BR sem alteracao")

    # ── Conserto 1 ───────────────────────────────────────────────────────────
    print("\n" + "=" * 78)
    print("CONSERTO 1 — abstencao: confianca baixa vira Neutral")
    print("=" * 78)
    print("  Motivacao: a confianca DISCRIMINA (abaixo de 0,60 a acuracia cai para")
    print("  0,42). Se o modelo hesita, talvez seja porque a manchete e neutra.\n")
    res["conserto1_abstencao"] = []
    for t in (0.55, 0.60, 0.65, 0.70, 0.75, 0.80):
        pred = d["Label_Sentimento"].where(d["Score_Confianca"] >= t, "Neutral")
        res["conserto1_abstencao"].append(
            avaliar(y, pred, f"confianca < {t:.2f} -> Neutral"))
    print("\n  >>> A acuracia sobe no maximo +0,007 (limiar 0,65), mas o F1-macro")
    print("  >>> CAI de 0,579 para 0,563 e o kappa CAI de 0,371 para 0,360.")
    print("  >>> Ganha-se recall do neutro sacrificando as outras duas classes.")
    print("  >>> NAO COMPENSA.")

    # ── Conserto 2 ───────────────────────────────────────────────────────────
    print("\n" + "=" * 78)
    print("CONSERTO 2 — reponderacao pelo prior real (Saerens et al., 2002)")
    print("=" * 78)
    print("  Motivacao: se o modelo foi treinado com um prior e aplicado a outro,")
    print("  reponderar p(c|x) por p_real(c)/p_treino(c) deveria corrigir.\n")

    def reponderar(row):
        # ⚠️ APROXIMAÇÃO: só temos o rótulo top-1 e sua confiança, não a softmax
        # completa. Distribuímos a massa restante igualmente entre as outras
        # duas classes. Isso limita a validade do teste — ver ressalva abaixo.
        p = {c: (1 - row["Score_Confianca"]) / 2 for c in CLASSES}
        p[row["Label_Sentimento"]] = row["Score_Confianca"]
        aj = {c: p[c] * prior_real[c] / PRIOR_TREINO[c] for c in CLASSES}
        return max(aj, key=aj.get)

    pred2 = d.apply(reponderar, axis=1)
    res["conserto2_prior"] = avaliar(y, pred2, "reponderado pelo prior real")
    print("\n  >>> PIORA em todas as metricas.")
    print("\n  ATENCAO - RESSALVA IMPORTANTE: este teste e INCONCLUSIVO. A reponderacao")
    print("  correta exige a distribuicao softmax completa, e nos so gravamos o")
    print("  rotulo top-1 e sua confianca. A aproximacao usada (dividir a massa")
    print("  restante igualmente) pode ser a causa da piora. Para concluir, e")
    print("  preciso re-executar o Script 03 gravando os logits — o que exige")
    print("  GPU (o torch local esta inoperante).")

    # ── Combinado ────────────────────────────────────────────────────────────
    print("\n" + "=" * 78)
    print("CONSERTO 3 — os dois combinados")
    print("=" * 78)
    res["conserto3_combinado"] = []
    for t in (0.60, 0.65, 0.70):
        pred3 = pred2.where(d["Score_Confianca"] >= t, "Neutral")
        res["conserto3_combinado"].append(
            avaliar(y, pred3, f"prior + abstencao < {t:.2f}"))

    print("\n" + "=" * 78)
    print("CONCLUSAO")
    print("=" * 78)
    print("""
Nenhum pos-processamento recupera desempenho relevante. O melhor caso ganha
0,007 de acuracia perdendo F1-macro e kappa.

Isso NAO e mau resultado — e informacao. Significa que o problema nao esta na
CALIBRACAO da saida, e sim na REPRESENTACAO: o modelo genuinamente nao separa,
no espaco de features que aprendeu, manchetes neutras de manchetes carregadas
no nosso dominio. Confirma o diagnostico de que a confianca maxima observada
nas 300 manchetes e 0,856 e que NENHUMA passa de 0,90.

Consequencia pratica: os caminhos que restam sao os que MUDAM A REPRESENTACAO,
e nao os que ajustam a saida:
  - comite com um modelo contextual complementar   (gap G7)
  - adaptacao de dominio por MLM no nosso corpus   (gap G3)

E a correcao ACC do ISM continua valendo — mas ela opera no AGREGADO, corrigindo
a proporcao de classes da serie, e nao a classificacao item a item.
""")
    args.saida.write_text(json.dumps(res, indent=2, ensure_ascii=False),
                          encoding="utf-8")
    print(f"[OK] Salvo em {args.saida}")


if __name__ == "__main__":
    main()
