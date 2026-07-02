# -*- coding: utf-8 -*-
# ==============================================================================
#   avaliar_regras.py — Mede a ACURÁCIA da leitura econômica setorial (regras)
#   Dissertação PETR4 | Vanderlei Barbosa da Silva
#
#   Roda um conjunto ROTULADO de manchetes (direção esperada, definida por
#   raciocínio econômico) contra a mesma lógica usada pelo backend
#   (regras_setoriais.py). Serve para (a) medir objetivamente a qualidade da
#   camada interpretável, (b) evitar 'viciar' em exemplos avulsos — cada mudança
#   nas regras é reavaliada aqui — e (c) apresentar um número de validação à banca.
#
#   Uso:  python site/backend/avaliar_regras.py
#   (Não requer FinBERT/torch — a polaridade vem de um léxico simples.)
# ==============================================================================

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))   # regras_setoriais
sys.path.insert(0, str(RAIZ / "src" / "comum"))            # taxonomia

import regras_setoriais as rs


def veredito(frase: str) -> str:
    """Replica o veredito final do backend (endpoint /api/prever, passo-síntese),
    usando a polaridade do léxico no lugar do FinBERT."""
    low = frase.lower()
    cat_id, _rot, _qtd = rs.detectar_categoria(low)
    if cat_id is None:
        return "sem_influencia"
    pol = rs.polaridade_lexico(low)
    dir_set, _just, _ev = rs.analisar_direcao(low, pol, cat_id)
    if dir_set in ("alta", "baixa"):
        return dir_set
    return "indefinida"


# ── Conjunto rotulado (frase → direção esperada) ──────────────────────────────
# Rótulos: alta | baixa | indefinida | sem_influencia
CASOS = [
    # Empresa — positivo → alta
    ("Petrobras anuncia dividendos recordes e lucro acima do esperado", "alta"),
    ("Petrobras aprova pagamento de JCP extraordinário aos acionistas", "alta"),
    ("Petrobras bate recorde de produção no pré-sal", "alta"),
    # Empresa — cessação de valor ao acionista → baixa
    ("Petrobras deixará de pagar dividendos neste trimestre", "baixa"),
    ("Conselho da Petrobras aprova corte de dividendos", "baixa"),
    ("Petrobras suspende o pagamento de proventos", "baixa"),
    ("Petrobras reduz a distribuição de JCP", "baixa"),
    ("Petrobras registra prejuízo bilionário no trimestre", "baixa"),
    ("Dividendos da Petrobras vêm abaixo do esperado", "baixa"),
    # Empresa/governança — negativo → baixa
    ("Petrobras demite diretores por suspeita de corrupção", "baixa"),
    ("Polícia Federal investiga fraude na Petrobras", "baixa"),
    ("CPI investiga contratos da Petrobras", "baixa"),
    ("Ex-diretor da Petrobras é condenado por propina", "baixa"),
    ("Governo demite o presidente da Petrobras", "baixa"),
    ("Acidente em plataforma da Petrobras interrompe a produção", "baixa"),
    ("Petrobras enfrenta greve de petroleiros", "baixa"),
    # Governança/jurídico — resolução → alta
    ("Justiça arquiva a investigação contra a Petrobras", "alta"),
    ("Fim da greve dos petroleiros após acordo com a Petrobras", "alta"),
    # Oferta — choque (disrupção/corte) → alta (favorece a produtora)
    ("Preço do petróleo Brent dispara com a guerra Israel", "alta"),
    ("Fechamento do Estreito de Ormuz ameaça a navegação", "alta"),
    ("Ataque Houthi a navios eleva o preço do petróleo", "alta"),
    ("OPEP anuncia corte de produção de petróleo", "alta"),
    # Oferta — distensão/aumento → baixa
    ("Cessar-fogo no conflito Oriente Médio derruba o petróleo", "baixa"),
    ("OPEP decide aumento de produção de petróleo", "baixa"),
    # Macro → indefinida (efeito ambíguo)
    ("Transição energética ameaça a demanda por combustível fóssil", "indefinida"),
    ("Aumento dos juros pressiona o mercado de energia", "indefinida"),
    # Irrelevante → sem influência
    ("Seleção brasileira vence amistoso de futebol", "sem_influencia"),
    ("Nova novela estreia na televisão nesta segunda", "sem_influencia"),

    # ── Casos DIFÍCEIS / adversariais (sondam limites reais; podem falhar) ────
    ("Petrobras estuda deixar de distribuir dividendos extraordinários", "baixa"),
    ("Analistas elevam a recomendação da PETR4 para compra", "alta"),
    ("Acionistas não receberão dividendos da Petrobras este ano", "baixa"),
    ("Petrobras pode ter lucro menor que o esperado", "baixa"),
    ("Dólar em alta encarece a dívida da Petrobras", "baixa"),
]


def main():
    acertos, erros = 0, []
    for frase, esperado in CASOS:
        obtido = veredito(frase)
        ok = obtido == esperado
        acertos += ok
        marca = "OK " if ok else "XX "
        print(f"  {marca}esperado={esperado:14} obtido={obtido:14} | {frase}")
        if not ok:
            erros.append((frase, esperado, obtido))
    n = len(CASOS)
    print("\n" + "=" * 70)
    print(f"Acuracia da leitura setorial: {acertos}/{n} = {100*acertos/n:.1f}%")
    if erros:
        print(f"\n{len(erros)} erro(s) — casos a investigar (limites conhecidos das regras):")
        for f, e, o in erros:
            print(f"  - '{f}'  (esperado {e}, obtido {o})")


if __name__ == "__main__":
    main()
