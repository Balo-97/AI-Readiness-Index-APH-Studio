# ARI Weighting Studio

An expert-weighted **AI Readiness Index (ARI)** at the **census tract or county level**, and the browser tool that builds it.

- **Website (AIreadiness):** <https://balo-97.github.io/AI-Readiness-Index-APH-Studio/>
- **Open the studio:** <https://balo-97.github.io/AI-Readiness-Index-APH-Studio/ARI_Weighting_Studio.html>
- **Example project (Charlotte, Mecklenburg County):** [`examples/ari_11_indicators_four_dimensions.json`](examples/ari_11_indicators_four_dimensions.json)
- **Using it for another city:** [Getting a map for another US city](#getting-a-map-for-another-us-city)

The studio runs entirely in your browser. There is nothing to install and no server; your data and judgements stay on your computer.

## Contents

1. [Introduction](#introduction)
2. [What the studio does](#what-the-studio-does)
3. [Methodology](#methodology)
4. [Quick start with the Charlotte example](#quick-start-with-the-charlotte-example)
5. [Working as a team](#working-as-a-team)
6. [Using your own data](#using-your-own-data)
7. [Running it locally](#running-it-locally)
8. [Repository layout](#repository-layout)
9. [Data, credits and status](#data-credits-and-status)

## Introduction

Artificial intelligence is reaching many areas of community life at once, including transport, health care, education and work. It will not arrive the same way everywhere. Whether residents can benefit depends on whether they have the digital infrastructure AI runs on and the education, income and skills to use it, and both vary sharply between neighbourhoods within the same city. Existing AI-readiness indices compare countries, which says little about which neighbourhoods are prepared and which risk being left behind.

The ARI measures readiness at the census tract or county level, with two pillars:

- **Access**: the digital infrastructure available to residents, such as broadband subscriptions and computers.
- **Capacity**: residents' ability to make use of it: education, income, employment and skills.

Census tracts show the differences between neighbourhoods within a city; counties compare places across a region. The studio switches between the two with the **Unit of analysis** setting on the Index tab, using the same expert weights for both.

How much each indicator should count is a value judgement that local policy makers and experts have to make for their own area. The studio lets a panel make those judgements in a structured, transparent way with the **Analytic Hierarchy Process (AHP)**, checks them for consistency, and turns them into weights, an index, maps and a sensitivity analysis. It is tested on Charlotte and Mecklenburg County, North Carolina, with data from the [Carolinas Regional Explorer](https://github.com/kvenkita/crxp) and the U.S. Census Bureau's American Community Survey.

## What the studio does

| Tab | What you do there |
|---|---|
| **Setup** | Build the hierarchy: dimensions (Level 1) and indicators (Level 2). Give each indicator a pillar (Access or Capacity), a direction (higher or lower is better) and a data column. A searchable catalogue lists ready-made indicators. Import and export project files. |
| **Compare** | Each team member compares items two at a time on Saaty's 1–9 scale, first the dimensions, then the indicators within each dimension. The studio flags inconsistent answers and suggests which to revisit. |
| **Group weights** | Pools everyone's judgements into group weights, with each person's consistency ratio, the group's agreement (Kendall's W) and a full report. Import teammates' judgement files here. |
| **Index** | Load the tract table, set the study area, and compute the Access and Capacity scores, the ARI and the readiness gap for every tract. Map them, find spatial clusters (Moran's I, LISA), click any tract for a breakdown with radar charts, and test how stable the ranking is (Monte Carlo). Switch between census tracts and counties with **Unit of analysis**; each level has its own table and map, and the weights are shared. |
| **Disaggregation (beta)** | Break the results down by characteristics of the tracts, such as income or majority race, alone or in combination. **Still being worked on and not yet tested**: treat its results as provisional. |
| **Guide** | Instructions inside the app. |

**Export all…** in the top bar saves every output (weights, matrices, results, maps, statistics and a README) as one zip file.

## Methodology

The ARI combines two streams. On the weights side, experts' pairwise judgements become indicator weights. On the data side, each indicator's raw value for every tract becomes a score between 0 and 1. The two meet in the pillar scores.

```
 WEIGHTS                                   DATA
 Pairwise judgements (Saaty 1-9)           Raw indicator values (tract or county)
        |                                         |
 Indicator weights (decision matrix)       Indicator scores 0-1 (normalise, flip, floor)
               \                                 /
                 Pillar scores A and C (weighted geometric mean, 0-100)
                /                                  \
     ARI = sqrt(A x C)  overall readiness      Gap G = A - C  where to invest
```

**1. Hierarchy.** The goal (AI readiness of census tracts or counties) splits into dimensions, and each dimension into indicators. Each indicator belongs to one pillar, Access ($A$) or Capacity ($C$), and has a direction $\delta_j = +1$ (higher is better) or $-1$ (lower is better).

**2. Pairwise comparisons.** For each pair of siblings, an expert answers how much more important one is than the other: 1 equal, 3 moderately, 5 strongly, 7 very strongly, 9 extremely more important (2, 4, 6, 8 in between). The answers fill a reciprocal matrix $\mathbf{A}=(a_{ij})$ with $a_{ii}=1$ and $a_{ji}=1/a_{ij}$.

**3. Local weights.** The row geometric mean gives the weights within each set:

$$g_i=\Bigl(\prod_{j=1}^{n}a_{ij}\Bigr)^{1/n},\qquad w_i=\frac{g_i}{\sum_k g_k}.$$

**4. Consistency.** With $\lambda_{\max}$ the principal eigenvalue, $\mathrm{CI}=(\lambda_{\max}-n)/(n-1)$ and $\mathrm{CR}=\mathrm{CI}/\mathrm{RI}(n)$, where $\mathrm{RI}$ is Saaty's random index (0.58 for $n=3$, 0.90 for $n=4$). Matrices with $\mathrm{CR}<0.10$ are accepted; above that the studio suggests revisions.

**5. Combining the panel.** Each cell is pooled across the $K$ experts with a weighted geometric mean, which keeps the matrix reciprocal:

$$a^{G}_{ij}=\prod_{k=1}^{K}a_{ij,k}^{\lambda_k/\sum_l\lambda_l}.$$

**6. Global and pillar weights.** An indicator's global weight is its dimension's weight times its weight within the dimension, $w_j=w_d\,w_{j\mid d}$. The weights are then rescaled to sum to 1 within each pillar, $w^{P}_j=w_j/\sum_{k\in P}w_k$.

**7. Indicator scores.** Tracts with fewer residents than a minimum (100 by default) are left unscored first: survey estimates for a handful of residents are mostly 0% or 100% and would otherwise set the scale for everyone else. Each indicator is then rescaled across the $N$ remaining tracts of the study area, flipped if lower is better, and raised off zero by a small floor $f=0.01$:

$$z_{tj}=\frac{x_{tj}-\min_s x_{sj}}{\max_s x_{sj}-\min_s x_{sj}},\qquad z_{tj}\leftarrow 1-z_{tj}\ \text{if}\ \delta_j=-1,\qquad x'_{tj}=f+(1-f)\,z_{tj}.$$

Percentile ranks are available instead of min–max.

**8. Pillar scores.** A weighted geometric mean on a 0–100 scale, so a weak indicator cannot be fully offset by a strong one:

$$P_t=100\prod_{j\in P}\bigl(x'_{tj}\bigr)^{w^{P}_j},\qquad P\in\{A,C\}.$$

**9. The index and the gap.**

$$\mathrm{ARI}_t=\sqrt{A_t\,C_t},\qquad G_t=A_t-C_t.$$

The ARI is high only when both pillars are high. A positive gap means access is ahead of residents' capacity to use it (invest in skills); a negative gap means capacity is ahead of access (invest in connectivity).

**10. Robustness and spatial pattern.** A Monte Carlo analysis moves every judgement randomly by up to ±k steps of the scale, recomputes everything, and reports each tract's range of ranks. Moran's I and local Moran (LISA) statistics, with a false-discovery-rate correction, show where high and low readiness cluster. They use 9,999 permutations by default: with $n$ tracts the correction can only find a single tract significant if the number of permutations is at least $n/\alpha-1$ (about 6,000 for 300 tracts), and the studio warns when it is lower.

**A note on responsible use.** Weights are value judgements, and the same flexibility that lets a community set its own priorities can be used to make an area look more or less ready than it is. Document who took part and what they judged, report consistency, run the sensitivity analysis, and publish the weights with the results.

## Quick start with the Charlotte example

1. **Open the studio** at <https://balo-97.github.io/AI-Readiness-Index-APH-Studio/ARI_Weighting_Studio.html>. On a first visit it opens a demo; nothing in the demo is saved.
2. **Load the example project.** Download [`ari_11_indicators_four_dimensions.json`](examples/ari_11_indicators_four_dimensions.json). In the studio, click **Import project file…** in the banner, or go to **Setup → Import .json files…**, or drag the file onto the page. Check the preview and press **Start the project**.

   It has four dimensions and eleven indicators, all mapped to columns of the bundled Charlotte data:

   | Dimension | Indicator | Pillar | Direction |
   |---|---|---|---|
   | Economy | Median household income | Capacity | higher is better |
   | | Labour-force participation rate | Capacity | higher is better |
   | | Broadband subscription of any type | Access | higher is better |
   | Education and Employment | High-AI-exposure occupation share | Access | higher is better |
   | | High school diploma or higher | Capacity | higher is better |
   | | College enrolment (share of adults 18+) | Capacity | higher is better |
   | Health and Transport | Health insurance coverage | Access | higher is better |
   | | Routine checkup (adults) | Access | higher is better |
   | | Households without a vehicle | Access | lower is better |
   | Character | Population aged 18–34 | Capacity | higher is better |
   | | Residents 65+ with a computer and broadband | Capacity | higher is better |

3. **Add yourself.** In the top bar, choose **You are → ＋ New participant…** and type your name.
4. **Compare.** On the **Compare** tab, answer each pair: click the number on the side of the more important item (16 comparisons for this example). Revise any set whose consistency ratio is above 0.10.
5. **See the weights** on the **Group weights** tab.
6. **Compute the index.** On the **Index** tab, click **Load example tracts (CRXP + Census ACS, 2024)**. The study area is already set to Mecklenburg County. Until every comparison is answered, equal weights stand in and results are marked provisional.
7. **Explore.** Map the ARI, the pillars, the gap or the bivariate Access × Capacity classes; click a tract for its breakdown; run the sensitivity analysis; look for spatial clusters.
8. **Save.** Use **Setup → Export project + all judgements (.json)** to keep your work, and **Export all…** for every output.

## Working as a team

The website version keeps everything in your browser only (it uses the browser's local storage), so teammates combine their work by exchanging files:

1. **The facilitator** builds the hierarchy on the Setup tab, agrees it with the group, clicks **Lock hierarchy**, and sends everyone **Export project + all judgements (.json)**.
2. **Each member** opens the studio, imports that file, adds themselves as a participant, makes their comparisons, and sends back **Export only my judgements**.
3. **The facilitator** imports all the returned files at once: **Group weights → Import teammates' files…**, or drag them onto the page. A preview shows each person, how many of their judgements fit the hierarchy, and whether a newer copy replaces an older one. Nothing changes until you press **Import**.

Everyone must judge the **same hierarchy**: the AHP pools judgements pair by pair, so judgements made on different dimensions or indicators cannot be combined. The preview warns you when files come from a different hierarchy.

## Using your own data

### The table (CSV)

Any CSV with a header row and **one row per area** works: tracts, block groups, neighbourhoods, counties. For county-level data, switch **Unit of analysis** on the Index tab to **Counties** before you upload; the census-tract and county levels each keep their own table and map.

- **An ID column**, such as `geoid`, unique for each row. It is also what joins the table to the map.
- **A name column** (optional), such as `tract_name`.
- **A column to define the study area** (optional), such as `county_name`, so you can analyse a subset of rows.
- **A population column** (recommended), such as `total-population`, so areas with almost no residents can be left out (see step 2 below).
- **One numeric column per indicator.** Percentages, rates, medians or counts all work; the studio rescales them.
- **Reliability columns** (optional): name a column `<indicator>_cv` and the studio reads it as that indicator's coefficient of variation (%) and flags unreliable estimates (default threshold 30%).

See [`data/template_tracts.csv`](data/template_tracts.csv) for the layout:

```csv
geoid,tract_name,county_name,household-income,household-income_cv,acs-broadband-any,acs-broadband-any_cv,...
37119000101,Second Ward / Uptown,Mecklenburg County,119044.0,10.01,97.1429,3.97,...
```

**How values are read.** Commas, semicolons or tabs separate the columns. Quoted fields may contain commas. Thousands separators, `$`, `%` and spaces are ignored, so `$61,250` and `12.5%` read as numbers. Blank cells and `NA`, `N/A`, `null`, `NaN`, `none` and `-` count as missing. Decimal commas (`1,5`) are not supported.

**In the studio:**

1. On the **Index** tab, click **Upload CSV…** and choose your file.
2. Set the **ID column**, the name column and, if you want a subset, **Study area: filter rows by** a column and its values. Check the **Population column** and **Minimum residents** (default 100): areas with fewer residents are left unscored and cannot set any indicator's minimum or maximum. The studio finds a column named like `total-population` on its own; choose *None* or a minimum of 0 to switch the rule off.
3. On the **Setup** tab, give each indicator its **data column** (a dropdown lists your columns), its pillar and its direction.
4. Choose how missing values are handled (leave the tract unscored, reweight, or fill with the median) and the normalisation (min–max or percentile) on the Index tab.

### The boundaries (GeoJSON)

The built-in map covers only the 14 counties of the Charlotte region. For anywhere else, upload a boundary file: click **Upload boundaries (GeoJSON)…** on the Index tab. The file needs:

- polygons or multipolygons (a FeatureCollection, a single Feature or a bare geometry);
- one property whose values match the table's ID column (the studio finds the best match itself; you can change it under the map's **Join** setting);
- longitude/latitude coordinates (WGS 84, EPSG:4326), the GeoJSON standard.

Have a shapefile or GeoPackage? Convert it in QGIS (*Export → Save Features As… → GeoJSON, CRS EPSG:4326*) or at [mapshaper.org](https://mapshaper.org) (*Export → GeoJSON*). Simplify large files there first (*Simplify → 10–20%*); they draw much faster.

#### Getting a map for another US city

Census tract boundaries for every state are free from the U.S. Census Bureau. It takes about five minutes:

1. **Download the tracts for your state.** Open the Census Bureau's [Cartographic Boundary Files](https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html), pick the year that matches your data, and download **Census Tracts** for your state as a shapefile (`.zip`). For North Carolina in 2024, for example, the file is `cb_2024_37_tract_500k.zip`. Tract boundaries are fixed for the decade, so any year from 2020 on matches current ACS estimates.
2. **Cut it to your area and convert it** at [mapshaper.org](https://mapshaper.org), a free tool that runs in your browser:
   1. Drag the `.zip` onto the page and click **Import**.
   2. To keep only your county, click **Console** and type a filter with the county's three-digit code, then press Enter. For Mecklenburg County (code 119):
      ```
      -filter 'COUNTYFP == "119"'
      ```
      For several counties: `-filter '["119","025","179"].includes(COUNTYFP)'`. The county code is digits 3–5 of any tract's `GEOID`.
   3. Click **Simplify** and set the slider to about 10–20% so the map draws quickly.
   4. Click **Export**, choose **GeoJSON** and save the file.
3. **Upload it in the studio.** On the Index tab, click **Upload boundaries (GeoJSON)…**. The studio matches the file's `GEOID` to your table's ID column on its own. Check that the map's **Join** setting shows every row matched; rows without a shape have IDs that are not in the file.
4. **Optional: add an outline.** County outlines help orient readers. Download **Counties** from the same Census page, convert it the same way, and add it under **Outline layer → Upload…**.

**Working at the county level?** Switch **Unit of analysis** on the Index tab to **Counties** first; each level keeps its own table and map. In step 1, download **Counties** instead of Census Tracts. That file covers the whole country, so filter it to your state or region in step 2, for example `-filter 'STATEFP == "37"'` for North Carolina. A county's `GEOID` has 5 digits: state (2) and county (3), for example `37119`.

**Make the IDs in your table match.** A tract's `GEOID` has 11 digits: state (2), county (3) and tract (6), for example `37119000101`. How you get it depends on where your data comes from:

- **data.census.gov** tables have a `GEO_ID` column such as `1400000US37119000101`. Keep only the last 11 digits (in Excel, `=RIGHT(A2,11)`).
- **The Census API** returns separate `state`, `county` and `tract` columns. Join them in that order.
- **Excel** removes leading zeros, so Alabama's `01073000100` becomes `1073000100`. The studio ignores leading zeros when matching, so either form works.

#### Other places and other kinds of area

Any polygon boundaries work, as long as one property matches an ID column in your table. Examples include block groups (from the same Census page), neighbourhoods, wards or council districts from a city's open-data portal, and small statistical areas from a national statistics office outside the US. City portals often publish shapefiles in a local projection. Convert those to longitude/latitude before exporting: type `-proj wgs84` in the mapshaper console, or in QGIS choose *CRS EPSG:4326* when you save as GeoJSON.

### Privacy

Uploaded tables and boundaries are processed in your browser and never sent anywhere. They are kept in your browser's local storage so they are still there next time; use the **Export** buttons to keep copies.

## Running it locally

**Option 1: one file, no installation.** Download [`ARI_Weighting_Studio.html`](ARI_Weighting_Studio.html) (click *Download raw file* on its GitHub page) and double-click it. It opens in any modern browser (Chrome, Edge, Firefox, Safari) and works offline, with the Charlotte example data built in. Without an internet connection the fonts fall back to your system's fonts.

**Option 2: the whole repository.**

```bash
git clone https://github.com/Balo-97/AI-Readiness-Index-APH-Studio.git
cd AI-Readiness-Index-APH-Studio
python -m http.server 8000
```

Then open <http://localhost:8000/> for the website or <http://localhost:8000/ARI_Weighting_Studio.html> for the studio. Any static web server works; you can also just double-click `ARI_Weighting_Studio.html`.

**Option 3: change the code or the built-in data.** The source of the studio is [`app/ari_weighting_studio.html`](app/ari_weighting_studio.html). After editing it, or after replacing the files in `data/`, rebuild the standalone file (Python 3.8 or later, standard library only):

```bash
python tools/build_standalone.py
```

This embeds the tract table, the county table, the tract names and both boundary files into `ARI_Weighting_Studio.html`. To regenerate the example project, run `python tools/make_four_dimension_example.py`. Note that `app/ari_weighting_studio.html` is a page body without the surrounding `<html>` document, so open the built `ARI_Weighting_Studio.html`, not the source.

## Repository layout

```
index.html                     the website (introduction, methodology, how to use it)
ARI_Weighting_Studio.html      the studio: one self-contained file with the example data built in
app/ari_weighting_studio.html  source of the studio
examples/                      the Charlotte example project (4 dimensions, 11 indicators)
data/                          example data for the Charlotte region, a template, and data credits
tools/build_standalone.py      builds ARI_Weighting_Studio.html from app/ and data/
tools/ines_indicators.py       definitions of the indicator catalogue built into the studio
tools/make_four_dimension_example.py   builds the example project
```

## Data, credits and status

**Data.** The example covers the 752 census tracts and the 14 counties of the Charlotte region (North and South Carolina); the example study area is Mecklenburg County's 305 tracts. Sources and licences are listed in [`data/README.md`](data/README.md):

- Carolinas Regional Explorer, UNC Charlotte Urban Institute. © 2026 Kailas Venkitasubramanian. Data licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). <https://github.com/kvenkita/crxp>
- U.S. Census Bureau, American Community Survey 2020–2024 five-year estimates (public domain).
- CDC PLACES (public domain).
- Neighbourhood names © OpenStreetMap contributors (ODbL).

**Status.**

- The **Disaggregation (beta)** tab is still being worked on and has not yet been tested.
- ACS margins of error are flagged (by the coefficient of variation) but not propagated into the scores.
- The example project contains no judgements: the weights must come from your own panel.

**Licence.** The data in `data/` is licensed as listed above. A licence for the code has not yet been chosen.
