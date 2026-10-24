"""Correlation report for this dataset: a scatter-plot matrix that states each Pearson r with its 95% confidence interval,
p-value and sample size, plus a table (data/correlations.parquet) with the same figures, Spearman's rho and, for annual
series, the correlation of year-on-year changes. Reads only the published Parquet files in out/data."""
import glob, os, sys, textwrap, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.lines import Line2D
from scipy import stats

for f in glob.glob('fonts/*.otf') + ['/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc']:
    if os.path.exists(f): fm.fontManager.addfont(f)
_n = {f.name for f in fm.fontManager.ttflist}
FONT = next((n for n in ('Noto Sans CJK SC', 'Noto Sans CJK JP') if n in _n), 'DejaVu Sans')
plt.rcParams.update({'font.family': FONT, 'font.size': 10, 'axes.edgecolor': '#BBBBBB', 'axes.linewidth': .6,
                     'xtick.color': '#666666', 'ytick.color': '#666666', 'axes.labelcolor': '#444444', 'text.color': '#1F1F1F',
                     'savefig.dpi': 200})
INK, MID, LIGHT, LAND, PAPER = '#1F1F1F', '#8A8A8A', '#C9C6BF', '#ECE9E3', '#FFFFFF'
RED, RED_SOFT, BLUE, BLUE_SOFT = '#B33A2B', '#E3B5AE', '#2F4B7C', '#B9C4D6'


def strength(r):
    a = abs(r)
    return 'negligible' if a < .1 else 'weak' if a < .3 else 'moderate' if a < .5 else 'strong' if a < .7 else 'very strong'


def pearson(x, y):
    """r, 95% CI (Fisher z), two-sided p-value (t test), n, on pairwise complete observations."""
    m = x.notna() & y.notna(); x, y = x[m].astype(float), y[m].astype(float); n = int(m.sum())
    if n < 4 or x.std() == 0 or y.std() == 0: return dict(n=n, r=np.nan, lo=np.nan, hi=np.nan, p=np.nan, rho=np.nan)
    r = float(np.corrcoef(x, y)[0, 1]); r = max(min(r, .999999), -.999999)
    z, se = np.arctanh(r), 1 / np.sqrt(n - 3)
    t = r * np.sqrt((n - 2) / (1 - r * r))
    return dict(n=n, r=r, lo=float(np.tanh(z - 1.96 * se)), hi=float(np.tanh(z + 1.96 * se)),
                p=float(2 * stats.t.sf(abs(t), n - 2)), rho=float(stats.spearmanr(x, y).statistic))


def pfmt(p):
    return 'p < 0.001' if p < .001 else f'p = {p:.3f}' if p < .01 else f'p = {p:.2f}'


def values(d, v, o):
    return np.log10(d[v].astype(float)) if 'log' in o else d[v].astype(float)


def table(d, V, year=None):
    """One row per pair of variables. With `year`, also the correlation of year-on-year changes (consecutive years only)."""
    rows = []
    if year is not None:
        dd = d.sort_values(year); gap = dd[year].diff() == 1
        diff = {v: values(dd, v, o[0] if o else {}).diff().where(gap) for v, _, *o in V}
    for i, (vi, li, *oi) in enumerate(V):
        for j, (vj, lj, *oj) in enumerate(V):
            if j >= i: continue
            s = pearson(values(d, vj, oj[0] if oj else {}), values(d, vi, oi[0] if oi else {}))
            row = dict(x=vj, y=vi, x_label=lj.replace('\n', ' '), y_label=li.replace('\n', ' '), n=s['n'], pearson_r=round(s['r'], 3),
                       r_squared=round(s['r'] ** 2, 3), ci95_low=round(s['lo'], 3), ci95_high=round(s['hi'], 3), p_value=float(f"{s['p']:.3g}"),
                       spearman_rho=round(s['rho'], 3), strength=strength(s['r']), direction='positive' if s['r'] > 0 else 'negative')
            if year is not None:
                c = pearson(diff[vj], diff[vi])
                row.update(n_changes=c['n'], pearson_r_changes=round(c['r'], 3), p_value_changes=float(f"{c['p']:.3g}"))
            rows.append(row)
    return pd.DataFrame(rows)


def matrix(d, V, groups, title, subtitle, note, out, year=None, legend=True):
    """Lower triangle: scatter with least-squares line. Diagonal: distribution. Upper triangle: the statistics, tinted by r.
    V: list of (column, label, options) with options in {'log': ticks, 'jitter': width}. groups: list of (label, mask, colour)."""
    k = len(V); T = table(d, V, year)
    X = {v: values(d, v, o[0] if o else {}) for v, _, *o in V}
    rng = np.random.default_rng(7)
    fig, axs = plt.subplots(k, k, figsize=(2.35 * k + 1.2, 2.35 * k + 1.6))
    for i, (vi, li, *oi) in enumerate(V):
        oi = oi[0] if oi else {}
        for j, (vj, lj, *oj) in enumerate(V):
            oj = oj[0] if oj else {}
            ax = axs[i, j]; ax.spines[['top', 'right']].set_visible(False); ax.tick_params(labelsize=6.5, length=2)
            if j > i:   # statistics
                s = T[(T.x == vi) & (T.y == vj)].iloc[0]
                r = s.pearson_r
                ax.set_facecolor(RED if r > 0 else BLUE); ax.patch.set_alpha(min(abs(r), 1) * .32)
                for sp in ax.spines.values(): sp.set_visible(False)
                ax.set_xticks([]); ax.set_yticks([])
                col = RED if r > 0 else BLUE
                ax.text(.5, .7, f'{r:+.2f}', ha='center', va='center', fontsize=17, weight='bold', color=col if s.p_value < .05 else MID, transform=ax.transAxes)
                ax.text(.5, .5, f'95% CI {s.ci95_low:+.2f} to {s.ci95_high:+.2f}', ha='center', fontsize=6.8, color=INK, transform=ax.transAxes)
                ax.text(.5, .38, f'{pfmt(s.p_value)}, n = {s.n}', ha='center', fontsize=6.8, color=INK, transform=ax.transAxes)
                ax.text(.5, .26, s.strength, ha='center', fontsize=6.8, color=MID, style='italic', transform=ax.transAxes)
                if year is not None and pd.notna(s.pearson_r_changes):
                    ax.text(.5, .1, f'yearly changes: {s.pearson_r_changes:+.2f} ({pfmt(s.p_value_changes)})', ha='center', fontsize=6.3, color=MID, transform=ax.transAxes)
                continue
            x, y = X[vj].copy(), X[vi].copy()
            if i == j:
                vals = x.dropna(); lo, hi = vals.min(), vals.max(); pad = (hi - lo) * .06 or .01
                ax.set_xlim(lo - pad, hi + pad); ax.set_yticks([])
                e = np.histogram_bin_edges(vals, 12)
                ax.hist([x[m].dropna() for _, m, _ in groups], bins=e, color=[c for *_, c in groups], stacked=True, edgecolor=PAPER)
                ax.spines['left'].set_visible(False)
            else:
                if 'jitter' in oj: x = x + rng.uniform(-oj['jitter'], oj['jitter'], len(x))
                if 'jitter' in oi: y = y + rng.uniform(-oi['jitter'], oi['jitter'], len(y))
                for _, m, c in groups: ax.scatter(x[m], y[m], s=13, c=c, alpha=.8, lw=0)
                ok = X[vj].notna() & X[vi].notna()
                if ok.sum() > 3:
                    b, a0 = np.polyfit(X[vj][ok], X[vi][ok], 1); xs = np.array([X[vj][ok].min(), X[vj][ok].max()])
                    ax.plot(xs, a0 + b * xs, color=INK, lw=.8, alpha=.7)
            if 'log' in oj: ax.set_xticks(np.log10(oj['log'])); ax.set_xticklabels([f"{t / oj.get('k', 1):g}" for t in oj['log']])
            if 'log' in oi and i != j: ax.set_yticks(np.log10(oi['log'])); ax.set_yticklabels([f"{t / oi.get('k', 1):g}" for t in oi['log']])
            if i < k - 1: ax.set_xticklabels([])
            if j > 0 and i != j: ax.set_yticklabels([])
            if i == k - 1: ax.set_xlabel(lj, fontsize=8)
            if j == 0: ax.set_ylabel(li, fontsize=8)
    fig.text(.05, .975, title, fontsize=15, weight='bold', va='top')
    fig.text(.05, .94, subtitle, fontsize=9, color='#555555', va='top')
    if legend:
        fig.legend(handles=[Line2D([], [], marker='o', ls='', c=c, label=l) for l, _, c in groups], loc='upper left', bbox_to_anchor=(.045, .918),
                   ncol=len(groups), frameon=False, fontsize=8.5)
    W = 2.35 * k + 1.2; lines = textwrap.wrap(note, int(W * 18))
    fig.text(.05, .008, '\n'.join(lines), fontsize=7, color=MID, va='bottom', linespacing=1.4)
    plt.subplots_adjust(left=.09, right=.98, top=.87, bottom=.068 + .0125 * len(lines) * 10.6 / W, wspace=.1, hspace=.1)
    fig.savefig(out, facecolor=PAPER); plt.close(fig)
    return T


HOW = ('Below the diagonal: each point is one {unit}, with a least-squares line. Diagonal: distribution of each variable. Above the diagonal: Pearson r '
       '(+1 perfect positive, 0 none, -1 perfect negative), its 95% confidence interval, p-value and number of {unit}s; tint grows with |r|, and r is in colour only when p < 0.05, i.e. when its confidence interval excludes zero. '
       'Each figure above the diagonal describes the pair in its row and column. Strength: under 0.1 negligible, 0.1 to 0.3 weak, 0.3 to 0.5 moderate, 0.5 to 0.7 strong, 0.7 and above very strong.')


if __name__ == '__main__':
    yr = pd.read_parquet('out/data/ming_silver_annual.parquet')
    V = [('silver_tonnes_5yr_mean', 'Potosí silver\n(t, five-year mean)'), ('rice_g_silver_per_liter_decade', 'Rice in silver\n(g per litre, decade)'),
         ('share_famine', 'Famine\n(share of places)'), ('share_drought', 'Drought\n(share of places)'), ('share_flood', 'Flood\n(share of places)')]
    d = yr.dropna(subset=[v for v, _ in V]).reset_index(drop=True)
    late = d.reign == 'Chongzhen'
    T = matrix(d, V, [('1560 to 1627', ~late, BLUE), ('Chongzhen reign, 1628 to 1644', late, RED)], 'Silver, prices and disaster in late Ming China',
               f'{len(d)} years, 1560 to 1644. Silver is a five-year mean and rice a decade value, so neighbouring years are not independent.',
               HOW.format(unit='year') + ' Because two series are smoothed, p-values here overstate the evidence; read r as a description.',
               'out/assets/scatter_matrix.png')
    T.to_parquet('out/data/correlations.parquet', index=False); print(T.to_string())
