import React, { useEffect, useState } from "react";

const TXT = {
  alta: "Tende à ALTA", baixa: "Tende à BAIXA", indefinida: "Direção indefinida",
  sem_influencia: "Sem influência", neutra: "Sem direção clara", contextual: "Efeito contextual",
};
const SETA = { alta: "▲", baixa: "▼", indefinida: "●", sem_influencia: "○", neutra: "●", contextual: "◆" };

// Caminhos do "gráfico de preço" desenhado no fim (sobe / desce / estável).
const PATHS = {
  alta:  "M5,72 L65,62 L125,52 L185,38 L245,22 L300,10",
  baixa: "M5,14 L65,24 L125,34 L185,50 L245,64 L300,80",
  flat:  "M5,46 L65,44 L125,47 L185,45 L245,46 L300,45",
};
const PONTA_Y = { alta: 10, baixa: 80, flat: 45 };

function PrecoAnim({ direcao }) {
  const tipo = direcao === "alta" ? "alta" : direcao === "baixa" ? "baixa" : "flat";
  const cor = tipo === "alta" ? "#15924a" : tipo === "baixa" ? "#d33" : "#71808d";
  return (
    <svg className="preco-svg" width="305" height="92" viewBox="0 0 308 92" aria-hidden="true">
      <path className="linha" d={PATHS[tipo]} fill="none" stroke={cor} strokeWidth="3"
        strokeLinecap="round" strokeLinejoin="round" />
      <circle className="ponta" cx="300" cy={PONTA_Y[tipo]} r="6" fill={cor} />
    </svg>
  );
}

function tipoSent(rotulo) {
  return rotulo === "Positivo" ? "pos" : rotulo === "Negativo" ? "neg" : "neutro";
}
function tipoDir(d) {
  return d === "alta" ? "alta" : d === "baixa" ? "baixa" : "ind";
}

function construirEtapas(res) {
  return [
    {
      icone: "📝", titulo: "1. Frase recebida",
      desc: "O texto é normalizado e enviado ao pipeline de análise.",
      entrada: null, saida: { texto: "texto pronto", tipo: "neutro" },
    },
    {
      icone: "🧠", titulo: "2. Análise de sentimento — FinBERT-PT-BR",
      desc: "Um modelo de linguagem especializado em finanças lê a frase e classifica o tom.",
      entrada: "frase", saida: { texto: `${res.sentimento.rotulo} (${res.sentimento.indice})`, tipo: tipoSent(res.sentimento.rotulo) },
    },
    {
      icone: "🏷️", titulo: "3. Relevância e categoria",
      desc: "Verifica se a notícia se relaciona à PETR4/petróleo (152 termos) e identifica a categoria temática.",
      entrada: "frase", saida: { texto: res.relevante ? res.categoria.rotulo : "não relevante", tipo: res.relevante ? "pos" : "neutro" },
    },
    {
      icone: "⚖️", titulo: "4. Leitura econômica setorial",
      desc: "Aplica a teoria (Kilian, 2009; Hamilton, 1983): o efeito sobre a Petrobras pode diferir do efeito sobre o mercado.",
      entrada: "categoria + sentimento", saida: { texto: TXT[res.leitura_setorial.direcao] || "—", tipo: tipoDir(res.leitura_setorial.direcao) },
    },
    {
      icone: "🌳", titulo: "5. Modelo estatístico — XGBoost (Data Fusion)",
      desc: "Combina retorno do dia, volatilidade (GARCH) e sentimento para estimar a probabilidade de alta.",
      entrada: "retorno · volatilidade · sentimento",
      saida: { texto: `P(alta) = ${(res.leitura_modelo.prob_alta * 100).toFixed(0)}%`, tipo: tipoDir(res.leitura_modelo.direcao) },
    },
    {
      icone: "🎯", titulo: "6. Veredito final",
      desc: "Síntese dos sinais → direção provável do preço da PETR4 no próximo pregão.",
      final: true,
    },
  ];
}

export default function Jornada({ res }) {
  const etapas = construirEtapas(res);
  const [ativa, setAtiva] = useState(0);

  useEffect(() => {
    setAtiva(0);
    const timers = etapas.map((_, i) => setTimeout(() => setAtiva(i + 1), (i + 1) * 1400));
    return () => timers.forEach(clearTimeout);
    // eslint-disable-next-line
  }, [res]);

  const concluida = ativa > etapas.length - 1;

  return (
    <div className="painel">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 10 }}>
        <h2 style={{ margin: 0 }}>🚀 Jornada da previsão</h2>
        {concluida && <button className="btn sec" onClick={() => { setAtiva(0); setTimeout(() => {
          let i = 0; const t = setInterval(() => { i++; setAtiva(i); if (i > etapas.length - 1) clearInterval(t); }, 1400);
        }, 60); }}>↻ Repetir animação</button>}
      </div>

      <div className="frase-pill">“{res.frase}”</div>

      <div className="jornada">
        {etapas.map((e, i) => {
          const estado = i < ativa ? "feita" : i === ativa ? "ativa" : "pendente";
          return (
            <div className={`etapa ${estado}`} key={i}>
              <div className="no">{i < ativa ? "✓" : e.icone}</div>
              <div className="corpo">
                <h4>{e.titulo}</h4>
                <p className="desc">{e.desc}</p>

                {e.final ? (
                  i < ativa ? (
                    <div className="preco-final saida-anim">
                      <div>
                        <div className={`grande ${res.direcao}`}>{SETA[res.direcao]} {TXT[res.direcao]}</div>
                        <div className="desc" style={{ maxWidth: "60ch" }}>{res.explicacao}</div>
                      </div>
                      <PrecoAnim direcao={res.direcao} />
                    </div>
                  ) : i === ativa ? (
                    <span className="processando"><span className="spinner" /> sintetizando…</span>
                  ) : <span className="chip" style={{ opacity: .5 }}>aguardando</span>
                ) : (
                  <div className="fluxo">
                    {e.entrada && <><span className="chip">{e.entrada}</span><span className="seta-fluxo">→</span></>}
                    {i < ativa
                      ? <span className={`saida saida-anim ${e.saida.tipo}`}>{e.saida.texto}</span>
                      : i === ativa
                        ? <span className="processando"><span className="spinner" /> processando…</span>
                        : <span className="chip" style={{ opacity: .5 }}>aguardando</span>}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
