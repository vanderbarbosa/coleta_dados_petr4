# -*- coding: utf-8 -*-
# ==============================================================================
#   Etapa 4 — A HORA OFICIAL DE ENTREGA, do Protocolo de Entrega da CVM
#
#   POR QUE ESTA ETAPA EXISTE
#     O conjunto aberto (IPE) traz apenas a DATA. O dicionário oficial confirma:
#     "Data de entrega/recebimento do documento", sem hora. Sem a hora não se
#     sabe se o documento saiu antes da abertura, com o pregão aberto ou depois
#     do fechamento — e isso decide a janela do estudo de evento.
#
#   O QUE FOI DESCARTADO, E POR QUÊ
#     O carimbo /ModDate do PDF do documento. Ele registra quando a EMPRESA
#     fechou o arquivo, não quando a CVM recebeu. É hora aproximada — e hora
#     aproximada, num estudo de evento, é pior que hora nenhuma.
#
#     A tela de consulta do RAD também traz hora (dd/mm/aaaa hh:mm), mas só
#     devolve documentos de 2026 em diante. Não serve para 2018–2025.
#
#   DE ONDE VEM A HORA USADA AQUI
#     Do PROTOCOLO DE ENTREGA — o recibo oficial que a CVM emite para cada
#     documento. Texto literal do recibo:
#
#       Protocolo de Entrega
#       9512 - PETRÓLEO BRASILEIRO S.A. - PETROBRAS
#       O documento foi entregue para CVM e B3
#       Tipo de Documento: Fato Relevante
#       Data do Documento: 03/01/2018
#       Data da Entrega: 03/01/2018 07:20:19      <-- oficial, com segundos
#       Protocolo: 009512IPE030120180104310213-17
#
#     Obtido pelo método público frmConsultaExternaCVM.aspx/RetornarProtocoloPDF,
#     que recebe o numSequencia — presente em 100% dos Link_Download do conjunto
#     aberto. O captcha da tela está desligado na origem (hdnHabilitaCaptcha=N);
#     nada foi contornado.
#
#   O script é RETOMÁVEL: grava a cada lote e relê o que já foi feito.
#
#   Saída: CVM/dados/cvm_hora_entrega.csv
# ==============================================================================
from __future__ import annotations

import argparse
import base64
import io
import re
import sys
import time
import warnings
from pathlib import Path

import pandas as pd
import requests
import urllib3
from pypdf import PdfReader

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore")

AQUI = Path(__file__).resolve().parent
DADOS = AQUI / "dados"
SAIDA = DADOS / "cvm_hora_entrega.csv"

BASE = "https://www.rad.cvm.gov.br/ENETWeb/"
METODO = BASE + "frmConsultaExternaCVM.aspx/RetornarProtocoloPDF"

RE_ENTREGA = re.compile(r"Data da Entrega:\s*(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2}:\d{2})")
RE_DOC = re.compile(r"Data do Documento:\s*(\d{2}/\d{2}/\d{4})")
RE_PROT = re.compile(r"Protocolo:\s*(\S+)")

PAUSA = 0.7          # cortesia com o servidor
LOTE = 50            # grava a cada N documentos


def sessao() -> requests.Session:
    s = requests.Session()
    s.verify = False
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": BASE + "frmConsultaExternaCVM.aspx",
        "Origin": "https://www.rad.cvm.gov.br"})
    s.get(BASE + "frmConsultaExternaCVM.aspx", timeout=60)
    return s


def recibo(s: requests.Session, num_seq: str) -> dict | None:
    """Baixa o Protocolo de Entrega e extrai a data/hora oficial."""
    for k in range(1, 4):
        try:
            r = s.post(METODO, timeout=120,
                       json={"numeroSequencialDocumento": int(num_seq),
                             "tipoDocumento": "IPE"})
            v = r.json().get("d", "")
            if not isinstance(v, str) or v.startswith("ERRO") or len(v) < 200:
                return None
            txt = "\n".join((p.extract_text() or "")
                            for p in PdfReader(io.BytesIO(base64.b64decode(v))).pages)
            m = RE_ENTREGA.search(txt)
            if not m:
                return None
            md, mp = RE_DOC.search(txt), RE_PROT.search(txt)
            return {"numSequencia": num_seq,
                    "Data_Entrega_oficial": m.group(1),
                    "Hora_Entrega_oficial": m.group(2),
                    "Data_Documento_recibo": md.group(1) if md else "",
                    "Protocolo_recibo": mp.group(1) if mp else ""}
        except Exception:                                     # noqa: BLE001
            time.sleep(3 * k)
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--categoria", default="Fato Relevante",
                    help="'Fato Relevante', 'Comunicado ao Mercado' ou 'todas'")
    ap.add_argument("--limite", type=int, default=0, help="0 = sem limite")
    a = ap.parse_args()

    base = pd.read_csv(DADOS / "cvm_para_classificar.csv", dtype=str)
    base["numSequencia"] = base["Link_Download"].str.extract(r"numSequencia=(\d+)")
    base = base[base["numSequencia"].notna()]
    if a.categoria != "todas":
        base = base[base["Categoria"] == a.categoria]

    feitos: set[str] = set()
    if SAIDA.exists():
        ja = pd.read_csv(SAIDA, dtype=str)
        feitos = set(ja["numSequencia"])
    fila = [x for x in base["numSequencia"].tolist() if x not in feitos]
    if a.limite:
        fila = fila[:a.limite]

    print("=" * 76)
    print("ETAPA 4 — HORA OFICIAL DE ENTREGA (Protocolo de Entrega da CVM)")
    print("=" * 76)
    print(f"  categoria ..... {a.categoria}")
    print(f"  já coletados .. {len(feitos):,}")
    print(f"  na fila ....... {len(fila):,}\n")
    if not fila:
        print("  nada a fazer."); return

    s = sessao()
    buf, ok, falha, t0 = [], 0, 0, time.time()
    for i, seq in enumerate(fila, start=1):
        r = recibo(s, seq)
        if r:
            buf.append(r); ok += 1
        else:
            falha += 1
        if i % LOTE == 0 or i == len(fila):
            if buf:
                pd.DataFrame(buf).to_csv(
                    SAIDA, mode="a", header=not SAIDA.exists(), index=False,
                    encoding="utf-8-sig")
                buf = []
            vel = i / max(time.time() - t0, 1)
            resta = (len(fila) - i) / max(vel, 1e-9) / 60
            print(f"  [{i:>6,}/{len(fila):,}] ok={ok:,} falha={falha:,}  "
                  f"{vel:.2f}/s  restam ~{resta:.0f} min", flush=True)
        time.sleep(PAUSA)

    print(f"\n  concluído: {ok:,} com hora, {falha:,} sem.")
    print(f"  gravado: {SAIDA}")


if __name__ == "__main__":
    main()
