import React, { useEffect, useRef, useState } from "react";
import { som } from "../som.js";

const TXT = {
  alta: "Tende à ALTA", baixa: "Tende à BAIXA", indefinida: "Direção indefinida",
  sem_influencia: "Sem influência", neutra: "Sem direção clara", contextual: "Efeito contextual",
};
const SETA = { alta: "▲", baixa: "▼", indefinida: "●", sem_influencia: "○", neutra: "●", contextual: "◆" };
const PATHS = {
  alta: "M5,72 L65,62 L125,52 L185,38 L245,22 L300,10",
  baixa: "M5,14 L65,24 L125,34 L185,50 L245,64 L300,80",
  flat: "M5,46 L65,44 L125,47 L185,45 L245,46 L300,45",
};
const PONTA_Y = { alta: 10, baixa: 80, flat: 45 };
const classeFinal = (d) => (d === "alta" || d === "baixa") ? d : (d === "sem_influencia" ? "sem_influencia" : "indefinida");
const tipoSent = (r) => (r === "Positivo" ? "pos" : r === "Negativo" ? "neg" : "neutro");
const tipoDir = (d) => (d === "alta" ? "alta" : d === "baixa" ? "baixa" : "ind");

function Cog({ cor }) {
  const dentes = Array.from({ length: 12 }, (_, i) => i * 30);
  return (
    <svg className="cog" viewBox="0 0 100 100" aria-hidden="true">
      {dentes.map((a) => (
        <rect key={a} x="45" y="3" width="10" height="16" rx="2.5" fill={cor} transform={`rotate(${a} 50 50)`} />
      ))}
      <circle cx="50" cy="50" r="35" fill={cor} />
      <circle cx="50" cy="50" r="23" fill="#ffffff" />
    </svg>
  );
}

function Engrenagem({ estado, icone, anti }) {
  const cor = estado === "feita" ? "#15924a" : estado === "ativa" ? "#0b6fb8" : "#c3ccd6";
  return (
    <div className={`engr ${estado} ${estado === "ativa" ? "girando" : ""} ${anti ? "anti" : ""}`}>
      <Cog cor={cor} />
      <span className="icone">{estado === "feita" ? "✓" : icone}</span>
    </div>
  );
}

function PrecoAnim({ direcao }) {
  const tipo = direcao === "alta" ? "alta" : direcao === "baixa" ? "baixa" : "flat";
  const cor = tipo === "alta" ? "#15924a" : tipo === "baixa" ? "#d33" : "#71808d";
  return (
    <svg className="preco-svg" width="305" height="92" viewBox="0 0 308 92" aria-hidden="true">
      <path className="linha" d={PATHS[tipo]} fill="none" stroke={cor} strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
      <circle className="ponta" cx="300" cy={PONTA_Y[tipo]} r="6" fill={cor} />
    </svg>
  );
}

function construirEtapas(res) {
  return [
    { icone: "📝", titulo: "Frase recebida", entrada: null, saida: { texto: "texto pronto", tipo: "neutro" } },
    { icone: "🧠", titulo: "Sentimento (FinBERT-PT-BR)", entrada: "frase", saida: { texto: `${res.sentimento.rotulo} (${res.sentimento.indice})`, tipo: tipoSent(res.sentimento.rotulo) } },
    { icone: "🏷️", titulo: "Relevância e categoria", entrada: "frase", saida: { texto: res.relevante ? res.categoria.rotulo.replace(/^CAT\d+\s*[—-]\s*/, "") : "não relevante", tipo: res.relevante ? "pos" : "neutro" } },
    { icone: "⚖️", titulo: "Leitura econômica setorial", entrada: "categoria + sentim.", saida: { texto: TXT[res.leitura_setorial.direcao] || "—", tipo: tipoDir(res.leitura_setorial.direcao) } },
    { icone: "🌳", titulo: "Modelo XGBoost (Data Fusion)", entrada: "retorno·volat·sentim.", saida: { texto: `P(alta) = ${(res.leitura_modelo.prob_alta * 100).toFixed(0)}%`, tipo: tipoDir(res.leitura_modelo.direcao) } },
    { icone: "🎯", titulo: "Veredito final", entrada: "síntese", saida: { texto: TXT[res.direcao] || "—", tipo: tipoDir(res.direcao) } },
  ];
}

export default function Jornada({ res }) {
  const etapas = construirEtapas(res);
  const N = etapas.length;
  const [ativa, setAtiva] = useState(0);
  const [mudo, setMudo] = useState(som.isMudo());
  const ativaRef = useRef(null);
  const timersRef = useRef([]);

  function tocarPasso(k) {
    if (k > 0) som.ding(k - 1);          // etapa k-1 concluída
    if (k < N) som.engrenar();           // etapa k iniciando
    if (k === N) som.veredito(res.direcao); // todas concluídas
  }

  function rodar() {
    timersRef.current.forEach(clearTimeout);
    setAtiva(0); tocarPasso(0);
    timersRef.current = Array.from({ length: N }, (_, i) =>
      setTimeout(() => { setAtiva(i + 1); tocarPasso(i + 1); }, (i + 1) * 1500));
  }

  useEffect(() => { rodar(); return () => timersRef.current.forEach(clearTimeout); /* eslint-disable-next-line */ }, [res]);
  useEffect(() => {
    if (ativaRef.current) ativaRef.current.scrollIntoView({ behavior: "smooth", inline: "center", block: "nearest" });
  }, [ativa]);

  function alternarSom() { const novo = !mudo; setMudo(novo); som.setMudo(novo); }
  const concluida = ativa >= N;

  return (
    <div className="painel">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 10 }}>
        <h2 style={{ margin: 0 }}>⚙️ Jornada da previsão</h2>
        <div style={{ display: "flex", gap: 8 }}>
          <button className="btn sec" onClick={alternarSom}>{mudo ? "🔇 Som off" : "🔊 Som on"}</button>
          {concluida && <button className="btn sec" onClick={rodar}>↻ Repetir</button>}
        </div>
      </div>

      <div className="frase-pill">“{res.frase}”</div>

      <div className="esteira">
        <div className="trilho">
          {etapas.map((e, i) => {
            const estado = i < ativa ? "feita" : i === ativa ? "ativa" : "pendente";
            return (
              <React.Fragment key={i}>
                <div className={`estacao ${estado}`} ref={i === ativa ? ativaRef : null}>
                  <div className="topo-engr"><Engrenagem estado={estado} icone={e.icone} anti={i % 2 === 1} /></div>
                  <div className="estacao-card">
                    <h4>{i + 1}. {e.titulo}</h4>
                    <div className="io-v">
                      {e.entrada && <><span className="chip">{e.entrada}</span><span className="seta-v">▼</span></>}
                      {estado === "feita"
                        ? <span className={`saida saida-anim ${e.saida.tipo}`}>{e.saida.texto}</span>
                        : estado === "ativa"
                          ? <span className="processando"><span className="spinner" /> processando…</span>
                          : <span className="chip" style={{ opacity: .5 }}>aguardando</span>}
                    </div>
                  </div>
                </div>
                {i < N - 1 && (
                  <div className={`conector-h ${i + 1 < ativa ? "feito" : ""} ${i + 1 === ativa ? "ativo" : ""}`} />
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>

      {concluida && (
        <div className={`veredito-final ${classeFinal(res.direcao)}`} style={{ marginTop: 18 }}>
          <div>
            <div className="grande">{SETA[res.direcao]} {TXT[res.direcao]}</div>
            <div className="desc" style={{ maxWidth: "58ch", marginTop: 4 }}>{res.explicacao}</div>
          </div>
          <PrecoAnim direcao={res.direcao} />
        </div>
      )}
    </div>
  );
}
