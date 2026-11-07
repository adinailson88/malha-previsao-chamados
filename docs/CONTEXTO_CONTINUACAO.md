# Contexto de continuação para o Claude executado no PC do autor

Documento de passagem de trabalho, escrito em 03/11/2026 ao fim de uma sessão em nuvem cujo saldo de créditos expira em 05/11/2026. A continuação será feita pelo autor com o Claude no computador local. Leia este arquivo, `AGENTS.md`, `docs/PLANO_PROXIMO_ARTIGO.md` e `docs/DIAGNOSTICO_SERIE_CUSTOS.md` antes de qualquer alteração. Quando um dado não puder ser verificado, declare: `Informação insuficiente para verificar.`

## 1. Objetivo

Decidir e preparar o próximo artigo do doutorado de Adinailson Guimarães de Oliveira (PPG Biossistemas, UFSB). O candidato recomendado é A, previsão de chamados de manutenção predial, com duas previsões: (1) quantidade mensal de chamados e (2) custo mensal, ambos em função de covariáveis (mês, ano, chuva, número de pessoas, período letivo, área construída, campus e outras), com a quantidade de chamados entrando também como covariável do custo. O candidato B (aprendizado contínuo da classificação) fica como reserva por risco alto de fatiamento em relação ao artigo de classificação enviado ao RAP. Não se modela conversão de chamado em ordem de serviço.

## 2. Estado dos repositórios (03/11/2026)

1. `adinailson88/malha-previsao-chamados` (este): PR #4 mergeado (plano em `docs/PLANO_PROXIMO_ARTIGO.md`). PR #5 (diagnóstico de custos, covariáveis, scripts, workflow e este documento) pode estar aberto ou mergeado; confira com `git log origin/main` antes de assumir.
2. `adinailson88/malha-ia` (hub): não foi alterado. É a fonte da base `CHAMADOS` e dos motores que escrevem na planilha.
3. `adinailson88/malha-previsao-custos` (Artigo 3): não foi alterado; contém JSON com codificação corrompida.
4. `adinailson88/classificacao-chamados`: apenas lido (branch `claude/xenodochial-nightingale-81823d`).

## 3. Achados críticos (verificados)

1. Inversão de dia e mês nas datas: `extrair_serie_temporal` (e as funções equivalentes de custos e ODS) cai em `pd.to_datetime(..., dayfirst=True)` quando a data está em formato ISO, o que troca dia e mês para dias menores ou iguais a 12. A série "Quantidade Real" do último snapshot válido de 30/10/2026 reproduz exatamente (RMSE 0,0) a contagem com essa inversão. Todos os resultados de previsão publicados até agora são inválidos. Reprodução: `python scripts/diagnostico/serie_chamados_inversao_datas.py <caminho>/malha-ia/dados/chamados.json`.
2. `previsao_temporal.json` e `previsao_detalhes.json` estão vazios (`[[""]]`) no hub desde 02/11/2026.
3. Sazonalidade espúria: com as datas corretas o ACF de lag 12 da contagem é próximo de zero (-0,02) e médias simples têm RMSE em torno de 26 nos últimos 24 meses; o pico de maio e o vale de dezembro eram artefato da inversão.
4. Covariáveis atuais não são dados reais: a precipitação de `dados/contexto_sazonal.json` vem de `np.random.uniform(30, 250)` com semente fixa (116 linhas marcadas "valor-exemplo"); o período letivo é regra fixa por mês; a área é anual e global.
5. Custo: o valor da coluna Q é o valor das ordens de serviço, presentes em 16,5% dos chamados (2.402 de 14.580); 93 chamados de "Posto de trabalho" respondem por 52,6% do valor; cauda muito pesada; correlação mensal entre quantidade e custo sem "Posto de trabalho" de 0,04; regressões simples com quantidade real não superaram a média histórica. Reprodução: `scripts/diagnostico/serie_custos.py` e `regressao_covariaveis_teste.py`.
6. `chamados.json` do hub tem 69,9% de linhas vazias (33.838 de 48.418) e 30 colunas, 12 sem nome.

## 4. Decisões do autor

1. Chuva: usar a soma mensal (mm) por cidade, a partir de dado da internet. Não sabe se prefere estação do INMET ou reanálise; ficou combinado começar pela reanálise (Open-Meteo, base ERA5, por coordenada do município) e comparar com INMET depois, se houver estação.
2. Pessoas por campus: não existe na planilha; usar dados simulados marcados `SIMULADO` e substituir pelos reais depois. Projeção de anos futuros: último valor mais 5% ao ano.
3. Calendário letivo: o da UFSB (buscar na internet; a UFSB adotou regime semestral em 2024, após regime quadrimestral até 2023, segundo notícia institucional ainda não conferida na resolução).
4. Área construída e total: usar a aba "Área Manutenção" (global, anual); se faltar, projeção com +5% ao ano (2027 = 2026 + 5%).
5. Os dados ficam na planilha CHAMADOS (https://docs.google.com/spreadsheets/d/1VgHY6NmCQLtA3lcfQAzGIRqJFZGHwcGhZ4zaXkqOmz4/edit); o repositório lê a planilha e o autor não quer editar o GitHub manualmente. O autor pretende conduzir as próximas etapas com o Claude no próprio computador.
6. Estilo de texto: português, prosa técnica impessoal, sem travessão, sem frases curtas de remate, tabelas somente onde comparam.

## 5. Restrições permanentes

1. Não alterar `malha-ia`, seus workflows ou secrets sem aprovação explícita; propor a alteração por escrito.
2. Não criar nem alterar secrets; as rotinas deste repositório não usam credenciais.
3. Não fazer push direto na `main`; trabalhar em branch e abrir PR somente quando o autor pedir.
4. Não duplicar `dados/chamados.json` neste repositório.
5. Não declarar dado simulado, pendente ou ausente como resultado de artigo; `python scripts/gerar_covariaveis.py --verificar --modo artigo` deve passar antes de qualquer resultado.
6. Referências bibliográficas: citar só o que for verificável; os itens marcados "DOI não encontrado" em `docs/PLANO_PROXIMO_ARTIGO.md` precisam ser conferidos no editor.

## 6. Pendências em ordem de prioridade

1. Parse de datas em `malha-ia`: correção feita em 03/11/2026 e mergeada (PR https://github.com/adinailson88/malha-ia/pull/6), com `parse_data_abertura`, contagem de descartes e `tests/test_parse_datas.py` (`python -m unittest tests.test_parse_datas -v`). Cobre `motor_previsao_chamados.py`, `motor_previsao_custos.py`, `motor_previsao_filtros.py` e `motor_ods.py`. Falta: reexecutar os workflows `2A - Previsao Global Chamados`, de custos e de filtros para regenerar as abas (as previsões atuais usam a série invertida; `PREVISAO_TEMPORAL` está vazio), e replicar a correção nas cópias dos motores em `malha-previsao-chamados` (`motor_previsao_chamados.py`) e `malha-previsao-custos` (`motor_previsao_custos.py`). Com a correção, a série de chamados passa a começar em 06/2015 (primeiro chamado real) e tem 137 meses até 10/2026.
2. Criar na planilha as abas `COV_PESSOAS`, `COV_AREA_CAMPUS`, `COV_CALENDARIO` e, se quiser, `COV_PRECIPITACAO`, copiando os modelos de `dados_externos/modelos_abas_planilha/`, e executar `python scripts/sincronizar_covariaveis_planilha.py --exigir`. Se o Apps Script não servir esses nomes de aba, ajustar o script do Apps Script (o código dele não está nos repositórios).
3. Executar `python scripts/coletar_precipitacao.py` (ou o workflow `Sincronizar covariaveis`) e conferir o CSV gerado; verificar com o autor se prefere estação do INMET.
4. Baixar os PDFs de calendário da UFSB (página `ufsb.edu.br/acesso-informacao/documentos/109-documentos-academicos/402-calendarios`) e preencher `COV_CALENDARIO` (início e término por período; variável final: fração de dias do mês em período letivo).
5. Área por campus: já existe no repositório `malha-ods-esg`, arquivo `dados/patrimonio_imobiliario_campus_ano.json` (colunas `Area_Utilizacao_m2` e `Area_Terreno_m2`, campi CJA, CPF, CSC e Reitoria, de 2015 a 2025, fonte: planilha Google "Patrimônio Imobiliário", aba "Patrimônio Imobiliário1"). A soma de `Area_Utilizacao_m2` entre campi coincide com a área construída global usada aqui (`dados/area_manutencao.json`): 0,0% de diferença de 2015 a 2021, +0,3% de 2022 a 2024 e +4,8% em 2025, forte indício de que é a área construída por campus (equivalência e mapeamento CJA, CPF, CSC para Jorge Amado, Paulo Freire e Sosígenes Costa a confirmar com o autor). Falta área de 2026 (projetar com +5%) e de Maria Felipa. Ainda faltam dados reais de pessoas (estudantes, docentes, técnicos, terceirizados).
6. Implementar o experimento descrito em `docs/PLANO_PROXIMO_ARTIGO.md` (seções 2.7 e 4.5) e `docs/DIAGNOSTICO_SERIE_CUSTOS.md` (seção 5): rolling-origin com no mínimo 24 origens, comparadores simples, MASE, RMSSE, CRPS, pinball, cobertura, Diebold-Mariano com correção de Harvey-Leybourne-Newbold.
7. Organização do repositório (itens da seção 5 do plano, nenhum executado): fundir ou remover `previsao_chamados_global.yml`, reduzir o cron de 30 minutos de `atualizar-dados-hub.yml`, mover `Referência Bibliográfica - Drive/` para `docs/referencias/`, restringir `pages.yml`, corrigir `CITATION.cff` (aponta para `adinailson88-jpg`), escolher licença, criar `tests/`.
8. Perguntas ainda abertas ao autor: o rótulo "Posto de trabalho > Contratação" é evento contratual? A queda de ordens de serviço em 2026 é real ou atraso de registro? Existe data de conclusão ou empenho da OS? Qual a relação atual com o orientador e a definição de coautoria (não consta nos repositórios e não foi presumida)? Qual periódico-alvo e qual o Qualis vigente (consultar a Plataforma Sucupira)?

## 7. Como executar no Windows (PowerShell)

Os scripts novos usam apenas a biblioteca padrão do Python (3.11 ou 3.12 recomendado).

```powershell
git clone https://github.com/adinailson88/malha-previsao-chamados
git clone https://github.com/adinailson88/malha-ia
cd malha-previsao-chamados
python scripts\coletar_precipitacao.py --selftest
python scripts\sincronizar_covariaveis_planilha.py --selftest
python scripts\gerar_covariaveis.py
python scripts\gerar_covariaveis.py --verificar
python scripts\diagnostico\serie_custos.py ..\malha-ia\dados\chamados.json
```

Na máquina do autor, os hosts de Open-Meteo, INMET, NASA POWER e `ufsb.edu.br`, bloqueados na sessão em nuvem, provavelmente estão acessíveis; a coleta de chuva e a leitura da planilha ainda não foram executadas com dados reais.

## 8. Mapa de arquivos criados nesta rodada

1. `docs/PLANO_PROXIMO_ARTIGO.md`: inventário, diagnóstico de A, comparação A contra B, estrutura do artigo, particionamento proposto.
2. `docs/DIAGNOSTICO_SERIE_CUSTOS.md`: série de custos, covariáveis e desenho das duas previsões.
3. `dados_externos/`: `config_covariaveis.json`, `area_global_projetada.csv`, `pessoas_por_campus_SIMULADO.csv`, `calendario_letivo_ufsb.csv` (pendente), `modelos_abas_planilha/` e `README.md`.
4. `scripts/coletar_precipitacao.py`, `scripts/sincronizar_covariaveis_planilha.py`, `scripts/gerar_covariaveis.py` e `scripts/diagnostico/` (análises reproduzíveis, somente leitura).
5. `.github/workflows/sincronizar-covariaveis.yml`: rotina diária e sob demanda, sem secrets.

## 9. Eixo ODS/ESG (trabalho paralelo)

O terceiro trabalho do ecossistema está em `adinailson88/malha-ods-esg` (plano em `docs/PLANO_ARTIGO_ODS_ESG.md` e contexto em `docs/CONTEXTO_CONTINUACAO.md` daquele repositório). Achados que também afetam os Artigos 2 e 3: a área por campus existe lá; o valor da coluna Q concentra 50% a 61% em chamados "Posto de trabalho > Contratação" em cada campus; e a criticidade parece ser lida na coluna errada pelo `motor_ods.py` (índice 30 em vez de 29).
