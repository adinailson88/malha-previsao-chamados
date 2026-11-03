# Covariáveis externas para as previsões de quantidade e custo

Fonte única dos dados editáveis: a [planilha CHAMADOS](https://docs.google.com/spreadsheets/d/1VgHY6NmCQLtA3lcfQAzGIRqJFZGHwcGhZ4zaXkqOmz4/edit), nas abas `COV_*` (modelos em `modelos_abas_planilha/`). `scripts/sincronizar_covariaveis_planilha.py` e o workflow `Sincronizar covariaveis` trazem os dados; não é necessário editar o GitHub.

Estas tabelas alimentam os modelos descritos em `docs/DIAGNOSTICO_SERIE_CUSTOS.md` (seção 5). Cada linha traz a origem do dado, e `python scripts/gerar_covariaveis.py --verificar --modo artigo` bloqueia o uso em artigo enquanto houver dado simulado, ausente ou pendente.

| Covariável | Arquivo | Situação em 03/11/2026 | Como completar |
|---|---|---|---|
| Precipitação mensal por campus | `precipitacao_mensal_por_campus.csv` (ainda não gerado) | Ausente: a rede da sessão bloqueia `archive-api.open-meteo.com`, o INMET e a NASA POWER | Executar `python scripts/coletar_precipitacao.py` em máquina com internet; soma mensal (mm) como variável principal e média dos valores diários (mm/dia) como auxiliar |
| Número de pessoas por campus | `pessoas_por_campus_SIMULADO.csv` | Simulado, sem base empírica, apenas para testar o pipeline | Substituir pelos dados reais mantendo as colunas, trocando `origem` para o nome da fonte |
| Calendário letivo | `calendario_letivo_ufsb.csv` | Pendente: o site `ufsb.edu.br` está bloqueado na sessão | Preencher início e término de cada período a partir dos PDFs oficiais de calendário da UFSB |
| Área construída e total | `area_global_projetada.csv` (reserva) e `area_por_campus.csv` (da planilha) | Observada de 2015 a 2026 (global, sem detalhe por campus); 2027 e 2028 projetados com +5% ao ano | Fornecer área por campus e ano |

Observações de método:

1. A precipitação vem de reanálise por coordenada do município (Open-Meteo, base ERA5), e não de estação do INMET; as coordenadas em `config_covariaveis.json` são aproximadas do centro municipal. Se o autor preferir estação do INMET, o código deve ser adaptado e o código da estação conferido em fonte oficial, o que não foi possível verificar.
2. A variável principal é a soma mensal (mm), por decisão do autor em 03/11/2026; a média dos valores diários (mm/dia) fica como auxiliar e é quase proporcional à soma, diferindo apenas pelo número de dias do mês.
3. A UFSB adotou regime semestral em 2024, após regime quadrimestral até 2023 (informação de notícia institucional encontrada em busca, ainda não conferida no documento da resolução). O calendário deve ser modelado como fração de dias do mês em período letivo, o que permite tratar os dois regimes numa só variável.
4. A simulação de pessoas é uma tendência suave e colinear com o tempo; não carrega informação e não deve ser interpretada.
5. A projeção de área e de pessoas usa crescimento composto de 5% ao ano a partir do último ano observado ou simulado. O motor atual repete o último valor de área nos meses futuros; adotar a regra de 5% exige alterar o motor no hub.
