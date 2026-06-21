# -*- coding: utf-8 -*-
# ==============================================================================
#
#   DISSERTAÇÃO : O Impacto do Sentimento de Notícias Financeiras na Previsão
#                 de Direção e Volatilidade do Ativo PETR4
#   Autor       : Vanderlei Barbosa da Silva
#   Orientador  : Prof. Dr. Julio Cesar Nievola — PUCPR
#   Script      : 02b — Coleta de Notícias via WordPress REST API (timestamp exato)
#   Versão      : 2.0 (com taxonomia de 7 categorias)
#
# ==============================================================================
#
#   POR QUE ESTE SCRIPT EXISTE
#   ──────────────────────────
#   A banca (Prof. Emerson) exigiu que cada notícia tenha a HORA EXATA de
#   publicação (timestamp). Sem ela, não é possível garantir o alinhamento
#   temporal Lead-Lag — uma notícia publicada às 20h (mercado fechado) só pode
#   impactar o pregão do dia seguinte. A biblioteca GoogleNews usada antes
#   MASCARAVA a hora, forçando datas estocásticas (aleatórias) e invalidando
#   a prova de causalidade com o GARCH(1,1).
#
#   A SOLUÇÃO (rota Cardoso & Nakane, 2024 — coleta direta do portal)
#   ─────────────────────────────────────────────────────────────────
#   Os grandes portais financeiros brasileiros rodam em WordPress, que expõe
#   uma API REST pública e gratuita: /wp-json/wp/v2/posts. Ela devolve JSON
#   ESTRUTURADO com título, resumo, link e — crucialmente — o campo `date`
#   no horário de Brasília (e `date_gmt` em UTC). Isso entrega o timestamp
#   exato sem Selenium e sem raspar HTML frágil.
#
#   TAXONOMIA DE 7 CATEGORIAS (preservada do Script 02 multi-fonte)
#   ───────────────────────────────────────────────────────────────
#   Cada notícia é capturada por um termo de busca pertencente a uma das 7
#   categorias temáticas (Empresa, Mercado de Petróleo, Geopolítica,
#   Infraestrutura, Sanções/Navegação, Governança, Macro/Energia). A categoria
#   é GRAVADA no CSV (coluna `categoria`), permitindo a ANÁLISE DE ABLAÇÃO na
#   modelagem: remover uma categoria por vez e medir o impacto na performance —
#   respondendo "qual tipo de notícia é mais informativo para prever a
#   volatilidade do PETR4?". Justificativa acadêmica completa de cada categoria
#   no cabeçalho do Script 02 (02_coleta_noticias_petr4.py, Seção 2).
#
#   ESTRATÉGIA DE COLETA HÍBRIDA (eficiência + completude)
#   ───────────────────────────────────────────────────────
#   Testado em 18/06/2026: a paginação profunda da API (offset > 10.000) fica
#   lenta/instável. Por isso, para cada par (termo, portal):
#     • Se o termo retorna POUCAS páginas (<= LIMITE_PAGINAS_FULLRANGE):
#       pagina o período inteiro de uma vez — barato e completo. É o caso da
#       maioria dos termos da taxonomia (raros/médios).
#     • Se retorna MUITAS páginas (alto volume, ex.: "Petrobras", "OPEP"):
#       coleta por JANELA MENSAL — cada mês é pequeno e paginável sem atingir
#       o teto de offset, garantindo a cobertura completa de 2018-2025.
#
#   SAÍDA
#   ─────
#   CSV consumível pelo Script 03 (que normaliza o schema automaticamente).
#   Colunas: data_publicacao, data_gmt, ativo, categoria, fonte_coleta,
#            termo_busca, titulo, resumo, url, dominio, idioma, hash_titulo
#
#   COMO RODAR
#   ──────────
#   Teste rápido (1 mês, 2 portais, 2 categorias): MODO_TESTE = True
#   Coleta completa (2018-2025, 5 portais, 7 categorias): MODO_TESTE = False
#   Execução: python 02b_coleta_noticias_wordpress_petr4.py
#
# ==============================================================================

import csv
import hashlib
import html as _html
import logging
import random
import re
import time
from datetime import datetime
from pathlib import Path

import requests
import urllib3
from dateutil.relativedelta import relativedelta

# O ambiente local pode ter interceptação SSL (proxy). Em Colab não é necessário.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# ==============================================================================
# BLOCO 1 — CONFIGURAÇÕES
# ==============================================================================

# ── Modo de execução ──────────────────────────────────────────────────────────
# True  = teste rápido: 1 mês, 2 primeiros portais, 2 primeiras categorias
# False = coleta completa: todo o período, todos os portais, todas as categorias
MODO_TESTE = False

# ── Período de análise ────────────────────────────────────────────────────────
DATA_INICIO = datetime(2018, 1, 1)
DATA_FIM    = datetime(2025, 12, 31)
TESTE_INICIO = datetime(2019, 6, 1)
TESTE_FIM    = datetime(2019, 6, 30)

# ── Portais (endpoint WordPress REST API /wp-json/wp/v2/posts) ─────────────────
# Validados em 18/06/2026. A chave é o rótulo gravado em `dominio`/`fonte_coleta`.
PORTAIS = {
    "InfoMoney"    : "https://www.infomoney.com.br/wp-json/wp/v2/posts",
    "Exame"        : "https://exame.com/wp-json/wp/v2/posts",
    "MoneyTimes"   : "https://www.moneytimes.com.br/wp-json/wp/v2/posts",
    "Petronoticias": "https://petronoticias.com.br/wp-json/wp/v2/posts",
    "Poder360"     : "https://www.poder360.com.br/wp-json/wp/v2/posts",
}

# ── Parâmetros de requisição ──────────────────────────────────────────────────
PER_PAGE   = 100   # Máximo permitido pela API WP REST
PAUSA_S    = 0.8   # Pausa base entre requisições (jitter ±0.3s adicionado)
TIMEOUT_S  = 45    # Timeout generoso (páginas profundas são lentas no servidor)
MAX_RETRY  = 3     # Tentativas por requisição antes de desistir
VERIFY_SSL = False # Local com proxy: False. Em Colab/produção: True.
USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
              "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36")

# Acima de quantas páginas (full-range) um termo passa a usar janela mensal.
LIMITE_PAGINAS_FULLRANGE = 50

# ── Filtro de relevância ──────────────────────────────────────────────────────
# Por padrão DESLIGADO: o próprio termo de busca (taxonomia) já é o sinal de
# relevância — exigir "Petrobras" no título descartaria justamente as notícias
# exógenas (geopolítica, OPEP, câmbio) que as categorias 2-7 existem para
# capturar. Mantido como opção para quem quiser um corpus mais restrito.
FILTRAR_RELEVANCIA = False
TERMOS_RELEVANCIA = ["petrobras", "petr4", "petr3", "petroleira", "petróleo",
                     "petroleo", "brent", "opep", "barril", "combustível"]

# ── Caminhos ──────────────────────────────────────────────────────────────────
# Raiz do projeto: este script vive em src/coleta/, então sobe 2 níveis.
try:
    _RAIZ = Path(__file__).resolve().parents[2]
except NameError:           # execução interativa (ex.: %run no Colab)
    _RAIZ = Path.cwd()
_NO_COLAB   = Path("/content/drive/MyDrive").exists()
PASTA_BASE  = Path("/content/drive/MyDrive/Mestrado_PETR4") if _NO_COLAB \
              else _RAIZ / "Mestrado_PETR4"
PASTA_BASE.mkdir(parents=True, exist_ok=True)

ARQUIVO_CSV = PASTA_BASE / ("base_textual_wordpress_TESTE.csv" if MODO_TESTE
                            else "base_textual_petr4_wordpress_2018_2025.csv")
ARQUIVO_LOG = PASTA_BASE / "coleta_wordpress.log"

CAMPOS_CSV = [
    "data_publicacao", "data_gmt", "ativo", "categoria", "fonte_coleta",
    "termo_busca", "titulo", "resumo", "url", "dominio", "idioma", "hash_titulo",
]

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler(ARQUIVO_LOG, encoding="utf-8"),
              logging.StreamHandler()],
)
log = logging.getLogger("coleta_wp")


# ==============================================================================
# BLOCO 2 — TAXONOMIA DE TERMOS DE BUSCA (7 CATEGORIAS)
# ==============================================================================
# Reproduzida fielmente do Script 02 (02_coleta_noticias_petr4.py, Bloco 4).
# A justificativa acadêmica de cada categoria (com referências: Tetlock 2008,
# Kilian 2009, Hamilton 1983, Caldara & Iacoviello 2022, Zhang 2008 etc.) está
# documentada no cabeçalho daquele script (Seção 2).
#
# A categoria de cada termo é gravada no CSV → permite análise de ablação.

TERMOS_POR_CATEGORIA = {

    # CAT-1: EMPRESA E ATIVO — notícias corporativas diretas (Tetlock et al., 2008)
    "CAT1_Empresa": [
        "Petrobras",
        "PETR4",
        "PETR3",
        "Petróleo Brasileiro SA",
        "petróleo brasileiro S.A.",
        "pré-sal",
        "pre-sal",
        "Petrobras dividendos",
        "Petrobras resultado",
        "Petrobras lucro",
        "Petrobras prejuízo",
        "Petrobras produção",
        "Petrobras exploração",
        "Petrobras refino",
        "Petrobras dívida",
        "Petrobras privatização",
        "Petrobras contrato",
        "campo de Búzios",
        "campo de Tupi",
        "bacia de Santos",
        "bacia de Campos",
    ],

    # CAT-2: MERCADO DE PETRÓLEO — fundamentos globais (Kilian, 2009)
    "CAT2_Mercado_Petroleo": [
        "preço do petróleo",
        "cotação do petróleo",
        "barril de petróleo",
        "petróleo Brent",
        "petróleo WTI",
        "OPEP",
        "OPEC",
        "OPEP+",
        "corte de produção petróleo",
        "aumento de produção petróleo",
        "demanda por petróleo",
        "oferta de petróleo",
        "estoques de petróleo EUA",
        "EIA estoques petróleo",
        "petróleo mercado",
        "commodity petróleo",
        "crise do petróleo",
        "choque do petróleo",
        "petróleo bruto",
        "mercado de energia",
    ],

    # CAT-3: GEOPOLÍTICA E CONFLITOS (Hamilton, 1983; Caldara & Iacoviello, 2022)
    "CAT3_Geopolitica": [
        "guerra Oriente Médio",
        "conflito Oriente Médio",
        "guerra Israel",
        "guerra Hamas",
        "guerra Irã",
        "tensão Irã",
        "sanção Irã",
        "guerra Iraque",
        "conflito Iraque",
        "guerra Líbia",
        "conflito Líbia",
        "guerra Yemen",
        "conflito Houthi",
        "ataque Houthi",
        "guerra Rússia Ucrânia",
        "invasão Ucrânia",
        "conflito Rússia",
        "sanção Rússia petróleo",
        "guerra Síria petróleo",
        "conflito Venezuela petróleo",
        "tensão Golfo Pérsico",
        "Estreito de Ormuz",
        "cessar-fogo Oriente Médio",
        "acordo de paz Oriente Médio",
        "acordo paz Rússia Ucrânia",
        "Arábia Saudita petróleo",
        "crise geopolítica petróleo",
    ],

    # CAT-4: OFERTA, INFRAESTRUTURA E PRODUÇÃO — choques de oferta (Aramco 2019)
    "CAT4_Infraestrutura": [
        "refinaria petróleo",
        "oleoduto",
        "gasoduto",
        "plataforma petróleo",
        "plataforma offshore",
        "terminal de petróleo",
        "duto petróleo",
        "interrupção refinaria",
        "acidente refinaria",
        "ataque refinaria",
        "greve petroleiros",
        "paralisação petróleo",
        "shale oil",
        "fracking",
        "petróleo de xisto",
        "capacidade de refino",
        "produção petróleo OPEP",
        "produção petróleo Estados Unidos",
        "produção petróleo Rússia",
        "produção petróleo Brasil",
    ],

    # CAT-5: ACORDOS, SANÇÕES E NAVEGAÇÃO — rotas e prêmio de risco (Ormuz/Suez)
    "CAT5_Sancoes_Navegacao": [
        "embargo petróleo",
        "sanção petróleo",
        "bloqueio petróleo",
        "bloqueio naval",
        "proibição navio petróleo",
        "navio petroleiro",
        "teto de preço petróleo",
        "price cap petróleo",
        "apreensão navio petróleo",
        "ataque navio petroleiro",
        "Mar Vermelho petróleo",
        "Canal de Suez petróleo",
        "Bab-el-Mandeb",
        "acordo nuclear Irã",
        "acordo petróleo",
        "acordo OPEP",
        "tratado energia",
        "acordo clima petróleo",
        "transição energética petróleo",
        "COP petróleo",
    ],

    # CAT-6: LIDERANÇA, GOVERNANÇA E POLÍTICA ENERGÉTICA — event study (CEO 2022)
    "CAT6_Governanca": [
        "CEO Petrobras",
        "presidente Petrobras",
        "demissão Petrobras",
        "troca presidente Petrobras",
        "indicação Petrobras",
        "conselho Petrobras",
        "interventor Petrobras",
        "ministro de minas e energia",
        "ministério de minas e energia Brasil",
        "política energética Brasil",
        "eleição Venezuela petróleo",
        "eleição Arábia Saudita petróleo",
        "eleição Irã petróleo",
        "secretário energia EUA",
        "príncipe Mohammed bin Salman",
        "MBS Aramco",
        "Aramco",
        "Saudi Aramco",
        "CEO Aramco",
        "PDVSA",
        "Nicolás Maduro petróleo",
        "Lula Petrobras",
        "governo Petrobras",
        "intervenção estatal Petrobras",
    ],

    # CAT-7: MACROECONOMIA, CÂMBIO E ENERGIA ALTERNATIVA (Zhang 2008; Kilian & Murphy 2014)
    "CAT7_Macro_Energia": [
        "dólar petróleo",
        "câmbio petróleo",
        "real dólar",
        "Federal Reserve petróleo",
        "juros EUA petróleo",
        "recessão demanda petróleo",
        "crescimento China petróleo",
        "demanda China petróleo",
        "PIB China petróleo",
        "inflação petróleo",
        "energia renovável petróleo",
        "veículo elétrico petróleo",
        "hidrogênio verde petróleo",
        "descarbonização petróleo",
        "ESG Petrobras",
        "combustível fóssil",
        "energia limpa",
        "transição energética",
        "gás natural preço",
        "GNL",
    ],
}


# ==============================================================================
# BLOCO 3 — FUNÇÕES AUXILIARES
# ==============================================================================

def limpar_html(texto: str) -> str:
    """Remove tags HTML e decodifica entidades (&aacute; → á)."""
    return re.sub(r"<[^>]+>", "", _html.unescape(texto or "")).strip()


def hash_titulo(titulo: str) -> str:
    """Hash SHA-256 do título normalizado (minúsculas, espaços colapsados)."""
    norm = re.sub(r"\s+", " ", titulo.lower()).strip()
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()


def e_relevante(titulo: str, resumo: str) -> bool:
    """True se título OU resumo contiver algum termo de relevância."""
    alvo = f"{titulo} {resumo}".lower()
    return any(t in alvo for t in TERMOS_RELEVANCIA)


def _pausa() -> None:
    """Pausa de cortesia com jitter aleatório (evita padrão periódico)."""
    time.sleep(max(0.2, PAUSA_S + random.uniform(-0.3, 0.3)))


def _get(endpoint: str, params: dict):
    """
    GET robusto à API WP REST com retry/backoff.
    Retorna (lista_de_posts, total_paginas) ou (None, 0) em caso de falha.
    """
    headers = {"User-Agent": USER_AGENT}
    for tentativa in range(1, MAX_RETRY + 1):
        try:
            r = requests.get(endpoint, headers=headers, params=params,
                             timeout=TIMEOUT_S, verify=VERIFY_SSL)
            if r.status_code == 200:
                total_pg = int(r.headers.get("X-WP-TotalPages", 1) or 1)
                return r.json(), total_pg
            # 400 com page além do fim é normal (fim da paginação) — encerra
            if r.status_code == 400:
                return [], 0
            return None, 0
        except Exception:
            time.sleep(min(4 * tentativa, 12))
    return None, 0


def _montar(post: dict, categoria: str, termo: str, portal: str) -> dict:
    """Converte um post da API no registro padronizado do CSV."""
    titulo = limpar_html(post.get("title", {}).get("rendered", ""))
    resumo = limpar_html(post.get("excerpt", {}).get("rendered", ""))
    return {
        "data_publicacao": post.get("date", ""),       # Brasília
        "data_gmt"       : post.get("date_gmt", ""),    # UTC
        "ativo"          : "PETR4",
        "categoria"      : categoria,
        "fonte_coleta"   : f"WP_{portal}",
        "termo_busca"    : termo,
        "titulo"         : titulo,
        "resumo"         : resumo,
        "url"            : post.get("link", ""),
        "dominio"        : portal,
        "idioma"         : "pt",
        "hash_titulo"    : hash_titulo(titulo),
    }


# ==============================================================================
# BLOCO 4 — COLETOR DE UM PORTAL (híbrido: full-range OU janela mensal)
# ==============================================================================

_FIELDS = "id,date,date_gmt,link,title,excerpt"


def _paginar(endpoint: str, base_params: dict, total_pg: int,
             categoria: str, termo: str, portal: str):
    """Itera as páginas 2..total_pg (a página 1 é tratada por quem chama)."""
    for pg in range(2, total_pg + 1):
        _pausa()
        params = dict(base_params, page=pg)
        posts, _ = _get(endpoint, params)
        if not posts:
            break
        for p in posts:
            yield _montar(p, categoria, termo, portal)


def coletar_termo(portal: str, endpoint: str, categoria: str, termo: str,
                  inicio: datetime, fim: datetime):
    """
    Gera artigos de um portal para um (categoria, termo), escolhendo a estratégia:
      • full-range se o termo tiver poucas páginas no período;
      • janela mensal se for de alto volume.
    """
    janela = {
        "search": termo, "per_page": PER_PAGE, "orderby": "date", "order": "asc",
        "after": inicio.strftime("%Y-%m-%dT00:00:00"),
        "before": fim.strftime("%Y-%m-%dT23:59:59"),
        "_fields": _FIELDS, "page": 1,
    }
    posts, total_pg = _get(endpoint, janela)
    if posts is None:
        log.warning("%s | '%s' | falha na sondagem inicial — pulado.", portal, termo)
        return

    # --- Estratégia A: full-range (poucas páginas) ---
    if total_pg <= LIMITE_PAGINAS_FULLRANGE:
        for p in posts:
            yield _montar(p, categoria, termo, portal)
        yield from _paginar(endpoint, janela, total_pg, categoria, termo, portal)
        return

    # --- Estratégia B: janela mensal (alto volume) ---
    log.info("   %s | '%s' alto volume (%d págs) → janela mensal", portal, termo, total_pg)
    cursor = inicio
    while cursor <= fim:
        fim_mes = min(cursor + relativedelta(months=1) - relativedelta(seconds=1), fim)
        mp = {
            "search": termo, "per_page": PER_PAGE, "orderby": "date", "order": "asc",
            "after": cursor.strftime("%Y-%m-%dT00:00:00"),
            "before": fim_mes.strftime("%Y-%m-%dT23:59:59"),
            "_fields": _FIELDS, "page": 1,
        }
        posts_m, total_m = _get(endpoint, mp)
        if posts_m:
            for p in posts_m:
                yield _montar(p, categoria, termo, portal)
            yield from _paginar(endpoint, mp, total_m, categoria, termo, portal)
        _pausa()
        cursor += relativedelta(months=1)


# ==============================================================================
# BLOCO 5 — ORQUESTRADOR
# ==============================================================================

def executar() -> None:
    inicio = TESTE_INICIO if MODO_TESTE else DATA_INICIO
    fim    = TESTE_FIM    if MODO_TESTE else DATA_FIM
    portais = dict(list(PORTAIS.items())[:2]) if MODO_TESTE else PORTAIS
    taxonomia = (dict(list(TERMOS_POR_CATEGORIA.items())[:2])
                 if MODO_TESTE else TERMOS_POR_CATEGORIA)

    n_termos = sum(len(v) for v in taxonomia.values())
    log.info("=" * 70)
    log.info("COLETA WORDPRESS REST | modo=%s | período %s → %s",
             "TESTE" if MODO_TESTE else "COMPLETO", inicio.date(), fim.date())
    log.info("Portais: %s", list(portais))
    log.info("Categorias: %d | Termos: %d | Pares (termo×portal): %d",
             len(taxonomia), n_termos, n_termos * len(portais))
    log.info("=" * 70)

    # Retomada: carrega hashes já gravados
    hashes: set[str] = set()
    if ARQUIVO_CSV.exists():
        try:
            import pandas as pd
            hashes = set(pd.read_csv(ARQUIVO_CSV, usecols=["hash_titulo"])["hash_titulo"].dropna())
            log.info("Retomada: %d artigos já gravados.", len(hashes))
        except Exception:
            pass

    cnt = {"bruto": 0, "novos": 0, "dup": 0, "irrelevante": 0}
    por_portal: dict[str, int] = {}
    por_categoria: dict[str, int] = {}

    modo = "a" if ARQUIVO_CSV.exists() else "w"
    with open(ARQUIVO_CSV, modo, newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CAMPOS_CSV)
        if modo == "w":
            writer.writeheader()

        for portal, endpoint in portais.items():
            log.info("──── PORTAL: %s ────", portal)
            for categoria, termos in taxonomia.items():
                for termo in termos:
                    for art in coletar_termo(portal, endpoint, categoria, termo, inicio, fim):
                        cnt["bruto"] += 1
                        if FILTRAR_RELEVANCIA and not e_relevante(art["titulo"], art["resumo"]):
                            cnt["irrelevante"] += 1
                            continue
                        if art["hash_titulo"] in hashes:
                            cnt["dup"] += 1
                            continue
                        hashes.add(art["hash_titulo"])
                        cnt["novos"] += 1
                        por_portal[portal] = por_portal.get(portal, 0) + 1
                        por_categoria[categoria] = por_categoria.get(categoria, 0) + 1
                        writer.writerow(art)
                    f.flush()
                log.info("   [%s/%s] acumulado: %d notícias únicas", portal, categoria, cnt["novos"])

    log.info("=" * 70)
    log.info("CONCLUÍDO | brutos=%d | novos=%d | duplicados=%d | irrelevantes=%d",
             cnt["bruto"], cnt["novos"], cnt["dup"], cnt["irrelevante"])
    log.info("Por portal:")
    for nome, n in sorted(por_portal.items(), key=lambda x: -x[1]):
        log.info("   %-14s: %d", nome, n)
    log.info("Por categoria:")
    for nome, n in sorted(por_categoria.items(), key=lambda x: -x[1]):
        log.info("   %-24s: %d", nome, n)
    log.info("Arquivo: %s", ARQUIVO_CSV)
    log.info("=" * 70)


if __name__ == "__main__":
    executar()
