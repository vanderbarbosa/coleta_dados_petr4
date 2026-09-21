# -*- coding: utf-8 -*-
# ==============================================================================
#   Organiza o projeto em pastas de Artigo e de Mentoria
#
#   Idempotente: pode rodar quantas vezes quiser. Copia, não move, para que
#   nada se perca se algum caminho estiver errado.
# ==============================================================================
from __future__ import annotations

import shutil
from pathlib import Path

AQUI = Path(__file__).resolve().parent
MEM_ORIGEM = Path("C:/Users/Vanderlei/.claude/projects/"
                  "d--Mestrado-scripts-claude-base-textual/memory")

# ── estrutura de pastas ──────────────────────────────────────────────────────
ARTIGOS = {
    "Artigo_1_O_Relogio_da_CVM": [
        (AQUI / "Artigos/01_ARTIGO_CVM_HORA_OFICIAL.docx", "01_ARTIGO.docx"),
        (AQUI / "CVM/01_RESULTADO_CVM.docx", "fontes/Resultado_completo_CVM.docx"),
        (AQUI / "CVM/04_EXPLICACAO_COMPLETA.docx", "fontes/Explicacao_para_leigos.docx"),
        (AQUI / "CVM/05_PAINEL_RESULTADOS.xlsx", "fontes/Painel_de_resultados.xlsx"),
        (AQUI / "CVM/dados/numeros_artigo1.json", "dados/numeros_do_artigo.json"),
        (AQUI / "CVM/dados/rodada_A.json", "dados/rodada_A.json"),
        (AQUI / "CVM/dados/fr_vs_cm.json", "dados/fato_relevante_vs_comunicado.json"),
        (AQUI / "CVM/dados/evento_por_horario.json", "dados/evento_por_horario.json"),
        (AQUI / "CVM/dados/numeros_concretos.json", "dados/numeros_concretos.json"),
        (AQUI / "CVM/dados/casos_concretos_top.csv", "dados/casos_ilustrativos.csv"),
        (AQUI / "CVM/01_coletar_ipe.py", "codigo/01_coletar_ipe.py"),
        (AQUI / "CVM/04_coletar_hora_oficial.py", "codigo/02_coletar_hora_oficial.py"),
        (AQUI / "CVM/06_coletar_ohlcv.py", "codigo/03_coletar_precos.py"),
        (AQUI / "CVM/07_rodada_A.py", "codigo/04_estudo_de_evento.py"),
        (AQUI / "CVM/05_evento_por_horario.py", "codigo/05_evento_por_horario.py"),
        (AQUI / "CVM/09_casos_concretos.py", "codigo/06_casos_concretos.py"),
    ],
    "Artigo_2_Auditoria_do_Classificador": [
        (AQUI / "Rotulagem_Especialistas/02_RESULTADO_PARA_A_MENTORIA.docx",
         "fontes/Resultado_rotulagem_especialistas.docx"),
        (AQUI / "Rotulagem_Especialistas/01_PROTOCOLO.docx", "fontes/Protocolo.docx"),
        (AQUI / "Rotulagem_Especialistas/_v2_para_auditoria.csv",
         "dados/224_pareceres_PARA_AUDITAR.csv"),
        (AQUI / "Rotulagem_Especialistas/_v2_resultado.json", "dados/resultado.json"),
        (AQUI / "Rotulagem_Especialistas/02_extrair_veredictos_v2.py",
         "codigo/extrair_veredictos.py"),
        (AQUI / "Mentoria_Emerson_13082026/10_GLOSSARIO.docx", "fontes/Glossario.docx"),
    ],
    "Artigo_3_Armadilhas_de_Medicao": [
        (AQUI / "CVM/dados/numeros_concretos.json", "dados/composicao_vs_efeito.json"),
        (AQUI / "CVM/dados/confronto_corrigido.json", "dados/regra_corrigida.json"),
        (AQUI / "CVM/12_confronto_fontes.py", "codigo/confronto_fontes.py"),
    ],
}

MENTORIAS = {
    "2026-08-13_Emerson": [
        (AQUI / "Mentoria_Emerson_13082026", None),      # pasta inteira
    ],
    "2026-08-26_Emerson_e_Julio": [
        (AQUI / "Rotulagem_Especialistas/01_PROTOCOLO.docx", "01_Protocolo.docx"),
        (AQUI / "Rotulagem_Especialistas/02_RESULTADO_PARA_A_MENTORIA.docx",
         "02_Resultado.docx"),
        (AQUI / "CVM/01_RESULTADO_CVM.docx", "03_Resultado_CVM.docx"),
    ],
    "2026-09-16_Emerson_e_Julio": [
        (AQUI / "CVM/02_PLANO_VALIDACAO.docx", "01_Plano.docx"),
        (AQUI / "CVM/03_RESULTADOS_A_E_B.docx", "02_Resultados.docx"),
        (AQUI / "CVM/04_EXPLICACAO_COMPLETA.docx", "03_Explicacao_completa.docx"),
        (AQUI / "CVM/05_PAINEL_RESULTADOS.xlsx", "04_Painel_resultados.xlsx"),
    ],
    "2026-09-20_Julio_e_Emerson": [
        (AQUI / "Artigos/00_TRES_PROPOSTAS.docx", "01_Tres_propostas.docx"),
        (AQUI / "Artigos/01_ARTIGO_CVM_HORA_OFICIAL.docx", "02_Artigo_1.docx"),
    ],
}


def copia(origem: Path, destino: Path) -> bool:
    if not origem.exists():
        return False
    destino.parent.mkdir(parents=True, exist_ok=True)
    if origem.is_dir():
        shutil.copytree(origem, destino, dirs_exist_ok=True)
    else:
        shutil.copy2(origem, destino)
    return True


def main() -> None:
    print("=" * 76)
    print("ORGANIZANDO O PROJETO")
    print("=" * 76)

    # ── Artigos ──────────────────────────────────────────────────────────────
    print("\n  ARTIGOS")
    for pasta, itens in ARTIGOS.items():
        base = AQUI / "Artigos" / pasta
        ok = falta = 0
        for orig, rel in itens:
            if copia(orig, base / rel):
                ok += 1
            else:
                falta += 1
                print(f"     [ausente] {orig.name}")
        print(f"    {pasta:<38} {ok:>2} arquivos"
              + (f"  ({falta} ausentes)" if falta else ""))

    # fontes bibliográficas compartilhadas
    pdfs = AQUI / "Mentoria_Emerson_13082026" / "pesquisas_pdf"
    if pdfs.exists():
        dest = AQUI / "Artigos" / "_fontes_bibliograficas"
        shutil.copytree(pdfs, dest, dirs_exist_ok=True)
        n = len(list(dest.glob("*.pdf")))
        print(f"    {'_fontes_bibliograficas':<38} {n:>2} PDFs das pesquisas citadas")

    # ── Mentorias ────────────────────────────────────────────────────────────
    print("\n  MENTORIAS")
    for pasta, itens in MENTORIAS.items():
        base = AQUI / "Mentorias" / pasta
        ok = 0
        for orig, rel in itens:
            destino = base if rel is None else base / rel
            if copia(orig, destino):
                ok += 1
        print(f"    {pasta:<38} {ok:>2} itens")

    # ── memória portátil ─────────────────────────────────────────────────────
    print("\n  MEMÓRIA")
    destino = AQUI / "_memoria_claude" / "memory"
    if MEM_ORIGEM.exists():
        shutil.copytree(MEM_ORIGEM, destino, dirs_exist_ok=True)
        n = len(list(destino.glob("*.md")))
        print(f"    copiados {n} arquivos de memória para _memoria_claude/memory/")
    else:
        print(f"    [ausente] {MEM_ORIGEM}")

    print("\n" + "-" * 76)
    print("  Concluído. Os arquivos foram COPIADOS, não movidos — as pastas")
    print("  originais continuam intactas.")


if __name__ == "__main__":
    main()
