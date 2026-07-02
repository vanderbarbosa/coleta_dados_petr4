# -*- coding: utf-8 -*-
# ==============================================================================
#   regras_setoriais.py — Leitura ECONÔMICA SETORIAL da PETR4 (fonte única)
#   Dissertação PETR4 | Vanderlei Barbosa da Silva
#
#   Camada interpretável (baseada em conhecimento, NÃO treinada) que classifica a
#   direção provável da PETR4 a partir do TIPO de evento × MECANISMO de transmissão,
#   fundamentada em Kilian (2009) e Hamilton (1983). É importada pelo backend
#   (app.py) e pelo script de avaliação (avaliar_regras.py) — garantindo uma única
#   fonte de verdade. O motor equivalente no navegador é `frontend/src/previsao_local.js`
#   (mantido espelhado).
#
#   Princípio central: distinguir o efeito sobre o MERCADO de petróleo do efeito
#   sobre o ATIVO (Petrobras é produtora), e a SEMÂNTICA do evento — o fim de uma
#   coisa ruim (resolução) favorece; o fim de uma coisa boa (cessação de valor)
#   pressiona — corrigindo a ambiguidade de polaridade dos modelos de linguagem.
# ==============================================================================

import unicodedata

try:
    import taxonomia as tx
    ROTULOS = tx.ROTULOS_CATEGORIA
    TERMOS = tx.TERMOS_POR_CATEGORIA
except Exception:
    ROTULOS, TERMOS = {}, {}


def sem_acento(s: str) -> str:
    """Remove acentos (NFKD) para casar termos de forma robusta
    ('petrobrás' passa a casar com 'Petrobras')."""
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


# ── Detecção de categoria pela taxonomia completa (152 termos) ────────────────
def detectar_categoria(texto_low: str):
    """Retorna (categoria_id, rotulo, qtd_termos_casados) ou (None, None, 0)."""
    alvo = sem_acento(texto_low)
    melhor, melhor_qtd = None, 0
    for cat, termos in TERMOS.items():
        qtd = sum(1 for t in termos if sem_acento(t.lower()) in alvo)
        if qtd > melhor_qtd:
            melhor, melhor_qtd = cat, qtd
    if melhor is None:
        return None, None, 0
    return melhor, ROTULOS.get(melhor, melhor), melhor_qtd


# ── Léxicos de evento (comparados sobre o texto SEM acento) ───────────────────
# RESOLUÇÃO = fim de uma coisa RUIM (favorece); DISRUPÇÃO = coisa ruim acontecendo.
RESOLUCAO = [
    "acordo", "fim da greve", "greve termina", "termina a greve", "fim da paralis",
    "retomada", "retoma", "normaliz", "volta ao normal", "cessar-fogo", "cessar fogo",
    "acordo de paz", "tregua", "reabertura", "reabre", "fim do bloqueio", "fim do embargo",
    "fim das sanc", "alivio", "encerr", "resolv", "supera", "aprova", "conclui", "avanc",
    # resolução no plano jurídico/governança:
    "absolv", "arquiva", "arquivamento", "inocent", "sem irregularidad",
]
DISRUPCAO = [
    "greve", "paralis", "bloqueio", "ataque", "guerra", "sanc", "embargo", "interrup",
    "acidente", "fechamento", "fecha", "invasao", "conflito", "explos", "sabotagem",
    "apreens", "demiss", "demite", "intervenc", "rompe", "crise", "tensao", "ameac",
    "queda", "prejuizo", "rombo", "vazamento de oleo", "derramamento",
    # alerta de resultado (profit warning) — inequivocamente baixista:
    "lucro menor", "lucro abaixo", "queda do lucro", "queda no lucro", "lucro cai",
    "lucro caiu", "lucro despenca", "lucro frustra",
]
# GOVERNANÇA/JURÍDICO NEGATIVO (nível empresa → pressiona a ação):
GOVERNANCA_NEG = [
    "corrupc", "fraude", "investigac", "investiga", "delacao", "cpi",
    "operacao policial", "policia federal", "escandalo", "propina",
    "lavagem de dinheiro", "denuncia", "indiciad", "indiciamento", " reu ",
    "condenac", "condenad", "busca e apreensao", "irregularidad", "desvio de",
    "superfaturamento", "cartel", "improbidade", "quebra de sigilo",
]

# CESSAÇÃO DE VALOR AO ACIONISTA (fim de uma coisa BOA → pressiona a ação),
# ainda que o texto contenha palavras usualmente positivas ('dividendos', 'lucro').
CESSA_MARCADORES = [
    "deixar de", "deixara de", "deixou de", "deixa de", "suspend", "corte de", "corta ",
    "cortar", "reduz", "reduc", "cancela", "cancelamento", "fim do", "fim dos", "fim da",
    "nao pag", "nao rece", "nao have", "nao distribu", "sem distribu", "abaixo do esperado",
    "revisa para baixo", "revisao para baixo", "menor que o esperado", "frustr",
]
VALOR_ACIONISTA = [
    "dividendo", "provento", "jcp", "juros sobre capital", "recompra",
    "distribuicao de resultado", "distribuir resultado", "payout",
]

CATS_EMPRESA = {"CAT1_Empresa", "CAT6_Governanca"}
CATS_OFERTA_MERC = {"CAT2_Mercado_Petroleo", "CAT3_Geopolitica", "CAT5_Sancoes_Navegacao"}


def _tem(t, lista):
    return any(sem_acento(k) in t for k in lista)


def cessacao_valor(low_n: str) -> bool:
    if "prejuizo" in low_n or "rombo" in low_n:
        return True
    return _tem(low_n, VALOR_ACIONISTA) and _tem(low_n, CESSA_MARCADORES)


def governanca_negativa(low_n: str) -> bool:
    return _tem(low_n, GOVERNANCA_NEG)


def tipo_evento(texto_low: str) -> str:
    t = sem_acento(texto_low)
    if _tem(t, RESOLUCAO):
        return "resolucao"
    if _tem(t, DISRUPCAO):
        return "disrupcao"
    return "neutro"


def mecanismo(cat_id, texto_low: str) -> str:
    if cat_id in CATS_EMPRESA:
        return "empresa"
    if cat_id in CATS_OFERTA_MERC:
        return "oferta"
    if cat_id == "CAT4_Infraestrutura":
        t = sem_acento(texto_low)
        return "empresa" if ("petrobras" in t or "brasil" in t) else "oferta"
    return "macro"  # CAT7


# ── Léxico simples de polaridade (fallback quando não há FinBERT) ─────────────
POS = ["lucro", "alta", "sobe", "subiu", "ganho", "recorde", "dividendo", "acordo", "aprova",
       "cresce", "crescimento", "valoriza", "avanc", "positivo", "melhora", "supera",
       "otimismo", "recuperac", "expansao", "reforca", "eleva"]
NEG = ["queda", "cai", "caiu", "prejuizo", "perda", "greve", "crise", "demiss", "rombo",
       "despenca", "negativo", "piora", "ataque", "guerra", "sanc", "embargo", "bloqueio",
       "acidente", "conflito", "tensao", "recessao", "colapso", "risco", "temor", "corrupc", "fraude"]


def polaridade_lexico(texto_low: str) -> int:
    t = sem_acento(texto_low)
    p = sum(1 for w in POS if sem_acento(w) in t)
    n = sum(1 for w in NEG if sem_acento(w) in t)
    return 1 if p > n else (-1 if n > p else 0)


def analisar_direcao(texto_low: str, polaridade: int, cat_id):
    """Direção provável da PETR4. Retorna (direcao, justificativa, tipo_evento)."""
    low_n = sem_acento(texto_low)
    ev = tipo_evento(texto_low)
    mec = mecanismo(cat_id, texto_low)

    if mec == "empresa":
        # 1) Cessação de valor ao acionista (corte de proventos / prejuízo) → baixa.
        if cessacao_valor(low_n):
            return "baixa", ("Cessação ou redução de proventos ao acionista (corte, suspensão ou "
                             "fim de dividendos/JCP/recompra) — ou prejuízo — reduz o retorno "
                             "esperado e tende a PRESSIONAR a PETR4, ainda que o texto mencione "
                             "termos usualmente positivos como 'dividendos' ou 'lucro'."), "disrupcao"
        # 2) Governança/jurídico negativo (corrupção, fraude, investigação) → baixa,
        #    salvo quando o texto já indica resolução (absolvição, arquivamento).
        if governanca_negativa(low_n) and ev != "resolucao":
            return "baixa", ("Evento negativo de governança ou jurídico (corrupção, fraude, "
                             "investigação, operação policial, denúncia) eleva o risco percebido "
                             "e o prêmio de risco da estatal, tendendo a PRESSIONAR a PETR4."), "disrupcao"
        if ev == "resolucao":
            return "alta", ("Resolução de evento operacional, corporativo ou jurídico (acordo, fim de "
                            "paralisação, normalização, arquivamento/absolvição) tende a FAVORECER a "
                            "PETR4, ainda que o tom textual contenha termos negativos."), ev
        if ev == "disrupcao":
            return "baixa", ("Disrupção operacional, de governança ou corporativa (greve, "
                             "intervenção, acidente, demissão) tende a PRESSIONAR a PETR4."), ev
        if polaridade > 0:
            return "alta", "Notícia corporativa de tom positivo tende a favorecer a PETR4.", ev
        if polaridade < 0:
            return "baixa", "Notícia corporativa de tom negativo tende a pressionar a PETR4.", ev
        return "neutra", "Notícia corporativa de tom neutro, sem direção clara.", ev

    if mec == "oferta":
        # Choques explícitos na PRODUÇÃO/oferta da commodity (Kilian, 2009):
        # corte de oferta → preço sobe → favorece a produtora; aumento → o inverso.
        corte_oferta = _tem(low_n, ["corte de produc", "corte na produc", "corta a produc",
                                    "reduz a produc", "reducao da produc", "reduz a oferta",
                                    "reducao da oferta", "corta a oferta"])
        aumento_oferta = _tem(low_n, ["aumento da produc", "aumenta a produc", "aumentar a produc",
                                      "eleva a produc", "aumento de produc", "eleva a oferta",
                                      "aumento da oferta", "aumenta a oferta"])
        if ev == "disrupcao" or corte_oferta:
            return "alta", ("Choque de OFERTA (conflito, bloqueio, sanção, ataque, interrupção ou "
                            "corte de produção) tende a ELEVAR o preço do petróleo; como a Petrobras "
                            "é produtora da commodity, o efeito sobre a PETR4 costuma ser FAVORÁVEL — "
                            "ainda que o tom seja negativo para o mercado (Kilian, 2009; Hamilton, 1983)."), "disrupcao"
        if ev == "resolucao" or aumento_oferta:
            return "baixa", ("Distensão ou aumento da oferta (cessar-fogo, acordo, elevação da "
                             "produção) tende a REDUZIR o preço do petróleo, DESFAVORÁVEL à "
                             "Petrobras."), "resolucao"
        return "neutra", "Evento de mercado de petróleo de tom neutro, sem direção clara.", ev

    return "contextual", ("Fator macroeconômico (câmbio, juros, demanda, transição energética) de "
                          "efeito ambíguo, dependente do contexto."), ev
