# -*- coding: utf-8 -*-
# ==============================================================================
#
#   DISSERTAÇÃO : O Impacto do Sentimento de Notícias Financeiras na Previsão
#                 de Direção e Volatilidade do Ativo PETR4
#   Autor       : Vanderlei Barbosa da Silva
#   Orientador  : Prof. Dr. Julio Cesar Nievola — PUCPR
#   Script      : 02a — Diagnóstico de RSS Feeds
#   Versão      : 2.0 (atualizado após validação de 10/06/2026)
#
# ==============================================================================
#
#   O QUE ESTE SCRIPT FAZ
#   ──────────────────────
#   Testa todas as URLs de RSS configuradas no Script 02 (coleta principal)
#   e reporta quais estão funcionando, quantas entradas retornam, e quantas
#   são relevantes para o corpus de petróleo/Petrobras.
#
#   QUANDO EXECUTAR
#   ────────────────
#   Execute este script ANTES de rodar o Script 02 pela primeira vez,
#   e sempre que suspeitar que algum feed parou de funcionar.
#   Feeds RSS mudam de URL ou são encerrados sem aviso — validação
#   periódica é boa prática para garantir a integridade do corpus.
#
#   COMO EXECUTAR
#   ──────────────
#   No terminal, com o ambiente virtual ativo (.venv):
#     python teste_rss_feeds.py
#
#   Tempo estimado: ~40 segundos (0.8s de pausa entre cada feed)
#
#   INTERPRETANDO O RESULTADO
#   ──────────────────────────
#   ✅ OK    → Feed funcionando. Número após OK = total de entradas no feed.
#   ❌ VAZIO → URL acessível mas sem entradas. Feed encerrado ou URL desatualizada.
#   ❌ ERRO  → URL inacessível (timeout, DNS, bloqueio). Verificar manualmente.
#
#   A coluna RELEV mostra quantas entradas contêm ao menos um termo relevante
#   para o corpus (petróleo, Petrobras, OPEP etc.). Feeds com RELEV = 0 podem
#   ser mantidos mesmo assim — o filtro de relevância no Script 02 usa termos
#   mais abrangentes e contextos que este diagnóstico não cobre totalmente.
#
#   HISTÓRICO DE VALIDAÇÕES
#   ────────────────────────
#   10/06/2026 — Primeira validação completa. Resultado: 18 OK, 13 mortos.
#     Feeds encerrados identificados: Reuters (feeds.reuters.com e
#     reuters.com/*/feed/), Bloomberg Energy, Valor Econômico (URL antiga),
#     Estadão Economia, InfoMoney mercados/ações, Agência Brasil,
#     Band News, EIA, Platts.
#     Ação: URLs corrigidas e feeds substitutos incluídos no Script 02.
#
# ==============================================================================


import feedparser
import time
from datetime import datetime

# Exatamente os mesmos feeds configurados no Script 02 (coleta principal).
# Quando o Script 02 for atualizado com novos feeds, atualizar aqui também.
FEEDS_PARA_TESTAR: dict[str, str] = {

    # ── NACIONAIS ─────────────────────────────────────────────────────────────
    "G1_Economia"        : "https://g1.globo.com/rss/g1/economia/",
    "G1_Mercado"         : "https://g1.globo.com/rss/g1/economia/mercados/",
    "InfoMoney"          : "https://www.infomoney.com.br/feed/",
    "Valor_Economico"    : "http://www.valor.com.br/rss",
    "Exame_Invest"       : "https://exame.com/feed/",
    "UOL_Economia"       : "https://rss.uol.com.br/feed/economia.xml",
    "Folha_Mercado"      : "https://feeds.folha.uol.com.br/mercado/rss091.xml",
    "CNN_Brasil_Negocios": "https://www.cnnbrasil.com.br/feed/",
    "Poder360_Econ"      : "https://www.poder360.com.br/feed/",
    "Money_Times"        : "https://www.moneytimes.com.br/feed/",
    "E_Investidor"       : "https://einvestidor.estadao.com.br/feed/",
    "BrazilJournal"      : "https://braziljournal.com/feed/",
    "Agencia_Camara"     : "https://www.camara.leg.br/noticias/rss/ultimas",
    "Metropoles_Econ"    : "https://www.metropoles.com/feed",

    # ── INTERNACIONAIS ────────────────────────────────────────────────────────
    "BBC_Business"       : "https://feeds.bbci.co.uk/news/business/rss.xml",
    "MarketWatch"        : "https://feeds.marketwatch.com/marketwatch/topstories/",
    "OilPrice_News"      : "https://oilprice.com/rss/main",
    "Rigzone"            : "https://www.rigzone.com/news/rss/rigzone_latest.aspx",
    "CNBC_Energy"        : "https://www.cnbc.com/id/10000664/device/rss/rss.html",
    "FT_Energy"          : "https://www.ft.com/energy?format=rss",
    "Investing_Oil"      : "https://www.investing.com/rss/news_14.rss",
    "Investing_Commod"   : "https://www.investing.com/rss/news_11.rss",
    "Yahoo_Finance"      : "https://finance.yahoo.com/news/rssindex",
    "GoogleNews_Oil"     : "https://news.google.com/rss/search?q=oil+price+OPEC&hl=en-US&gl=US&ceid=US:en",
    "World_Oil"          : "https://worldoil.com/rss?feed=news",
}

# Termos usados para contar notícias relevantes (diagnóstico apenas).
# O filtro real no Script 02 usa TERMOS_FILTRO_RSS, mais completo.
TERMOS_RELEVANCIA: list[str] = [
    "petrobras", "petr4", "petróleo", "brent", "wti", "opep", "opec",
    "barril", "refinaria", "oleoduto", "offshore", "aramco", "pdvsa",
    "oriente médio", "rússia", "ucrânia", "embargo", "bloqueio",
    "combustível", "gasolina", "diesel", "energia", "oil", "petroleum",
    "crude", "natural gas", "lng", "opec", "barrel",
]


def contar_relevantes(entries: list) -> int:
    """Conta entradas que contêm ao menos um termo relevante no título ou resumo."""
    count = 0
    for e in entries:
        texto = (e.get("title", "") + " " + e.get("summary", "")).lower()
        if any(t in texto for t in TERMOS_RELEVANCIA):
            count += 1
    return count


# ── Execução do diagnóstico ───────────────────────────────────────────────────

agora = datetime.now().strftime("%d/%m/%Y %H:%M")
print()
print("=" * 74)
print(f"  DIAGNÓSTICO DE RSS FEEDS  —  {agora}")
print(f"  Total de feeds testados: {len(FEEDS_PARA_TESTAR)}")
print("=" * 74)
print(f"  {'STATUS':<8} {'TOTAL':>5} {'RELEV':>5}   {'NOME':<22}   PRIMEIRO TÍTULO")
print("-" * 74)

feeds_ok:    list[tuple] = []
feeds_mortos: list[tuple] = []

for nome, url in FEEDS_PARA_TESTAR.items():
    try:
        feed = feedparser.parse(url)
        total = len(feed.entries)
        relev = contar_relevantes(feed.entries)
        titulo = feed.entries[0].get("title", "")[:35] if total > 0 else "—"

        if total > 0:
            status = "✅ OK"
            feeds_ok.append((nome, url, total, relev))
        else:
            status = "❌ VAZIO"
            feeds_mortos.append((nome, url, "sem entradas"))

        print(f"  {status:<8} {total:>5} {relev:>5}   {nome:<22}   {titulo}")

    except Exception as exc:
        feeds_mortos.append((nome, url, str(exc)))
        print(f"  {'❌ ERRO':<8} {'?':>5} {'?':>5}   {nome:<22}   {exc}")

    time.sleep(0.8)

# ── Relatório final ───────────────────────────────────────────────────────────
print("=" * 74)
print(f"\n  ✅ Feeds funcionando  : {len(feeds_ok)}")
print(f"  ❌ Feeds com problema : {len(feeds_mortos)}")

total_entradas = sum(t for _, _, t, _ in feeds_ok)
total_relev    = sum(r for _, _, _, r in feeds_ok)
print(f"\n  Total de entradas nos feeds ativos : {total_entradas}")
print(f"  Entradas relevantes para o corpus  : {total_relev}")

if feeds_mortos:
    print("\n  ── Feeds que precisam de atenção ──────────────────────────────────")
    for nome, url, motivo in feeds_mortos:
        print(f"    ❌ {nome:<22}  ({motivo})")
    print()
    print("  Se novos feeds estiverem mortos, cole este resultado no chat")
    print("  para atualizar as URLs no Script 02.")
else:
    print("\n  Todos os feeds estão funcionando. Script 02 pode ser executado.")

print()
