# Case Técnico – Analista de Inteligência de Mercado e Precificação

## Objetivo
Consolidar as bases COTAÇÕES e SalesForce, enriquecer a base principal com Frete Comercial e Chapa, calcular recorrência de aprovações em janela móvel de 30 dias e responder às análises de negócio solicitadas.

## Execução
1. Coloque `COTAÇÕES - CASE.xlsx`, `SalesForce - CASE.xlsx` e `solucao_case.py` na mesma pasta.
2. Instale: `pip install pandas openpyxl numpy`.
3. Execute: `python solucao_case.py`.
4. O script gera `base_consolidada.csv`.

## Premissas adotadas
- O cabeçalho da base COTAÇÕES está na terceira linha da aba Base.
- Cruzamento por ID da Cotação do SAP + Material + Cód. Expedição, usando LEFT JOIN para preservar todas as linhas de COTAÇÕES.
- Linhas do SalesForce sem chave completa são descartadas antes do cruzamento.
- Em duplicidades do SalesForce, valores nulos e zero não prevalecem sobre valores não zero. Havendo mais de um valor não zero divergente, é escolhido o de maior magnitude. A regra é determinística e conservadora, evitando subestimar componentes de preço; deve ser validada com a área em ambiente produtivo.
- Ausência de correspondência no SalesForce permanece nula e não é convertida em zero.
- Cotação aprovada: somente `Status da Cotação = Aprovada`.
- Janela de 30 dias: 30 dias corridos anteriores à `Dt. Criação Sol.` da linha, excluindo a própria linha.
- Recorrência considera apenas tipos `Banda` e `PrecoFixo`, no agrupamento Código do Cliente + Material + Cód. Expedição.
- Nulos em `Var. Preço Proposto` são tratados como zero apenas na soma da janela, preservando o nulo na coluna original.
- Para a análise de concessão, valores negativos de `Var. Preço Proposto` representam redução de preço e são convertidos para magnitude positiva. Valores positivos não são considerados concessão de desconto; nulos equivalem a zero para essa análise.

## Validações
- Base principal: 4.354 linhas.
- O merge final mantém 4.354 linhas.
- Registros sem correspondência no SalesForce continuam na base final.
- Frete ausente é distinto de Frete Comercial = 0.

## Arquivos de entrega
- `solucao_case.py`: preparação obrigatória em Python.
- `base_consolidada.xlsx`: base final enriquecida.
- `analises_case.xlsx`: respostas e resumo executivo dos itens 5.1 a 5.4.
