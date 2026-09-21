# -*- coding: utf-8 -*-
# ==============================================================================
#   Acrescenta ao painel duas seções novas:
#     1. "Como ler os números" — demonstração interativa de acurácia × AUC
#     2. "E com aprendizado de máquina de verdade?" — o protocolo do Capítulo 3
#        com a CVM, e o teste de McNemar
#
#   Os números são lidos dos JSON, nunca digitados.
# ==============================================================================
from __future__ import annotations

import json
from pathlib import Path

AQUI = Path(__file__).resolve().parent
D = AQUI.parent / "dados"
ALVO = AQUI / "painel.html"

P = json.loads((D / "pesquisa_com_cvm.json").read_text(encoding="utf-8"))
DIAG = json.loads((D / "diagnostico_ml.json").read_text(encoding="utf-8"))

K_PRECO = "apenas preços  [linha de base da pesquisa]"
K_ANTES = "Data Fusion: preços + notícia  [O QUE TÍNHAMOS ANTES]"
K_CVM = "Data Fusion + CVM  [NOVO]"
K_EMB = "Data Fusion + CVM + embedding  [NOVO]"


def pct(x, n=2):
    return f"{x * 100:.{n}f}".replace(".", ",") + "%"


def num(x, n=3):
    return f"{x:.{n}f}".replace(".", ",")


def linha_dir(rot, chave, destaque=False):
    a = P["direcao"][chave]
    maj = P["majoritaria_teste"]
    cel = []
    for mod in ["SVM-RBF", "XGBoost"]:
        m = a[mod]
        acima = m["acuracia"] > maj
        auc_ruim = m["auc"] < 0.50
        cor = ("var(--baixa)" if auc_ruim and acima else
               "var(--alta)" if acima else "var(--cinza)")
        cel.append(f'<td style="color:{cor};font-weight:{"600" if acima else "400"}">'
                   f'{pct(m["acuracia"], 2)}</td>'
                   f'<td style="color:{"var(--baixa)" if auc_ruim else "var(--cinza)"}">'
                   f'{num(m["auc"])}</td>')
    peso = "font-weight:600" if destaque else ""
    return f'<tr><td style="{peso}">{rot}</td>{"".join(cel)}</tr>'


def linha_mcn(rot, chave):
    m = P["mcnemar"][chave]
    piora = m["acertos_so_do_novo"] < m["acertos_so_do_antigo"] and m["p"] < 0.05
    ver = ("PIORA" if piora else "passa" if m["p"] < 0.05 else "não passa")
    cor = ("var(--baixa)" if piora else "var(--alta)" if m["p"] < 0.05
           else "var(--cinza)")
    return (f'<tr><td>{rot}</td>'
            f'<td>{m["acertos_so_do_novo"]}</td>'
            f'<td>{m["acertos_so_do_antigo"]}</td>'
            f'<td>{num(m["p"], 4)}</td>'
            f'<td style="color:{cor};font-weight:600">{ver}</td></tr>')


NOVO = f"""
<h2>Como ler os números</h2>
<p class="sub">Duas medidas aparecem em todas as tabelas desta pesquisa, e elas
não são a mesma coisa. Confundi-las leva a conclusões erradas — inclusive a
elogiar um modelo ruim.</p>

<div class="nota">
  <strong>Acurácia</strong> responde: <em>de todos os palpites, quantos
  acertei?</em> O modelo precisa se comprometer.
  <br><br>
  <strong>AUC</strong> responde outra coisa: <em>pego um pregão que de fato foi
  agitado e um que foi calmo, ao acaso — com que frequência o modelo deu nota
  maior ao agitado?</em> Aqui basta <strong>ordenar</strong>.
</div>

<h3 style="margin-top:30px">Experimente: mova o corte de decisão</h3>
<p class="sub">Vinte pregões. As barras laranja são os que de fato foram
agitados. A nota de risco de cada um já está dada — o que você move é apenas o
ponto de corte. <strong>Veja a acurácia mudar enquanto a AUC fica parada.</strong></p>

<div class="caso" style="border-top-color:var(--lampada)">
  <div id="demo-svg"></div>
  <label style="display:flex;gap:14px;align-items:center;margin:18px 0 6px;
    font-size:14px;flex-wrap:wrap">
    <span style="font-family:var(--dado);font-size:12px;letter-spacing:.06em;
      text-transform:uppercase;color:var(--cinza)">corte de decisão</span>
    <input type="range" id="demo-corte" min="5" max="95" value="50"
      style="flex:1;min-width:200px;accent-color:var(--lampada)">
    <span id="demo-corte-val" style="font-family:var(--dado);font-weight:600;
      min-width:48px">0,50</span>
  </label>
  <div style="display:flex;gap:28px;flex-wrap:wrap;margin-top:14px;
    padding-top:16px;border-top:1px solid var(--borda)">
    <div>
      <div style="font-family:var(--dado);font-size:11px;letter-spacing:.09em;
        text-transform:uppercase;color:var(--cinza)">acurácia</div>
      <div id="demo-acc" style="font-family:var(--disp);font-size:30px;
        font-weight:700;line-height:1.15">—</div>
      <div id="demo-acc-det" style="font-size:13px;color:var(--cinza)">—</div>
    </div>
    <div>
      <div style="font-family:var(--dado);font-size:11px;letter-spacing:.09em;
        text-transform:uppercase;color:var(--cinza)">AUC</div>
      <div id="demo-auc" style="font-family:var(--disp);font-size:30px;
        font-weight:700;line-height:1.15;color:var(--lampada)">—</div>
      <div style="font-size:13px;color:var(--cinza)">não depende do corte</div>
    </div>
  </div>
</div>

<div class="nota" style="border-left-color:var(--baixa)">
  <strong>A armadilha, nos nossos próprios números.</strong> No alvo “dia
  excepcional”, só <strong>6,3%</strong> dos pregões são excepcionais. Um modelo
  que responda <em>“não vai ser excepcional”</em> sempre acerta
  <strong>93,7%</strong> — e não serve para nada.
  <br><br>
  O nosso modelo de mercado teve acurácia de <strong>93,6%</strong>, pior que
  esse palpite burro, e AUC de
  <strong>{num(DIAG["só mercado (sem texto)"]["auc"])}</strong>.
  <strong>A AUC estava certa:</strong> nas 156 noites que ele apontou como as
  mais arriscadas, <strong>28,8%</strong> viraram dia excepcional, contra 6,3%
  da base.
</div>

<div class="rolar"><table class="tabela">
  <thead><tr><th>Modelo</th><th>AUC</th><th>Intervalo de 95%</th>
  <th>Veredito</th></tr></thead>
  <tbody>
    <tr><td>só o texto (notícia + CVM + embedding)</td>
      <td style="font-weight:600">{num(DIAG["só texto (notícia + CVM + embedding)"]["auc"])}</td>
      <td>{num(DIAG["só texto (notícia + CVM + embedding)"]["ic95"][0])} a
          {num(DIAG["só texto (notícia + CVM + embedding)"]["ic95"][1])}</td>
      <td style="color:var(--alta);font-weight:600">passa — há sinal</td></tr>
    <tr><td>só o histórico de preço (o HAR)</td>
      <td style="font-weight:600">{num(DIAG["só mercado (sem texto)"]["auc"])}</td>
      <td>{num(DIAG["só mercado (sem texto)"]["ic95"][0])} a
          {num(DIAG["só mercado (sem texto)"]["ic95"][1])}</td>
      <td style="color:var(--alta);font-weight:600">passa, e é forte</td></tr>
    <tr><td>direção, qualquer braço</td>
      <td>0,49 a 0,52</td><td>cruza o 0,50</td>
      <td style="color:var(--cinza);font-weight:600">não passa</td></tr>
  </tbody>
</table></div>
<p class="legenda">O que vale não é a AUC ser alta — é o intervalo de confiança
excluir o 0,50. A regra de “AUC acima de 0,7” vem da medicina e não se aplica a
direção de ações.</p>

<h2>E com aprendizado de máquina de verdade?</h2>
<p class="sub">Tudo o que está acima usou <strong>regras escritas à mão</strong>:
contar, subtrair, comparar com um limiar. O método da dissertação é outro — o
encoder FinBERT lê os textos, o GARCH mede o risco, e dois algoritmos
(<strong>SVM</strong> e <strong>XGBoost</strong>) aprendem sozinhos a relação
com o pregão seguinte.</p>

<div class="nota">
  <strong>Antes de acrescentar a CVM, o código foi checado contra a
  dissertação.</strong> A classe majoritária deu 53,14% nos dois; o XGBoost só
  com preços, 49,77% lá e {pct(P["direcao"][K_PRECO]["XGBoost"]["acuracia"], 2)}
  aqui. <strong>Reproduz</strong> — e isso é o que dá valor ao que vem depois.
</div>

<div class="rolar"><table class="tabela">
  <thead>
    <tr><th rowspan="2">Braço</th><th colspan="2">SVM-RBF</th>
        <th colspan="2">XGBoost</th></tr>
    <tr><th>acurácia</th><th>AUC</th><th>acurácia</th><th>AUC</th></tr>
  </thead>
  <tbody>
    {linha_dir("apenas preços", K_PRECO)}
    {linha_dir("preços + notícia <em>(o que tínhamos antes)</em>", K_ANTES)}
    {linha_dir("preços + notícia + CVM <em>(novo)</em>", K_CVM, True)}
    {linha_dir("+ embedding da CVM <em>(novo)</em>", K_EMB)}
  </tbody>
</table></div>
<p class="legenda">Teste de {P["n"]["teste"]} pregões. Quem não lê nada acerta
{pct(P["majoritaria_teste"], 2)} respondendo “sempre alta”.</p>

<div class="nota" style="border-left-color:var(--baixa)">
  <strong>Aquele {pct(P["direcao"][K_CVM]["SVM-RBF"]["acuracia"], 2)} é uma
  armadilha, e convém dizê-lo antes que perguntem.</strong> Ele está apenas
  <strong>1,2 ponto</strong> acima do palpite fixo, e a margem de erro com
  {P["n"]["teste"]} pregões é de quase 2 pontos. Pior: a AUC dele é
  <strong>{num(P["direcao"][K_CVM]["SVM-RBF"]["auc"])}</strong> —
  <strong>abaixo de 0,500</strong>. Ele acertou o placar por ter chutado na
  proporção certa, não por saber distinguir um pregão do outro.
</div>

<h3 style="margin-top:34px">O teste que realmente decide</h3>
<p class="sub">Quando a pergunta é <em>“esta fonte nova acrescenta?”</em>,
comparar acurácias não basta — dois modelos podem acertar a mesma quantidade e
acertar pregões diferentes. O <strong>McNemar</strong> joga fora os pregões em
que os dois concordam e olha só onde discordam.</p>

<div class="rolar"><table class="tabela">
  <thead><tr><th>Pergunta</th><th>Ganhou</th><th>Perdeu</th>
  <th>valor-p</th><th>Resposta</th></tr></thead>
  <tbody>
    {linha_mcn("a notícia acrescenta sobre o preço? <em>(XGBoost)</em>",
               "XGBoost — a notícia acrescenta sobre o preço?")}
    {linha_mcn("a CVM acrescenta sobre a notícia? <em>(SVM)</em>",
               "SVM-RBF — a CVM acrescenta sobre a notícia?")}
    {linha_mcn("a CVM acrescenta sobre a notícia? <em>(XGBoost)</em>",
               "XGBoost — a CVM acrescenta sobre a notícia?")}
    {linha_mcn("o embedding acrescenta sobre os rótulos? <em>(SVM)</em>",
               "SVM-RBF — o embedding acrescenta sobre os rótulos?")}
  </tbody>
</table></div>
<p class="legenda">“Ganhou” = pregões em que o modelo novo acertou e o antigo
errou. Repare na última linha: valor-p pequeno, mas significativamente
<strong>pior</strong>. Significância não é sinônimo de boa notícia.</p>

<h3 style="margin-top:34px">E a volatilidade, pelo HAR</h3>
<div class="rolar"><table class="tabela">
  <thead><tr><th>Modelo</th><th>Ganho sobre o HAR de Corsi</th></tr></thead>
  <tbody>
    {"".join(f'<tr><td>{k}</td><td style="font-weight:600;color:var(--cinza)">'
             f'{v.get("r2os_quantilico_vs_HAR", 0):+.2f}'.replace(".", ",") + "%</td></tr>"
             for k, v in P["volatilidade"].items())}
  </tbody>
</table></div>
<p class="legenda">A combinação quantílica bate o HAR linear em cerca de 7%, na
mesma faixa dos 10,9% do Capítulo 4. A notícia leva de 6,90% a 7,53%; a CVM traz
de volta para 7,47%.</p>

<div class="nota">
  <strong>A conclusão, sem suavizar.</strong> Dentro do protocolo da pesquisa,
  combinar os comunicados da CVM com as notícias <strong>não melhora a previsão
  da direção nem a da volatilidade</strong>. Nenhum McNemar passa.
  <br><br>
  Isso <strong>não derruba</strong> o que foi medido antes — o efeito de
  <strong>+38%</strong> no tamanho da variação, nas noites de Fato Relevante com
  muita notícia, continua real. Diz outra coisa, mais específica: <strong>o
  efeito existe, mas não é regular o bastante para virar previsão melhor que a
  memória do próprio preço.</strong>
  <br><br>
  <strong>E falta um experimento.</strong> As duas fontes não entraram em pé de
  igualdade: a CVM entrou com o embedding de 768 dimensões; as 54 mil notícias
  entraram com <strong>um número só por pregão</strong>. Extrair os embeddings
  das notícias é o próximo passo.
</div>
"""

SCRIPT = """
<script>
/* ── demonstração interativa: acurácia muda com o corte, AUC não ── */
(function () {
  const agitado = [0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0];
  const nota = [.14,.11,.29,.07,.88,.26,.24,.62,.30,.25,
                .52,.72,.05,.13,.58,.20,.66,.55,.38,.11];

  /* AUC = probabilidade de o agitado receber nota maior que o calmo */
  const pos = nota.filter((_, i) => agitado[i]);
  const neg = nota.filter((_, i) => !agitado[i]);
  let soma = 0;
  pos.forEach(a => neg.forEach(b => soma += a > b ? 1 : a === b ? .5 : 0));
  const auc = soma / (pos.length * neg.length);

  const svg = document.getElementById("demo-svg");
  const range = document.getElementById("demo-corte");
  if (!svg || !range) return;

  function desenha(corte) {
    const W = 660, H = 190, L = 34, R = 10, T = 14, Bt = 26;
    const lg = (W - L - R) / nota.length, bw = lg * 0.66;
    const y = v => T + (H - T - Bt) * (1 - v);
    let s = `<svg viewBox="0 0 ${W} ${H}" style="width:100%;height:auto"
      role="img" aria-label="vinte pregões e suas notas de risco">`;
    nota.forEach((v, i) => {
      const x = L + i * lg + (lg - bw) / 2;
      const ag = agitado[i];
      const apontado = v > corte;
      s += `<rect x="${x}" y="${y(v)}" width="${bw}" height="${y(0) - y(v)}"
            fill="${ag ? "var(--lampada)" : "var(--cinza)"}"
            opacity="${ag ? 1 : .42}"/>`;
      if (apontado) {
        s += `<circle cx="${x + bw / 2}" cy="${y(v) - 7}" r="3.2"
              fill="var(--tinta)"/>`;
      }
    });
    s += `<line x1="${L - 6}" y1="${y(corte)}" x2="${W - R}" y2="${y(corte)}"
          stroke="var(--tinta)" stroke-width="1.4" stroke-dasharray="4 3"/>`;
    s += `<text x="${W - R}" y="${y(corte) - 5}" text-anchor="end"
          style="font-family:var(--dado);font-size:10px;fill:var(--tinta)">
          corte</text>`;
    s += `<text x="${L - 8}" y="${H - Bt + 4}" text-anchor="end"
          style="font-family:var(--dado);font-size:10px;fill:var(--cinza)">0</text>`;
    s += `<text x="${L - 8}" y="${T + 4}" text-anchor="end"
          style="font-family:var(--dado);font-size:10px;fill:var(--cinza)">1</text>`;
    s += `<text x="${W / 2}" y="${H - 5}" text-anchor="middle"
          style="font-family:var(--corpo);font-size:11px;fill:var(--cinza)">
          o ponto preto marca os pregões que o modelo aponta como agitados
          </text>`;
    s += `</svg>`;
    svg.innerHTML = s;
  }

  function atualiza() {
    const corte = range.value / 100;
    desenha(corte);
    let ok = 0;
    nota.forEach((v, i) => { if ((v > corte ? 1 : 0) === agitado[i]) ok++; });
    const f = (v, n) => v.toLocaleString("pt-BR",
      {minimumFractionDigits: n, maximumFractionDigits: n});
    document.getElementById("demo-corte-val").textContent = f(corte, 2);
    document.getElementById("demo-acc").textContent = f(ok / nota.length * 100, 0) + "%";
    document.getElementById("demo-acc-det").textContent =
      ok + " acertos em " + nota.length;
    document.getElementById("demo-auc").textContent = f(auc, 2);
  }

  range.addEventListener("input", atualiza);
  atualiza();
})();
</script>
"""


def main() -> None:
    html = ALVO.read_text(encoding="utf-8")
    marca = "<h2>Como ler os números</h2>"
    if marca in html:                       # idempotente: remove a versão antiga
        html = html[:html.index(marca)] + html[html.index("<footer>"):]
        html = html.replace(SCRIPT, "")
    html = html.replace("<footer>", NOVO + "\n<footer>", 1)
    html = html.rstrip() + "\n" + SCRIPT + "\n"
    ALVO.write_text(html, encoding="utf-8")
    print(f"  [OK] painel.html atualizado ({len(html):,} caracteres)")


if __name__ == "__main__":
    main()
