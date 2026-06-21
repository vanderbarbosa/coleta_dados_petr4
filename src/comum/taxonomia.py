# -*- coding: utf-8 -*-
# ==============================================================================
#   taxonomia.py — Fonte ÚNICA de verdade dos termos de busca e filtragem
#   Dissertação PETR4 | Vanderlei Barbosa da Silva
#
#   Centraliza a taxonomia completa (7 categorias, 152 termos) e os critérios de
#   filtragem (estrita e leve). É importado tanto pelo coletor (02b) quanto pelos
#   geradores de documentação, garantindo que NENHUM termo fique de fora das
#   tabelas — completude total exigida para a dissertação.
# ==============================================================================

# ── Taxonomia de 7 categorias temáticas (152 termos) ──────────────────────────
TERMOS_POR_CATEGORIA = {

    # CAT-1: EMPRESA E ATIVO (21 termos) — notícias corporativas diretas
    "CAT1_Empresa": [
        "Petrobras", "PETR4", "PETR3", "Petróleo Brasileiro SA",
        "petróleo brasileiro S.A.", "pré-sal", "pre-sal", "Petrobras dividendos",
        "Petrobras resultado", "Petrobras lucro", "Petrobras prejuízo",
        "Petrobras produção", "Petrobras exploração", "Petrobras refino",
        "Petrobras dívida", "Petrobras privatização", "Petrobras contrato",
        "campo de Búzios", "campo de Tupi", "bacia de Santos", "bacia de Campos",
    ],

    # CAT-2: MERCADO DE PETRÓLEO (20 termos) — fundamentos globais
    "CAT2_Mercado_Petroleo": [
        "preço do petróleo", "cotação do petróleo", "barril de petróleo",
        "petróleo Brent", "petróleo WTI", "OPEP", "OPEC", "OPEP+",
        "corte de produção petróleo", "aumento de produção petróleo",
        "demanda por petróleo", "oferta de petróleo", "estoques de petróleo EUA",
        "EIA estoques petróleo", "petróleo mercado", "commodity petróleo",
        "crise do petróleo", "choque do petróleo", "petróleo bruto",
        "mercado de energia",
    ],

    # CAT-3: GEOPOLÍTICA E CONFLITOS (27 termos)
    "CAT3_Geopolitica": [
        "guerra Oriente Médio", "conflito Oriente Médio", "guerra Israel",
        "guerra Hamas", "guerra Irã", "tensão Irã", "sanção Irã", "guerra Iraque",
        "conflito Iraque", "guerra Líbia", "conflito Líbia", "guerra Yemen",
        "conflito Houthi", "ataque Houthi", "guerra Rússia Ucrânia",
        "invasão Ucrânia", "conflito Rússia", "sanção Rússia petróleo",
        "guerra Síria petróleo", "conflito Venezuela petróleo",
        "tensão Golfo Pérsico", "Estreito de Ormuz", "cessar-fogo Oriente Médio",
        "acordo de paz Oriente Médio", "acordo paz Rússia Ucrânia",
        "Arábia Saudita petróleo", "crise geopolítica petróleo",
    ],

    # CAT-4: OFERTA, INFRAESTRUTURA E PRODUÇÃO (20 termos)
    "CAT4_Infraestrutura": [
        "refinaria petróleo", "oleoduto", "gasoduto", "plataforma petróleo",
        "plataforma offshore", "terminal de petróleo", "duto petróleo",
        "interrupção refinaria", "acidente refinaria", "ataque refinaria",
        "greve petroleiros", "paralisação petróleo", "shale oil", "fracking",
        "petróleo de xisto", "capacidade de refino", "produção petróleo OPEP",
        "produção petróleo Estados Unidos", "produção petróleo Rússia",
        "produção petróleo Brasil",
    ],

    # CAT-5: ACORDOS, SANÇÕES E NAVEGAÇÃO (20 termos)
    "CAT5_Sancoes_Navegacao": [
        "embargo petróleo", "sanção petróleo", "bloqueio petróleo",
        "bloqueio naval", "proibição navio petróleo", "navio petroleiro",
        "teto de preço petróleo", "price cap petróleo", "apreensão navio petróleo",
        "ataque navio petroleiro", "Mar Vermelho petróleo", "Canal de Suez petróleo",
        "Bab-el-Mandeb", "acordo nuclear Irã", "acordo petróleo", "acordo OPEP",
        "tratado energia", "acordo clima petróleo", "transição energética petróleo",
        "COP petróleo",
    ],

    # CAT-6: LIDERANÇA, GOVERNANÇA E POLÍTICA ENERGÉTICA (24 termos)
    "CAT6_Governanca": [
        "CEO Petrobras", "presidente Petrobras", "demissão Petrobras",
        "troca presidente Petrobras", "indicação Petrobras", "conselho Petrobras",
        "interventor Petrobras", "ministro de minas e energia",
        "ministério de minas e energia Brasil", "política energética Brasil",
        "eleição Venezuela petróleo", "eleição Arábia Saudita petróleo",
        "eleição Irã petróleo", "secretário energia EUA",
        "príncipe Mohammed bin Salman", "MBS Aramco", "Aramco", "Saudi Aramco",
        "CEO Aramco", "PDVSA", "Nicolás Maduro petróleo", "Lula Petrobras",
        "governo Petrobras", "intervenção estatal Petrobras",
    ],

    # CAT-7: MACROECONOMIA, CÂMBIO E ENERGIA ALTERNATIVA (20 termos)
    "CAT7_Macro_Energia": [
        "dólar petróleo", "câmbio petróleo", "real dólar", "Federal Reserve petróleo",
        "juros EUA petróleo", "recessão demanda petróleo", "crescimento China petróleo",
        "demanda China petróleo", "PIB China petróleo", "inflação petróleo",
        "energia renovável petróleo", "veículo elétrico petróleo",
        "hidrogênio verde petróleo", "descarbonização petróleo", "ESG Petrobras",
        "combustível fóssil", "energia limpa", "transição energética",
        "gás natural preço", "GNL",
    ],
}

# Rótulos legíveis das categorias (para tabelas e figuras)
ROTULOS_CATEGORIA = {
    "CAT1_Empresa":           "CAT1 — Empresa e Ativo",
    "CAT2_Mercado_Petroleo":  "CAT2 — Mercado de Petróleo",
    "CAT3_Geopolitica":       "CAT3 — Geopolítica e Conflitos",
    "CAT4_Infraestrutura":    "CAT4 — Oferta, Infraestrutura e Produção",
    "CAT5_Sancoes_Navegacao": "CAT5 — Acordos, Sanções e Navegação",
    "CAT6_Governanca":        "CAT6 — Liderança, Governança e Política Energética",
    "CAT7_Macro_Energia":     "CAT7 — Macroeconomia, Câmbio e Energia Alternativa",
}

# Âncora teórica de cada categoria (justificativa na literatura)
ANCORA_TEORICA = {
    "CAT1_Empresa":           "Tetlock et al. (2008)",
    "CAT2_Mercado_Petroleo":  "Kilian (2009)",
    "CAT3_Geopolitica":       "Hamilton (1983); Caldara e Iacoviello (2022)",
    "CAT4_Infraestrutura":    "Hamilton (1983) — choques de oferta",
    "CAT5_Sancoes_Navegacao": "Kilian (2009) — fluxo físico e prêmio de risco",
    "CAT6_Governanca":        "Estudos de evento (event study)",
    "CAT7_Macro_Energia":     "Zhang et al. (2008); Kilian e Murphy (2014)",
}

# ── Filtragem ESTRITA (testada e descartada) ──────────────────────────────────
# Exigia que título ou resumo contivesse explicitamente um destes termos.
TERMOS_RELEVANCIA_ESTRITA = [
    "petrobras", "petr4", "petr3", "petroleira", "petróleo", "petroleo",
    "brent", "wti", "opep", "barril", "combustível", "combustivel", "refinaria",
]

# ── Filtragem LEVE (adotada) — limpeza de qualidade ───────────────────────────
LIMPEZA_LEVE = {
    "min_titulo_chars": 15,
    "marcadores_invalidos": ["[removed]", "[removida]", "(sem título)", "sem titulo"],
}


def total_termos() -> int:
    """Número total de termos na taxonomia (deve ser 152)."""
    return sum(len(v) for v in TERMOS_POR_CATEGORIA.values())
