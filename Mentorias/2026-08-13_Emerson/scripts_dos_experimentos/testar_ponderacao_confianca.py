# -*- coding: utf-8 -*-
# =============================================================================
#  DISSERTAÇÃO PETR4 — A ponderação por confiança realmente ajuda?
# =============================================================================
#
#  ------------------------------------------------------------------
#  DE ONDE VEM A PERGUNTA
#  ------------------------------------------------------------------
#  A dissertação sustenta, com base na suíte de refinamento, que ponderar o
#  sentimento pela confiança do classificador eleva a acurácia de 50,30% para
#  54,93%, e conclui que "o sinal preditivo está na intensidade e na certeza
#  da classificação, e não na contagem de manchetes".
#
#  Duas circunstâncias recomendam reexaminar essa conclusão:
#
#  1. Aquela medição é anterior aos testes mais rigorosos hoje disponíveis
#     (correlação com a volatilidade, auditoria por pregão, efeito de cauda).
#
#  2. Descobriu-se depois que a confiança publicada pelo artefato NÃO é a
#     probabilidade softmax, e sim uma sigmoide — consequência do
#     `problem_type: multi_label_classification` declarado na configuração.
#     Ou seja: o peso usado está na escala errada. Se a ponderação de fato
#     carrega o ganho, então corrigir a escala importa muito; se não carrega,
#     a correção é irrelevante e a conclusão da dissertação precisa mudar.
#
#  ------------------------------------------------------------------
#  O QUE SE TESTA
#  ------------------------------------------------------------------
#  Quatro formas de converter o rótulo de cada notícia em número:
#
#    A — ponderada pela confiança      polaridade x confianca   (a atual)
#    B — polaridade pura               +1, 0, -1                (sem peso)
#    C — só as de alta confiança       polaridade, se conf > mediana
#    D — saldo de votos                (n_pos - n_neg) / n_total
#
#  Se a tese da ponderação estiver correta, A deve superar B de forma
#  detectável. Se A e B forem indistinguíveis, o ganho atribuído à ponderação
#  era ruído — e a escala errada da sigmoide deixa de ser problema.
#
#  Uso:
#      python src/sentimento/testar_ponderacao_confianca.py
# =============================================================================
from __future__ import annotations

import argparse
import json
import warnings
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")

RAIZ = Path(__file__).resolve().parents[2]
DIR = RAIZ / "Mestrado_PETR4"
N_BOOT = 10_000
POLARIDADE = {"Positive": 1.0, "Neutral": 0.0, "Negative": -1.0}


def carregar():
    n = pd.read_csv(DIR / "noticias_com_sentimento.csv",
                    usecols=["Data_Coleta", "Data_Ajustada", "categoria",
                             "Label_Sentimento", "Score_Confianca",
                             "Indice_Sentimento"])
    n["dia"] = pd.to_datetime(n["Data_Ajustada"], errors="coerce")
    n["hora"] = pd.to_datetime(n["Data_Coleta"], errors="coerce").dt.hour
    n = n.dropna(subset=["dia", "Label_Sentimento", "Score_Confianca"])
    n["pol"] = n["Label_Sentimento"].map(POLARIDADE)

    p = pd.read_csv(DIR / "base_financeira_petr4.csv", skiprows=[1])
    p["Date"] = pd.to_datetime(p["Date"], errors="coerce")
    p["Close"] = pd.to_numeric(p["Close"], errors="coerce")
    p = p.dropna(subset=["Date", "Close"]).sort_values("Date").reset_index(drop=True)
    p["ret"] = np.log(p["Close"]).diff()
    p["vol"] = p["ret"].abs()
    p["vol_prox"] = p["vol"].shift(-1)
    p["ret_prox"] = p["ret"].shift(-1)
    return n, p


def construir_variantes(n: pd.DataFrame) -> dict[str, pd.Series]:
    """Quatro agregações diárias do mesmo conjunto de rótulos."""
    lim = n["Score_Confianca"].median()
    g = n.groupby(n["dia"].dt.date)

    alta = n[n["Score_Confianca"] > lim]
    return {
        "A_ponderada_confianca": g["Indice_Sentimento"].mean(),
        "B_polaridade_pura": g["pol"].mean(),
        "C_so_alta_confianca": alta.groupby(alta["dia"].dt.date)["pol"].mean(),
        "D_saldo_de_votos": g["pol"].apply(
            lambda s: (s > 0).sum() / len(s) - (s < 0).sum() / len(s)),
    }


def bootstrap_dif(x1, x2, y, n=N_BOOT, seed=42):
    """Diferença de |r| entre duas variantes, reamostrando os MESMOS pregões."""
    rng = np.random.default_rng(seed)
    x1, x2, y = np.asarray(x1), np.asarray(x2), np.asarray(y)
    d = np.empty(n)
    for k in range(n):
        i = rng.integers(0, len(y), len(y))
        d[k] = (abs(np.corrcoef(x1[i], y[i])[0, 1])
                - abs(np.corrcoef(x2[i], y[i])[0, 1]))
    lo, hi = np.percentile(d, [2.5, 97.5])
    return float(d.mean()), float(lo), float(hi), \
        float(2 * min((d <= 0).mean(), (d >= 0).mean()))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--saida", type=Path, default=DIR / "ponderacao_confianca.json")
    ap.add_argument("--apos17h", action="store_true",
                    help="restringe ao recorte usado na suite de refinamento original")
    args = ap.parse_args()

    n, p = carregar()
    if args.apos17h:
        n = n[n["hora"] >= 17]
        print(f"[recorte APOS 17h — o mesmo da suite de refinamento original]\n")
    variantes = construir_variantes(n)

    print("=" * 78)
    print("A PONDERACAO POR CONFIANCA CARREGA O SINAL?")
    print("=" * 78)
    print(f"  noticias: {len(n):,} | mediana da confianca: "
          f"{n['Score_Confianca'].median():.4f}")

    # ── diagnóstico da escala: sigmoide ou softmax? ─────────────────────────
    #
    #  Num softmax de 3 classes, a probabilidade da classe vencedora NUNCA
    #  pode ficar abaixo de 1/3 — as três somam 1 e a maior é, no mínimo, a
    #  média. Qualquer valor abaixo disso prova que a escala não é softmax.
    abaixo = int((n["Score_Confianca"] < 1 / 3).sum())
    print(f"\n  DIAGNOSTICO DA ESCALA")
    print(f"    minimo observado ......... {n['Score_Confianca'].min():.4f}")
    print(f"    maximo observado ......... {n['Score_Confianca'].max():.4f}")
    print(f"    piso matematico do softmax  0.3333")
    print(f"    valores abaixo do piso ... {abaixo:,}")
    print(f"    -> a escala {'NAO e softmax (e sigmoide)' if abaixo else 'e compativel com softmax'}")

    d = p.set_index(p["Date"].dt.date)[["vol", "vol_prox", "ret_prox"]]
    for k, s in variantes.items():
        d = d.join(s.rename(k))
    d = d.dropna(subset=list(variantes) + ["vol_prox", "ret_prox"])
    print(f"\n  pregoes com todas as variantes: {len(d):,}")

    # ── correlação com a volatilidade ───────────────────────────────────────
    print("\n" + "=" * 78)
    print("1. ASSOCIACAO COM A VOLATILIDADE DO PREGAO SEGUINTE")
    print("=" * 78)
    print(f"  {'variante':28s}{'|r|':>10s}{'p':>12s}")
    res = {"data_execucao": date.today().isoformat(), "n_pregoes": int(len(d)),
           "escala_confianca": {
               "minimo": round(float(n["Score_Confianca"].min()), 4),
               "maximo": round(float(n["Score_Confianca"].max()), 4),
               "abaixo_do_piso_softmax": abaixo,
               "e_softmax": bool(abaixo == 0)},
           "variantes": {}}
    for k in variantes:
        r, pv = stats.pearsonr(d[k], d["vol_prox"])
        print(f"  {k:28s}{abs(r):>10.4f}{pv:>12.6f}")
        res["variantes"][k] = {"abs_r_vol": round(abs(r), 4),
                               "p_vol": round(float(pv), 8)}

    # ── a ponderação supera a polaridade pura? ──────────────────────────────
    print("\n" + "=" * 78)
    print("2. A PONDERACAO SUPERA A POLARIDADE PURA? (bootstrap pareado)")
    print("=" * 78)
    res["comparacoes"] = []
    for a, b, rot in [("A_ponderada_confianca", "B_polaridade_pura",
                       "ponderada x polaridade pura"),
                      ("C_so_alta_confianca", "B_polaridade_pura",
                       "so alta confianca x polaridade pura"),
                      ("A_ponderada_confianca", "D_saldo_de_votos",
                       "ponderada x saldo de votos")]:
        m, lo, hi, pv = bootstrap_dif(d[a], d[b], d["vol_prox"])
        sig = lo > 0 or hi < 0
        print(f"  {rot:36s} delta|r|={m:+.4f}  IC95=[{lo:+.4f},{hi:+.4f}]  "
              f"p={pv:.4f}  -> {'SIGNIFICATIVA' if sig else 'nao significativa'}")
        res["comparacoes"].append({"contraste": rot, "delta_abs_r": round(m, 4),
                                   "ic95": [round(lo, 4), round(hi, 4)],
                                   "p_valor": round(pv, 4),
                                   "significativa": bool(sig)})

    # ── quanto as variantes diferem entre si? ───────────────────────────────
    print("\n" + "=" * 78)
    print("3. AS VARIANTES SAO DE FATO DIFERENTES?")
    print("=" * 78)
    print("  Correlacao entre as series diarias (1,000 = identicas):\n")
    chaves = list(variantes)
    print("  " + " " * 28 + "".join(f"{k[:12]:>14s}" for k in chaves))
    for a in chaves:
        linha = "".join(f"{np.corrcoef(d[a], d[b])[0, 1]:>14.4f}" for b in chaves)
        print(f"  {a:28s}{linha}")

    r_ab = float(np.corrcoef(d["A_ponderada_confianca"], d["B_polaridade_pura"])[0, 1])
    res["correlacao_A_B"] = round(r_ab, 4)
    print(f"\n  A x B = {r_ab:.4f}")
    if r_ab > 0.98:
        print("  As duas series sao quase a MESMA COISA. A ponderacao redistribui")
        print("  muito pouco, e a escala da confianca torna-se irrelevante para o")
        print("  resultado agregado.")

    # ── e na acurácia direcional, que é a alegação original? ────────────────
    #
    #  A afirmação da dissertação — ponderar eleva a acurácia de 50,30% para
    #  54,93% — é sobre DIREÇÃO, não sobre volatilidade. Convém, pois, medi-la
    #  no mesmo terreno, com o XGBoost e o protocolo do Script 04, trocando
    #  apenas a forma de agregar o sentimento.
    from sklearn.metrics import accuracy_score, roc_auc_score          # noqa: E402
    from xgboost import XGBClassifier                                  # noqa: E402

    print("\n" + "=" * 78)
    print("4. E NA ACURACIA DIRECIONAL? (XGBoost, divisao cronologica 60/15/25)")
    print("=" * 78)

    b = d.copy()
    b["ret_ont"] = b["vol"].shift(1)          # marcador de escala do dia anterior
    b["vol_ont"] = b["vol"].shift(1)
    b["alvo"] = (b["ret_prox"] > 0).astype(int)
    b = b.dropna()
    n_ = len(b)
    i_tr, i_va = int(n_ * 0.60), int(n_ * 0.75)
    y = b["alvo"].to_numpy()

    print(f"  pregoes: {n_:,} | treino {i_tr} | validacao {i_va - i_tr} | "
          f"teste {n_ - i_va}")
    print(f"\n  {'variante do sentimento':28s}{'validacao':>11s}{'TESTE':>9s}{'AUC':>9s}")
    res["direcao"] = {}
    for k in variantes:
        X = b[["ret_ont", "vol_ont", k]].to_numpy()
        melhor, melhor_acc = None, -1
        for md in (3, 5):
            for lr in (0.05, 0.1):
                m = XGBClassifier(n_estimators=100, max_depth=md, learning_rate=lr,
                                  subsample=0.8, colsample_bytree=0.8,
                                  eval_metric="logloss", random_state=42, verbosity=0)
                m.fit(X[:i_tr], y[:i_tr])
                a = accuracy_score(y[i_tr:i_va], m.predict(X[i_tr:i_va]))
                if a > melhor_acc:
                    melhor, melhor_acc = (md, lr), a
        m = XGBClassifier(n_estimators=100, max_depth=melhor[0], learning_rate=melhor[1],
                          subsample=0.8, colsample_bytree=0.8, eval_metric="logloss",
                          random_state=42, verbosity=0)
        m.fit(X[:i_va], y[:i_va])
        acc = accuracy_score(y[i_va:], m.predict(X[i_va:]))
        auc = roc_auc_score(y[i_va:], m.predict_proba(X[i_va:])[:, 1])
        print(f"  {k:28s}{melhor_acc:>11.4f}{acc:>9.4f}{auc:>9.4f}")
        res["direcao"][k] = {"acuracia_validacao": round(float(melhor_acc), 4),
                             "acuracia_teste": round(float(acc), 4),
                             "auc_teste": round(float(auc), 4)}

    dif = (res["direcao"]["A_ponderada_confianca"]["acuracia_teste"]
           - res["direcao"]["B_polaridade_pura"]["acuracia_teste"])
    print(f"\n  ponderada menos polaridade pura, no teste: {dif:+.4f} "
          f"({dif * 100:+.2f} pontos percentuais)")
    res["direcao"]["delta_A_menos_B_pp"] = round(dif * 100, 2)

    args.saida.write_text(json.dumps(res, indent=2, ensure_ascii=False, default=float),
                          encoding="utf-8")
    print(f"\n[OK] Salvo em {args.saida}")


if __name__ == "__main__":
    main()
