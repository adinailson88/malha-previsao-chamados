#!/usr/bin/env python3
"""Le as abas COV_* da planilha CHAMADOS (via Apps Script) e grava CSVs em dados_externos/.

Uso:
    python scripts/sincronizar_covariaveis_planilha.py             # sincroniza as abas existentes
    python scripts/sincronizar_covariaveis_planilha.py --exigir    # falha se alguma aba obrigatoria faltar
    python scripts/sincronizar_covariaveis_planilha.py --selftest  # testa a validacao sem rede

O autor edita os dados somente na planilha; este script nao usa credenciais, pois emprega o
mesmo endpoint publico do Apps Script que o dashboard ja usa (parametro ?sheet=NOME_DA_ABA).
Cada CSV recebe a coluna origem=PLANILHA. Abas ausentes ou vazias sao registradas e puladas.

Formato de data aceito: AAAA-MM-DD (ou datetime ISO do Sheets, de que se usa apenas a data) e
DD/MM/AAAA (dia primeiro, formato brasileiro). Qualquer outro formato e rejeitado, para evitar
a inversao de dia e mes.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

RAIZ = Path(__file__).resolve().parents[1]
CONFIG = RAIZ / "dados_externos" / "config_covariaveis.json"
DESTINO = RAIZ / "dados_externos"
COLUNAS_DATA = {"inicio", "termino", "mes"}
COLUNAS_TEXTO = {"campus", "periodo"}


def normalizar(nome: str) -> str:
    s = unicodedata.normalize("NFKD", str(nome)).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def parse_data(valor) -> str:
    s = str(valor).strip()
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})(?:$|[T ])", s)
    if m:
        a, mes, d = map(int, m.groups())
    else:
        m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", s)
        if not m:
            raise ValueError(f"data em formato nao aceito: {s!r}")
        d, mes, a = map(int, m.groups())
    return date(a, mes, d).isoformat()  # levanta ValueError se invalida


def parse_numero(valor) -> float:
    if isinstance(valor, (int, float)):
        return float(valor)
    s = str(valor).strip().replace(" ", "").replace(" ", "")
    if re.fullmatch(r"\d{1,3}(\.\d{3})+", s):  # 2.500 em texto: milhar brasileiro
        s = s.replace(".", "")
    elif "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    return float(s)


def validar_aba(nome: str, dados: list[list], colunas: list[str]) -> list[dict]:
    """Converte lista de listas do Apps Script em linhas validadas; levanta ValueError."""
    if not dados or len(dados) < 2:
        return []
    cab = [normalizar(c) for c in dados[0]]
    faltam = [c for c in colunas if c not in cab]
    if faltam:
        raise ValueError(f"aba {nome}: colunas ausentes {faltam}; encontradas {cab}")
    idx = {c: cab.index(c) for c in colunas}
    linhas = []
    for n, linha in enumerate(dados[1:], start=2):
        if all(str(x).strip() == "" for x in linha):
            continue
        reg = {}
        for c in colunas:
            bruto = linha[idx[c]] if idx[c] < len(linha) else ""
            if c in COLUNAS_TEXTO:
                reg[c] = str(bruto).strip()
            elif c in COLUNAS_DATA:
                reg[c] = "" if str(bruto).strip() == "" else parse_data(bruto)
            else:
                if str(bruto).strip() == "":
                    reg[c] = ""
                else:
                    try:
                        reg[c] = parse_numero(bruto)
                    except ValueError:
                        raise ValueError(f"aba {nome}, linha {n}, coluna {c}: numero invalido {bruto!r}")
        linhas.append(reg)
    return linhas


def buscar_aba(url_base: str, nome: str, timeout: int = 75):
    req = Request(f"{url_base}?{urlencode({'sheet': nome})}", headers={"User-Agent": "malha-previsao-chamados"})
    with urlopen(req, timeout=timeout) as r:
        dados = json.loads(r.read().decode("utf-8"))
    if isinstance(dados, dict) and dados.get("error"):
        raise RuntimeError(str(dados["error"]))
    if not isinstance(dados, list):
        raise RuntimeError(f"retorno inesperado para {nome}: {type(dados).__name__}")
    return dados


def gravar(caminho: Path, colunas: list[str], linhas: list[dict]):
    with caminho.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[*colunas, "origem"])
        w.writeheader()
        for r in linhas:
            w.writerow({**r, "origem": "PLANILHA"})


def sincronizar(exigir: bool) -> int:
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))["planilha"]
    status = 0
    for aba, info in cfg["abas"].items():
        try:
            dados = buscar_aba(cfg["apps_script_url"], aba)
            linhas = validar_aba(aba, dados, info["colunas"])
        except Exception as e:
            print(f"[{aba}] ERRO: {e}", file=sys.stderr)
            status = 1
            continue
        if not linhas:
            print(f"[{aba}] ausente ou vazia; arquivo {info['arquivo']} mantido como esta")
            if exigir and not info.get("opcional"):
                status = 1
            continue
        gravar(DESTINO / info["arquivo"], info["colunas"], linhas)
        print(f"[{aba}] {len(linhas)} linhas -> {info['arquivo']}")
    return status


def selftest() -> int:
    ok = [["Ano", "Campus", "Estudantes", "Docentes", "Técnicos", "Terceirizados"],
          [2025, "Campus Jorge Amado", "2.500", 150, "70,0", 60], ["", "", "", "", "", ""]]
    r = validar_aba("COV_PESSOAS", ok, ["ano", "campus", "estudantes", "docentes", "tecnicos", "terceirizados"])
    assert len(r) == 1 and r[0]["estudantes"] == 2500.0 and r[0]["tecnicos"] == 70.0, r
    assert parse_data("2018-03-01T03:00:00.000Z") == "2018-03-01"
    assert parse_data("05/06/2024") == "2024-06-05"  # dia primeiro
    for ruim in ("2024/06/05", "06-05-2024", "abc"):
        try:
            parse_data(ruim)
        except ValueError:
            continue
        raise AssertionError(ruim)
    try:
        validar_aba("X", [["ano"], [1]], ["ano", "campus"])
    except ValueError:
        pass
    else:
        raise AssertionError("coluna ausente deveria falhar")
    print("selftest ok")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--exigir", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    sys.exit(selftest() if a.selftest else sincronizar(a.exigir))
