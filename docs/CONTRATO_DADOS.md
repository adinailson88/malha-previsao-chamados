# Contrato de dados - Artigo 2

## Fonte central

O repositorio `adinailson88/malha-ia` permanece como hub central dos dados. Este repositorio usa snapshots de leitura para dashboard, auditoria e reproducibilidade do artigo.

## Abas/arquivos pertinentes

| Aba no Google Sheets | Arquivo JSON | Papel no artigo |
|---|---|---|
| PREVISAO_TEMPORAL | `dados/previsao_temporal.json` | Serie historica, backtest e forecast por modelo |
| PREVISAO_DETALHES | `dados/previsao_detalhes.json` | Parametros, erro padrao e p-valores |
| PREVISAO_INCERTEZAS | `dados/previsao_incertezas.json` | Intervalos bootstrap |
| PREVISAO_DIAGNOSTICO | `dados/previsao_diagnostico.json` | Diagnosticos por modelo |
| PREVISAO_RESIDUOS | `dados/previsao_residuos.json` | Residuos por modelo |
| PREVISAO_QQPLOT | `dados/previsao_qqplot.json` | Pontos para Q-Q plot |
| PREVISAO_VALIDACAO | `dados/previsao_validacao.json` | Validacao rolling-origin |
| PREVISAO_PRESSUPOSTOS | `dados/previsao_pressupostos.json` | Testes de pressupostos |
| PREVISAO_POR_CATEGORIA | `dados/previsao_por_categoria.json` | Resumo por categoria |
| PREVISAO_DIEBOLD_MARIANO | `dados/previsao_diebold_mariano.json` | Comparacao estatistica entre modelos |
| PREVISAO_CRPS_MULTICRITERIO | `dados/previsao_crps_multicriterio.json` | Selecao multicriterio |
| PREVISAO_GRANGER | `dados/previsao_granger.json` | Testes de causalidade temporal |
| CONTEXTO_SAZONAL | `dados/contexto_sazonal.json` | Variaveis exogenas sazonais |
| FILTROS_DISPONIVEIS | `dados/filtros_disponiveis.json` | Filtros de campus/tipo/categoria |
| Area Manutencao | `dados/area_manutencao.json` | Area construida e area total por ano |
| Artefato local | `dados/protocolo_zuur.json` | Diagnostico transversal de exploracao de dados segundo Zuur et al. (2010) |
| Artefato local | `dados/analise_gam.json` | Adequacao de GAM como benchmark explicavel para contagens |

## Regra de fronteira

`CHAMADOS` nao deve ser duplicado aqui como fonte primaria. Quando for necessario auditar a base bruta, usar o hub `malha-ia` ou a planilha institucional vigente.
