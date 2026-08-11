# -*- coding: utf-8 -*-
# =============================================================================
#  Gera um notebook Colab AUTÔNOMO para as três medições que estão bloqueadas
#  pelo PyTorch inoperante na máquina local.
#
#  Saída: notebooks/revalidacao_encoder_colab.ipynb
#
#  As três medições, em ordem de prioridade:
#    EXP 1 — caixa alta: reclassificar com títulos normalizados
#            (hipótese: as 36 manchetes do Petronoticias melhoram muito)
#    EXP 2 — granularidade: Título x Título+Resumo
#            (hipótese: Título+Resumo, com mediana 42 palavras, se aproxima do
#             regime de treino de Santos, mediana 39)
#    EXP 3 — comitê com pysentimiento (gap G7)
#
#  Os 300 exemplos do conjunto-ouro vão embutidos em base64 — o notebook não
#  precisa de upload nem de Drive.
# =============================================================================
import base64
import csv
import io
import json
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
OURO = RAIZ / "Mestrado_PETR4" / "conjunto_ouro"
OUTDIR = RAIZ / "notebooks"
OUTDIR.mkdir(exist_ok=True)

MAPA = {"Positivo": "Positive", "Negativo": "Negative", "Neutro": "Neutral"}
SIGLAS = {"ANP", "OPEP", "OPEC", "CNPE", "ANEEL", "IBAMA", "CADE", "CVM", "BNDES",
          "GLP", "GNL", "GNV", "FPSO", "FPSOS", "LNG", "IPO", "PIB", "ICMS", "CIDE",
          "PPI", "IPCA", "COPOM", "BCB", "EUA", "UE", "ONU", "OMC", "OTAN", "BR",
          "PETR3", "PETR4", "B3", "CEO", "CFO", "TCU", "STF", "MP", "PL", "PEC"}

# ── extrai título, resumo, rótulo humano e predição atual ───────────────────
rot = pd.read_excel(OURO / "conjunto_ouro_para_rotular.xlsx", sheet_name="Rotular")
gab = pd.read_csv(OURO / "conjunto_ouro_gabarito_modelo.csv")
d = rot.merge(gab[["ID_OURO", "Label_Sentimento"]], on="ID_OURO", how="inner")
d["humano"] = d["Sentimento_Humano"].map(MAPA)
d = d[d["humano"].isin(["Negative", "Neutral", "Positive"])]
d = d[d["Título"].notna()].copy()

buf = io.StringIO()
w = csv.writer(buf)
w.writerow(["id", "fonte", "categoria", "titulo", "resumo", "humano", "finbert_atual"])
for _, r in d.iterrows():
    w.writerow([
        r["ID_OURO"], r.get("Fonte", ""), r.get("Categoria", ""),
        str(r["Título"]).replace("\n", " ").strip(),
        str(r.get("Resumo", "")).replace("\n", " ").strip(),
        r["humano"], r["Label_Sentimento"],
    ])
B64 = base64.b64encode(buf.getvalue().encode("utf-8")).decode("ascii")
print(f"Embutidos {len(d)} exemplos | base64 = {len(B64) / 1024:.1f} KB")


def md(txt):
    return {"cell_type": "markdown", "metadata": {},
            "source": txt.strip("\n").splitlines(keepends=True)}


def code(txt):
    return {"cell_type": "code", "metadata": {}, "execution_count": None,
            "outputs": [], "source": txt.strip("\n").splitlines(keepends=True)}


celulas = [
    md("""
# Revalidação do FinBERT-PT-BR — dissertação PETR4

Três medições que estão bloqueadas na máquina local (PyTorch com falha de DLL).

| Experimento | Hipótese | Tempo |
|---|---|---|
| **1. Caixa alta** | 10,5% do corpus é publicado em CAIXA ALTA; o modelo é *cased*. Normalizar deve melhorar. | ~3 min |
| **2. Granularidade** | Santos treinou com sentenças (mediana 39 palavras); damos manchetes (13). `Título+Resumo` dá 42. | ~5 min |
| **3. Comitê** | O modelo é léxico; um modelo contextual complementa (gap G7). | ~5 min |

**Runtime → Alterar tipo de execução → GPU (T4).** Os 300 exemplos do conjunto-ouro
já estão embutidos — não é preciso subir arquivo nem montar o Drive.

**Números atuais, para comparação:**

| Recorte | n | Acurácia | F1-macro | Kappa |
|---|---|---|---|---|
| Geral | 300 | 0,580 | 0,579 | 0,371 |
| Caixa normal | 264 | 0,587 | 0,585 | 0,386 |
| **CAIXA ALTA** | **36** | **0,528** | **0,487** | **0,195** |
"""),

    code("""
# Só o essencial para os experimentos 1 e 2. O pysentimiento é instalado
# depois, imediatamente antes do experimento 3 — ele costuma fixar uma versão
# do transformers, e instalá-lo agora poderia quebrar os dois primeiros.
!pip -q install -U transformers scikit-learn 2>/dev/null

import torch
print("transformers OK | GPU disponivel:", torch.cuda.is_available())
if not torch.cuda.is_available():
    print("\\n*** ATENCAO: sem GPU. Va em Ambiente de execucao ->")
    print("*** Alterar o tipo de ambiente de execucao -> T4 GPU, e rode de novo.")
"""),

    code(f'''
import base64, io, re
import pandas as pd

DADOS_B64 = "{B64}"

df = pd.read_csv(io.StringIO(base64.b64decode(DADOS_B64).decode("utf-8")))
df["resumo"] = df["resumo"].fillna("").astype(str)
print(f"conjunto-ouro: {{len(df)}} manchetes")
print(df["humano"].value_counts().to_dict())
df.head(3)
'''),

    md("""
## Preparação — detecção e normalização de caixa alta
"""),

    code(f"""
SIGLAS = {sorted(SIGLAS)!r}
SIGLAS = set(SIGLAS)

def eh_caixa_alta(t):
    L = [c for c in str(t) if c.isalpha()]
    return len(L) >= 10 and sum(c.isupper() for c in L) / len(L) > 0.90

def normalizar(t):
    saida = []
    for i, p in enumerate(str(t).split()):
        nu = re.sub(r"\\W", "", p).upper()
        if nu in SIGLAS:      saida.append(p.upper())
        elif i == 0:          saida.append(p.capitalize())
        else:                 saida.append(p.lower())
    r = " ".join(saida)
    return (r[0].upper() + r[1:]) if r else r

df["caps"] = df["titulo"].map(eh_caixa_alta)
df["titulo_norm"] = df.apply(
    lambda r: normalizar(r["titulo"]) if r["caps"] else r["titulo"], axis=1)

print(f"em caixa alta: {{df['caps'].sum()}} de {{len(df)}}")
print(df[df["caps"]]["fonte"].value_counts().to_dict())
for _, r in df[df["caps"]].head(2).iterrows():
    print("\\nANTES :", r["titulo"][:90])
    print("DEPOIS:", r["titulo_norm"][:90])
"""),

    md("""
## Carga do modelo e função de avaliação
"""),

    code("""
from transformers import pipeline
from sklearn.metrics import accuracy_score, f1_score, cohen_kappa_score, classification_report

CLASSES = ["Negative", "Neutral", "Positive"]
MAPA_FB = {"POSITIVE": "Positive", "NEGATIVE": "Negative", "NEUTRAL": "Neutral"}

pipe = pipeline("text-classification", model="lucas-leme/FinBERT-PT-BR",
                truncation=True, max_length=512, device=0)

# verificação defensiva: a ordem de rótulos do FinBERT é contraintuitiva
id2label = {int(k): v for k, v in pipe.model.config.id2label.items()}
assert id2label == {0: "POSITIVE", 1: "NEGATIVE", 2: "NEUTRAL"}, id2label
print("mapeamento de rótulos conferido:", id2label)

def classificar(textos, bs=32):
    return [MAPA_FB[r["label"]] for r in pipe(list(textos), batch_size=bs)]

def avaliar(y, p, nome, mostrar=False):
    m = dict(config=nome, n=len(y),
             acc=accuracy_score(y, p),
             f1=f1_score(y, p, average="macro", labels=CLASSES, zero_division=0),
             kappa=cohen_kappa_score(y, p, labels=CLASSES))
    print(f"  {nome:38s} n={m['n']:3d}  acc={m['acc']:.3f}  "
          f"F1={m['f1']:.3f}  kappa={m['kappa']:+.3f}")
    if mostrar:
        print(classification_report(y, p, labels=CLASSES, digits=3, zero_division=0))
    return m
"""),

    md("""
## EXPERIMENTO 1 — a normalização de caixa alta recupera desempenho?

**Hipótese:** o `tokenizer_config.json` declara `do_lower_case: False`. A cobertura do
vocabulário cai de 78,6% (caixa normal) para 22,2% (caixa alta). Normalizar deve
recuperar as 36 manchetes do Petronoticias.

**Alvo:** superar acurácia 0,528 e kappa 0,195 no subconjunto em caixa alta.
"""),

    code("""
resultados = []

pred_orig = classificar(df["titulo"])
pred_norm = classificar(df["titulo_norm"])
df["pred_orig"], df["pred_norm"] = pred_orig, pred_norm

print("=== GERAL (300) ===")
resultados.append(avaliar(df["humano"], df["pred_orig"], "titulo original"))
resultados.append(avaliar(df["humano"], df["pred_norm"], "titulo normalizado"))

print("\\n=== SÓ AS EM CAIXA ALTA (o que deve mudar) ===")
c = df[df["caps"]]
resultados.append(avaliar(c["humano"], c["pred_orig"], "CAIXA ALTA original"))
resultados.append(avaliar(c["humano"], c["pred_norm"], "CAIXA ALTA normalizado", True))

print("\\n=== controle: as de caixa normal (nao devem mudar) ===")
n = df[~df["caps"]]
avaliar(n["humano"], n["pred_orig"], "caixa normal original")

print("\\n=== o que o modelo prediz nas caixa alta ===")
print("antes :", c["pred_orig"].value_counts().to_dict())
print("depois:", c["pred_norm"].value_counts().to_dict())
print("humano:", c["humano"].value_counts().to_dict())
"""),

    md("""
## EXPERIMENTO 2 — granularidade: `Título` × `Título` + `Resumo`

**Hipótese:** Santos treinou com sentenças de corpo de notícia (mediana 39 palavras);
alimentamos manchetes (mediana 13). `Título` + `Resumo` tem mediana 42 — praticamente
o mesmo regime.

Usa o **título já normalizado**, para não misturar os dois efeitos.
"""),

    code("""
df["tit_res"] = (df["titulo_norm"].str.rstrip(". ") + ". " + df["resumo"]).str.strip()
df["n_pal_tit"] = df["titulo_norm"].str.split().str.len()
df["n_pal_tr"]  = df["tit_res"].str.split().str.len()
print(f"palavras — titulo: mediana={df['n_pal_tit'].median():.0f} | "
      f"titulo+resumo: mediana={df['n_pal_tr'].median():.0f}")
print("(referencia: textos de treino de Santos, mediana = 39)")

df["pred_tr"] = classificar(df["tit_res"])

print("\\n=== GERAL ===")
resultados.append(avaliar(df["humano"], df["pred_norm"], "titulo normalizado"))
resultados.append(avaliar(df["humano"], df["pred_tr"], "titulo + resumo", True))

print("\\n=== por categoria (onde o contexto extra mais ajuda?) ===")
for cat, g in df.groupby("categoria"):
    if len(g) < 15: continue
    a1 = accuracy_score(g["humano"], g["pred_norm"])
    a2 = accuracy_score(g["humano"], g["pred_tr"])
    print(f"  {cat:26s} n={len(g):3d}  titulo={a1:.3f}  tit+res={a2:.3f}  delta={a2-a1:+.3f}")
"""),

    md("""
## EXPERIMENTO 3 — comitê com modelo contextual (gap G7)

Błoch, Santana e Amantino (2026) caracterizam o FinBERT-PT-BR como *"fortemente
influenciado pela presença de termos negativos ou positivos"* — ou seja, **léxico**.
O `pysentimiento` é **contextual**. O comitê ataca exatamente a fronteira do neutro,
que concentra 90% dos nossos erros.

Usa a **melhor configuração de texto** dos experimentos 1 e 2.

> ⚠️ A instalação do `pysentimiento` pode pedir **reiniciar a sessão**. Se o Colab avisar,
> clique em *Reiniciar sessão* e **execute novamente a partir da célula de dados** (a que
> começa com `DADOS_B64`) — os experimentos 1 e 2 rodam rápido. Se preferir, os resultados
> desses dois já estarão salvos: basta anotá-los antes de reiniciar.
"""),

    code("""
!pip -q install pysentimiento 2>/dev/null
print("pysentimiento instalado")
"""),

    code("""
from pysentimiento import create_analyzer
MAPA_PY = {"POS": "Positive", "NEU": "Neutral", "NEG": "Negative"}
geral = create_analyzer(task="sentiment", lang="pt")

# escolhe automaticamente a melhor coluna de texto pelos experimentos anteriores
col = "tit_res" if (accuracy_score(df["humano"], df["pred_tr"]) >
                    accuracy_score(df["humano"], df["pred_norm"])) else "titulo_norm"
pred_fin = df["pred_tr"] if col == "tit_res" else df["pred_norm"]
print("texto escolhido:", col)

saidas = geral.predict(df[col].tolist())
df["pred_pysent"] = [MAPA_PY[s.output] for s in saidas]
probs_py = [{MAPA_PY[k]: v for k, v in s.probas.items()} for s in saidas]

def comite(a, b, pb, regra):
    if a == b: return a
    if regra == "voto":      return a          # empate 1x1 -> modelo de dominio
    if regra == "abstencao": return "Neutral"  # discordancia -> neutro
    if regra == "contextual": return b
    raise ValueError(regra)

print("\\n=== membros isolados ===")
resultados.append(avaliar(df["humano"], pred_fin, "FinBERT-PT-BR (lexico)"))
resultados.append(avaliar(df["humano"], df["pred_pysent"], "pysentimiento (contextual)"))

print("\\n=== comite ===")
for regra in ("voto", "abstencao", "contextual"):
    p = [comite(a, b, pb, regra) for a, b, pb in
         zip(pred_fin, df["pred_pysent"], probs_py)]
    resultados.append(avaliar(df["humano"], p, f"comite ({regra})"))

print("\\n=== recall da classe Neutral (a metrica-chave) ===")
for nome, p in [("FinBERT", pred_fin), ("pysentimiento", df["pred_pysent"])]:
    r = sum((h == "Neutral") and (x == "Neutral") for h, x in zip(df["humano"], p))
    print(f"  {nome:16s} {r}/{(df['humano']=='Neutral').sum()} = "
          f"{r/(df['humano']=='Neutral').sum():.3f}")
"""),

    md("""
## Consolidação — o que levar de volta

Baixe o CSV e traga para `Mestrado_PETR4/`. Se os experimentos 1 e 2 confirmarem
ganho, o passo seguinte é **reprocessar o corpus completo** e **recalibrar o ISM**
com a nova matriz de confusão.
"""),

    code("""
import pandas as pd
res = pd.DataFrame(resultados).round(4)
print(res.to_string(index=False))

# tolerante a execucao parcial: se a sessao foi reiniciada e so os experimentos
# 1 e 2 rodaram, a consolidacao continua funcionando
linhas_base = res[res["config"] == "titulo original"]
if len(linhas_base):
    base = linhas_base.iloc[0]
    melhor = res.sort_values("f1", ascending=False).iloc[0]
    print(f"\\nlinha de base : {base['config']:34s} acc={base['acc']:.3f} "
          f"F1={base['f1']:.3f} kappa={base['kappa']:+.3f}")
    print(f"melhor config : {melhor['config']:34s} acc={melhor['acc']:.3f} "
          f"F1={melhor['f1']:.3f} kappa={melhor['kappa']:+.3f}")
    print(f"ganho em F1-macro: {melhor['f1']-base['f1']:+.4f}")
else:
    print("\\n(linha de base ausente — rode a partir da celula de dados)")

res.to_csv("revalidacao_resultados.csv", index=False)
df.to_csv("revalidacao_predicoes.csv", index=False)
print("\\narquivos gravados. baixando...")
try:
    from google.colab import files
    files.download("revalidacao_resultados.csv")
    files.download("revalidacao_predicoes.csv")
except Exception as e:
    print("download automatico indisponivel:", type(e).__name__)
    print("pegue os arquivos no painel de Arquivos, a esquerda.")
"""),

    md("""
---

### ⚠️ Antes de reportar qualquer ganho

Rodar `src/sentimento/reconstrucao_santos_bootstrap.py` sobre `revalidacao_predicoes.csv`
para obter intervalos de confiança e teste Z. Com n = 300, diferenças menores que
cerca de 5 pontos percentuais provavelmente **não** são significativas — e afirmar
superioridade sem esse teste é exatamente a crítica que Santos antecipou no próprio
trabalho dele.
"""),
]

nb = {
    "cells": celulas,
    "metadata": {
        "colab": {"provenance": [], "toc_visible": True},
        "kernelspec": {"name": "python3", "display_name": "Python 3"},
        "language_info": {"name": "python"},
        "accelerator": "GPU",
    },
    "nbformat": 4,
    "nbformat_minor": 0,
}

destino = OUTDIR / "revalidacao_encoder_colab.ipynb"
destino.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"OK -> {destino.relative_to(RAIZ)}  ({destino.stat().st_size / 1024:.0f} KB)")
