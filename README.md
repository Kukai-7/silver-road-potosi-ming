# Silver Road: Potosí to Ming China

[Dataset on Hugging Face](https://huggingface.co/datasets/Kukai-7/silver-road-potosi-ming) · code in this repository

**Did American silver make, and then break, Ming China?** From the 1570s the silver of Potosí, in the Andes, crossed the Pacific on the Manila galleon or went round by Seville, and much of it ended in China, where taxes had come to be paid in silver. This dataset puts side by side what the royal treasury of Potosí recorded, year by year from 1560 to 1823, what a litre of rice cost in silver in China, and the disasters of the [Ming Crisis Atlas](https://huggingface.co/datasets/Kukai-7/ming-crisis-atlas).

*L'argent de Potosí et la Chine des Ming.*

![The silver road, from Potosí to Ming China](https://huggingface.co/datasets/Kukai-7/silver-road-potosi-ming/resolve/main/assets/map_silver_road.png)

*Reading the map: red is the Pacific route (the Manila galleon from 1571), blue the Atlantic one; triangles mark the silver mines of Potosí, Zacatecas and Iwami. Most American silver reached China through Manila or round the Cape, Japanese silver directly.*

## At a glance

| | |
|---|---|
| Period | Potosí 1560 to 1823, annual; Chinese rice 961 to 1910; joint panel 1560 to 1644 |
| Potosí | 246 accounted years of the royal treasury: silver taxes, the registered silver they imply, and the full revenue mix |
| Rice in silver | 122 observations from three series: Peng Xinwei (reign averages), Liu Guanglin (decades), Kishimoto Mio (Suzhou, annual) |
| Late Ming | 85 years joined with drought, flood and famine shares from the Ming Crisis Atlas |
| Map | 18 places and 6 routes of the silver trade, with coordinates |
| Format | Parquet, six configurations: `ming_silver_annual`, `potosi_annual`, `potosi_revenue`, `china_rice_silver`, `places`, `routes` |

## What it shows

![Silver out of Potosí, and what silver bought in China](https://huggingface.co/datasets/Kukai-7/silver-road-potosi-ming/resolve/main/assets/timeline_silver.png)

*Reading the chart: grey bars are Potosí silver implied by royal taxes, the black line its five-year mean (left axis); blue steps are the price of rice in grams of silver per litre in China (right axis). Silver peaks around 1590 and declines slowly; rice gets dearer in silver in the 1640s, when the Ming fall.*

- **The boom is real and fast.** Registered silver implied by the royal taxes goes from about 30 tonnes a year in the early 1570s to about 180 tonnes in the 1590s, once mercury amalgamation is in use. Over 1560 to 1644 the accounts imply about 10,000 tonnes.
- **Potosí declines, it does not collapse, before the Ming fall.** The five-year mean is about 126 tonnes in 1630 to 1644, 30% below the 1590s peak but close to the average of the Wanli reign (146). If the flow of silver into China dried up in the late 1630s, as one well-known thesis holds, the cause is more likely on the routes (Manila, Japan) than at the mine. This dataset measures the mine, not the arrivals.
- **Rice got dearer in silver, not cheaper.** Peng's reign averages go from 0.16 grams of silver per litre under the Hongwu emperor to 0.22 under Wanli, 0.32 under Tianqi and 0.40 under Chongzhen. More silver in circulation and worse harvests both push in that direction; the data cannot separate them.
- **Famine follows drought, not silver.** Over 1560 to 1644 the share of places reporting famine correlates at 0.50 with drought and at 0.17 with Potosí output. The last reign, Chongzhen, stands out by its drought (25% of places against 19% before), not by its silver.
- **Mercury paid for silver.** After the 1570s, sales of mercury, a royal monopoly needed to refine the ore, bring the treasury a sixth to a quarter of its own revenue, close to a third in the 1770s.

![Silver, prices and disaster in late Ming China](https://huggingface.co/datasets/Kukai-7/silver-road-potosi-ming/resolve/main/assets/scatter_matrix.png)

*Reading the chart: see "Reading the correlations" below. Famine lines up with drought, not with silver.*

![What the Potosí treasury lived on](https://huggingface.co/datasets/Kukai-7/silver-road-potosi-ming/resolve/main/assets/treasury_mix.png)

*Reading the chart: each bar is a decade of the Potosí treasury's own revenue, split by source. Silver taxes fall from over 80% in the 1560s to about a third; mercury sales and the mint take over.*

## Reading the correlations

**How to read r.** Pearson's r measures how closely two variables move along a straight line: +1 is a perfect positive line, 0 no linear link, -1 a perfect negative line. r² is the share of the variance of one variable that a straight line on the other accounts for (r = 0.7 means about half). The labels used here: under 0.1 negligible, 0.1 to 0.3 weak, 0.3 to 0.5 moderate, 0.5 to 0.7 strong, 0.7 and above very strong.

**How sure is it?** The 95% confidence interval gives the range of r compatible with the data; when it excludes zero, p is below 0.05 and the link is distinguishable from chance. Strength and certainty are different things: a weak r can be certain with many observations, and a strong r can be uncertain with few. Spearman's ρ repeats the exercise on ranks, so a large gap between r and ρ points to outliers or a curved relationship.

In the scatter-plot matrix (`scatter_matrix.png`), the panels below the diagonal show the points with a least-squares line, the diagonal shows each distribution, and the panels above the diagonal give r, its 95% confidence interval, p and n for the pair in that row and column. A figure is in colour only when p < 0.05.

**What stands out**

- **Famine goes with drought (+0.50, 95% CI +0.32 to +0.65) and against flood (-0.38).** In the same years, drought and flood exclude each other (-0.63): a dry year is rarely a wet one across the empire.
- **Silver barely relates to anything.** Potosí output correlates at +0.17 with famine and +0.19 with rice prices, with intervals that include zero; its +0.25 with drought is weak and, given smoothing, not reliable.
- **Rice in silver is dearer in flood-poor, drought-prone years (-0.41 with flood, +0.27 with drought)**, which fits a harvest story better than a money story.

**All pairs**, sorted by the size of r. The same figures are in the `correlations` configuration.

| Pair | r | 95% CI | p | n | Spearman ρ | Reading |
|---|---|---|---|---|---|---|
| Drought (share of places) × Flood (share of places) | **-0.63** | -0.74 to -0.47 | < 0.001 | 83 | -0.64 | strong, negative; distinguishable from zero |
| Famine (share of places) × Drought (share of places) | **+0.50** | +0.32 to +0.65 | < 0.001 | 83 | +0.48 | strong, positive; distinguishable from zero |
| Rice in silver (g per litre, decade) × Flood (share of places) | **-0.41** | -0.57 to -0.21 | < 0.001 | 83 | -0.31 | moderate, negative; distinguishable from zero |
| Famine (share of places) × Flood (share of places) | **-0.38** | -0.55 to -0.18 | < 0.001 | 83 | -0.38 | moderate, negative; distinguishable from zero |
| Rice in silver (g per litre, decade) × Drought (share of places) | **+0.27** | +0.06 to +0.46 | 0.01 | 83 | +0.34 | weak, positive; distinguishable from zero |
| Potosí silver (t, five-year mean) × Drought (share of places) | **+0.25** | +0.04 to +0.44 | 0.02 | 83 | +0.16 | weak, positive; distinguishable from zero |
| Potosí silver (t, five-year mean) × Flood (share of places) | **-0.24** | -0.43 to -0.03 | 0.03 | 83 | -0.14 | weak, negative; distinguishable from zero |
| Potosí silver (t, five-year mean) × Rice in silver (g per litre, decade) | **+0.19** | -0.02 to +0.39 | 0.08 | 83 | +0.22 | weak, positive; not distinguishable from zero |
| Potosí silver (t, five-year mean) × Famine (share of places) | **+0.17** | -0.05 to +0.37 | 0.14 | 83 | +0.16 | weak, positive; not distinguishable from zero |
| Rice in silver (g per litre, decade) × Famine (share of places) | **+0.15** | -0.07 to +0.35 | 0.19 | 83 | +0.16 | weak, positive; not distinguishable from zero |

**What it does not say**

- Silver is a five-year mean and rice a decade value, so neighbouring years are not independent and the p-values overstate the evidence; the r values describe, they do not test.
- The famine and drought shares come from surviving local records, which grow over time.
- No correlation here identifies a cause.

## Load it

```python
from datasets import load_dataset

late_ming = load_dataset("Kukai-7/silver-road-potosi-ming", "ming_silver_annual", split="train").to_pandas()
potosi = load_dataset("Kukai-7/silver-road-potosi-ming", "potosi_annual", split="train").to_pandas()

# Potosí output and drought, reign by reign
late_ming.groupby("reign", sort=False)[["silver_tonnes_5yr_mean", "share_drought", "share_famine"]].mean()
```

## Configurations

### `ming_silver_annual` (default), 85 rows

| column | description |
|---|---|
| `year`, `reign` | 1560 to 1644 and the Ming reign |
| `implied_registered_silver_tonnes`, `silver_tonnes_5yr_mean`, `likely_bundled_arrears`, `tax_regime` | From `potosi_annual` |
| `rice_g_silver_per_liter_decade` | Liu's decade mean for the decade containing the year |
| `rice_g_silver_per_liter_suzhou` | Kishimoto's Suzhou price, when available |
| `n_places_reporting`, `share_drought`, `share_flood`, `share_famine`, `share_cannibalism`, `share_war_banditry`, `places_famine`, `enso_event`, `china_temp_anomaly_c` | From the [Ming Crisis Atlas](https://huggingface.co/datasets/Kukai-7/ming-crisis-atlas) `annual` table |

### `potosi_annual`, 264 rows (1560 to 1823)

| column | description |
|---|---|
| `period`, `period_years` | Account period as written in the ledger; a period covering several years is spread evenly over them |
| `treasury_income_pesos` | All entries of the account, in pesos of 8 reales (pesos ensayados of 450 maravedís converted at 450/272) |
| `silver_tax_pesos` | Royal taxes on silver: the fifth (*quinto*), the tenth (*diezmo*) and the 1 to 1.5% *cobos* |
| `implied_registered_silver_pesos`, `implied_registered_silver_tonnes` | Tax divided by its rate, then 25.56 grams of fine silver per peso |
| `tax_regime` | Fifth or tenth, as named in the account |
| `account_missing`, `no_silver_tax_line`, `likely_bundled_arrears` | Quality flags, see Limitations |
| `silver_tonnes_5yr_mean` | Centred five-year mean, flagged years left out |

### `potosi_revenue`, 1,576 rows

`year`, `group`, `pesos`: every account entry sorted into silver taxes, mercury sales, mint and bullion, tribute, sales tax (*alcabala*), other revenue, and transfers, loans and balances.

### `china_rice_silver`, 122 rows

`source`, `region`, `start_year`, `end_year`, `grams_silver_per_liter`. One row per reign (Peng), decade (Liu) or year (Kishimoto), all converted to grams of silver per litre of husked rice.

### `places`, 18 rows, and `routes`, 6 rows

Mines, ports and capitals of the trade with latitude, longitude, role and a short note; routes as ordered lists of places.

### `correlations`, 10 rows

One row per pair of variables in the scatter-plot matrix: `x`, `y` and their labels, `n`, `pearson_r`, `r_squared`, `ci95_low`, `ci95_high` (Fisher z interval), `p_value` (two-sided t test), `spearman_rho`, `strength`, `direction`. Made by `correlations.py`.

## How it was built

1. **Potosí.** The royal treasury accounts (*cartas cuentas*) of the Caja de Potosí, as transcribed by John TePaske and Herbert Klein and published online by El Colegio de México ([La Real Hacienda](https://realhacienda.colmex.mx/)). Each entry is read with its period; silver-tax lines are recognised by name and their rate (fifth or tenth, plus the *cobos* where stated) is used to infer the silver that paid it.
2. **Rice prices.** The workbook *China rice prices 961 to 1910* of the [Global Price and Income History Group](https://gpih.ucdavis.edu/Datafilelist.htm), which converts Peng Xinwei's *Zhongguo huobi shi*, Liu Guanglin's decade series and Kishimoto Mio's Suzhou prices into grams of silver per litre.
3. **Disasters.** The annual table of the Ming Crisis Atlas, built from the Ming *Shilu* and climate reconstructions.
4. **Places and routes.** Curated for this dataset from standard histories of the trade; coordinates are those of the modern town.
5. **Charts.** Python and Matplotlib; coastline from Natural Earth. The full pipeline is in [`code/`](./). The correlation figures come from `correlations.py`, which reads only the published Parquet files.

## Limitations

- **Taxed silver is not all silver.** The estimate covers silver that was registered and taxed at Potosí. Contraband, which historians think was large, is missing, and so is silver taxed at other treasuries.
- **The estimate rests on a rate.** A line taxed at a lower rate than its name suggests, or a tax paid late, shifts the result. Two years (1586 and 1706) look like several years of arrears paid at once and are flagged; the 1643 account has no silver-tax line and is left blank.
- **Gaps.** Eighteen years in 1560 to 1823 have no account: 1584, 1588, 1595, 1597, 1599, 1703 to 1704, 1713 to 1715 and eight years of the 1810s.
- **Mine is not market.** Nothing here measures how much silver reached China, or when.
- **Rice series are coarse.** Peng gives reign averages, Liu decade means from scattered sources, Kishimoto one region. A few early Liu decades (1120s, 1130s) are far above their neighbours and probably reflect paper-money prices of the Song wars; they are kept as published.
- **Correlation only.** With 85 years, overlapping trends and coarse prices, none of these correlations identifies a cause.

## Credits and licences

- Potosí: TePaske, J. J. and Klein, H. S., *The Royal Treasuries of the Spanish Empire in America*, Duke University Press, 1982, digital edition by El Colegio de México. This dataset shares annual aggregates derived from it; consult the original for the entries.
- Rice: Peng Xinwei, Liu Guanglin and Kishimoto Mio, compiled by the Global Price and Income History Group, UC Davis.
- Disasters: [Ming Crisis Atlas](https://huggingface.co/datasets/Kukai-7/ming-crisis-atlas) and its sources.
- Coastline: Natural Earth (public domain).
- This compilation, derived columns and charts: CC BY 4.0.

## Related

- [Ming Crisis Atlas](https://huggingface.co/datasets/Kukai-7/ming-crisis-atlas), the disasters of Ming China, 1368 to 1644.
- [Edo Rice, Paper and Protest](https://huggingface.co/datasets/Kukai-7/edo-rice-paper-protest), the same questions for Tokugawa Japan.
- [GitHub: Kukai-7](https://github.com/Kukai-7)
