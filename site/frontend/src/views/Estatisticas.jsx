import React, { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { api } from "../api.js";

export default function Estatisticas() {
  const [est, setEst] = useState(null);
  const [erro, setErro] = useState(null);
  useEffect(() => { api.estatisticas().then(setEst).catch((e) => setErro(e.message)); }, []);

  if (erro) return <div className="aviso">Falha ao carregar estatísticas: {erro}</div>;
  if (!est) return <div className="carregando"><span className="spinner" /> Carregando estatísticas…</div>;

  const porAno = Object.entries(est.por_ano).map(([ano, n]) => ({ ano, n }));
  const porCat = est.por_categoria.map((c) => ({ nome: c.rotulo.replace(/^CAT\d+\s*[—-]\s*/, ""), n: c.total }));
  const porPortal = Object.entries(est.por_portal).map(([nome, n]) => ({ nome, n }));

  return (
    <div>
      <h1>Estatísticas do corpus e da série</h1>
      <p className="sub">
        Período das notícias: {est.periodo_noticias[0]} a {est.periodo_noticias[1]} ·
        Período dos preços: {est.periodo_precos[0]} a {est.periodo_precos[1]}.
      </p>

      <div className="cartoes">
        <div className="cartao"><div className="num">{est.noticias_total.toLocaleString("pt-BR")}</div><div className="rot">Notícias</div></div>
        <div className="cartao"><div className="num">{est.pregoes_total.toLocaleString("pt-BR")}</div><div className="rot">Pregões</div></div>
        <div className="cartao"><div className="num">{est.lead_lag_pct}%</div><div className="rot">Após o fechamento (Lead-Lag)</div></div>
        <div className="cartao"><div className="num">{est.por_categoria.length}</div><div className="rot">Categorias</div></div>
      </div>

      <div className="painel">
        <h2 style={{ marginTop: 0 }}>Notícias por ano</h2>
        <div style={{ width: "100%", height: 280 }}>
          <ResponsiveContainer>
            <BarChart data={porAno}><CartesianGrid strokeDasharray="3 3" stroke="#eef2f6" />
              <XAxis dataKey="ano" tick={{ fontSize: 12 }} /><YAxis tick={{ fontSize: 11 }} width={56}
                tickFormatter={(v) => v.toLocaleString("pt-BR")} />
              <Tooltip formatter={(v) => v.toLocaleString("pt-BR")} />
              <Bar dataKey="n" fill="#2c7bb6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="painel">
        <h2 style={{ marginTop: 0 }}>Notícias por categoria temática</h2>
        <div style={{ width: "100%", height: 320 }}>
          <ResponsiveContainer>
            <BarChart data={porCat} layout="vertical" margin={{ left: 40 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#eef2f6" />
              <XAxis type="number" tick={{ fontSize: 11 }} tickFormatter={(v) => v.toLocaleString("pt-BR")} />
              <YAxis type="category" dataKey="nome" tick={{ fontSize: 11 }} width={150} />
              <Tooltip formatter={(v) => v.toLocaleString("pt-BR")} />
              <Bar dataKey="n" fill="#0b5394" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="painel">
        <h2 style={{ marginTop: 0 }}>Notícias por portal (fonte)</h2>
        <table>
          <thead><tr><th>Portal</th><th>Notícias</th></tr></thead>
          <tbody>
            {porPortal.map((p) => (
              <tr key={p.nome}><td>{p.nome}</td><td>{p.n.toLocaleString("pt-BR")}</td></tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
