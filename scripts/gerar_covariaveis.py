#!/usr/bin/env python3
"""Gera covariaveis auxiliares para os modelos de quantidade e custo de chamados.

Uso:
    python scripts/gerar_covariaveis.py                 # gera area projetada e pessoas SIMULADAS
    python scripts/gerar_covariaveis.py --verificar     # lista a origem de cada covariavel
    python scripts/gerar_covariaveis.py --verificar --modo artigo   # falha se houver dado SIMULADO

Regras (definidas pelo autor):
  1. Area construida e total: valores observados de dados/area_manutencao.json; anos futuros
     = valor do ano anterior * (1 + 5%). Origem: OBSERVADO ou PROJETADO_5PCT.
  2. Pessoas (estudantes, docentes, tecnicos, terceirizados) por campus: nao existem em nenhum
     repositorio; sao SIMULADAS ate que os dados reais sejam fornecidos. Anos futuros = anterior * 1,05.
     Origem: SIMULADO. A simulacao e tendencia suave, colinear com o tempo, e serve apenas para
     testar o pipeline; nenhum resultado de artigo pode usa-la.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CONFIG = RAIZ / "dados_externos" / "config_covariaveis.json"
AREA_JSON = RAIZ / "dados" / "area_manutencao.json"
SAIDA_AREA = RAIZ / "dados_externos" / "area_global_projetada.csv"
SAIDA_PESSOAS = RAIZ / "dados_externos" / "pessoas_por_campus_SIMULADO.csv"
CATEGORIAS = ["estudantes", "docentes", "tecnicos", "terceirizados"]


def ler_area(caminho: Path = AREA_JSON) -> dict[int, tuple[float, float]]:
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    return {int(r[0]): (float(r[1]), float(r[2])) for r in dados[1:] if r and r[0] not in ("", None)}


def projetar_area(observada: dict[int, tuple[float, float]], anos: list[int], taxa: float):
    """Devolve lista de (ano, construida, total, origem) com projecao composta de taxa ao ano."""
    linhas = [(a, c, t, "OBSERVADO") for a, (c, t) in sorted(observada.items())]
    ultimo = max(observada)
    c, t = observada[ultimo]
    for ano in sorted(anos):
        if ano <= ultimo:
            continue
        c, t = c * (1 + taxa), t * (1 + taxa)
        linhas.append((ano, round(c, 2), round(t, 2), "PROJETADO_5PCT"))
    return linhas


def simular_pessoas(cfg: dict, anos_projetados: list[int]):
    """Tendencia linear de razao_2018*base em 2018 ate base no ano base; depois, crescimento composto."""
    p = cfg["pessoas_simuladas"]
    base_ano, r0, taxa = p["ano_base"], p["razao_2018_sobre_base"], p["crescimento_projecao_anual"]
    linhas = []
    for campus, base in p["base"].items():
        for ano in range(2018, max(anos_projetados) + 1):
            vals = {}
            for cat in CATEGORIAS:
                b = base[cat]
                if ano <= base_ano:
                    frac = r0 + (1 - r0) * (ano - 2018) / (base_ano - 2018)
                    v = b * frac
                else:
                    v = b * (1 + taxa) ** (ano - base_ano)
                vals[cat] = round(v)
            linhas.append({"ano": ano, "campus": campus, **vals, "origem": "SIMULADO"})
    return linhas


def gravar_csv(caminho: Path, campos: list[str], linhas: list[dict]):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(linhas)


def gerar() -> int:
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    area = projetar_area(ler_area(), cfg["area"]["anos_projetados"], cfg["area"]["crescimento_projecao_anual"])
    gravar_csv(SAIDA_AREA, ["ano", "area_construida_m2", "area_total_m2", "origem"],
               [{"ano": a, "area_construida_m2": c, "area_total_m2": t, "origem": o} for a, c, t, o in area])
    pessoas = simular_pessoas(cfg, cfg["area"]["anos_projetados"])
    gravar_csv(SAIDA_PESSOAS, ["ano", "campus", *CATEGORIAS, "origem"], pessoas)
    print(f"{len(area)} linhas em {SAIDA_AREA.name}; {len(pessoas)} linhas SIMULADAS em {SAIDA_PESSOAS.name}")
    return 0


def verificar(modo: str) -> int:
    estado = {}
    for nome, caminho in (("area", SAIDA_AREA), ("pessoas", SAIDA_PESSOAS),
                          ("precipitacao", RAIZ / "dados_externos" / "precipitacao_mensal_por_campus.csv"),
                          ("calendario", RAIZ / "dados_externos" / "calendario_letivo_ufsb.csv")):
        if not caminho.exists():
            estado[nome] = "AUSENTE"
            continue
        with caminho.open(encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        origens = sorted({r.get("origem") or r.get("status") or "REAL_FONTE_EXTERNA" for r in rows})
        estado[nome] = ",".join(origens)
    for k, v in estado.items():
        print(f"{k}: {v}")
    if modo == "artigo":
        ruins = {k: v for k, v in estado.items() if "SIMULADO" in v or "AUSENTE" in v or "PENDENTE" in v}
        if ruins:
            print(f"BLOQUEADO para artigo: {ruins}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--verificar", action="store_true")
    ap.add_argument("--modo", choices=["teste", "artigo"], default="teste")
    a = ap.parse_args()
    sys.exit(verificar(a.modo) if a.verificar else gerar())
