// Cliente da API da pesquisa.
//
// Arquitetura de hospedagem (GitHub Pages + backend externo opcional):
//
//  • DADOS (notícias, preços, estatísticas, eventos, demonstração, resultados)
//    — no site publicado (produção) vêm do SNAPSHOT ESTÁTICO em `public/dados/`
//    (gerado por `site/exportar_estatico.py`). É confiável e não depende de
//    servidor. Em desenvolvimento local (`npm run dev`), vêm do backend FastAPI
//    ao vivo (proxy `/api` → http://localhost:8000).
//
//  • PREVISÃO (`prever`) — usa o backend externo definido em `VITE_API_URL`
//    (ex.: um Hugging Face Space com FinBERT-PT-BR + XGBoost). Se não houver
//    backend, ou se ele estiver indisponível/hibernando, a leitura econômica
//    setorial é calculada NO PRÓPRIO NAVEGADOR (ver `previsao_local.js`).

import { preverLocal } from "./previsao_local.js";

// URL do backend externo de previsão (sem barra final).
const API_URL = (import.meta.env.VITE_API_URL || "").replace(/\/$/, "");
// Prefixo dos arquivos estáticos, respeitando o `base` do Vite (subpasta do Pages).
const ESTATICO = `${import.meta.env.BASE_URL}dados`;
const DEV = import.meta.env.DEV;

async function fetchJson(url, opts) {
  const resp = await fetch(url, opts);
  if (!resp.ok) throw new Error(`Falha na API (${resp.status})`);
  return resp.json();
}

// GET no backend local (apenas em desenvolvimento, via proxy /api).
async function backendGet(caminho, params = {}) {
  const url = new URL(caminho, window.location.origin);
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== "") url.searchParams.set(k, v);
  });
  return fetchJson(url.pathname + url.search);
}

async function estatico(nome) {
  return fetchJson(`${ESTATICO}/${nome}`);
}

// ── Filtros aplicados no cliente sobre o snapshot estático ────────────────────
function filtrarNoticias(dados, { categoria, inicio, fim, q, pagina = 1, por_pagina = 20 }) {
  let itens = dados.itens || [];
  if (categoria) itens = itens.filter((n) => n.categoria === categoria);
  if (inicio) itens = itens.filter((n) => (n.data || "").slice(0, 10) >= inicio);
  if (fim) itens = itens.filter((n) => (n.data || "").slice(0, 10) <= fim);
  if (q) { const t = q.toLowerCase(); itens = itens.filter((n) => (n.titulo || "").toLowerCase().includes(t)); }
  const total = itens.length;
  const pp = Math.max(1, Math.min(Number(por_pagina), 100));
  const ini = Math.max(0, (Number(pagina) - 1) * pp);
  return {
    total, pagina: Number(pagina), por_pagina: pp, itens: itens.slice(ini, ini + pp),
    amostragem: dados.total_corpus ? { corpus: dados.total_corpus, amostra: dados.amostra } : null,
  };
}

function filtrarPrecos(itens, { ano, mes, inicio, fim }) {
  return itens.filter((d) => {
    const ymd = d.data;
    if (ano && ymd.slice(0, 4) !== String(ano)) return false;
    if (mes && Number(ymd.slice(5, 7)) !== Number(mes)) return false;
    if (inicio && ymd < inicio) return false;
    if (fim && ymd > fim) return false;
    return true;
  });
}

// Em dev usa o backend ao vivo (com fallback estático); em produção, estático.
async function dados(fnBackend, fnEstatico) {
  if (DEV) {
    try { return await fnBackend(); }
    catch (e) { /* backend local fora do ar → snapshot estático */ }
  }
  return fnEstatico();
}

export const api = {
  saude: () => dados(() => backendGet("/api/saude"),
    async () => ({ status: "ok", servico: "PETR4 (snapshot estático)" })),

  categorias: () => dados(() => backendGet("/api/categorias"),
    () => estatico("categorias.json")),

  estatisticas: () => dados(() => backendGet("/api/estatisticas"),
    () => estatico("estatisticas.json")),

  noticias: (params) => dados(() => backendGet("/api/noticias", params),
    async () => filtrarNoticias(await estatico("noticias.json"), params)),

  precos: (params) => dados(() => backendGet("/api/precos", params),
    async () => filtrarPrecos(await estatico("precos.json"), params)),

  eventos: () => dados(() => backendGet("/api/eventos"),
    () => estatico("eventos.json")),

  demonstracao: (params) => dados(() => backendGet("/api/demonstracao", params),
    () => estatico(`demonstracao/${params.data}.json`)),

  resultados: () => dados(() => backendGet("/api/resultados"),
    () => estatico("resultados.json")),

  // Previsão: backend externo (FinBERT + XGBoost) se configurado; senão, ou em
  // caso de falha, executa a leitura econômica setorial no navegador.
  prever: async (texto) => {
    const alvo = API_URL ? `${API_URL}/api/prever` : (DEV ? "/api/prever" : null);
    if (alvo) {
      try {
        return await fetchJson(alvo, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ texto }),
        });
      } catch (e) { /* backend de previsão indisponível → motor local */ }
    }
    return preverLocal(texto);
  },
};
