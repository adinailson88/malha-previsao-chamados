# Protocolo de exploracao de dados - Zuur et al. (2010)

Este eixo aplica o protocolo de oito passos de Zuur, Ieno & Elphick (2010) aos snapshots publicos de previsao mensal de chamados.

Referencia: Zuur, A.F., Ieno, E.N. & Elphick, C.S. (2010). A protocol for data exploration to avoid common statistical problems. Methods in Ecology and Evolution, 1(1), 3-14. doi:10.1111/j.2041-210X.2009.00001.x.

Aplicacao no artigo: a serie mensal de contagens e explorada antes da inferencia preditiva. O diagnostico cobre outliers na resposta, homogeneidade de variancia, normalidade dos residuos, meses com zero chamado, colinearidade das covariaveis exogenas, relacoes temporais exploratorias, interacoes por categoria e independencia temporal por residuos e validacao rolling-origin.

Artefatos:

1. `scripts/gerar_protocolo_zuur.py`
2. `dados/protocolo_zuur.json`
3. `dados_csv/protocolo_zuur.csv`
4. Bloco "Protocolo Zuur" em `dashboard.html`

Diagnostico atual: os insumos principais ja estao publicados neste repositorio. A mudanca minima foi materializar o resumo transversal e exibi-lo no dashboard.
