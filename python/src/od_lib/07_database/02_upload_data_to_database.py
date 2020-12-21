from sqlalchemy import create_engine
import od_lib.definitions.path_definitions as path_definitions
import pandas as pd
import os
import datetime


engine = create_engine("postgresql://postgres:postgres@localhost:5432/next")

# Load Final Data

CONTRIBUTIONS = os.path.join(path_definitions.DATA_FINAL, "contributions.pkl")
SPOKEN_CONTENT = os.path.join(path_definitions.DATA_FINAL, "speech_content.pkl")
FACTIONS = os.path.join(path_definitions.DATA_FINAL, "factions.pkl")
PEOPLE = os.path.join(path_definitions.DATA_FINAL, "politicians.csv")
CONTRIBUTIONS_LOOKUP = os.path.join(
    path_definitions.CONTRIBUTIONS_LOOKUP, "contributions_lookup.pkl"
)
CONTRIBUTIONS_LOOKUP_WP19 = os.path.join(
    path_definitions.CONTRIBUTIONS_LOOKUP, "contributions_lookup_electoral_term_19.pkl"
)
ELECTORAL_TERMS = os.path.join(path_definitions.ELECTORAL_TERMS, "electoral_terms.csv")

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
        "institution_member_from",
        "institution_member_until",
    ],
    axis=1,
)

politicians.columns = [
    "id",
    "first_name",
    "last_name",
    "birth_place",
    "birth_country",
    "birth_year",
    "death_year",
    "gender",
    "profession",
    "constituency",
    "aristocracy",
    "prefix",
    "academic_title",
    "salutation",
    "vita_short",
    "disclosure_requirement",
    "constituency_number",
    "constituency_name",
    "constituency_region",
    "electoral_list",
    "type_of_mandate",
    "mp_from",
    "mp_until",
    "history_from",
    "history_until",
    "function_long",
    "function_from",
    "function_until",
]

series = {
    "id": -1,
    "first_name": "Not found",
    "last_name": "",
    "birth_place": None,
    "birth_country": None,
    "birth_year": None,
    "death_year": None,
    "gender": None,
    "profession": None,
    "constituency": None,
    "aristocracy": None,
    "prefix": None,
    "academic_title": None,
    "salutation": None,
    "vita_short": None,
    "disclosure_requirement": None,
    "constituency_number": None,
    "constituency_name": None,
    "electoral_list": None,
    "mp_from": None,
    "mp_until": None,
    "history_from": None,
    "history_until": None,
    "function_long": None,
    "function_from": None,
    "function_until": None,
}

politicians = politicians.append(pd.Series(series), ignore_index=True)


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
    speaker_id = row.politician_id

    politician_ids = politicians.id.tolist()
    if speaker_id not in politician_ids:
        speaker_id = -1
    return speaker_id


print("starting electoral_terms..")
electoral_terms.to_sql(
    "electoral_terms", engine, if_exists="append", schema="open_discourse", index=False
)


print("starting politicians..")

politicians = politicians.where((pd.notnull(politicians)), None)

politicians.birth_year = politicians.birth_year.apply(convert_date_politicians)
politicians.death_year = politicians.death_year.apply(convert_date_politicians)
politicians.mp_from = politicians.mp_from.apply(convert_date_politicians)
politicians.mp_until = politicians.mp_until.apply(convert_date_politicians)
politicians.history_from = politicians.history_from.apply(convert_date_politicians)
politicians.history_until = politicians.history_until.apply(convert_date_politicians)
politicians.function_from = politicians.function_from.apply(convert_date_politicians)
politicians.function_until = politicians.function_until.apply(convert_date_politicians)

politicians.to_sql(
    "politicians", engine, if_exists="append", schema="open_discourse", index=False
)


print("starting factions..")
factions = pd.DataFrame(
    {
        "id": [
            -1,
            0,
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            22,
            23,
            24,
            25,
            26,
        ],
        "abbreviation": [
            "not found",
            "AfD",
            "BHE",
            "BP",
            "Grüne",
            "CDU/CSU",
            "DA",
            "DIE LINKE.",
            "DP",
            "DP/DBP",
            "DP/FVP",
            "DPB",
            "DRP",
            "DRP/NR",
            "FDP",
            "FU",
            "FVP",
            "Fraktionslos",
            "GB/BHE",
            "Gast",
            "KO",
            "KPD",
            "NR",
            "PDS",
            "SPD",
            "SSW",
            "WAV",
            "Z",
        ],
        "full_name": [
            "not found",
            "Alternative für Deutschland",
            "Block der Heimatvertriebenen und Entrechteten",
            "Bayernpartei",
            "Bündnis 90/Die Grünen",
            "Christlich Demokratische Union Deutschlands/Christlich-Soziale Union in Bayern",
            "Demokratische Arbeitsgemeinschaft",
            "DIE LINKE.",
            "Deutsche Partei",
            "Deutsche Partei/Deutsche Partei Bayern",
            "Deutsche Partei/Freie Volkspartei",
            "Deutsche Partei Bayern",
            "Deutsche Reformpartei",
            "Deutsche Reichspartei/Nationale Rechte",
            "Freie Demokratische Partei",
            "Föderalistische Union",
            "Freie Volkspartei",
            "Fraktionslos",
            "Gesamtdeutscher Block/Bund der Heimatvertriebenen und Entrechteten",
            "Gast",
            "Kraft/Oberländer-Gruppe",
            "Kommunistische Partei Deutschlands",
            "Nationale Rechte",
            "Partei des Demokratischen Sozialismus",
            "Sozialdemokratische Partei Deutschlands",
            "Südschleswigscher Wählerverband",
            "Wirtschaftliche Aufbau-Vereinigung",
            "Deutsche Zentrumspartei",
        ],
    }
)

factions.id = factions.id.astype(int)

factions.to_sql(
    "factions", engine, if_exists="append", schema="open_discourse", index=False
)


print("starting speeches..")

speeches = pd.read_pickle(SPOKEN_CONTENT)

speeches["date"] = speeches["date"].apply(convert_date_speeches)

speeches = speeches.where((pd.notnull(speeches)), None)
speeches.politician_id = speeches.apply(check_politicians, axis=1)

speeches.to_sql(
    "speeches", engine, if_exists="append", schema="open_discourse", index=False
)


print("starting contributions..")

contributions = pd.read_pickle(CONTRIBUTIONS)

contributions = contributions.where((pd.notnull(contributions)), None)

contributions.to_sql(
    "contributions", engine, if_exists="append", schema="open_discourse", index=False
)


print("starting contributions_lookup..")

contributions_lookup = pd.read_pickle(CONTRIBUTIONS_LOOKUP)

contributions_lookup_electoral_term_19 = pd.read_pickle(CONTRIBUTIONS_LOOKUP_WP19)

contributions_lookup = pd.concat(
    [contributions_lookup, contributions_lookup_electoral_term_19], sort=False
)

contributions_lookup = contributions_lookup.where(
    (pd.notnull(contributions_lookup)), None
)

contributions_lookup["id"] = range(len(contributions_lookup.deleted_text))

contributions_lookup.to_sql(
    "contributions_lookup",
    engine,
    if_exists="append",
    schema="open_discourse",
    index=False,
)

print("finished")
