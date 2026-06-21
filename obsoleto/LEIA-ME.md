# ⚠️ Scripts DESATIVADOS (obsoletos)

Os arquivos desta pasta **não fazem mais parte do pipeline ativo**. Foram preservados apenas para registro histórico e auditoria (rastreabilidade metodológica da dissertação). **Não execute estes scripts** — eles foram substituídos pela coleta via WordPress REST API ([../src/coleta/02b_coleta_noticias_wordpress_petr4.py](../src/coleta/02b_coleta_noticias_wordpress_petr4.py)).

| Arquivo | O que era | Por que foi desativado |
|---------|-----------|------------------------|
| `02_coleta_noticias_gdelt_petr4.py` | Coleta simples via GDELT | GDELT só retorna o título e bloqueia o IP por volume (HTTP 429); cobertura irregular em português |
| `02_coleta_noticias_petr4.py` | Coleta multifonte v3.1 (GDELT + NewsAPI + RSS) | NewsAPI gratuita cobre só 30 dias; GDELT instável; substituída por fonte com **hora exata** (WordPress) |
| `02_coleta_noticias_petr4_OLD.py` | Versão 3.0 do multifonte | Versão anterior, mantida só para histórico |
| `teste_rss_feeds.py` | Diagnóstico dos feeds RSS | RSS deixou de ser usado após a migração para WordPress REST |

**Motivo central da substituição:** a banca de qualificação exigiu o *timestamp* exato de publicação (data, hora e minuto) para validar a causalidade Lead-Lag com o GARCH(1,1). Nenhuma destas fontes entregava isso de forma confiável; a API REST do WordPress entrega. Ver o histórico completo em [../docs/DOCUMENTACAO_BASES.md](../docs/DOCUMENTACAO_BASES.md) e no documento da Etapa 1.
