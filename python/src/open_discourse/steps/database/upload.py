import datetime

import numpy as np
import pandas as pd
from sqlalchemy import create_engine

import open_discourse.definitions.path_definitions as path_definitions

engine = create_engine("postgresql://postgres:postgres@localhost:5432/next")

# Load Final Data

CONTRIBUTIONS_EXTENDED = path_definitions.DATA_FINAL / "contributions_extended.pkl"
SPOKEN_CONTENT = path_definitions.DATA_FINAL / "speech_content.pkl"
FACTIONS = path_definitions.DATA_FINAL / "factions.pkl"
PEOPLE = path_definitions.DATA_FINAL / "politicians.csv"
CONTRIBUTIONS_SIMPLIFIED = (
    path_definitions.CONTRIBUTIONS_SIMPLIFIED / "contributions_simplified.pkl"
)
CONTRIBUTIONS_SIMPLIFIED_WP20 = (
    path_definitions.CONTRIBUTIONS_SIMPLIFIED
    / "electoral_term_pp20"
    / "contributions_simplified.pkl"
)
ELECTORAL_TERMS = path_definitions.ELECTORAL_TERMS / "electoral_terms.csv"

# Load data
electoral_terms = pd.read_csv(ELECTORAL_TERMS)

politicians = pd.read_csv(PEOPLE)
politicians = politicians.drop_duplicates(subset=["ui"], keep="first")
politicians = politicians.drop(
    [
        "electoral_term",
        "faction_id",
        "institution_type",
        "institution_name",
        "constituency",
    ],
    axis=1,
)

politicians.columns = [
    "id",
    "first_name",
    "last_name",
    "birth_place",
    "birth_country",
    "birth_date",
    "death_date",
    "gender",
    "profession",
    "aristocracy",
    "academic_title",
]

series = {
    "id": -1,
    "first_name": "Not found",
    "last_name": "",
    "birth_place": None,
    "birth_country": None,
    "birth_date": None,
    "death_date": None,
    "gender": None,
    "profession": None,
    "aristocracy": None,
    "academic_title": None,
}

politicians = pd.concat([politicians, pd.DataFrame([series])], ignore_index=True)


def convert_date_politicians(date):
    try:
        date = datetime.datetime.strptime(date, "%d.%m.%Y")
        date = date.strftime("%Y-%m-%d %H:%M:%S")
        return date
    except (ValueError, TypeError):
        return None


def convert_date_speeches(date):
    try:
        date = datetime.datetime.fromtimestamp(date)
        date = date.strftime("%Y-%m-%d %H:%M:%S")
        return date
    except (ValueError, TypeError) as e:
        print(e)
        return None


def check_politicians(row):
    speaker_id = row["politician_id"]

    politician_ids = politicians["id"].tolist()
    if speaker_id not in politician_ids:
        speaker_id = -1
    return speaker_id


print("Upload electoral_terms...", end="", flush=True)
electoral_terms.to_sql(
    "electoral_terms", engine, if_exists="append", schema="open_discourse", index=False
)
print("Done.")

print("Upload politicians...", end="", flush=True)

politicians = politicians.where((pd.notnull(politicians)), None)

politicians["birth_date"] = politicians["birth_date"].apply(convert_date_politicians)
politicians["death_date"] = politicians["death_date"].apply(convert_date_politicians)

politicians.to_sql(
    "politicians", engine, if_exists="append", schema="open_discourse", index=False
)
print("Done.")

print("Upload factions...", end="", flush=True)
# list of all factions in the form ["abbreviation", "full_name"]
factions = [
    ["not found", "not found"],
    ["AfD", "Alternative für Deutschland"],
    ["BHE", "Block der Heimatvertriebenen und Entrechteten"],
    ["BP", "Bayernpartei"],
    ["BSW", "Bündnis Sahra Wagenknecht"],
    ["Grüne", "Bündnis 90/Die Grünen"],
    [
        "CDU/CSU",
        "Christlich Demokratische Union Deutschlands/Christlich-Soziale Union in Bayern",
    ],
    ["DA", "Demokratische Arbeitsgemeinschaft"],
    ["DIE LINKE.", "DIE LINKE."],
    ["DP", "Deutsche Partei"],
    ["DP/DPB", "Deutsche Partei/Deutsche Partei Bayern"],
    ["DP/FVP", "Deutsche Partei/Freie Volkspartei"],
    ["DPB", "Deutsche Partei Bayern"],
    ["DRP", "Deutsche Reformpartei"],
    ["DRP/NR", "Deutsche Reichspartei/Nationale Rechte"],
    ["DSU", "Deutsche Soziale Union"],
    ["FDP", "Freie Demokratische Partei"],
    ["FU", "Föderalistische Union"],
    ["FVP", "Freie Volkspartei"],
    ["Fraktionslos", "Fraktionslos"],
    ["GB/BHE", "Gesamtdeutscher Block/Bund der Heimatvertriebenen und Entrechteten"],
    ["Gast", "Gast"],
    ["KO", "Kraft/Oberländer-Gruppe"],
    ["KPD", "Kommunistische Partei Deutschlands"],
    ["NR", "Nationale Rechte"],
    ["PDS", "Partei des Demokratischen Sozialismus"],
    ["SPD", "Sozialdemokratische Partei Deutschlands"],
    ["SSW", "Südschleswigscher Wählerverband"],
    ["WAV", "Wirtschaftliche Aufbau-Vereinigung"],
    ["Z", "Deutsche Zentrumspartei"],
]

# convert to dataframe and add id-field
factions = pd.DataFrame(
    [[idx - 1, *entry] for idx, entry in enumerate(factions)],
    columns=["id", "abbreviation", "full_name"],
)
factions["id"] = factions["id"].astype(int)

# factions.to_sql(
#     "factions", engine, if_exists="append", schema="open_discourse", index=False
# )
print("Done.")

print("Upload speeches...", end="", flush=True)

speeches: pd.DataFrame = pd.read_pickle(SPOKEN_CONTENT)

speeches["date"] = speeches["date"].apply(convert_date_speeches)

speeches = speeches.where((pd.notnull(speeches)), None)
speeches = speeches.replace({"position_long": {r"^\s*$": None}}, regex=True)
speeches["politician_id"] = np.where(
    speeches["politician_id"].isin(politicians["id"]),
    speeches["politician_id"],
    np.ones(len(speeches)) * -1,
)

# speeches.to_sql(
#     "speeches", engine, if_exists="append", schema="open_discourse", index=False
# )
print(speeches.shape)
print("Done.")

print("Upload contributions_extended...", end="", flush=True)

contributions_extended = pd.read_pickle(CONTRIBUTIONS_EXTENDED)

contributions_extended = contributions_extended.where(
    (pd.notnull(contributions_extended)), None
)

contributions_extended.to_sql(
    "contributions_extended",
    engine,
    if_exists="append",
    schema="open_discourse",
    index=False,
)
print("Done.")

print("Upload contributions_simplified...", end="", flush=True)

contributions_simplified = pd.read_pickle(CONTRIBUTIONS_SIMPLIFIED)
contributions_simplified_electoral_term_20 = pd.read_pickle(
    CONTRIBUTIONS_SIMPLIFIED_WP20
)

contributions_simplified = pd.concat(
    [
        contributions_simplified,
        contributions_simplified_electoral_term_20,
    ],
    sort=False,
)

contributions_simplified = contributions_simplified.where(
    (pd.notnull(contributions_simplified)), None
)

contributions_simplified["id"] = range(len(contributions_simplified.content))

contributions_simplified.to_sql(
    "contributions_simplified",
    engine,
    if_exists="append",
    schema="open_discourse",
    index=False,
)
print("Done.")
