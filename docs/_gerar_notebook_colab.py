# -*- coding: utf-8 -*-
# Gera um notebook Colab AUTÔNOMO (dados embutidos) para o fine-tuning/comparação
# de encoders de sentimento. Saída: notebooks/finetune_encoder_colab.ipynb
import base64, csv, io, json
from pathlib import Path
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
OURO = RAIZ / "Mestrado_PETR4" / "conjunto_ouro"
OUTDIR = RAIZ / "notebooks"; OUTDIR.mkdir(exist_ok=True)
MAPA = {"Positivo": "Positive", "Negativo": "Negative", "Neutro": "Neutral",
        "Positive": "Positive", "Negative": "Negative", "Neutral": "Neutral"}

# ── Extrai os 300 rótulos (título, humano, FinBERT) e embute em base64 ────────
rot = pd.read_excel(OURO / "conjunto_ouro_para_rotular.xlsx", sheet_name="Rotular")
gab = pd.read_csv(OURO / "conjunto_ouro_gabarito_modelo.csv")
d = rot.merge(gab[["ID_OURO", "Label_Sentimento"]], on="ID_OURO", how="inner")
d = d[d["Sentimento_Humano"].notna() & d["Título"].notna()].copy()
d["humano"] = d["Sentimento_Humano"].map(MAPA)
d["finbert"] = d["Label_Sentimento"].map(MAPA)
d = d[d["humano"].isin(["Negative", "Neutral", "Positive"])]

buf = io.StringIO()
w = csv.writer(buf)
w.writerow(["id", "titulo", "humano", "finbert"])
for _, r in d.iterrows():
    w.writerow([r["ID_OURO"], str(r["Título"]).replace("\n", " ").strip(), r["humano"], r["finbert"]])
B64 = base64.b64encode(buf.getvalue().encode("utf-8")).decode("ascii")
print(f"Embutidos {len(d)} exemplos | base64 {len(B64)/1024:.1f} KB")


def code(src):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [],
            "source": src}
def md(src):
    return {"cell_type": "markdown", "metadata": {}, "source": src}


c_intro = md(
"""# Fine-tuning de encoder de sentimento — PETR4

Compara, por **validação cruzada 5-fold**, encoders em português (**Albertina/DeBERTa**, **BERTimbau**)
*ajustados* no conjunto-ouro rotulado por humano, contra o **FinBERT-PT-BR** atual — sob **acurácia,
F1-macro e Kappa de Cohen**. Os 300 exemplos rotulados estão **embutidos** neste notebook (nada a subir).

### Como usar
1. **Ambiente de execução → Alterar o tipo de ambiente → GPU (T4)**.
2. **Ambiente de execução → Executar tudo**. Pronto — o resultado aparece na última célula.

> Base pequena (300) ⇒ resultado *piloto*; o k-fold dá estabilidade. Dissertação PETR4 · Vanderlei Barbosa da Silva.""")

c_install = code(
"""!pip -q install -U transformers scikit-learn pandas >/dev/null 2>&1
import torch
print("PyTorch", torch.__version__, "| GPU:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU — troque para GPU em Ambiente de execução!")""")

c_dados = code(
'''import base64, io, pandas as pd
DADOS_B64 = "%s"
df = pd.read_csv(io.StringIO(base64.b64decode(DADOS_B64).decode("utf-8")))
print(len(df), "manchetes rotuladas")
print("humano :", df.humano.value_counts().to_dict())
print("finbert:", df.finbert.value_counts().to_dict())
df.head(3)''' % B64)

c_func = code(
'''import numpy as np, time
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, f1_score, cohen_kappa_score
from torch.utils.data import DataLoader, TensorDataset
from torch.optim import AdamW
from transformers import AutoTokenizer, AutoModelForSequenceClassification

CLASSES = ["Negative","Neutral","Positive"]; ID = {c:i for i,c in enumerate(CLASSES)}
dev = "cuda" if torch.cuda.is_available() else "cpu"
textos = df.titulo.astype(str).tolist()
y = np.array([ID[c] for c in df.humano]); fin = df.finbert.tolist()

def met(yt, yp):
    return (accuracy_score(yt,yp), f1_score(yt,yp,average="macro"),
            cohen_kappa_score(yt,yp,labels=CLASSES))

def avaliar_encoder(modelo, cv=5, epocas=3, maxlen=128, seed=42):
    # fp32 sempre: o DeBERTa (Albertina) NAO funciona com fp16 (overflow no masked_fill).
    grande = ("900m" in modelo) or ("large" in modelo)
    batch = 8 if grande else 16
    tok = AutoTokenizer.from_pretrained(modelo)
    enc = tok(textos, truncation=True, max_length=maxlen, padding="max_length", return_tensors="pt")
    ids, mask = enc["input_ids"], enc["attention_mask"]
    skf = StratifiedKFold(n_splits=cv, shuffle=True, random_state=seed)
    novo, base = [], []; t0=time.time()
    for k,(tr,te) in enumerate(skf.split(np.zeros(len(y)), y),1):
        torch.manual_seed(seed)
        m = AutoModelForSequenceClassification.from_pretrained(modelo, num_labels=3).to(dev)
        if grande:
            m.config.use_cache = False; m.gradient_checkpointing_enable()
        dl = DataLoader(TensorDataset(ids[tr],mask[tr],torch.tensor(y[tr])), batch_size=batch, shuffle=True)
        opt = AdamW(m.parameters(), lr=2e-5)
        m.train()
        for _ in range(epocas):
            for bi,bm,by in dl:
                opt.zero_grad()
                out = m(input_ids=bi.to(dev), attention_mask=bm.to(dev), labels=by.to(dev))
                out.loss.backward(); opt.step()
        m.eval(); preds=[]
        with torch.no_grad():
            for i in range(0,len(te),64):
                idx=te[i:i+64]
                lo=m(input_ids=ids[idx].to(dev), attention_mask=mask[idx].to(dev)).logits
                preds.extend(lo.argmax(1).cpu().numpy())
        yt=[CLASSES[c] for c in y[te]]
        novo.append(met(yt,[CLASSES[c] for c in preds]))
        base.append(met(yt,[fin[i] for i in te]))
        del m; torch.cuda.empty_cache() if dev=="cuda" else None
        print(f"  fold {k}/{cv}: {modelo.split('/')[-1]} acc={novo[-1][0]:.3f} kappa={novo[-1][2]:.3f} | {time.time()-t0:.0f}s")
    A=np.array(novo); B=np.array(base)
    return {"acc":A[:,0].mean(),"acc_dp":A[:,0].std(),"f1":A[:,1].mean(),"kappa":A[:,2].mean(),
            "fin_acc":B[:,0].mean(),"fin_kappa":B[:,2].mean()}
print("Funções prontas. Device:", dev)''')

c_run = code(
'''MODELOS = [
    "PORTULAN/albertina-100m-portuguese-ptbr-encoder",
    "neuralmind/bert-base-portuguese-cased",       # BERTimbau-base
    "neuralmind/bert-large-portuguese-cased",      # BERTimbau-large
    # "PORTULAN/albertina-900m-portuguese-ptbr-encoder",  # so em GPU grande (A100). Em fp32 pode estourar a T4; DeBERTa nao aceita fp16.
]
linhas = []
for mdl in MODELOS:
    print("==>", mdl)
    r = avaliar_encoder(mdl)
    linhas.append({"Encoder": mdl.split("/")[-1], "Acurácia (%)": round(r["acc"]*100,2),
                   "±dp": round(r["acc_dp"]*100,2), "F1-macro (%)": round(r["f1"]*100,2),
                   "Kappa": round(r["kappa"],3), "FinBERT acc (%)": round(r["fin_acc"]*100,2),
                   "FinBERT Kappa": round(r["fin_kappa"],3),
                   "Δacc (pp)": round((r["acc"]-r["fin_acc"])*100,2)})
import pandas as pd
res = pd.DataFrame(linhas).sort_values("Acurácia (%)", ascending=False)
res''')

c_save = code(
'''res.to_csv("resultado_encoders_petr4.csv", index=False, encoding="utf-8-sig")
print("Baseline FinBERT-PT-BR (mesmos folds): acc ~%.2f%% | Kappa ~%.3f" % (linhas[0]["FinBERT acc (%)"], linhas[0]["FinBERT Kappa"]))
print("\\nInterprete Δacc/ΔKappa: positivo = o encoder ajustado SUPERA o FinBERT no sentimento.")
try:
    from google.colab import files; files.download("resultado_encoders_petr4.csv")
except Exception: pass''')

nb = {"cells": [c_intro, c_install, c_dados, c_func, c_run, c_save],
      "metadata": {"accelerator": "GPU",
                   "colab": {"provenance": [], "toc_visible": True},
                   "kernelspec": {"display_name": "Python 3", "name": "python3"},
                   "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}

out = OUTDIR / "finetune_encoder_colab.ipynb"
out.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
print("✓", out)
