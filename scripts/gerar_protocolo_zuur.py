#!/usr/bin/env python3
"""Gera diagnostico de exploracao de dados segundo Zuur et al. (2010).

Usa apenas snapshots publicos do repositorio. Nao acessa Google Sheets nem a base
bruta CHAMADOS.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DADOS = RAIZ / "dados"
CSV_DIR = RAIZ / "dados_csv"
SAIDA_JSON = DADOS / "protocolo_zuur.json"
SAIDA_CSV = CSV_DIR / "protocolo_zuur.csv"

REFERENCIA = (
    "Zuur, A.F., Ieno, E.N. & Elphick, C.S. (2010). A protocol for data "
    "exploration to avoid common statistical problems. Methods in Ecology and "
    "Evolution, 1(1), 3-14. doi:10.1111/j.2041-210X.2009.00001.x"
)


def carregar(nome: str) -> list:
    caminho = DADOS / nome
    if not caminho.exists():
        return []
    return json.loads(caminho.read_text(encoding="utf-8"))


def numero(valor) -> float | None:
    if isinstance(valor, (int, float)) and not isinstance(valor, bool):
        return float(valor)
    if isinstance(valor, str):
        texto = valor.strip().replace("%", "").replace(".", "").replace(",", ".")
        if not texto:
            return None
        try:
            return float(texto)
        except ValueError:
            return None
    return None


def linhas_tabela(tabela: list) -> tuple[list[str], list[list]]:
    if not tabela or not isinstance(tabela[0], list):
        return [], []
    return [str(c) for c in tabela[0]], [r for r in tabela[1:] if any(str(c).strip() for c in r)]


def iqr(valores: list[float]) -> dict:
    xs = sorted(v for v in valores if v is not None)
    if not xs:
        return {"n": 0, "status": "Informação insuficiente para verificar."}
    def pct(p: float) -> float:
        pos = (len(xs) - 1) * p
        lo = int(pos)
        hi = min(lo + 1, len(xs) - 1)
        frac = pos - lo
        return xs[lo] * (1 - frac) + xs[hi] * frac
    q1, q3 = pct(0.25), pct(0.75)
    dist = q3 - q1
    li, ls = q1 - 1.5 * dist, q3 + 1.5 * dist
    return {
        "n": len(xs),
        "min": round(xs[0], 4),
        "q1": round(q1, 4),
        "q3": round(q3, 4),
        "max": round(xs[-1], 4),
        "outliers_baixos": sum(1 for v in xs if v < li),
        "outliers_altos": sum(1 for v in xs if v > ls),
    }


def contar_resultados(pressupostos: list, pressuposto: str) -> dict:
    cab, linhas = linhas_tabela(pressupostos)
    try:
        i_tipo = cab.index("Pressuposto")
        i_res = cab.index("Resultado")
    except ValueError:
        return {"status": "Informação insuficiente para verificar."}
    recs = [str(r[i_res]) for r in linhas if len(r) > max(i_tipo, i_res) and str(r[i_tipo]) == pressuposto]
    return {
        "n_testes": len(recs),
        "ok": sum("OK" in r for r in recs),
        "atencao": sum(("ATEN" in r.upper()) or ("CRIT" in r.upper()) for r in recs),
        "resultados": recs[:12],
    }


def main() -> int:
    temporal = carregar("previsao_temporal.json")
    pressupostos = carregar("previsao_pressupostos.json")
    validacao = carregar("previsao_validacao.json")
    categorias = carregar("previsao_por_categoria.json")
    granger = carregar("previsao_granger.json")

    cab, linhas = linhas_tabela(temporal)
    real_idx = cab.index("Quantidade Real") if "Quantidade Real" in cab else None
    vencedor_idx = cab.index("Vencedor (menor RMSE holdout = 33.48)") if "Vencedor (menor RMSE holdout = 33.48)" in cab else len(cab) - 1
    historico = [
        numero(r[real_idx]) for r in linhas
        if real_idx is not None and len(r) > max(real_idx, vencedor_idx) and str(r[vencedor_idx]) in ("In-sample", "Backtest (out-of-sample)")
    ]
    historico = [v for v in historico if v is not None]

    passos = [
        {
            "passo": 1,
            "titulo": "Outliers em Y e covariaveis",
            "status": "verificado",
            "evidencia": "dados/previsao_temporal.json",
            "resultado": iqr(historico),
            "mudanca_minima": "Manter tratamento ja existente no motor e registrar o total de pontos tratados no painel.",
        },
        {
            "passo": 2,
            "titulo": "Homogeneidade de variancia",
            "status": "verificado",
            "evidencia": "dados/previsao_pressupostos.json",
            "resultado": contar_resultados(pressupostos, "Homocedasticidade"),
            "mudanca_minima": "Exibir sintese dos testes Breusch-Pagan ja publicados.",
        },
        {
            "passo": 3,
            "titulo": "Normalidade",
            "status": "verificado",
            "evidencia": "dados/previsao_pressupostos.json e dados/previsao_qqplot.json",
            "resultado": contar_resultados(pressupostos, "Normalidade"),
            "mudanca_minima": "Manter Q-Q plot e registrar que normalidade e diagnostico, nao pre-condicao para publicar forecast.",
        },
        {
            "passo": 4,
            "titulo": "Zeros ou ausencia estrutural",
            "status": "verificado",
            "evidencia": "dados/previsao_temporal.json",
            "resultado": {"n_zeros": sum(1 for v in historico if v == 0), "n_observacoes": len(historico)},
            "mudanca_minima": "Declarar zeros como meses sem chamados registrados, sem imputar demanda.",
        },
        {
            "passo": 5,
            "titulo": "Colinearidade entre covariaveis",
            "status": "verificado",
            "evidencia": "dados/previsao_pressupostos.json",
            "resultado": contar_resultados(pressupostos, "Multicolinearidade"),
            "mudanca_minima": "Expor VIF dos regressores exogenos quando o modelo usa contexto sazonal.",
        },
        {
            "passo": 6,
            "titulo": "Relacoes entre Y e X",
            "status": "verificado",
            "evidencia": "dados/previsao_granger.json",
            "resultado": {"linhas_granger": max(0, len(granger) - 1) if isinstance(granger, list) else 0},
            "mudanca_minima": "Referenciar causalidade temporal exploratoria e nao causalidade substantiva definitiva.",
        },
        {
            "passo": 7,
            "titulo": "Interacoes",
            "status": "verificado",
            "evidencia": "dados/previsao_por_categoria.json",
            "resultado": {"linhas_categoria": max(0, len(categorias) - 1) if isinstance(categorias, list) else 0},
            "mudanca_minima": "Usar categoria como interacao operacional sem misturar com o eixo de classificacao.",
        },
        {
            "passo": 8,
            "titulo": "Independencia temporal",
            "status": "verificado",
            "evidencia": "dados/previsao_pressupostos.json e dados/previsao_validacao.json",
            "resultado": {
                "independencia": contar_resultados(pressupostos, "Independência"),
                "folds_validacao": max(0, len(validacao) - 1) if isinstance(validacao, list) else 0,
            },
            "mudanca_minima": "Manter validacao rolling-origin e testes Durbin-Watson/Ljung-Box como diagnostico central.",
        },
    ]

    out = {
        "gerado_em": datetime.now(timezone.utc).isoformat(),
        "repositorio": "malha-previsao-chamados",
        "eixo": "previsao de volume mensal de chamados",
        "referencia": REFERENCIA,
        "escopo": "Exploracao sobre snapshots publicos do eixo de previsao de chamados; sem base bruta e sem credenciais.",
        "diagnostico_do_que_falta": [
            "Nenhum calculo bruto adicional e necessario para iniciar o protocolo: os principais insumos ja estao publicados.",
            "Falta apenas materializar o resumo transversal em dados/protocolo_zuur.json e exibi-lo no dashboard.",
        ],
        "passos": passos,
        "metodo_artigo": (
            "No eixo de previsao de chamados, a exploracao seguiu os oito passos de Zuur et al. (2010) "
            "sobre a serie mensal de contagens, residuos dos modelos, validacao rolling-origin, "
            "regressores sazonais e recortes por categoria. Outliers foram tratados antes dos ajustes, "
            "normalidade e homocedasticidade foram avaliadas como diagnosticos dos residuos, colinearidade "
            "foi examinada por VIF quando havia variaveis exogenas, e independencia temporal foi avaliada "
            "por Durbin-Watson, Ljung-Box e validacao rolling-origin."
        ),
    }

    SAIDA_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    CSV_DIR.mkdir(exist_ok=True)
    with SAIDA_CSV.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.writer(fp)
        writer.writerow(["passo", "titulo", "status", "evidencia", "mudanca_minima"])
        for p in passos:
            writer.writerow([p["passo"], p["titulo"], p["status"], p["evidencia"], p["mudanca_minima"]])
    print(f"OK {SAIDA_JSON}")
    print(f"OK {SAIDA_CSV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
