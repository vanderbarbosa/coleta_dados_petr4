import React, { useState } from "react";
import { api } from "../api.js";
import Jornada from "./Jornada.jsx";

const EXEMPLOS = [
  "Guerra leva ao fechamento do Estreito de Ormuz, impossibilitando a navegação dos navios petroleiros.",
  "Petrobras anuncia dividendos recordes e lucro acima do esperado no trimestre.",
  "Governo anuncia intervenção e demite o presidente da Petrobras.",
];

const SETA = { alta: "▲", baixa: "▼", indefinida: "●", sem_influencia: "○", neutra: "●", contextual: "◆" };
const TXT = {
  alta: "Tende à ALTA", baixa: "Tende à BAIXA", indefinida: "Direção indefinida",
  sem_influencia: "Sem influência relevante", neutra: "Sem direção clara", contextual: "Efeito contextual",
};
const classe = (d) => (d === "alta" || d === "baixa") ? d : (d === "sem_influencia" ? "sem_influencia" : "indefinida");

export default function Previsao() {
  const [texto, setTexto] = useState("");
  const [res, setRes] = useState(null);
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState(null);

  function avaliar(t) {
    const txt = (t ?? texto).trim();
    if (txt.length < 10) { setErro("Digite uma notícia com pelo menos 10 caracteres."); return; }
    if (t) setTexto(t);
    setErro(null); setCarregando(true); setRes(null);
    api.prever(txt)
      .then((r) => (r.erro ? setErro(r.erro) : setRes({ ...r, frase: txt })))
      .catch((e) => setErro("Não foi possível avaliar. A API de previsão está no ar? " + e.message))
      .finally(() => setCarregando(false));
  }

  return (
    <div>
      <h1>Avaliar uma notícia</h1>
      <p className="sub">
        Informe o texto de uma manchete. O sistema identifica o <strong>sentimento</strong> (FinBERT-PT-BR),
        a <strong>categoria temática</strong> e a <strong>direção provável</strong> da PETR4, combinando uma
        leitura econômica setorial (fundamentada na literatura) com o modelo estatístico treinado.
      </p>

      <div className="painel">
        <div className="campo" style={{ width: "100%" }}>
          <label htmlFor="texto">Texto da notícia</label>
          <textarea id="texto" rows={4} value={texto} onChange={(e) => setTexto(e.target.value)}
            placeholder="Ex.: Ataque a refinaria reduz a oferta global e eleva o preço do barril de petróleo…"
            style={{ resize: "vertical" }} />
        </div>
        <div style={{ display: "flex", gap: 10, marginTop: 12, flexWrap: "wrap" }}>
          <button className="btn" onClick={() => avaliar()} disabled={carregando}>
            {carregando ? "Avaliando…" : "Avaliar notícia"}
          </button>
          {EXEMPLOS.map((ex, i) => (
            <button key={i} className="btn sec" onClick={() => avaliar(ex)} disabled={carregando}>Exemplo {i + 1}</button>
          ))}
        </div>
        {erro && <div className="aviso" style={{ marginTop: 14 }}>{erro}</div>}
        {carregando && <div className="carregando"><span className="spinner" /> Processando o modelo de linguagem… (a 1ª vez pode levar alguns segundos)</div>}
        <p className="sub" style={{ margin: "10px 0 0", fontSize: ".8rem" }}>
          Dica: experimente os exemplos. A primeira avaliação carrega o modelo na memória.
        </p>
      </div>

      {res && (
        <>
          {res.origem === "navegador" && (
            <div className="aviso" style={{ marginTop: 14 }}>
              ℹ️ Previsão calculada <strong>no seu navegador</strong> (regras da taxonomia + léxico).
              O índice FinBERT-PT-BR e a probabilidade do XGBoost só aparecem quando o backend de
              previsão está no ar. {res.motor}
            </div>
          )}

          <Jornada res={res} />

          <h2>Detalhes da análise</h2>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 18 }}>
            <span className={`tag ${res.sentimento.rotulo === "Positivo" ? "verde" : res.sentimento.rotulo === "Negativo" ? "verm" : "cinza"}`}>
              Sentimento: {res.sentimento.rotulo} ({res.sentimento.indice})
            </span>
            <span className="tag">{res.categoria.id ? res.categoria.rotulo : "Sem categoria"}</span>
            <span className={`tag ${res.relevante ? "verde" : "cinza"}`}>
              Relevância: {res.nivel_relevancia}
            </span>
            {res.leitura_setorial.evento && res.leitura_setorial.evento !== "neutro" && (
              <span className="tag">
                Evento: {res.leitura_setorial.evento === "resolucao" ? "↑ Resolução" : "↓ Disrupção"}
              </span>
            )}
          </div>

          <div className="grade-2">
            <div className="painel" style={{ margin: 0 }}>
              <h2 style={{ marginTop: 0 }}>📚 Leitura econômica setorial</h2>
              <p style={{ marginTop: 0 }}><strong>{TXT[res.leitura_setorial.direcao] || "—"}</strong></p>
              <p style={{ color: "var(--tinta-2)", fontSize: ".92rem" }}>{res.leitura_setorial.justificativa}</p>
            </div>
            <div className="painel" style={{ margin: 0 }}>
              <h2 style={{ marginTop: 0 }}>📈 Modelo estatístico (dados)</h2>
              {res.leitura_modelo.prob_alta != null ? (
                <p style={{ marginTop: 0 }}>
                  <strong>{TXT[res.leitura_modelo.direcao] || "—"}</strong> · P(alta) = {(res.leitura_modelo.prob_alta * 100).toFixed(1)}%
                </p>
              ) : (
                <p style={{ marginTop: 0 }}><strong>Indisponível offline</strong></p>
              )}
              <p style={{ color: "var(--tinta-2)", fontSize: ".92rem" }}>{res.leitura_modelo.nota}</p>
            </div>
          </div>

          <div className="painel">
            {res.contexto && (
              <table>
                <tbody>
                  <tr><th>Modelo</th><td>{res.contexto.modelo}</td></tr>
                  <tr><th>Acurácia / AUC (teste)</th><td>{res.contexto.acuracia_teste}% · {res.contexto.auc_teste}</td></tr>
                  <tr><th>Contexto (ref. {res.contexto.data_referencia})</th>
                    <td>retorno recente {res.contexto.retorno_recente_pct}% · volatilidade {res.contexto.volatilidade_recente}</td></tr>
                </tbody>
              </table>
            )}
            <div className="aviso" style={{ marginTop: 14 }}>{res.aviso}</div>
          </div>
        </>
      )}
    </div>
  );
}
