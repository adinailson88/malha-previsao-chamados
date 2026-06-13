#!/usr/bin/env python3
"""Baixa do hub malha-ia os JSONs usados pelo Artigo 2."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


BASE_RAW_PADRAO = "https://raw.githubusercontent.com/adinailson88/malha-ia/main/dados"

ARQUIVOS = [
    "previsao_temporal.json",
    "previsao_detalhes.json",
    "previsao_incertezas.json",
    "previsao_diagnostico.json",
    "previsao_residuos.json",
    "previsao_qqplot.json",
    "previsao_validacao.json",
    "previsao_pressupostos.json",
    "previsao_por_categoria.json",
    "previsao_diebold_mariano.json",
    "previsao_crps_multicriterio.json",
    "previsao_granger.json",
    "contexto_sazonal.json",
    "filtros_disponiveis.json",
    "area_manutencao.json",
]


def baixar_json(url: str, timeout: int) -> object:
    req = Request(url, headers={"User-Agent": "malha-previsao-chamados/1.0"})
    with urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
    return json.loads(raw)


def main() -> int:
    parser = argparse.ArgumentParser(description="Sincroniza snapshots JSON a partir do hub malha-ia.")
    parser.add_argument("--base-raw", default=BASE_RAW_PADRAO)
    parser.add_argument("--saida", default="dados")
    parser.add_argument("--timeout", type=int, default=90)
    args = parser.parse_args()

    saida = Path(args.saida)
    saida.mkdir(parents=True, exist_ok=True)

    manifest = {
        "gerado_em_utc": datetime.now(timezone.utc).isoformat(),
        "hub_raw": args.base_raw.rstrip("/"),
        "arquivos": {},
        "falhas": {},
    }

    for nome in ARQUIVOS:
        url = f"{args.base_raw.rstrip('/')}/{nome}"
        try:
            dados = baixar_json(url, args.timeout)
            destino = saida / nome
            destino.write_text(json.dumps(dados, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
            linhas = len(dados) if isinstance(dados, list) else None
            manifest["arquivos"][nome] = {"url": url, "linhas": linhas}
            print(f"OK {nome}: {linhas if linhas is not None else 'json'}")
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
            manifest["falhas"][nome] = f"{type(exc).__name__}: {exc}"
            print(f"AVISO {nome}: {exc}")

    (saida / "manifest_hub.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    if manifest["falhas"]:
        raise SystemExit(f"Falhas ao baixar {len(manifest['falhas'])} arquivo(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
