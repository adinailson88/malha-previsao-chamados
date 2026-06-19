# Camada GAM na previsao de chamados

Este repositorio passa a documentar GAM como camada explicavel e benchmark estatistico para a serie mensal de quantidade de chamados. A decisao metodologica e nao substituir ARIMA, SARIMAX, Holt-Winters, Prophet/UC, GradientBoosting, LSTM_Forecast, Theta ou Ensemble sem validacao temporal comparativa.

## Papel metodologico

O uso adequado e ajustar um modelo aditivo generalizado para contagens, preferencialmente Negative Binomial quando houver sobredispersao ou Poisson quando a variancia for compativel com a media. Os termos recomendados sao uma suavizacao de tendencia temporal, uma suavizacao ciclica de mes e, quando houver alinhamento temporal, covariaveis institucionais ja publicadas em `contexto_sazonal.json`.

## Artefatos

- `scripts/gerar_analise_gam.py`: gera o diagnostico local de adequacao.
- `dados/analise_gam.json`: contrato consumido pelo dashboard.
- `dados_csv/analise_gam.csv`: resumo tabular para auditoria e artigo.

## Criterio de leitura

O artefato atual indica se ha suporte minimo para usar GAM como benchmark explicavel. Ele nao declara ganho empirico. Antes de afirmar superioridade, e necessario executar validacao rolling-origin e comparar MAE, RMSE, MAPE e cobertura de intervalos contra os modelos ja publicados.

O script tambem gera um `benchmark_aditivo` operacional sem dependencia nova, baseado em tendencia e sazonalidade Fourier sobre `log(y+0.5)`. Esse benchmark serve para triagem e comparacao inicial; o ajuste GAM completo com GLM/Negative Binomial continua dependendo de ambiente estatistico com `statsmodels`/`scipy`.

Quando o benchmark GAM nao tiver sido executado, a conclusao deve ser: Informação insuficiente para verificar.
