"""
Build the standalone, double-click version of the studio.

    python tools/build_standalone.py

Reads   app/ari_weighting_studio.html      (the page source; also what is published online)
        data/ari_tracts_2024.csv           (optional; the example table, embedded so it works offline)
        data/ari_counties_2024.csv         (optional; the county-level example table)
        data/tract_names.csv               (optional; matches Data Extractor exports that list tracts by name)
        data/tracts_2020.geojson,
        data/counties_2020.geojson         (optional; embedded so the map's bundled boundaries work offline)
Writes  ARI_Weighting_Studio.html          (open it in any modern browser; no server needed)

It also refreshes the catalogues embedded in the page source: CRXP's from tools/.crxp_cache/manifest.json when
that cache exists (created by fetch_crxp.py), and the INES indicator set from tools/ines_indicators.py.
"""

import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "app", "ari_weighting_studio.html")
CSV = os.path.join(ROOT, "data", "ari_tracts_2024.csv")          # CRXP + Census ACS (tools/census_bridge.py)
COUNTY_CSV = os.path.join(ROOT, "data", "ari_counties_2024.csv")  # the same columns for the 14 counties
NAMES = os.path.join(ROOT, "data", "tract_names.csv")           # tract-name lookup for Data Extractor exports
GEO = os.path.join(ROOT, "data", "tracts_2020.geojson")
OUTLINE = os.path.join(ROOT, "data", "counties_2020.geojson")
OUT = os.path.join(ROOT, "ARI_Weighting_Studio.html")
MANIFEST = os.path.join(HERE, ".crxp_cache", "manifest.json")


def short_source(s):
    if s.startswith("U.S. Census Bureau, American"):
        return "ACS 5-yr"
    for key, label in (("LEHD", "LEHD LODES"), ("PLACES", "CDC PLACES"), ("Geological", "USGS NLCD"), ("VIIRS", "VIIRS night lights")):
        if key in s:
            return label
    return s[:30]


def refresh_catalog(src):
    if not os.path.exists(MANIFEST):
        return src
    with open(MANIFEST, encoding="utf-8") as f:
        m = json.load(f)
    rows = []
    for i in m["indicators"]:
        h = i.get("higherIsBetter")
        rows.append([i["slug"], i["label"], i["category"], i.get("description", ""),
                     1 if h is True else -1 if h is False else 0, short_source(i.get("source", ""))])
    blob = json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
    new, n = re.subn(r"/\*CRXP_CATALOG\*/\[.*?\];", lambda _: f"/*CRXP_CATALOG*/{blob};", src, count=1, flags=re.S)
    if n:
        print(f"CRXP catalogue: {len(rows)} indicators")
    return new


def refresh_ines(src):
    """Write the INES indicator set (tools/ines_indicators.py) into the page's INES_CATALOG."""
    import sys
    sys.path.insert(0, HERE)
    import ines_indicators
    blob = json.dumps(ines_indicators.catalogue_rows(), ensure_ascii=False, separators=(",", ":"))
    new, n = re.subn(r"/\*INES_CATALOG\*/\[.*?\];", lambda _: f"/*INES_CATALOG*/{blob};", src, count=1, flags=re.S)
    if n:
        print(f"INES indicator set: {len(ines_indicators.INDICATORS)} indicators")
    return new


def main():
    with open(SRC, encoding="utf-8") as f:
        src = f.read()
    src = refresh_ines(refresh_catalog(src))
    with open(SRC, "w", encoding="utf-8") as f:
        f.write(src)

    embedded = ""
    if os.path.exists(CSV):
        with open(CSV, encoding="utf-8") as f:
            csv_text = f.read()
        embedded = f'<script type="text/plain" id="bundled-csv">\n{csv_text}</script>\n'
        print(f"Embedded {os.path.basename(CSV)} ({len(csv_text) // 1024} KB)")
    if os.path.exists(COUNTY_CSV):
        with open(COUNTY_CSV, encoding="utf-8") as f:
            county_text = f.read()
        embedded += f'<script type="text/plain" id="bundled-csv-county">\n{county_text}</script>\n'
        print(f"Embedded {os.path.basename(COUNTY_CSV)} ({len(county_text) // 1024} KB)")
    if os.path.exists(NAMES):
        with open(NAMES, encoding="utf-8") as f:
            names_text = f.read()
        embedded += f'<script type="text/plain" id="bundled-names">\n{names_text}</script>\n'
        print(f"Embedded {os.path.basename(NAMES)} ({len(names_text) // 1024} KB)")
    for path, el_id in ((GEO, "bundled-geo"), (OUTLINE, "bundled-outline")):
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                text = f.read().replace("</", "<\\/")
            embedded += f'<script type="application/json" id="{el_id}">{text}</script>\n'
            print(f"Embedded {os.path.basename(path)} ({len(text) // 1024} KB)")

    page = (
        "<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1,viewport-fit=cover\">\n"
        "</head>\n<body>\n" + embedded + src + "\n</body>\n</html>\n"
    )
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"Wrote {OUT} ({len(page) // 1024} KB)")


if __name__ == "__main__":
    main()
