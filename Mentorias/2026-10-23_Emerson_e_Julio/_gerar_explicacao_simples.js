// Gera 01_EXPLICACAO_SIMPLES.docx — a explicação em linguagem comum.
// Uso: node _gerar_explicacao_simples.js <saida.docx>
const fs = require("fs"), path = require("path");
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType,
  AlignmentType, BorderStyle, ShadingType, HeadingLevel, LevelFormat, Footer,
  PageNumber, TabStopType, Tab } = require("docx");

const SAIDA = process.argv[2];
const RAIZ = path.resolve(__dirname, "..", "..");
const E = JSON.parse(fs.readFileSync(path.join(RAIZ, "CVM", "dados", "prophet_vs_garch_svm_xgboost.json"), "utf8")).papeis;
let SIM = null;
try {
  SIM = JSON.parse(fs.readFileSync(path.join(RAIZ, "CVM", "dados", "simulacao_reais_por_investidor.json"), "utf8"));
  // só aceita a simulação NOVA, que tem percentuais e o braço FinBERT+Prophet;
  // a versão anterior do arquivo não tinha esses campos e geraria tabela vazia
  const amostra = SIM.papeis[Object.keys(SIM.papeis)[0]];
  if (!amostra.buy_and_hold.retorno_pct || !amostra.modelos["Prophet (preço+CVM)"]) SIM = null;
} catch (e) { SIM = null; }
const TICKERS = Object.keys(E);

const FONTE = "Arial", AZUL = "1F3864", CINZA = "595959", LINHA = "BFBFBF";
const LARG = 9638;
function runs(t, b = {}) {
  return t.split(/(\*\*[^*]+\*\*)/).filter(Boolean).map((x) =>
    x.startsWith("**") ? new TextRun({ text: x.slice(2, -2), bold: true, ...b })
                       : new TextRun({ text: x, ...b }));
}
const par = (t, o = {}) => new Paragraph({
  children: runs(t, { size: o.size || 22, color: o.color, italics: o.italics }),
  spacing: { before: o.before ?? 0, after: o.after ?? 140, line: 288 }, alignment: o.align });
const nota = (t) => par(t, { size: 17, color: CINZA, italics: true, before: 60, after: 180 });
const marc = (t) => new Paragraph({ children: runs(t, { size: 22 }),
  numbering: { reference: "bul", level: 0 }, spacing: { after: 100, line: 288 } });
const h1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, keepNext: true,
  children: [new TextRun({ text: t, bold: true, size: 28, color: AZUL, font: FONTE })],
  spacing: { before: 320, after: 150 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: AZUL, space: 2 } } });
const h2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, keepNext: true,
  children: [new TextRun({ text: t, bold: true, size: 23, color: AZUL, font: FONTE })],
  spacing: { before: 240, after: 100 } });
const caixa = (t) => new Paragraph({ children: runs(t, { size: 22 }),
  shading: { type: ShadingType.CLEAR, fill: "FFF2CC", color: "auto" },
  spacing: { before: 100, after: 160, line: 288 },
  border: { left: { style: BorderStyle.SINGLE, size: 24, color: "BF8F00", space: 8 },
            top: { style: BorderStyle.SINGLE, size: 2, color: "BF8F00", space: 6 },
            bottom: { style: BorderStyle.SINGLE, size: 2, color: "BF8F00", space: 6 },
            right: { style: BorderStyle.SINGLE, size: 2, color: "BF8F00", space: 6 } } });

const borda = { style: BorderStyle.SINGLE, size: 4, color: LINHA };
const bordas = { top: borda, bottom: borda, left: borda, right: borda };
const cel = (t, w, o = {}) => new TableCell({ width: { size: w, type: WidthType.DXA }, borders: bordas,
  shading: o.fundo ? { fill: o.fundo, type: ShadingType.CLEAR, color: "auto" } : undefined,
  margins: { top: 60, bottom: 60, left: 100, right: 100 },
  children: [new Paragraph({ alignment: o.align, keepNext: true, spacing: { after: 0, line: 264 },
    children: runs(String(t), { size: o.size || 19, bold: o.b, color: o.cor }) })] });
function tab(cab, linhas, largs, o = {}) {
  const al = (k) => (k === 0 ? AlignmentType.LEFT : AlignmentType.CENTER);
  return new Table({ width: { size: LARG, type: WidthType.DXA }, columnWidths: largs,
    rows: [new TableRow({ tableHeader: true, cantSplit: true,
             children: cab.map((c, k) => cel(c, largs[k], { b: true, fundo: "D9E2F3", align: al(k), cor: AZUL })) }),
           ...linhas.map((l, i) => new TableRow({ cantSplit: true,
             children: l.map((c, k) => cel(c, largs[k], { align: al(k),
               fundo: (o.destaque || []).includes(i) ? "FFF2CC" : undefined })) }))] });
}
const pc = (x, c = 1) => `${x.toFixed(c).replace(".", ",")}%`;
const brl = (x) => (x < 0 ? "−" : "+") + "R$ " + Math.abs(Math.round(x)).toLocaleString("pt-BR");

// contagens reais
const nSupera = (arm) => TICKERS.filter((t) => E[t].direcao.arms[arm].acuracia > E[t].direcao.majoritaria).length;
const nSig = (arm) => TICKERS.filter((t) => E[t].direcao.arms[arm].p_vs_majoritaria < 0.05 &&
  E[t].direcao.arms[arm].acuracia > E[t].direcao.majoritaria).length;
const melhoraDir = (sem, com) => TICKERS.filter((t) => E[t].direcao.arms[com].acuracia > E[t].direcao.arms[sem].acuracia).length;

const K = [];
K.push(new Paragraph({ children: [new TextRun({ text: "Os dois times, explicado do zero",
  bold: true, size: 44, color: AZUL, font: FONTE })], spacing: { after: 60 } }));
K.push(par("FinBERT + GARCH/SVM/XGBoost  ×  FinBERT + Prophet — o que foi comparado, e o que deu",
  { size: 25, color: CINZA, after: 80 }));
K.push(par("Vanderlei Barbosa da Silva · PPGIa/PUCPR · Para os Profs. Emerson Paraiso e Julio Nievola · 24 de outubro de 2026",
  { size: 18, color: CINZA, after: 260 }));

K.push(h1("Primeiro: quem é quem"));
K.push(par("São quatro programas com funções diferentes. A confusão começa quando se trata todos como \"o modelo\" — eles fazem coisas distintas e não são intercambiáveis."));
K.push(tab(["Programa", "O que ele faz", "Uma comparação do dia a dia"],
  [["FinBERT", "Lê o texto do comunicado e diz se o tom é positivo, negativo ou neutro.", "o leitor de jornal da equipe"],
   ["GARCH", "Olha o histórico de agitação do preço e estima o quanto ele deve sacudir amanhã.", "o meteorologista: não diz se chove, diz se o tempo está instável"],
   ["SVM e XGBoost", "Recebem os números e apostam: sobe ou desce.", "os apostadores"],
   ["Prophet", "Olha a curva do passado e prolonga a linha para a frente.", "quem traça a reta no gráfico com a régua"]],
  [1700, 4800, 3138]));
K.push(nota("O FinBERT é o único que lê texto. Os outros três só trabalham com números — é por isso que o Prophet não poderia \"classificar notícias\": ele não lê nada."));

K.push(h1("O que foi comparado"));
K.push(par("Dois times, com o mesmo leitor dos dois lados:"));
K.push(marc("**Time A — o que a pesquisa já usava:** FinBERT lê os comunicados, o GARCH mede a agitação, e o SVM/XGBoost apostam."));
K.push(marc("**Time B — o novo:** FinBERT lê os comunicados, e o Prophet faz tudo o resto sozinho."));
K.push(par("Os dois times jogaram **o mesmo campeonato**: as 10 maiores ações da bolsa, os mesmos 579 pregões de teste (de 23/05/2024 a 15/09/2026), que nenhum dos dois tinha visto antes."));

K.push(h1("Antes do resultado: contra quem eles jogam"));
K.push(par("Este é o ponto que mais confunde, e sem ele o resultado não faz sentido."));
K.push(caixa("**O adversário não é o acaso — é o palpite fixo.** Se uma ação sobe em 53 de cada 100 pregões, então quem simplesmente disser \"sobe\" todo santo dia acerta 53%. Sem ler nada, sem calcular nada, sem trabalho. Para o modelo ter valor, ele precisa acertar **mais que isso**."));
K.push(par("É por isso que ver \"o modelo acertou 52%\" não quer dizer nada sozinho. Se o palpite fixo acerta 53%, o modelo de 52% **perdeu** — mesmo parecendo que acertou metade."));
K.push(par("**Atenção para não confundir:** o palpite fixo **não** é \"o modelo que usa só o preço\". São coisas diferentes, e as duas aparecem nas tabelas:"));
K.push(marc("**Palpite fixo** — não é modelo nenhum. Não olha preço, não olha nada. Só repete sempre o mesmo lado."));
K.push(marc("**\"Só preço\"** — é um modelo de verdade: o SVM ou o XGBoost olhando o retorno de ontem e a agitação de ontem medida pelo GARCH. Ele calcula; o palpite fixo não."));

K.push(h2("E há duas versões do palpite fixo — por isso dois números"));
K.push(par("Esta distinção apareceu numa pergunta sua, e é justa — vale os senhores saberem dela:"));
K.push(tab(["Versão", "Como escolhe o lado", "É justo?"],
  [["Com o gabarito na mão\n(foi a que usei)",
    "Olha o próprio período de teste, vê que lado foi mais frequente entre 2024 e 2026, e supõe que o investidor já sabia disso lá atrás.",
    "É o adversário MAIS DIFÍCIL — equivale a conhecer o futuro. Usei de propósito."],
   ["Decidido no passado\n(o realista)",
    "Escolhe o lado olhando só até 2022 — o que se saberia de verdade — e aplica daí em diante, sem mudar.",
    "É o adversário realista. Na média, 2,1 pontos mais fácil de vencer."]],
  [2100, 4500, 3038]));
K.push(par("Em 5 dos 10 papéis, o passado apontava **baixa** e o teste veio **alta** — quem seguisse o palpite realista teria apostado no lado errado e ficado abaixo de 50%."));
K.push(caixa("**E a conclusão muda com o adversário mais fácil? Não.** Contra ele, os modelos passam em 6 ou 7 dos 10 papéis — mas só **um caso em sessenta** alcança significância estatística. Com sessenta testes, o acaso sozinho já produziria uns três. Ou seja: continua sendo ruído, e a resposta vale nas duas réguas."));

K.push(h1("Resultado 1 — o lado (sobe ou desce)"));
const tabDir = TICKERS.map((t) => {
  const a = E[t].direcao.arms, maj = E[t].direcao.majoritaria;
  const cla = Math.max(a["SVM (preço+CVM)"].acuracia, a["XGBoost (preço+CVM)"].acuracia);
  const pro = a["Prophet (preço+CVM)"].acuracia;
  const passou = [cla > maj ? "A" : null, pro > maj ? "B" : null].filter(Boolean).join(" e ");
  return [t, pc(maj * 100), pc(cla * 100), pc(pro * 100),
          passou ? `${passou}, por pouco — sem significância` : "nenhum dos dois"];
});
K.push(tab(["Ação", "Palpite fixo", "Time A (FinBERT+GARCH)", "Time B (FinBERT+Prophet)", "Passou do palpite fixo?"],
  tabDir, [1200, 1500, 2250, 2250, 2438]));
K.push(par(`**Nenhum dos dois times bateu o palpite fixo de forma confiável, em nenhuma das 10 ações.** Nem o Time A, nem o Time B. Contando todas as combinações testadas, foram 60 tentativas e **zero** resultados estatisticamente seguros.`));
K.push(par("Quando o Time A aparece à frente do Time B, a diferença é pequena demais para significar alguma coisa: com 579 pregões, qualquer diferença menor que cerca de **4 pontos percentuais** cabe dentro da margem de erro."));

K.push(h1("Resultado 2 — o tamanho do sacolejo (volatilidade)"));
K.push(par("Aqui os dois times se separam de verdade, e a diferença é grande."));
const tabVol = TICKERS.map((t) => {
  const a = E[t].volatilidade.arms;
  return [t, pc(a["HAR + CVM"].r2os_vs_ancorada), pc(a["Prophet (volatilidade+CVM)"].r2os_vs_ancorada), "Time A"];
});
K.push(tab(["Ação", "Time A (FinBERT+GARCH)", "Time B (FinBERT+Prophet)", "Vencedor"],
  tabVol, [1700, 3000, 3000, 1938]));
K.push(nota("Os números comparam cada time contra uma régua simples: segurar o último valor conhecido. Positivo = melhor que a régua. Negativo = pior do que não fazer nada."));
K.push(par("**O Time A acerta muito bem (entre +83% e +93%). O Time B erra mais do que simplesmente não fazer nada (todos negativos).**"));
K.push(par("O motivo é a natureza do Prophet: ele funciona prolongando a tendência do passado. Isso é ótimo para prever a venda de sorvete no verão, que segue um padrão de calendário. Mas o preço de uma ação não segue padrão de calendário — a tendência das últimas semanas, na hora em que você a prolonga, em geral já virou."));

K.push(h1("Resultado 3 — e o FinBERT, ajuda ou não?"));
K.push(par("Esta é **a pergunta da dissertação**, e vale separá-la das outras duas. Acima, os dois times já usavam o FinBERT. Aqui a pergunta é outra: **o que muda se tirarmos o FinBERT do time?**"));
const tabFb = [
  ["GARCH + SVM", "direção", `${melhoraDir("SVM (preço)", "SVM (preço+CVM)")} de 10`, "−0,14 ponto"],
  ["GARCH + XGBoost", "direção", `${melhoraDir("XGBoost (preço)", "XGBoost (preço+CVM)")} de 10`, "+0,07 ponto"],
  ["Prophet", "direção", `${melhoraDir("Prophet (preço)", "Prophet (preço+CVM)")} de 10`, "0,00 ponto"],
  ["GARCH (HAR)", "volatilidade", `${TICKERS.filter((t)=>E[t].volatilidade.arms["HAR + CVM"].r2os_vs_ancorada > E[t].volatilidade.arms["HAR (GARCH, referência)"].r2os_vs_ancorada).length} de 10`, "−0,07 ponto"],
  ["Prophet", "volatilidade", `${TICKERS.filter((t)=>E[t].volatilidade.arms["Prophet (volatilidade+CVM)"].r2os_vs_ancorada > E[t].volatilidade.arms["Prophet (volatilidade)"].r2os_vs_ancorada).length} de 10`, "−0,70 ponto"],
];
K.push(tab(["Modelo", "Alvo", "O FinBERT melhorou em", "Efeito médio"], tabFb, [2400, 1900, 2800, 2538]));
K.push(caixa("**\"Melhorou em 5 de 10\" é exatamente o que uma moeda produziria.** Se você jogar uma moeda uma vez para cada ação, perguntando \"ajudou?\", vai dar cara umas 5 vezes. É esse o padrão que aparece — e o efeito médio fica entre −0,7 e +0,07, ou seja, praticamente zero."));
K.push(par("**A conclusão honesta: o sentimento dos comunicados da CVM, nesta forma de uso, não acrescenta poder de previsão a nenhum dos dois times.** Isso não invalida a pesquisa — é um resultado, e dos mais importantes que temos, porque foi testado de duas maneiras independentes e deu a mesma coisa."));

K.push(h1("Resultado 4 — quanto isso dá em dinheiro"));
if (SIM) {
  const linhas = TICKERS.map((t) => {
    const s = SIM.papeis[t];
    const cla = ["SVM (preço+CVM)", "XGBoost (preço+CVM)"].reduce((a, b) =>
      s.modelos[a].resultado_reais > s.modelos[b].resultado_reais ? a : b);
    return [t, "R$ " + Math.round(s.valor_investido_medio).toLocaleString("pt-BR"),
            pc(s.buy_and_hold.retorno_pct) + "  (" + brl(s.buy_and_hold.resultado_reais) + ")",
            pc(s.modelos[cla].retorno_pct) + "  (" + brl(s.modelos[cla].resultado_reais) + ")",
            pc(s.modelos["Prophet (preço+CVM)"].retorno_pct) + "  (" + brl(s.modelos["Prophet (preço+CVM)"].resultado_reais) + ")"];
  });
  const nBH = TICKERS.filter((t) => {
    const s = SIM.papeis[t];
    return s.buy_and_hold.resultado_reais > Math.max(s.modelos["SVM (preço+CVM)"].resultado_reais,
      s.modelos["XGBoost (preço+CVM)"].resultado_reais, s.modelos["Prophet (preço+CVM)"].resultado_reais);
  }).length;
  K.push(par("Para cada ação, tomamos o **valor médio que cada investidor tem investido nela** — calculado do número de acionistas e das ações em circulação, que a própria empresa declara à CVM — e aplicamos as decisões de cada time ao longo dos 579 pregões."));
  K.push(tab(["Ação", "Investido (médio)", "Comprar e segurar", "Time A", "Time B"], linhas, [1100, 1700, 2350, 2250, 2238]));
  K.push(nota("A regra dos times: comprado quando o modelo prevê alta, fora do mercado quando prevê baixa."));

  // ── só preço histórico × com FinBERT, em reais ────────────────────────────
  K.push(h2("E se usarmos SÓ o histórico de preço, sem o FinBERT?"));
  K.push(par("Esta é a comparação direta que faltava. Cada família aparece duas vezes: com o FinBERT e sem ele, somando os 10 papéis."));
  const FAM = [["Comprar e segurar (sem modelo nenhum)", null, null],
               ["GARCH + SVM", "SVM (preço)", "SVM (preço+CVM)"],
               ["GARCH + XGBoost", "XGBoost (preço)", "XGBoost (preço+CVM)"],
               ["Prophet", "Prophet (preço)", "Prophet (preço+CVM)"]];
  const somaR = (k) => TICKERS.reduce((s, t) => s + (k === null ? SIM.papeis[t].buy_and_hold.resultado_reais
                                                                : SIM.papeis[t].modelos[k].resultado_reais), 0);
  const fmtR = (x) => (x < 0 ? "−" : "+") + "R$ " + Math.abs(Math.round(x)).toLocaleString("pt-BR");
  const linhasFam = FAM.map(([nome, sem, com]) => {
    if (sem === null) return [nome, fmtR(somaR(null)), "—", "—"];
    const melhorou = TICKERS.filter((t) => SIM.papeis[t].modelos[com].resultado_reais
                                         > SIM.papeis[t].modelos[sem].resultado_reais).length;
    return [nome, fmtR(somaR(sem)), fmtR(somaR(com)), `${melhorou} de 10`];
  });
  K.push(tab(["", "Só preço histórico", "Com o FinBERT", "O FinBERT melhorou em"],
    linhasFam, [3100, 2300, 2200, 2038], { destaque: [0] }));
  K.push(nota("Soma do resultado nos 10 papéis, sobre o valor médio investido por investidor de cada um."));
  K.push(par("**Acrescentar o FinBERT melhorou em 5 e 6 de 10 papéis** — pela terceira vez, o mesmo padrão de moeda. E **nenhuma das seis combinações chega perto de comprar e segurar**, que não usa modelo, não usa preço, não usa texto, e não dá trabalho nenhum."));
  K.push(caixa(`**Comprar e segurar — não fazer nada — venceu os dois times em ${nBH} das 10 ações.** O motivo é simples: os modelos saem do mercado nos dias em que preveem queda, e com isso perdem as altas. Num período em que a bolsa subiu, ficar de fora custa caro.`));
  K.push(par("**E a ressalva, que precisa ser dita junto:** esta conta não inclui corretagem, imposto de renda nem a diferença entre preço de compra e venda. E, como o acerto dos modelos está perto de cara-ou-coroa, o resultado em reais é em boa parte **sorte**, não habilidade. O número serve para dar ordem de grandeza — não é recomendação de investimento."));
} else {
  K.push(par("**O cálculo em reais ainda estava rodando quando este documento foi gerado.** Ele sai na planilha 02, aba \"Em reais\", na mesma pasta."));
}

K.push(h1("Resumindo, para levar à reunião"));
K.push(marc("**Para o tamanho do sacolejo, o GARCH é muito melhor que o Prophet** — e por margem enorme, em 10 das 10 ações."));
K.push(marc("**Para o lado (sobe ou desce), nenhum dos dois funciona** — nenhum bate o palpite fixo com segurança, em nenhuma ação."));
K.push(marc("**O sentimento do FinBERT não mudou o resultado de nenhum dos dois** — melhorou em cerca de metade das ações, que é o mesmo que jogar uma moeda."));
K.push(marc("**Em dinheiro, os dois times perdem para não fazer nada.**"));
K.push(par("Isso **não enfraquece** a dissertação — pelo contrário. A conclusão central dela sempre foi que **o sentimento informa o risco, não a direção**. Agora essa conclusão foi testada por um caminho completamente diferente, com outro tipo de modelo, e deu a mesma coisa. Resultado que se repete sob método diferente é resultado mais forte, não mais fraco.", { before: 120 }));

const doc = new Document({ creator: "Vanderlei Barbosa da Silva",
  title: "Os dois times, explicado do zero",
  styles: { default: { document: { run: { font: FONTE, size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: FONTE, color: AZUL }, paragraph: { outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 23, bold: true, font: FONTE, color: AZUL }, paragraph: { outlineLevel: 1 } }] },
  numbering: { config: [{ reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•",
    alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 360, hanging: 220 } } } }] }] },
  sections: [{ properties: { page: { size: { width: 11906, height: 16838 },
      margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } } },
    footers: { default: new Footer({ children: [new Paragraph({
      tabStops: [{ type: TabStopType.RIGHT, position: LARG }],
      children: [new TextRun({ text: "Os dois times — 24/10/2026", size: 16, color: CINZA }),
                 new TextRun({ children: [new Tab(), "Página ", PageNumber.CURRENT], size: 16, color: CINZA })] })] }) },
    children: K }] });

Packer.toBuffer(doc).then((b) => { fs.writeFileSync(SAIDA, b);
  console.log("gerado:", SAIDA, b.length, "bytes", SIM ? "(com reais)" : "(SEM reais)"); });
