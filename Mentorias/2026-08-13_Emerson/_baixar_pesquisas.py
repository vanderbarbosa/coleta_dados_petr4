# -*- coding: utf-8 -*-
# ==============================================================================
#   Baixa os PDFs abertos das pesquisas levantadas
#   Saída: Mentoria_Emerson_13082026/pesquisas_pdf/
#
#   Baixa APENAS o que está publicamente disponível: arXiv, MDPI e SBC (acesso
#   aberto), SSRN (preprints) e repositórios institucionais. O que estiver atrás
#   de assinatura de editora é registrado no manifesto como não obtido, com a
#   indicação de onde consegui-lo pela biblioteca da PUCPR.
# ==============================================================================
from __future__ import annotations

import json
import time
import urllib.request
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DESTINO = AQUI / "pesquisas_pdf"
DESTINO.mkdir(exist_ok=True)

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"}

# (arquivo, url, autor/ano, o que preve)
ABERTOS = [
    ("01_HALOUSKOVA_LYOCSA_2025_volatilidade_404_acoes.pdf",
     "https://arxiv.org/pdf/2503.19767",
     "Halousková e Lyócsa (2025)", "VOLATILIDADE"),
    ("02_BODILSEN_LUNDE_2025_news_analytics_volatilidade.pdf",
     "https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID4401032_code1234.pdf?abstractid=4401032",
     "Bodilsen e Lunde (2025)", "VOLATILIDADE"),
    ("03_MINO_WILLIAMSON_2025_BERT_GARCH.pdf",
     "https://arxiv.org/pdf/2510.16503",
     "Mino e Williamson (2025)", "VOLATILIDADE"),
    ("04_RAHIMIKIA_POON_embeddings_volatilidade.pdf",
     "https://arxiv.org/pdf/2108.00480",
     "Rahimikia e Poon (2021)", "VOLATILIDADE"),
    ("05_HASHAMIA_MALDONADO_2025_direcao_da_volatilidade_petroleo.pdf",
     "https://arxiv.org/pdf/2508.20707",
     "Hashamia e Maldonado (2025)", "DIRECAO DA VOLATILIDADE"),
    ("06_BOLLEN_2011_twitter_mood_direcao_DJIA.pdf",
     "https://arxiv.org/pdf/1010.3003",
     "Bollen, Mao e Zeng (2011)", "DIRECAO (indice)"),
    ("07_LACHANSKI_PAV_2017_refutacao_do_Bollen.pdf",
     "https://econjwatch.org/file_download/1037/LachanskiPavSept2017.pdf",
     "Lachanski e Pav (2017)", "REFUTACAO do Bollen"),
    ("08_FINBERT_LSTM_2024_preco_NASDAQ.pdf",
     "https://arxiv.org/pdf/2407.16150",
     "Gu e Zhong (2024)", "PRECO (nivel)"),
    ("09_FINBERT_LSTM_2022_original.pdf",
     "https://arxiv.org/pdf/2211.07392",
     "FinBERT-LSTM (2022)", "PRECO (nivel)"),
    ("10_FINBERT_SHAP_2025_direcao_SP500.pdf",
     "https://www.mdpi.com/2227-7390/13/17/2747/pdf",
     "MDPI Mathematics (2025)", "DIRECAO"),
    # --------------------------------------------------- encoders e referencia
    ("11_ARACI_2019_FinBERT_ingles.pdf",
     "https://arxiv.org/pdf/1908.10063",
     "Araci (2019)", "encoder"),
    ("12_YANG_2020_FinBERT_HKUST.pdf",
     "https://arxiv.org/pdf/2006.08097",
     "Yang, Uy e Huang (2020)", "encoder"),
    ("13_SHAH_2022_FLANG_FLUE.pdf",
     "https://arxiv.org/pdf/2211.00083",
     "Shah et al. (2022)", "encoder"),
    ("14_KAPLAN_2023_CrudeBERT_petroleo.pdf",
     "https://arxiv.org/pdf/2305.06140",
     "Kaplan et al. (2023)", "encoder (petroleo)"),
    ("15_MALO_2014_Financial_PhraseBank.pdf",
     "https://arxiv.org/pdf/1307.5336",
     "Malo et al. (2014)", "padrao-ouro de rotulagem"),
    ("16_ELECTRONICS_2025_ajuste_setorial_FinBERT.pdf",
     "https://www.mdpi.com/2079-9292/14/23/4680/pdf",
     "Electronics 14(23):4680 (2025)", "encoder — o do F1 0,555 -> 0,707"),
    ("17_SANTOS_2023_FinBERT_PT_BR.pdf",
     "https://sol.sbc.org.br/index.php/bwaif/article/download/24960/24781/",
     "Santos, Bianchi e Costa (2023)", "encoder — O NOSSO"),
    ("18_TELES_2025_LLMs_sentimento.pdf",
     "https://arxiv.org/pdf/2510.15929",
     "Teles e Figueiredo (2025)", "comparacao LLM"),
]

# nao abertos — registrar onde obter
FECHADOS = [
    ("Schumaker e Chen (2009)", "DIRECAO (20 min)",
     "Information Processing & Management 45:571-583",
     "Elsevier — obter pela biblioteca da PUCPR (Portal de Periodicos CAPES)"),
    ("Barak, Arjmand e Ortobelli (2017)", "RETORNO e RISCO",
     "Information Fusion",
     "Elsevier — Portal de Periodicos CAPES"),
    ("Nguyen, Shirai e Velcin (2015)", "DIRECAO",
     "Expert Systems with Applications",
     "Elsevier — Portal de Periodicos CAPES"),
    ("Li et al. (2020)", "TENDENCIA",
     "Information Processing & Management",
     "Elsevier — Portal de Periodicos CAPES"),
    ("Huang, Wang e Yang (2023)", "encoder",
     "Contemporary Accounting Research 40(2):806-841",
     "Wiley — Portal de Periodicos CAPES. O preprint (item 12) cobre o essencial"),
    ("Bodilsen e Lunde (2025) — versao publicada", "VOLATILIDADE",
     "Journal of Applied Econometrics 40(1):18-36",
     "Wiley — Portal de Periodicos CAPES. Tentamos a versao SSRN"),
    ("Horserace cripto (2024)", "VOLATILIDADE",
     "Asia-Pacific Financial Markets",
     "Springer — Portal de Periodicos CAPES"),
    ("Silva (2018)", "RETORNO e VOLATILIDADE",
     "Tese de doutorado",
     "Repositorio da instituicao de origem"),
]


def baixar(nome: str, url: str) -> tuple[bool, str]:
    alvo = DESTINO / nome
    if alvo.exists() and alvo.stat().st_size > 20_000:
        return True, f"ja existia ({alvo.stat().st_size // 1024} KB)"
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=60) as r:
            dados = r.read()
        if not dados.startswith(b"%PDF"):
            return False, "resposta nao e PDF (provavel bloqueio)"
        alvo.write_bytes(dados)
        return True, f"{len(dados) // 1024} KB"
    except Exception as e:                                    # noqa: BLE001
        return False, f"{type(e).__name__}: {str(e)[:60]}"


def main() -> None:
    print("=" * 74)
    print("BAIXANDO AS PESQUISAS DE ACESSO ABERTO")
    print("=" * 74)
    manifesto = {"baixados": [], "nao_obtidos": []}

    for nome, url, autor, alvo_prev in ABERTOS:
        ok, msg = baixar(nome, url)
        print(f"  [{'OK ' if ok else 'FALHA'}] {autor:34s} {msg}")
        (manifesto["baixados"] if ok else manifesto["nao_obtidos"]).append(
            {"autor": autor, "preve": alvo_prev, "arquivo": nome if ok else None,
             "url": url, "situacao": msg})
        time.sleep(1.5)                      # cortesia com os servidores

    for autor, alvo_prev, veiculo, onde in FECHADOS:
        print(f"  [FECHADO] {autor:31s} {veiculo}")
        manifesto["nao_obtidos"].append(
            {"autor": autor, "preve": alvo_prev, "veiculo": veiculo,
             "situacao": "assinatura de editora", "como_obter": onde})

    (DESTINO / "_MANIFESTO.json").write_text(
        json.dumps(manifesto, indent=2, ensure_ascii=False), encoding="utf-8")

    n_ok = len(manifesto["baixados"])
    print("\n" + "=" * 74)
    print(f"  baixados ....... {n_ok}")
    print(f"  nao obtidos .... {len(manifesto['nao_obtidos'])}")
    print(f"  pasta .......... {DESTINO}")


if __name__ == "__main__":
    main()
