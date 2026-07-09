#!/usr/bin/env python3
"""Baixa do hub malha-ia os JSONs usados pelo Artigo 2."""

from __future__ import annotations

import argparse
import json
import time
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


def baixar_json(url: str, timeout: int, tentativas: int = 5) -> object:
    req = Request(url, headers={"User-Agent": "malha-previsao-chamados/1.0"})
    ultima_excecao: Exception | None = None
    for tentativa in range(1, tentativas + 1):
        try:
            with urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8")
            return json.loads(raw)
        except HTTPError as exc:
            ultima_excecao = exc
            if exc.code not in (429, 500, 502, 503, 504) or tentativa == tentativas:
                raise
        except (URLError, TimeoutError) as exc:
            ultima_excecao = exc
            if tentativa == tentativas:
                raise
        espera = min(60, 2 ** tentativa)
        print(f"AVISO tentativa {tentativa}/{tentativas} falhou para {url}: {ultima_excecao}. Nova tentativa em {espera}s.")
        time.sleep(espera)
    raise RuntimeError(f"Falha ao baixar {url}: {ultima_excecao}")


def falha_transitoria(exc: Exception) -> bool:
    if isinstance(exc, HTTPError):
        return exc.code in (429, 500, 502, 503, 504)
    return isinstance(exc, (URLError, TimeoutError))


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
            destino = saida / nome
            manifest["falhas"][nome] = f"{type(exc).__name__}: {exc}"
            if falha_transitoria(exc) and destino.exists():
                try:
                    dados_cache = json.loads(destino.read_text(encoding="utf-8"))
                    linhas = len(dados_cache) if isinstance(dados_cache, list) else None
                    manifest.setdefault("falhas_toleradas", {})[nome] = manifest["falhas"].pop(nome)
                    manifest["arquivos"][nome] = {
                        "url": url,
                        "linhas": linhas,
                        "origem": "cache_local_por_falha_transitoria",
                    }
                    print(f"AVISO {nome}: {exc}; mantido snapshot local existente.")
                    continue
                except (json.JSONDecodeError, OSError):
                    pass
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
