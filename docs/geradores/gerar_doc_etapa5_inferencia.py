# -*- coding: utf-8 -*-
# ==============================================================================
#   DISSERTAÇÃO PETR4 — Gerador da Documentação (ETAPA 5: Sistema de Inferência)
#   Autor: Vanderlei Barbosa da Silva | Orientador: Prof. Dr. Julio Cesar Nievola
#
#   Documento ABNT sobre a aplicação que avalia uma notícia nova e prevê a
#   direção da PETR4: arquitetura, pipeline de inferência, e a EVOLUÇÃO dos
#   refinamentos (versões 1→2→3) com os ajustes, testes e exemplos de resultado
#   após cada melhoria. Saída: docs/saida/Documentacao_Etapa5_Inferencia_PETR4.docx
# ==============================================================================

import sys
from pathlib import Path
RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src" / "comum"))
import abnt_docx as abnt

SAIDA = RAIZ / "docs" / "saida" / "Documentacao_Etapa5_Inferencia_PETR4.docx"

doc = abnt.novo_documento()
abnt.capa(
    doc,
    "Sistema de Inferência e Previsão de Direção da PETR4",
    "Etapa 5 — Aplicação, Refinamentos e Evolução dos Resultados",
    "Vanderlei Barbosa da Silva",
    "Orientador: Prof. Dr. Julio Cesar Nievola",
    "Pontifícia Universidade Católica do Paraná — Mestrado em Informática",
    descricao=("Documento técnico-metodológico da dissertação “O Impacto do Sentimento de Notícias "
               "Financeiras na Previsão de Direção e Volatilidade do Ativo PETR4”. Descreve a "
               "aplicação que aplica o modelo a uma notícia inédita e a evolução iterativa de seus "
               "refinamentos, com testes e exemplos de resultado após cada ajuste."),
)

# 1
abnt.secao(doc, "1", "Objetivo e arquitetura da aplicação")
abnt.paragrafo(doc,
 "A aplicação recebe o texto de uma notícia inédita e estima a direção provável da PETR4 no próximo "
 "pregão, tornando o pipeline da pesquisa verificável de forma interativa. A arquitetura é "
 "cliente-servidor: um backend em FastAPI (Python) expõe os modelos por uma API; um frontend em "
 "React apresenta os resultados, incluindo uma visualização animada do percurso da notícia pelas "
 "etapas. Os modelos empregados são o FinBERT-PT-BR (sentimento) e o XGBoost Data Fusion (direção), "
 "ambos treinados nas etapas anteriores.")
abnt.tabela_abnt(doc, "1", "Bibliotecas e ferramentas da aplicação e sua justificativa",
 ["Ferramenta", "Função", "Justificativa"],
 [["FastAPI", "API HTTP do backend", "Framework moderno, performático e com documentação automática"],
  ["transformers + PyTorch", "Inferência do FinBERT-PT-BR", "Backend nativo do modelo de sentimento"],
  ["XGBoost", "Inferência da direção", "Modelo treinado na Etapa 4 (Data Fusion)"],
  ["React + Vite", "Interface interativa", "Padrão de mercado para aplicações web responsivas"],
  ["Recharts", "Gráficos interativos", "Biblioteca de gráficos para React, leve e acessível"]])

# 2
abnt.secao(doc, "2", "Pipeline de inferência")
abnt.paragrafo(doc,
 "Ao receber uma notícia, a aplicação executa seis etapas encadeadas, apresentadas ao usuário como "
 "uma jornada animada:")
abnt.lista(doc, [
 "**Recepção** do texto e normalização.",
 "**Sentimento** (FinBERT-PT-BR): classifica o tom em positivo, negativo ou neutro, com escore.",
 "**Relevância e categoria**: verifica se a notícia se relaciona à PETR4/petróleo (taxonomia de 152 termos) e identifica a categoria temática.",
 "**Leitura econômica setorial**: interpreta o efeito sobre a Petrobras à luz da literatura (distinguindo mercado e ativo).",
 "**Modelo estatístico** (XGBoost Data Fusion): estima a probabilidade de alta a partir de retorno, volatilidade e sentimento.",
 "**Veredito**: sintetiza os sinais e indica a direção provável, com a respectiva justificativa.",
])

# 3 — Evolução dos refinamentos
abnt.secao(doc, "3", "Evolução dos refinamentos: ajustes, testes e novos resultados")
abnt.paragrafo(doc,
 "O sistema de inferência foi aprimorado em três versões sucessivas, a partir de casos de teste que "
 "revelaram limitações. Cada ajuste é documentado com o problema observado, a correção e o resultado.")
abnt.tabela_abnt(doc, "2", "Evolução dos refinamentos da inferência",
 ["Versão", "Ajuste introduzido", "Problema que passou a ser resolvido"],
 [["v1 — inicial", "Relevância por 13 termos; veredito pela probabilidade do modelo",
   "Linha de base; falhava em notícias relevantes não cobertas pelos poucos termos"],
  ["v2 — leitura setorial", "Relevância pela taxonomia completa (152 termos) + interpretação econômica por categoria (Kilian, 2009; Hamilton, 1983)",
   "“Fechamento do Estreito de Ormuz” passou a ser reconhecido como relevante e classificado como ALTA (choque de oferta favorece a produtora)"],
  ["v3 — camada de evento", "Distinção entre DISRUPÇÃO (evento ruim ocorrendo) e RESOLUÇÃO (evento ruim terminando), e entre mecanismo de EMPRESA e de MERCADO",
   "“Petroleiros aceitam acordo e greve termina” passou de BAIXA para ALTA, pois é a resolução de um evento operacional"]])

abnt.secao(doc, "3.1", "Problema de polaridade e a correção semântica", nivel=2)
abnt.paragrafo(doc,
 "Um caso de teste evidenciou uma limitação importante: a manchete “Petroleiros aceitam acordo da "
 "Petrobras e greve termina após 16 dias” era classificada como NEGATIVA pelo modelo de sentimento "
 "(pela presença da palavra “greve”) e, consequentemente, como tendência de BAIXA. Contudo, o "
 "TÉRMINO de uma greve é, economicamente, FAVORÁVEL à empresa. A correção (versão 3) introduziu uma "
 "camada semântica que distingue o sentido do evento, conforme o Quadro 1.")
abnt.quadro_codigo(doc, "1", "Camada semântica: disrupção × resolução (lógica)",
'''RESOLUCAO  = ["acordo", "greve termina", "fim da paralisação", "cessar-fogo",
              "normalização", "retomada", "trégua", "fim do bloqueio", ...]
DISRUPCAO  = ["greve", "paralisação", "ataque", "guerra", "intervenção",
              "bloqueio", "sanção", "acidente", "demissão", ...]

tipo_evento = "resolução"  se houver termo de RESOLUCAO
              "disrupção"  se houver termo de DISRUPCAO
              "neutro"     caso contrário''')
abnt.quadro_codigo(doc, "2", "Mecanismo de transmissão por categoria (lógica)",
'''# Empresa (Petrobras/governança): o evento afeta a operação/valor
if mecanismo == "empresa":
    resolução -> ALTA ;  disrupção -> BAIXA
# Mercado de petróleo (oferta/geopolítica): o evento afeta o PREÇO da commodity
if mecanismo == "oferta":
    disrupção -> ALTA  (preço do petróleo sobe, favorece a produtora)
    resolução -> BAIXA (preço do petróleo cai)''')

# 4 — Exemplos de resultado
abnt.secao(doc, "4", "Exemplos de resultado após os refinamentos")
abnt.paragrafo(doc,
 "A Tabela 3 apresenta o veredito do sistema (versão 3) para um conjunto de manchetes de teste. Os "
 "casos foram escolhidos para cobrir as distinções relevantes — disrupção × resolução e empresa × "
 "mercado — e todos produziram o resultado economicamente esperado.")
abnt.tabela_abnt(doc, "3", "Vereditos do sistema (versão 3) em casos de teste",
 ["Manchete de teste", "Categoria", "Evento", "Veredito"],
 [["Petroleiros aceitam acordo e greve termina após 16 dias", "Empresa", "resolução", "▲ Alta"],
  ["Petroleiros iniciam greve e paralisam refinarias da Petrobras", "Empresa", "disrupção", "▼ Baixa"],
  ["Guerra fecha o Estreito de Ormuz e impede a navegação de petroleiros", "Geopolítica", "disrupção", "▲ Alta"],
  ["Cessar-fogo no Oriente Médio derruba o preço do petróleo", "Mercado de Petróleo", "resolução", "▼ Baixa"],
  ["Petrobras anuncia dividendos recordes e lucro acima do esperado", "Empresa", "—", "▲ Alta"],
  ["Governo demite o presidente da Petrobras e anuncia intervenção", "Empresa", "disrupção", "▼ Baixa"],
  ["Receita de bolo de cenoura com cobertura de chocolate", "—", "—", "○ Sem influência"]])
abnt.paragrafo(doc,
 "O último caso ilustra o controle de relevância: uma notícia sem relação com o ativo é corretamente "
 "rotulada como “sem influência”, não gerando previsão.")

# 5 — Mercado x ativo
abnt.secao(doc, "5", "Distinção entre mercado e ativo (resposta à banca)")
abnt.paragrafo(doc,
 "A banca de qualificação (Prof. Hisson) questionou como o método diferenciaria uma notícia negativa "
 "para o MERCADO de uma notícia negativa para a PETROBRAS — citando o exemplo de uma guerra no "
 "Oriente Médio, que derruba a bolsa mas, ao elevar o preço do petróleo, pode beneficiar a "
 "Petrobras. A leitura econômica setorial responde diretamente a essa observação: para eventos de "
 "oferta (geopolítica, sanções, infraestrutura global), uma disrupção de tom negativo é tratada "
 "como FAVORÁVEL à produtora, ao passo que, para eventos da própria empresa, o efeito segue o "
 "sentido do evento. Essa distinção, fundamentada em Kilian (2009) e Hamilton (1983), é apresentada "
 "ao usuário de forma transparente, ao lado da leitura puramente estatística do modelo.")

# 6 — Limitações
abnt.secao(doc, "6", "Limitações e natureza dos sinais")
abnt.lista(doc, [
 "A leitura econômica setorial é uma heurística baseada em regras e vocabulário; não substitui o modelo estatístico, sendo apresentada em paralelo a ele com total transparência.",
 "O modelo estatístico mantém acurácia da ordem de 53%; as previsões têm caráter acadêmico/experimental e não constituem recomendação de investimento.",
 "O vocabulário de eventos (disrupção/resolução) é finito e pode não cobrir todas as formulações; sua expansão é trabalho contínuo.",
 "A categorização de uma notícia inédita usa correspondência de termos; casos ambíguos podem exigir desambiguação adicional.",
])

abnt.referencias(doc, "7", [
 "HAMILTON, J. D. Oil and the macroeconomy since World War II. Journal of Political Economy, v. 91, n. 2, p. 228-248, 1983.",
 "KILIAN, L. Not all oil price shocks are alike: disentangling demand and supply shocks in the crude oil market. American Economic Review, v. 99, n. 3, p. 1053-1069, 2009.",
 "CHEN, T.; GUESTRIN, C. XGBoost: a scalable tree boosting system. In: KDD, 2016. p. 785-794.",
])

doc.save(SAIDA)
print(f"✅ Documento ABNT gerado: {SAIDA}")
