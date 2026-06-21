import React, { useEffect, useState } from "react";
import { api } from "../api.js";

const POR_PAGINA = 20;

export default function Noticias() {
  const [cats, setCats] = useState([]);
  const [filtros, setFiltros] = useState({ categoria: "", inicio: "", fim: "", q: "" });
  const [pagina, setPagina] = useState(1);
  const [dados, setDados] = useState({ total: 0, itens: [] });
  const [carregando, setCarregando] = useState(false);

  useEffect(() => { api.categorias().then(setCats).catch(() => {}); }, []);

  function buscar(p = 1) {
    setCarregando(true);
    api.noticias({ ...filtros, pagina: p, por_pagina: POR_PAGINA })
      .then((d) => { setDados(d); setPagina(p); })
      .finally(() => setCarregando(false));
  }
  useEffect(() => { buscar(1); /* eslint-disable-next-line */ }, []);

  const totPaginas = Math.max(1, Math.ceil(dados.total / POR_PAGINA));

  return (
    <div>
      <h1>Notícias coletadas</h1>
      <p className="sub">Corpus de notícias da Petrobras/PETR4 (2018–2025), com data e hora exatas, categorizado por tema.</p>

      <div className="painel">
        <div className="filtros">
          <div className="campo">
            <label htmlFor="f-cat">Categoria</label>
            <select id="f-cat" value={filtros.categoria}
              onChange={(e) => setFiltros({ ...filtros, categoria: e.target.value })}>
              <option value="">Todas as categorias</option>
              {cats.map((c) => <option key={c.id} value={c.id}>{c.rotulo} ({c.total.toLocaleString("pt-BR")})</option>)}
            </select>
          </div>
          <div className="campo">
            <label htmlFor="f-ini">De</label>
            <input id="f-ini" type="date" value={filtros.inicio}
              onChange={(e) => setFiltros({ ...filtros, inicio: e.target.value })} />
          </div>
          <div className="campo">
            <label htmlFor="f-fim">Até</label>
            <input id="f-fim" type="date" value={filtros.fim}
              onChange={(e) => setFiltros({ ...filtros, fim: e.target.value })} />
          </div>
          <div className="campo">
            <label htmlFor="f-q">Buscar no título</label>
            <input id="f-q" type="text" placeholder="ex.: dividendos" value={filtros.q}
              onChange={(e) => setFiltros({ ...filtros, q: e.target.value })}
              onKeyDown={(e) => e.key === "Enter" && buscar(1)} />
          </div>
          <button className="btn" onClick={() => buscar(1)}>Filtrar</button>
        </div>
      </div>

      <div className="painel">
        {carregando ? <div className="carregando">Carregando…</div> : (
          <>
            <p className="sub" style={{ margin: "0 0 8px" }}>
              <strong>{dados.total.toLocaleString("pt-BR")}</strong> notícias encontradas.
            </p>
            {dados.itens.map((n, i) => (
              <article className="noticia" key={i}>
                <div className="meta">
                  <span>{n.data}</span>
                  <span className="tag">{n.rotulo_categoria}</span>
                  {n.fonte && <span>{n.fonte}</span>}
                  {n.conjunto && <span>conjunto: {n.conjunto}</span>}
                </div>
                <h3>{n.url ? <a href={n.url} target="_blank" rel="noreferrer">{n.titulo}</a> : n.titulo}</h3>
                {n.resumo && n.resumo !== n.titulo && <p>{n.resumo}</p>}
              </article>
            ))}
            {dados.total > POR_PAGINA && (
              <div className="paginacao">
                <button className="btn sec" disabled={pagina <= 1} onClick={() => buscar(pagina - 1)}>‹ Anterior</button>
                <span>Página {pagina} de {totPaginas.toLocaleString("pt-BR")}</span>
                <button className="btn sec" disabled={pagina >= totPaginas} onClick={() => buscar(pagina + 1)}>Próxima ›</button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
