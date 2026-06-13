# AGENTS.md - Malha Previsao de Chamados

## Regime de trabalho

Atuar em modo tecnico, objetivo e verificavel. Quando houver insuficiencia de dados, declarar exatamente: `Informação insuficiente para verificar.`

## Fronteira do repositorio

Este repositorio corresponde ao Artigo 2 do ecossistema Malha IA: previsao de volume mensal de chamados de manutencao predial e estatisticas temporais associadas.

O repositorio `adinailson88/malha-ia` permanece como hub central dos dados. Este repositorio pode manter snapshots JSON/CSV derivados para reprodutibilidade, mas nao deve se tornar a fonte primaria da base `CHAMADOS`.

## Arquivos principais

1. `motor_previsao_chamados.py`: motor de series temporais para contagem de chamados/mes.
2. `dashboard.html`: painel especifico do Artigo 2.
3. `dados/*.json`: snapshots de leitura vindos do hub `malha-ia` ou do Apps Script.
4. `dados_csv/*.csv`: tabelas derivadas para auditoria e analise.
5. `scripts/baixar_dados_hub.py`: sincroniza snapshots publicos do hub.
6. `scripts/exportar_dados_json.py`: exporta abas PREVISAO_* do Apps Script quando necessario.
7. `.github/workflows/previsao_chamados_global.yml`: recalcula a previsao no Google Sheets.
8. `.github/workflows/atualizar-dados-hub.yml`: atualiza os snapshots deste repositorio a partir do hub.

## Limites

Nao trazer motores de classificacao, custos ou ODS para este repositorio, exceto quando houver dependencia documental explicitamente justificada.

Nao duplicar `dados/chamados.json` por padrao. A base bruta pertence ao hub `malha-ia`.

