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

## Etapa 2. Diagnóstico científico do candidato A (previsão de chamados)

### 2.1 Pergunta de pesquisa

Formulação proposta, ajustável pelo autor: em uma série mensal de chamados de manutenção predial de uma universidade federal multicampi, com regime de demanda instável (adoção do sistema, interrupção em 2020, mistura de manutenção preventiva programada e corretiva), qual família de modelos produz previsões a 1 a 12 meses com erro e calibração de incerteza superiores a comparadores simples, sob validação rolling-origin com testes formais de acurácia preditiva, e qual é o ganho operacional de usar esses intervalos para dimensionar equipe e contratos? A pergunta é de natureza comparativa e aplicada, e a hipótese nula relevante é que modelos sofisticados não superam a média móvel ou a média histórica, como indicado pela literatura de competições (itens 6, 7 e 8 da seção 2.8).

### 2.2 Séries disponíveis

Todos os números desta seção foram calculados nesta etapa a partir de `malha-ia/dados/chamados.json` (commit `526abb8`), com a data de abertura interpretada no formato ISO, sem inversão de dia e mês. Trata-se de reconstrução própria para diagnóstico; não substitui a execução do motor.

1. Série global mensal: 2015-06 a 2026-09 (136 meses completos; outubro de 2026 está incompleto e é excluído pela própria regra do motor), 14.391 chamados no intervalo e 14.580 até 2026-10. A partir de 2018-01 (n = 105) a média é 130,1 chamados/mês, variância 1.843, razão variância/média de 14,2 (sobredispersão em relação a Poisson), coeficiente de variação 0,33, ACF lag 1 de 0,65 e ACF lag 12 de -0,02. A partir de 2021-01 (n = 69) a média é 128,2, razão variância/média de 10,7, ACF lag 1 de 0,49 e ACF lag 12 de -0,04. Não há mês com contagem zero após 2018.
2. Regimes: 2015 a 2017 correspondem à adoção do sistema (28, 172 e 533 chamados/ano), 2018 e 2019 ao pico (1.741 e 2.085), 2020 a uma queda (989), seguida de recuperação gradual (1.182 em 2021 a 1.662 em 2025). O intervalo estável utilizável para modelagem é de 2021 em diante, com 69 meses; o intervalo desde 2018 tem 105 meses, mas contém a quebra de 2020.
3. Perfil sazonal médio de 2021 a 2025, janeiro a dezembro: 95, 110, 107, 131, 129, 139, 129, 136, 109, 142, 143 e 124. Há amplitude moderada (janeiro e fevereiro baixos, segundo semestre alto), porém a autocorrelação sazonal de lag 12 é praticamente nula, o que indica sazonalidade fraca e instável entre anos.
4. Por tipo de categoria (`CATEGORIA COMPLETA`): Manutenção Preventiva 4.864 chamados (33,4%), Estrutura Predial 2.972, Elétrica 1.937, Climatização 1.735, Hidrossanitária 1.394, TI/Dados/Rede 480, Instalação de Acessórios e Mobiliário 406, Outros 293. A série preventiva (média de 45,2/mês desde 2018, razão variância/média de 14,4) é gerada por programação contratual e não por demanda espontânea, o que contamina a série agregada.
5. Por campus: Sosígenes Costa (4.245), Jorge Amado (3.946), Paulo Freire (3.924), Reitoria (2.454) e Jequié (11, com 64 zeros em 69 meses, inadequado para modelagem). Médias mensais desde 2021: 37,2, 36,5, 34,8 e 19,4 para os quatro principais.
6. Sem preditores observados além de `contexto_sazonal.json` (precipitação, período letivo) e áreas construída e total, que são constantes (a Granger-causalidade falhou por coluna constante no snapshot válido). A origem da série de precipitação não foi identificada no código lido.

Efeito do defeito de datas sobre as propriedades da série: com a inversão de dia e mês, o desvio absoluto médio mensal entre as duas séries desde 2018 é de 30,2 chamados (máximo 221), a razão variância/média desde 2021 sobe de 10,7 para 23,1, o ACF lag 12 sobe de -0,04 para 0,66 e o perfil sazonal apresenta um pico artificial em maio (236 em média) e um vale em dezembro (79). Esse pico e esse vale são justamente o que o artefato `analise_gam.json` registra como "mês de maior média = 5 e menor = 12". A sazonalidade anual forte que sustentaria SARIMAX com período 12, Holt-Winters sazonal e variáveis exógenas é, portanto, em grande parte um artefato do parse de datas. A hipótese de sazonalidade deve ser testada novamente na série corrigida.

### 2.3 Modelos já rodados

Último snapshot válido (30/10/2026), todos sobre a série com datas invertidas: ARIMA(2,1,3), SARIMAX(0,1,2)(0,1,1)[12] com exógenas, SARIMAX(0,1,2)(1,1,1)[6], Holt-Winters (α = 0,514; β = 0,011; γ = 0,009), UnobservedComponents (nomeado "Prophet/UC", tendência local linear, sazonalidade 12, exógenas), Theta (período 12), Gradient Boosting direto (H = 12; 200 árvores; profundidade 3; taxa 0,05), ensemble por 1/RMSE e LSTM (falhou). Para a validação rolling-origin constam ainda Naive sazonal e Drift. O código também prevê ablação, SHAP, STL, periodograma, ACF/PACF, block bootstrap de resíduos (biblioteca `arch`) e CRPS empírico. O único modelo sem exógenas é o ARIMA; os demais usam precipitação e período letivo, cuja contribuição foi nula no SARIMAX-12 (coeficientes com p entre 0,85 e 1,00 no snapshot válido), segundo `previsao_detalhes.json` da versão `ddeff7d`.

### 2.4 Métricas, validação temporal e comparadores atuais

1. Métricas calculadas: MAE, RMSE, R², MAPE, AIC, BIC por modelo, CRPS empírico, desvio das dobras de validação cruzada, ranking multicritério (RMSE 0,5; CRPS 0,3; desvio 0,2). Não há MASE, sMAPE ou RMSSE, que são necessários para comparar séries com escalas distintas e evitar o viés do MAPE.
2. Validação: um holdout único de 12 meses (RMSE usado para eleger o "vencedor"), mais 3 dobras rolling-origin de 12 meses para seis modelos; a validação cruzada não inclui Prophet/UC, Gradient Boosting, ensemble nem LSTM, de modo que o vencedor multicritério combina RMSE do holdout com o desvio de dobras ausente para ele ("—").
3. Comparadores: ARIMA, Naive sazonal e Drift. Não há média móvel ou média histórica, que na série corrigida são fortes (item 2.5).
4. Teste de acurácia preditiva: Diebold-Mariano aplicado com h = 1 (`teste_diebold_mariano`, linhas 2389 a 2424, perda quadrática, p-valor pela normal) sobre resíduos in-sample (141 pares), não sobre erros de previsão fora da amostra multi-horizonte; o estatístico não aplica a correção de Harvey-Leybourne-Newbold nem erros robustos a heterocedasticidade e autocorrelação para h > 1, e os erros apresentam heterocedasticidade (Breusch-Pagan com p < 0,05 em ARIMA e SARIMAX-12) e não normalidade (Jarque-Bera com p ≈ 0).

### 2.5 Diagnóstico quantitativo da série corrigida com comparadores simples

Para dimensionar o efeito do defeito e fixar o piso de desempenho, foram calculados, nesta etapa, quatro comparadores sem parâmetros ajustáveis em 24 origens rolling consecutivas (as últimas), horizonte de 1 a 12 meses, treino a partir de 2018-01 e erros agregados sobre todos os horizontes e origens.

| Comparador | Série corrigida (MAE; RMSE) | Série com dia e mês invertidos (MAE; RMSE) |
|---|---|---|
| Naive (último valor) | 28,5; 40,5 | 54,2; 88,4 |
| Naive sazonal (mesmo mês do ano anterior) | 31,0; 44,9 | 19,9; 27,5 |
| Média dos últimos 12 meses | 19,9; 26,4 | 37,0; 60,0 |
| Média histórica | 19,4; 26,1 | 33,5; 60,6 |

Na série invertida, o Naive sazonal parece muito bom, porque o artefato é recorrente (maio alto todo ano); na série correta, as médias simples vencem com folga o Naive sazonal e ficam muito próximas do RMSE de 25,03 atribuído ao "vencedor" Prophet/UC do snapshot. O resultado indica que, na série correta, o espaço para ganho de modelos complexos é pequeno e que a hipótese a testar é se algum modelo supera estatisticamente as médias simples. Esses números são piso de referência e não resultados do artigo.

### 2.6 Ameaças à validade

1. Validade de construto: o parse de datas inverte dia e mês (seção 1.1); a série agregada mistura manutenção preventiva programada (33,4%) com demanda corretiva; o ramp-up de 2015 a 2017 e a queda de 2020 introduzem quebras estruturais; a série de entrada do motor começa em 2015-01 com zeros anteriores ao primeiro chamado.
2. Validade interna: holdout único; apenas 3 dobras; Diebold-Mariano sobre resíduos in-sample; critério de seleção que usa o próprio holdout; ausência de testes de quebra estrutural (por exemplo CUSUM, Bai-Perron) e de estacionariedade confiáveis (ADF e KPSS foram corrompidos em data pelo Sheets); ajuste de hiperparâmetros por grid search sem separação documentada entre ajuste e avaliação; tratamento de outliers por mediana móvel com |z| > 3 aplicado à série completa no pipeline principal (linha 3177 do motor) antes da divisão treino/teste, o que usa informação do período de teste (na validação cruzada, linha 2212, o tratamento é aplicado apenas ao treino).
3. Validade estatística: modelos gaussianos (ARIMA, SARIMAX, Holt-Winters) aplicados a contagens sobredispersas; intervalos por bootstrap de resíduos com resíduos não normais; MAPE como métrica em séries com valores baixos; R² negativo e NaN em vários modelos.
4. Validade externa: uma única instituição (UFSB), quatro unidades relevantes, 69 meses estáveis; sem validação em outra universidade.
5. Reprodutibilidade: motor executado apenas no hub com secret e planilha privada; o repositório do artigo contém snapshots mutáveis (cron de 30 min) e código divergente do executado; o LSTM depende de TensorFlow não instalado no ambiente do workflow; não há semente e versão de pacotes registradas no snapshot além de `requirements.txt` com versões fixas.
6. Conflito de papéis: o autor é também o responsável pelo sistema de chamados, de modo que mudanças de processo (migração GLPI, política de abertura de chamados) afetam a série; a documentação dessas mudanças é necessária e não foi encontrada nos repositórios.

### 2.7 O que falta rodar

1. Corrigir o parse de datas no motor (formato ISO explícito `%Y-%m-%d %H:%M` com `dayfirst=False`, com falha ruidosa para formatos inesperados) e reexecutar o pipeline completo; registrar o commit do hub e a data da execução.
2. Definir a variável-alvo: total, corretivos apenas, preventivos apenas, e por campus (três campi mais Reitoria); decidir se a janela é 2018-01 em diante ou 2021-01 em diante, com análise de sensibilidade.
3. Executar rolling-origin com origens expansivas ou deslizantes (no mínimo 24 origens), horizontes 1, 3, 6 e 12, reportando MASE, RMSSE, MAE, RMSE e CRPS; incluir os comparadores média histórica, média de 12 meses, ETS automático, Theta, regressão binomial negativa e, se justificável, INGARCH ou GAM binomial negativo (o GAM já está documentado em `docs/METODOLOGIA_GAM.md` e ainda não foi executado); manter SARIMAX e Gradient Boosting; avaliar LSTM somente se TensorFlow for instalado e a série tiver tamanho suficiente.
4. Aplicar Diebold-Mariano com correção de Harvey-Leybourne-Newbold sobre erros fora da amostra por horizonte, com erros robustos, e Model Confidence Set como alternativa; bootstrap em blocos para intervalos de confiança das métricas.
5. Calibrar intervalos preditivos (cobertura empírica de 80% e 95%, pinball loss, CRPS) com previsão conforme (conformal) como comparador.
6. Testar quebras estruturais (Bai-Perron ou CUSUM) e sazonalidade na série corrigida (teste de Kruskal-Wallis por mês, STL) antes de justificar SARIMAX sazonal.
7. Estudar valor operacional: transformar os intervalos em necessidade de horas de equipe ou contratos, usando o custo por chamado do repositório de custos, e registrar uma estimativa de erro de dimensionamento.
8. Recalcular `analise_gam.json`, `protocolo_zuur.json`, `previsao_*.json` e restaurar `previsao_temporal.json` e `previsao_detalhes.json` no hub, que hoje estão vazios.

### 2.8 Lacuna na literatura e referências verificadas

Buscas realizadas em 03/11/2026 em motor de busca geral (a API do Crossref não está acessível na rede da sessão, de modo que os DOIs abaixo são apenas os que apareceram textualmente nos resultados de busca; os demais constam como "DOI não encontrado"). A busca não é uma revisão sistemática e não localizou artigo de periódico que preveja o volume mensal de chamados de manutenção em edificações universitárias ou públicas com validação rolling-origin e testes formais de acurácia preditiva. Os trabalhos encontrados tratam de classificação de pedidos, manutenção preditiva de equipamentos, previsão de demanda de mão de obra e competições gerais de previsão. Essa ausência, restrita ao escopo da busca, sustenta provisoriamente a lacuna; antes da submissão, recomenda-se busca sistemática em Scopus e Web of Science com os termos "work order forecasting", "maintenance request demand" e "service request time series".

| Nº | Referência | Tipo e uso no artigo | DOI |
|---|---|---|---|
| 1 | Adhikari, Karunaratne e Sumanarathna (2025). Machine learning techniques for predictive maintenance of building services: a comprehensive review and research outlook. *Facilities*, 43(11-12), 803-817 | Revisão de 118 artigos; indica o estado da arte e que previsão de demanda de chamados é pouco explorada | DOI não encontrado |
| 2 | D'Orazio, Bernardini e Di Giuseppe (2023). LSTM e Bi-LSTM sobre dados de CMMS para prioridade e designação de equipe. *Facilities*, 41(15/16) (volume e páginas conforme resumo de busca, a conferir) | Trabalho vizinho que usa dados de CMMS; mostra que a literatura se concentra em classificação | 10.1108/F-07-2022-0093 |
| 3 | Workforce forecasting in the building maintenance and repair work: Evaluating machine learning and LSTM models. *Journal of Building Engineering* (2024) | Comparação de ML e LSTM contra ARIMA para demanda de mão de obra em Hong Kong, horizontes de 30 a 365 dias; autoria não verificada | DOI não encontrado (identificador ScienceDirect S2352710224016930) |
| 4 | Predictive Maintenance in Building Facilities: A Machine Learning-Based Approach. *Sensors* (2021) | Aplicação de ML a instalações prediais; autoria não verificada | 10.3390/s21041044 |
| 5 | Makridakis, Spiliotis e Assimakopoulos (2022). M5 accuracy competition: Results, findings, and conclusions. *International Journal of Forecasting*, 38(4), 1346-1364 | Evidência sobre séries com intermitência e superioridade de ML em dados de varejo; contraponto ao caso de poucas observações | DOI não encontrado |
| 6 | Makridakis e colaboradores (2023). Statistical, machine learning and deep learning forecasting methods: comparisons and ways forward. *Journal of the Operational Research Society* (título e autoria a conferir; DOI retornado pela busca) | Combinações de modelos de aprendizado profundo superam padrões em séries mensais e horizontes longos | 10.1080/01605682.2022.2118629 |
| 7 | Petropoulos et al. (2022). Forecasting: theory and practice. *International Journal of Forecasting*, 38(3), 705-871 | Referência de boas práticas de avaliação e seleção de modelos | 10.1016/j.ijforecast.2021.11.001 |
| 8 | Makridakis, Spiliotis e Assimakopoulos (2018). Statistical and Machine Learning forecasting methods: Concerns and ways forward. *PLOS ONE*, 13(3), e0194889 | Métodos de ML ficam atrás de oito estatísticos em 1.045 séries mensais da M3; justifica comparadores simples | 10.1371/journal.pone.0194889 |
| 9 | Harvey, Leybourne e Zu (2024). Artigo no *Journal of Business & Economic Statistics* sobre falha do teste de Diebold-Mariano com média da diferença de perdas variável no tempo (título não verificado) | Fundamenta cautela no uso do teste de Diebold-Mariano em séries com quebras | 10.1080/07350015.2024.2418835 |
| 10 | Harvey, Leybourne e Newbold (1997). Testing the equality of prediction mean squared errors. *International Journal of Forecasting*, 13(2), 281-291 | Correção de pequena amostra para Diebold-Mariano, necessária com 12 a 24 erros por horizonte | DOI não encontrado |
| 11 | Hyndman e Koehler (2006). Another look at measures of forecast accuracy. *International Journal of Forecasting*, 22(4), 679-688 | Fundamenta MASE em lugar de MAPE | 10.1016/j.ijforecast.2006.03.001 |
| 12 | Bergmeir e Benítez (2012). On the use of cross-validation for time series predictor evaluation. *Information Sciences*, 191, 192-213 | Fundamenta validação em blocos e comparação de esquemas de avaliação | 10.1016/j.ins.2011.12.028 |

Itens complementares citáveis para calibração probabilística: Gneiting e Raftery (2007), Strictly proper scoring rules, prediction, and estimation, *Journal of the American Statistical Association*, 102(477), 359-378, DOI 10.1198/016214506000001437. Dos 12 itens, 8 são de 2021 a 2025 e 4 são referências metodológicas anteriores; os itens 1, 3, 5, 9 e 10 exigem conferência de autoria, título ou DOI diretamente no editor antes do uso.

## Etapa 3. Comparação entre A (previsão de chamados) e B (aprendizado contínuo da classificação)

### 3.1 Fontes e verificação do candidato B

O candidato B foi examinado no repositório `classificacao-chamados`, branch `claude/xenodochial-nightingale-81823d` (commit `2e815f0`, 02/11/2026), arquivos `src/aprendizado_continuo.py` (194 linhas) e `docs/dados/trilha_b/aprendizado_continuo.json`. O protocolo é cronológico: o modelo inicial (`linear_svc`) treina com chamados abertos até 2021, cada trimestre é predito antes de os rótulos serem revelados, há auditoria aleatória de 100 chamados por bloco, que calibra o limiar do Learn-then-Test (meta de erro de 10%), e as estratégias comparadas são estático, aleatório, ativo e completo, em 20 blocos e 7.691 chamados avaliados. A acurácia agregada gravada no JSON é de 0,7673 (estático), 0,8074 (aleatório), 0,8107 (ativo) e 0,8109 (completo), e a acurácia anual do modelo estático cai de 0,8099 em 2022 para 0,6971 em 2026, o que confere com o enunciado (0,81 para 0,70). Nesse arquivo, "aleatório" e "ativo" somam à auditoria 100 revisões por bloco, de modo que a diferença ativo menos aleatório é de 0,33 ponto, compatível com o intervalo de +0,3 a +0,7 informado. O valor de 0,7977 para "somente auditoria de 100 chamados por trimestre", o ganho de +3,0 pontos com IC95% de 1,45 a 4,86 e a razão de cerca de 70% do ganho total não constam no arquivo lido; não foi possível verificar a origem desses três números (outra execução, outro parâmetro ou cálculo posterior).

Verificou-se ainda que o artigo submetido ao RAP (`docs/trilha_b/artigo_rap/artigo_rap.txt`, cerca de 7.500 palavras, 14.357 chamados em 39 categorias) já menciona, na discussão, a necessidade de "auditoria amostral periódica e recalibração" como capacidade institucional, e que a versão v3 do artigo de classificação (`04_artigo/artigo_classificacao_chamados_v3.md`) não contém os termos "aprendizado contínuo", "aprendizado ativo" ou "retreino". Isso define a fronteira: o artigo de classificação cita a ideia, e B a testaria empiricamente.

### 3.2 Comparação

| Critério | A. Previsão de chamados | B. Aprendizado contínuo com auditoria amostral |
|---|---|---|
| Estado dos resultados | Nenhum resultado utilizável: série do motor com dia e mês invertidos, `previsao_temporal.json` vazio no hub; exige correção do motor e reexecução completa | Simulação já executada e registrada (20 blocos, 7.691 chamados, quatro estratégias); faltam IC e testes pareados nos números do enunciado, além de reprodução do 0,7977 |
| Pergunta e novidade | Previsão de volume mensal em edificações públicas com validação rolling-origin, comparadores simples, calibração probabilística e valor operacional; lacuna aparente na literatura buscada (seção 2.8) | Valor marginal da auditoria aleatória e do aprendizado ativo na manutenção de um classificador sob deriva; extensão de uma ideia já citada no artigo de classificação |
| Risco de fatiamento em relação ao artigo de classificação | Baixo a moderado: outro objeto (série de contagens, não rótulos) e outra família de métodos; sobreposição apenas na base de chamados e, se houver recortes por categoria, na dependência da taxonomia | Alto: mesma base, mesmo corte B, mesmo modelo (`linear_svc`), mesmo protocolo Learn-then-Test e mesma autoria; revisores do RAP ou de outro periódico podem entender como divisão artificial de um único estudo |
| Viabilidade com dados existentes | Média: 136 meses completos, 69 estáveis desde 2021, quatro séries por unidade e séries por tipo; poder estatístico limitado para 12 meses de horizonte; exige correção de código e execução em ambiente com Python científico | Alta: dados e código prontos; limitação de ser simulação retrospectiva com um modelo e uma instituição |
| Contribuição para a tese (ODS 9, 11, 12) e para o ecossistema Malha IA | Alta: sustenta a etapa de governança preditiva e alimenta o Artigo 3 (custos), que usa o mesmo motor e o mesmo defeito de parse | Média: consolida o fluxo humano-IA da classificação, sem avançar a camada preditiva |
| Principal risco científico | Resultado negativo (médias simples dificilmente serão superadas na série corrigida, seção 2.5), poucos meses estáveis e quebras estruturais | Ganho incremental pequeno do aprendizado ativo (+0,3 ponto) e dependência de um único modelo e de simulação sem custo real de auditoria |
| Dependência entre os artigos | Pode usar a taxonomia revisada do artigo de classificação para recortes por categoria corretiva, sem republicar resultados | Depende do artigo de classificação estar aceito ou publicado para não parecer duplicação |

### 3.3 Periódicos-alvo com rota gratuita

Esta subseção está limitada ao que foi confirmado em busca em 03/11/2026. A classificação Qualis vigente não pôde ser verificada (os resultados trouxeram classificações antigas e conflitantes), e deve ser conferida na Plataforma Sucupira antes da escolha final; nenhum periódico abaixo é declarado A1 ou A2 neste documento.

1. *International Journal of Forecasting* (Elsevier): modelo híbrido segundo um agregador de métricas, com acesso por assinatura como padrão e acesso aberto opcional; a existência de rota de publicação sem taxa e o Qualis não foram confirmados. Adequado ao desenho de A (comparação de métodos, avaliação rolling-origin, calibração), com alta seletividade.
2. *Facilities* (Emerald): rota verde gratuita confirmada na política da editora (depósito do manuscrito aceito sem embargo, com licença CC-BY-NC, sem pagamento); o periódico publicou a revisão de Adhikari et al. (2025) e o trabalho de D'Orazio et al. (2023) sobre dados de CMMS (seção 2.8), o que mostra aderência temática para A e para B. Qualis não verificado.
3. *Ambiente Construído* (ANTAC, SEER/UFRGS): acesso aberto com licença CC-BY e indexação em DOAJ e SciELO; a existência de taxa de publicação e o Qualis atual não foram confirmados (há registros de conceito A em quatro áreas e, em editorial posterior, B1 em três áreas). Alternativa nacional para A com enquadramento em manutenção e gestão de edificações.
4. *Journal of Building Engineering* (Elsevier): publicou trabalho comparável de previsão de mão de obra em manutenção predial (2024); política de acesso e Qualis não verificados.
5. Para B, o mesmo conjunto serve, com a ressalva de que a submissão pelo mesmo grupo e com a mesma base deve declarar a relação com o artigo do RAP; outros periódicos de sistemas de apoio à decisão não foram avaliados.

### 3.4 Recomendação

Recomenda-se escrever A primeiro, com um ponto de decisão (gate) antes do investimento na redação completa. Os motivos são os seguintes. O risco de fatiamento de B é alto e tende a prejudicar tanto B quanto o artigo de classificação, que ainda está em tramitação; A possui objeto, método e público distintos e avança a etapa preditiva que sustenta a tese. Os resultados de B já existem e não se perdem: podem ser mantidos como material de reserva e submetidos depois, como comunicação curta ou como extensão após a decisão editorial do RAP, o que reduz o custo de esperar. A condição para A é a correção do parse de datas e a reexecução, e a decisão se apoia em três critérios mensuráveis: (i) na série corrigida, cobertura empírica dos intervalos de 80% e 95% dentro de ±5 pontos percentuais para ao menos um modelo; (ii) ao menos um modelo com MASE inferior ao da média histórica em horizontes de 1 a 3 meses, com Diebold-Mariano corrigido por Harvey-Leybourne-Newbold; (iii) estabilidade do ranking entre as janelas 2018 em diante e 2021 em diante. Se nenhum critério for satisfeito, A mantém publicabilidade como estudo de comparação que demonstra o limite de modelos complexos em séries curtas e sobredispersas e documenta o efeito do erro de parse sobre a inferência de sazonalidade, e a alternativa é inverter a ordem e priorizar B em formato curto, com a ressalva de fatiamento declarada.

Riscos e ressalvas da recomendação: a qualidade de A depende de dados que o autor controla (planilha `CHAMADOS`, formato das datas), que não foram acessados nesta análise; o ganho esperado de modelos complexos é pequeno; e a duração da execução do motor completo (o workflow do hub declara limite de 600 minutos) é um custo real. A estimativa de esforço em horas não foi calculada por falta de dados sobre a disponibilidade do autor.

## Etapa 4. Estrutura do artigo recomendado (A)

### 4.1 Título provisório

Português: Previsão mensal de chamados de manutenção predial em universidade federal multicampi: comparação de modelos sob validação rolling-origin e calibração de intervalos preditivos.

Inglês: Monthly forecasting of building maintenance requests at a multicampus federal university: model comparison under rolling-origin validation and predictive interval calibration.

O título não afirma superioridade de nenhuma família de modelos, porque o resultado depende da reexecução.

### 4.2 Resumo provisório (152 palavras, sem resultados numéricos por não existirem)

A previsão do volume mensal de chamados de manutenção em edificações públicas apoia o dimensionamento de equipes e contratos, mas a literatura concentra-se em classificação de pedidos e em manutenção de equipamentos, com poucas avaliações de previsão de demanda sob validação temporal rigorosa. Este estudo compara modelos estatísticos, de aprendizado de máquina e de aprendizado profundo na previsão mensal de chamados de uma universidade federal multicampi, separando a demanda corretiva da manutenção preventiva programada e tratando quebras estruturais. A avaliação emprega origens rolling-origin em horizontes de 1 a 12 meses, comparadores simples (média histórica e média móvel), MASE, RMSSE e CRPS, teste de Diebold-Mariano com correção de pequena amostra e cobertura empírica dos intervalos preditivos. Documenta-se ainda o efeito de um erro de interpretação de datas sobre a sazonalidade aparente. Os resultados serão inseridos após a reexecução com a série corrigida [a preencher]. Discute-se o uso dos intervalos no planejamento da manutenção.

### 4.3 Seções e conteúdo

1. Introdução. Problema de gestão (dimensionamento de equipes, contratos e orçamento com demanda variável), lacuna identificada na seção 2.8, objetivo, perguntas de pesquisa (qual família supera a média histórica, qual a calibração dos intervalos, qual a sensibilidade à janela e ao alvo) e contribuições, entre elas o registro do efeito de um erro de parse de datas na sazonalidade aparente. Nesta seção cita-se o artigo de classificação apenas para delimitar fronteira, sem reutilizar seus resultados.
2. Referencial e trabalhos relacionados. Previsão de demanda de manutenção e de mão de obra em edificações (itens 1 a 4 da seção 2.8), competições de previsão e comparadores simples (itens 5, 6 e 8), avaliação rolling-origin e métricas escaladas (itens 7, 11 e 12), testes de acurácia preditiva (itens 9 e 10) e avaliação probabilística (Gneiting e Raftery, 2007), mais normas aplicáveis ao contexto da manutenção (NBR 5674, NBR 14037 e NBR ISO 41001), cuja pertinência ao texto deve ser conferida pelo autor.
3. Dados e construção da série. Fonte (GLPI e planilha institucional, via hub `malha-ia`), commit e data da extração, regras de limpeza (remoção de linhas vazias, que somam 69,9% das linhas do `chamados.json`), interpretação explícita do formato ISO das datas, exclusão do mês corrente, janelas 2018 em diante e 2021 em diante, separação corretiva e preventiva, recortes por campus e Reitoria, e descrição dos regimes (adoção, pico, queda de 2020, recuperação). Inclui um quadro de eventos institucionais que afetam a série.
4. Método. Modelos (ETS, Theta, ARIMA, SARIMAX, regressão binomial negativa ou GAM, Gradient Boosting direto e, condicionalmente, LSTM), comparadores (Naive, Naive sazonal, média histórica, média de 12 meses), esquema rolling-origin com no mínimo 24 origens e horizontes 1, 3, 6 e 12, métricas pontuais (MASE, RMSSE, MAE, RMSE) e probabilísticas (CRPS, pinball, cobertura de 80% e 95%), Diebold-Mariano com correção de Harvey-Leybourne-Newbold sobre erros fora da amostra, bootstrap em blocos, previsão conforme, testes de quebra e de sazonalidade, e regras de reprodutibilidade (sementes, versões, hash do snapshot).
5. Resultados. Descrição da série corrigida e do efeito do erro de datas, desempenho por horizonte e por recorte, comparações pareadas, calibração dos intervalos, análises de sensibilidade (janela, alvo, tratamento de outliers) e previsão de 12 meses à frente com intervalo.
6. Discussão. Quais modelos justificam a complexidade, uso dos intervalos no planejamento (horas de equipe e contratos, usando custo por chamado do repositório de custos), implicações para gestão pública e para ODS 9, 11 e 12, e limitações (instituição única, poucos meses estáveis, intervenções de processo não modeladas).
7. Conclusão. Respostas objetivas às perguntas de pesquisa e agenda futura (séries hierárquicas por campus e categoria, variáveis exógenas de clima e calendário acadêmico, validação em outra instituição).
8. Declarações e referências. Disponibilidade de dados e código (snapshots e scripts do repositório, base bruta sob controle do hub), contribuição dos autores, uso de ferramentas de IA, conflito de interesses (autor também gestor do sistema de chamados) e referências em ABNT ou no padrão do periódico escolhido.

### 4.4 Tabelas e figuras previstas

Tabelas: T1 estatísticas descritivas por regime, campus e tipo; T2 especificação dos modelos e hiperparâmetros; T3 desempenho por modelo e horizonte (MASE, RMSSE, CRPS); T4 comparações pareadas de Diebold-Mariano com correção, com ajuste para múltiplas comparações; T5 cobertura e largura dos intervalos; T6 sensibilidade à janela e ao alvo; T7 efeito do erro de datas sobre ACF, perfil sazonal e ranking de modelos (pode ir ao suplemento).

Figuras: F1 fluxo de dados e pipeline (hub, snapshot, motor, validação); F2 série mensal com regimes e quebras; F3 comparação entre perfil sazonal e ACF da série corrigida e da invertida; F4 erro por horizonte e por modelo; F5 gráfico de cobertura e fan chart de um recorte; F6 previsão de 12 meses com intervalo para o total e por campus.

Material suplementar: diagnósticos de resíduos, protocolo de exploração de Zuur et al. (2010), análise GAM, tabela completa de hiperparâmetros e checklist de reprodutibilidade.

### 4.5 Pendências por responsável

Autor (decisões e conferências que dependem do pesquisador):

1. Definir a variável-alvo principal (corretiva, total ou ambas) e a janela principal (2018 em diante ou 2021 em diante), com a outra como sensibilidade.
2. Confirmar o formato real das datas na planilha `CHAMADOS` (texto ISO, texto dia/mês/ano ou data nativa) e autorizar a correção do motor no hub.
3. Escolher o periódico e confirmar Qualis vigente na Plataforma Sucupira e a política de taxas.
4. Informar o status da relação com o orientador e a definição de coautoria, que não constam nos repositórios e não foram presumidos.
5. Documentar mudanças de processo que afetam a série (migração de sistema, política de abertura de chamados, contratos de manutenção preventiva, greves e períodos sem aulas), em especial 2015 a 2017 e 2020.
6. Decidir a relação de citação entre este artigo e o artigo de classificação (citação como contexto, sem reutilizar tabelas).

Dados novos:

1. Série de precipitação com fonte e estação identificadas (INMET ou equivalente) e calendário acadêmico oficial por campus, em lugar do indicador binário atual.
2. Programação contratual de manutenção preventiva por mês, para explicar a série preventiva.
3. Séries de custo por mês do repositório de custos, para a análise de valor operacional (após correção do mesmo defeito de datas, que afeta o Artigo 3).
4. Taxonomia revisada do artigo de classificação, se houver recortes por categoria.

Experimentos:

1. Corrigir o parse de datas e reexecutar o pipeline no hub, restaurando `previsao_temporal.json` e `previsao_detalhes.json`.
2. Implementar o rolling-origin multi-horizonte com no mínimo 24 origens e os comparadores simples.
3. Ajustar ETS, Theta, ARIMA, SARIMAX, regressão binomial negativa ou GAM, Gradient Boosting e, se TensorFlow estiver disponível, LSTM.
4. Calcular MASE, RMSSE, CRPS, pinball e cobertura, e Diebold-Mariano com correção de Harvey-Leybourne-Newbold.
5. Testar quebras estruturais e sazonalidade na série corrigida.
6. Executar a previsão conforme e o bootstrap em blocos para intervalos.
7. Produzir as tabelas T1 a T7 e as figuras F1 a F6 por script único versionado, com hash do snapshot.

A execução de 1 a 7 depende de Python científico e do acesso à planilha, e pode ser feita em GitHub Actions de repositório público ou localmente, sem relação com o saldo de créditos da nuvem, que expira em 05/11/2026.

## Etapa 5. Proposta de particionamento e organização dos repositórios (A recomendado)

Esta proposta não move, remove nem altera nenhum arquivo. Ela segue a regra do hub (`docs/PARTICIONAMENTO_REPOSITORIOS.md`): permanece no hub o que serve a mais de um eixo ou é fonte oficial; vai para o repositório do eixo o que pertence a um único artigo. Cada ação abaixo é reversível por `git revert` e deve ser aprovada individualmente pelo autor.

### 5.1 Papel de cada repositório

1. `malha-ia` (hub): permanece como fonte única de `chamados.json`, `contexto_sazonal.json`, `area_manutencao.json`, `filtros_disponiveis.json`, scripts de exportação e motores que escrevem na planilha. Passa a ser o único local de correção do parse de datas nos três motores (chamados, custos e ODS).
2. `malha-previsao-chamados` (Artigo 2, A): torna-se o repositório reprodutível do artigo, com código de avaliação, resultados versionados por rodada, texto de apoio e dashboard.
3. `malha-previsao-custos` (Artigo 3): continua separado; recebe a correção de datas e a recodificação dos JSON; reutiliza do Artigo 2 apenas o módulo de avaliação, por cópia versionada ou pacote, e não por duplicação manual.
4. `classificacao-chamados`: permanece independente; B fica como material de reserva neste repositório, sem migração.
5. Repositório "Demais": não criar agora; nada do que foi inventariado justifica, e a regra do hub exige inventário final do hub antes.

### 5.2 Estrutura-alvo de `malha-previsao-chamados`

Estrutura proposta, mantendo na raiz os arquivos citados em `AGENTS.md` até que esse arquivo seja atualizado:

1. Raiz: `README.md`, `AGENTS.md`, `CITATION.cff` (corrigido para este repositório e para o Artigo 2), `LICENSE` (licença a ser escolhida pelo autor; hoje ausente), `dashboard.html`, `index.html`, `motor_previsao_chamados.py` (cópia sincronizada com o hub).
2. `docs/`: `CONTRATO_DADOS.md`, `METODOLOGIA_GAM.md`, `METODOLOGIA_PROTOCOLO_ZUUR.md`, `PLANO_PROXIMO_ARTIGO.md`, `referencias/README.md` (movido de `Referência Bibliográfica - Drive/`) e `decisoes/` para registros curtos de decisão (por exemplo, janela e alvo adotados).
3. `avaliacao/` (novo): módulos de série, validação rolling-origin, métricas e testes, escritos para rodar sem credenciais a partir de um snapshot do hub, de modo a separar o experimento do artigo do motor que escreve na planilha.
4. `resultados/` (novo): saídas por rodada, em subpastas datadas, cada uma com hash do snapshot e do commit do hub, versões de pacotes e sementes; substitui o uso de `dados/previsao_*.json` como evidência do artigo, que deixam de ser fonte de resultados citáveis por serem mutáveis.
5. `tests/` (novo): teste de regressão do parse de datas (casos `2026-05-06` e `2026-05-29`), testes das métricas e do esquema rolling-origin.
6. `scripts/`: `baixar_dados_hub.py` e `exportar_dados_csv.py` (sincronização), subpasta `analise/` para `gerar_analise_gam.py` e `gerar_protocolo_zuur.py`, e `exportar_dados_json.py` (uso manual).
7. `dados/` e `dados_csv/`: apenas snapshots de leitura, conforme `AGENTS.md`; `chamados.json` continua ausente.
8. `.github/workflows/`: um workflow único de sincronização com frequência reduzida, `pages.yml` restrito aos arquivos publicáveis e `testes.yml` novo para executar `tests/`.

### 5.3 Itens para remoção ou fusão (nenhum removido)

| Item | Ação | Condição | Reversão |
|---|---|---|---|
| `.github/workflows/previsao_chamados_global.yml` | Remover | Fusão prévia de seu gatilho diário no workflow de sincronização | `git revert` |
| Cron de 30 minutos em `atualizar-dados-hub.yml` | Reduzir para diário | Aprovação do autor; hoje gera cerca de 5 a 6 commits de bot por dia | Alterar o cron |
| `Referência Bibliográfica - Drive/` | Mover para `docs/referencias/` | Atualizar links internos, se houver | `git mv` inverso |
| `path: '.'` em `pages.yml` | Publicar somente `index.html`, `dashboard.html` e `dados/` | Testar o dashboard após a mudança | Restaurar linha |
| `execucao_offline/requirements.txt` | Separar `requirements-sync.txt` (pandas) de `requirements-motor.txt` | Nenhuma | `git revert` |
| `CITATION.cff` | Corrigir URLs (`adinailson88`), título e escopo | Escolha da licença | `git revert` |
| `dados/previsao_*.json` vazios | Restaurar após reexecução, não apagar | Correção do motor no hub | Não se aplica |
| Linhas vazias de `malha-ia/dados/chamados.json` | Propor ao hub a poda das 33.838 linhas vazias | Fora do escopo deste repositório | Fora do escopo |

Não há arquivo considerado lixo irrecuperável neste repositório; os candidatos acima são duplicações, configurações excessivas ou arquivos fora do local adequado. Nenhum dado de `dados_csv/` é candidato à remoção.

### 5.4 Ações em outros repositórios (fora desta branch, a serem decididas pelo autor)

1. `malha-ia`: corrigir `extrair_serie_temporal` em `motor_previsao_chamados.py` (formato `%Y-%m-%d %H:%M` explícito, `dayfirst=False`, erro explícito para formato desconhecido), aplicar a mesma verificação às linhas 555 e 604 de `motor_previsao_custos.py` e 357 e 358 de `motor_ods.py`, reexecutar `previsao_chamados_global.yml` e restaurar `PREVISAO_TEMPORAL`. Esta é a ação de maior prioridade e a única que desbloqueia A.
2. `malha-previsao-custos`: após a correção no hub, ressincronizar os snapshots e recodificar os JSON com texto corrompido ("PerÃ­odo").
3. `classificacao-chamados`: nenhuma alteração; registrar, no plano daquele repositório, que B é reserva e que o fatiamento deve ser evitado.

### 5.5 Sequência sugerida de execução

1. Aprovar a correção no hub e reexecutar a previsão global (ação 5.4.1).
2. Neste repositório: corrigir `CITATION.cff` e criar `LICENSE` (após escolha do autor), mover a pasta de referências, fundir os workflows e restringir `pages.yml`.
3. Criar `avaliacao/`, `resultados/` e `tests/`, com o teste de regressão de datas como primeiro commit.
4. Executar o experimento completo e congelar a primeira rodada em `resultados/`.
5. Avaliar o gate de decisão da seção 3.4 e confirmar A ou voltar a B.

Estado: etapa 5 concluída
