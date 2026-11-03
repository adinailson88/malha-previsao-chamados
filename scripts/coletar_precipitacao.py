#!/usr/bin/env python3
"""Coleta precipitacao diaria por municipio e agrega por mes.

Uso:
    python scripts/coletar_precipitacao.py            # baixa e grava o CSV
    python scripts/coletar_precipitacao.py --selftest # testa a agregacao sem rede

Saida: dados_externos/precipitacao_mensal_por_campus.csv
Colunas: mes, campus, municipio, precip_media_diaria_mm, precip_total_mm,
         dias_validos, dias_no_mes, mes_completo, fonte

A media mensal (mm/dia) e a variavel principal, conforme definicao do autor; a
soma mensal (mm) e gravada para comparacao. Meses incompletos (mes corrente) ou
com menos de 80% de dias validos ficam com valor vazio.
"""

from __future__ import annotations

import argparse
import calendar
import csv
import json
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

RAIZ = Path(__file__).resolve().parents[1]
CONFIG = RAIZ / "dados_externos" / "config_covariaveis.json"
SAIDA = RAIZ / "dados_externos" / "precipitacao_mensal_por_campus.csv"
CAMPOS = ["mes", "campus", "municipio", "precip_media_diaria_mm", "precip_total_mm",
          "dias_validos", "dias_no_mes", "mes_completo", "fonte"]


def baixar_diario(lat: float, lon: float, inicio: str, fim: str, cfg: dict, tentativas: int = 4):
    """Devolve (datas, valores) diarios; valores podem ser None."""
    params = urlencode({
        "latitude": lat, "longitude": lon, "start_date": inicio, "end_date": fim,
        "daily": cfg["variavel_diaria"], "timezone": cfg["fuso"],
    })
    url = f"{cfg['url']}?{params}"
    ultimo = None
    for i in range(1, tentativas + 1):
        try:
            with urlopen(Request(url, headers={"User-Agent": "malha-previsao-chamados"}), timeout=60) as r:
                dados = json.load(r)
            diario = dados["daily"]
            return diario["time"], diario[cfg["variavel_diaria"]]
        except Exception as e:  # rede, JSON ou chave ausente
            ultimo = e
            time.sleep(2 ** i)
    raise RuntimeError(f"Falha ao baixar {url}: {ultimo}")


def agregar_mensal(datas, valores, hoje: date, fracao_minima: float):
    """Agrega series diarias em dict {(ano, mes): (media, total, validos, dias_no_mes, completo)}."""
    por_mes: dict[tuple[int, int], list] = {}
    for d, v in zip(datas, valores):
        dt = datetime.strptime(d, "%Y-%m-%d").date()
        por_mes.setdefault((dt.year, dt.month), []).append(v)
    saida = {}
    for (ano, mes), vals in sorted(por_mes.items()):
        dias_mes = calendar.monthrange(ano, mes)[1]
        validos = [x for x in vals if x is not None]
        ultimo_dia = date(ano, mes, dias_mes)
        completo = ultimo_dia < hoje and len(vals) == dias_mes
        if completo and len(validos) >= fracao_minima * dias_mes:
            total = sum(validos)
            media = total / len(validos)
        else:
            media = total = None
        saida[(ano, mes)] = (media, total, len(validos), dias_mes, completo)
    return saida


def executar(config_path: Path = CONFIG, saida: Path = SAIDA) -> int:
    cfg_all = json.loads(config_path.read_text(encoding="utf-8"))
    cfg = cfg_all["precipitacao"]
    hoje = date.today()
    fim = (hoje - timedelta(days=5)).isoformat()  # reanalise tem defasagem de dias
    linhas = []
    for campus, info in cfg_all["campi"].items():
        datas, vals = baixar_diario(info["lat"], info["lon"], cfg["inicio"], fim, cfg)
        for (ano, mes), (media, total, val, dias, comp) in agregar_mensal(
                datas, vals, hoje, cfg["fracao_minima_dias_validos"]).items():
            linhas.append({
                "mes": f"{ano}-{mes:02d}-01", "campus": campus, "municipio": info["municipio"],
                "precip_media_diaria_mm": "" if media is None else round(media, 3),
                "precip_total_mm": "" if total is None else round(total, 1),
                "dias_validos": val, "dias_no_mes": dias, "mes_completo": int(comp),
                "fonte": cfg["fonte"],
            })
    saida.parent.mkdir(parents=True, exist_ok=True)
    with saida.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        w.writeheader()
        w.writerows(linhas)
    print(f"{len(linhas)} linhas gravadas em {saida}")
    return 0


def selftest() -> int:
    datas = [(date(2024, 1, 1) + timedelta(days=i)).isoformat() for i in range(60)]  # jan e fev/2024
    vals = [1.0] * 31 + [2.0] * 29
    r = agregar_mensal(datas, vals, date(2024, 6, 1), 0.8)
    assert r[(2024, 1)][0] == 1.0 and r[(2024, 1)][1] == 31.0, r
    assert r[(2024, 2)][0] == 2.0 and r[(2024, 2)][1] == 58.0, r
    vals2 = vals[:]
    for i in range(10):
        vals2[i] = None  # 21 de 31 dias validos em janeiro (67%) -> descartado
    r2 = agregar_mensal(datas, vals2, date(2024, 6, 1), 0.8)
    assert r2[(2024, 1)][0] is None and r2[(2024, 2)][0] == 2.0, r2
    r3 = agregar_mensal(datas, vals, date(2024, 2, 15), 0.8)  # fevereiro ainda em curso
    assert r3[(2024, 2)][0] is None and r3[(2024, 2)][4] is False, r3
    print("selftest ok")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    sys.exit(selftest() if a.selftest else executar())
