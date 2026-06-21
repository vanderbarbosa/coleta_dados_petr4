import React, { useState } from "react";
import { api } from "../api.js";

const EXEMPLOS = [
  "Petrobras anuncia dividendos recordes e lucro acima do esperado no trimestre",
  "Governo anuncia intervenção e troca o comando da Petrobras; ação despenca",
  "Guerra no Oriente Médio eleva o preço do petróleo Brent acima de US$ 90",
];

const COR = { alta: "#1a9641", baixa: "#d7191c", indefinida: "#6b7884", sem_influencia: "#6b7884" };
const ROTULO = {
  alta: "▲ Tende à ALTA",
  baixa: "▼ Tende à BAIXA",
  indefinida: "● Direção indefinida",
  sem_influencia: "○ Sem influência relevante",
};

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
      .then((r) => (r.erro ? setErro(r.erro) : setRes(r)))
      .catch((e) => setErro("Não foi possível avaliar. A API de previsão está no ar (ambiente petr4)? " + e.message))
      .finally(() => setCarregando(false));
  }

  return (
    <div>
      <h1>Avaliar uma notícia</h1>
      <p className="sub">
        Informe o texto de uma notícia. O sistema avalia o <strong>sentimento</strong> (FinBERT-PT-BR),
        se a notícia é <strong>relevante</strong> para a PETR4 e a <strong>direção prevista</strong> do
        próximo pregão pelo modelo XGBoost (preços + GARCH + sentimento).
      </p>

      <div className="painel">
        <div className="campo" style={{ width: "100%" }}>
          <label htmlFor="texto">Texto da notícia</label>
          <textarea id="texto" rows={4} value={texto} onChange={(e) => setTexto(e.target.value)}
            placeholder="Ex.: Petrobras aprova novo plano de investimentos e eleva projeção de produção…"
            style={{ padding: "10px 12px", border: "1px solid var(--cinza-200)", borderRadius: 8, fontSize: ".95rem", fontFamily: "inherit", resize: "vertical" }} />
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
        <p className="sub" style={{ margin: "12px 0 0", fontSize: ".8rem" }}>
          A primeira avaliação pode levar alguns segundos (carregamento do modelo de linguagem).
        </p>
      </div>

      {res && (
        <div className="painel">
          <div style={{ display: "flex", alignItems: "center", gap: 14, flexWrap: "wrap" }}>
            <span style={{ fontSize: "1.3rem", fontWeight: 700, color: COR[res.direcao] }}>
              {ROTULO[res.direcao]}
            </span>
            <span className="tag">Sentimento: {res.sentimento.rotulo} ({res.sentimento.indice})</span>
            <span className="tag">Relevante: {res.relevante ? "sim" : "não"}</span>
            <span className="tag">P(alta) = {(res.prob_alta * 100).toFixed(1)}%</span>
          </div>
          <p style={{ marginTop: 12 }}>{res.explicacao}</p>

          <table style={{ marginTop: 8 }}>
            <tbody>
              <tr><th>Modelo</th><td>{res.contexto.modelo}</td></tr>
              <tr><th>Acurácia / AUC (teste)</th><td>{res.contexto.acuracia_teste}% / {res.contexto.auc_teste}</td></tr>
              <tr><th>Contexto (referência {res.contexto.data_referencia})</th>
                <td>retorno recente {res.contexto.retorno_recente_pct}% · volatilidade {res.contexto.volatilidade_recente}</td></tr>
            </tbody>
          </table>

          <div className="aviso" style={{ marginTop: 14 }}>{res.aviso}</div>
        </div>
      )}
    </div>
  );
}
