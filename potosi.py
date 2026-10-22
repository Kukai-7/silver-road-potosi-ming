"""Potosí royal treasury (TePaske and Klein, via El Colegio de México) -> silver taxes and implied registered production."""
import re, glob, xlrd, numpy as np, pandas as pd

ENS = 450 / 272          # one peso ensayado (450 maravedis) in pesos de a ocho (272 maravedis)
G_PER_PESO = 25.56       # grams of fine silver in a peso de a ocho (approximate, pre-1728 standard)

def parse(path):
    sh = xlrd.open_workbook(path).sheet_by_index(0)
    rows, per = [], None
    for r in range(sh.nrows):
        a = str(sh.cell_value(r, 0)).strip()
        m = re.match(r'^(\d{1,2})/(\d{4})-(\d{1,2})/(\d{4})$', a)
        if m:
            per = (int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)))
            continue
        if per is None or not a or a.startswith('TOTAL') or a.startswith('S '):
            continue
        def num(c):
            v = sh.cell_value(r, c)
            return float(v) if isinstance(v, float) else 0.0
        rows.append(dict(m1=per[0], y1=per[1], m2=per[2], y2=per[3], item=a, ocho=num(1), ensayados=num(2), oro=num(3)))
    return pd.DataFrame(rows)

def classify(item):
    s = item.upper()
    if 'LABRAD' in s or 'ORO' in s: return None
    if not ('PLATA' in s or 'PLAT' in s or 'PLAZA' in s): return None
    cobo = 0.0
    m = re.match(r'^(\d(?:\.\d)?)%', s)
    if m: cobo = float(m.group(1)) / 100
    if 'QUINT' in s and 'DIEZM' in s: return ('quinto to diezmo', 0.10 + cobo)
    if 'QUINT' in s: return ('quinto', 0.20 + cobo)
    if 'DIEZM' in s: return ('diezmo', 0.10 + cobo)
    return None

def annual(df, caja):
    df = df.copy()
    df['pesos'] = df.ocho + df.ensayados * ENS
    c = df.item.map(classify)
    df['tax_kind'] = [x[0] if x else None for x in c]
    df['rate'] = [x[1] if x else np.nan for x in c]
    tax = df[df.tax_kind.notna()].copy()
    tax['implied'] = tax.pesos / tax.rate
    # spread multi-year periods evenly over their calendar years
    out = []
    for (y1, m1, y2, m2), g in df.groupby(['y1', 'm1', 'y2', 'm2']):
        yrs = list(range(y1, y2 + 1)) if y2 >= y1 else [y1]
        t = tax[(tax.y1 == y1) & (tax.m1 == m1) & (tax.y2 == y2) & (tax.m2 == m2)]
        for y in yrs:
            out.append(dict(year=y, caja=caja, period=f'{m1}/{y1}-{m2}/{y2}', period_years=len(yrs),
                            treasury_income_pesos=g.pesos.sum() / len(yrs),
                            silver_tax_pesos=t.pesos.sum() / len(yrs),
                            implied_registered_silver_pesos=t.implied.sum() / len(yrs),
                            tax_regime='diezmo' if (t.tax_kind == 'diezmo').any() and not (t.tax_kind == 'quinto').any()
                            else ('quinto' if len(t) else None)))
    a = pd.DataFrame(out).groupby(['year', 'caja'], as_index=False).agg(
        period=('period', 'first'), period_years=('period_years', 'max'), treasury_income_pesos=('treasury_income_pesos', 'sum'),
        silver_tax_pesos=('silver_tax_pesos', 'sum'), implied_registered_silver_pesos=('implied_registered_silver_pesos', 'sum'),
        tax_regime=('tax_regime', 'first'))
    a['implied_registered_silver_tonnes'] = (a.implied_registered_silver_pesos * G_PER_PESO / 1e6).round(2)
    return a, df

if __name__ == '__main__':
    pot, items = annual(parse(glob.glob('raw/Pot*.xls')[0]), 'Potosi')
    print(pot.describe().round(1).to_string())
    print(pot[pot.year.isin([1570, 1580, 1592, 1600, 1610, 1620, 1630, 1640, 1650, 1660, 1700, 1750, 1790])].to_string())
    print(items[items.tax_kind.notna()].groupby('item').pesos.sum().sort_values().tail(15))
