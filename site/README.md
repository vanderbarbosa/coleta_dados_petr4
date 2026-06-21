# Site da Pesquisa (PETR4) — FastAPI + React

Aplicação interativa que apresenta os **dados reais** da pesquisa: consulta de notícias
(por categoria/data/texto), preços da PETR4 (por data/ano/mês), estatísticas descritivas e,
futuramente, a previsão de direção a partir de uma notícia e a demonstração prática.

## Arquitetura
- **backend/** — API em FastAPI (Python), serve os dados de `Mestrado_PETR4/`.
- **frontend/** — SPA em React + Vite (gráficos com Recharts).

## Como executar (local)

### 1. Backend (ambiente conda `petr4` — tem pandas, torch/FinBERT e xgboost)
```bash
cd site/backend
conda run -n petr4 uvicorn app:app --reload --port 8000
# ou: C:/Users/Vanderlei/anaconda3.12/envs/petr4/Scripts/uvicorn.exe app:app --port 8000
# Documentação interativa da API: http://localhost:8000/docs
```
> Os endpoints de **dados** funcionam em qualquer ambiente com pandas; o endpoint de
> **previsão** (`POST /api/prever`) exige o `petr4` (carrega o FinBERT-PT-BR e o modelo XGBoost).
> Os imports de torch/transformers são *lazy* — só carregam na primeira previsão.

### 2. Frontend (ambiente conda `web`, que tem Node)
```bash
cd site/frontend
conda run -n web npm install      # apenas na primeira vez
conda run -n web npm run dev      # abre em http://localhost:5173
```
O Vite encaminha `/api` para o backend (porta 8000) automaticamente.

## Notas
- Em rede com proxy/SSL, rode antes: `conda run -n web npm config set strict-ssl false`.
- Funcionalidades de **previsão** e **demonstração** dependem dos modelos treinados (Etapa 4);
  serão habilitadas após o processamento completo do sentimento.
- Nenhum dado é inventado — tudo vem das bases reais da pesquisa.
