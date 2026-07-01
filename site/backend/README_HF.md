---
title: PETR4 API de Previsão
emoji: 📈
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# Backend de previsão — PETR4 (FinBERT-PT-BR + XGBoost)

Este é o backend **opcional** de previsão ao vivo do site da dissertação
*"O Impacto do Sentimento de Notícias Financeiras na Previsão de Direção e
Volatilidade do Ativo PETR4"* (Vanderlei Barbosa da Silva). O site (GitHub Pages)
funciona sem ele — a previsão então roda no navegador. Com este backend no ar, a
previsão passa a usar o **FinBERT-PT-BR** e o **modelo XGBoost** treinados.

## Como publicar no Hugging Face Spaces (grátis)

1. Crie um Space: https://huggingface.co/new-space → **SDK: Docker**.
2. No repositório do Space, coloque:
   - `app.py`          (copie de `site/backend/app.py`)
   - `Dockerfile`      (copie de `site/backend/Dockerfile`)
   - `requirements.txt`(copie de `site/backend/requirements.txt`)
   - `taxonomia.py`    (copie de `src/comum/taxonomia.py`)
   - `README.md`       (este arquivo, com o cabeçalho YAML acima)
   - `dados/modelo_xgb_fusion.json` e `dados/modelo_meta.json`
     (copie de `Mestrado_PETR4/`). Só esses dois arquivos são necessários para a
     previsão; são pequenos (< 300 KB).
3. O Space builda sozinho. Teste: `https://<usuario>-<space>.hf.space/api/saude`
   e a documentação interativa em `/docs`.

> O modelo FinBERT-PT-BR (`lucas-leme/FinBERT-PT-BR`) é baixado do Hugging Face
> na primeira previsão. A primeira chamada leva alguns segundos.

## Ligar o site a este backend

No repositório do **frontend** (GitHub), defina a variável de repositório
`VITE_API_URL` com a URL do Space (ex.: `https://vander-petr4-api.hf.space`) em
*Settings → Secrets and variables → Actions → Variables* e rode o workflow
*Deploy site (GitHub Pages)*. O site passará a chamar este backend na aba
"Avaliar notícia".

## Rodar localmente (contêiner)

```bash
cd site/backend
mkdir -p dados && cp ../../Mestrado_PETR4/modelo_*.json dados/
cp ../../src/comum/taxonomia.py .
docker build -t petr4-api .
docker run -p 7860:7860 petr4-api      # http://localhost:7860/docs
```
