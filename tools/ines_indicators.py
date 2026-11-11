"""
The INES indicator set for the Charlotte AI Readiness Index: chosen indicators C1-C20 and additional candidates
A1-A14, as defined in "Candidate Indicators for a Census-Tract AI Readiness Index" (INES Group, October 2026).

This file is the single source of truth for
  - tools/census_bridge.py         which downloads the ACS columns, computes every indicator with its margin of error
                                   and checks each Census column label before using it;
  - tools/build_standalone.py      which writes the studio's "INES indicator set" catalogue from catalogue_rows().

Each indicator has
  column   the column of data/ari_tracts_2024.csv that the catalogue links to. Where CRXP publishes the indicator,
           this is the CRXP column (the document's preferred source, with CRXP's reliability flags); otherwise it is
           a share computed here from the ACS.
  acs      the ACS definition, exactly as in the document's Columns field:
             share   100 x sum(num) / (sum(den) - sum(den_minus))
             value   a single published value (median, Gini index)
             ratio   (sum(num) / sum(den)) / (sum(num2) / sum(den2))   (the Internet Income Ratio, A3)
           For CRXP indicators the ACS definition is computed too and compared with CRXP's values (a cross-check).
  check    (codes, text): every listed code's Census label must contain the text, or the bridge stops.
"""


def r(table, *lines):
    """ACS estimate codes, e.g. r("B15003", 22, 23) -> ["B15003_022E", "B15003_023E"]."""
    return [f"{table}_{n:03d}E" for n in lines]


def span(table, a, b):
    return r(table, *range(a, b + 1))


C9_GROUPS = ["Business and financial operations occupations", "Computer and mathematical occupations",
             "Architecture and engineering occupations", "Life, physical, and social science occupations",
             "Legal occupations", "Office and administrative support occupations"]
C9_MALE = r("C24010", 6, 8, 9, 10, 13, 29)
C9_FEMALE = r("C24010", 42, 44, 45, 46, 49, 65)
LEP_PERSONS = r("C16001", *range(5, 39, 3))                       # 005, 008, ..., 038
DISABILITY = r("B18101", 4, 7, 10, 13, 16, 19, 23, 26, 29, 32, 35, 38)
UNDER18 = span("B01001", 3, 6) + span("B01001", 27, 30)

INDICATORS = [
    # ------------------------------------------------------------------ chosen: Engagement Opportunity pillar (code S; the proposal's Supply)
    dict(id="C1", name="Broadband of any type subscription rate", pillar="S", dir=1, theme="economy", tag="Chosen",
         source="ACS B28002 · CRXP 10", column="acs-broadband-any", crxp="internet-access",
         measure="Households with a broadband subscription of any type (cable, fibre, DSL, satellite or cellular data plan), share of all households.",
         acs=dict(kind="share", num=r("B28002", 4), den=r("B28002", 1)),
         check=[(r("B28002", 4), "Broadband of any type")]),
    dict(id="C2", name="Households with no internet access", pillar="S", dir=-1, theme="economy", tag="Chosen",
         source="ACS B28002", column="acs-no-internet",
         measure="Households with no internet access, share of all households.",
         acs=dict(kind="share", num=r("B28002", 13), den=r("B28002", 1)),
         check=[(r("B28002", 13), "No Internet access")]),
    dict(id="C3", name="Cellular-data-only households", pillar="S", dir=-1, theme="economy", tag="Chosen",
         source="ACS B28002", column="acs-cellular-only",
         measure="Households whose only internet subscription is a cellular data plan, share of all households.",
         acs=dict(kind="share", num=r("B28002", 6), den=r("B28002", 1)),
         check=[(r("B28002", 6), "Cellular data plan with no other type of Internet subscription")]),
    dict(id="C4", name="Computer with broadband subscription", pillar="S", dir=1, theme="economy", tag="Chosen",
         source="ACS B28003", column="acs-computer-broadband",
         measure="Households with a computer and a broadband subscription, share of all households.",
         acs=dict(kind="share", num=r("B28003", 4), den=r("B28003", 1)),
         check=[(r("B28003", 4), "Has a computer › With a broadband Internet subscription")]),
    dict(id="C5", name="Smartphone-only households", pillar="S", dir=-1, theme="economy", tag="Chosen",
         source="ACS B28001", column="acs-smartphone-only",
         measure="Households whose only computing device is a smartphone, share of all households.",
         acs=dict(kind="share", num=r("B28001", 6), den=r("B28001", 1)),
         check=[(r("B28001", 6), "Smartphone with no other type of computing device")]),
    dict(id="C6", name="Low-income broadband adoption", pillar="S", dir=1, theme="economy", tag="Chosen",
         source="ACS B28004", column="acs-lowincome-broadband",
         measure="Broadband subscription rate among households with income below $20,000. Small cells: expect large margins of error.",
         acs=dict(kind="share", num=r("B28004", 4, 8), den=r("B28004", 2, 6)),
         check=[(r("B28004", 4, 8), "With a broadband Internet subscription"), (r("B28004", 2, 4), "Less than $10,000"),
                (r("B28004", 6, 8), "$10,000 to $19,999")]),
    # ------------------------------------------------------------------ chosen: Adoption Potential pillar (code D; the proposal's Demand)
    dict(id="C7", name="Bachelor's degree or higher", pillar="D", dir=1, theme="education", tag="Chosen",
         source="ACS B15003 · CRXP 11", column="bachelors-or-higher", crxp="bachelors-or-higher",
         measure="Adults 25+ with a bachelor's, master's, professional or doctoral degree, share of all adults 25+.",
         acs=dict(kind="share", num=span("B15003", 22, 25), den=r("B15003", 1)),
         check=[(r("B15003", 22), "Bachelor's degree"), (r("B15003", 23), "Master's degree"),
                (r("B15003", 24), "Professional school degree"), (r("B15003", 25), "Doctorate degree")]),
    dict(id="C8", name="Less than high school education", pillar="D", dir=-1, theme="education", tag="Chosen",
         source="ACS B15003 · CRXP 12 (complement)", column="acs-less-than-hs", crxp="high-school-diploma", crxp_complement=True,
         measure="Adults 25+ with no schooling through 12th grade without a diploma, share of all adults 25+ (100 minus CRXP's high-school-diploma).",
         acs=dict(kind="share", num=span("B15003", 2, 16), den=r("B15003", 1)),
         check=[(r("B15003", 2), "No schooling completed"), (r("B15003", 16), "12th grade, no diploma"),
                (span("B15003", 5, 15), "grade")]),
    dict(id="C9", name="High-AI-exposure occupation share", pillar="D", dir=0, theme="economy", tag="Chosen",
         source="ACS C24010", column="acs-high-ai-exposure-occ",
         measure="Employed civilians 16+ in business and financial operations, computer and mathematical, architecture and engineering, "
                 "life, physical and social science, legal, and office and administrative support occupations. Direction not fixed.",
         acs=dict(kind="share", num=C9_MALE + C9_FEMALE, den=r("C24010", 1)),
         check=[([m, f], g) for m, f, g in zip(C9_MALE, C9_FEMALE, C9_GROUPS)] + [(C9_MALE, "› Male ›"), (C9_FEMALE, "› Female ›")]),
    dict(id="C10", name="Management, business, science and arts occupation share", pillar="D", dir=1, theme="economy", tag="Chosen",
         source="ACS C24010 · CRXP 59", column="white-collar", crxp="white-collar",
         measure="Employed civilians 16+ in the management, business, science and arts major group (male plus female).",
         acs=dict(kind="share", num=r("C24010", 3, 39), den=r("C24010", 1)),
         check=[(r("C24010", 3, 39), "› Management, business, science, and arts occupations")]),
    dict(id="C11", name="Labour-force participation rate", pillar="D", dir=1, theme="economy", tag="Chosen",
         source="ACS B23025", column="acs-labour-force-participation",
         measure="Population 16+ in the labour force, share of the population 16+.",
         acs=dict(kind="share", num=r("B23025", 2), den=r("B23025", 1)),
         check=[(r("B23025", 2), "In labor force")]),
    dict(id="C12", name="Unemployment rate", pillar="D", dir=-1, theme="economy", tag="Chosen",
         source="ACS B23025 · CRXP 31", column="unemployment-rate", crxp="unemployment-rate",
         measure="Unemployed, share of the civilian labour force.",
         acs=dict(kind="share", num=r("B23025", 5), den=r("B23025", 3)),
         check=[(r("B23025", 5), "Civilian labor force › Unemployed"), (r("B23025", 3), "Civilian labor force")]),
    dict(id="C13", name="Population aged 65 and over", pillar="D", dir=-1, theme="character", tag="Chosen",
         source="ACS B01001 · CRXP 1", column="older-adults", crxp="older-adults",
         measure="Residents aged 65 and over, share of total population.",
         acs=dict(kind="share", num=span("B01001", 20, 25) + span("B01001", 44, 49), den=r("B01001", 1)),
         check=[(r("B01001", 20, 44), "65 and 66 years"), (r("B01001", 25, 49), "85 years and over")]),
    # CRXP's "limited-english-households" (id 34) is NOT this indicator: its values equal 100 x (C16002_001 - C16002_002) /
    # C16002_001, the share of households speaking a language other than English, in every tract (checked by the bridge
    # and by verification/verify_math.py). So C14 is computed here from the ACS, as the document defines it.
    dict(id="C14", name="Limited English proficiency (households)", pillar="D", dir=-1, theme="character", tag="Chosen",
         source="ACS C16002 (not CRXP 34; see note)", column="acs-lep-households",
         measure="Households in which no one aged 14+ speaks English \"very well\", share of all households. The document's preferred unit. "
                 "CRXP's limited-english-households column is the share of households speaking a language other than English, not this.",
         acs=dict(kind="share", num=r("C16002", 4, 7, 10, 13), den=r("C16002", 1)),
         crxp_mismatch=dict(column="limited-english-households", actual=dict(kind="share", num=r("C16002", 1), den=r("C16002", 1), num_minus=r("C16002", 2)),
                            actual_text="100 x (C16002_001 - C16002_002) / C16002_001: households speaking a language other than English"),
         check=[(r("C16002", 4, 7, 10, 13), "› Limited English speaking household"), (r("C16002", 2), "English only")]),
    dict(id="C14p", name="Limited English proficiency (persons 5+)", pillar="D", dir=-1, theme="character", tag="Chosen (alternative unit)",
         source="ACS C16001", column="acs-lep-persons",
         measure="Persons 5+ who speak English less than \"very well\", share of all persons 5+ (the SVI's person-based form).",
         acs=dict(kind="share", num=LEP_PERSONS, den=r("C16001", 1)),
         check=[(LEP_PERSONS, "Speak English less than \"very well\"")]),
    dict(id="C15", name="Disability prevalence", pillar="D", dir=-1, theme="health", tag="Chosen",
         source="ACS B18101 · CRXP 62", column="disability", crxp="disability",
         measure="Civilian noninstitutionalised residents with a disability, share of the civilian noninstitutionalised population.",
         acs=dict(kind="share", num=DISABILITY, den=r("B18101", 1)),
         check=[(DISABILITY, "› With a disability")]),
    dict(id="C16", name="Median household income", pillar="D", dir=1, theme="economy", tag="Chosen",
         source="ACS B19013 · CRXP 20", column="household-income", crxp="household-income",
         measure="Median household income in the past 12 months, in dollars of the survey's final year.",
         acs=dict(kind="value", code="B19013_001E"),
         check=[(["B19013_001E"], "Median household income")]),
    dict(id="C17", name="Poverty rate", pillar="D", dir=-1, theme="economy", tag="Chosen",
         source="ACS B17001 · CRXP 30", column="poverty-rate", crxp="poverty-rate",
         measure="People with income below the poverty level, share of people for whom poverty status is determined.",
         acs=dict(kind="share", num=r("B17001", 2), den=r("B17001", 1)),
         check=[(r("B17001", 2), "below poverty level")]),
    dict(id="C18", name="Work-from-home share", pillar="D", dir=1, theme="economy", tag="Chosen",
         source="ACS B08301", column="acs-work-from-home",
         measure="Workers 16+ who worked from home, share of all workers 16+.",
         acs=dict(kind="share", num=r("B08301", 21), den=r("B08301", 1)),
         check=[(r("B08301", 21), "Worked from home")]),
    dict(id="C19", name="School and college enrolment (all levels, age 3+)", pillar="D", dir=1, theme="education", tag="Chosen",
         source="ACS B14001 · CRXP 58", column="school-enrollment", crxp="school-enrollment",
         measure="Population 3+ enrolled in school at any level, share of the population 3+ (CRXP's version).",
         acs=dict(kind="share", num=r("B14001", 2), den=r("B14001", 1)),
         check=[(r("B14001", 2), "Enrolled in school")]),
    dict(id="C19c", name="College enrolment (share of adults 18+)", pillar="D", dir=1, theme="education", tag="Chosen (alternative construct)",
         source="ACS B14001, B01001", column="acs-college-enrolment",
         measure="Undergraduate plus graduate or professional enrolment, over the population 18+ (total population minus residents under 18).",
         acs=dict(kind="share", num=r("B14001", 8, 9), den=r("B01001", 1), den_minus=UNDER18),
         check=[(r("B14001", 8), "Enrolled in college, undergraduate years"), (r("B14001", 9), "Graduate or professional school"),
                (r("B01001", 3, 27), "Under 5 years"), (r("B01001", 6, 30), "15 to 17 years")]),
    dict(id="C20", name="Information and professional-services employment", pillar="D", dir=1, theme="economy", tag="Chosen",
         source="ACS C24030", column="acs-info-prof-services",
         measure="Employed residents 16+ in the Information industry and in Professional, scientific and technical services, share of all employed civilians 16+.",
         acs=dict(kind="share", num=r("C24030", 13, 40, 18, 45), den=r("C24030", 1)),
         check=[(r("C24030", 13, 40), "› Information"), (r("C24030", 18, 45), "Professional, scientific, and technical services")]),
    dict(id="C20f", name="Information, professional services, and finance and insurance employment", pillar="D", dir=1, theme="economy",
         tag="Chosen (variant with finance)", source="ACS C24030", column="acs-info-prof-finance",
         measure="C20 plus Finance and insurance, as the document suggests given Charlotte's banking sector.",
         acs=dict(kind="share", num=r("C24030", 13, 40, 18, 45, 15, 42), den=r("C24030", 1)),
         check=[(r("C24030", 15, 42), "› Finance and insurance")]),
    # ------------------------------------------------------------------ additional candidates: Engagement Opportunity side
    dict(id="A1", name="Fixed wireline broadband subscription rate", pillar="S", dir=1, theme="economy", tag="Recommended addition",
         source="ACS B28002", column="acs-fixed-broadband",
         measure="Households subscribing to cable, fibre-optic or DSL broadband, share of all households.",
         acs=dict(kind="share", num=r("B28002", 7), den=r("B28002", 1)),
         check=[(r("B28002", 7), "Broadband such as cable, fiber optic or DSL")]),
    dict(id="A2", name="Households with no computing device", pillar="S", dir=-1, theme="economy", tag="Optional (alternative to C4)",
         source="ACS B28001", column="acs-no-computer",
         measure="Households with no computer of any kind, including smartphones and tablets, share of all households.",
         acs=dict(kind="share", num=r("B28001", 11), den=r("B28001", 1)),
         check=[(r("B28001", 11), "No Computer")]),
    dict(id="A3", name="Internet Income Ratio", pillar="S", dir=-1, theme="economy", tag="Optional (alternative to C6)",
         source="ACS B28004", column="acs-internet-income-ratio",
         measure="Share without an internet subscription among households under $35,000, divided by that share among households at $75,000 or more. "
                 "A ratio, not a percentage; unstable where few high-income households lack a subscription.",
         acs=dict(kind="ratio", num=r("B28004", 5, 9, 13), den=r("B28004", 2, 6, 10), num2=r("B28004", 25), den2=r("B28004", 22)),
         check=[(r("B28004", 5, 9, 13, 25), "Without an Internet subscription"), (r("B28004", 10), "$20,000 to $34,999"),
                (r("B28004", 22, 25), "$75,000 or more")]),
    dict(id="A4", name="Broadband subscription among residents aged 65+", pillar="S", dir=1, theme="economy", tag="Exploratory",
         source="ACS B28005", column="acs-seniors-connected",
         measure="Persons 65+ in households with a computer and broadband, share of all persons 65+ in households.",
         acs=dict(kind="share", num=r("B28005", 17), den=r("B28005", 14)),
         check=[(r("B28005", 17), "65 years and over › Has a computer › With a broadband Internet subscription"), (r("B28005", 14), "65 years and over")]),
    dict(id="A5", name="Broadband subscription among adults without a high school diploma", pillar="S", dir=1, theme="economy", tag="Exploratory",
         source="ACS B28006", column="acs-nodiploma-connected",
         measure="Adults 25+ with less than high school in households with a computer and broadband, share of all adults 25+ with less than high school.",
         acs=dict(kind="share", num=r("B28006", 5), den=r("B28006", 2)),
         check=[(r("B28006", 5), "Less than high school graduate or equivalency › Has a computer › With a broadband Internet subscription"),
                (r("B28006", 2), "Less than high school graduate or equivalency")]),
    dict(id="A6", name="Broadband subscription among employed residents", pillar="S", dir=1, theme="economy", tag="Exploratory",
         source="ACS B28007", column="acs-employed-connected",
         measure="Employed civilians 16+ in households with a computer and broadband, share of all employed civilians 16+.",
         acs=dict(kind="share", num=r("B28007", 6), den=r("B28007", 3)),
         check=[(r("B28007", 6), "Employed › Has a computer › With a broadband Internet subscription"), (r("B28007", 3), "› Employed")]),
    # ------------------------------------------------------------------ additional candidates: Adoption Potential side
    dict(id="A7", name="Employment–population ratio", pillar="D", dir=1, theme="economy", tag="Optional (alternative to C11 and C12)",
         source="ACS B23025 · CRXP 9", column="employment", crxp="employment",
         measure="Employed civilians, share of the population 16+.",
         acs=dict(kind="share", num=r("B23025", 4), den=r("B23025", 1)),
         check=[(r("B23025", 4), "Civilian labor force › Employed")]),
    dict(id="A8", name="Population aged 18–34", pillar="D", dir=1, theme="character", tag="Recommended addition",
         source="ACS B01001", column="acs-age-18-34",
         measure="Residents aged 18 to 34, share of total population.",
         acs=dict(kind="share", num=span("B01001", 7, 12) + span("B01001", 31, 36), den=r("B01001", 1)),
         check=[(r("B01001", 7, 31), "18 and 19 years"), (r("B01001", 12, 36), "30 to 34 years")]),
    dict(id="A9", name="Households with children", pillar="D", dir=1, theme="character", tag="Recommended addition",
         source="ACS B11005 · CRXP 53", column="households-with-children", crxp="households-with-children",
         measure="Households with one or more people under 18, share of all households.",
         acs=dict(kind="share", num=r("B11005", 2), den=r("B11005", 1)),
         check=[(r("B11005", 2), "one or more people under 18 years")]),
    dict(id="A10", name="Income inequality (Gini index)", pillar="D", dir=-1, theme="economy", tag="Exploratory",
         source="ACS B19083 · CRXP 57", column="gini-index", crxp="gini-index",
         measure="Gini index of household income (0 = equal, 1 = unequal). Better used to qualify scores than as a weighted component.",
         acs=dict(kind="value", code="B19083_001E"),
         check=[(["B19083_001E"], "Gini Index")]),
    dict(id="A11", name="Households receiving SNAP", pillar="D", dir=-1, theme="economy", tag="Exploratory",
         source="ACS B22010 · CRXP 33", column="snap-households", crxp="snap-households",
         measure="Households that received SNAP benefits in the past 12 months, share of all households. An alternative to C17, not an addition.",
         acs=dict(kind="share", num=r("B22010", 2), den=r("B22010", 1)),
         check=[(r("B22010", 2), "received Food Stamps/SNAP")]),
    dict(id="A12", name="Foreign-born residents", pillar="D", dir=0, theme="character", tag="Exploratory",
         source="ACS B05012 · CRXP 63", column="foreign-born", crxp="foreign-born",
         measure="Residents born outside the United States, share of total population. Direction not fixed.",
         acs=dict(kind="share", num=r("B05012", 3), den=r("B05012", 1)),
         check=[(r("B05012", 3), "Foreign-born")]),
    dict(id="A13", name="Households without a vehicle", pillar="D", dir=-1, theme="transportation", tag="Optional",
         source="ACS B08201 · CRXP 17", column="no-vehicle", crxp="no-vehicle",
         measure="Households with no vehicle available, share of all households.",
         acs=dict(kind="share", num=r("B08201", 2), den=r("B08201", 1)),
         check=[(r("B08201", 2), "No vehicle available")]),
    dict(id="A14", name="Transportation barriers", pillar="D", dir=-1, theme="health", tag="Exploratory",
         source="CDC PLACES · CRXP 68 (model-based)", column="transportation-barriers", crxp="transportation-barriers",
         measure="Adults reporting a lack of reliable transportation in the past year. Model-based, not a survey estimate; no ACS equivalent.",
         acs=None, check=[]),
]


def acs_codes(ind):
    a = ind.get("acs")
    if not a:
        return []
    if a["kind"] == "value":
        return [a["code"]]
    codes = [c for k in ("num", "den", "den_minus", "num2", "den2") for c in a.get(k, [])]
    mm = ind.get("crxp_mismatch")
    if mm:
        codes += [c for k in ("num", "den", "num_minus") for c in mm["actual"].get(k, []) if c not in codes]
    return codes


def all_codes():
    return sorted({c for i in INDICATORS for c in acs_codes(i)})


def formula(ind):
    a = ind.get("acs")
    if not a:
        return "CRXP only (CDC PLACES)"
    s = lambda cs: " + ".join(c[:-1] for c in cs)
    if a["kind"] == "value":
        return a["code"][:-1]
    if a["kind"] == "ratio":
        return f"[({s(a['num'])}) / ({s(a['den'])})] / [({s(a['num2'])}) / ({s(a['den2'])})]"
    den = s(a["den"]) + (f" - ({s(a['den_minus'])})" if a.get("den_minus") else "")
    return f"100 x ({s(a['num'])}) / ({den})"


def catalogue_rows():
    """Rows for the studio's catalogue: [id, name, pillar, dir, theme, source, column, description, tag]."""
    return [[i["id"], i["name"], i["pillar"], i["dir"], i["theme"], i["source"], i["column"], i["measure"], i["tag"]] for i in INDICATORS]
