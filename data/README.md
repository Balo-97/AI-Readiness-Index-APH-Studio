# Example data: the Charlotte region

These files are the example data built into the studio. They cover the 752 census tracts (2020 boundaries) of the 14-county Charlotte region in North and South Carolina; the example study area is the 305 tracts of Mecklenburg County.

| File | What it holds |
|---|---|
| `ari_tracts_2024.csv` | One row per tract: `geoid`, `tract_name`, `county_name` and 92 indicators, 82 of them with a `<column>_cv` column holding the coefficient of variation (%). |
| `ari_counties_2024.csv` | The same columns for the 14 counties, for the studio's county level. |
| `tracts_2020.geojson` | Tract boundaries; the property `geoid` matches the table's `geoid` column. |
| `counties_2020.geojson` | County outlines (`geoid`, `name`), drawn for context on the map. |
| `tract_names.csv` | Tract names as the Carolinas Regional Explorer shows them, used to match Data Extractor exports that list tracts by name. |
| `template_tracts.csv` | Three real Mecklenburg rows and a few columns, showing the layout to follow for your own data. |

Indicator values are percentages unless the column is a count, a median (such as `household-income`, in US dollars) or an index. The indicators come from the American Community Survey 2020–2024 five-year estimates and CDC PLACES, as compiled by the Carolinas Regional Explorer, plus additional ACS tables (internet subscriptions, devices, occupations, labour force, age) computed for this project.

## Credits and licences

- **Carolinas Regional Explorer** (CRXP), UNC Charlotte Urban Institute. © 2026 Kailas Venkitasubramanian. Data licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). <https://github.com/kvenkita/crxp>
- **U.S. Census Bureau**, American Community Survey 5-year estimates (public domain).
- **CDC PLACES** (public domain).
- **Neighbourhood names** in `tract_names.csv` and the `tract_name` column © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright), licensed ODbL.

The CRXP-derived files are redistributed here under CC BY 4.0 with the attribution above. If you reuse them, keep that attribution.
