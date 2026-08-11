# -*- coding: utf-8 -*-
# =============================================================================
#  Gera o notebook de CONTROLE do G3 — o último experimento do classificador
#  Saída: notebooks/g3_controle_colab.ipynb
#
#  POR QUE ELE EXISTE
#  A rodada de 09/08/2026 produziu dois números que NÃO podem ser reportados
#  como estão:
#
#  (1) "perplexidade 36.511 -> 3,67, ganho de 99,99%"
#      INVÁLIDO. O relatório de carga mostra que TODA a cabeça de MLM veio
#      MISSING do checkpoint — o modelo publicado é um classificador e não
#      contém `cls.predictions.*`. Perplexidade 36.511 é da ordem do vocabulário
#      (29.794), assinatura de cabeça ALEATÓRIA. O "ganho" mede treinar uma
#      cabeça do zero, não adaptação de domínio.
#
#  (2) "B (adaptado) 0,5467 contra A (publicado) 0,5800"
#      CONFUNDIDO. A foi treinado por Santos nos 503 rótulos com validação
#      cruzada; B foi treinado em 70% deles (352). B viu MENOS dados. A queda
#      pode ser disso, e não da adaptação.
#
#  O QUE ESTE NOTEBOOK MEDE
#      C — FinBERT-PT-BR ORIGINAL, sem adaptação, ajustado nos MESMOS 352
#          exemplos, com o MESMO protocolo e a MESMA semente.
#
#      C isola o efeito da adaptação:
#        C ≈ B  -> a adaptação foi NEUTRA; a queda veio do protocolo de ajuste
#        C > B  -> a adaptação ATRAPALHOU (esquecimento catastrófico)
#        C < B  -> a adaptação AJUDOU
#
#      + perplexidade do BERTimbau (que TEM cabeça de MLM treinada) no mesmo
#        holdout, como referência válida para os 3,669 do modelo adaptado.
#
#  É o ÚLTIMO experimento da linha do classificador. Qualquer que seja o
#  resultado, ele torna o G3 reportável — e aí a decisão é migrar para a escrita.
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

rot = pd.read_excel(OURO / "conjunto_ouro_para_rotular.xlsx", sheet_name="Rotular")
gab = pd.read_csv(OURO / "conjunto_ouro_gabarito_modelo.csv")
d = rot.merge(gab[["ID_OURO", "Label_Sentimento"]], on="ID_OURO", how="inner")
d["humano"] = d["Sentimento_Humano"].map(MAPA)
d = d[d["humano"].isin(["Negative", "Neutral", "Positive"]) & d["Título"].notna()]

buf = io.StringIO()
w = csv.writer(buf)
w.writerow(["id", "categoria", "titulo", "humano", "finbert_base"])
for _, r in d.iterrows():
    w.writerow([r["ID_OURO"], r.get("Categoria", ""),
                str(r["Título"]).replace("\n", " ").strip(),
                r["humano"], r["Label_Sentimento"]])
B64 = base64.b64encode(buf.getvalue().encode("utf-8")).decode("ascii")
print(f"Embutidos {len(d)} exemplos | {len(B64)/1024:.0f} KB")


def md(t):
    return {"cell_type": "markdown", "metadata": {},
            "source": t.strip("\n").splitlines(keepends=True)}


def code(t):
    return {"cell_type": "code", "metadata": {}, "execution_count": None,
            "outputs": [], "source": t.strip("\n").splitlines(keepends=True)}


celulas = [
    md("""
# Controle do G3 — o último experimento

A rodada anterior produziu dois números que **não podem ser reportados como estão**.

### Problema 1 — a perplexidade "36.511 → 3,67" é inválida

O relatório de carga mostrou:

```
cls.predictions.transform.dense.weight  | MISSING
cls.predictions.decoder.bias            | MISSING
cls.predictions.bias                    | MISSING
...
This checkpoint seem corrupted. The tied weights mapping ... both are absent
```

**Toda a cabeça de MLM veio ausente** — o modelo publicado é um classificador e não
contém `cls.predictions.*`. Perplexidade de 36.511 é da ordem do vocabulário (29.794):
assinatura de cabeça **aleatória**. O "ganho de 99,99%" mede treinar uma cabeça do zero,
**não** adaptação de domínio.

### Problema 2 — a comparação A × B está confundida

| | Rótulos de treino |
|---|---|
| A — publicado | **503**, com validação cruzada (Santos) |
| B — adaptado | **352** (70% de 503) |

**B viu menos dados.** A queda de 0,580 para 0,547 pode vir daí, não da adaptação.

---

## O que este notebook mede

**Modelo C** — FinBERT-PT-BR **original**, sem adaptação, ajustado nos **mesmos 352**
exemplos, mesmo protocolo, mesma semente.

| Se | Então |
|---|---|
| **C ≈ B** (~0,547) | a adaptação foi **neutra**; a queda veio do protocolo de ajuste |
| **C > B** | a adaptação **atrapalhou** (esquecimento catastrófico) |
| **C < B** | a adaptação **ajudou** |

Mais a perplexidade do **BERTimbau** — que tem cabeça de MLM de verdade — no mesmo
*holdout*, como referência válida para os 3,669 do modelo adaptado.

> **~30 minutos.** Não precisa refazer o MLM. Runtime → T4 GPU.
"""),

    code("""
!pip -q install -U transformers datasets accelerate scikit-learn 2>/dev/null
import torch
print("GPU:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "NENHUMA")
"""),

    md("""
## Parte 1 — Modelo C: o controle decisivo

Não precisa do corpus nem do modelo adaptado. Só do FinBERT original e dos 503 de Santos.
"""),

    code("""
import numpy as np, pandas as pd, torch
from torch.utils.data import DataLoader, Dataset as TorchDS
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.model_selection import train_test_split

MODELO = "lucas-leme/FinBERT-PT-BR"
MAX_TOKENS, LR_FT, EPOCAS_FT = 128, 5e-6, 11     # identicos a rodada anterior
CLASSES = ["Negative", "Neutral", "Positive"]
C2I = {c: i for i, c in enumerate(CLASSES)}
dev = "cuda"

tok = AutoTokenizer.from_pretrained(MODELO)

santos = pd.read_csv("https://huggingface.co/datasets/lucas-leme/"
                     "Sentiments-FinBERT-PT-BR/resolve/main/sentiments.csv")
MAPA_S = {"Positivo":"Positive", "Negativo":"Negative", "Neutro":"Neutral"}
santos = santos[santos["sentiment"].isin(MAPA_S)].copy()
santos["label"] = santos["sentiment"].map(MAPA_S)
print(f"{len(santos)} rotulados |", santos["label"].value_counts().to_dict())

class DS(TorchDS):
    def __init__(self, X, y):
        self.e = tok(list(X), truncation=True, max_length=MAX_TOKENS,
                     padding="max_length", return_tensors="pt")
        self.y = torch.tensor([C2I[v] for v in y])
    def __len__(self): return len(self.y)
    def __getitem__(self, i):
        it = {k: v[i] for k, v in self.e.items()}; it["labels"] = self.y[i]; return it

def blocos(m): return getattr(m, "bert", None) or m.base_model
def congelar(m):
    for p in blocos(m).parameters(): p.requires_grad = False
def descongelar(m, n):
    cam = blocos(m).encoder.layer
    for l in cam[max(0, len(cam)-n):]:
        for p in l.parameters(): p.requires_grad = True

def treinar(caminho, nome):
    # MESMA semente e MESMO split da rodada anterior -> os 352 sao os mesmos
    Xtr, Xva, ytr, yva = train_test_split(
        santos["text"].values, santos["label"].values,
        test_size=0.30, stratify=santos["label"], random_state=42)
    print(f"  treino={len(Xtr)}  validacao={len(Xva)}")
    m = AutoModelForSequenceClassification.from_pretrained(
        caminho, num_labels=3, ignore_mismatched_sizes=True,
        problem_type="single_label_classification").to(dev)
    congelar(m)
    dtr = DataLoader(DS(Xtr, ytr), batch_size=16, shuffle=True)
    dva = DataLoader(DS(Xva, yva), batch_size=16)
    melhor, estado = float("inf"), None
    for ep in range(EPOCAS_FT):
        descongelar(m, ep + 1)
        opt = torch.optim.AdamW([p for p in m.parameters() if p.requires_grad], lr=LR_FT)
        m.train()
        for b in dtr:
            b = {k: v.to(dev) for k, v in b.items()}
            opt.zero_grad(); m(**b).loss.backward(); opt.step()
        m.eval(); perdas = []
        with torch.no_grad():
            for b in dva:
                b = {k: v.to(dev) for k, v in b.items()}
                perdas.append(m(**b).loss.item())
        lv = float(np.mean(perdas))
        print(f"  [{nome}] epoca {ep+1:2d}/{EPOCAS_FT}  loss_val={lv:.4f}")
        if lv < melhor:
            melhor, estado = lv, {k: v.cpu().clone() for k, v in m.state_dict().items()}
    m.load_state_dict(estado); return m

print("\\n=== C: FinBERT ORIGINAL, mesmos 352 exemplos ===")
modelo_C = treinar(MODELO, "controle")
"""),

    code(f'''
import base64, io
DADOS_B64 = "{B64}"
ouro = pd.read_csv(io.StringIO(base64.b64decode(DADOS_B64).decode("utf-8")))
print(f"conjunto-ouro: {{len(ouro)}} manchetes")
'''),

    code("""
from sklearn.metrics import (accuracy_score, f1_score, cohen_kappa_score,
                             classification_report, confusion_matrix)

def prever(m, textos, bs=32):
    m.eval(); out = []
    for i in range(0, len(textos), bs):
        b = tok(list(textos[i:i+bs]), truncation=True, max_length=MAX_TOKENS,
                padding=True, return_tensors="pt").to(dev)
        with torch.no_grad(): out += m(**b).logits.argmax(-1).cpu().tolist()
    return [CLASSES[i] for i in out]

def avaliar(y, p, nome, det=False):
    r = dict(config=nome, acc=accuracy_score(y, p),
             f1=f1_score(y, p, average="macro", labels=CLASSES, zero_division=0),
             kappa=cohen_kappa_score(y, p, labels=CLASSES))
    print(f"  {nome:44s} acc={r['acc']:.4f}  F1={r['f1']:.4f}  kappa={r['kappa']:+.4f}")
    if det:
        print(classification_report(y, p, labels=CLASSES, digits=3, zero_division=0))
        print(pd.DataFrame(confusion_matrix(y, p, labels=CLASSES),
                           index=CLASSES, columns=CLASSES).to_string())
    return r

ouro["pred_C"] = prever(modelo_C, ouro["titulo"].values)

res = []
print("=== COMPARACAO FINAL ===")
res.append(avaliar(ouro["humano"], ouro["finbert_base"],
                   "A - publicado (503 rotulos, CV)"))
res.append(dict(config="B - adaptado + 352 rotulos", acc=0.5467, f1=0.5279, kappa=0.3088))
print(f"  {'B - adaptado + 352 rotulos':44s} acc=0.5467  F1=0.5279  kappa=+0.3088   (rodada anterior)")
res.append(avaliar(ouro["humano"], ouro["pred_C"],
                   "C - SEM adaptacao + 352 rotulos", True))

C_, B_ = res[2], res[1]
print(f"\\n>>> C - B em F1-macro: {C_['f1']-B_['f1']:+.4f}")
if abs(C_["f1"] - B_["f1"]) < 0.03:
    print(">>> C ~ B  ->  a ADAPTACAO foi NEUTRA. A queda veio do protocolo de")
    print(">>>          ajuste fino (352 rotulos contra os 503 com CV de Santos).")
elif C_["f1"] > B_["f1"]:
    print(">>> C > B  ->  a ADAPTACAO ATRAPALHOU (esquecimento catastrofico).")
else:
    print(">>> C < B  ->  a ADAPTACAO AJUDOU.")
"""),

    md("""
## Parte 2 — perplexidade com referência válida

O BERTimbau **tem** cabeça de MLM treinada. Medir a perplexidade dele no mesmo *holdout*
dá a referência que faltava para os **3,669** do modelo adaptado.

Suba de novo o `corpus_mlm_petr4.csv.gz`. Se preferir pular, a Parte 1 já responde à
pergunta principal.
"""),

    code("""
import os, math
from datasets import Dataset
from transformers import (AutoModelForMaskedLM, DataCollatorForLanguageModeling,
                          Trainer, TrainingArguments)

if not os.path.exists("corpus_mlm_petr4.csv.gz"):
    from google.colab import files
    print("Suba o corpus_mlm_petr4.csv.gz:")
    files.upload()

corpus = pd.read_csv("corpus_mlm_petr4.csv.gz")
corpus["text"] = corpus["text"].astype(str)

def perplexidade(nome_modelo, rotulo):
    tk = AutoTokenizer.from_pretrained(nome_modelo)
    md_ = AutoModelForMaskedLM.from_pretrained(nome_modelo)
    # MESMA semente e MESMO tamanho de holdout da rodada anterior
    ds = Dataset.from_pandas(corpus[["text"]]).train_test_split(test_size=10_000, seed=42)
    ds = ds["test"].map(lambda b: tk(b["text"], truncation=True, max_length=128),
                        batched=True, remove_columns=["text"])
    col = DataCollatorForLanguageModeling(tokenizer=tk, mlm=True, mlm_probability=0.15)
    tr = Trainer(model=md_,
                 args=TrainingArguments(output_dir="ppl", per_device_eval_batch_size=32,
                                        fp16=True, report_to=[]),
                 eval_dataset=ds, data_collator=col)
    p = math.exp(tr.evaluate()["eval_loss"])
    print(f"  {rotulo:44s} perplexidade = {p:.4f}")
    return p

print("=== PERPLEXIDADE no mesmo holdout de 10.000 textos ===")
ppl_bertimbau = perplexidade("neuralmind/bert-base-portuguese-cased",
                             "BERTimbau (cabeca de MLM treinada)")
print(f"  {'FinBERT adaptado ao PETR4 (rodada anterior)':44s} perplexidade = 3.6694")
print(f"\\n>>> referencia de Santos: BERTimbau 1,51 -> FinBERT-PT-BR 1,24")
print(">>> (medidas no corpus DELE, nao comparaveis em valor absoluto com as nossas)")
if ppl_bertimbau > 3.6694:
    print("\\n>>> O modelo adaptado tem perplexidade MENOR que o BERTimbau no nosso")
    print(">>> corpus. A adaptacao de dominio funcionou COMO MODELO DE LINGUAGEM.")
else:
    print("\\n>>> O BERTimbau ja modela nosso corpus melhor. A adaptacao nao agregou.")
"""),

    md("""
## Consolidação
"""),

    code("""
tab = pd.DataFrame(res).round(4)
print(tab.to_string(index=False))
tab.to_csv("g3_controle_resultados.csv", index=False)
ouro.to_csv("g3_controle_predicoes.csv", index=False)
try:
    ppl_txt = f"bertimbau={ppl_bertimbau:.6f}\\nfinbert_adaptado=3.669423\\n"
except NameError:
    ppl_txt = "parte 2 nao executada\\n"
open("g3_controle_perplexidade.txt", "w").write(ppl_txt)
try:
    from google.colab import files
    for a in ("g3_controle_resultados.csv", "g3_controle_predicoes.csv",
              "g3_controle_perplexidade.txt"):
        files.download(a)
except Exception as e:
    print("baixe pelo painel de Arquivos:", type(e).__name__)
"""),

    md("""
---

### Este é o último experimento da linha do classificador

Somando tudo, são **oito tentativas** sem ganho relevante. Qualquer que seja o resultado
aqui, ele torna o G3 **reportável** — e a recomendação passa a ser encerrar esta linha e
migrar o tempo restante para a modelagem de volatilidade e para a **escrita**.

Os resultados negativos não são desperdício: viram uma seção de *"hipóteses testadas e
rejeitadas"* com oito entradas medidas, que demonstra rigor melhor do que qualquer
melhoria isolada não testada.
"""),
]

nb = {"cells": celulas,
      "metadata": {"colab": {"provenance": [], "toc_visible": True},
                   "kernelspec": {"name": "python3", "display_name": "Python 3"},
                   "language_info": {"name": "python"},
                   "accelerator": "GPU"},
      "nbformat": 4, "nbformat_minor": 0}

destino = OUTDIR / "g3_controle_colab.ipynb"
destino.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"OK -> {destino.relative_to(RAIZ)}  ({destino.stat().st_size/1024:.0f} KB)")
