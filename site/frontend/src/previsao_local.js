// ==============================================================================
//  previsao_local.js — Previsão de direção da PETR4 executada NO NAVEGADOR.
//  Dissertação PETR4 | Vanderlei Barbosa da Silva
//
//  Porta para JavaScript a LEITURA ECONÔMICA SETORIAL do backend (app.py):
//  taxonomia de 7 categorias/152 termos + classificação evento×mecanismo
//  (resolução/disrupção × empresa/oferta), fundamentada em Kilian (2009) e
//  Hamilton (1983). Usado quando não há backend FinBERT/XGBoost ao vivo, para
//  que a previsão de direção continue funcionando no GitHub Pages.
//
//  Diferença em relação ao backend: aqui o SENTIMENTO vem de um léxico simples
//  (não do FinBERT-PT-BR) e NÃO há a probabilidade estatística do XGBoost.
//  A leitura econômica (a parte mais interpretável) é idêntica.
// ==============================================================================

// ── Taxonomia (espelho de src/comum/taxonomia.py — fonte única de verdade) ────
export const TERMOS_POR_CATEGORIA = {
  CAT1_Empresa: [
    "Petrobras", "PETR4", "PETR3", "Petróleo Brasileiro SA", "petróleo brasileiro S.A.",
    "pré-sal", "pre-sal", "Petrobras dividendos", "Petrobras resultado", "Petrobras lucro",
    "Petrobras prejuízo", "Petrobras produção", "Petrobras exploração", "Petrobras refino",
    "Petrobras dívida", "Petrobras privatização", "Petrobras contrato", "campo de Búzios",
    "campo de Tupi", "bacia de Santos", "bacia de Campos",
  ],
  CAT2_Mercado_Petroleo: [
    "preço do petróleo", "cotação do petróleo", "barril de petróleo", "petróleo Brent",
    "petróleo WTI", "OPEP", "OPEC", "OPEP+", "corte de produção petróleo",
    "aumento de produção petróleo", "demanda por petróleo", "oferta de petróleo",
    "estoques de petróleo EUA", "EIA estoques petróleo", "petróleo mercado",
    "commodity petróleo", "crise do petróleo", "choque do petróleo", "petróleo bruto",
    "mercado de energia",
  ],
  CAT3_Geopolitica: [
    "guerra Oriente Médio", "conflito Oriente Médio", "guerra Israel", "guerra Hamas",
    "guerra Irã", "tensão Irã", "sanção Irã", "guerra Iraque", "conflito Iraque",
    "guerra Líbia", "conflito Líbia", "guerra Yemen", "conflito Houthi", "ataque Houthi",
    "guerra Rússia Ucrânia", "invasão Ucrânia", "conflito Rússia", "sanção Rússia petróleo",
    "guerra Síria petróleo", "conflito Venezuela petróleo", "tensão Golfo Pérsico",
    "Estreito de Ormuz", "cessar-fogo Oriente Médio", "acordo de paz Oriente Médio",
    "acordo paz Rússia Ucrânia", "Arábia Saudita petróleo", "crise geopolítica petróleo",
  ],
  CAT4_Infraestrutura: [
    "refinaria petróleo", "oleoduto", "gasoduto", "plataforma petróleo", "plataforma offshore",
    "terminal de petróleo", "duto petróleo", "interrupção refinaria", "acidente refinaria",
    "ataque refinaria", "greve petroleiros", "paralisação petróleo", "shale oil", "fracking",
    "petróleo de xisto", "capacidade de refino", "produção petróleo OPEP",
    "produção petróleo Estados Unidos", "produção petróleo Rússia", "produção petróleo Brasil",
  ],
  CAT5_Sancoes_Navegacao: [
    "embargo petróleo", "sanção petróleo", "bloqueio petróleo", "bloqueio naval",
    "proibição navio petróleo", "navio petroleiro", "teto de preço petróleo",
    "price cap petróleo", "apreensão navio petróleo", "ataque navio petroleiro",
    "Mar Vermelho petróleo", "Canal de Suez petróleo", "Bab-el-Mandeb", "acordo nuclear Irã",
    "acordo petróleo", "acordo OPEP", "tratado energia", "acordo clima petróleo",
    "transição energética petróleo", "COP petróleo",
  ],
  CAT6_Governanca: [
    "CEO Petrobras", "presidente Petrobras", "demissão Petrobras", "troca presidente Petrobras",
    "indicação Petrobras", "conselho Petrobras", "interventor Petrobras",
    "ministro de minas e energia", "ministério de minas e energia Brasil",
    "política energética Brasil", "eleição Venezuela petróleo", "eleição Arábia Saudita petróleo",
    "eleição Irã petróleo", "secretário energia EUA", "príncipe Mohammed bin Salman",
    "MBS Aramco", "Aramco", "Saudi Aramco", "CEO Aramco", "PDVSA", "Nicolás Maduro petróleo",
    "Lula Petrobras", "governo Petrobras", "intervenção estatal Petrobras",
  ],
  CAT7_Macro_Energia: [
    "dólar petróleo", "câmbio petróleo", "real dólar", "Federal Reserve petróleo",
    "juros EUA petróleo", "recessão demanda petróleo", "crescimento China petróleo",
    "demanda China petróleo", "PIB China petróleo", "inflação petróleo",
    "energia renovável petróleo", "veículo elétrico petróleo", "hidrogênio verde petróleo",
    "descarbonização petróleo", "ESG Petrobras", "combustível fóssil", "energia limpa",
    "transição energética", "gás natural preço", "GNL",
  ],
};

export const ROTULOS_CATEGORIA = {
  CAT1_Empresa: "CAT1 — Empresa e Ativo",
  CAT2_Mercado_Petroleo: "CAT2 — Mercado de Petróleo",
  CAT3_Geopolitica: "CAT3 — Geopolítica e Conflitos",
  CAT4_Infraestrutura: "CAT4 — Oferta, Infraestrutura e Produção",
  CAT5_Sancoes_Navegacao: "CAT5 — Acordos, Sanções e Navegação",
  CAT6_Governanca: "CAT6 — Liderança, Governança e Política Energética",
  CAT7_Macro_Energia: "CAT7 — Macroeconomia, Câmbio e Energia Alternativa",
};

// ── Léxico simples de polaridade (substitui o FinBERT no modo navegador) ──────
const POS = ["lucro", "alta", "sobe", "subiu", "ganho", "recorde", "dividendos", "acordo",
  "aprova", "cresce", "crescimento", "valoriza", "avanço", "avança", "positivo", "melhora",
  "supera", "otimismo", "recuperação", "expansão", "vantagem", "reforça"];
const NEG = ["queda", "cai", "caiu", "prejuízo", "perda", "greve", "crise", "demissão", "demite",
  "rombo", "despenca", "negativo", "piora", "ataque", "guerra", "sanção", "embargo", "bloqueio",
  "acidente", "conflito", "tensão", "recessão", "colapso", "risco", "temor", "incerteza"];

const RESOLUCAO = ["acordo", "fim da greve", "greve termina", "termina a greve", "fim da paralis",
  "retomada", "retoma", "normaliz", "volta ao normal", "cessar-fogo", "cessar fogo", "acordo de paz",
  "trégua", "tregua", "reabertura", "reabre", "fim do bloqueio", "fim do embargo", "fim das sanç",
  "alívio", "alivio", "encerr", "resolv", "supera", "aprova", "conclui", "avanç"];
const DISRUPCAO = ["greve", "paralis", "bloqueio", "ataque", "guerra", "sanç", "embargo", "interrup",
  "acidente", "fechamento", "fecha", "invasão", "invasao", "conflito", "explos", "sabotagem",
  "apreens", "demiss", "demite", "intervenç", "intervenc", "rompe", "crise", "tensão", "tensao",
  "ameaç", "queda", "prejuízo", "prejuizo", "rombo"];

const CATS_EMPRESA = new Set(["CAT1_Empresa", "CAT6_Governanca"]);
const CATS_OFERTA_MERC = new Set(["CAT2_Mercado_Petroleo", "CAT3_Geopolitica", "CAT5_Sancoes_Navegacao"]);

function detectarCategoria(low) {
  let melhor = null, melhorQtd = 0;
  for (const [cat, termos] of Object.entries(TERMOS_POR_CATEGORIA)) {
    let qtd = 0;
    for (const t of termos) if (low.includes(t.toLowerCase())) qtd++;
    if (qtd > melhorQtd) { melhor = cat; melhorQtd = qtd; }
  }
  if (melhor === null) return [null, null, 0];
  return [melhor, ROTULOS_CATEGORIA[melhor] || melhor, melhorQtd];
}

function polaridade(low) {
  let p = 0, n = 0;
  for (const w of POS) if (low.includes(w)) p++;
  for (const w of NEG) if (low.includes(w)) n++;
  if (p > n) return 1;
  if (n > p) return -1;
  return 0;
}

function tipoEvento(low) {
  if (RESOLUCAO.some((k) => low.includes(k))) return "resolucao";
  if (DISRUPCAO.some((k) => low.includes(k))) return "disrupcao";
  return "neutro";
}

function mecanismo(catId, low) {
  if (CATS_EMPRESA.has(catId)) return "empresa";
  if (CATS_OFERTA_MERC.has(catId)) return "oferta";
  if (catId === "CAT4_Infraestrutura")
    return (low.includes("petrobras") || low.includes("brasil")) ? "empresa" : "oferta";
  return "macro";
}

function analisarDirecao(low, pol, catId) {
  const ev = tipoEvento(low);
  const mec = mecanismo(catId, low);
  if (mec === "empresa") {
    if (ev === "resolucao") return ["alta", "Resolução de evento operacional ou corporativo (acordo, fim de paralisação, normalização) tende a FAVORECER a PETR4, ainda que o tom textual contenha termos negativos.", ev];
    if (ev === "disrupcao") return ["baixa", "Disrupção operacional, de governança ou corporativa (greve, intervenção, acidente, demissão) tende a PRESSIONAR a PETR4.", ev];
    if (pol > 0) return ["alta", "Notícia corporativa de tom positivo tende a favorecer a PETR4.", ev];
    if (pol < 0) return ["baixa", "Notícia corporativa de tom negativo tende a pressionar a PETR4.", ev];
    return ["neutra", "Notícia corporativa de tom neutro, sem direção clara.", ev];
  }
  if (mec === "oferta") {
    if (ev === "disrupcao") return ["alta", "Choque de OFERTA (conflito, bloqueio, sanção, ataque, interrupção) tende a ELEVAR o preço do petróleo; como a Petrobras é produtora da commodity, o efeito sobre a PETR4 costuma ser FAVORÁVEL — ainda que o tom seja negativo para o mercado em geral (Kilian, 2009; Hamilton, 1983).", ev];
    if (ev === "resolucao") return ["baixa", "Distensão ou normalização da oferta (cessar-fogo, acordo, aumento de produção) tende a REDUZIR o preço do petróleo, DESFAVORÁVEL à Petrobras.", ev];
    return ["neutra", "Evento de mercado de petróleo de tom neutro, sem direção clara.", ev];
  }
  return ["contextual", "Fator macroeconômico (câmbio, juros, demanda, transição energética) de efeito ambíguo, dependente do contexto.", ev];
}

// ── API pública: prevê a direção a partir do texto, no navegador ──────────────
export function preverLocal(texto) {
  const txt = (texto || "").trim();
  if (txt.length < 10) return { erro: "Informe um texto de notícia com pelo menos 10 caracteres." };
  const low = txt.toLowerCase();

  const pol = polaridade(low);
  const rotuloSent = pol > 0 ? "Positivo" : pol < 0 ? "Negativo" : "Neutro";

  const [catId, catRotulo, qtd] = detectarCategoria(low);
  const relevante = catId !== null;
  const nivel = relevante ? (qtd >= 2 ? "alta" : "media") : "baixa";

  let dirSet, justSet, evento;
  if (relevante) {
    [dirSet, justSet, evento] = analisarDirecao(low, pol, catId);
  } else {
    dirSet = "sem_influencia";
    justSet = "A notícia não casa com nenhum termo da taxonomia (Petrobras, mercado de petróleo, geopolítica, infraestrutura, sanções, governança ou macroeconomia).";
    evento = "neutro";
  }

  let direcao, explica;
  if (!relevante) {
    direcao = "sem_influencia"; explica = "Notícia sem relevância aparente para a PETR4.";
  } else if (dirSet === "alta" || dirSet === "baixa") {
    const seta = dirSet === "alta" ? "ALTA" : "BAIXA";
    direcao = dirSet; explica = `Tendência de ${seta}. ${justSet}`;
  } else {
    direcao = "indefinida"; explica = justSet;
  }

  return {
    origem: "navegador",
    motor: "Análise no navegador — regras da taxonomia + léxico (sem FinBERT/XGBoost ao vivo).",
    sentimento: { rotulo: rotuloSent, indice: pol === 0 ? 0 : (pol > 0 ? 0.5 : -0.5), confianca: null },
    relevante,
    nivel_relevancia: nivel,
    categoria: { id: catId, rotulo: catRotulo, termos_casados: qtd },
    direcao,
    explicacao: explica,
    leitura_setorial: { direcao: dirSet, justificativa: justSet, evento },
    leitura_modelo: { direcao: "indefinida", prob_alta: null,
      nota: "A probabilidade estatística (XGBoost Data Fusion) só está disponível quando o backend de previsão está no ar." },
    aviso: "Análise acadêmica/experimental (executada no navegador) — não é recomendação de investimento.",
  };
}
