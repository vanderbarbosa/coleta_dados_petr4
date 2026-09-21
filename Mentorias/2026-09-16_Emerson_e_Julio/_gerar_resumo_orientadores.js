// Uso: npm install docx && node _gerar_resumo_orientadores.js 15_Resumo_para_orientadores.docx
// Gera 15_Resumo_para_orientadores.docx  (requer: npm install docx)
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType,
  AlignmentType, BorderStyle, ShadingType, HeadingLevel, LevelFormat, Footer,
  PageNumber, TabStopType, Tab,
} = require("docx");

const SAIDA = process.argv[2];
const FONTE = "Arial";
const AZUL = "1F3864", CINZA = "595959", LINHA = "BFBFBF";
const LARG = 9638; // A4 (11906) - margens de 2 cm (2 x 1134)

// ── texto com **negrito** e ^{sobrescrito} ─────────────────────────────────────
function runs(texto, base = {}) {
  return texto.split(/(\*\*[^*]+\*\*|\^\{[^}]+\})/).filter(Boolean).map((t) => {
    if (t.startsWith("**")) return new TextRun({ text: t.slice(2, -2), bold: true, ...base });
    if (t.startsWith("^{")) return new TextRun({ text: t.slice(2, -1), superScript: true, ...base });
    return new TextRun({ text: t, ...base });
  });
}
const par = (texto, o = {}) =>
  new Paragraph({
    children: runs(texto, { size: o.size || 21, color: o.color, italics: o.italics }),
    spacing: { before: o.before ?? 0, after: o.after ?? 100, line: 276 },
    alignment: o.align, keepNext: o.keepNext,
  });
const nota = (texto) => par(texto, { size: 16, color: CINZA, italics: true, before: 60, after: 160 });
const marcador = (texto) =>
  new Paragraph({
    children: runs(texto, { size: 21 }),
    numbering: { reference: "bul", level: 0 },
    spacing: { after: 70, line: 276 },
  });
const h1 = (t) =>
  new Paragraph({
    heading: HeadingLevel.HEADING_1, keepNext: true,
    children: [new TextRun({ text: t, bold: true, size: 26, color: AZUL, font: FONTE })],
    spacing: { before: 280, after: 120 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: AZUL, space: 2 } },
  });
const h2 = (t) =>
  new Paragraph({
    heading: HeadingLevel.HEADING_2, keepNext: true,
    children: [new TextRun({ text: t, bold: true, size: 22, color: AZUL, font: FONTE })],
    spacing: { before: 200, after: 80 },
  });

// ── tabelas ───────────────────────────────────────────────────────────────────
const borda = { style: BorderStyle.SINGLE, size: 4, color: LINHA };
const bordas = { top: borda, bottom: borda, left: borda, right: borda };

// conteudo: string ou array de {t, b, small}
function celula(conteudo, largura, o = {}) {
  const itens = Array.isArray(conteudo) ? conteudo : [{ t: conteudo, b: o.b }];
  return new TableCell({
    width: { size: largura, type: WidthType.DXA },
    borders: bordas,
    shading: o.fundo ? { fill: o.fundo, type: ShadingType.CLEAR, color: "auto" } : undefined,
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
    children: itens.map((i) =>
      new Paragraph({
        alignment: o.align, keepNext: true,   // mantém a tabela inteira na mesma página
        spacing: { after: 0, line: 252 },
        children: runs(i.t, {
          size: i.small ? 16 : (o.size || 20), bold: i.b, color: i.small ? CINZA : (o.cor || undefined),
        }),
      })),
  });
}
function tabela(cabecalho, linhas, larguras, o = {}) {
  const alinha = (k) => (k === 0 ? AlignmentType.LEFT : AlignmentType.CENTER);
  const cab = new TableRow({
    tableHeader: true, cantSplit: true,
    children: cabecalho.map((c, k) => celula(c, larguras[k], { b: true, fundo: "D9E2F3", align: alinha(k), cor: AZUL })),
  });
  const corpo = linhas.map((l, r) =>
    new TableRow({
      cantSplit: true,
      children: l.map((c, k) => celula(c, larguras[k], {
        align: alinha(k), fundo: (o.destaque || []).includes(r) ? "FFF2CC" : undefined,
      })),
    }));
  return new Table({
    width: { size: LARG, type: WidthType.DXA }, columnWidths: larguras, rows: [cab, ...corpo],
  });
}
const v = (valor, pequeno) => (pequeno ? [{ t: valor, b: true }, { t: pequeno, small: true }] : [{ t: valor, b: true }]);

// ═════════════════════════════════════════════════════════════════════════════
const filhos = [];

filhos.push(new Paragraph({
  children: [new TextRun({ text: "Comunicados da CVM, notícias e mercado", bold: true, size: 40, color: AZUL, font: FONTE })],
  spacing: { after: 60 },
}));
filhos.push(par("Resumo dos resultados: o que move o preço e o que ainda não conseguimos prever", { size: 24, color: CINZA, after: 80 }));
filhos.push(par("Vanderlei Barbosa da Silva · PPGIa/PUCPR · Para os Profs. Julio Nievola e Emerson Paraiso · 21 de setembro de 2026",
  { size: 17, color: CINZA, after: 200 }));

// ── resposta direta ──────────────────────────────────────────────────────────
const caixa = (texto) => new Paragraph({
  children: runs(texto, { size: 21 }),
  numbering: { reference: "num", level: 0 },
  shading: { type: ShadingType.CLEAR, fill: "EEF3FA", color: "auto" },
  spacing: { before: 0, after: 60, line: 276 },
  border: { left: { style: BorderStyle.SINGLE, size: 24, color: AZUL, space: 6 } },
});
filhos.push(h1("Em quatro linhas"));
filhos.push(caixa("**O comunicado da CVM move o tamanho do movimento, não a direção.** O Fato Relevante eleva a volatilidade em **18,2%** e o volume em **36,4%** no pregão seguinte, contra pregões sem comunicado (56 papéis, 11.161 eventos)."));
filhos.push(caixa("**Como previsão, o texto pouco acrescenta.** Na volatilidade da PETR4, notícia e CVM somam no máximo 0,6 ponto sobre um modelo de preços que já ganha 6,9% sozinho."));
filhos.push(caixa("**A direção continua imprevisível.** Nenhuma fonte, sozinha ou combinada, supera o palpite fixo da classe majoritária."));
filhos.push(caixa("**O volume foi medido, mas não projetado.** Só a volatilidade, o dia excepcional e a direção foram projetados."));

// ── como foi medido ──────────────────────────────────────────────────────────
filhos.push(h1("Como foi medido"));
filhos.push(par("Só entram comunicados entregues **após o fechamento** (a partir das 17h, pela hora oficial de entrega recuperada da CVM). Observa-se o **pregão seguinte** e divide-se a volatilidade (medida de Parkinson, que usa máxima e mínima do dia) e o volume pela **média dos 5 pregões anteriores do mesmo papel**: 1,00 significa um dia igual ao habitual."));
filhos.push(par("O termo de comparação são pregões do mesmo papel **sem nenhum comunicado** (cerca de 105 mil), e não 1,00. Mesmo sem evento a razão média fica acima de 1, porque um dia pode ser várias vezes mais agitado que a média, mas nunca menos que zero."));

// ── 1. medição, 56 papéis ────────────────────────────────────────────────────
filhos.push(h1("1. Medição: o comunicado move volatilidade e volume"));
filhos.push(tabela(
  ["Tipo de comunicado", "Eventos", "Volatilidade", "Volume"],
  [
    [[{ t: "Fato Relevante", b: true }], "3.292", v("+18,2%", "IC 95%: +13,8 a +21,9"), v("+36,4%", "IC 95%: +30,5 a +41,7")],
    [[{ t: "Comunicado ao Mercado", b: true }], "7.869", v("+6,9%", "IC 95%: +2,4 a +9,9"), v("+12,2%", "IC 95%: +7,3 a +16,0")],
    [[{ t: "Os dois juntos", b: true }], "11.161", v("+9,6%"), v("+16,5%")],
  ],
  [3000, 1300, 2669, 2669], { destaque: [0] }));
filhos.push(nota("Fonte: 56 papéis da B3, jan/2018 a ago/2026; excesso sobre pregões sem comunicado. IC 95% por reamostragem de dias (bootstrap em blocos de dia, que respeita vários papéis reagindo no mesmo dia), recalculado em 21/09/2026. O total é medido por pregão com comunicado (9.192 pregões-papel; vários comunicados no mesmo dia contam uma vez). Contando cada evento, seria +10,2% e +19,3%."));
filhos.push(h2("Como ler"));
filhos.push(marcador("Contra pregões sem comunicado, o Fato Relevante dá p < 10^{-50} nas duas medidas: não é acaso."));
filhos.push(marcador("O excesso do Fato Relevante é **2,65 vezes** o do Comunicado ao Mercado na volatilidade e **3,0 vezes** no volume (p = 7×10^{-18} e 5×10^{-26}). A hierarquia da lei aparece no preço."));
filhos.push(marcador("O total (+9,6%) fica perto do Comunicado ao Mercado porque ele responde por 70% dos eventos."));
filhos.push(marcador("O efeito não é só de casos extremos, mas os casos grandes puxam a média: a **mediana** do Fato Relevante sobe +13,5% na volatilidade e +20,0% no volume, contra +18,2% e +36,4% na média."));
filhos.push(marcador("**Direção: nenhum efeito.** A variação média do pregão inteiro é igual com e sem comunicado (p = 0,74)."));

// ── 2. medição PETR4 ─────────────────────────────────────────────────────────
filhos.push(h1("2. Medição só na PETR4: jornal, CVM e combinação"));
filhos.push(par("Mesma régua, agora para a PETR4 (2.309 pregões), contra **618 noites em que não houve nada** (nem notícia acima do normal, nem comunicado). “Muita notícia” significa mais de 50 textos de portal na noite.", { keepNext: true }));
const ns = (x, p) => [{ t: x }, { t: p, small: true }];
filhos.push(tabela(
  ["Tipo de noite", "Noites", "Volatilidade", "Tamanho da variação", "Volume"],
  [
    ["Muita notícia de jornal (sem CVM)", "449", ns("−3,5%", "n.s. (p = 0,11)"), ns("−0,6%", "n.s. (p = 0,95)"), ns("−5,0%", "p = 0,004")],
    ["Comunicado ao Mercado", "828", ns("−0,5%", "n.s. (p = 0,97)"), ns("−1,3%", "n.s. (p = 0,79)"), ns("−1,1%", "p = 0,042")],
    ["Fato Relevante", "414", ns("+6,4%", "n.s. (p = 0,24)"), ns("+18,9%", "p = 0,040"), ns("+11,9%", "n.s. (p = 0,81)")],
    [[{ t: "Fato Relevante + muita notícia", b: true }], "225", ns("+13,2%", "p = 0,043"), v("+38,2%", "p = 0,0002"), ns("+19,4%", "n.s. (p = 0,14)")],
  ],
  [3038, 900, 1900, 1900, 1900], { destaque: [3] }));
filhos.push(nota("n.s. = não significativo. “Tamanho da variação” é o valor absoluto do retorno do dia. Foram 12 comparações (limite de p = 0,004 pela correção de Bonferroni): o +38,2% passa com folga e a queda de 5,0% do volume passa por pouco. As demais não passam."));
filhos.push(marcador("**Nem o jornal sozinho nem o Comunicado ao Mercado movem o preço.** O Fato Relevante com muita notícia move o tamanho da variação em +38%."));
filhos.push(marcador("**Ressalva:** é um único papel e 225 noites. Falta replicar em VALE3, ITUB4 e BBAS3, com bootstrap e teste-placebo. Na PETR4 sozinha o volume não sobe de forma significativa."));

// ── 3. projeção ──────────────────────────────────────────────────────────────
filhos.push(h1("3. Projeção"));
filhos.push(par("Foram projetados três alvos: **volatilidade**, **dia excepcional** e **direção**. O volume não foi projetado.", { keepNext: true }));

filhos.push(h2("3.1 Volatilidade da PETR4"));
filhos.push(tabela(
  ["O que o modelo enxerga", "Ganho sobre o HAR simples (R²-OS)", "Erro médio (MAE)"],
  [
    ["A. Só preços (sem notícia e sem CVM)", "+6,90%", "0,0520"],
    ["B. Preços + notícia (sem CVM)", [{ t: "+7,53%", b: true }], "0,0526"],
    ["C. Preços + CVM (sem notícia)", "+6,91%", "0,0526"],
    ["D. Preços + notícia + CVM (a combinação)", "+7,47%", "0,0529"],
  ],
  [4438, 2900, 2300]));
filhos.push(nota("Protocolo do Cap. 3, 647 pregões de teste que o modelo não viu. R²-OS: quanto o erro da previsão diminui em relação ao HAR simples, que prevê a volatilidade de amanhã com a média dos últimos 1, 5 e 22 dias. Meta: acima de +5%."));
filhos.push(marcador("O ganho de cerca de 7% **já existe sem texto** (linha A): vem do método de combinar modelos, não da notícia."));
filhos.push(marcador("A notícia acrescenta 0,63 ponto, a CVM sozinha 0,01 e as duas 0,57. Diferenças dessa ordem tratamos como empate; o arquivo de resultados não traz teste de significância para elas."));
filhos.push(marcador("O erro médio (MAE) até **piora** um pouco quando entra texto."));

filhos.push(h2("3.2 Dia excepcional (os 10% mais agitados)"));
filhos.push(tabela(
  ["O que o modelo enxerga", "AUC"],
  [
    ["Só mercado (sem texto)", [{ t: "0,794", b: true }]],
    ["Só notícia", "0,609"],
    ["Só CVM (rótulos)", "0,573"],
    ["Notícia + CVM", "0,624"],
    ["Mercado + texto", "0,786"],
  ],
  [6638, 3000]));
filhos.push(nota("AUC: 0,50 equivale a uma moeda; 1,00 é acerto perfeito. PETR4, 1.566 previsões fora da amostra."));
filhos.push(marcador("O texto sozinho tem alguma informação (AUC 0,57 a 0,62), mas o mercado tem 0,79. **Somar texto ao mercado não acrescenta:** a diferença de AUC é −0,008 (IC 95%: −0,032 a +0,015), com o zero dentro."));
filhos.push(marcador("Em descrição simples, sem modelo: em noites de Fato Relevante com muita notícia, **15,7%** dos dias são excepcionais contra 9,4% da base (1,67 vez, p = 0,00015). Nenhum dos dois sinais funciona sozinho."));

filhos.push(h2("3.3 Direção"));
filhos.push(tabela(
  ["O que o modelo enxerga", "SVM: acerto", "XGBoost: acerto", "SVM: AUC", "XGBoost: AUC"],
  [
    [[{ t: "Palpite fixo (classe majoritária)", b: true }], "53,14%", "53,14%", "—", "—"],
    ["Só preços", "52,07%", "49,31%", "0,478", "0,493"],
    ["Preços + notícia", "52,53%", "52,83%", "0,503", "0,525"],
    ["Preços + CVM (sem notícia)", "52,53%", "49,92%", "0,507", "0,475"],
    ["Preços + notícia + CVM", "54,36%", "50,84%", "0,489", "0,495"],
  ],
  [3238, 1600, 1600, 1600, 1600], { destaque: [0] }));
filhos.push(nota("Protocolo do Cap. 3, 653 pregões de teste. Nenhuma linha se distingue do palpite fixo: o maior acerto (54,36%) está 1,2 ponto acima, e o teste binomial contra 53,14% dá p = 0,56."));
filhos.push(marcador("O 54,36% do SVM com notícia + CVM tem **AUC 0,489, abaixo de 0,50**: acerta por chutar na proporção certa, não por distinguir altas de baixas."));
filhos.push(marcador("Nas noites de Fato Relevante, jornal + CVM acertou 55,2% contra 51,5% do palpite fixo (+3,7 pontos). O p = 0,04 divulgado antes comparava com 50%; **contra o palpite fixo é ≈ 0,15** (recalculado em 21/09/2026)."));

// ── limites e próximos passos ────────────────────────────────────────────────
filhos.push(h1("Limites e próximos passos"));
filhos.push(par("**O que não afirmamos**", { keepNext: true, after: 60 }));
filhos.push(marcador("Que o texto **preveja** o preço: a agitação medida depois do comunicado não melhora a previsão feita só com o histórico de preços."));
filhos.push(marcador("Que o +38% valha além da PETR4, nem que a notícia o cause: o desenho mede associação."));
filhos.push(marcador("Nada sobre a previsão do volume."));
filhos.push(par("**Próximos passos propostos**", { keepNext: true, before: 100, after: 60 }));
filhos.push(marcador("Projetar o volume no mesmo protocolo (HAR de volume), com e sem CVM."));
filhos.push(marcador("Extrair os embeddings das 54.259 notícias no Colab, para pôr jornal e CVM em pé de igualdade no modelo."));
filhos.push(marcador("Replicar o +38% em VALE3, ITUB4 e BBAS3, com bootstrap e teste-placebo."));

// ═════════════════════════════════════════════════════════════════════════════
const doc = new Document({
  creator: "Vanderlei Barbosa da Silva",
  title: "Comunicados da CVM, notícias e mercado — resumo para os orientadores",
  styles: {
    default: { document: { run: { font: FONTE, size: 21 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: FONTE, color: AZUL }, paragraph: { outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 22, bold: true, font: FONTE, color: AZUL }, paragraph: { outlineLevel: 1 } },
    ],
  },
  numbering: {
    config: [
      { reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 360, hanging: 220 } } } }] },
      { reference: "num", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 420, hanging: 320 } } } }] },
    ],
  },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } } },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          tabStops: [{ type: TabStopType.RIGHT, position: LARG }],
          children: [
            new TextRun({ text: "Comunicados da CVM, notícias e mercado", size: 16, color: CINZA }),
            new TextRun({ children: [new Tab(), "Página ", PageNumber.CURRENT], size: 16, color: CINZA }),
          ],
        })],
      }),
    },
    children: filhos,
  }],
});

Packer.toBuffer(doc).then((b) => { fs.writeFileSync(SAIDA, b); console.log("gerado:", SAIDA, b.length, "bytes"); });

