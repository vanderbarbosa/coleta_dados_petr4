# -*- coding: utf-8 -*-
# ==============================================================================
#   SÓ OS DIAS QUE TÊM COMUNICADO — pedido da mentoria de 29/10/2026
#
#   A pergunta: o sentimento acrescenta pouco quando medido sobre TODOS os
#   pregões. Mas em 60,4% dos pregões não houve comunicado nenhum, e nesses a
#   coluna de sentimento é um zero de preenchimento. Medir sobre tudo dilui o
#   sinal em dois terços de dias mudos. Restringindo a avaliação aos pregões
#   que de fato tiveram comunicado na véspera (após o fechamento), os índices
#   melhoram?
#
#   ─── A ARMADILHA QUE ESTE SCRIPT EVITA ──────────────────────────────────
#   Comparar "54% nos dias com evento" contra "52% em todos os dias" NÃO prova
#   nada: ao trocar de subconjunto, o ADVERSÁRIO também muda. A classe
#   majoritária dos dias com evento é outra. Por isso cada subconjunto é
#   julgado contra a SUA própria classe majoritária, e nunca contra a do
#   outro. Além disso o subconjunto é menor, então o intervalo de confiança
#   alarga — um mesmo ganho em pontos vale menos como evidência. Ambos os
#   efeitos são reportados.
#
#   ─── DUAS FÓRMULAS DE SENTIMENTO, DE PROPÓSITO ──────────────────────────
#   Achou-se uma divergência entre a dissertação e o ramo da CVM:
#     (A) p_positivo − p_negativo        — o que os scripts da CVM usam
#     (B) polaridade × confiança         — o que o Cap. 3 documenta, e o que
#                                          o pipeline de notícias (Script 03)
#                                          de fato faz; neutro vira zero
#   Em vez de escolher uma no escuro, as duas entram como variantes e o
#   resultado decide.
#
#   NOTA DE ESCOPO: "comunicado" aqui são os documentos da CVM entregues após
#   as 17h. Notícia de jornal NÃO entra — o corpus classificado não está nesta
#   máquina. A restrição é, portanto, "dias com comunicado oficial".
#
#   Saída: dados/dias_com_evento.json
# ==============================================================================
from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from arch import arch_model
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from xgboost import XGBClassifier

warnings.filterwarnings("ignore")

AQUI = Path(__file__).resolve().parent
DADOS = AQUI / "dados"
TOP10 = ["VALE3", "ITUB4", "PETR4", "SBSP3", "BBDC4", "B3SA3", "ITSA4",
         "BPAC11", "BBAS3", "ABEV3"]
XGB = dict(n_estimators=300, max_depth=3, learning_rate=0.05, subsample=0.9,
           colsample_bytree=0.9, random_state=42, eval_metric="logloss", n_jobs=-1)

_OHLCV = pd.read_csv(DADOS / "ohlcv_b3.csv", parse_dates=["Data"])
_CASOS = pd.read_csv(DADOS / "rodada_A_casos.csv", low_memory=False,
                      usecols=["Protocolo_Entrega", "Ticker", "Categoria", "Entrega", "Pregao_reacao"])
_CASOS["Entrega"] = pd.to_datetime(_CASOS["Entrega"], errors="coerce")
_CASOS["Data"] = pd.to_datetime(_CASOS["Pregao_reacao"], errors="coerce")
_CLASS = pd.read_csv(DADOS / "cvm_classificado.csv", low_memory=False)


def painel(ticker: str) -> pd.DataFrame:
    px = _OHLCV[_OHLCV["Ticker"] == ticker].sort_values("Data").reset_index(drop=True)
    px = px[px["Retorno"].notna()].reset_index(drop=True)
    g = arch_model(px["Retorno"].values * 100.0, vol="Garch", p=1, q=1, dist="t").fit(disp="off")
    px["Volatilidade_GARCH"] = g.conditional_volatility

    a = _CASOS[(_CASOS["Ticker"] == ticker) & _CASOS["Entrega"].notna() & _CASOS["Data"].notna()]
    a = a[a["Entrega"].dt.hour >= 17]
    c = a.merge(_CLASS[["Protocolo_Entrega", "p_pos", "p_neg", "p_neu", "Rotulo", "Confianca"]],
                on="Protocolo_Entrega", how="inner")
    # (A) a fórmula dos scripts da CVM
    c["ismA"] = c["p_pos"] - c["p_neg"]
    # (B) a fórmula que o Cap. 3 documenta: polaridade × confiança
    pol = c["Rotulo"].map({"POSITIVE": 1, "NEUTRAL": 0, "NEGATIVE": -1}).fillna(0)
    c["ismB"] = pol * c["Confianca"]
    cvm = c.groupby("Data").agg(SentA=("ismA", "mean"), SentB=("ismB", "mean"),
                                 Qtd=("ismA", "size"),
                                 FR=("Categoria", lambda s: int((s == "Fato Relevante").sum()))).reset_index()

    d = px.merge(cvm, on="Data", how="left")
    d["TEM_EVENTO"] = d["Qtd"].notna()
    for col in ["SentA", "SentB", "Qtd", "FR"]:
        d[col] = d[col].fillna(0.0)
    d["Retorno_Ontem"] = d["Retorno"].shift(1) * 100.0
    d["Volatilidade_Ontem"] = d["Volatilidade_GARCH"].shift(1)
    d["Alvo"] = np.where(d["Retorno"] > 0, 1, 0)
    return d.dropna(subset=["Retorno_Ontem", "Volatilidade_Ontem"]).reset_index(drop=True)


def corta(n: int):
    return slice(0, int(n * 0.60)), slice(int(n * 0.60), int(n * 0.75)), slice(int(n * 0.75), n)


def avalia(y, pred, prob=None) -> dict:
    """Cada subconjunto é julgado contra a SUA própria classe majoritária."""
    n = len(y)
    if n < 30:
        return {"n": int(n), "aviso": "amostra pequena demais para avaliar"}
    maj = float(max(y.mean(), 1 - y.mean()))
    acc = float(accuracy_score(y, pred))
    k = int((y == pred).sum())
    # meia-largura do IC95% da taxa de acerto, p/ deixar explícito o custo do n menor
    ic = 1.96 * np.sqrt(0.25 / n) * 100
    out = {"n": int(n), "majoritaria": round(maj, 4), "acuracia": round(acc, 4),
           "ganho_pp": round((acc - maj) * 100, 2),
           "ic95_meia_largura_pp": round(float(ic), 2),
           "p_vs_majoritaria": float(stats.binomtest(k, n, maj).pvalue)}
    if prob is not None and len(np.unique(y)) > 1:
        out["auc"] = round(float(roc_auc_score(y, prob)), 4)
    return out


def r2os(e, ref) -> float:
    return float(1 - (np.asarray(e) ** 2).sum() / (np.asarray(ref) ** 2).sum())


def processa(ticker: str) -> dict:
    d = painel(ticker)
    tr, va, te = corta(len(d))
    fit = slice(0, te.start)
    y = d["Alvo"].astype(int)
    yte = y.iloc[te].values
    evento = d["TEM_EVENTO"].iloc[te].values

    BASE = ["Retorno_Ontem", "Volatilidade_Ontem"]
    BRACOS = [("só preço", BASE),
              ("preço + sentimento (A: p_pos − p_neg)", BASE + ["SentA", "Qtd"]),
              ("preço + sentimento (B: polaridade × confiança)", BASE + ["SentB", "Qtd"])]

    # índices de treino que TÊM evento — para o modelo "especialista"
    idx_fit = np.arange(0, te.start)
    idx_fit_ev = idx_fit[d["TEM_EVENTO"].values[idx_fit]]

    direcao = {}
    for nome, cols in BRACOS:
        for mn in ["SVM", "XGBoost"]:
            novo = (lambda: make_pipeline(StandardScaler(), SVC(kernel="rbf", probability=True,
                                                                random_state=42))) if mn == "SVM" \
                else (lambda: XGBClassifier(**XGB))
            X = d[cols].fillna(0.0)
            # (1) treinado com TODOS os dias — o modelo generalista
            m1 = novo(); m1.fit(X.iloc[fit], y.iloc[fit])
            pv, pp = m1.predict(X.iloc[te]), m1.predict_proba(X.iloc[te])[:, 1]
            bloco = {"todos_os_dias": avalia(yte, pv, pp),
                     "so_dias_com_evento": avalia(yte[evento], pv[evento], pp[evento]),
                     "so_dias_sem_evento": avalia(yte[~evento], pv[~evento], pp[~evento])}
            # (2) treinado SÓ com dias de evento — o modelo especialista.
            # Responde à objeção de que o generalista aprendeu num mundo em que
            # 60% dos dias não têm comunicado, e por isso não estaria preparado
            # para o subconjunto em que eles existem.
            if len(idx_fit_ev) >= 100 and len(np.unique(y.values[idx_fit_ev])) > 1:
                m2 = novo(); m2.fit(X.iloc[idx_fit_ev], y.iloc[idx_fit_ev])
                pv2 = m2.predict(X.iloc[te]); pp2 = m2.predict_proba(X.iloc[te])[:, 1]
                bloco["especialista_treinado_so_em_eventos"] = avalia(
                    yte[evento], pv2[evento], pp2[evento])
                bloco["_n_treino_especialista"] = int(len(idx_fit_ev))
            else:
                bloco["especialista_treinado_so_em_eventos"] = {
                    "aviso": f"só {len(idx_fit_ev)} dias de evento no treino — insuficiente"}
            bloco["_cru"] = {"y": yte.tolist(), "pred": pv.tolist(),
                             "evento": evento.astype(int).tolist()}
            direcao[f"{mn} — {nome}"] = bloco

    # ── volatilidade: HAR, e HAR + cada fórmula de sentimento ───────────────
    v = d["Volatilidade_GARCH"]
    H = pd.DataFrame({"har1": v.shift(1), "har5": v.shift(1).rolling(5).mean(),
                      "har22": v.shift(1).rolling(22).mean()})
    yv = v.iloc[te].values
    vol, preds = {}, {}
    for nome, extra in [("HAR (referência)", []),
                        ("HAR + sentimento (A)", ["SentA", "Qtd"]),
                        ("HAR + sentimento (B)", ["SentB", "Qtd"])]:
        X = H.copy()
        for c_ in extra:
            X[c_] = d[c_]
        lin = LinearRegression().fit(X.iloc[fit].fillna(0), v.iloc[fit])
        preds[nome] = lin.predict(X.iloc[te].fillna(0))
    ref = yv - preds["HAR (referência)"]
    for nome, p in preds.items():
        e = yv - p
        vol[nome] = {
            "todos_os_dias": {"n": int(len(yv)), "mae": round(float(np.abs(e).mean()), 4),
                              "r2os_vs_HAR": round(r2os(e, ref) * 100, 2)},
            "so_dias_com_evento": {"n": int(evento.sum()),
                                   "mae": round(float(np.abs(e[evento]).mean()), 4),
                                   "r2os_vs_HAR": round(r2os(e[evento], ref[evento]) * 100, 2)},
        }
    return {"n_teste": int(len(yte)), "n_com_evento": int(evento.sum()),
            "pct_com_evento": round(float(evento.mean()) * 100, 1),
            "direcao": direcao, "volatilidade": vol}


def main() -> None:
    res = {"escopo": ("'evento' = comunicado da CVM entregue após as 17h da véspera; "
                      "notícia de jornal não entra (corpus ausente nesta máquina)"),
           "cuidado": ("cada subconjunto é avaliado contra a SUA própria classe majoritária; "
                       "o IC95% alarga no subconjunto menor, e isso é reportado"),
           "papeis": {}}
    for tk in TOP10:
        r = processa(tk)
        res["papeis"][tk] = r
        # resumo SEM escolher o melhor braço — escolher o melhor é viés de seleção
        ev = [a["so_dias_com_evento"] for a in r["direcao"].values()
              if "ganho_pp" in a["so_dias_com_evento"]]
        td = [a["todos_os_dias"]["ganho_pp"] for a in r["direcao"].values()]
        if ev:
            m_ev = float(np.mean([e["ganho_pp"] for e in ev]))
            sig = sum(e["p_vs_majoritaria"] < 0.05 and e["ganho_pp"] > 0 for e in ev)
            ic = ev[0]["ic95_meia_largura_pp"]
            esp = [a["especialista_treinado_so_em_eventos"] for a in r["direcao"].values()
                   if "ganho_pp" in a["especialista_treinado_so_em_eventos"]]
            m_esp = float(np.mean([e["ganho_pp"] for e in esp])) if esp else None
            sig_esp = sum(e["p_vs_majoritaria"] < 0.05 and e["ganho_pp"] > 0 for e in esp)
            r["resumo"] = {"ganho_medio_todos_pp": round(float(np.mean(td)), 2),
                           "ganho_medio_com_evento_pp": round(m_ev, 2),
                           "ganho_medio_especialista_pp": round(m_esp, 2) if m_esp is not None else None,
                           "ic95_com_evento_pp": ic,
                           "bracos_significativos_com_evento": int(sig),
                           "bracos_significativos_especialista": int(sig_esp)}
            esp_txt = f"{m_esp:+.2f}pp ({sig_esp}/6 sig.)" if m_esp is not None else "n/d"
            print(f"{tk}: {r['n_com_evento']} eventos ({r['pct_com_evento']}%) | média dos 6 braços — "
                  f"todos {np.mean(td):+.2f} | evento {m_ev:+.2f} (IC ±{ic:.1f}, {sig}/6 sig.) | "
                  f"especialista {esp_txt}", flush=True)
        else:
            r["resumo"] = {"aviso": f"só {r['n_com_evento']} dias com evento no teste — "
                                    f"abaixo do mínimo de 30 para avaliar"}
            print(f"{tk}: teste {r['n_teste']} ({r['n_com_evento']} com evento, "
                  f"{r['pct_com_evento']}%) | NÃO AVALIÁVEL — amostra pequena demais", flush=True)
    # ── AGRUPANDO OS 10 PAPÉIS NUM SÓ CONJUNTO ───────────────────────────
    # Cada papel isolado tem de 33 a 165 dias de evento — pouco demais, com
    # IC de ±8 a ±17 pontos. Juntando os dez, o n cresce e o IC encolhe. É a
    # resposta correta ao problema de poder estatístico, e só é legítimo
    # porque todos passaram pelo MESMO protocolo e pela mesma janela.
    print("\n" + "=" * 86)
    print("  OS 10 PAPÉIS AGRUPADOS — o mesmo teste, com poder estatístico de verdade")
    print("=" * 86)
    bracos = list(next(iter(res["papeis"].values()))["direcao"].keys())
    res["agrupado"] = {}
    for b in bracos:
        Y, P, EV = [], [], []
        for tk in TOP10:
            cru = res["papeis"][tk]["direcao"][b]["_cru"]
            Y += cru["y"]; P += cru["pred"]; EV += cru["evento"]
        Y, P, EV = np.array(Y), np.array(P), np.array(EV).astype(bool)
        res["agrupado"][b] = {"todos_os_dias": avalia(Y, P),
                              "so_dias_com_evento": avalia(Y[EV], P[EV]),
                              "so_dias_sem_evento": avalia(Y[~EV], P[~EV])}
        a, e = res["agrupado"][b]["todos_os_dias"], res["agrupado"][b]["so_dias_com_evento"]
        print(f"  {b:52} todos n={a['n']:5} {a['ganho_pp']:+6.2f}pp (p={a['p_vs_majoritaria']:.3f}) | "
              f"evento n={e['n']:4} {e['ganho_pp']:+6.2f}pp (IC ±{e['ic95_meia_largura_pp']:.1f}, "
              f"p={e['p_vs_majoritaria']:.3f})")
    # limpa os dados crus antes de gravar (ocupariam megabytes sem necessidade)
    for tk in TOP10:
        for b in res["papeis"][tk]["direcao"]:
            res["papeis"][tk]["direcao"][b].pop("_cru", None)
    (DADOS / "dias_com_evento.json").write_text(
        json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\ngravado: dados/dias_com_evento.json")


if __name__ == "__main__":
    main()
