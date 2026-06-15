# Malha Previsao de Chamados

Repositorio do Artigo 2 do ecossistema Malha IA: previsao temporal de volume de chamados de manutencao predial e estatisticas associadas.

Repositorio-hub de dados: [adinailson88/malha-ia](https://github.com/adinailson88/malha-ia)  
Dashboard previsto: `https://adinailson88.github.io/malha-previsao-chamados/`

## Escopo

Este repositorio separa o eixo de previsao de chamados do repositorio central `malha-ia`. O objetivo e manter um produto tecnico-cientifico especifico para o artigo sobre demanda mensal de manutencao, comparacao de modelos temporais, validacao rolling-origin, incerteza e estatisticas temporais.

Ficam fora deste repositorio:

1. Classificacao de chamados.
2. Previsao de custos.
3. Painel ODS/ESG.
4. Atualizacao reversa GLPI.
5. Base bruta completa `CHAMADOS` como fonte primaria.

## Componentes

1. `motor_previsao_chamados.py`: executa os modelos ARIMA, SARIMAX, Holt-Winters, Prophet/UC, Gradient Boosting, LSTM Forecast, Theta e Ensemble.
2. `dashboard.html`: dashboard especifico de previsao temporal de chamados.
3. `dados/*.json`: snapshots de resultados pertinentes ao Artigo 2.
4. `dados_csv/*.csv`: versoes tabulares derivadas dos JSONs.
5. `scripts/baixar_dados_hub.py`: baixa do hub `malha-ia` os JSONs publicos usados pelo dashboard.
6. `scripts/exportar_dados_json.py`: alternativa manual para exportar diretamente do Apps Script/Google Sheets, quando necessario.
7. `.github/workflows/previsao_chamados_global.yml`: workflow de compatibilidade que sincroniza as previsoes publicas do hub.
8. `.github/workflows/atualizar-dados-hub.yml`: workflow periodico para atualizar snapshots a partir do hub.

## Contrato com o hub de dados

O `malha-ia` e a fonte central dos dados. Este repositorio consome os seguintes arquivos do hub:

1. `previsao_temporal.json`
2. `previsao_detalhes.json`
3. `previsao_incertezas.json`
4. `previsao_diagnostico.json`
5. `previsao_residuos.json`
6. `previsao_qqplot.json`
7. `previsao_validacao.json`
8. `previsao_pressupostos.json`
9. `previsao_por_categoria.json`
10. `previsao_diebold_mariano.json`
11. `previsao_crps_multicriterio.json`
12. `previsao_granger.json`
13. `contexto_sazonal.json`
14. `filtros_disponiveis.json`
15. `area_manutencao.json`

## Execucao local

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r execucao_offline\requirements.txt
```

Validacao sintatica:

```powershell
python -m py_compile motor_previsao_chamados.py
python -m py_compile scripts\baixar_dados_hub.py
python -m py_compile scripts\exportar_dados_json.py
python -m py_compile scripts\exportar_dados_csv.py
```

Atualizar snapshots a partir do hub:

```powershell
python scripts\baixar_dados_hub.py
python scripts\exportar_dados_csv.py
```

Recalculo autenticado:

O recalculo completo contra Google Sheets fica centralizado no repositorio `malha-ia`, que publica os snapshots em `dados/*.json`. Este repositorio nao precisa de `AUTENTICACAO_GOOGLE` para atualizar o dashboard.

## Dados e reprodutibilidade

Os arquivos em `dados/` sao snapshots derivados. Para uma analise final de artigo, registre a data de sincronizacao do hub, o commit do hub `malha-ia`, o commit deste repositorio e o conteudo de `dados/manifest_hub.json`.

## Licenca

Informação insuficiente para verificar.
