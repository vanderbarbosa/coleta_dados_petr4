# -*- coding: utf-8 -*-
# ==============================================================================
#   DISSERTAÇÃO PETR4 — Fine-tuning de ENCODER de sentimento (k-fold, CPU/GPU)
#   Autor: Vanderlei Barbosa da Silva | Orientador: Prof. Dr. Julio Cesar Nievola
#
#   Responde ao item 8 da banca. Faz o fine-tuning de um encoder (padrão: Albertina
#   PT-BR/DeBERTa) na tarefa de sentimento financeiro em PT, usando o CONJUNTO-OURO
#   rotulado por HUMANO, e compara, nos MESMOS folds, com o FinBERT-PT-BR atual.
#
#   Como a base rotulada é pequena (300), usa VALIDAÇÃO CRUZADA estratificada
#   (k-fold) e reporta média ± desvio de acurácia, F1-macro e Kappa de Cohen — em
#   vez de um único teste minúsculo. Laço de treino manual (sem 'datasets'/'accelerate').
#   Roda em CPU (suficiente aqui) ou GPU NVIDIA se houver. NÃO inventa rótulos.
#
#   Uso: python src/sentimento/12_finetune_albertina_ptbr.py \
#            --modelo PORTULAN/albertina-100m-portuguese-ptbr-encoder --cv 5 --epocas 3
# ==============================================================================
import argparse, json, time
from pathlib import Path
import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
OURO = RAIZ / "Mestrado_PETR4" / "conjunto_ouro"
SAIDA = RAIZ / "Mestrado_PETR4" / "experimentos_encoder"
SAIDA.mkdir(exist_ok=True)
FINBERT = "lucas-leme/FinBERT-PT-BR"
CLASSES = ["Negative", "Neutral", "Positive"]
MAPA = {"Positivo": "Positive", "Negativo": "Negative", "Neutro": "Neutral",
        "Positive": "Positive", "Negative": "Negative", "Neutral": "Neutral"}


def _ssl_off():
    # HF via proxy/SSL relaxado (o modelo é baixado uma vez e fica em cache).
    try:
        import huggingface_hub, requests, urllib3
        urllib3.disable_warnings()
        huggingface_hub.configure_http_backend(
            backend_factory=lambda: (lambda s: (s.__setattr__("verify", False) or s))(requests.Session()))
    except Exception:
        pass


def carregar_gold():
    rot = pd.read_excel(OURO / "conjunto_ouro_para_rotular.xlsx", sheet_name="Rotular")
    gab = pd.read_csv(OURO / "conjunto_ouro_gabarito_modelo.csv")
    df = rot.merge(gab[["ID_OURO", "Label_Sentimento"]], on="ID_OURO", how="inner")
    df = df[df["Sentimento_Humano"].notna() & df["Título"].notna()].copy()
    df["y"] = df["Sentimento_Humano"].map(MAPA)
    df["finbert"] = df["Label_Sentimento"].map(MAPA)
    df = df[df["y"].isin(CLASSES)].reset_index(drop=True)
    print(f"Conjunto-ouro: {len(df)} manchetes rotuladas por humano.")
    return df


def metricas(y_true, y_pred):
    from sklearn.metrics import accuracy_score, f1_score, cohen_kappa_score
    return (round(float(accuracy_score(y_true, y_pred)), 4),
            round(float(f1_score(y_true, y_pred, average="macro")), 4),
            round(float(cohen_kappa_score(y_true, y_pred, labels=CLASSES)), 4))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelo", default="PORTULAN/albertina-100m-portuguese-ptbr-encoder")
    ap.add_argument("--cv", type=int, default=5)
    ap.add_argument("--epocas", type=int, default=3)
    ap.add_argument("--lr", type=float, default=2e-5)
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--maxlen", type=int, default=160)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    _ssl_off()

    import torch
    from torch.utils.data import DataLoader, TensorDataset
    from torch.optim import AdamW
    from sklearn.model_selection import StratifiedKFold
    from transformers import AutoTokenizer, AutoModelForSequenceClassification

    dev = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Modelo: {args.modelo} | device: {dev} | k-fold: {args.cv} | épocas: {args.epocas}")
    gold = carregar_gold()
    lab2id = {c: i for i, c in enumerate(CLASSES)}
    textos = gold["Título"].astype(str).tolist()
    y = np.array([lab2id[c] for c in gold["y"]])
    fin = gold["finbert"].tolist()

    tok = AutoTokenizer.from_pretrained(args.modelo)
    enc = tok(textos, truncation=True, max_length=args.maxlen, padding="max_length", return_tensors="pt")
    ids, mask = enc["input_ids"], enc["attention_mask"]

    skf = StratifiedKFold(n_splits=args.cv, shuffle=True, random_state=args.seed)
    novo, base = [], []
    t0 = time.time()
    for k, (tr, te) in enumerate(skf.split(np.zeros(len(y)), y), start=1):
        torch.manual_seed(args.seed)
        modelo = AutoModelForSequenceClassification.from_pretrained(
            args.modelo, num_labels=3).to(dev)
        ds = TensorDataset(ids[tr], mask[tr], torch.tensor(y[tr]))
        dl = DataLoader(ds, batch_size=args.batch, shuffle=True)
        opt = AdamW(modelo.parameters(), lr=args.lr)
        modelo.train()
        for ep in range(args.epocas):
            for bi, bm, by in dl:
                opt.zero_grad()
                out = modelo(input_ids=bi.to(dev), attention_mask=bm.to(dev), labels=by.to(dev))
                out.loss.backward()
                opt.step()
        modelo.eval()
        preds = []
        with torch.no_grad():
            for i in range(0, len(te), 32):
                idx = te[i:i + 32]
                lo = modelo(input_ids=ids[idx].to(dev), attention_mask=mask[idx].to(dev)).logits
                preds.extend(lo.argmax(1).cpu().numpy())
        y_te = [CLASSES[c] for c in y[te]]
        y_pr = [CLASSES[c] for c in preds]
        novo.append(metricas(y_te, y_pr))
        base.append(metricas(y_te, [fin[i] for i in te]))
        del modelo
        if dev == "cuda":
            torch.cuda.empty_cache()
        print(f"  fold {k}/{args.cv}: novo acc={novo[-1][0]:.3f} kappa={novo[-1][2]:.3f} | "
              f"FinBERT acc={base[-1][0]:.3f} kappa={base[-1][2]:.3f} | {time.time()-t0:.0f}s")

    def agg(L):
        A = np.array(L)
        return {"acuracia_media": round(A[:, 0].mean() * 100, 2), "acuracia_dp": round(A[:, 0].std() * 100, 2),
                "f1_macro_media": round(A[:, 1].mean() * 100, 2),
                "kappa_media": round(A[:, 2].mean(), 3), "kappa_dp": round(A[:, 2].std(), 3)}

    res = {"data": time.strftime("%Y-%m-%d"), "modelo_novo": args.modelo, "cv": args.cv,
           "epocas": args.epocas, "n": len(y), "device": dev,
           "modelo_novo_metricas": agg(novo), "finbert_baseline_metricas": agg(base),
           "delta_acuracia_pp": round(agg(novo)["acuracia_media"] - agg(base)["acuracia_media"], 2),
           "delta_kappa": round(agg(novo)["kappa_media"] - agg(base)["kappa_media"], 3)}
    nome = args.modelo.split("/")[-1]
    (SAIDA / f"resultado_{nome}_{res['data']}.json").write_text(
        json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=2))
    print(f"\n✓ Salvo em experimentos_encoder/resultado_{nome}_{res['data']}.json")


if __name__ == "__main__":
    main()
