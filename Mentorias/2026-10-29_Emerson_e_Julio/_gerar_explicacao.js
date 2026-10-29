// Gera 01_EXPLICACAO_SIMPLES.docx — mentoria de 29/10/2026.
const fs = require("fs"), path = require("path");
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType,
  AlignmentType, BorderStyle, ShadingType, HeadingLevel, LevelFormat, Footer,
  PageNumber, TabStopType, Tab } = require("docx");

const SAIDA = process.argv[2];
const RAIZ = path.resolve(__dirname, "..", "..");
const D = JSON.parse(fs.readFileSync(path.join(RAIZ, "CVM", "dados", "dias_com_evento.json"), "utf8"));
const P = D.papeis, AG = D.agrupado, TICK = Object.keys(P);

const FONTE = "Arial", AZUL = "1F3864", CINZA = "595959", LINHA = "BFBFBF", LARG = 9638;
const runs = (t, b = {}) => t.split(/(\*\*[^*]+\*\*)/).filter(Boolean).map((x) =>
  x.startsWith("**") ? new TextRun({ text: x.slice(2, -2), bold: true, ...b })
                     : new TextRun({ text: x, ...b }));
const par = (t, o = {}) => new Paragraph({ children: runs(t, { size: o.size || 22, color: o.color, italics: o.italics }),
  spacing: { before: o.before ?? 0, after: o.after ?? 140, line: 288 } });
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
function tab(cb, ln, lg, o = {}) {
  const al = (k) => (k === 0 ? AlignmentType.LEFT : AlignmentType.CENTER);
  return new Table({ width: { size: LARG, type: WidthType.DXA }, columnWidths: lg,
    rows: [new TableRow({ tableHeader: true, cantSplit: true,
      children: cb.map((c, k) => cel(c, lg[k], { b: true, fundo: "D9E2F3", align: al(k), cor: AZUL })) }),
      ...ln.map((l, i) => new TableRow({ cantSplit: true,
        children: l.map((c, k) => cel(c, lg[k], { align: al(k),
          fundo: (o.vermelho || []).includes(i) ? "FCE4E4" : undefined })) }))] });
}
const pp = (x) => `${x >= 0 ? "+" : "−"}${Math.abs(x).toFixed(2).replace(".", ",")}`;

const K = [];
K.push(new Paragraph({ children: [new TextRun({ text: "Olhar só os dias que têm notícia",
  bold: true, size: 44, color: AZUL, font: FONTE })], spacing: { after: 60 } }));
K.push(par("A hipótese era boa. O resultado foi o contrário — e o motivo é o que interessa",
  { size: 25, color: CINZA, after: 80 }));
K.push(par("Vanderlei Barbosa da Silva · PPGIa/PUCPR · Para os Profs. Emerson Paraiso e Julio Nievola · 29 de outubro de 2026",
  { size: 18, color: CINZA, after: 260 }));

// ── p_pos / p_neg ───────────────────────────────────────────────────────────
K.push(h1("Antes: o que são p(positivo) e p(negativo)"));
K.push(par("O FinBERT não devolve \"positivo\" ou \"negativo\" direto. Ele devolve **três números que somam 1** — o quanto ele aposta em cada classe."));
K.push(tab(["Comunicado real da Petrobras", "p(positivo)", "p(negativo)", "p(neutro)"],
  [["\"Petrobras sobre ofício do Ministério de Minas e Energia\"", "0,050", "0,506", "0,444"]],
  [4800, 1613, 1613, 1612]));
K.push(par("Leia como repartição de convicção: **5% positivo, 51% negativo, 44% neutro**. Vence o negativo, mas sem folga — ele está quase em cima do muro."));
K.push(par("É como um júri de cem pessoas lendo o texto: cinco acham positivo, cinquenta e um acham negativo, quarenta e quatro ficam indiferentes."));
K.push(caixa("**E por que isso importa:** 70% dos comunicados da Petrobras caem em \"neutro\". Dependendo da fórmula que se use para transformar esses três números em um só, esses 70% viram **zero** ou viram **um valor pequeno**. São duas escolhas diferentes, e a pesquisa estava usando as duas em lugares diferentes — ver o fim deste documento."));

// ── a hipótese ──────────────────────────────────────────────────────────────
K.push(h1("A hipótese que testamos"));
K.push(par("Na conversa anterior apareceu um número incômodo: **em 6 de cada 10 pregões não houve comunicado nenhum** na véspera. Nesses dias, a coluna de sentimento é um zero de preenchimento — não é informação, é ausência dela."));
K.push(par("Daí a hipótese, que é razoável: se medirmos **só nos dias em que houve comunicado**, o sentimento deveria mostrar o seu valor."));

K.push(h1("O resultado: a hipótese não se confirmou"));
K.push(par("Os índices não melhoraram. **Pioraram.** Mas o motivo é instrutivo, e é ele que vale levar à reunião."));

K.push(h2("Primeiro problema: sozinho, nenhum papel tem amostra suficiente"));
K.push(tab(["Papel", "Pregões com comunicado", "Margem de erro"],
  TICK.map((t) => [t, `${P[t].n_com_evento}  (${P[t].pct_com_evento.toFixed(1).replace(".", ",")}%)`,
    P[t].resumo && P[t].resumo.ic95_com_evento_pp
      ? `±${P[t].resumo.ic95_com_evento_pp.toFixed(1).replace(".", ",")} pontos`
      : "não avaliável"]),
  [1800, 4000, 3838], { vermelho: [TICK.indexOf("ABEV3")] }));
K.push(caixa("**Com margem de erro de ±8 a ±17 pontos, não há como detectar um efeito de 2 ou 3 pontos** — que é a ordem de grandeza que procuramos. É como tentar pesar uma carta numa balança de caminhão: o instrumento não tem precisão para a pergunta."));
K.push(par("A Ambev saiu da análise: só **5 pregões** com comunicado em todo o teste. Não foi excluída por dar resultado ruim — foi excluída porque não há o que medir."));

K.push(h2("A saída: juntar os dez papéis num só conjunto"));
K.push(par(`Como nenhum papel isolado tinha amostra, juntei os dez. Isso é legítimo porque todos passaram pelo mesmo protocolo e pela mesma janela. O número de dias com comunicado sobe para **${AG[Object.keys(AG)[0]].so_dias_com_evento.n}** e a margem de erro cai para **±${AG[Object.keys(AG)[0]].so_dias_com_evento.ic95_meia_largura_pp.toFixed(1).replace(".", ",")} pontos** — aí sim dá para medir.`));
K.push(tab(["Arranjo", "Todos os dias", "Só com comunicado", "Melhorou?"],
  Object.entries(AG).map(([b, v]) => [b,
    `${pp(v.todos_os_dias.ganho_pp)} pp`,
    `${pp(v.so_dias_com_evento.ganho_pp)} pp`,
    v.so_dias_com_evento.ganho_pp > v.todos_os_dias.ganho_pp ? "sim" : "NÃO"]),
  [4200, 1900, 2100, 1438], { vermelho: Object.keys(AG).map((_, i) => i) }));
K.push(nota("Ganho sobre o palpite fixo de cada subconjunto. Negativo = pior que simplesmente repetir sempre o mesmo lado."));
K.push(par("**Em todos os seis arranjos, olhar só os dias com comunicado piorou.** E nos dois que usam apenas preço, o déficit é grande o bastante para ser estatisticamente confiável — ou seja, nesses dias o modelo é **comprovadamente pior** que não fazer nada."));

K.push(h2("Testei também a objeção óbvia"));
K.push(par("Alguém poderia dizer: \"o modelo foi treinado num mundo onde 60% dos dias não têm comunicado — claro que ele não se sai bem no subconjunto\". Justo. Então treinei um **modelo especialista**, usando **apenas** dias de comunicado."));
K.push(par("**Também não resolveu:** piorou em 6 dos 7 papéis em que havia treino suficiente. Em dois papéis não deu nem para treinar — menos de 100 dias de comunicado disponíveis."));

K.push(h2("Um padrão que vale notar — mas que eu não afirmo"));
K.push(par("Compare, na tabela acima, as duas primeiras linhas (só preço) com as quatro seguintes (com sentimento). Nos dias com comunicado, os arranjos **com** sentimento erram **menos** que os de preço puro — uma diferença de dois a três pontos."));
K.push(par("Pode ser que o sentimento atue, nesses dias, **reduzindo o erro** em vez de produzir acerto. É um padrão consistente, mas **não testei essa diferença diretamente** — isso exigiria um teste pareado que não fiz. Fica como conjectura, não como achado."));

// ── o que significa ─────────────────────────────────────────────────────────
K.push(h1("O que isso significa — e por que fortalece a pesquisa"));
K.push(caixa("**A limitação não está no modelo, nem na forma de medir o sentimento. Está na raridade do fenômeno.** Comunicado oficial depois do fechamento acontece em 1% a 28% dos pregões, conforme o papel. Para detectar um efeito de 2 ou 3 pontos com o rigor que esta pesquisa adota, seria preciso mais eventos do que uma década de dez papéis oferece."));
K.push(par("**O caminho não passa por um modelo mais elaborado — passa por uma base maior.** Mais ativos, horizonte mais longo, ou os dois. Isso é uma recomendação concreta, não uma desculpa."));
K.push(par("E é coerente com o que a pesquisa já tinha documentado sobre o efeito de cauda: a divulgação **move** o preço, e isso foi medido com significância inequívoca; mas o movimento se concentra numa minoria de eventos. A regularidade que a previsão exigiria não está no caso típico."));

// ── divergência de fórmula ──────────────────────────────────────────────────
K.push(h1("Uma divergência que encontrei e corrigi"));
K.push(par("Ao verificar os números, achei que a dissertação e o código usavam **fórmulas diferentes** para transformar os três números do FinBERT em um só:"));
K.push(tab(["Onde", "Fórmula", "O que acontece com um comunicado neutro"],
  [["Dissertação (Cap. 3) e o ramo de notícias", "polaridade × confiança", "vira exatamente ZERO"],
   ["Ramo da CVM (scripts 18 a 24)", "p(positivo) − p(negativo)", "conserva a inclinação, não zera"]],
  [3300, 2600, 3738]));
K.push(par("Isso importa porque **70% dos comunicados são neutros** — sob a primeira fórmula, todos virariam zero."));
K.push(par("**Como resolvi:** em vez de escolher uma no escuro, rodei **as duas** como variantes (são as linhas A e B da tabela de resultados), e medi: o desvio-padrão é 0,319 numa e 0,344 na outra — praticamente igual. **A diferença entre elas não altera nenhuma conclusão.** A dissertação agora documenta as duas, com a medição."));
K.push(nota("Isto é o tipo de inconsistência que um examinador atento encontra. Melhor termos achado antes."));

const doc = new Document({ creator: "Vanderlei Barbosa da Silva",
  title: "Olhar só os dias que têm notícia",
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
      children: [new TextRun({ text: "Só os dias com notícia — 29/10/2026", size: 16, color: CINZA }),
                 new TextRun({ children: [new Tab(), "Página ", PageNumber.CURRENT], size: 16, color: CINZA })] })] }) },
    children: K }] });

Packer.toBuffer(doc).then((b) => { fs.writeFileSync(SAIDA, b); console.log("gerado:", SAIDA, b.length, "bytes"); });
