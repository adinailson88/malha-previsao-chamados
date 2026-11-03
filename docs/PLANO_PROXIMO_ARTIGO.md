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
4. Teste de acurácia preditiva: Diebold-Mariano aplicado com h = 1 sobre resíduos in-sample (141 pares), não sobre erros de previsão fora da amostra multi-horizonte; o estatístico não aplica a correção de Harvey-Leybourne-Newbold nem erros robustos a heterocedasticidade e autocorrelação para h > 1, e os erros apresentam heterocedasticidade (Breusch-Pagan com p < 0,05 em ARIMA e SARIMAX-12) e não normalidade (Jarque-Bera com p ≈ 0).

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
2. Validade interna: holdout único; apenas 3 dobras; Diebold-Mariano sobre resíduos in-sample; critério de seleção que usa o próprio holdout; ausência de testes de quebra estrutural (por exemplo CUSUM, Bai-Perron) e de estacionariedade confiáveis (ADF e KPSS foram corrompidos em data pelo Sheets); ajuste de hiperparâmetros por grid search sem separação documentada entre ajuste e avaliação; tratamento de outliers por mediana móvel com |z| > 3 aplicado antes da divisão treino/teste, o que vaza informação.
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

Itens complementares citáveis para calibração probabilística: Gneiting e Raftery (2007), Strictly proper scoring rules, prediction, and estimation, *Journal of the American Statistical Association*, 102(477), 359-378, DOI 10.1198/016214506000001437. Dos 12 itens, 7 são de 2021 a 2025 e 5 são referências metodológicas anteriores; os itens 1, 3, 5, 9 e 10 exigem conferência de autoria, título ou DOI diretamente no editor antes do uso.

Estado: etapa 2 concluída
