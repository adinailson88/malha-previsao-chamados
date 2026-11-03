# Diagnóstico do desenho da série de custos (Artigo 3) e melhorias propostas

Documento de 03/11/2026, complementar a `docs/PLANO_PROXIMO_ARTIGO.md`. Foi elaborado a partir da leitura de `malha-previsao-custos/motor_previsao_custos.py` (commit `0b5d0f1`, funções `parse_valor_chamado`, `construir_serie_custo`, `extrair_serie_custo` e `executar_previsao_custo`), dos snapshots `previsao_custo_*.json` do hub `malha-ia` e do repositório de custos, e de cálculos próprios sobre `malha-ia/dados/chamados.json` (commit `526abb8`, coluna 16, "Valor do chamado"). Nenhum modelo foi reajustado; os números abaixo descrevem a série e comparadores sem parâmetros. Nada foi alterado nos outros repositórios. Em 03/11/2026 o autor esclareceu que (i) o valor da coluna Q reflete as ordens de serviço (OS), em número muito menor que os chamados, e (ii) o desenho consiste em duas previsões: a quantidade de chamados e o custo, ambas em função de covariáveis (mês, ano, chuva, número de pessoas, período letivo, área construída, campus e outras), com a quantidade de chamados entrando também como covariável do custo. Não se modela conversão de chamado em OS. Esta versão incorpora essa orientação (seções 2, 4, 5 e 7).

## 1. Como a série de custos é construída hoje

O alvo é a soma mensal, por data de abertura, dos valores positivos da coluna Q. Linhas com valor vazio, zero ou inválido são descartadas, meses com soma zero são removidos depois da agregação (`contagem[contagem['Quantidade'] > 0]`), o mês corrente é excluído, e a série entra no mesmo pipeline do Artigo 2 (ARIMA, SARIMAX, Holt-Winters, UnobservedComponents, Theta, Gradient Boosting, LSTM e ensemble), com validação de 3 dobras de 12 meses, holdout de 12 meses, tratamento de outliers por mediana móvel com |z| > 3 e o mesmo `dayfirst=True` do motor de chamados. Os valores são nominais, em reais, sem deflator. A coluna de data de conclusão está definida como `None` (`COL_DATA_CONCLUSAO`), de modo que o custo é sempre atribuído ao mês de abertura.

## 2. Propriedades da série, medidas nesta análise

1. Estrutura chamado e ordem de serviço: dos 14.580 chamados com data, 2.402 (16,5%) têm valor positivo e 12.178 têm valor zero. Os campos "TÍTULO O.S.M." ou "DESCRIÇÃO O.S.M." estão preenchidos em 2.459 chamados, dos quais 2.402 com valor positivo e 57 (2,3% das OS) sem valor; nenhum chamado tem valor sem registro de OS. Portanto o zero não é dado faltante: indica chamado sem OS, e a base permite identificar a OS mesmo sem valor. O percentual de chamados com valor (16,5%) é uma característica da base e não deve ser lido como preenchimento incompleto; o desenho não o modela. A proporção anual de chamados com OS é de 0% (2015 e 2016, sem OS registrada), 9% (2017), 12% (2018), 14% (2019), 20% (2020 e 2021), 17% (2022), 20% (2023), 22% (2024), 19% (2025) e 12% (2026 até outubro); por mês, em 2025 e 2026, oscila entre 6% e 33%. A média mensal de 2018 a 2025 é 18,7% e a de 2026 é 13,5%; o coeficiente de variação mensal da proporção é 0,42. Por campus, a proporção é de 11% na Reitoria, 12% em Jorge Amado, 20% em Sosígenes Costa e 21% em Paulo Freire; por tipo, 9% na manutenção preventiva e de 15% a 25% nas demais categorias principais. A queda em 2026 pode ser real ou defasagem de registro das OS mais recentes, o que não pôde ser distinguido sem extrações anteriores da base. O custo é, portanto, o custo das OS e não o de todos os chamados, e o nome da série deve refletir isso. A correspondência entre valor e OS foi informada pelo autor e confirmada nos dados.
2. Concentração: a soma é de R$ 20,23 milhões; o 1% de maiores chamados responde por 42,2% do total, os 10 maiores por 25,5%, o maior chamado (R$ 776.268, 11/04/2023) equivale a cerca de 4% de todo o período, e o quantil 99% é R$ 177.287 contra mediana de R$ 616. Um estimador de Hill sobre os 5% superiores (117 observações) resultou em índice de cauda de 0,96, valor próximo de 1, abaixo do qual a média teórica não existe; é indicativo, sem intervalo de confiança.
3. Eventos de contratação dominam: 93 chamados da categoria "Posto de trabalho" (rótulo "Contratação de Posto de trabalho...") somam R$ 10,64 milhões, 52,6% do total, e ocupam 8 das 12 maiores posições. Os maiores aparecem em dezembro, janeiro e novembro (por exemplo, dois em 15/01/2025, dois em 12/01/2026 e dois em 06/12/2023), o que sugere ciclo orçamentário e contratual, e não demanda corretiva. A interpretação do rótulo é inferida do texto da categoria e deve ser confirmada pelo autor.
4. Série mensal desde 2018-01 (105 meses, sem mês zerado quando as datas são lidas corretamente): média de R$ 188.914, desvio-padrão de R$ 329.671, coeficiente de variação de 1,75, razão máximo/mediana de 23,7, ACF de lag 1 igual a 0,00 e de lag 12 igual a 0,34. Sem os chamados de "Posto de trabalho", a média cai para R$ 88.910, o coeficiente de variação para 1,34, o ACF lag 1 passa a 0,16 e o lag 12 a -0,01, ou seja, a autocorrelação sazonal de 0,34 do total vem dos eventos de contratação. Agregada por trimestre (35 trimestres), a série tem coeficiente de variação de 0,94 e ACF lag 1 de -0,06.
5. Relação mensal entre quantidade de chamados e custo: desde 2018, a correlação entre o número de chamados e o custo mensal sem "Posto de trabalho" é 0,04 (0,25 entre o logaritmo do custo e o logaritmo da quantidade), e a correlação entre número de chamados e número de OS é 0,44. Em teste de rolling-origin com 24 origens (seção 5.6), incluir a quantidade real do mês como regressor (oráculo) não melhorou o RMSE em relação à média histórica. A hipótese de que a quantidade de chamados explica o custo não foi sustentada no nível mensal agregado com as covariáveis disponíveis, mas o teste é limitado (série global, regressão linear no logaritmo, covariáveis pobres) e não substitui a avaliação do modelo proposto.
6. Descontinuidade: a série global do snapshot de custos tem 114 pontos entre 2017-01 e 2026-10 (118 meses civis), com meses ausentes após o filtro de soma positiva (por exemplo, 2017-02 e 2017-03). Não foi verificado se o pipeline posterior reindexa os meses ausentes ou trata a série como contígua. As séries por filtro têm de 41 a 118 pontos, duas delas sem nenhum (`prev_extintor` e `prev_gerador`).
7. Defeito de datas: o mesmo `dayfirst=True` aplicado a datas ISO (seção 1.1 do plano) desloca valores entre meses; na reconstrução própria, o RMSE dos comparadores muda entre as séries com e sem inversão (mediana dos últimos 12 meses: 378.805 na invertida e 494.041 na correta), e o ACF de lag 12 passa de 0,10 para 0,34, de modo que a estrutura da série e o ranking dos modelos mudam.

## 3. Comparadores sem parâmetros (24 origens rolling-origin, horizontes de 1 a 12 meses, treino desde 2018-01)

| Série | Naive (MAE; RMSE) | Média de 12 meses | Mediana de 12 meses | Média histórica |
|---|---|---|---|---|
| Total, datas corretas | 345.449; 644.440 | 285.146; 481.800 | 221.541; 494.041 | 233.846; 485.749 |
| Total, datas invertidas | 274.338; 550.806 | 232.798; 384.538 | 159.204; 378.805 | 169.523; 372.116 |
| Sem "Posto de trabalho", datas corretas | 85.803; 107.659 | 75.254; 91.885 | 72.229; 88.160 | 69.076; 86.767 |

Em todos os casos o último valor (naive) é o pior comparador e as médias e medianas sem tendência vencem com folga, o que é esperado em série com autocorrelação próxima de zero e cauda pesada. O snapshot atual reporta R² negativo em todos os modelos com valor numérico e MAPE entre 120% e 404%, resultado coerente com essa estrutura e não apenas com falha de ajuste. O RMSE de 84.122,04 do LSTM no snapshot não é comparável aos valores acima, porque vem de outro holdout, de série com datas invertidas e com tratamento de outliers.

## 4. Problemas de desenho e melhorias propostas

1. Alvo tratado como série isolada e sem covariáveis reais. O desenho atual trata o custo como uma série univariada com regressores que não são reais (seção 5). Melhoria: dois modelos com covariáveis observadas, descritos na seção 5, e separação dos eventos de contratação, que têm calendário próprio (dezembro e janeiro).
2. Modelo gaussiano sobre soma de cauda pesada. Melhoria: família adequada a custo não negativo e assimétrico (Tweedie ou GAMLSS lognormal/gama), com saída distribucional e quantis de 50%, 90% e 95% para reserva orçamentária em lugar de previsão pontual, e cauda avaliada por teoria do valor extremo (Peaks-over-Threshold e Pareto generalizada) como análise complementar. O RMSE deixa de ser o critério de seleção.
3. Tratamento de outliers que remove o fenômeno de interesse. A mediana móvel com |z| > 3 apaga justamente os eventos de maior custo, que são os que determinam o orçamento. Melhoria: não substituir caudas; usar transformação logarítmica ou Box-Cox apenas como componente de modelagem e preservar os valores originais na avaliação.
4. Métricas inadequadas. MAPE, R² e RMSE comparam mal séries de cauda pesada com meses de valor muito baixo (4 meses abaixo de R$ 5 mil). Melhoria: pinball loss, CRPS e cobertura empírica dos intervalos, mais RMSSE e comparação com média e mediana históricas como comparadores obrigatórios, com Diebold-Mariano corrigido por Harvey-Leybourne-Newbold.
5. Horizonte e granularidade. Com ACF de lag 1 próximo de zero no mensal e coeficiente de variação de 0,94 no trimestral, previsões mensais agregam pouca informação. Melhoria: avaliar horizontes trimestral e anual (reserva orçamentária anual), e testar o mensal apenas como desagregação proporcional.
6. Relação com a quantidade de chamados não explorada. Melhoria: incluir a quantidade de chamados como covariável do custo (valor observado no ajuste e distribuição preditiva da previsão 1 na projeção) e medir sua contribuição por ablação, comparando o custo com e sem a quantidade; verificar, comparando extrações sucessivas da base, se a queda de OS em 2026 é defasagem de registro (as extrações anteriores não foram encontradas nos repositórios lidos) e, enquanto isso não for esclarecido, tratar os meses recentes como possivelmente incompletos.
7. Atribuição temporal. O custo é lançado no mês de abertura, mas o gasto ocorre na execução ou no pagamento. Melhoria: se a base tiver data de conclusão ou de empenho (o motor de ODS usa `COL_DATA_CONCLUSAO`; a existência da coluna na base não foi verificada), construir a série pela data de execução ou de empenho e comparar com a de abertura.
8. Valores nominais. Em série de 2017 a 2026, o nível nominal mistura inflação com demanda. Melhoria: deflacionar por índice oficial (IPCA ou INCC; série e fonte a verificar no IBGE ou na FGV antes do uso) e comparar resultados nominais e reais.
9. Meses removidos pelo filtro de soma positiva. Melhoria: reindexar para o calendário completo, registrar explicitamente os meses sem custo registrado (zero ou ausente) e testar se o pipeline trata a série como contígua; para recortes esparsos (41 a 85 pontos), usar modelos de demanda intermitente.
10. Previsão independente por 31 recortes. Cada recorte é modelado separadamente, sem consistência entre níveis e com vencedor "In-sample" em categorias. Melhoria: abordagem hierárquica (total, campus e tipo, categoria) com reconciliação (por exemplo, proporções históricas ou mínimos quadrados) e restrição de recortes a séries com número mínimo de eventos.
11. Datas. Corrigir o parse (formato ISO explícito, falha ruidosa) em `extrair_serie_custo`, `construir_serie_custo` e no restante do motor, e reexecutar antes de qualquer conclusão.
12. Qualidade dos artefatos do repositório de custos. Os arquivos `previsao_custo_*.json` estão com codificação corrompida ("PerÃ­odo", "RMSE_MÃ©dio_CV"); o ADF do snapshot de chamados é gravado como data pelo Google Sheets, e o mesmo risco existe nas abas de custo. Melhoria: gravar estatísticas como número com formato explícito ou como texto e recodificar os JSON.

## 5. Desenho proposto: duas previsões com covariáveis

### 5.1 Estado das covariáveis nos repositórios

1. Precipitação: o arquivo `dados/contexto_sazonal.json` tem 116 linhas, todas marcadas "(valor-exemplo, preencher com dado real)". O código que as gera (`gerar_contexto_sazonal_padrao`, linhas 399 a 410 do motor de chamados) usa `np.random.uniform(30, 250)` com semente fixa, ou seja, a precipitação usada pelos modelos de chamados e de custos é aleatória e não observada. Isso explica o resultado nulo do teste de Granger para chuva (p = 0,38) e torna sem valor qualquer inferência sobre efeito de chuva nos snapshots atuais, incluindo as exógenas do SARIMAX, do Gradient Boosting e do LSTM. A série é global, não por campus.
2. Período letivo: é uma regra fixa por mês (letivo em março a junho e agosto a dezembro; não letivo em janeiro, fevereiro e julho), idêntica em todos os anos e para todos os campi. Na prática é uma variável binária de mês, sem relação com o calendário acadêmico real, e seu "efeito" (p = 0,013 no lag 5) não pode ser separado da sazonalidade, que por sua vez está contaminada pelo erro de datas (seção 1.1 do plano). Não foi verificado se o calendário real da instituição coincide com essa regra.
3. Área construída e área total: valores anuais globais (2015 a 2026) em `dados/area_manutencao.json`, constantes dentro do ano, sem detalhamento por campus; as áreas de 2023 e 2024 são idênticas, o que pode indicar valor repetido.
4. Número de pessoas (estudantes, docentes, técnicos, terceirizados): não existe em nenhum repositório lido. Informação insuficiente para verificar a fonte.
5. Campus: disponível na base (Jorge Amado, Paulo Freire, Sosígenes Costa, Reitoria; Jequié tem 11 chamados e fica fora). Os quatro campi principais têm médias mensais de 21 a 39 chamados e correlação de 0,70 a 0,90 com o total, o que permite um painel de cerca de 420 observações campus-mês desde 2018.
6. Outras covariáveis possíveis, sem dados nos repositórios: calendário de contratos de manutenção preventiva, eventos institucionais, obras entregues, idade das edificações, indicadores de temperatura e umidade.

### 5.2 Previsão 1: quantidade de chamados

Alvo: contagem mensal de chamados por campus (painel) e total. Covariáveis: mês e ano (efeito sazonal e tendência), precipitação observada por campus (estação meteorológica mais próxima, a definir com o autor), número de pessoas por campus e período, período letivo do calendário real de cada campus, área construída por campus e ano, e campus como efeito fixo ou aleatório. Modelo: regressão binomial negativa ou GAM com família binomial negativa, com termo autorregressivo ou de nível local, comparada a ETS, Theta, SARIMAX e Gradient Boosting direto. Como a razão variância/média é de 10,7 a 14,2 no total, a família Poisson é inadequada. A separação entre preventiva e corretiva deve ser testada, porque a preventiva segue programação contratual.

### 5.3 Previsão 2: custo

Alvo: custo mensal por campus (soma dos valores das OS lançadas no mês de abertura do chamado) e total, com os eventos de contratação ("Posto de trabalho") modelados à parte. Covariáveis: as mesmas da previsão 1 e a quantidade de chamados. Para a distribuição do custo, que tem zeros em alguns recortes, cauda pesada e coeficiente de variação de 1,3 a 1,8, recomenda-se modelo Tweedie (composto Poisson-gama) ou GAMLSS com família lognormal ou gama, comparado a ETS, Gradient Boosting e à média e mediana históricas.

Tratamento da quantidade de chamados no custo: no ajuste, usa-se a quantidade observada; na projeção, usa-se a distribuição preditiva da previsão 1 (amostras simuladas), de modo que a incerteza da quantidade se propague ao custo. A contribuição da quantidade é medida por ablação (custo com e sem a quantidade) e por teste de Diebold-Mariano corrigido por Harvey-Leybourne-Newbold. Uma versão alternativa, com a quantidade real do mês (oráculo), dá o limite superior do ganho possível com a quantidade.

### 5.4 Avaliação comum

Rolling-origin com no mínimo 24 origens, horizontes de 1, 3, 6 e 12 meses, e agregação trimestral e anual do custo. Métricas: para a quantidade, MASE, RMSSE, CRPS e cobertura; para o custo, pinball loss, CRPS e cobertura dos intervalos, com quantis de 50%, 90% e 95% para reserva orçamentária. Comparadores obrigatórios: média histórica, média e mediana de 12 meses. Análises de sensibilidade: janela (2018 e 2021 em diante), com e sem "Posto de trabalho", e covariáveis reais contra covariáveis removidas.

### 5.5 Dados novos necessários

1. Série de precipitação mensal por campus de estação oficial (a fonte e a estação devem ser definidas; a disponibilidade e o formato de acesso não foram verificados).
2. Número de estudantes, docentes, técnicos e terceirizados por campus e período.
3. Calendário acadêmico real por campus e ano.
4. Área construída e total por campus e ano, com conferência dos valores repetidos de 2023 e 2024.
5. Confirmação do que representa a data de abertura para o custo e, se existir, data de execução ou de empenho da OS.

### 5.6 Resultado preliminar de verificação (somente com o que existe hoje)

Em 24 origens rolling-origin sobre a série global desde 2018 (datas corretas), regressões lineares no logaritmo com as covariáveis disponíveis não superaram a média histórica. Para a quantidade de chamados, o RMSE da média histórica foi 26,1 e o dos modelos com tendência, período letivo, dummies de mês e chuva sintética ficou entre 29,1 e 39,3. Para o custo, o RMSE da média histórica foi 485.749 no total e 86.767 sem "Posto de trabalho", contra 485.325 e 89.924 do melhor modelo com quantidade real, período letivo e tendência. O resultado reflete covariáveis pobres, série global e modelo simples, e serve apenas para calibrar expectativas: o ganho dependerá das covariáveis reais por campus e do painel, que ainda não existem.

## 6. Ordem sugerida e dependências

1. Corrigir o parse de datas no hub (prioridade única, comum ao Artigo 2).
2. Confirmar com o autor o rótulo "Posto de trabalho" e a defasagem de registro das OS recentes (o significado da coluna Q como valor de OS já foi esclarecido).
3. Reunir as covariáveis reais por campus (precipitação, pessoas, calendário letivo, área) e reconstruir as séries de quantidade e custo em painel.
4. Executar comparadores simples, as duas previsões da seção 5 e a avaliação probabilística em horizontes mensal, trimestral e anual.
5. Só então decidir se o Artigo 3 mantém a comparação multimodelo do Artigo 2 ou adota o enquadramento de reserva orçamentária sob cauda pesada.

## 7. Limites desta análise

1. Não foram ajustados modelos; os resultados são descrições da série e de comparadores simples.
2. A política de preenchimento das OS, a defasagem de registro e a existência de data própria da OS, de conclusão ou de empenho na base não puderam ser verificadas (a data usada é a abertura do chamado).
3. A interpretação de "Posto de trabalho > Contratação" como evento contratual é inferida do rótulo.
4. O índice de Hill é indicativo e depende do limiar de 5%.
5. O repositório `malha-previsao-filtros`, que gera os recortes, não foi lido; as observações sobre recortes usam apenas os snapshots do hub.
6. Fontes de deflatores não foram consultadas.
