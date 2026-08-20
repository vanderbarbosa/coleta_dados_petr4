# -*- coding: utf-8 -*-
# ==============================================================================
#   Monta a pasta com os PDFs das SEIS pesquisas essenciais
#   Saída: Mentoria_Emerson_13082026/AS_SEIS_PESQUISAS_PDF/
#
#   Copia as que já temos e tenta baixar as demais por rotas alternativas
#   legítimas: CDN do MDPI (acesso aberto), site do próprio autor, e arquivos
#   abertos institucionais (HAL, repositórios universitários).
# ==============================================================================
from __future__ import annotations

import json
import shutil
import time
import urllib.request
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ORIGEM = AQUI / "pesquisas_pdf"
DESTINO = AQUI / "AS_SEIS_PESQUISAS_PDF"
DESTINO.mkdir(exist_ok=True)

UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/pdf,text/html,*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
}

# (arquivo_destino, alvo, autor, [ja_temos] ou [urls candidatas])
SEIS = [
    # ---------------------------------------------------------- VOLATILIDADE
    ("VOL_1_HALOUSKOVA_LYOCSA_2025.pdf", "VOLATILIDADE",
     "Halousková e Lyócsa (2025) — 404 ações do S&P 500, vence o HAR",
     {"copiar": "01_HALOUSKOVA_LYOCSA_2025_volatilidade_404_acoes.pdf"}),

    ("VOL_2_HASHAMI_MALDONADO_2025.pdf", "DIREÇÃO DA VOLATILIDADE",
     "Hashami e Maldonado (2025) — petróleo Brent, embedding vence sentimento",
     {"copiar": "05_HASHAMIA_MALDONADO_2025_direcao_da_volatilidade_petroleo.pdf"}),

    ("VOL_3_BODILSEN_LUNDE_2025.pdf", "VOLATILIDADE",
     "Bodilsen e Lunde (2025) — J. Applied Econometrics, macro contra empresa",
     {"urls": [
         "https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID4401032_code5340923.pdf?abstractid=4401032&mirid=1",
         "https://pure.au.dk/portal/files/exploiting-news-analytics.pdf",
     ]}),

    # --------------------------------------------------------------- DIREÇÃO
    ("DIR_1_RUAN_JIANG_2025.pdf", "DIREÇÃO",
     "Ruan e Jiang (2025) — Mathematics, arquitetura quase idêntica à nossa",
     {"urls": [
         "https://mdpi-res.com/d_attachment/mathematics/mathematics-13-02747/"
         "article_deploy/mathematics-13-02747.pdf",
     ]}),

    ("DIR_2_NGUYEN_SHIRAI_VELCIN_2015.pdf", "DIREÇÃO",
     "Nguyen, Shirai e Velcin (2015) — ganho de 2 a 10 p.p., a nossa régua",
     {"urls": [
         "https://hal.science/hal-01203094/document",
         "https://hal.science/hal-01203094v1/file/paper.pdf",
     ]}),

    ("DIR_3_SCHUMAKER_CHEN_2009.pdf", "DIREÇÃO (20 min)",
     "Schumaker e Chen (2009) — AZFinText, 71,18%",
     {"urls": [
         "https://www.robschumaker.com/publications/"
         "IPM%20-%20A%20Quantitative%20Stock%20Prediction%20System%20based%20on%20Financial%20News.pdf",
     ]}),
]

COMO_OBTER = {
    "VOL_3_BODILSEN_LUNDE_2025.pdf":
        "Journal of Applied Econometrics 40(1):18-36 (Wiley). Obter pelo Portal de "
        "Periódicos CAPES com o login da PUCPR. Versão de trabalho no SSRN, "
        "abstract_id=4401032.",
}


def baixar(urls: list[str]) -> tuple[bytes | None, str]:
    for url in urls:
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as r:
                dados = r.read()
            if dados.startswith(b"%PDF"):
                return dados, f"{len(dados) // 1024} KB de {url.split('/')[2]}"
            ultimo = "resposta não era PDF"
        except Exception as e:                                  # noqa: BLE001
            ultimo = f"{type(e).__name__}"
        time.sleep(1.5)
    return None, ultimo


def main() -> None:
    print("=" * 76)
    print("MONTANDO A PASTA DAS SEIS PESQUISAS ESSENCIAIS")
    print("=" * 76)

    manifesto = {"pasta": str(DESTINO), "pesquisas": []}
    obtidas = 0

    for arquivo, alvo, autor, fonte in SEIS:
        destino = DESTINO / arquivo
        if "copiar" in fonte:
            origem = ORIGEM / fonte["copiar"]
            if origem.exists():
                shutil.copy2(origem, destino)
                msg, ok = f"copiado ({destino.stat().st_size // 1024} KB)", True
            else:
                msg, ok = "arquivo de origem não encontrado", False
        else:
            dados, msg = baixar(fonte["urls"])
            ok = dados is not None
            if ok:
                destino.write_bytes(dados)

        obtidas += ok
        print(f"  [{'OK   ' if ok else 'FALHA'}] {arquivo:34s} {msg}")
        manifesto["pesquisas"].append({
            "arquivo": arquivo if ok else None, "alvo": alvo, "autor": autor,
            "obtido": ok, "situacao": msg,
            **({"como_obter": COMO_OBTER[arquivo]}
               if not ok and arquivo in COMO_OBTER else {})})

    (DESTINO / "_MANIFESTO.json").write_text(
        json.dumps(manifesto, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n" + "=" * 76)
    print(f"  obtidas: {obtidas} de 6")
    print(f"  pasta:   {DESTINO}")


if __name__ == "__main__":
    main()
