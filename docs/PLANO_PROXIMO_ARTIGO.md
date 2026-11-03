# Plano do próximo artigo: diagnóstico e decisão entre previsão de chamados (A) e aprendizado contínuo da classificação (B)

Documento de trabalho elaborado em 03/11/2026, construído por etapas e salvo a cada etapa. Todas as afirmações abaixo foram obtidas por leitura direta dos repositórios `adinailson88/malha-previsao-chamados` (commit `22cae38`), `adinailson88/malha-ia` (commit `526abb8`) e `adinailson88/malha-previsao-custos` (commit `0b5d0f1`), clonados em 03/11/2026. Quando uma informação não pôde ser lida, consta "não foi possível verificar". O repositório `classificacao-chamados` e os resultados da simulação do candidato B foram informados no enunciado e não foram relidos nesta etapa.

## Etapa 1. Inventário dos repositórios

### 1.1 Achado central do inventário: a série mensal publicada não corresponde aos dados-fonte

O arquivo `dados/previsao_temporal.json` do hub e deste repositório contém apenas `[[""]]` desde o commit `d364655` (02/11/2026); a aba `PREVISAO_TEMPORAL` do `manifest.json` do hub registra 0 linhas, e o mesmo ocorre com `previsao_detalhes.json`. A última versão com conteúdo (commit `ddeff7d`, atualização de 30/10/2026, 178 linhas) foi recuperada do histórico e comparada com a série mensal reconstruída a partir de `malha-ia/dados/chamados.json`.

A comparação mostrou que a coluna "Quantidade Real" da planilha reproduz exatamente (RMSE = 0,0 para 2018-01 em diante) a contagem mensal obtida quando se trocam dia e mês em todas as datas com dia menor ou igual a 12. A causa é verificável no código: `extrair_serie_temporal` (`motor_previsao_chamados.py`, linhas 646 a 700) tenta os formatos `%d/%m/%Y %H:%M:%S` e `%d/%m/%Y` e, ao falhar, recorre a `pd.to_datetime(..., dayfirst=True)`. Com datas em formato ISO (`AAAA-MM-DD HH:MM`, como em `chamados.json`), esse último recurso inverte dia e mês quando o dia é menor ou igual a 12. O comportamento foi reproduzido com pandas 3.0.5: `2026-05-06 10:51` resulta em `2026-06-05`, enquanto `2026-05-29 10:51` permanece correto. A fonte exata lida pelo motor (texto da planilha) não pôde ser inspecionada, mas a coincidência exata dos valores sustenta que as células chegam ao motor em formato ISO.

Consequências comprovadas nos valores publicados: o mês de maio de 2026 aparece com 280 chamados na série do motor contra 146 na contagem correta, e a soma dos 12 meses de holdout usada para eleger o vencedor (Prophet/UC, RMSE = 25,03) contém esse ponto espúrio. Todos os resultados derivados da série (ARIMA, SARIMAX, Holt-Winters, Theta, Gradient Boosting, ensemble, bootstrap, CRPS, Diebold-Mariano, Granger, Zuur, GAM) devem ser tratados como não confiáveis até a reexecução com a série corrigida. O mesmo padrão `dayfirst=True` existe em `motor_previsao_custos.py` (linhas 555 e 604 da cópia do repositório de custos) e em `motor_ods.py` (linhas 357 e 358), de modo que a revisão se estende ao Artigo 3 e ao eixo ODS; o efeito sobre esses eixos não foi quantificado.

### 1.2 Dados-fonte no hub

O arquivo `malha-ia/dados/chamados.json` (11,8 MB) contém 48.418 linhas de dados mais cabeçalho, das quais 33.838 (69,9%) estão totalmente vazias; as 14.580 linhas preenchidas cobrem de 2015-06 a 2026-10 (137 meses consecutivos, sem mês ausente). O cabeçalho possui 30 colunas, 12 delas sem nome. A distribuição anual de aberturas é: 2015 (28), 2016 (172), 2017 (533), 2018 (1.741), 2019 (2.085), 2020 (989), 2021 (1.182), 2022 (1.393), 2023 (1.633), 2024 (1.596), 2025 (1.662) e 2026 até outubro (1.566). Média mensal de 106,4 chamados, desvio-padrão populacional de 59,4, mínimo 1, máximo 260. Os campi são Sosígenes Costa (4.245), Jorge Amado (3.946), Paulo Freire (3.924), Reitoria (2.454) e Jequié (11).

### 1.3 Inventário por repositório

| Item | `malha-previsao-chamados` | `malha-ia` (hub) | `malha-previsao-custos` |
|---|---|---|---|
| Modelos | `motor_previsao_chamados.py` (4.424 linhas, 55 funções): ARIMA/auto-ARIMA, SARIMAX-12 e SARIMAX-6, Holt-Winters, Prophet com fallback para UnobservedComponents, Theta, Gradient Boosting direto (H=12), LSTM, ensemble ponderado por 1/RMSE, além de ablação, SHAP, STL, periodograma e ACF/PACF | `motor_previsao_chamados.py` (4.453 linhas), `motor_previsao_custos.py` (4.725), `motor_previsao_filtros.py` (5.180), `motor_classificacao_v1.py` (1.364), `motor_ods.py` (547) | `motor_previsao_custos.py` (cópia, difere do hub) |
| Dados | 19 JSON em `dados/` e 11 CSV em `dados_csv/`; `chamados.json` ausente, conforme AGENTS.md | 401 arquivos em `dados/` (24 MB), dos quais 387 com prefixo `previsao`; `dados_csv/` com 20 MB | 11 JSON de custo e contexto em `dados/` e 9 CSV |
| Resultados | Último snapshot válido de 30/10/2026: RMSE de holdout (12 meses) de 25,03 para Prophet/UC, 39,6 a 57,2 para os demais; tabelas de Diebold-Mariano, CRPS multicritério, Granger, diagnóstico de resíduos e incertezas bootstrap | Os mesmos arquivos, mais os recortes por filtro e por custo (387 arquivos com prefixo `previsao`) | Série de custos em R$ com RMSE de holdout do melhor modelo (LSTM) de 84.122,04 e R² negativo em todos os modelos com valor numérico (Gradient Boosting aparece como NaN) |
| Validação | `previsao_validacao.json`: rolling-origin com 3 dobras de 12 meses para 6 modelos (ARIMA, SARIMAX-12, Holt-Winters, Theta, Naive sazonal, Drift); Diebold-Mariano com 141 pares (128 para Gradient Boosting) | Idem | Rolling-origin com 3 dobras para custos |
| Texto | `README.md`, `docs/CONTRATO_DADOS.md`, `docs/METODOLOGIA_GAM.md`, `docs/METODOLOGIA_PROTOCOLO_ZUUR.md`, `Referência Bibliográfica - Drive/README.md` (47 referências, 26 com resumo); não existe rascunho de artigo | `README.md`, `CHANGELOG.md`, docs de particionamento, inventário, secrets, portal e `docs/instrucoes_ia/`; sem rascunho de artigo | `README.md`, 4 documentos em `docs/` (inclui `PARTICIONAMENTO_REPOSITORIOS_E_ARTIGOS.md`) |
| Workflows | `atualizar-dados-hub.yml` (cron a cada 30 min), `previsao_chamados_global.yml` (diário 06:30 UTC, apenas baixa JSON do hub), `pages.yml` | 13 workflows, incluindo `previsao_chamados_global.yml` (diário, executa o motor com o secret `AUTENTICACAO_GOOGLE`) | `atualizar-dados-hub.yml`, `previsao_custo_global.yml`, `pages.yml` |

### 1.4 Modelos já rodados e problemas de integridade observados no último snapshot válido

1. O LSTM aparece como falho no único snapshot completo recuperado ("TensorFlow indisponível"), embora `execucao_offline/requirements.txt` liste `tensorflow==2.17.0`; o workflow deste repositório instala apenas `pandas` e não executa o motor, de modo que o LSTM só poderia rodar no hub.
2. O teste ADF aparece como `1899-12-27T08:45:35.200Z` e o KPSS como `1899-12-30T21:14:05.920Z`, assim como o MAE do SARIMAX-6 (`1900-02-10T08:52:04.000Z`): números convertidos em datas pelo Google Sheets e exportados como texto de data. Os valores originais não são recuperáveis a partir do JSON.
3. O RMSE do mesmo modelo difere entre tabelas do mesmo snapshot (SARIMAX-12: 40,82 no holdout, 41,48 em `previsao_crps_multicriterio.json`, 29,33 como média das dobras em `previsao_validacao.json`; Prophet/UC: 25,03 contra 24,25), sem documentação do motivo.
4. `previsao_por_categoria.json` registra "In-sample" como modelo vencedor e RMSE igual a 0 para as categorias, ou seja, não há avaliação fora da amostra por categoria.
5. A série do motor inicia em 2015-01 com zeros até 2015-05, anterior ao primeiro chamado real (2015-06), e inclui o ramp-up de adoção do sistema (2015 a 2017) e a queda de 2020, o que sugere quebras estruturais não tratadas.
6. A validação rolling-origin usa apenas 3 dobras, todas com o rótulo automático "Alta variância" para cinco dos seis modelos.
7. Os arquivos `previsao_custo_*.json` do repositório de custos estão com codificação duplamente convertida (por exemplo "PerÃ­odo"); os JSON deste repositório estão íntegros em UTF-8. O código-fonte do motor de chamados também contém texto corrompido (586 linhas com "Ã"), que afeta apenas mensagens e comentários.
8. `dados/analise_gam.json` e `dados/protocolo_zuur.json`, gerados localmente, derivam de `previsao_temporal.json` (137 observações, média 99,45) e portanto herdam o defeito de datas; o protocolo de Zuur foi gerado em 18/06/2026 e a análise GAM não traz data verificável.

### 1.5 Duplicações entre repositórios

1. `motor_previsao_chamados.py` existe nos dois repositórios com divergência: o hub possui a função `_conectar_planilha` com retry e backoff para erros 429/5xx do Google (cerca de 30 linhas a mais), ausente nesta cópia. Esta cópia não é executada por nenhum workflow local, portanto serve apenas como documentação do artigo e pode estar defasada em relação ao que de fato gera os resultados.
2. `contexto_sazonal.json`, `area_manutencao.json` e `filtros_disponiveis.json` são idênticos entre este repositório e o de custos, e `analise_gam.json`, `protocolo_zuur.json`, `scripts/` (5 scripts) e `docs/METODOLOGIA_*` existem nos dois com pequenas diferenças de conteúdo.
3. `CITATION.cff` é idêntico entre os três repositórios, com título "Malha IA" e URLs apontando para `adinailson88-jpg`, conta diferente da usada em todos os demais links (`adinailson88`).
4. `Referência Bibliográfica - Drive/README.md` existe nos três repositórios com conteúdos diferentes (73,5 KB neste).
5. O hub mantém 387 arquivos `previsao_*` (incluindo recortes de custo por categoria), enquanto o repositório de custos mantém apenas os quatro arquivos globais de custo; a equivalência de conteúdo entre as duas cópias não foi verificada.
6. Os workflows `atualizar-dados-hub.yml` e `previsao_chamados_global.yml` deste repositório executam os mesmos passos (`baixar_dados_hub.py`, `exportar_dados_csv.py`, commit), diferindo apenas no gatilho.

### 1.6 Itens desatualizados

1. `README.md` informa licença como "Informação insuficiente para verificar" e o `CITATION.cff` usa `license: NOASSERTION`; não há arquivo `LICENSE`.
2. `CITATION.cff` aponta para `adinailson88-jpg/malha-ia` e descreve o projeto inteiro, não o Artigo 2.
3. `dados/previsao_validacao.json` traz 3 dobras e `previsao_incertezas.json` (106 KB) e `previsao_residuos.json` (44 KB) permanecem de execuções anteriores, sem garantia de correspondência com o `previsao_temporal.json` atual (vazio).
4. O `manifest_hub.json` registra a sincronização de 03/11/2026 03:34 UTC, mas o hub gerou o `manifest.json` em 02/11/2026 13:54 UTC; a defasagem entre os dois manifestos deve ser considerada ao registrar o commit do hub usado em cada resultado.
5. O `.gitignore` referencia `docs/artigo/`, pasta inexistente; não é defeito, apenas indica que o texto do artigo reside fora do repositório (Drive).
6. O clone local é raso (50 commits, todos de `github-actions[bot]` entre 25/10 e 03/11/2026), de modo que o histórico anterior a 25/10 e a autoria humana não puderam ser verificados.

### 1.7 Itens que não foi possível verificar

1. Conteúdo real da planilha `CHAMADOS` (Google Sheets) e formato textual das datas lidas pelo `gspread`.
2. Logs e status das execuções de GitHub Actions do hub, inclusive o motivo do esvaziamento de `PREVISAO_TEMPORAL` em 02/11/2026.
3. Repositório `classificacao-chamados` (não relido nesta etapa; os números do candidato B foram assumidos conforme o enunciado).
4. Conteúdo dos repositórios `malha-previsao-filtros`, `malha-ods-esg` e `malha-estatisticas-associadas`; apenas o motor de filtros foi lido, na cópia do hub.
5. Dados de precipitação e período letivo usados como exógenas além do que está em `contexto_sazonal.json` (fonte primária da precipitação não identificada no código lido).

### 1.8 Candidatos a limpeza e reorganização (somente planejamento; nada foi alterado ou removido)

A pedido do autor, o repositório deve ficar organizado e o material sem função deve ser listado para eventual remoção. A lista abaixo separa o que pode ser apagado do que deve ser movido ou corrigido, e a execução depende de aprovação explícita.

| Item | Ação proposta | Justificativa |
|---|---|---|
| `dados/previsao_temporal.json` e `dados/previsao_detalhes.json` com `[[""]]` | Não apagar; restaurar a última versão válida após a correção da série e registrar o defeito | Arquivos exigidos pelo dashboard e pelo contrato de dados |
| `.github/workflows/previsao_chamados_global.yml` | Remover (ou fundir com `atualizar-dados-hub.yml`) | Duplica os passos do outro workflow e o nome sugere execução do motor, o que não ocorre |
| `.github/workflows/atualizar-dados-hub.yml` (cron a cada 30 min) | Reduzir a frequência (por exemplo, diária) | 50 commits de bot em 10 dias poluem o histórico e disparam o `pages.yml` repetidamente |
| `Referência Bibliográfica - Drive/` | Mover para `docs/referencias/README.md` (nome sem acento e sem espaços) | O diretório é publicado integralmente no GitHub Pages (`path: '.'` em `pages.yml`) e o nome dificulta links |
| `pages.yml` (publica a raiz inteira, inclusive o motor de 200 KB e os dados brutos) | Publicar apenas `index.html`, `dashboard.html` e `dados/` | Reduz exposição e tamanho do site |
| `motor_previsao_chamados.py` (cópia divergente do hub) | Manter, mas sincronizar com o hub e corrigir o parse de datas; avaliar mover para `src/` | Evita divergência silenciosa entre código documentado e código executado |
| `CITATION.cff` | Corrigir URLs e título para o Artigo 2 | Aponta para conta diferente e escopo errado |
| `dados_csv/` | Manter | Derivação documentada em AGENTS.md para auditoria |
| `execucao_offline/requirements.txt` | Reduzir ao necessário ou separar `requirements-motor.txt` de `requirements-sync.txt` | O workflow instala apenas `pandas`; o arquivo atual mistura dependências do motor completo |
| `dados/chamados.json` no hub (69,9% de linhas vazias, 11,8 MB) | Propor ao hub a poda das linhas vazias (fora do escopo deste repositório) | Reduz tamanho e risco de erro de leitura |
| Material de classificação, ODS e custos | Nada a apagar aqui; já ausente | Conforme limites do AGENTS.md |

Estado: etapa 1 concluída
