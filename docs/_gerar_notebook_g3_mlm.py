# -*- coding: utf-8 -*-
# =============================================================================
#  Gera o notebook Colab do GAP G3 — adaptação de domínio por MLM
#  Saída: notebooks/g3_adaptacao_dominio_colab.ipynb
#
#  DESENHO EXPERIMENTAL
#  Duas variantes do mesmo classificador, treinadas com EXATAMENTE os mesmos
#  503 rótulos de Santos. A única diferença é a adaptação de domínio:
#
#    A (linha de base) : lucas-leme/FinBERT-PT-BR, como publicado
#                        -> já medido no nosso conjunto-ouro: acc 0,580
#
#    B (experimento)   : FinBERT-PT-BR -> MLM nas 205 mil notícias da PETR4
#                        -> nova cabeça de sentimento
#                        -> ajuste fino nos 503 de Santos (gradual unfreezing)
#
#  Como os rótulos são os mesmos, qualquer diferença é atribuível à adaptação.
#
#  É a última carta com fundamentação forte: foi a etapa de maior ganho em
#  Santos (perplexidade 1,51 -> 1,24) e é a única testada até aqui que MUDA A
#  REPRESENTAÇÃO, que é onde o diagnóstico localizou o problema.
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
print(f"Embutidos {len(d)} exemplos do conjunto-ouro | {len(B64)/1024:.0f} KB")


def md(t):
    return {"cell_type": "markdown", "metadata": {},
            "source": t.strip("\n").splitlines(keepends=True)}


def code(t):
    return {"cell_type": "code", "metadata": {}, "execution_count": None,
            "outputs": [], "source": t.strip("\n").splitlines(keepends=True)}


celulas = [
    md("""
# G3 — Adaptação de domínio por MLM

**A última carta com fundamentação forte.** Seis tentativas anteriores de melhorar o
classificador não renderam ganho relevante; todas mexiam na **saída**. Esta mexe na
**representação**, que é onde o diagnóstico localizou o problema.

### Desenho

| | Adaptação ao nosso domínio | Rótulos de treino | Resultado |
|---|---|---|---|
| **A — linha de base** | não | 503 de Santos | **acc 0,580** (já medido) |
| **B — experimento** | **MLM em 205 mil notícias PETR4** | **os mesmos 503** | a medir |

Os rótulos são idênticos nas duas. **Qualquer diferença é atribuível à adaptação.**

### O que esperar

Santos obteve perplexidade **1,51 → 1,24** (ganho de ~18%) adaptando o BERTimbau a
1,4 milhão de notícias financeiras. Nós partimos de um modelo já financeiro e
adaptamos a 205 mil notícias de um subdomínio (Petrobras, petróleo, estatais). O ganho
de perplexidade deve ser **menor** — o modelo já viu texto financeiro. A pergunta é se
sobra sinal para o subdomínio.

> **Runtime → Alterar o tipo de ambiente de execução → T4 GPU.** Tempo total estimado:
> 60 a 90 minutos.
"""),

    code("""
!pip -q install -U transformers datasets accelerate scikit-learn 2>/dev/null
import torch
print("GPU:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "NENHUMA")
if not torch.cuda.is_available():
    print("\\n*** Ative a GPU: Ambiente de execucao -> Alterar tipo -> T4 GPU ***")
"""),

    md("""
## 1. Corpus

Suba o arquivo **`corpus_mlm_petr4.csv.gz`** (~20 MB) pelo painel de Arquivos, à esquerda.
Ele foi gerado por `docs/_exportar_corpus_mlm.py` e contém `Título` + `Resumo` de cada
notícia — mediana de **39 palavras**, exatamente o regime dos textos de treino de Santos.

> Usar `Resumo` aqui **não** contradiz o experimento que mostrou que ele atrapalha a
> classificação. São etapas distintas: no MLM não há rótulo, e o objetivo é ensinar
> vocabulário — texto mais longo é estritamente melhor. Na inferência continuamos usando
> só o `Título`.
"""),

    code("""
import pandas as pd, os

CAMINHO = "corpus_mlm_petr4.csv.gz"
if not os.path.exists(CAMINHO):
    from google.colab import files
    print("Selecione o corpus_mlm_petr4.csv.gz:")
    files.upload()

corpus = pd.read_csv(CAMINHO)
corpus["text"] = corpus["text"].astype(str)
print(f"corpus: {len(corpus):,} textos")
print(f"palavras: mediana={corpus['text'].str.split().str.len().median():.0f}")
corpus.head(3)
"""),

    md("""
## 2. Perplexidade ANTES

Métrica intrínseca — **não depende de gabarito humano**. É por isso que este experimento
é compatível com a suspensão da rotulagem.
"""),

    code("""
import math, numpy as np, torch
from datasets import Dataset
from transformers import (AutoTokenizer, AutoModelForMaskedLM,
                          DataCollatorForLanguageModeling, Trainer, TrainingArguments)

MODELO_BASE = "lucas-leme/FinBERT-PT-BR"
MAX_TOKENS  = 128     # nossos textos tem ~39 palavras; 128 cobre com folga e e rapido
MASCARA     = 0.15    # Devlin et al. (2018), replicado por Santos
LR_MLM      = 2e-5    # Sun et al. (2019), replicado por Santos
EPOCAS_MLM  = 2       # Santos: 2 epocas
BATCH       = 32

tok = AutoTokenizer.from_pretrained(MODELO_BASE)
# AutoModelForMaskedLM descarta a cabeca de classificacao e cria uma de MLM.
# O aviso de "newly initialized" e ESPERADO aqui.
mlm = AutoModelForMaskedLM.from_pretrained(MODELO_BASE)

ds = Dataset.from_pandas(corpus[["text"]]).train_test_split(test_size=10_000, seed=42)
ds = ds.map(lambda b: tok(b["text"], truncation=True, max_length=MAX_TOKENS),
            batched=True, remove_columns=["text"], desc="tokenizando")

collator = DataCollatorForLanguageModeling(tokenizer=tok, mlm=True,
                                           mlm_probability=MASCARA)

args = TrainingArguments(
    output_dir="mlm_out", learning_rate=LR_MLM,
    per_device_train_batch_size=BATCH, per_device_eval_batch_size=BATCH,
    num_train_epochs=EPOCAS_MLM, eval_strategy="epoch", save_strategy="no",
    logging_steps=200, fp16=True, report_to=[], dataloader_num_workers=2,
)
trainer = Trainer(model=mlm, args=args, train_dataset=ds["train"],
                  eval_dataset=ds["test"], data_collator=collator)

ppl_antes = math.exp(trainer.evaluate()["eval_loss"])
print(f"\\nPERPLEXIDADE ANTES: {ppl_antes:.4f}")
print("(referencia Santos: BERTimbau 1,51 -> FinBERT-PT-BR 1,24)")
"""),

    md("""
## 3. Treino MLM  *(~40 a 60 min)*
"""),

    code("""
trainer.train()
ppl_depois = math.exp(trainer.evaluate()["eval_loss"])
print(f"\\nPERPLEXIDADE ANTES : {ppl_antes:.4f}")
print(f"PERPLEXIDADE DEPOIS: {ppl_depois:.4f}")
print(f"ganho relativo     : {(ppl_antes-ppl_depois)/ppl_antes:+.2%}")
mlm.save_pretrained("finbert_petr4_mlm"); tok.save_pretrained("finbert_petr4_mlm")
print("\\nmodelo adaptado salvo em finbert_petr4_mlm/")
"""),

    md("""
> ### ⚠️ Aviso sobre o `config.json` publicado
>
> O modelo original declara `"problem_type": "multi_label_classification"` — o que está
> **errado** para três classes mutuamente exclusivas. Duas consequências:
>
> 1. **No treino:** o modelo usaria `BCEWithLogitsLoss` e esperaria alvos `[batch, 3]`.
>    Por isso passamos `problem_type="single_label_classification"` ao carregar. Sem isso
>    o treino quebra.
> 2. **Na inferência:** a `pipeline` aplica **sigmoide** em vez de *softmax*. Os **rótulos
>    não mudam** (a sigmoide é monotônica, o argmax é o mesmo), mas o `Score_Confianca`
>    que gravamos **não é probabilidade de classe**. Isso afeta o nosso ISM, que usa
>    `polaridade × confiança`. Ver a célula de diagnóstico no fim do notebook.
"""),

    md("""
## 4. Ajuste fino de sentimento com os 503 de Santos

O dataset foi publicado em `lucas-leme/Sentiments-FinBERT-PT-BR` — baixado direto do
Hugging Face, sem upload.

Protocolo replicado de Santos (2023, Seção 3.2): **gradual unfreezing**, `lr = 5e-6`,
**11 épocas**, validação cruzada substituída aqui por um *holdout* de 30% para caber no
tempo de sessão.
"""),

    code("""
santos = pd.read_csv("https://huggingface.co/datasets/lucas-leme/"
                     "Sentiments-FinBERT-PT-BR/resolve/main/sentiments.csv")
MAPA_S = {"Positivo":"Positive", "Negativo":"Negative", "Neutro":"Neutral"}
santos = santos[santos["sentiment"].isin(MAPA_S)].copy()
santos["label"] = santos["sentiment"].map(MAPA_S)
print(f"{len(santos)} textos rotulados (esperado: 503)")
print(santos["label"].value_counts().to_dict())
print(f"palavras: mediana={santos['text'].str.split().str.len().median():.0f}")
"""),

    code("""
from torch.utils.data import DataLoader, Dataset as TorchDS
from transformers import AutoModelForSequenceClassification
from sklearn.model_selection import train_test_split

CLASSES = ["Negative", "Neutral", "Positive"]
C2I = {c:i for i,c in enumerate(CLASSES)}
LR_FT, EPOCAS_FT = 5e-6, 11     # Santos, Secao 3.2
dev = "cuda"

class DS(TorchDS):
    def __init__(self, textos, rotulos):
        self.e = tok(list(textos), truncation=True, max_length=MAX_TOKENS,
                     padding="max_length", return_tensors="pt")
        self.y = torch.tensor([C2I[r] for r in rotulos])
    def __len__(self): return len(self.y)
    def __getitem__(self, i):
        it = {k: v[i] for k, v in self.e.items()}; it["labels"] = self.y[i]; return it

def blocos(m):
    return (getattr(m, "bert", None) or m.base_model)

def congelar(m):
    for p in blocos(m).parameters(): p.requires_grad = False

def descongelar(m, n):
    cam = blocos(m).encoder.layer
    for l in cam[max(0, len(cam)-n):]:
        for p in l.parameters(): p.requires_grad = True

def treinar(caminho_modelo, nome):
    Xtr, Xva, ytr, yva = train_test_split(
        santos["text"].values, santos["label"].values,
        test_size=0.30, stratify=santos["label"], random_state=42)
    # problem_type="single_label_classification" e OBRIGATORIO aqui.
    # O config.json publicado do FinBERT-PT-BR declara
    # "problem_type": "multi_label_classification", o que faz o modelo usar
    # BCEWithLogitsLoss e esperar alvos [batch, 3] em vez de [batch].
    # Sem esta linha o treino quebra com:
    #   ValueError: Target size ([16]) must be the same as input size ([16, 3])
    m = AutoModelForSequenceClassification.from_pretrained(
        caminho_modelo, num_labels=3, ignore_mismatched_sizes=True,
        problem_type="single_label_classification").to(dev)
    congelar(m)
    dtr = DataLoader(DS(Xtr, ytr), batch_size=16, shuffle=True)
    dva = DataLoader(DS(Xva, yva), batch_size=16)
    melhor, estado = float("inf"), None
    for ep in range(EPOCAS_FT):
        descongelar(m, ep + 1)          # uma camada a mais por epoca
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
        print(f"  [{nome}] epoca {ep+1:2d}/{EPOCAS_FT}  camadas={ep+1:2d}  loss_val={lv:.4f}")
        if lv < melhor:
            melhor, estado = lv, {k: v.cpu().clone() for k, v in m.state_dict().items()}
    m.load_state_dict(estado)
    return m

print("=== B: modelo ADAPTADO ao dominio ===")
modelo_B = treinar("finbert_petr4_mlm", "adaptado")
"""),

    md("""
## 5. Avaliação no nosso conjunto-ouro

Os 300 exemplos vão embutidos. A linha de base (`lucas-leme/FinBERT-PT-BR` como
publicado) já está medida: **acc 0,580 · F1 0,579 · kappa 0,371**.
"""),

    code(f'''
import base64, io
DADOS_B64 = "{B64}"
ouro = pd.read_csv(io.StringIO(base64.b64decode(DADOS_B64).decode("utf-8")))
print(f"conjunto-ouro: {{len(ouro)}} manchetes")
print(ouro["humano"].value_counts().to_dict())
'''),

    code("""
from sklearn.metrics import (accuracy_score, f1_score, cohen_kappa_score,
                             classification_report, confusion_matrix)

def prever(m, textos, bs=32):
    m.eval(); out = []
    for i in range(0, len(textos), bs):
        b = tok(list(textos[i:i+bs]), truncation=True, max_length=MAX_TOKENS,
                padding=True, return_tensors="pt").to(dev)
        with torch.no_grad():
            out += m(**b).logits.argmax(-1).cpu().tolist()
    return [CLASSES[i] for i in out]

def avaliar(y, p, nome, detalhe=False):
    r = dict(config=nome,
             acc=accuracy_score(y, p),
             f1=f1_score(y, p, average="macro", labels=CLASSES, zero_division=0),
             kappa=cohen_kappa_score(y, p, labels=CLASSES))
    print(f"  {nome:34s} acc={r['acc']:.4f}  F1={r['f1']:.4f}  kappa={r['kappa']:+.4f}")
    if detalhe:
        print(classification_report(y, p, labels=CLASSES, digits=3, zero_division=0))
        print("matriz (linhas=humano, colunas=modelo):")
        print(pd.DataFrame(confusion_matrix(y, p, labels=CLASSES),
                           index=CLASSES, columns=CLASSES).to_string())
    return r

res = []
print("=== RESULTADO ===")
res.append(avaliar(ouro["humano"], ouro["finbert_base"], "A - FinBERT-PT-BR publicado"))
ouro["pred_B"] = prever(modelo_B, ouro["titulo"].values)
res.append(avaliar(ouro["humano"], ouro["pred_B"], "B - adaptado ao dominio", True))

d_acc = res[1]["acc"] - res[0]["acc"]
d_f1  = res[1]["f1"]  - res[0]["f1"]
print(f"\\nDELTA acuracia : {d_acc:+.4f}")
print(f"DELTA F1-macro : {d_f1:+.4f}")
print(f"perplexidade   : {ppl_antes:.4f} -> {ppl_depois:.4f}")
print("\\n>>> Com n=300, diferenca menor que ~0,05 provavelmente NAO e significativa.")
print(">>> Confirmar com bootstrap antes de reportar qualquer ganho.")
"""),

    md("""
## 6. Consolidação
"""),

    code("""
import pandas as pd
tab = pd.DataFrame(res).round(4)
print(tab.to_string(index=False))
tab.to_csv("g3_resultados.csv", index=False)
ouro.to_csv("g3_predicoes.csv", index=False)

with open("g3_perplexidade.txt", "w") as f:
    f.write(f"antes={ppl_antes:.6f}\\ndepois={ppl_depois:.6f}\\n"
            f"ganho_relativo={(ppl_antes-ppl_depois)/ppl_antes:.6f}\\n"
            f"n_corpus={len(corpus)}\\nmax_tokens={MAX_TOKENS}\\n"
            f"mascara={MASCARA}\\nlr={LR_MLM}\\nepocas={EPOCAS_MLM}\\n")

try:
    from google.colab import files
    for a in ("g3_resultados.csv", "g3_predicoes.csv", "g3_perplexidade.txt"):
        files.download(a)
except Exception as e:
    print("baixe pelo painel de Arquivos:", type(e).__name__)
"""),

    md("""
## 7. Diagnóstico extra — sigmoide × *softmax* no modelo original

Consequência do `problem_type` errado: a `pipeline` aplica sigmoide, e o
`Score_Confianca` gravado no nosso corpus **não é probabilidade de classe**. Esta célula
quantifica a diferença.
"""),

    code("""
from transformers import AutoModelForSequenceClassification as AMSC
import torch.nn.functional as F

orig = AMSC.from_pretrained("lucas-leme/FinBERT-PT-BR").to(dev).eval()
print("problem_type declarado:", orig.config.problem_type)

amostra = ouro["titulo"].head(200).tolist()
enc = tok(amostra, truncation=True, max_length=MAX_TOKENS,
          padding=True, return_tensors="pt").to(dev)
with torch.no_grad():
    logits = orig(**enc).logits

sig = torch.sigmoid(logits)                 # o que a pipeline aplica hoje
smx = F.softmax(logits, dim=-1)             # o que deveria aplicar
i = logits.argmax(-1)
conf_sig = sig[range(len(i)), i].cpu().numpy()
conf_smx = smx[range(len(i)), i].cpu().numpy()

print(f"\\nconfianca do rotulo escolhido, em {len(amostra)} manchetes:")
print(f"  SIGMOIDE (atual) : media={conf_sig.mean():.4f}  max={conf_sig.max():.4f}")
print(f"  SOFTMAX (correto): media={conf_smx.mean():.4f}  max={conf_smx.max():.4f}")

concorda = (torch.sigmoid(logits).argmax(-1) == smx.argmax(-1)).float().mean().item()
print(f"\\nos ROTULOS coincidem em {concorda:.1%} dos casos "
      "(esperado: 100%, a sigmoide e monotonica)")
print("\\n>>> Os rotulos, e portanto acuracia/F1/kappa, estao CORRETOS.")
print(">>> O que muda de escala e o Score_Confianca — e o nosso ISM usa")
print(">>> polaridade x confianca. Vale recalcular o ISM com softmax.")
"""),

    md("""
---

### Como ler o resultado

| Situação | O que significa | O que fazer |
|---|---|---|
| **Perplexidade cai e F1 sobe > 0,05** | A adaptação funcionou | Reprocessar o corpus com o modelo B e refazer o ISM |
| **Perplexidade cai, F1 não sobe** | O modelo aprendeu o vocabulário, mas isso não se converte em classificação — coerente com as seis tentativas anteriores | Encerrar a linha; reportar como resultado |
| **Perplexidade não cai** | O FinBERT-PT-BR já cobria o subdomínio | Encerrar a linha; é achado interessante por si só |

**Em qualquer dos três casos há resultado reportável.** A perplexidade antes/depois é
número publicável, medido sem gabarito humano, e responde diretamente ao trabalho futuro
que Santos deixou em aberto: *"aplicar a metodologia para setores específicos da bolsa"*.
"""),
]

nb = {"cells": celulas,
      "metadata": {"colab": {"provenance": [], "toc_visible": True},
                   "kernelspec": {"name": "python3", "display_name": "Python 3"},
                   "language_info": {"name": "python"},
                   "accelerator": "GPU"},
      "nbformat": 4, "nbformat_minor": 0}

destino = OUTDIR / "g3_adaptacao_dominio_colab.ipynb"
destino.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"OK -> {destino.relative_to(RAIZ)}  ({destino.stat().st_size/1024:.0f} KB)")
