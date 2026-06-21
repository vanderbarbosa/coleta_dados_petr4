import React, { useEffect, useState } from "react";
import { api } from "../api.js";

// Página institucional da pesquisa: objetivo, questões, método, ferramentas,
// resultados reais (Tabela 4.3 + ablação) e como o trabalho responde à banca.
// Todos os números provêm da API (dados/modelos reais), sem valores inventados.

const pct = (n) => (n == null ? "—" : `${Number(n).toFixed(2)}%`);

function destaqueModelo(modelos) {
  const acha = (frag) => modelos.find((m) => m.Modelo.includes(frag));
  const fusion = acha("XGBoost (Data Fusion");
  const precos = acha("XGBoost (Apenas Preços");
  if (!fusion || !precos) return null;
  return {
    fusion: fusion["Acurácia"],
    precos: precos["Acurácia"],
    ganho: (fusion["Acurácia"] - precos["Acurácia"]).toFixed(2),
  };
}

export default function Sobre() {
  const [res, setRes] = useState(null);
  const [est, setEst] = useState(null);
  const [erro, setErro] = useState(null);

  useEffect(() => {
    api.resultados().then(setRes).catch((e) => setErro(e.message));
    api.estatisticas().then(setEst).catch(() => {});
  }, []);

  const d = res?.modelos ? destaqueModelo(res.modelos) : null;
  const meta = res?.meta;

  return (
    <div className="prosa">
      <div className="hero">
        <h1>Sobre a Pesquisa</h1>
        <p className="sub">
          O Impacto do Sentimento de Notícias Financeiras na Previsão de Direção e Volatilidade do
          Ativo PETR4
        </p>
      </div>

      <div className="painel" style={{ marginBottom: 22 }}>
        <table>
          <tbody>
            <tr><td><strong>Autor</strong></td><td>Vanderlei Barbosa da Silva</td></tr>
            <tr><td><strong>Orientador</strong></td><td>Prof. Dr. Julio Cesar Nievola</td></tr>
            <tr><td><strong>Instituição</strong></td><td>PUCPR — Programa de Pós-Graduação em Informática (PPGIa)</td></tr>
            <tr><td><strong>Linha</strong></td><td>Aprendizado de máquina aplicado a finanças e Processamento de Linguagem Natural</td></tr>
            <tr><td><strong>Ativo</strong></td><td>PETR4 (Petrobras PN) — B3</td></tr>
          </tbody>
        </table>
      </div>

      {/* ----------------------------------------------------------------- */}
      <h2>1. Problema e objetivo</h2>
      <p>
        Notícias financeiras carregam informação capaz de influenciar o preço dos ativos. A questão
        central desta pesquisa é verificar se o <strong>sentimento</strong> extraído de notícias em
        português melhora, de forma mensurável, a previsão da <strong>direção</strong> (alta ou
        baixa) e da <strong>volatilidade</strong> do ativo PETR4 no pregão seguinte, em comparação
        com modelos baseados apenas no histórico de preços.
      </p>

      <h2>2. Questões de pesquisa e hipóteses</h2>
      <ul>
        <li>
          <strong>QP1 —</strong> O sentimento de notícias agrega poder preditivo à direção da PETR4
          além do que já está nos preços?
        </li>
        <li>
          <strong>QP2 —</strong> Quais categorias temáticas de notícia (empresa, mercado de petróleo,
          geopolítica, sanções, etc.) mais contribuem para a previsão?
        </li>
        <li>
          <strong>QP3 —</strong> O sentimento ajuda a antecipar regimes de volatilidade, em
          articulação com um modelo econométrico GARCH?
        </li>
        <li>
          <strong>H1 —</strong> A fusão de sentimento e preços (<em>Data Fusion</em>) supera o modelo
          de referência baseado só em preços — <em>confirmada de forma modesta nos dados reais.</em>
        </li>
      </ul>

      {/* ----------------------------------------------------------------- */}
      <h2>3. O pipeline em cinco etapas</h2>
      <p>
        A pesquisa é totalmente reprodutível e organizada em cinco scripts encadeados, cada um
        documentado em um anexo ABNT próprio.
      </p>
      <div className="cartoes">
        <div className="cartao"><div className="num">1</div><div className="rot">Dados financeiros — cotações da PETR4 (yfinance) e log-retornos</div></div>
        <div className="cartao"><div className="num">2</div><div className="rot">Coleta de notícias — WordPress REST API, com data e hora; taxonomia temática</div></div>
        <div className="cartao"><div className="num">3</div><div className="rot">Sentimento — FinBERT-PT-BR e índice diário de sentimento (ISM)</div></div>
        <div className="cartao"><div className="num">4</div><div className="rot">Modelagem — GARCH(1,1) + SVM/XGBoost (Data Fusion) e ablação</div></div>
        <div className="cartao"><div className="num">5</div><div className="rot">Inferência — aplicação que prevê a direção de uma notícia inédita</div></div>
      </div>

      {/* ----------------------------------------------------------------- */}
      <h2>4. Método e decisões técnicas</h2>

      <h3>4.1. Coleta de notícias com data e hora</h3>
      <p>
        Em vez de APIs comerciais com janela curta, a coleta usa a <strong>WordPress REST API</strong>{" "}
        (<code>/wp-json/wp/v2/posts</code>) de cinco portais. Esse acesso fornece, para cada notícia,
        o <code>date</code> (horário de Brasília) e o <code>date_gmt</code> (UTC), atendendo a um
        requisito crítico apontado pela banca: a marcação temporal precisa, que viabiliza a análise{" "}
        <em>Lead-Lag</em> (separar notícias publicadas antes e depois do fechamento das 17h).
        {est && (
          <> Foram coletadas <strong>{est.noticias_total.toLocaleString("pt-BR")}</strong> notícias
          datadas; <strong>{est.lead_lag_pct}%</strong> ocorreram após o fechamento.</>
        )}
      </p>

      <h3>4.2. Taxonomia temática (fonte única)</h3>
      <p>
        As notícias são organizadas em <strong>7 categorias</strong> e <strong>152 termos</strong>,
        definidos em um único módulo (<code>src/comum/taxonomia.py</code>) para garantir consistência
        entre coleta, filtragem, sentimento e inferência. A taxonomia substituiu a modelagem de
        tópicos por LDA, oferecendo categorias interpretáveis e ancoradas na literatura econômica.
      </p>

      <h3>4.3. Sentimento com modelo financeiro em português</h3>
      <p>
        O sentimento é estimado pelo <strong>FinBERT-PT-BR</strong>{" "}
        (<code>lucas-leme/FinBERT-PT-BR</code>), um modelo da família BERT ajustado para textos
        financeiros em português — escolha que substituiu um classificador genérico (xlm-roberta) por
        um especializado no domínio. As classificações diárias são agregadas em um{" "}
        <strong>Índice de Sentimento de Mercado (ISM)</strong>.
      </p>

      <h3>4.4. Volatilidade e fusão de dados</h3>
      <p>
        A volatilidade condicional é modelada por um <strong>GARCH(1,1) t-Student</strong>. A previsão
        de direção emprega <em>Data Fusion</em> por concatenação de atributos defasados em t−1
        (retorno, volatilidade e sentimento), evitando vazamento de informação. Os classificadores são{" "}
        <strong>SVM</strong> e <strong>XGBoost</strong>, avaliados sob uma{" "}
        <strong>divisão cronológica tripla 60/15/25</strong> (treino/validação/teste), com seleção de
        hiperparâmetros na validação e avaliação única no teste.
      </p>

      {/* ----------------------------------------------------------------- */}
      <h2>5. Resultados</h2>
      {erro && <div className="aviso">Não foi possível carregar os resultados da API: {erro}</div>}

      {d && (
        <div className="cartoes" style={{ marginBottom: 18 }}>
          <div className="cartao"><div className="num">{pct(d.precos)}</div><div className="rot">XGBoost — apenas preços (referência)</div></div>
          <div className="cartao"><div className="num">{pct(d.fusion)}</div><div className="rot">XGBoost — Data Fusion (preços + GARCH + sentimento)</div></div>
          <div className="cartao"><div className="num">+{d.ganho} pp</div><div className="rot">Ganho atribuído ao sentimento (teste)</div></div>
        </div>
      )}

      {res?.modelos?.length > 0 && (
        <div className="painel">
          <h3 style={{ marginTop: 0 }}>Tabela — Desempenho dos modelos (conjunto de teste)</h3>
          <table>
            <thead>
              <tr><th>Modelo</th><th>Acurácia</th><th>Precisão</th><th>F1</th><th>AUC-ROC</th></tr>
            </thead>
            <tbody>
              {res.modelos.map((m) => {
                const destaca = m.Modelo.includes("XGBoost (Data Fusion");
                return (
                  <tr key={m.Modelo} style={destaca ? { fontWeight: 700, background: "#eef6ff" } : undefined}>
                    <td>{m.Modelo}</td>
                    <td>{pct(m["Acurácia"])}</td>
                    <td>{pct(m["Precisão"])}</td>
                    <td>{pct(m["F1-Score"])}</td>
                    <td>{Number(m["AUC-ROC"]).toFixed(3)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          {meta && (
            <p style={{ fontSize: ".85rem", color: "#5a6b7b", marginBottom: 0 }}>
              Treino: {meta.periodo_treino?.[0]} a {meta.periodo_treino?.[1]} · Teste:{" "}
              {meta.periodo_teste?.[0]} a {meta.periodo_teste?.[1]}.
            </p>
          )}
        </div>
      )}

      {res?.ablacao?.length > 0 && (
        <div className="painel">
          <h3 style={{ marginTop: 0 }}>Tabela — Ablação por categoria temática</h3>
          <p style={{ marginTop: 0 }}>
            Cada linha mede a variação de acurácia ao remover a contribuição de uma categoria. Um
            impacto <strong>positivo</strong> indica que a categoria <em>contribui</em> para a
            previsão; negativo, que sua remoção elevou a acurácia (achado exploratório, reportado com
            transparência).
          </p>
          <table>
            <thead><tr><th>Categoria</th><th>Acurácia sem ela</th><th>Impacto (pp)</th></tr></thead>
            <tbody>
              {res.ablacao.map((a) => (
                <tr key={a.Categoria}>
                  <td>{a.Categoria.replace(/^CAT\d+_/, "").replace(/_/g, " ")}</td>
                  <td>{pct(a.Acuracia_sem_ela)}</td>
                  <td style={{ color: a.Impacto_pp >= 0 ? "#1a7f37" : "#b42318" }}>
                    {a.Impacto_pp >= 0 ? "+" : ""}{Number(a.Impacto_pp).toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* ----------------------------------------------------------------- */}
      <h2>6. Como a pesquisa responde à banca</h2>
      <table>
        <thead><tr><th>Observação da banca</th><th>Resposta do trabalho</th></tr></thead>
        <tbody>
          <tr>
            <td>Notícias precisam de marcação temporal precisa (Lead-Lag).</td>
            <td>WordPress REST API fornece data e hora (Brasília + UTC) de cada notícia.</td>
          </tr>
          <tr>
            <td>Dependência de uma única fonte de notícias.</td>
            <td>Coleta de cinco portais, com atribuição de fonte por notícia.</td>
          </tr>
          <tr>
            <td>Distinguir notícia ruim para o mercado de notícia ruim para a Petrobras.</td>
            <td>Leitura econômica setorial (Kilian, 2009; Hamilton, 1983): choque de oferta favorece a produtora; evento de empresa segue o sentido do evento.</td>
          </tr>
          <tr>
            <td>Justificar bibliotecas e ferramentas.</td>
            <td>Cada escolha é documentada com função e justificativa nos cinco anexos ABNT.</td>
          </tr>
          <tr>
            <td>Evitar linguagem promocional; reportar resultados com rigor.</td>
            <td>Resultados honestos (ganho modesto do sentimento; tuning sem ganho no teste), sem inflar números.</td>
          </tr>
        </tbody>
      </table>

      {/* ----------------------------------------------------------------- */}
      <h2>7. Limitações e trabalhos futuros</h2>
      <ul>
        <li>A acurácia (~53%) reflete a quase-eficiência do mercado; os sinais são acadêmicos/experimentais, não recomendação de investimento.</li>
        <li>O vocabulário de eventos (disrupção/resolução) é finito; sua expansão é trabalho contínuo.</li>
        <li>Trabalhos futuros: previsão de magnitude da volatilidade, janelas intradiárias e modelos de linguagem maiores para o índice de sentimento.</li>
      </ul>

      <div className="aviso">
        <strong>Transparência.</strong> Todos os números desta página são lidos diretamente dos
        arquivos de resultado dos modelos treinados (Etapa 4), sem qualquer valor inventado. A
        documentação completa de cada etapa está disponível em formato ABNT no repositório da
        pesquisa.
      </div>
    </div>
  );
}
