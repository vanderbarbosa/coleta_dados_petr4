# -*- coding: utf-8 -*-
# ==============================================================================
#   Monta o notebook do Colab que classifica os textos da CVM
#   Saída: CVM/colab/CVM_classificar_FinBERT.ipynb
#
#   Por que um notebook e não um script local: o PyTorch está quebrado nesta
#   máquina (c10.dll). A classificação roda no Colab; toda a estatística
#   continua rodando aqui.
#
#   Dois cuidados que o notebook toma, e que vêm de bugs já diagnosticados
#   nesta pesquisa:
#
#     1. NÃO usa transformers.pipeline(). A configuração do FinBERT-PT-BR traz
#        um problem_type que faz a pipeline aplicar SIGMOIDE em vez de softmax.
#        O rótulo sai certo, mas o escore de confiança sai em escala errada.
#        Aqui o softmax é aplicado à mão.
#
#     2. Normaliza CAIXA ALTA. O modelo é "cased" e se perde com texto todo
#        em maiúsculas. São 210 casos (1,0%) no corpus da CVM.
#
#   E aproveita a passagem para extrair os EMBEDDINGS, que é o caminho que
#   Hashami e Maldonado (2025) mostraram ser superior à cabeça de sentimento
#   (0,6694 contra 0,5368 no mesmo FinBERT).
# ==============================================================================
import json
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SAIDA = AQUI / "CVM_classificar_FinBERT.ipynb"


def md(txt):
    return {"cell_type": "markdown", "metadata": {}, "source": txt.splitlines(True)}


def code(txt):
    return {"cell_type": "code", "execution_count": None, "metadata": {},
            "outputs": [], "source": txt.splitlines(True)}


CELULAS = [
    md("""# Classificação dos comunicados da CVM com o FinBERT-PT-BR

**Dissertação de Vanderlei Barbosa da Silva — PUCPR/PPGIa**

Este caderno lê os 20.421 comunicados da CVM já coletados e produz, para cada um:

| Coluna | O que é |
|---|---|
| `Rotulo` | Positive, Negative ou Neutral |
| `p_pos`, `p_neu`, `p_neg` | as três probabilidades, por **softmax** |
| `Indice` | `p_pos − p_neg`, que vai de −1 a +1 |
| `emb_000 … emb_767` | o **embedding** do texto (opcional) |

## Dois cuidados, que vêm de bugs já diagnosticados nesta pesquisa

**1. Não se usa `pipeline()`.** A configuração do FinBERT-PT-BR traz um
`problem_type` que faz a pipeline aplicar **sigmoide** em vez de softmax. O
rótulo sai certo, mas o escore de confiança sai numa escala errada. Aqui o
softmax é aplicado à mão.

**2. Normaliza-se CAIXA ALTA.** O modelo é *cased* — distingue maiúscula de
minúscula — e se perde diante de texto inteiramente em maiúsculas.

## Como usar

1. Runtime → Alterar tipo de ambiente de execução → **GPU T4**
2. Rodar as células na ordem
3. Subir `cvm_para_classificar.csv` quando for pedido
4. Baixar `cvm_classificado.csv` ao final
"""),

    md("## 1. Instalar e conferir o ambiente"),
    code("""!pip -q install "transformers>=4.40" "torch" "pandas" "tqdm"

import torch, transformers
print("torch       :", torch.__version__)
print("transformers:", transformers.__version__)
print("GPU         :", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "NENHUMA — vai rodar em CPU, mais lento")
"""),

    md("""## 2. Subir o arquivo

Suba o `cvm_para_classificar.csv` que está em `coleta_dados_petr4/CVM/dados/`."""),
    code("""from google.colab import files
import pandas as pd

subidos = files.upload()
ARQ = list(subidos.keys())[0]

d = pd.read_csv(ARQ, dtype=str)
print(f"linhas: {len(d):,}")
print("colunas:", list(d.columns))
assert "Assunto" in d.columns, "falta a coluna Assunto"
d.head(3)
"""),

    md("""## 3. Preparar o texto

Duas correções antes de classificar:

- **caixa alta** → o modelo é *cased*; texto todo em maiúsculas o confunde;
- **espaços repetidos** → limpeza trivial."""),
    code("""import re

def normaliza(s: str) -> str:
    s = str(s or "").strip()
    letras = re.sub(r"[^A-Za-zÀ-ÿ]", "", s)
    # se as letras estão TODAS em maiúscula e há texto suficiente, converte
    if len(letras) > 10 and letras.upper() == letras:
        s = s.capitalize()
    return re.sub(r"\\s+", " ", s)

d["texto"] = d["Assunto"].map(normaliza)
n_alta = sum(1 for a, t in zip(d["Assunto"], d["texto"]) if str(a) != t)
print(f"textos normalizados: {n_alta:,}")
print(f"comprimento médio: {d['texto'].str.len().mean():.0f} caracteres")
d[["Assunto", "texto"]].head(3)
"""),

    md("""## 4. Carregar o modelo

`lucas-leme/FinBERT-PT-BR` — Santos, Bianchi e Costa (2023)."""),
    code("""from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODELO = "lucas-leme/FinBERT-PT-BR"
tok = AutoTokenizer.from_pretrained(MODELO)
mod = AutoModelForSequenceClassification.from_pretrained(MODELO)
mod.eval()
if torch.cuda.is_available():
    mod = mod.cuda()

print("mapa de rótulos:", mod.config.id2label)
print("problem_type   :", getattr(mod.config, "problem_type", None),
      " <- é por causa disto que NÃO usamos pipeline()")
"""),

    md("""## 5. Classificar

Softmax aplicado à mão. Os embeddings são a média dos estados ocultos da
última camada, ponderada pela máscara de atenção — o resumo numérico que o
modelo formou do texto."""),
    code("""import numpy as np
from tqdm.auto import tqdm

LOTE = 64
GUARDA_EMBEDDING = True     # ponha False se só quiser o sentimento

textos = d["texto"].tolist()
probs, embs = [], []

with torch.no_grad():
    for i in tqdm(range(0, len(textos), LOTE)):
        lote = textos[i:i + LOTE]
        x = tok(lote, padding=True, truncation=True, max_length=512,
                return_tensors="pt")
        if torch.cuda.is_available():
            x = {k: v.cuda() for k, v in x.items()}

        saida = mod(**x, output_hidden_states=GUARDA_EMBEDDING)

        # SOFTMAX à mão — a pipeline usaria sigmoide por causa do problem_type
        p = torch.softmax(saida.logits, dim=-1).cpu().numpy()
        probs.append(p)

        if GUARDA_EMBEDDING:
            h = saida.hidden_states[-1]                    # (lote, tokens, 768)
            m = x["attention_mask"].unsqueeze(-1).float()
            e = (h * m).sum(1) / m.sum(1).clamp(min=1e-9)  # média mascarada
            embs.append(e.cpu().numpy())

probs = np.vstack(probs)
print("probabilidades:", probs.shape)
print("soma de cada linha (tem de dar 1,0):", probs.sum(axis=1)[:5].round(4))
"""),

    md("## 6. Montar a saída"),
    code("""id2label = mod.config.id2label
nomes = [id2label[i] for i in range(probs.shape[1])]
print("ordem das colunas:", nomes)

for j, nome in enumerate(nomes):
    d[f"p_{nome.lower()[:3]}"] = probs[:, j]

d["Rotulo"] = [nomes[k] for k in probs.argmax(axis=1)]
d["Confianca"] = probs.max(axis=1)

# índice contínuo, de -1 (péssimo) a +1 (ótimo)
col_pos = [c for c in d.columns if c.startswith("p_pos")][0]
col_neg = [c for c in d.columns if c.startswith("p_neg")][0]
d["Indice"] = d[col_pos] - d[col_neg]

print(d["Rotulo"].value_counts())
print()
print(d["Rotulo"].value_counts(normalize=True).round(3))
print(f"\\nÍndice: média {d['Indice'].mean():+.4f} | mediana {d['Indice'].median():+.4f}")
"""),

    md("""### Conferência rápida

Se a distribuição vier com muito mais negativos que positivos, **é o viés já
documentado nesta pesquisa** — o mesmo modelo viu 21,9% de positivas onde 30
casas de análise viram 84,8%. Não é erro do caderno."""),
    code("""for cls in d["Rotulo"].unique():
    print(f"\\n===== {cls} =====")
    for t in d[d["Rotulo"] == cls]["texto"].head(4):
        print("  •", t[:95])
"""),

    md("## 7. Salvar e baixar"),
    code("""cols = [c for c in d.columns if c != "texto"]
d[cols].to_csv("cvm_classificado.csv", index=False, encoding="utf-8-sig")
print(f"cvm_classificado.csv — {len(d):,} linhas")

from google.colab import files
files.download("cvm_classificado.csv")
"""),

    md("""### Embeddings, em arquivo separado

São 768 números por texto. O arquivo fica grande, por isso vai em formato
comprimido (`.npz`), separado do CSV.

**Para que servem:** Hashami e Maldonado (2025) mostraram que o **mesmo**
FinBERT rende 0,5368 quando usado como classificador de sentimento e **0,6694**
quando usado como extrator de embeddings. Treze pontos de diferença. Guardar
agora custa um minuto e abre esse caminho."""),
    code("""if GUARDA_EMBEDDING:
    E = np.vstack(embs).astype(np.float32)
    print("embeddings:", E.shape)
    np.savez_compressed("cvm_embeddings.npz",
                        emb=E,
                        protocolo=d["Protocolo_Entrega"].values.astype(str))
    from google.colab import files
    files.download("cvm_embeddings.npz")
else:
    print("embeddings não foram guardados (GUARDA_EMBEDDING = False)")
"""),

    md("""---

## Ao terminar

Coloque os dois arquivos em `coleta_dados_petr4/CVM/dados/`:

- `cvm_classificado.csv`
- `cvm_embeddings.npz`

E rode `python CVM/08_rodada_B.py`, que faz a análise de direção."""),
]


def main() -> None:
    nb = {"cells": CELULAS,
          "metadata": {"kernelspec": {"display_name": "Python 3", "name": "python3"},
                       "language_info": {"name": "python"},
                       "colab": {"provenance": [], "toc_visible": True}},
          "nbformat": 4, "nbformat_minor": 0}
    SAIDA.write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"[OK] {SAIDA}")
    print(f"     {len(CELULAS)} células "
          f"({sum(1 for c in CELULAS if c['cell_type'] == 'code')} de código)")


if __name__ == "__main__":
    main()
