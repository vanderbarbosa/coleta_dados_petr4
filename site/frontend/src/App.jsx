import React, { useState } from "react";
import Inicio from "./views/Inicio.jsx";
import Noticias from "./views/Noticias.jsx";
import Precos from "./views/Precos.jsx";
import Estatisticas from "./views/Estatisticas.jsx";
import Previsao from "./views/Previsao.jsx";
import Demonstracao from "./views/Demonstracao.jsx";

const PAGINAS = [
  { id: "inicio", rotulo: "Início", comp: Inicio },
  { id: "noticias", rotulo: "Notícias", comp: Noticias },
  { id: "precos", rotulo: "Preços (PETR4)", comp: Precos },
  { id: "estatisticas", rotulo: "Estatísticas", comp: Estatisticas },
  { id: "previsao", rotulo: "Avaliar notícia", comp: Previsao },
  { id: "demonstracao", rotulo: "Demonstração", comp: Demonstracao },
];

export default function App() {
  const [pagina, setPagina] = useState("inicio");
  const Atual = (PAGINAS.find((p) => p.id === pagina) || PAGINAS[0]).comp;

  return (
    <>
      <header className="topo">
        <div className="container">
          <div className="marca">
            <span className="dot" aria-hidden="true" />
            <span>
              PETR4 · Sentimento &amp; Previsão
              <small>Dissertação de Mestrado — PUCPR/PPGIa</small>
            </span>
          </div>
          <nav className="nav" aria-label="Navegação principal">
            {PAGINAS.map((p) => (
              <button
                key={p.id}
                onClick={() => setPagina(p.id)}
                aria-current={pagina === p.id ? "page" : undefined}
              >
                {p.rotulo}
              </button>
            ))}
          </nav>
        </div>
      </header>

      <main>
        <div className="container">
          <Atual />
        </div>
      </main>

      <footer>
        <div className="container">
          O Impacto do Sentimento de Notícias Financeiras na Previsão de Direção e Volatilidade do
          Ativo PETR4 · Vanderlei Barbosa da Silva · Orientador: Prof. Dr. Julio Cesar Nievola ·
          PUCPR — Mestrado em Informática.
        </div>
      </footer>
    </>
  );
}
