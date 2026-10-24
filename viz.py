import json, os, glob, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Polygon as MPoly
from matplotlib.ticker import FixedLocator, FixedFormatter, NullFormatter
from shapely.geometry import shape, box
from shapely import affinity

for f in glob.glob('fonts/*.otf') + ['/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc']:
    if os.path.exists(f): fm.fontManager.addfont(f)
_n = {f.name for f in fm.fontManager.ttflist}
FONT = next((n for n in ('Noto Sans CJK SC', 'Noto Sans CJK JP') if n in _n), 'DejaVu Sans')
plt.rcParams.update({'font.family': FONT, 'font.size': 10, 'axes.edgecolor': '#BBBBBB', 'axes.linewidth': .6,
                     'xtick.color': '#666666', 'ytick.color': '#666666', 'axes.labelcolor': '#444444', 'text.color': '#1F1F1F',
                     'savefig.dpi': 200})
INK, MID, LIGHT, LAND, PAPER = '#1F1F1F', '#8A8A8A', '#C9C6BF', '#ECE9E3', '#FFFFFF'
RED, RED_SOFT, BLUE, BLUE_SOFT = '#B33A2B', '#E3B5AE', '#2F4B7C', '#B9C4D6'
os.makedirs('out/assets', exist_ok=True)

pot = pd.read_parquet('out/data/potosi_annual.parquet')
rev = pd.read_parquet('out/data/potosi_revenue.parquet')
rice = pd.read_parquet('out/data/china_rice_silver.parquet')
yr = pd.read_parquet('out/data/ming_silver_annual.parquet')
places = pd.read_parquet('out/data/places.parquet').set_index('place')
ROUTES = json.load(open('out/routes.json'))

def title(fig, t, s, y=.95):
    fig.text(.05, y, t, fontsize=15, weight='bold')
    fig.text(.05, y - .045, s, fontsize=9, color='#555555')

# ------------------------------------------------------------------ 1. map, centred on the Pacific
W0, W1, S, N = 40, 368, -42, 58
def sh(lon): return lon + 360 if lon < W0 else lon
clip = box(W0 - 1, S - 1, W1 + 1, N + 1)
land = []
for f in json.load(open('raw/ne_110m_land.geojson'))['features']:
    g = shape(f['geometry'])
    for dx in (0, 360):
        gg = affinity.translate(g, xoff=dx).intersection(clip)
        if not gg.is_empty: land.append(gg)
fig, ax = plt.subplots(figsize=(13, 5.6))
for g in land:
    for p in getattr(g, 'geoms', [g]):
        if p.geom_type == 'Polygon':
            ax.add_patch(MPoly(np.array(p.exterior.coords), closed=True, fc=LAND, ec=LIGHT, lw=.4))

def arc(a, b, bend=.12, n=60):
    (x0, y0), (x1, y1) = a, b
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    dx, dy = x1 - x0, y1 - y0
    cx, cy = mx - dy * bend, my + dx * bend
    t = np.linspace(0, 1, n)[:, None]
    P = (1 - t) ** 2 * np.array([x0, y0]) + 2 * (1 - t) * t * np.array([cx, cy]) + t ** 2 * np.array([x1, y1])
    return P[:, 0], P[:, 1]
STYLE = {'Potosi to Seville (Atlantic)': (BLUE, 1.8, '-', .10), 'Acapulco to Manila (galleon)': (RED, 2.4, '-', -.10),
         'Lima to Acapulco (Pacific coast)': (RED, 1.2, '--', .12), 'Manila to China': (RED, 2.4, '-', .2),
         'Japan to China (via Macau)': (MID, 1.6, '-', .15)}
for r, stops in ROUTES.items():
    if r not in STYLE: continue
    c, lw, ls, bend = STYLE[r]
    pts = [(sh(places.loc[s, 'longitude']), places.loc[s, 'latitude']) for s in stops]
    for a, b in zip(pts[:-1], pts[1:]):
        x, y = arc(a, b, bend)
        ax.plot(x, y, color=c, lw=lw, ls=ls, alpha=.9, solid_capstyle='round', zorder=3)
for p, r in places.iterrows():
    x = sh(r.longitude)
    if not (W0 <= x <= W1): continue
    mine = r.role == 'silver mine'
    ax.scatter(x, r.latitude, s=70 if mine else 22, marker='^' if mine else 'o', c=INK if mine else PAPER,
               edgecolors=INK, lw=.8, zorder=5)
LAB = {'Potosi': ('Potosí', (8, -4), 'left', INK, 10), 'Zacatecas': ('Zacatecas', (6, 4), 'left', INK, 8),
       'Iwami Ginzan': ('Iwami', (6, 4), 'left', INK, 8), 'Seville': ('Seville', (-6, 6), 'right', INK, 8.5),
       'Acapulco': ('Acapulco', (-6, -12), 'right', INK, 8.5), 'Manila': ('Manila', (6, -10), 'left', INK, 8.5),
       'Yuegang (Moon Harbour)': ('Yuegang', (-6, 5), 'right', INK, 8.5), 'Macau': ('Macau', (-6, -10), 'right', INK, 8),
       'Nagasaki': ('Nagasaki', (6, -8), 'left', INK, 8), 'Beijing': ('Beijing', (-6, 4), 'right', INK, 8.5),
       'Havana': ('Havana', (6, 5), 'left', INK, 8), 'Portobelo': ('Portobelo', (8, 2), 'left', INK, 8),
       'Lima and Callao': ('Lima', (-6, -3), 'right', INK, 8), 'Arica': ('Arica', (-6, -8), 'right', MID, 7.5),
       'Goa': ('Goa', (-6, -4), 'right', MID, 7.5)}
for p, (t, off, ha, col, fs) in LAB.items():
    r = places.loc[p]
    ax.annotate(t, (sh(r.longitude), r.latitude), xytext=off, textcoords='offset points', ha=ha, fontsize=fs, color=col, zorder=6)
ax.text(205, 9, 'Manila galleon\nAcapulco to Manila, from 1571', ha='center', fontsize=8.5, color=RED, style='italic')
ax.text(318, 33, 'Spanish treasure fleets', ha='center', fontsize=8.5, color=BLUE, style='italic')
ax.text(141, 30, 'Japanese silver', ha='left', fontsize=8.5, color=MID, style='italic')
ax.text(103, -20, 'To Lisbon via the Cape:\nthe Portuguese route,\nnot drawn', ha='center', fontsize=7.5, color=MID)
ax.set_xlim(W0, W1); ax.set_ylim(S, N); ax.set_aspect(1.05)
ax.set_xticks([]); ax.set_yticks([])
for s_ in ax.spines.values(): s_.set_visible(False)
from matplotlib.lines import Line2D
h = [Line2D([], [], marker='^', ls='', c=INK, ms=8, label='Silver mine'), Line2D([], [], marker='o', ls='', mfc=PAPER, mec=INK, ms=5, label='Port or city'),
     Line2D([], [], c=RED, lw=2.2, label='Pacific route'), Line2D([], [], c=BLUE, lw=1.8, label='Atlantic route')]
ax.legend(handles=h, loc='lower left', frameon=False, fontsize=8.5)
title(fig, 'The silver road, from Potosí to Ming China', 'Main routes of American and Japanese silver towards China, late sixteenth to mid seventeenth century.', y=.96)
fig.text(.05, .03, 'Places and routes: curated for this dataset from standard histories of the trade. Coastline: Natural Earth.', fontsize=7, color=MID)
plt.subplots_adjust(left=.02, right=.98, top=.86, bottom=.06)
fig.savefig('out/assets/map_silver_road.png', facecolor=PAPER); plt.close(fig)

# ------------------------------------------------------------------ 2. timeline: Potosí silver and Chinese rice in silver
fig, ax = plt.subplots(figsize=(12, 5))
p = pot[pot.year <= 1810]
ok = p.implied_registered_silver_tonnes.notna() & ~p.likely_bundled_arrears
ax.bar(p.year[ok], p.implied_registered_silver_tonnes[ok], width=.85, color=LIGHT, lw=0, zorder=1, label='Potosí, registered silver implied by royal taxes (t per year)')
ax.bar(p.year[p.likely_bundled_arrears], np.minimum(p.implied_registered_silver_tonnes[p.likely_bundled_arrears], 240), width=.85,
       color=PAPER, edgecolor=MID, hatch='////', lw=.4, zorder=1, label='Account that likely bundles arrears')
ax.plot(p.year, p.silver_tonnes_5yr_mean, color=INK, lw=1.6, zorder=3, label='Five-year mean')
ax.set_ylim(0, 240); ax.set_ylabel('Tonnes of silver per year')
ax.spines[['top']].set_visible(False)
ax2 = ax.twinx()
liu = rice[rice.source.str.startswith('Liu') & (rice.end_year >= 1540) & (rice.start_year <= 1810)]
for r in liu.itertuples():
    ax2.plot([r.start_year, r.end_year + 1], [r.grams_silver_per_liter] * 2, color=BLUE, lw=2, solid_capstyle='butt', zorder=4)
ax2.plot([], [], color=BLUE, lw=2, label='China, rice in grams of silver per litre (decade mean)')
k = rice[rice.source.str.startswith('Kishimoto')]
ax2.scatter(k.start_year, k.grams_silver_per_liter, s=14, c=BLUE_SOFT, edgecolors=BLUE, lw=.5, zorder=4, label='Suzhou, annual (Kishimoto)')
ax2.set_ylim(0, 1.4); ax2.set_ylabel('Grams of silver per litre of rice', color=BLUE); ax2.tick_params(axis='y', colors=BLUE)
ax2.spines[['top']].set_visible(False)
for x, t in [(1567, ''), (1571, ''), (1573, '1567 to 1573\nYuegang opens,\nManila founded,\nmercury amalgamation'), (1644, 'Fall of\nthe Ming'), (1736, 'Tax cut\nto a tenth')]:
    ax.axvline(x, color=RED, lw=.7, ls=':', zorder=2)
    if t: ax.text(x + 1.2 if x != 1573 else 1546.5, 236, t, fontsize=7.4, color=RED, va='top', ha='left')
ax.set_xlim(1545, 1812)
h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, loc='lower left', bbox_to_anchor=(0, 1.0), ncol=3, frameon=False, fontsize=7.8)
title(fig, 'Silver out of Potosí, and what silver bought in China', 'Potosí peaks in the 1590s and fades after 1650; rice in silver spikes in the crisis of the 1640s, then climbs through the 1700s.', y=.965)
plt.subplots_adjust(left=.07, right=.93, top=.78, bottom=.08)
fig.savefig('out/assets/timeline_silver.png', facecolor=PAPER); plt.close(fig)

# ------------------------------------------------------------------ 3. scatter-plot matrix: made by correlations.py, with r, confidence intervals and p-values

# ------------------------------------------------------------------ 4. what the Potosí treasury lived on
ORDER = ['silver taxes', 'mercury sales', 'mint and bullion', 'tribute', 'sales tax (alcabala)', 'other revenue']
COL = {'silver taxes': RED, 'mercury sales': BLUE, 'mint and bullion': RED_SOFT, 'tribute': BLUE_SOFT, 'sales tax (alcabala)': LIGHT, 'other revenue': '#E6E3DD'}
r = rev[rev.group.isin(ORDER) & (rev.year <= 1809)].copy(); r['decade'] = r.year // 10 * 10
t = r.pivot_table(index='decade', columns='group', values='pesos', aggfunc='sum').reindex(columns=ORDER).fillna(0)
sh_ = t.div(t.sum(1), axis=0)
fig, ax = plt.subplots(figsize=(12, 4.6))
bottom = np.zeros(len(sh_))
for g in ORDER:
    ax.bar(sh_.index, sh_[g], width=8.2, bottom=bottom, color=COL[g], label=g, lw=0)
    bottom += sh_[g].values
ax.set_ylim(0, 1); ax.yaxis.set_major_locator(FixedLocator([0, .25, .5, .75, 1]))
ax.yaxis.set_major_formatter(FixedFormatter(['0', '25%', '50%', '75%', '100%']))
ax.set_xticks(sh_.index[::2]); ax.set_xticklabels([f'{c}s' for c in sh_.index[::2]], fontsize=8)
ax.spines[['top', 'right']].set_visible(False); ax.tick_params(length=0)
ax.legend(loc='lower left', bbox_to_anchor=(0, 1.0), ncol=6, frameon=False, fontsize=8.2)
title(fig, 'What the Potosí treasury lived on', 'Share of own revenue by decade, transfers, loans and carried-over balances excluded.', y=.96)
plt.subplots_adjust(left=.06, right=.985, top=.78, bottom=.08)
fig.savefig('out/assets/treasury_mix.png', facecolor=PAPER); plt.close(fig)
print('ok')
