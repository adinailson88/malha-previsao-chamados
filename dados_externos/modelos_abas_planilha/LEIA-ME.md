# Modelos de abas para a planilha

Cada arquivo `.csv` desta pasta é o cabeçalho (e as linhas a preencher) de uma aba da planilha `CHAMADOS`. Crie a aba com o nome do arquivo (por exemplo `COV_PESSOAS`), cole o conteúdo e preencha. O repositório lê as abas pelo endpoint do Apps Script, sem credenciais, e grava os CSVs em `dados_externos/`.

1. `COV_PESSOAS`: pessoas por campus e ano (estudantes, docentes, técnicos, terceirizados). Linhas de 2018 a 2026 já estão listadas; deixe vazio o que não souber, mas dados vazios impedem o uso em artigo.
2. `COV_AREA_CAMPUS`: área construída e total por campus e ano.
3. `COV_CALENDARIO`: um registro por período letivo (`periodo`, `inicio`, `termino` em AAAA-MM-DD ou DD/MM/AAAA). Use `Todos` em `campus` quando o calendário for o mesmo para todos.
4. `COV_PRECIPITACAO` (opcional): `mes` (AAAA-MM-DD, primeiro dia), `campus`, `precip_total_mm`, para substituir a coleta automática.

Os nomes dos campi devem ser exatamente: `Campus Jorge Amado`, `Campus Paulo Freire`, `Campus Sosígenes Costa` e `Reitoria`.
