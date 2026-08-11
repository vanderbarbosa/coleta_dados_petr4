# -*- coding: utf-8 -*-
# =============================================================================
#  Gera o notebook Colab do GAP G6 — LLM generativo x encoder especializado
#  Saída: notebooks/g6_llm_vs_encoder_colab.ipynb
#
#  O QUE PREENCHE
#  Teles e Figueiredo (2025) mostram LLMs superando modelos clássicos em
#  sentimento financeiro — mas inteiramente sobre corpora em INGLÊS, e sem
#  incluir o FinBERT-PT-BR entre os avaliados. A comparação em português,
#  contra um encoder de domínio, não existe na literatura.
#
#  DIFERENÇAS DELIBERADAS EM RELAÇÃO AO TRABALHO DELES
#    idioma ....... português (eles: inglês)
#    corpus ....... nosso conjunto-ouro, ativo específico (eles: 3 genéricos)
#    encoder ...... FinBERT-PT-BR incluído (eles: ausente)
#    prompt ....... instrução LITERAL de Santos, ancorada em rentabilidade
#                   (eles: uma frase genérica)
#    determinismo . temperatura 0 e repetição, para medir a variância
#
#  Usa LLM ABERTO rodando na própria GPU do Colab — sem chave de API.
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
w.writerow(["id", "categoria", "titulo", "humano", "finbert"])
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
# G6 — LLM generativo × encoder especializado, em português

Teles e Figueiredo (2025) mostram LLMs superando modelos clássicos em sentimento
financeiro. Mas testam **só em inglês**, e **não incluem o FinBERT-PT-BR**. A comparação
em português, contra um encoder de domínio, não existe.

### O que muda aqui

| | Teles e Figueiredo (2025) | Este experimento |
|---|---|---|
| Idioma | inglês | **português** |
| Corpus | 3 conjuntos genéricos | **nosso conjunto-ouro** |
| Encoder de domínio | ausente | **FinBERT-PT-BR incluído** |
| *Prompt* | uma frase genérica | **instrução literal de Santos** |
| Determinismo | não discutido | **temperatura 0 + repetição** |

### Três resultados possíveis, todos publicáveis

- **LLM ganha** → evidência para migrar; achado inédito em PT-BR
- **Encoder ganha** → justificativa empírica para mantê-lo, que hoje não temos
- **Empatam** → o argumento passa a ser custo, reprodutibilidade e determinismo

> **Runtime → T4 GPU.** Tempo: ~20 minutos. Linha de base a bater: **acc 0,580 · κ 0,371**.
"""),

    code("""
!pip -q install -U transformers accelerate scikit-learn 2>/dev/null
import torch
print("GPU:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "NENHUMA")
"""),

    code(f'''
import base64, io, re
import pandas as pd

DADOS_B64 = "{B64}"
ouro = pd.read_csv(io.StringIO(base64.b64decode(DADOS_B64).decode("utf-8")))
print(f"conjunto-ouro: {{len(ouro)}} manchetes")
print(ouro["humano"].value_counts().to_dict())
'''),

    md("""
## O *prompt*

Usa a **instrução literal de Santos (2022, Seção 4.2.3)** — a mesma dada aos três
anotadores humanos que produziram os 503 rótulos com que o FinBERT-PT-BR foi treinado.

Isso torna a comparação justa: o LLM recebe exatamente a mesma definição operacional que
gerou o gabarito do encoder. E, se houver ganho, ele é **atribuível ao modelo**, não a um
*prompt* mais elaborado.
"""),

    code('''
INSTRUCAO_SANTOS = (
    "Classifique a notícia considerando se o texto implicaria em uma "
    "rentabilidade Positiva, Negativa ou Neutra."
)

def montar_prompt(titulo):
    return (
        "Você é um analista do mercado financeiro brasileiro.\\n\\n"
        f"{INSTRUCAO_SANTOS}\\n"
        "Responda com uma única palavra: Positiva, Negativa ou Neutra.\\n\\n"
        f'Manchete: "{titulo}"\\n\\n'
        "Resposta:"
    )

MAPA_RESP = {
    "positiva":"Positive", "positivo":"Positive", "positive":"Positive",
    "negativa":"Negative", "negativo":"Negative", "negative":"Negative",
    "neutra":"Neutral",   "neutro":"Neutral",    "neutral":"Neutral",
}

def normalizar(resposta):
    t = re.sub(r"[^a-zà-ú]", " ", str(resposta).strip().lower())
    for tok_ in t.split():
        if tok_ in MAPA_RESP:
            return MAPA_RESP[tok_]
    return None

print(montar_prompt(ouro["titulo"].iloc[0]))
'''),

    md("""
## Carga do LLM

`Qwen2.5-3B-Instruct` — aberto, sem *gating*, bom em português e cabe numa T4 em fp16.
Se faltar memória, troque para a variante `1.5B` na primeira linha.
"""),

    code('''
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

MODELO_LLM = "Qwen/Qwen2.5-3B-Instruct"    # alternativa: "Qwen/Qwen2.5-1.5B-Instruct"

tk = AutoTokenizer.from_pretrained(MODELO_LLM)
llm = AutoModelForCausalLM.from_pretrained(
    MODELO_LLM, torch_dtype=torch.float16, device_map="auto")
llm.eval()
print("carregado:", MODELO_LLM)

@torch.no_grad()
def classificar_llm(titulos, bs=16, seed=42):
    torch.manual_seed(seed)
    saidas = []
    for i in range(0, len(titulos), bs):
        msgs = [[{"role": "user", "content": montar_prompt(t)}]
                for t in titulos[i:i+bs]]
        textos = [tk.apply_chat_template(m, tokenize=False, add_generation_prompt=True)
                  for m in msgs]
        enc = tk(textos, return_tensors="pt", padding=True,
                 padding_side="left").to(llm.device)
        out = llm.generate(**enc, max_new_tokens=6, do_sample=False,   # temperatura 0
                           pad_token_id=tk.eos_token_id)
        for j in range(len(textos)):
            gerado = out[j][enc["input_ids"].shape[1]:]
            saidas.append(tk.decode(gerado, skip_special_tokens=True))
        if (i // bs) % 5 == 0:
            print(f"  {min(i+bs, len(titulos))}/{len(titulos)}")
    return saidas
'''),

    md("""
## Execução — três repetições

Mesmo com `do_sample=False`, execuções repetidas podem divergir por não determinismo de
kernels em GPU. **Teles e Figueiredo não mediram isso.** Nós medimos.
"""),

    code("""
titulos = ouro["titulo"].tolist()
execucoes = []
for r in range(1, 4):
    print(f"execucao {r}/3")
    brutas = classificar_llm(titulos, seed=42)
    preds = [normalizar(b) for b in brutas]
    nao_rec = sum(p is None for p in preds)
    if nao_rec:
        print(f"  {nao_rec} respostas nao reconhecidas -> Neutral")
        print("  exemplos:", [b for b, p in zip(brutas, preds) if p is None][:3])
    execucoes.append([p or "Neutral" for p in preds])

iguais = sum(len(set(v)) == 1 for v in zip(*execucoes))
print(f"\\nestabilidade entre as 3 execucoes: {iguais}/{len(titulos)} = "
      f"{iguais/len(titulos):.1%} identicas")
ouro["pred_llm"] = execucoes[0]
"""),

    md("""
## Resultado
"""),

    code("""
from sklearn.metrics import (accuracy_score, f1_score, cohen_kappa_score,
                             classification_report, confusion_matrix)
CLASSES = ["Negative", "Neutral", "Positive"]

def avaliar(y, p, nome, detalhe=False):
    r = dict(config=nome,
             acc=accuracy_score(y, p),
             f1=f1_score(y, p, average="macro", labels=CLASSES, zero_division=0),
             kappa=cohen_kappa_score(y, p, labels=CLASSES))
    print(f"  {nome:36s} acc={r['acc']:.4f}  F1={r['f1']:.4f}  kappa={r['kappa']:+.4f}")
    if detalhe:
        print(classification_report(y, p, labels=CLASSES, digits=3, zero_division=0))
        print("matriz (linhas=humano, colunas=modelo):")
        print(pd.DataFrame(confusion_matrix(y, p, labels=CLASSES),
                           index=CLASSES, columns=CLASSES).to_string())
    return r

res = []
print("=== COMPARACAO ===")
res.append(avaliar(ouro["humano"], ouro["finbert"], "FinBERT-PT-BR (encoder)"))
res.append(avaliar(ouro["humano"], ouro["pred_llm"], "LLM (Qwen2.5-3B)", True))

d = res[1]["f1"] - res[0]["f1"]
print(f"\\nDELTA F1-macro: {d:+.4f}")
print(">>> Com n=300, diferenca menor que ~0,05 provavelmente NAO e significativa.")

print("\\n=== recall da classe Neutral (onde o encoder falha) ===")
for nome, col in [("FinBERT", "finbert"), ("LLM", "pred_llm")]:
    m = ((ouro["humano"] == "Neutral") & (ouro[col] == "Neutral")).sum()
    print(f"  {nome:10s} {m}/{(ouro['humano']=='Neutral').sum()} = "
          f"{m/(ouro['humano']=='Neutral').sum():.3f}")

print("\\n=== por categoria ===")
for cat, g in ouro.groupby("categoria"):
    if len(g) < 15: continue
    a1 = accuracy_score(g["humano"], g["finbert"])
    a2 = accuracy_score(g["humano"], g["pred_llm"])
    print(f"  {cat:26s} n={len(g):3d}  encoder={a1:.3f}  LLM={a2:.3f}  delta={a2-a1:+.3f}")
"""),

    code("""
import pandas as pd
tab = pd.DataFrame(res).round(4)
print(tab.to_string(index=False))
tab.to_csv("g6_resultados.csv", index=False)
ouro.to_csv("g6_predicoes.csv", index=False)
try:
    from google.colab import files
    files.download("g6_resultados.csv"); files.download("g6_predicoes.csv")
except Exception as e:
    print("baixe pelo painel de Arquivos:", type(e).__name__)
"""),

    md("""
---

### Ressalvas a declarar na dissertação, qualquer que seja o resultado

1. **Não determinismo.** Reportar a estabilidade medida entre as três execuções. Um
   encoder é determinístico; um LLM não é — e isso tem peso em reprodutibilidade.
2. **Custo.** Um LLM de 3B na GPU é ordens de magnitude mais caro por item que um
   encoder de 110M. Para 205 mil notícias, a diferença é operacional, não acadêmica.
3. **Modelos generativos alteram valores numéricos** em texto financeiro
   (ABÍLIO; COELHO; SILVA, 2024). Aqui a tarefa é classificação e não geração, o que
   mitiga o risco — mas a ressalva deve constar.
4. **`Qwen2.5-3B` não é o estado da arte.** Se o resultado for promissor, vale repetir
   com um modelo maior via API antes de concluir.
"""),
]

nb = {"cells": celulas,
      "metadata": {"colab": {"provenance": [], "toc_visible": True},
                   "kernelspec": {"name": "python3", "display_name": "Python 3"},
                   "language_info": {"name": "python"},
                   "accelerator": "GPU"},
      "nbformat": 4, "nbformat_minor": 0}

destino = OUTDIR / "g6_llm_vs_encoder_colab.ipynb"
destino.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"OK -> {destino.relative_to(RAIZ)}  ({destino.stat().st_size/1024:.0f} KB)")
