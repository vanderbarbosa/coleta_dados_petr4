// Sons sintetizados via Web Audio API (sem arquivos externos).
// Toca apenas após interação do usuário (clique em "Avaliar"), respeitando os navegadores.

let ctx = null;
let mudo = false;

function ac() {
  if (!ctx) {
    const AC = window.AudioContext || window.webkitAudioContext;
    if (AC) ctx = new AC();
  }
  if (ctx && ctx.state === "suspended") ctx.resume();
  return ctx;
}

function tom(freq, dur, tipo = "sine", vol = 0.15, atraso = 0) {
  if (mudo) return;
  const c = ac();
  if (!c) return;
  const t = c.currentTime + atraso;
  const o = c.createOscillator();
  const g = c.createGain();
  o.type = tipo;
  o.frequency.setValueAtTime(freq, t);
  g.gain.setValueAtTime(0.0001, t);
  g.gain.exponentialRampToValueAtTime(vol, t + 0.012);
  g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
  o.connect(g);
  g.connect(c.destination);
  o.start(t);
  o.stop(t + dur + 0.02);
}

export const som = {
  setMudo(v) { mudo = v; },
  isMudo() { return mudo; },
  // Engate da engrenagem ao iniciar uma etapa (zumbido mecânico curto).
  engrenar() { tom(120, 0.16, "sawtooth", 0.05); tom(180, 0.10, "square", 0.03, 0.02); },
  // Confirmação de etapa concluída (nota ascendente conforme avança).
  ding(i = 0) { tom(523.25 * Math.pow(2, (i * 2) / 12), 0.22, "sine", 0.16); },
  // Fanfarra do veredito: sobe (alta), desce (baixa) ou nota única (indefinido).
  veredito(dir) {
    if (dir === "alta") [392, 523, 659, 784].forEach((f, i) => tom(f, 0.26, "triangle", 0.18, i * 0.11));
    else if (dir === "baixa") [659, 523, 392, 294].forEach((f, i) => tom(f, 0.28, "triangle", 0.18, i * 0.11));
    else tom(440, 0.35, "sine", 0.14);
  },
};
