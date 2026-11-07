"""
Builds the four-dimension, eleven-indicator ARI hierarchy as a project file the studio can import.

    python tools/make_four_dimension_example.py

Writes
  examples/ari_11_indicators_four_dimensions.json

Dimensions: Economy; Education and Employment; Health and Transport; Character. Pillars follow the
group's assignment (S = Access, formerly Supply; D = Capacity, formerly Demand). No judgements are
included; everyone weighs from scratch. Columns point at data/ari_tracts_2024.csv, which holds all
eleven indicators for the Mecklenburg tracts.

Import on the Setup tab ("Import .json files...") or drop the file onto the page.
"""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "examples")

DIMS = [
    ("d_economy", "Economy", "Household income, labour-market participation and home internet subscription."),
    ("d_edu_emp", "Education and Employment", "Educational attainment, college enrolment and AI-exposed occupations."),
    ("d_health_transport", "Health and Transport", "Health-care coverage and use, and access to a vehicle."),
    ("d_character", "Character", "Who lives here: young adults and connected older residents."),
]

# id, dimension, name, pillar (S Access / D Capacity), direction, source, column in data/ari_tracts_2024.csv
INDICATORS = [
    ("i_income", "d_economy", "Median household income", "D", 1, "ACS B19013 · CRXP", "household-income"),
    ("i_lfpr", "d_economy", "Labour-force participation rate", "D", 1, "ACS B23025", "acs-labour-force-participation"),
    ("i_broadband", "d_economy", "Broadband subscription of any type", "S", 1, "ACS B28002 · CRXP", "acs-broadband-any"),
    ("i_ai_exposure", "d_edu_emp", "High-AI-exposure occupation share", "S", 1,
     "ACS C24010 · direction not fixed in the indicator document (set to + here)", "acs-high-ai-exposure-occ"),
    ("i_hs_diploma", "d_edu_emp", "High school diploma or higher", "D", 1, "ACS B15003 · CRXP", "high-school-diploma"),
    ("i_college", "d_edu_emp", "College enrolment (share of adults 18+)", "D", 1, "ACS B14001, B01001", "acs-college-enrolment"),
    ("i_insurance", "d_health_transport", "Health insurance coverage", "S", 1, "ACS · CRXP", "health-insurance"),
    ("i_checkup", "d_health_transport", "Routine checkup (adults)", "S", 1, "CDC PLACES · CRXP", "routine-checkup"),
    ("i_no_vehicle", "d_health_transport", "Households without a vehicle", "S", -1, "ACS B08201 · CRXP", "no-vehicle"),
    ("i_age_18_34", "d_character", "Population aged 18–34", "D", 1, "ACS B01001", "acs-age-18-34"),
    ("i_seniors_connected", "d_character", "Residents 65+ with a computer and broadband", "D", 1, "ACS B28005", "acs-seniors-connected"),
]

SETTINGS = {
    "priority": "rgmm", "pooling": "aij", "crMax": 0.1, "pw": {}, "excluded": [],
    "index": {"idCol": "geoid", "nameCol": "tract_name", "filterCol": "county_name", "filterVals": ["Mecklenburg County"],
              "norm": "minmax", "floor": 0.01, "winsor": 0, "missing": "exclude", "cvMax": 30,
              "excludeUnreliable": False, "fallbackEqual": True, "gap": "raw"},
}


def project():
    dims = [dict(id=i, name=n, desc=d) for i, n, d in DIMS]
    inds = [dict(id=i, dimId=dim, name=name, pillar=p, dir=d, column=col, cvColumn="", source=src)
            for i, dim, name, p, d, src, col in INDICATORS]
    return dict(title="AI Readiness Index — Charlotte (4 dimensions, 11 indicators)",
                goal="AI readiness of Charlotte census tracts", dims=dims, inds=inds, locked=False, settings=SETTINGS)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    p = project()
    path = os.path.join(OUT, "ari_11_indicators_four_dimensions.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(dict(format="ari-ahp-studio", version=1, project=p, participants={}), f, ensure_ascii=False, indent=1)
    k = [sum(1 for i in p["inds"] if i["dimId"] == d["id"]) for d in p["dims"]]
    l1 = len(p["dims"]) * (len(p["dims"]) - 1) // 2
    l2 = [n * (n - 1) // 2 for n in k]
    print(f"{path}: Level 1 {l1} comparisons; "
          + ", ".join(f"{d['name']} {n} ind. ({c})" for d, n, c in zip(p["dims"], k, l2))
          + f"; total {l1 + sum(l2)} per person")
