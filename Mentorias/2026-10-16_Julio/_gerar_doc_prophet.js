// Gera 03_Prophet_Explicacao_e_Resultados.docx — perguntas de 23/10/2026
// Uso: npm install docx && node _gerar_doc_prophet.js <saida.docx>
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType,
  AlignmentType, BorderStyle, ShadingType, HeadingLevel, LevelFormat, Footer,
  PageNumber, TabStopType, Tab,
} = require("docx");

const SAIDA = process.argv[2];
const RAIZ = path.resolve(__dirname, "..", "..");
const EXP = JSON.parse(fs.readFileSync(path.join(RAIZ, "CVM", "dados", "prophet_vs_garch_svm_xgboost.json"), "utf8"));
let SIM = null;
try { SIM = JSON.parse(fs.readFileSync(path.join(RAIZ, "CVM", "dados", "simulacao_reais_por_investidor.json"), "utf8")); } catch (e) { SIM = null; }
// nome da empresa e peso no Ibovespa vivem no JSON do script 22, não no do 23
const TOP = JSON.parse(fs.readFileSync(path.join(RAIZ, "CVM", "dados", "comparativo_top10_acoes.json"), "utf8")).papeis;

const FONTE = "Arial", AZUL = "1F3864", CINZA = "595959", LINHA = "BFBFBF";
const LARG = 9638;
const TICKERS = Object.keys(EXP.papeis);

function runs(t, base = {}) {
  return t.split(/(\*\*[^*]+\*\*)/).filter(Boolean).map((x) =>
    x.startsWith("**") ? new TextRun({ text: x.slice(2, -2), bold: true, ...base })
                       : new TextRun({ text: x, ...base }));
}
const par = (t, o = {}) => new Paragraph({
  children: runs(t, { size: o.size || 21, color: o.color, italics: o.italics }),
  spacing: { before: o.before ?? 0, after: o.after ?? 120, line: 276 },
  alignment: o.align,
});
const nota = (t) => par(t, { size: 16, color: CINZA, italics: true, before: 60, after: 180 });
const marcador = (t) => new Paragraph({
  children: runs(t, { size: 21 }),
  numbering: { reference: "bul", level: 0 },
  spacing: { after: 80, line: 276 },
});
const h1 = (t) => new Paragraph({
  heading: HeadingLevel.HEADING_1, keepNext: true,
  children: [new TextRun({ text: t, bold: true, size: 26, color: AZUL, font: FONTE })],
  spacing: { before: 300, after: 140 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: AZUL, space: 2 } },
});
const h2 = (t) => new Paragraph({
  heading: HeadingLevel.HEADING_2, keepNext: true,
  children: [new TextRun({ text: t, bold: true, size: 22, color: AZUL, font: FONTE })],
  spacing: { before: 220, after: 90 },
});

const borda = { style: BorderStyle.SINGLE, size: 4, color: LINHA };
const bordas = { top: borda, bottom: borda, left: borda, right: borda };
function celula(txt, larg, o = {}) {
  return new TableCell({
    width: { size: larg, type: WidthType.DXA }, borders: bordas,
    shading: o.fundo ? { fill: o.fundo, type: ShadingType.CLEAR, color: "auto" } : undefined,
    margins: { top: 50, bottom: 50, left: 90, right: 90 },
    children: [new Paragraph({
      alignment: o.align, keepNext: true, spacing: { after: 0, line: 252 },
      children: runs(String(txt), { size: o.size || 18, bold: o.b, color: o.cor }),
    })],
  });
}
function tabela(cab, linhas, largs, o = {}) {
  const al = (k) => (k === 0 ? AlignmentType.LEFT : AlignmentType.CENTER);
  const head = new TableRow({
    tableHeader: true, cantSplit: true,
    children: cab.map((c, k) => celula(c, largs[k], { b: true, fundo: "D9E2F3", align: al(k), cor: AZUL })),
  });
  const body = linhas.map((l, i) => new TableRow({
    cantSplit: true,
    children: l.map((c, k) => celula(c, largs[k], {
      align: al(k), fundo: (o.destaque || []).includes(i) ? "FFF2CC" : undefined,
    })),
  }));
  return new Table({ width: { size: LARG, type: WidthType.DXA }, columnWidths: largs, rows: [head, ...body] });
}
const pct = (x, c = 2) => `${x.toFixed(c).replace(".", ",")}%`;
const sinal = (x, c = 1) => `${x >= 0 ? "+" : "−"}${Math.abs(x).toFixed(c).replace(".", ",")}%`;
const brl = (x) => (x < 0 ? "−" : "+") + "R$ " + Math.abs(Math.round(x)).toLocaleString("pt-BR");
const brl0 = (x) => "R$ " + Math.round(x).toLocaleString("pt-BR");

const K = [];
K.push(new Paragraph({
  children: [new TextRun({ text: "O Prophet na pesquisa", bold: true, size: 40, color: AZUL, font: FONTE })],
  spacing: { after: 60 },
}));
K.push(par("O que ele usou, em que papéis, em que janela — e quanto daria em reais", { size: 24, color: CINZA, after: 80 }));
K.push(par("Vanderlei Barbosa da Silva · PPGIa/PUCPR · Para os Profs. Emerson Paraiso e Julio Nievola · 23 de outubro de 2026", { size: 17, color: CINZA, after: 240 }));

// ── 1 ────────────────────────────────────────────────────────────────────────
K.push(h1("1. O que o Prophet usou para fazer as projeções"));
K.push(par("Antes de tudo, a distinção que motivou todo o experimento: **o Prophet não lê texto.** Ele é uma biblioteca de previsão de série temporal (Taylor e Letham, 2018, do Meta/Facebook) — projeta números ao longo do tempo. Quem lê e classifica os comunicados continua sendo o FinBERT-PT-BR. O Prophet entrou como **mais um método de previsão**, não como substituto do classificador."));
K.push(h2("O que entrou como insumo"));
K.push(marcador("**A data e o histórico da própria série que ele deveria prever** — o preço de fechamento, num caso, e a volatilidade condicional do GARCH(1,1) do próprio papel, no outro."));
K.push(marcador("**Tendência e sazonalidade**, que o Prophet estima sozinho: tendência linear por partes com pontos de mudança, sazonalidade semanal e anual. A sazonalidade diária foi desligada (não faz sentido em dado de pregão)."));
K.push(marcador("**Numa segunda versão, o sentimento dos comunicados da CVM como variável regressora** — a média de (probabilidade positiva − probabilidade negativa) que o FinBERT já tinha atribuído aos comunicados entregues após as 17h, associada ao pregão que podia reagir a eles."));
K.push(h2("O que NÃO entrou, e é importante dizer"));
K.push(marcador("**Notícia de jornal.** Não entrou em nenhum dos 10 papéis — o corpus classificado não está disponível nesta máquina. Vale para o Prophet e para os modelos clássicos igualmente."));
K.push(marcador("**Os atributos de preço defasados** (retorno de ontem, volatilidade de ontem) que alimentam o SVM e o XGBoost. O Prophet não os recebe porque não é assim que ele funciona: ele consome a série inteira e decompõe. **Isso é uma assimetria real entre os métodos**, e não um descuido — é a diferença de desenho que o experimento justamente pretendia testar."));

// ── 2 ────────────────────────────────────────────────────────────────────────
K.push(h1("2. Quais papéis, e por quê"));
K.push(par("Os **10 papéis de maior peso na carteira teórica oficial do Ibovespa** (fonte: B3, consultada em 02/10/2026), **restritos aos que já fazem parte desta pesquisa** — isto é, que já têm comunicados da CVM coletados e classificados pelo FinBERT, e preço coletado."));
K.push(tabela(
  ["Papel", "Empresa", "Peso no Ibovespa"],
  TICKERS.map((tk) => [tk, TOP[tk].empresa, pct(TOP[tk].peso_ibovespa_pct, 2)]),
  [1600, 5038, 3000]));
K.push(nota("Fonte: B3, carteira teórica do Ibovespa, data-base 02/10/2026."));
K.push(par("**O critério é objetivo e verificável** — peso no índice, não escolha pessoal. E é restrito ao que já estava coletado porque incluir outros exigiria coletar e classificar comunicados da CVM do zero."));
K.push(par("**Ficaram de fora, por falta de dado coletado:** WEGE3, AXIA3 (a ex-Eletrobras, que trocou de ticker), EMBJ3 (Embraer), CPLE3 (Copel) e ENEV3 (Eneva). Se os senhores quiserem esses nomes especificamente, é coleta nova."));

// ── 3 ────────────────────────────────────────────────────────────────────────
K.push(h1("3. A janela de tempo"));
K.push(par("Mesma divisão usada em todo o Capítulo 4 da dissertação, **estritamente cronológica, sem embaralhar** — 60% treino, 15% validação, 25% teste:"));
K.push(tabela(
  ["Conjunto", "De", "Até", "Pregões", "Para que serve"],
  [
    ["Treino", "05/06/2017", "28/12/2022", "1.388", "o modelo aprende"],
    ["Validação", "29/12/2022", "22/05/2024", "347", "ajuste de escolhas"],
    ["Teste", "23/05/2024", "15/09/2026", "579", "medição final, intocado"],
  ],
  [1500, 1700, 1700, 1100, 3638], { destaque: [2] }));
K.push(nota("Os números são da PETR4; os demais papéis têm a mesma extensão (2.314 pregões cada) porque a coleta de preço cobre o mesmo período para todos."));
K.push(par("**Uma diferença de tratamento que precisa ficar registrada.** O SVM, o XGBoost e o HAR são ajustados **uma única vez** (sobre treino + validação) e aplicados ao teste inteiro. O Prophet é **reajustado a cada 21 pregões**, em janela expansiva, prevendo no máximo um mês à frente de cada vez."));
K.push(par("O motivo: na primeira execução o Prophet foi ajustado uma vez só e instado a prever os 579 pregões de uma vez — quase dois anos sem se reancorar. A tendência divergiu e o erro ficou duas ordens de grandeza acima de qualquer referência. **Não era o Prophet sendo ruim; era um resultado degenerado, sem valor informativo.** O reajuste periódico corrige isso."));

// ── 4 ────────────────────────────────────────────────────────────────────────
K.push(h1("4. O resultado do experimento"));
K.push(h2("A régua justa, e por que ela precisou ser construída"));
K.push(par("A comparação original era **desleal com o Prophet**, e isso foi corrigido antes de reportar. A previsão ingênua (\"repete o fechamento de ontem\") enxerga o preço de ontem em **todo** dia do teste. O Prophet, no 21º dia de um bloco, ainda opera sobre o que sabia **três semanas antes**. Comparar os dois assim é comparar quem responde com a notícia de ontem contra quem responde com a do mês passado."));
K.push(par("Por isso existe a **régua ancorada**: ela segura o último valor conhecido antes do bloco, pelo bloco inteiro — exatamente a mesma informação do Prophet. **É contra ela que o Prophet deve ser julgado.**"));

K.push(h2("Direção do pregão seguinte"));
K.push(tabela(
  ["Papel", "Classe majoritária", "Melhor clássico", "Prophet", "Prophet prevê alta em"],
  TICKERS.map((tk) => {
    const p = EXP.papeis[tk].direcao, m = p.melhor_classico;
    return [tk, pct(p.majoritaria * 100), pct(p.arms[m].acuracia * 100),
            pct(p.arms["Prophet (preço)"].acuracia * 100),
            pct(p.arms["Prophet (preço)"].pct_previu_alta, 1)];
  }),
  [1300, 2100, 2100, 2000, 2138]));
K.push(nota("A última coluna é diagnóstico: um previsor que aponte sempre o mesmo lado reproduz a classe majoritária sem conter informação alguma."));
K.push(par("O Prophet ficou abaixo do melhor modelo clássico em **7 dos 10 papéis**. Mas o ponto que importa mais: **nenhum dos dois se distingue de forma confiável do palpite da classe majoritária** — o que reitera, por outra via, a conclusão que o capítulo já sustentava."));

K.push(h2("Volatilidade e preço, contra a régua justa"));
K.push(tabela(
  ["Papel", "Prophet — volatilidade", "Prophet — preço", "Persistência diária (preço)"],
  TICKERS.map((tk) => [tk,
    sinal(EXP.papeis[tk].volatilidade.arms["Prophet (volatilidade)"].r2os_vs_ancorada),
    sinal(EXP.papeis[tk].preco.arms["Prophet (preço)"].r2os_vs_ancorada),
    sinal(EXP.papeis[tk].preco.arms["Ingênua diária (fechamento de ontem)"].r2os_vs_ancorada)]),
  [1500, 2800, 2600, 2738]));
K.push(nota("R²-OS: redução do erro quadrático contra a régua ancorada. Negativo = pior que simplesmente manter o último valor conhecido. A última coluna mede o valor de se reatualizar todo dia — não a qualidade de um modelo."));
K.push(par("**O resultado é inequívoco e negativo: em 10 de 10 papéis, nos dois alvos, o Prophet erra mais do que simplesmente não fazer nada**, dispondo da mesma informação. Extrapolar tendência, que é a força do Prophet em séries de negócio, vira passivo em preço de ação — a inclinação estimada no passado recente em geral já virou antes de o bloco de previsão terminar."));
K.push(par("**E há um achado embutido na última coluna**, que responde a pergunta feita na mentoria de 12/10 sobre quando o esforço computacional se justifica: só reatualizar todo dia, em vez de uma vez por mês, vale de **+90% a +94%**. Nesta base, **a frequência de reancoragem pesa muito mais que a sofisticação do modelo.** Reajustar o Prophet diariamente custaria cerca de 21 vezes mais processamento (≈1,3 s por ajuste) para disputar com uma régua que é de graça."));

// ── 5 — em reais ─────────────────────────────────────────────────────────────
K.push(h1("5. Quanto isso daria em reais, por investidor"));
if (SIM) {
  K.push(par(`Aplicando as decisões de cada modelo sobre o **valor médio investido por investidor** de cada papel (ações em circulação ÷ número de acionistas, do Formulário de Referência da CVM, × preço), ao longo dos 579 pregões de teste. Regra: **${SIM.regra}**.`));
  K.push(tabela(
    ["Papel", "Valor investido (médio)", "Comprar e segurar", "Melhor clássico", "Prophet"],
    TICKERS.map((tk) => {
      const s = SIM.papeis[tk];
      return [tk, brl0(s.valor_investido_medio), brl(s.buy_and_hold.resultado_reais),
              brl(s.modelos[s.melhor_modelo].resultado_reais),
              brl(s.modelos["Prophet (preço)"].resultado_reais)];
    }),
    [1300, 2400, 2100, 1919, 1919]));
  K.push(nota("Resultado acumulado nos 579 pregões de teste (23/05/2024 a 15/09/2026), sobre o valor médio investido por investidor de cada papel."));
  K.push(par("**A ressalva, que precisa ser dita junto com o número:** esta simulação **não inclui** corretagem, emolumentos, imposto de renda nem spread de compra e venda, e ignora o efeito de entrar e sair do mercado dezenas de vezes. E, sobretudo: **com o acerto direcional dos modelos perto de cara-ou-coroa, o resultado em reais é em boa parte sorte, não habilidade.** O número serve para dar ordem de grandeza, não para sustentar recomendação."));
  K.push(par("**A leitura honesta da tabela é a comparação com \"comprar e segurar\"** — o que o investidor faria sem modelo algum, sem custo e sem trabalho."));
} else {
  K.push(par("**Esta seção não entrou nesta versão do documento.** O cálculo em reais estava em execução quando o documento foi gerado — são 280 reajustes do Prophet, e não terminaram a tempo da reunião das 16h. Os números saem logo em seguida, na mesma pasta."));
}

// ── fecho ────────────────────────────────────────────────────────────────────
K.push(h1("O que isso significa para a dissertação"));
K.push(par("**O contraponto não enfraquece o arranjo da pesquisa; ele o delimita.** O HAR e os classificadores sobre atributos defasados não são preferidos por sofisticação, e sim porque operam sobre o dado da véspera em vez de projetar tendência."));
K.push(par("E a conclusão central do capítulo **se manteve sob um método de previsão inteiramente distinto**, o que lhe acrescenta robustez: **o sentimento informa o risco, não a direção.**"));
K.push(par("O experimento está escrito na dissertação como a seção 4p, \"Um contraponto de série temporal: o Prophet\", já ligada ao Capítulo 4, com a referência de Taylor e Letham (2018) na bibliografia. O validador do projeto confirma que compila.", { after: 60 }));
K.push(nota("Código: CVM/23_prophet_vs_garch_svm_xgboost.py e CVM/24_simulacao_reais_por_investidor.py. Dados: CVM/dados/prophet_vs_garch_svm_xgboost.json. Planilha com todas as abas estatísticas: 02_Prophet_vs_GARCH_SVM_XGBoost.xlsx, nesta mesma pasta."));

const doc = new Document({
  creator: "Vanderlei Barbosa da Silva",
  title: "O Prophet na pesquisa — explicação e resultados",
  styles: {
    default: { document: { run: { font: FONTE, size: 21 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: FONTE, color: AZUL }, paragraph: { outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 22, bold: true, font: FONTE, color: AZUL }, paragraph: { outlineLevel: 1 } },
    ],
  },
  numbering: { config: [{ reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•",
    alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 360, hanging: 220 } } } }] }] },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } } },
    footers: { default: new Footer({ children: [new Paragraph({
      tabStops: [{ type: TabStopType.RIGHT, position: LARG }],
      children: [new TextRun({ text: "O Prophet na pesquisa — 23/10/2026", size: 16, color: CINZA }),
                 new TextRun({ children: [new Tab(), "Página ", PageNumber.CURRENT], size: 16, color: CINZA })],
    })] }) },
    children: K,
  }],
});

Packer.toBuffer(doc).then((b) => { fs.writeFileSync(SAIDA, b); console.log("gerado:", SAIDA, b.length, "bytes", SIM ? "(com seção em reais)" : "(SEM seção em reais)"); });
