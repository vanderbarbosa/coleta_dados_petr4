# Site da Pesquisa (PETR4) — React + FastAPI, hospedado no GitHub Pages

Aplicação interativa que apresenta os **dados reais** da pesquisa: consulta de notícias
(por categoria/data/texto), preços da PETR4 (por data/ano/mês), estatísticas descritivas,
uma demonstração prática (estudo de evento) e a avaliação de direção a partir de uma notícia.

## 🌐 Acesso (de qualquer lugar)

**https://vanderbarbosa.github.io/coleta_dados_petr4/**

O site é publicado automaticamente no **GitHub Pages** a cada atualização do frontend
(workflow [`.github/workflows/deploy-pages.yml`](../.github/workflows/deploy-pages.yml)).

### Como funciona a hospedagem

O GitHub Pages serve apenas conteúdo **estático**, então a aplicação usa uma arquitetura híbrida:

| Recurso | No site publicado (Pages) | Em desenvolvimento local |
|---|---|---|
| Notícias, preços, estatísticas, eventos, demonstração, resultados | **Snapshot estático** (JSON em `frontend/public/dados/`, gerado por `exportar_estatico.py`) | Backend FastAPI ao vivo (proxy `/api`) |
| Avaliação de notícia (direção) | Backend externo de previsão **se configurado** (`VITE_API_URL`); senão, **cálculo no navegador** (regras da taxonomia + léxico, ver `frontend/src/previsao_local.js`) | Backend FastAPI (FinBERT-PT-BR + XGBoost) |

Ou seja: o site **funciona sozinho** no Pages (sem servidor). Um backend de previsão é
**opcional** e apenas troca a previsão do navegador pela previsão completa com FinBERT + XGBoost.

## Arquitetura

- **frontend/** — SPA em React + Vite (gráficos com Recharts). Publicada no GitHub Pages.
- **backend/** — API em FastAPI (Python). Uso local (dados + previsão) e/ou deploy externo
  do endpoint de previsão (ver `backend/README_HF.md`).
- **exportar_estatico.py** — gera o snapshot estático de dados consumido pelo site publicado.

## Como executar (local, funcionalidade completa)

> 📋 Para rodar em **outra máquina** (ex.: apresentação à banca), com a frase
> passando por todos os classificadores, siga o guia passo a passo:
> [**COMO_RODAR_LOCAL.md**](COMO_RODAR_LOCAL.md).

### 1. Backend (ambiente conda `petr4` — pandas, torch/FinBERT e xgboost)
```bash
cd site/backend
conda run -n petr4 uvicorn app:app --reload --port 8000
# Documentação interativa da API: http://localhost:8000/docs
```

### 2. Frontend (ambiente conda `web`, que tem Node)
```bash
cd site/frontend
conda run -n web npm install      # apenas na primeira vez
conda run -n web npm run dev      # abre em http://localhost:5173
```
Em `npm run dev`, o Vite encaminha `/api` para o backend (porta 8000), com queda para o
snapshot estático caso o backend esteja fora do ar.

> Em rede com proxy/SSL: `conda run -n web npm config set strict-ssl false`.

## Atualizar o snapshot estático (após mudar os dados da pesquisa)

```bash
python site/exportar_estatico.py      # regrava frontend/public/dados/*.json
```
Faça commit dos JSON atualizados; o deploy do Pages os publica automaticamente.

## Publicar o site (primeira vez)

1. Faça o push do repositório para o GitHub.
2. Em **Settings → Pages → Build and deployment**, selecione **Source: "GitHub Actions"**.
3. O workflow *Deploy site (GitHub Pages)* builda e publica em
   `https://<usuario>.github.io/<repo>/`.

## Ligar a previsão ao vivo (opcional)

1. Publique o backend de previsão (ex.: Hugging Face Spaces) — ver
   [`backend/README_HF.md`](backend/README_HF.md).
2. Em **Settings → Secrets and variables → Actions → Variables**, crie a variável
   `VITE_API_URL` com a URL do backend (ex.: `https://vander-petr4-api.hf.space`).
3. Rode novamente o workflow *Deploy site (GitHub Pages)*.

## Notas

- O site publicado usa uma **amostra** do corpus de notícias (para manter o download leve);
  os totais reais aparecem na aba *Estatísticas*. A execução local acessa o corpus completo.
- Nenhum dado é inventado — tudo vem das bases reais da pesquisa.
- Conteúdo de natureza acadêmica; não constitui recomendação de investimento.
