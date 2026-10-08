import pandas as pd
import numpy as np

COTACOES = 'COTAÇÕES - CASE.xlsx'
SALESFORCE = 'SalesForce - CASE.xlsx'

# 1) Leitura: o cabeçalho de COTAÇÕES está na 3ª linha (header=2)
cot = pd.read_excel(COTACOES, sheet_name='Base', header=2,
    dtype={'ID da Cotação do SAP':str,'Código do Cliente':str,'Material':str,'Cód. Expedição':str})
sf = pd.read_excel(SALESFORCE, sheet_name='Base 2',
    dtype={'ID da Cotação do SAP':str,'Código do Cliente':str,'Material: Código do material':str,'Cód. Expedição':str})

# 2) Limpeza básica do SalesForce: descarta registros sem a chave completa
key_sf = ['ID da Cotação do SAP','Material: Código do material','Cód. Expedição']
sf = sf.dropna(subset=key_sf).copy()

# 3) Deduplicação. Prioriza valores não nulos/não zero; se houver divergência
# entre valores não zero, usa o de maior magnitude (regra conservadora para não subestimar o componente).
def choose_value(s):
    x = pd.to_numeric(s, errors='coerce').dropna()
    if x.empty: return np.nan
    nz = x[x.ne(0)]
    if not nz.empty: return nz.loc[nz.abs().idxmax()]
    return 0.0

sf_dedup = (sf.groupby(key_sf, as_index=False)
              .agg({'Frete Comercial': choose_value, 'Chapa': choose_value}))

# 4) Cruzamento LEFT: garante que a quantidade de linhas da base principal não aumente
sf_dedup = sf_dedup.rename(columns={'Material: Código do material':'Material'})
key = ['ID da Cotação do SAP','Material','Cód. Expedição']
base = cot.merge(sf_dedup, on=key, how='left', validate='one_to_one')

# 5) Tipos
base['Dt. Criação Sol.'] = pd.to_datetime(base['Dt. Criação Sol.'], dayfirst=True, errors='coerce')
base['Var. Preço Proposto'] = pd.to_numeric(base['Var. Preço Proposto'], errors='coerce')

# 6) Recorrência 30 dias: aprovadas + Banda/PrecoFixo + mesmo cliente/material/expedição.
# A linha atual é excluída e a janela é (data_atual - 30 dias) <= data_anterior < data_atual.
base['Qtd. cotações aprovadas 30d'] = 0
base['Soma da variação de desconto 30d'] = 0.0
grp_cols = ['Código do Cliente','Material','Cód. Expedição']
elig = base['Status da Cotação'].eq('Aprovada') & base['TipoCotação'].isin(['Banda','PrecoFixo'])

for _, idx in base.groupby(grp_cols, dropna=False).groups.items():
    idx = list(idx)
    g = base.loc[idx].sort_values('Dt. Criação Sol.')
    approved = g.loc[elig.loc[g.index], ['Dt. Criação Sol.','Var. Preço Proposto']].copy()
    dates = approved['Dt. Criação Sol.']
    vals = approved['Var. Preço Proposto'].fillna(0)
    for i, row in g.iterrows():
        dt = row['Dt. Criação Sol.']
        m = dates.ge(dt - pd.Timedelta(days=30)) & dates.lt(dt)
        base.at[i,'Qtd. cotações aprovadas 30d'] = int(m.sum())
        base.at[i,'Soma da variação de desconto 30d'] = float(vals.loc[m].sum())

# 7) Exportação
base.to_csv('base_consolidada.csv', index=False, encoding='utf-8-sig')
print('Linhas finais:', len(base))
