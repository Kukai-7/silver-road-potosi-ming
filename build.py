"""Build the Silver Road dataset: Potosí silver (TePaske & Klein treasury accounts), Chinese rice prices in silver
(Peng, Liu, Kishimoto via GPIH) and the Ming Crisis Atlas, 1560-1644 and beyond."""
import re, json, os, xlrd, numpy as np, pandas as pd

RAW, OUT = 'raw', 'out/data'
os.makedirs(OUT, exist_ok=True)

# ------------------------------------------------------------------ Potosí
pot = pd.read_csv(f'{RAW}/potosi_annual.csv')
pot = pot.drop(columns='caja')
full = pd.DataFrame({'year': range(int(pot.year.min()), int(pot.year.max()) + 1)})
pot = full.merge(pot, on='year', how='left')
pot['account_missing'] = pot.period.isna()
# an account with no silver-tax line (1643) says nothing about output: keep the income, blank the estimate
pot['no_silver_tax_line'] = pot.period.notna() & (pot.silver_tax_pesos.fillna(0) == 0)
pot.loc[pot.no_silver_tax_line, ['implied_registered_silver_pesos', 'implied_registered_silver_tonnes']] = np.nan
# a year whose implied output is more than 1.6 times the median of its neighbours likely bundles arrears of missing years
med = pot.implied_registered_silver_tonnes.rolling(7, center=True, min_periods=3).median()
pot['likely_bundled_arrears'] = (pot.implied_registered_silver_tonnes > 1.6 * med).fillna(False)
clean = pot.implied_registered_silver_tonnes.where(~pot.likely_bundled_arrears)
pot['silver_tonnes_5yr_mean'] = clean.rolling(5, center=True, min_periods=3).mean().round(2)
for c in ['treasury_income_pesos', 'silver_tax_pesos', 'implied_registered_silver_pesos']:
    pot[c] = pot[c].round(1)
pot.to_parquet(f'{OUT}/potosi_annual.parquet', index=False)

rev = pd.read_csv(f'{RAW}/potosi_categories.csv')
rev.to_parquet(f'{OUT}/potosi_revenue.parquet', index=False)

# ------------------------------------------------------------------ Chinese rice prices in silver (GPIH workbook)
wb = xlrd.open_workbook(f'{RAW}/China_rice_961-1910.xls')
rows = []
pg = wb.sheet_by_name('Peng rice series')
mode = None
for r in range(pg.nrows):
    a = str(pg.cell_value(r, 0)).strip()
    if a.startswith('(A.)'): mode = 'peng'
    if a.startswith('(B)'): mode = 'liu'
    m = re.match(r'^(\d{3,4})-(\d{2,4})$', a)
    if not m or mode is None: continue
    y1 = int(m.group(1)); e = m.group(2)
    y2 = int(e) if len(e) == 4 else int(str(y1)[:len(str(y1)) - len(e)] + e)
    if mode == 'liu' and y2 < y1: y2 = y1 + 9
    if mode == 'liu' and (y2 - y1) > 10: y2 = y1 + 9
    v = pg.cell_value(r, 6 if mode == 'peng' else 2)
    if not isinstance(v, float): continue
    rows.append(dict(source='Peng Xinwei, reign averages' if mode == 'peng' else 'Liu Guanglin, decade averages',
                     region='China (empire-wide averages)' if mode == 'peng' else 'China (Liu compilation)',
                     start_year=y1, end_year=y2, grams_silver_per_liter=round(v, 4)))
ks = wb.sheet_by_name('Kishmoto rice series')
for r in range(5, ks.nrows):
    y = ks.cell_value(r, 0); v = ks.cell_value(r, 6)
    if isinstance(y, float) and isinstance(v, float):
        rows.append(dict(source='Kishimoto Mio, annual', region='Suzhou area (Lower Yangzi)', start_year=int(y), end_year=int(y),
                         grams_silver_per_liter=round(v, 4)))
rice = pd.DataFrame(rows)
rice.to_parquet(f'{OUT}/china_rice_silver.parquet', index=False)

# ------------------------------------------------------------------ joint annual panel, 1560-1644
ming = pd.read_parquet(f'{RAW}/ming_annual.parquet')
yr = pd.DataFrame({'year': range(1560, 1645)})
p = pot[['year', 'implied_registered_silver_tonnes', 'silver_tonnes_5yr_mean', 'likely_bundled_arrears', 'tax_regime']]
yr = yr.merge(p, on='year', how='left')
keep = ['year', 'reign', 'n_places_reporting', 'share_drought', 'share_flood', 'share_famine', 'share_cannibalism',
        'share_war_banditry', 'places_famine', 'enso_event', 'china_temp_anomaly_c']
yr = yr.merge(ming[keep], on='year', how='left')
liu = rice[rice.source.str.startswith('Liu')]
def liu_price(y):
    m = liu[(liu.start_year <= y) & (liu.end_year >= y)]
    return m.grams_silver_per_liter.iloc[0] if len(m) else np.nan
yr['rice_g_silver_per_liter_decade'] = yr.year.map(liu_price)
kis = rice[rice.source.str.startswith('Kishimoto')].groupby('start_year').grams_silver_per_liter.mean()
yr['rice_g_silver_per_liter_suzhou'] = yr.year.map(kis)
yr.to_parquet(f'{OUT}/ming_silver_annual.parquet', index=False)

# ------------------------------------------------------------------ places and routes of the silver trade (curated)
PLACES = [
    ('Potosi', -19.589, -65.753, 'silver mine', 'Cerro Rico; silver found in 1545'),
    ('Arica', -18.48, -70.32, 'port', 'Pacific outlet for Potosi silver'),
    ('Lima and Callao', -12.05, -77.15, 'port and capital', 'Viceroyalty of Peru'),
    ('Panama', 8.95, -79.53, 'port', 'Isthmus crossing to the Caribbean'),
    ('Portobelo', 9.55, -79.65, 'port', 'Caribbean fair for the Tierra Firme fleet'),
    ('Havana', 23.14, -82.36, 'port', 'Fleets gather before crossing the Atlantic'),
    ('Seville', 37.39, -5.99, 'port and treasury', 'Casa de Contratacion, monopoly port of the Indies trade'),
    ('Zacatecas', 22.77, -102.58, 'silver mine', 'Mexican silver, from 1546'),
    ('Acapulco', 16.85, -99.88, 'port', 'Galleon port for Manila'),
    ('Manila', 14.59, 120.98, 'port', 'Spanish city from 1571; Chinese junks bring silk for silver'),
    ('Yuegang (Moon Harbour)', 24.42, 117.85, 'port', 'Fujian port opened to private trade in 1567'),
    ('Macau', 22.19, 113.54, 'port', 'Portuguese base from 1557'),
    ('Guangzhou', 23.13, 113.26, 'market', 'Canton fairs supplying Macau'),
    ('Nagasaki', 32.75, 129.88, 'port', 'Portuguese, then Dutch and Chinese trade'),
    ('Iwami Ginzan', 35.11, 132.44, 'silver mine', 'Japanese silver, booming from the 1530s'),
    ('Beijing', 39.90, 116.40, 'capital', 'Ming court, paid in silver after the Single Whip reforms'),
    ('Lisbon', 38.72, -9.14, 'port', 'Portuguese Carreira da India'),
    ('Goa', 15.50, 73.83, 'port', 'Estado da India'),
]
places = pd.DataFrame(PLACES, columns=['place', 'latitude', 'longitude', 'role', 'note'])
places.to_parquet(f'{OUT}/places.parquet', index=False)
ROUTES = {
    'Potosi to Seville (Atlantic)': ['Potosi', 'Arica', 'Lima and Callao', 'Panama', 'Portobelo', 'Havana', 'Seville'],
    'Acapulco to Manila (galleon)': ['Zacatecas', 'Acapulco', 'Manila'],
    'Lima to Acapulco (Pacific coast)': ['Lima and Callao', 'Acapulco'],
    'Manila to China': ['Manila', 'Yuegang (Moon Harbour)'],
    'Japan to China (via Macau)': ['Iwami Ginzan', 'Nagasaki', 'Macau', 'Guangzhou'],
    'Lisbon to Macau (Cape route)': ['Lisbon', 'Goa', 'Macau'],
}
routes = pd.DataFrame([dict(route=k, stops=' > '.join(v)) for k, v in ROUTES.items()])
routes.to_parquet(f'{OUT}/routes.parquet', index=False)
json.dump(ROUTES, open('out/routes.json', 'w'))

stats = dict(potosi_years=int(pot.period.notna().sum()), first=int(pot.year.min()), last=int(pot.year.max()),
             peak_year=int(pot.loc[pot.silver_tonnes_5yr_mean.idxmax(), 'year']), peak_5yr=float(pot.silver_tonnes_5yr_mean.max()),
             rice_rows=len(rice), bundled=pot.loc[pot.likely_bundled_arrears, 'year'].tolist())
json.dump(stats, open('out/stats.json', 'w'), indent=1)
print(stats)
