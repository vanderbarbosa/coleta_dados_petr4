import React, { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, ReferenceLine } from "recharts";
import { api } from "../api.js";

function VarCard({ rotulo, valor }) {
  const cor = valor == null ? "var(--tinta-2)" : valor > 0 ? "var(--verde)" : valor < 0 ? "var(--vermelho)" : "var(--tinta-2)";
  const sinal = valor == null ? "—" : `${valor > 0 ? "▲ +" : valor < 0 ? "▼ " : ""}${valor}%`;
  return (
    <div className="cartao" style={{ textAlign: "center" }}>
      <div className="num" style={{ color: cor, fontSize: "1.5rem" }}>{sinal}</div>
      <div className="rot">{rotulo}</div>
    </div>
  );
}

export default function Demonstracao() {
  const [eventos, setEventos] = useState([]);
  const [sel, setSel] = useState(null);
  const [dados, setDados] = useState(null);
  const [carregando, setCarregando] = useState(false);

  useEffect(() => {
    api.eventos().then((evs) => { setEventos(evs); if (evs[0]) escolher(evs[0]); }).catch(() => {});
    // eslint-disable-next-line
  }, []);

  function escolher(ev) {
    setSel(ev.id); setCarregando(true); setDados(null);
    api.demonstracao({ data: ev.data, janela: 18 })
      .then((d) => setDados({ ...d, evento: ev }))
      .finally(() => setCarregando(false));
  }

  const v = dados?.variacoes;
  const corLinha = v && v.dia != null ? (v.dia >= 0 ? "#15924a" : "#d33") : "#0b5394";

  return (
    <div>
      <h1>Demonstração prática</h1>
      <p className="sub">
        Estudo de evento com <strong>dados reais</strong>: selecione um acontecimento notório e veja as
        notícias daquele dia e como o preço da PETR4 efetivamente se moveu — a notícia influenciando o ativo na prática.
      </p>

      <div className="painel">
        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
          {eventos.map((ev) => (
            <button key={ev.id} className={`btn ${sel === ev.id ? "" : "sec"}`} onClick={() => escolher(ev)}>
              {ev.titulo}
            </button>
          ))}
        </div>
      </div>

      {carregando && <div className="carregando"><span className="spinner" /> Carregando o evento…</div>}

      {dados && !carregando && (
        <>
          <div className="painel">
            <h2 style={{ marginTop: 0 }}>{dados.evento.titulo}</h2>
            <p style={{ marginTop: 0, color: "var(--tinta-2)" }}>{dados.evento.contexto}</p>
            <p className="sub" style={{ margin: "6px 0 0" }}>
              Data de referência: <strong>{dados.data_evento}</strong> · fechamento R$ {dados.preco_evento}
              {dados.ism_dia != null && <> · sentimento da mídia no dia (ISM): <strong>{dados.ism_dia}</strong>
                {" "}({dados.ism_dia < 0 ? "predomínio negativo" : dados.ism_dia > 0 ? "predomínio positivo" : "neutro"})</>}
            </p>
          </div>

          <div className="cartoes" style={{ marginBottom: 22 }}>
            <VarCard rotulo="No dia do evento" valor={v.dia} />
            <VarCard rotulo="Após 1 pregão" valor={v.d1} />
            <VarCard rotulo="Após 5 pregões" valor={v.d5} />
            <VarCard rotulo="Após 10 pregões" valor={v.d10} />
          </div>

          <div className="painel">
            <h2 style={{ marginTop: 0 }}>Preço da PETR4 em torno do evento</h2>
            <div style={{ width: "100%", height: 340 }}>
              <ResponsiveContainer>
                <LineChart data={dados.serie} margin={{ top: 10, right: 18, bottom: 8, left: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#eef2f6" />
                  <XAxis dataKey="data" tick={{ fontSize: 11 }} minTickGap={28} />
                  <YAxis tick={{ fontSize: 11 }} domain={["auto", "auto"]} width={54} tickFormatter={(x) => `R$${x}`} />
                  <Tooltip formatter={(x) => `R$ ${Number(x).toFixed(2)}`} />
                  <ReferenceLine x={dados.data_evento} stroke="#d33" strokeDasharray="4 3"
                    label={{ value: "evento", position: "top", fill: "#d33", fontSize: 11 }} />
                  <Line type="monotone" dataKey="fechamento" stroke={corLinha} dot={false} strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <p className="sub" style={{ margin: "8px 0 0" }}>
              A linha tracejada marca o dia do evento. {v.dia != null && (
                <>No pregão do evento, a PETR4 <strong style={{ color: v.dia >= 0 ? "var(--verde)" : "var(--vermelho)" }}>
                  {v.dia >= 0 ? "subiu" : "caiu"} {Math.abs(v.dia)}%</strong>.</>
              )}
            </p>
          </div>

          {dados.noticias.length > 0 && (
            <div className="painel">
              <h2 style={{ marginTop: 0 }}>Notícias reais daquele dia</h2>
              {dados.noticias.map((n, i) => (
                <article className="noticia" key={i}>
                  <div className="meta">
                    <span className="tag">{n.categoria}</span>
                    {n.fonte && <span>{n.fonte}</span>}
                  </div>
                  <h3 style={{ marginBottom: 0 }}>{n.titulo}</h3>
                </article>
              ))}
            </div>
          )}

          <div className="aviso">
            Demonstração de natureza acadêmica, com dados reais de notícias e de preços. Não constitui recomendação de investimento.
          </div>
        </>
      )}
    </div>
  );
}
