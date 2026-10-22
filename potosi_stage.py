"""Stage 1 (runs where the TePaske-Klein files are): Potosí ledger -> two small CSVs.
raw/potosi_annual.csv: one row per year, silver taxes and implied registered silver.
raw/potosi_categories.csv: one row per year and revenue group."""
import glob, re, numpy as np, pandas as pd
from potosi import parse, annual, ENS

df = parse(glob.glob('raw/Pot*.xls')[0])
pot, items = annual(df, 'Potosi')
pot.to_csv('raw/potosi_annual.csv', index=False)

def group(item):
    s = item.upper()
    if any(k in s for k in ['EXISTENCIA', 'VENIDO DE FUERA', 'OTRAS TESORERIAS', 'DEPOSITO', 'PRESTAMO', 'EMPRESTITO',
                            'DEBIDO', 'COBRADO VALORES', 'RESTOS', 'ALCANCES', 'REINTEGRO']):
        return 'transfers, loans and balances'
    if ('QUINT' in s or 'DIEZM' in s) and 'ORO' not in s and 'LABRAD' not in s: return 'silver taxes'
    if 'AZOGUE' in s or 'MERCUR' in s: return 'mercury sales'
    if 'TRIBUT' in s or 'YANACONA' in s: return 'tribute'
    if any(k in s for k in ['BARRA', 'CASA DE MONEDA', 'SENOREAGE', 'SENOREAJE', 'LABRAD', 'ENSAYE', 'FUNDICION']): return 'mint and bullion'
    if 'ALCABALA' in s: return 'sales tax (alcabala)'
    return 'other revenue'
items['group'] = items.item.map(group)
rows = []
for (y1, m1, y2, m2), g in items.groupby(['y1', 'm1', 'y2', 'm2']):
    yrs = list(range(y1, y2 + 1)) if y2 >= y1 else [y1]
    s = g.groupby('group').pesos.sum()
    for y in yrs:
        for k, v in s.items():
            rows.append(dict(year=y, group=k, pesos=v / len(yrs)))
cat = pd.DataFrame(rows).groupby(['year', 'group'], as_index=False).pesos.sum()
cat['pesos'] = cat.pesos.round(1)
cat.to_csv('raw/potosi_categories.csv', index=False)
print(len(pot), len(cat), cat.group.value_counts().to_dict())
