# Como rodar a aplicação localmente (com a classificação completa)

Guia para executar o site em **outra máquina** (ex.: para a apresentação à banca),
com a frase passando por **todo o processamento**: FinBERT-PT-BR (sentimento) +
taxonomia (categoria) + XGBoost (direção) + leitura econômica setorial.

> Diferente do site publicado no GitHub Pages (que avalia no navegador, por regras),
> a execução **local** usa os classificadores reais. É esta que você deve usar na banca.

---

## 0. Pré-requisitos (instalar uma vez na máquina nova)

- **Git** — https://git-scm.com/download/win
- **Miniconda** (ou Anaconda) — https://docs.conda.io/en/latest/miniconda.html
  (traz o Python; usaremos um ambiente isolado)
- **Node.js 20+** — https://nodejs.org (para o frontend)

---

## 1. Baixar o projeto

```bash
git clone https://github.com/vanderbarbosa/coleta_dados_petr4.git
cd coleta_dados_petr4
```

O clone **já traz** o modelo treinado (`Mestrado_PETR4/modelo_xgb_fusion.json` e
`modelo_meta.json`) e a taxonomia — tudo que a previsão precisa. (As bases de
notícias/preços, grandes, não vêm no clone; as telas de dados usam um *snapshot*
que já acompanha o repositório. A **previsão** não depende dessas bases.)

---

## 2. Backend (classificadores) — Python

Crie o ambiente e instale as dependências da previsão:

```bash
conda create -n petr4 python=3.11 -y
conda activate petr4
pip install -r site/backend/requirements.txt
```

Suba a API:

```bash
cd site/backend
uvicorn app:app --reload --port 8000
```

Deixe este terminal aberto. Teste em http://localhost:8000/docs (deve abrir a doc da API).

> **Rede com proxy/SSL** (ex.: universidade): antes do `pip install`, rode
> `pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r site/backend/requirements.txt`.

---

## 3. Frontend (interface) — Node

Em **outro terminal**, na raiz do projeto:

```bash
cd site/frontend
npm install        # apenas na 1ª vez
npm run dev        # abre em http://localhost:5173
```

> No Windows, se aparecer "node não reconhecido", garanta que o Node está no PATH
> (reinstale marcando "Add to PATH") ou use o Node do seu ambiente conda `web`.
> Proxy/SSL: `npm config set strict-ssl false` antes do `npm install`.

Abra **http://localhost:5173** → aba **"Avaliar notícia"**.

---

## 4. IMPORTANTE — aquecer o FinBERT ANTES da apresentação

Na **primeira** avaliação, o modelo FinBERT-PT-BR (~450 MB) é baixado do Hugging
Face e fica em cache. **Faça isso com antecedência, numa rede boa:**

1. Com backend + frontend rodando, vá em "Avaliar notícia".
2. Clique em **"Exemplo 1"** e aguarde (~20–40 s na 1ª vez).
3. Pronto — o modelo fica em cache (`~/.cache/huggingface`) e as próximas
   avaliações são rápidas e **funcionam mesmo offline**.

Não deixe para baixar o FinBERT na frente da banca.

---

## 5. Como CONFIRMAR que está usando a classificação completa

Ao avaliar uma frase, verifique na tela:

- ✅ **Está completo** se aparecerem o **índice do FinBERT** (ex.: "Sentimento:
  Negativo (−0,87)") e a **P(alta) do XGBoost** no painel "Modelo estatístico".
- ⚠️ **Está em modo navegador** (backend não conectado) se aparecer o aviso azul
  *"ℹ️ Previsão calculada no seu navegador"*. Nesse caso, confira se o backend
  (passo 2) está rodando na porta 8000 e recarregue a página.

---

## Resumo do fluxo da frase (o que a banca verá)

```
Frase da banca
   → FinBERT-PT-BR ....... sentimento (Positivo/Negativo/Neutro + índice)
   → Taxonomia (152 termos) relevância e categoria (CAT1–CAT7)
   → XGBoost Data Fusion .. P(alta) do próximo pregão
   → Leitura setorial ..... direção econômica (Kilian/Hamilton)
   → Veredito ............. tendência de ALTA / BAIXA / indefinida
```

A "Jornada da previsão" na tela anima exatamente essas etapas, uma engrenagem por classificador.
