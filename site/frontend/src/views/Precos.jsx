import React, { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { api } from "../api.js";

const ANOS = [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025];
const MESES = ["", "Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"];

export default function Precos() {
  const [filtros, setFiltros] = useState({ ano: "2025", mes: "" });
  const [dados, setDados] = useState([]);
  const [carregando, setCarregando] = useState(false);

  function buscar() {
    setCarregando(true);
    api.precos(filtros).then(setDados).finally(() => setCarregando(false));
  }
  useEffect(() => { buscar(); /* eslint-disable-next-line */ }, []);

  const fech = dados.map((d) => d.fechamento);
  const min = fech.length ? Math.min(...fech) : 0;
  const max = fech.length ? Math.max(...fech) : 0;

  return (
    <div>
      <h1>Preços do ativo PETR4</h1>
      <p className="sub">Série diária de cotações (Yahoo Finance / B3), filtrável por ano e mês.</p>

      <div className="painel">
        <div className="filtros">
          <div className="campo">
            <label htmlFor="p-ano">Ano</label>
            <select id="p-ano" value={filtros.ano} onChange={(e) => setFiltros({ ...filtros, ano: e.target.value })}>
              <option value="">Todos</option>
              {ANOS.map((a) => <option key={a} value={a}>{a}</option>)}
            </select>
          </div>
          <div className="campo">
            <label htmlFor="p-mes">Mês</label>
            <select id="p-mes" value={filtros.mes} onChange={(e) => setFiltros({ ...filtros, mes: e.target.value })}>
              <option value="">Todos</option>
              {ANOS.length && MESES.map((m, i) => i > 0 && <option key={i} value={i}>{m}</option>)}
            </select>
          </div>
          <button className="btn" onClick={buscar}>Filtrar</button>
        </div>
      </div>

      <div className="painel">
        {carregando ? <div className="carregando">Carregando…</div> : (
          <>
            <p className="sub" style={{ margin: "0 0 8px" }}>
              <strong>{dados.length.toLocaleString("pt-BR")}</strong> pregões
              {fech.length ? ` · fechamento entre R$ ${min.toFixed(2)} e R$ ${max.toFixed(2)}` : ""}
            </p>
            <div style={{ width: "100%", height: 340 }}>
              <ResponsiveContainer>
                <LineChart data={dados} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#eef2f6" />
                  <XAxis dataKey="data" tick={{ fontSize: 11 }} minTickGap={40} />
                  <YAxis tick={{ fontSize: 11 }} domain={["auto", "auto"]} width={52}
                    tickFormatter={(v) => `R$${v}`} />
                  <Tooltip formatter={(v) => `R$ ${Number(v).toFixed(2)}`} labelStyle={{ color: "#333" }} />
                  <Line type="monotone" dataKey="fechamento" stroke="#0b5394" dot={false} strokeWidth={1.6} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </>
        )}
      </div>

      {!carregando && dados.length > 0 && (
        <div className="painel">
          <h2 style={{ marginTop: 0 }}>Tabela de pregões</h2>
          <div style={{ maxHeight: 360, overflow: "auto" }}>
            <table>
              <thead><tr><th>Data</th><th>Abertura</th><th>Fechamento</th><th>Mín.</th><th>Máx.</th><th>Log-retorno</th><th>Volume</th></tr></thead>
              <tbody>
                {dados.map((d, i) => (
                  <tr key={i}>
                    <td>{d.data}</td><td>R$ {d.abertura.toFixed(2)}</td><td>R$ {d.fechamento.toFixed(2)}</td>
                    <td>R$ {d.minima.toFixed(2)}</td><td>R$ {d.maxima.toFixed(2)}</td>
                    <td>{(d.log_retorno * 100).toFixed(2)}%</td><td>{d.volume.toLocaleString("pt-BR")}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
