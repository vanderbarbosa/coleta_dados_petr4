// Cliente da API da pesquisa (backend FastAPI).
// Em dev, o Vite encaminha /api para http://localhost:8000 (ver vite.config.js).

async function get(caminho, params = {}) {
  const url = new URL(caminho, window.location.origin);
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== "") url.searchParams.set(k, v);
  });
  const resp = await fetch(url.pathname + url.search);
  if (!resp.ok) throw new Error(`Falha na API (${resp.status})`);
  return resp.json();
}

async function post(caminho, corpo) {
  const resp = await fetch(caminho, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(corpo),
  });
  if (!resp.ok) throw new Error(`Falha na API (${resp.status})`);
  return resp.json();
}

export const api = {
  saude: () => get("/api/saude"),
  categorias: () => get("/api/categorias"),
  noticias: (params) => get("/api/noticias", params),
  precos: (params) => get("/api/precos", params),
  estatisticas: () => get("/api/estatisticas"),
  prever: (texto) => post("/api/prever", { texto }),
  eventos: () => get("/api/eventos"),
  demonstracao: (params) => get("/api/demonstracao", params),
};
