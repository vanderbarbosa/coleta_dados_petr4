import React, { useEffect, useState } from "react";
import { api } from "../api.js";

const fmt = (n) => (n == null ? "—" : n.toLocaleString("pt-BR"));

export default function Inicio() {
  const [est, setEst] = useState(null);
  const [erro, setErro] = useState(null);

  useEffect(() => {
    api.estatisticas().then(setEst).catch((e) => setErro(e.message));
  }, []);

  return (
    <div className="prosa">
      <div className="hero">
        <h1>Sentimento de Notícias e a Previsão da PETR4</h1>
        <p className="sub">
          Plataforma interativa da pesquisa de mestrado que investiga se o sentimento extraído de
          notícias financeiras melhora a previsão da direção e da volatilidade do ativo PETR4.
        </p>
      </div>

      {erro && <div className="aviso" style={{ marginBottom: 18 }}>Não foi possível carregar os números (a API está no ar?). Detalhe: {erro}</div>}

      <div className="cartoes">
        <div className="cartao"><div className="num">{fmt(est?.noticias_total)}</div><div className="rot">Notícias coletadas (com data e hora)</div></div>
        <div className="cartao"><div className="num">{fmt(est?.pregoes_total)}</div><div className="rot">Pregões da PETR4 (2018–2025)</div></div>
        <div className="cartao"><div className="num">7</div><div className="rot">Categorias temáticas de notícia</div></div>
        <div className="cartao"><div className="num">{est ? est.lead_lag_pct + "%" : "—"}</div><div className="rot">Notícias após o fechamento (Lead-Lag)</div></div>
      </div>

      <h2>O que esta pesquisa faz</h2>
      <p>
        O estudo combina três fontes de informação em um modelo preditivo (abordagem de <em>Data
        Fusion</em>): (i) o histórico de preços da PETR4; (ii) a volatilidade condicional estimada
        por um modelo econométrico GARCH(1,1); e (iii) um índice diário de sentimento das notícias,
        obtido por um modelo de linguagem da família BERT especializado em texto financeiro em
        português (FinBERT-PT-BR). A direção do preço no dia seguinte (alta ou baixa) é então prevista
        por classificadores de aprendizado de máquina (SVM e XGBoost).
      </p>

      <h2>Como navegar</h2>
      <ul>
        <li><strong>Notícias</strong> — consulte o corpus coletado, filtrando por categoria temática, período e texto.</li>
        <li><strong>Preços (PETR4)</strong> — explore a série de cotações por data, ano ou mês.</li>
        <li><strong>Estatísticas</strong> — gráficos e tabelas descritivas do corpus e da série financeira.</li>
      </ul>

      <h2>Avaliar uma notícia (modelo treinado)</h2>
      <p>
        Na aba <strong>Avaliar notícia</strong> é possível inserir o texto de uma manchete e obter:
        o sentimento (FinBERT-PT-BR), se a notícia é relevante para a PETR4 e a direção prevista do
        próximo pregão pelo modelo XGBoost de <em>Data Fusion</em> (preços + GARCH + sentimento),
        treinado sobre o corpus completo de {fmt(est?.noticias_total)} notícias.
      </p>

      <div className="aviso">
        <strong>Transparência.</strong> Todos os números e previsões provêm dos dados e modelos reais
        da pesquisa, sem qualquer valor inventado. As previsões têm caráter acadêmico/experimental
        (acurácia da ordem de 53% no conjunto de teste) e não constituem recomendação de investimento.
      </div>
    </div>
  );
}
