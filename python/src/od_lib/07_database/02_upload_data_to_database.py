from sqlalchemy import create_engine
import od_lib.definitions.path_definitions as path_definitions
import pandas as pd
import datetime


engine = create_engine("postgresql://postgres:postgres@localhost:5432/postgres")

# Load Final Data

CONTRIBUTIONS_EXTENDED = path_definitions.DATA_FINAL / "contributions_extended.pkl"
SPOKEN_CONTENT = path_definitions.DATA_FINAL / "speech_content.pkl"
FACTIONS = path_definitions.DATA_FINAL / "factions.pkl"
PEOPLE = path_definitions.DATA_FINAL / "politicians.csv"
CONTRIBUTIONS_SIMPLIFIED = path_definitions.CONTRIBUTIONS_SIMPLIFIED \
    / "contributions_simplified.pkl"
CONTRIBUTIONS_SIMPLIFIED_WP19 = path_definitions.CONTRIBUTIONS_SIMPLIFIED \
    / "electoral_term_19" / "contributions_simplified.pkl"
CONTRIBUTIONS_SIMPLIFIED_WP20 = path_definitions.CONTRIBUTIONS_SIMPLIFIED \
    / "electoral_term_20" / "contributions_simplified.pkl"
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

politicians = pd.concat([politicians, pd.Series(series)], ignore_index=True)


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

politicians.birth_date = politicians.birth_date.apply(convert_date_politicians)
politicians.death_date = politicians.death_date.apply(convert_date_politicians)

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
speeches.position_long.replace([r"^\s*$"], [None], regex=True, inplace=True)
speeches.politician_id = speeches.apply(check_politicians, axis=1)

speeches.to_sql(
    "speeches", engine, if_exists="append", schema="open_discourse", index=False
)


print("starting contributions_extended..")

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


print("starting contributions_simplified..")

contributions_simplified = pd.read_pickle(CONTRIBUTIONS_SIMPLIFIED)

contributions_simplified_electoral_term_19 = pd.read_pickle(
    CONTRIBUTIONS_SIMPLIFIED_WP19
)
contributions_simplified_electoral_term_20 = pd.read_pickle(
    CONTRIBUTIONS_SIMPLIFIED_WP20
)

contributions_simplified = pd.concat(
    [
        contributions_simplified,
        contributions_simplified_electoral_term_19,
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

print("finished")
