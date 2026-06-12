# GUIA DE EXECUÇÃO — DISSERTAÇÃO PETR4
## Vanderlei Barbosa da Silva | PUCPR — Mestrado em Informática

---

## VISÃO GERAL DOS 4 SCRIPTS

```
Script 01  →  Script 02  →  Script 03  →  Script 04
  PETR4          Notícias     Sentimento    GARCH +
 Financeiro      GDELT        BERTimbau     SVM/XGBoost
```

Cada script gera arquivos que o próximo precisa. Execute **sempre na ordem**.

---

## ANTES DE COMEÇAR — CONFIGURAÇÕES DO COLAB

### 1. Criar uma pasta no seu Google Drive
- Abra o Google Drive
- Crie a pasta: `Mestrado_PETR4`
- Os scripts criam automaticamente todos os subdiretórios

### 2. Ativar GPU (obrigatório para o Script 03)
- No Colab: **Menu → Ambiente de execução → Alterar tipo de ambiente de execução**
- Em "Acelerador de hardware": selecione **GPU (T4)**
- Clique em **Salvar**

---

## SCRIPT 01 — Coleta Financeira
**Arquivo:** `01_coleta_dados_financeiros_petr4.py`
**Tempo estimado:** ~3 minutos

### O que faz:
Baixa os preços diários da PETR4 (2018-2025) da B3 via yFinance e calcula o Log-Retorno.

### O que gera:
- `Mestrado_PETR4/base_financeira_petr4.csv`

### Como rodar:
1. Abra o arquivo no Google Colab
2. Clique em **"Ambiente de execução" → "Executar tudo"**
3. Autorize o Drive quando aparecer a janela de permissão

### O que você deve ver no final:
```
✅ COLETA CONCLUÍDA COM SUCESSO!
   Arquivo salvo em: /content/drive/MyDrive/Mestrado_PETR4/base_financeira_petr4.csv
   Total de dias de pregão: ~1750
```

---

## SCRIPT 02 — Coleta de Notícias
**Arquivo:** `02_coleta_noticias_gdelt_petr4.py`
**Tempo estimado:** 25 a 45 minutos

### O que faz:
Coleta notícias sobre Petrobras/PETR4 publicadas entre 2018-2025 via GDELT Project
(base de dados global gratuita, citável academicamente).

### O que gera:
- `Mestrado_PETR4/base_textual_petr4_2018_2025.csv`
- `Mestrado_PETR4/checkpoints_noticias/` (salvamentos automáticos a cada 3 meses)

### Como rodar:
1. Abra no Colab e execute tudo
2. **Não feche o Colab** durante a execução (o script coleta mês a mês)
3. Se cair, pode rodar novamente — o script continua do início

### O que você deve ver:
```
📅 Coletando: Janeiro/2018 ... ✅ 45 notícias únicas encontradas
📅 Coletando: Fevereiro/2018 ... ✅ 38 notícias únicas encontradas
...
✅ COLETA CONCLUÍDA!   Total de notícias: ~8.000 a 15.000
```

### ⚠️ ATENÇÃO — Se a API retornar 0 notícias:
A API do GDELT pode estar sobrecarregada. Aguarde 10 minutos e tente novamente.

---

## SCRIPT 03 — Análise de Sentimento (BERTimbau)
**Arquivo:** `03_analise_sentimento_bertimbau_petr4.py`
**Tempo estimado:** 15-30 min (com GPU) ou 2-4h (sem GPU)

### Pré-requisito obrigatório:
- GPU **ativada** no Colab (veja "Antes de Começar" acima)
- Script 02 executado com sucesso

### O que faz:
- Baixa o modelo BERTimbau (~1 GB — acontece só na primeira vez)
- Lê cada notícia do corpus e classifica como Positivo/Neutro/Negativo
- Calcula o Índice de Sentimento Diário da Mídia (ISM)
- Aplica alinhamento temporal (notícias after-market → próximo pregão)

### O que gera:
- `Mestrado_PETR4/indice_sentimento_petr4.csv` ← **entrada do Script 04**
- `Mestrado_PETR4/noticias_com_sentimento.csv` ← corpus completo com sentimento

### O que você deve ver:
```
✅ GPU detectada: Tesla T4
🧠 Carregando o modelo: cardiffnlp/twitter-xlm-roberta-base-sentiment
✅ Modelo carregado!
   [  0.0%]    0/12543 notícias processadas...
   [ 25.0%] 3136/12543 notícias processadas...
   [100.0%] 12543/12543 notícias processadas.
✅ Extração de sentimento concluída!
```

---

## SCRIPT 04 — Modelagem GARCH + SVM + XGBoost
**Arquivo:** `04_modelagem_garch_svm_xgboost_petr4.py`
**Tempo estimado:** ~10 a 20 minutos

### Pré-requisito:
- Scripts 01, 02 e 03 executados com sucesso

### O que faz (na ordem):
1. **Testes estatísticos**: Jarque-Bera, ADF, ARCH-LM
2. **GARCH(1,1)**: modela a volatilidade condicional
3. **Data Fusion**: combina preços + GARCH + sentimento
4. **Treina 4 modelos**: SVM e XGBoost com e sem sentimento
5. **Walk-Forward Validation**: 80% treino, 20% teste cronológico
6. **Gera todos os gráficos** e a Tabela 4.3 da dissertação

### O que gera:
| Arquivo | Onde usar na dissertação |
|---------|--------------------------|
| `resultados_modelos_petr4.csv` | Tabela 4.3 |
| `grafico_volatilidade_garch.png` | Figura 4.2 |
| `grafico_dispersao_sentimento_volatilidade.png` | Figura 4.4 |
| `relatorio_testes_estatisticos.txt` | Seção 4.3 |
| `base_master_petr4.csv` | Base consolidada para análises futuras |

### O que você deve ver no final:
```
TABELA 4.3 — DESEMPENHO DOS CLASSIFICADORES
                          Modelo  Acurácia  Precisão  F1-Score  AUC-ROC
             SVM (Apenas Preços)     52.XX     51.XX     51.XX   0.5XX
         XGBoost (Apenas Preços)     54.XX     53.XX     54.XX   0.5XX
  SVM (Data Fusion — GARCH + NLP)    61.XX     62.XX     61.XX   0.6XX
XGBoost (Data Fusion — GARCH + NLP)  67.XX     68.XX     68.XX   0.7XX

📊 GANHO DE ACURÁCIA COM DATA FUSION:
   XGBoost: +13.XX pontos percentuais
```

---

## ESTRUTURA DE ARQUIVOS FINAL NO SEU DRIVE

```
Mestrado_PETR4/
│
├── base_financeira_petr4.csv              ← Script 01
├── base_textual_petr4_2018_2025.csv       ← Script 02
├── noticias_com_sentimento.csv            ← Script 03
├── indice_sentimento_petr4.csv            ← Script 03
├── base_master_petr4.csv                  ← Script 04
│
├── resultados_modelos_petr4.csv           ← Tabela 4.3
├── relatorio_testes_estatisticos.txt      ← Seção 4.3
├── grafico_volatilidade_garch.png         ← Figura 4.2
├── grafico_dispersao_sentimento_vol.png   ← Figura 4.4
│
└── checkpoints_noticias/                  ← Backups do Script 02
```

---

## ERROS COMUNS E SOLUÇÕES

| Erro | Causa | Solução |
|------|-------|---------|
| `FileNotFoundError` no Script 04 | Scripts anteriores não foram executados | Execute na ordem: 01 → 02 → 03 → 04 |
| `CUDA out of memory` no Script 03 | GPU sem memória | Mude `TAMANHO_LOTE = 32` para `16` no Script 03 |
| `0 notícias coletadas` no Script 02 | API GDELT sobrecarregada | Aguarde 10 min e rode novamente |
| Drive não conecta | Sessão expirada | Reconecte: clique no link de autenticação |
| Script 03 muito lento | GPU não ativada | Ative a GPU (veja "Antes de Começar") |

---

## COMO CITAR O GDELT NA DISSERTAÇÃO

> Os dados textuais foram extraídos do GDELT Project (LEETARU; SCHRODT, 2013),
> base de dados global de eventos e notícias jornalísticas que indexa mais de
> 100 idiomas, incluindo o português brasileiro, com cobertura desde 2015.

**Referência bibliográfica:**
LEETARU, K.; SCHRODT, P. A. GDELT: Global data on events, location, and tone, 1979–2012. In: *ISA Annual Convention*, 2013.

---

*Guia gerado em: 27/04/2026*
*Dissertação: O Impacto do Sentimento de Notícias Financeiras na Previsão de Direção e Volatilidade do Ativo PETR4 — PUCPR, 2026*
