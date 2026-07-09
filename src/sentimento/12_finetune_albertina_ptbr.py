# -*- coding: utf-8 -*-
# ==============================================================================
#   DISSERTAÇÃO PETR4 — Experimento: fine-tuning de ENCODER de sentimento
#   Autor: Vanderlei Barbosa da Silva | Orientador: Prof. Dr. Julio Cesar Nievola
#
#   Responde ao item 8 da banca (jul/2026): "existem encoders melhores?".
#   Faz o fine-tuning de um encoder (padrão: Albertina PT-BR / DeBERTa) na tarefa
#   de sentimento financeiro em PT, usando o CONJUNTO-OURO rotulado por humanos, e
#   compara, no MESMO conjunto de teste, com o FinBERT-PT-BR atual — sob as mesmas
#   métricas já usadas na dissertação (acurácia, F1-macro, Kappa de Cohen).
#
#   NÃO inventa dados: usa apenas o conjunto-ouro (rótulos humanos) e os títulos
#   reais do corpus. Requer GPU (recomendado) + transformers/torch.
#
#   Uso:
#     python src/sentimento/12_finetune_albertina_ptbr.py \
#            --modelo PORTULAN/albertina-100m-portuguese-ptbr-encoder --epocas 4
#   Modelos sugeridos (item 8):
#     PORTULAN/albertina-100m-portuguese-ptbr-encoder   (leve; começar por aqui)
#     PORTULAN/albertina-900m-portuguese-ptbr-encoder   (SOTA PT; precisa mais GPU)
#     neuralmind/bert-large-portuguese-cased            (BERTimbau-large)
#     turing-usp/FinBertPTBR                            (FinBERT-PT alternativo)
# ==============================================================================
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
OURO = RAIZ / "Mestrado_PETR4" / "conjunto_ouro"
CORPUS = RAIZ / "Mestrado_PETR4" / "noticias_com_sentimento.csv"
SAIDA = RAIZ / "Mestrado_PETR4" / "experimentos_encoder"
SAIDA.mkdir(exist_ok=True)

FINBERT = "lucas-leme/FinBERT-PT-BR"
CLASSES = ["Negative", "Neutral", "Positive"]
MAPA_PT = {"Positivo": "Positive", "Negativo": "Negative", "Neutro": "Neutral",
           "Positive": "Positive", "Negative": "Negative", "Neutral": "Neutral"}


def carregar_gold():
    """Monta (titulo, rótulo humano) a partir do conjunto-ouro + títulos do corpus."""
    rot = pd.read_excel(OURO / "conjunto_ouro_para_rotular.xlsx", sheet_name="Rotular")
    gab = pd.read_csv(OURO / "conjunto_ouro_gabarito_modelo.csv")
    col_hum = next((c for c in rot.columns if "humano" in c.lower()), None)
    if col_hum is None:
        raise SystemExit("Coluna de rótulo humano não encontrada na aba 'Rotular'.")
    df = rot.merge(gab[["ID_OURO", "hash_titulo"]], on="ID_OURO", how="inner")
    df = df[df[col_hum].notna() & (df[col_hum].astype(str).str.strip() != "")]
    # títulos reais do corpus (por hash)
    titulos = pd.read_csv(CORPUS, usecols=["hash_titulo", "Titulo"]).drop_duplicates("hash_titulo")
    df = df.merge(titulos, on="hash_titulo", how="left").dropna(subset=["Titulo"])
    df["y"] = df[col_hum].map(MAPA_PT)
    df = df[df["y"].isin(CLASSES)]
    print(f"Conjunto-ouro utilizável: {len(df)} exemplos rotulados por humano com título.")
    return df[["Titulo", "y"]].reset_index(drop=True)


def metricas(y_true, y_pred):
    from sklearn.metrics import accuracy_score, f1_score, cohen_kappa_score
    return {
        "acuracia": round(float(accuracy_score(y_true, y_pred)), 4),
        "f1_macro": round(float(f1_score(y_true, y_pred, average="macro")), 4),
        "kappa_cohen": round(float(cohen_kappa_score(y_true, y_pred)), 4),
        "n": int(len(y_true)),
    }


def avaliar_finbert(textos, y_true):
    """Baseline: FinBERT-PT-BR SEM re-treino, no mesmo teste."""
    from transformers import pipeline
    nlp = pipeline("sentiment-analysis", model=FINBERT, truncation=True, max_length=512, device=-1)
    pred = []
    for t in textos:
        L = str(nlp(t)[0]["label"]).upper()
        pred.append("Positive" if "POS" in L else ("Negative" if "NEG" in L else "Neutral"))
    return metricas(y_true, pred)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelo", default="PORTULAN/albertina-100m-portuguese-ptbr-encoder")
    ap.add_argument("--epocas", type=int, default=4)
    ap.add_argument("--lr", type=float, default=2e-5)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    import torch
    from sklearn.model_selection import train_test_split
    from transformers import (AutoTokenizer, AutoModelForSequenceClassification,
                              TrainingArguments, Trainer, DataCollatorWithPadding)
    from datasets import Dataset

    gold = carregar_gold()
    if len(gold) < 60:
        raise SystemExit(
            f"\n[BLOQUEADO] O conjunto-ouro tem apenas {len(gold)} exemplos rotulados por HUMANO.\n"
            "O fine-tuning de encoder exige a rotulagem manual da aba 'Rotular' de\n"
            "Mestrado_PETR4/conjunto_ouro/conjunto_ouro_para_rotular.xlsx (coluna 'Sentimento_Humano').\n"
            "Rotule (idealmente >=200 exemplos) e rode novamente. Nada é inventado.")
    lab2id = {c: i for i, c in enumerate(CLASSES)}
    gold["label"] = gold["y"].map(lab2id)

    # Split cronológico não se aplica (é rotulagem de sentimento); split estratificado.
    tr, tmp = train_test_split(gold, test_size=0.30, stratify=gold["label"], random_state=args.seed)
    val, te = train_test_split(tmp, test_size=0.50, stratify=tmp["label"], random_state=args.seed)
    print(f"treino={len(tr)}  validação={len(val)}  teste={len(te)}")

    tok = AutoTokenizer.from_pretrained(args.modelo)
    def prep(ds):
        d = Dataset.from_pandas(ds[["Titulo", "label"]].rename(columns={"Titulo": "text"}))
        return d.map(lambda e: tok(e["text"], truncation=True, max_length=256), batched=True)
    dtr, dval, dte = prep(tr), prep(val), prep(te)

    modelo = AutoModelForSequenceClassification.from_pretrained(
        args.modelo, num_labels=3, id2label={i: c for c, i in lab2id.items()}, label2id=lab2id)

    def compute(p):
        pred = np.argmax(p.predictions, axis=1)
        return {k: v for k, v in metricas(p.label_ids, pred).items() if k != "n"}

    targs = TrainingArguments(
        output_dir=str(SAIDA / "ckpt"), num_train_epochs=args.epocas,
        per_device_train_batch_size=args.batch, per_device_eval_batch_size=args.batch,
        learning_rate=args.lr, eval_strategy="epoch", save_strategy="no",
        seed=args.seed, logging_steps=20, report_to=[])
    tr_obj = Trainer(model=modelo, args=targs, train_dataset=dtr, eval_dataset=dval,
                     tokenizer=tok, data_collator=DataCollatorWithPadding(tok), compute_metrics=compute)
    tr_obj.train()

    # Avaliação no TESTE (mesmo conjunto para os dois modelos)
    pred_te = np.argmax(tr_obj.predict(dte).predictions, axis=1)
    id2lab = {i: c for c, i in lab2id.items()}
    m_novo = metricas([id2lab[i] for i in te["label"]], [id2lab[i] for i in pred_te])
    m_finbert = avaliar_finbert(list(te["Titulo"]), list(te["y"]))

    res = {"modelo_novo": args.modelo, "metricas_modelo_novo": m_novo,
           "baseline_finbert_ptbr": m_finbert,
           "delta_acuracia_pp": round(100 * (m_novo["acuracia"] - m_finbert["acuracia"]), 2),
           "n_treino": len(tr), "n_val": len(val), "n_teste": len(te)}
    nome = args.modelo.split("/")[-1]
    (SAIDA / f"resultado_{nome}.json").write_text(
        json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=2))
    print(f"\n✓ Salvo em {SAIDA / ('resultado_' + nome + '.json')}")


if __name__ == "__main__":
    main()
