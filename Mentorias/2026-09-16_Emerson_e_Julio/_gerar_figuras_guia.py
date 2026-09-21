# -*- coding: utf-8 -*-
# ==============================================================================
#   Figuras do guia "Como ler os números" — todas com dados reais da pesquisa,
#   exceto as duas primeiras, que são ilustrações didáticas e estão rotuladas
#   como tal no próprio gráfico.
# ==============================================================================
from __future__ import annotations

import json
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt   # noqa: E402
import numpy as np                # noqa: E402
import pandas as pd               # noqa: E402
from sklearn.decomposition import PCA              # noqa: E402
from sklearn.ensemble import RandomForestClassifier  # noqa: E402
from sklearn.metrics import roc_curve, roc_auc_score  # noqa: E402

warnings.filterwarnings("ignore")

AQUI = Path(__file__).resolve().parent
FIG = AQUI / "figuras"
FIG.mkdir(exist_ok=True)
D = AQUI.parent.parent / "CVM" / "dados"

ESCURO, OCRE, CINZA = "#1F3864", "#C8853A", "#8A8F98"
VERDE, VERM = "#2E7D5B", "#B03A3A"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10,
    "axes.edgecolor": "#CCCCCC", "axes.labelcolor": ESCURO,
    "text.color": ESCURO, "xtick.color": ESCURO, "ytick.color": ESCURO,
    "figure.facecolor": "white", "axes.facecolor": "white",
})


def salva(fig, nome):
    fig.tight_layout()
    fig.savefig(FIG / nome, dpi=170, bbox_inches="tight")
    plt.close(fig)
    print(f"  [OK] figuras/{nome}")


# ──────────────────────────────────────────────────────────────────────────────
#   Figura 1 — a diferença entre acertar e saber distinguir
# ──────────────────────────────────────────────────────────────────────────────
def fig1():
    """As notas sao fixas, e a acuracia e a AUC sao CALCULADAS a partir delas —
    nunca digitadas — para que a legenda jamais contradiga o desenho."""
    from sklearn.metrics import roc_auc_score

    # 20 pregoes; os de indice 4, 11 e 17 foram de fato agitados
    agitado = np.zeros(20, dtype=bool)
    agitado[[4, 11, 17]] = True

    nota_A = np.full(20, 0.10)                     # responde sempre "calmo"
    nota_B = np.array([0.14, 0.11, 0.29, 0.07, 0.88, 0.26, 0.24, 0.62,
                       0.30, 0.25, 0.52, 0.72, 0.05, 0.13, 0.58, 0.20,
                       0.66, 0.55, 0.38, 0.11])
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.6))
    for ax, (tit, nota) in zip(axs, [
            ("MODELO A — responde sempre “calmo”", nota_A),
            ("MODELO B — dá uma nota de risco a cada pregão", nota_B)]):
        acertos = int(((nota > 0.5) == agitado).sum())
        auc = roc_auc_score(agitado.astype(int), nota)
        ax.bar(range(20), nota, width=0.72,
               color=[OCRE if a else CINZA for a in agitado])
        ax.axhline(0.5, color=ESCURO, ls="--", lw=1)
        ax.text(19.6, 0.52, "corte de decisão", ha="right", va="bottom",
                fontsize=8, color=ESCURO)
        ax.set_ylim(0, 1)
        ax.set_title(tit, fontsize=10.5, weight="bold", pad=10)
        ax.set_xlabel("os mesmos 20 pregões", fontsize=9)
        ax.set_ylabel("nota de risco dada pelo modelo", fontsize=9)
        ax.set_xticks([])
        ax.text(0.5, -0.32,
                f"acerta {acertos} de 20  =  {acertos * 5}%"
                + chr(10) + f"AUC = {auc:.2f}".replace(".", ","),
                transform=ax.transAxes, ha="center", fontsize=10.5,
                weight="bold", color=ESCURO)
        for s_ in ("top", "right"):
            ax.spines[s_].set_visible(False)

    # os postos das barras laranja, calculados e nao afirmados
    ordem = np.argsort(-nota_B)
    postos = ", ".join(f"{list(ordem).index(i) + 1}º"
                       for i in np.where(agitado)[0])

    fig.text(0.5, 1.04, "Laranja = pregão que de fato foi agitado  ·  "
                        "Cinza = pregão calmo   (ilustração didática)",
             ha="center", fontsize=9, color=CINZA)
    fig.text(0.5, -0.13,
             "O Modelo A acerta MAIS e não serve para nada: ele nunca aponta "
             "um pregão agitado." + chr(10) +
             f"O Modelo B acerta MENOS e é bom: as três barras laranja ficaram "
             f"em {postos} entre as 20 notas.",
             ha="center", fontsize=9.5, color=ESCURO)
    salva(fig, "fig1_acuracia_vs_auc.png")


# ──────────────────────────────────────────────────────────────────────────────
#   Figura 2 — o que a AUC mede, em uma frase desenhada
# ──────────────────────────────────────────────────────────────────────────────
def fig2():
    fig, ax = plt.subplots(figsize=(10, 3.4))
    rng = np.random.default_rng(3)
    calmos = rng.normal(0.32, 0.11, 400)
    agitados = rng.normal(0.62, 0.13, 120)
    ax.hist(calmos, bins=34, color=CINZA, alpha=0.75, label="pregões calmos")
    ax.hist(agitados, bins=24, color=OCRE, alpha=0.85, label="pregões agitados")
    ax.axvline(0.5, color=ESCURO, ls="--", lw=1.2)
    ax.text(0.505, ax.get_ylim()[1] * 0.92, " corte de decisão", fontsize=8.5,
            color=ESCURO)
    ax.set_xlabel("nota de risco dada pelo modelo", fontsize=9.5)
    ax.set_ylabel("quantidade de pregões", fontsize=9.5)
    ax.legend(frameon=False, fontsize=9)
    ax.set_title("A AUC mede o quanto as duas montanhas estão separadas — "
                 "não onde fica o corte", fontsize=10.5, weight="bold", pad=12)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.text(0.5, -0.06,
             "Mover o corte muda a ACURÁCIA. Não muda a AUC.   (ilustração didática)",
             ha="center", fontsize=9, color=CINZA)
    salva(fig, "fig2_o_que_a_auc_mede.png")


# ──────────────────────────────────────────────────────────────────────────────
#   Figura 3 — as curvas ROC reais dos nossos modelos
# ──────────────────────────────────────────────────────────────────────────────
def roda(d, cols, emb, alvo="alvo_ext", TESTE=250, MIN=500, NP=16):
    d = d[d[alvo].notna()].reset_index(drop=True)
    usa = [c for c in cols if c in d.columns]
    real, prob = [], []
    ini = MIN
    while ini < len(d):
        fim = min(ini + TESTE, len(d))
        tr, te = d.iloc[:ini], d.iloc[ini:fim]
        if te.empty or tr[alvo].nunique() < 2:
            ini = fim
            continue
        Xtr, Xte = tr[usa].copy(), te[usa].copy()
        if emb:
            p = PCA(n_components=min(NP, len(emb)), random_state=42)
            p.fit(tr[emb].fillna(0.0).values)
            for i, v in enumerate(p.transform(tr[emb].fillna(0.0).values).T):
                Xtr[f"pc{i}"] = v
            for i, v in enumerate(p.transform(te[emb].fillna(0.0).values).T):
                Xte[f"pc{i}"] = v
        med = Xtr.median(numeric_only=True)
        Xtr, Xte = Xtr.fillna(med).fillna(0.0), Xte.fillna(med).fillna(0.0)
        m = RandomForestClassifier(n_estimators=400, min_samples_leaf=20,
                                   max_features="sqrt", random_state=42,
                                   n_jobs=-1).fit(Xtr, tr[alvo].astype(int))
        real += list(te[alvo].astype(int))
        prob += list(m.predict_proba(Xte)[:, 1])
        ini = fim
    return np.array(real), np.array(prob)


def fig3_e_4():
    d = pd.read_csv(D / "painel_ml.csv", parse_dates=["Data"])
    C = {p: [c for c in d.columns if c.startswith(p)]
         for p in ["m_", "nt_", "cv_", "emb"]}
    arms = {
        "só o histórico de preço (o HAR)": (C["m_"], [], ESCURO),
        "só o texto (notícia + CVM + embedding)": (C["nt_"] + C["cv_"], C["emb"], OCRE),
    }
    guard = {}

    # ── ROC ──────────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(6.4, 6))
    for nome, (cols, emb, cor) in arms.items():
        y, p = roda(d, cols, emb)
        guard[nome] = (y, p)
        fpr, tpr, _ = roc_curve(y, p)
        ax.plot(fpr, tpr, color=cor, lw=2.4,
                label=f"{nome}\nAUC = {roc_auc_score(y, p):.3f}".replace(".", ","))
    ax.plot([0, 1], [0, 1], color=CINZA, ls="--", lw=1.2,
            label="cara ou coroa\nAUC = 0,500")
    ax.set_xlabel("alarmes falsos", fontsize=10)
    ax.set_ylabel("dias agitados corretamente apontados", fontsize=10)
    ax.set_title("Curva ROC — prever o pregão excepcional\n"
                 "quanto mais a curva sobe pela esquerda, melhor",
                 fontsize=11, weight="bold", pad=14)
    ax.legend(frameon=False, fontsize=8.6, loc="lower right")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    salva(fig, "fig3_roc_real.png")

    # ── ganho por faixa de risco ─────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(9.6, 4.6))
    larg, i = 0.36, 0
    for nome, (y, p) in guard.items():
        cor = arms[nome][2]
        ordem = np.argsort(-p)
        faixas, rot = [], []
        for a, b, r in [(0, .10, "10% mais\narriscados"),
                        (.10, .25, "10–25%"), (.25, .50, "25–50%"),
                        (.50, 1.0, "metade mais\ncalma")]:
            sel = ordem[int(len(p) * a):int(len(p) * b)]
            faixas.append(y[sel].mean() * 100)
            rot.append(r)
        x = np.arange(len(faixas)) + (i - 0.5) * larg
        bars = ax.bar(x, faixas, larg, color=cor, label=nome)
        for bb, v in zip(bars, faixas):
            ax.text(bb.get_x() + bb.get_width() / 2, v + 0.5,
                    f"{v:.1f}%".replace(".", ","), ha="center", fontsize=8.6,
                    weight="bold", color=cor)
        i += 1
    base = np.mean([y.mean() for y, _ in guard.values()]) * 100
    ax.axhline(base, color=VERM, ls="--", lw=1.4)
    ax.text(3.45, base + 0.6, f"base: {base:.1f}% dos pregões".replace(".", ","),
            ha="right", fontsize=9, color=VERM, weight="bold")
    ax.set_xticks(range(4)); ax.set_xticklabels(rot, fontsize=9)
    ax.set_xlabel("pregões ordenados pela nota de risco do modelo", fontsize=9.5)
    ax.set_ylabel("% que virou dia excepcional", fontsize=9.5)
    ax.set_title("O que a AUC significa na prática: quando o modelo aponta "
                 "as noites de maior risco",
                 fontsize=11, weight="bold", pad=12)
    ax.legend(frameon=False, fontsize=9, loc="upper right")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    salva(fig, "fig4_ganho_por_faixa.png")


# ──────────────────────────────────────────────────────────────────────────────
#   Figura 5 — a direção, contra a linha de base certa
# ──────────────────────────────────────────────────────────────────────────────
def fig5():
    P = json.loads((D / "pesquisa_com_cvm.json").read_text(encoding="utf-8"))
    maj = P["majoritaria_teste"] * 100
    rot = {"apenas preços  [linha de base da pesquisa]": "apenas\npreços",
           "Data Fusion: preços + notícia  [O QUE TÍNHAMOS ANTES]":
               "preços +\nnotícia",
           "Data Fusion + CVM  [NOVO]": "preços +\nnotícia + CVM",
           "Data Fusion + CVM + embedding  [NOVO]": "+ embedding\nda CVM",
           "preços + CVM, sem notícia  [controle]": "preços + CVM\n(controle)"}

    fig, ax = plt.subplots(figsize=(10, 4.8))
    x = np.arange(len(rot))
    for i, (mod, cor) in enumerate([("SVM-RBF", ESCURO), ("XGBoost", OCRE)]):
        v = [P["direcao"][k][mod]["acuracia"] * 100 for k in rot]
        bars = ax.bar(x + (i - 0.5) * 0.38, v, 0.38, color=cor, label=mod)
        for bb, val in zip(bars, v):
            ax.text(bb.get_x() + bb.get_width() / 2, val + 0.25,
                    f"{val:.1f}".replace(".", ","), ha="center", fontsize=8.6,
                    weight="bold", color=cor)
    ax.axhline(maj, color=VERM, ls="--", lw=1.6)
    ax.text(len(rot) - 0.4, maj + 0.35,
            f"palpite fixo “sempre alta”: {maj:.2f}%".replace(".", ","),
            ha="right", fontsize=9.5, color=VERM, weight="bold")
    ax.axhline(50, color=CINZA, ls=":", lw=1.2)
    ax.text(-0.45, 50.2, "cara ou coroa: 50%", fontsize=8.6, color=CINZA)
    ax.set_xticks(x); ax.set_xticklabels(rot.values(), fontsize=9)
    ax.set_ylim(46, 57)
    ax.set_ylabel("acurácia no teste (%)", fontsize=9.5)
    ax.set_title("Direção do pregão seguinte — por que nenhum braço “ganha”\n"
                 "a linha vermelha é o adversário; a cinza é o acaso",
                 fontsize=11, weight="bold", pad=12)
    ax.legend(frameon=False, fontsize=9.5, loc="upper left")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    salva(fig, "fig5_direcao_linhas_base.png")


# ──────────────────────────────────────────────────────────────────────────────
#   Figura 6 — o painel de metas: o que buscar em cada alvo
# ──────────────────────────────────────────────────────────────────────────────
def fig6():
    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    ax.axis("off")
    linhas = [
        ("ALVO", "ADVERSÁRIO A BATER", "MEDIDA PRINCIPAL", "META REALISTA",
         "ONDE ESTAMOS"),
        ("Direção\n(alta ou baixa)", "classe majoritária\n53,14%",
         "acurácia + McNemar", "55–58%\ne McNemar < 0,05", "52,8%\nnão passa"),
        ("Volatilidade\n(quanto sacode)", "HAR de Corsi",
         "R²-OS fora da amostra", "R²-OS > +5%\nsobre o HAR",
         "+7,5% com notícia\n+7,5% com CVM"),
        ("Dia excepcional\n(topo 10%)", "a base de 6,3%",
         "AUC + ganho no decil", "AUC com IC que\nexclua 0,50",
         "texto: 0,624\nmercado: 0,794"),
    ]
    larg = [0.17, 0.20, 0.21, 0.21, 0.21]
    y0, alt = 0.86, 0.19
    for li, linha in enumerate(linhas):
        x = 0.01
        for ci, (txt, w) in enumerate(zip(linha, larg)):
            cab = li == 0
            ax.add_patch(plt.Rectangle((x, y0 - li * alt), w - 0.008, alt - 0.02,
                         facecolor=ESCURO if cab else ("#F4F1EC" if li % 2 else "white"),
                         edgecolor="#DDDDDD", lw=0.8))
            ax.text(x + (w - 0.008) / 2, y0 - li * alt + (alt - 0.02) / 2, txt,
                    ha="center", va="center", fontsize=9 if cab else 9.2,
                    weight="bold" if cab or ci == 0 else "normal",
                    color="white" if cab else (OCRE if ci == 4 else ESCURO))
            x += w
    ax.set_xlim(0, 1); ax.set_ylim(0.1, 1.0)
    ax.set_title("O que buscar em cada alvo — e contra quem comparar",
                 fontsize=12, weight="bold", pad=6)
    fig.text(0.5, 0.06,
             "Nenhum número isolado significa nada. O que significa é a distância "
             "até a linha de base certa,\ne se essa distância passa num teste.",
             ha="center", fontsize=9.5, style="italic", color=ESCURO)
    salva(fig, "fig6_o_que_buscar.png")


if __name__ == "__main__":
    fig1(); fig2(); fig3_e_4(); fig5(); fig6()
