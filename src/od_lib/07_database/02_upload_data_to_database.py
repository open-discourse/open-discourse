from sqlalchemy import create_engine
import od_lib.definitions.path_definitions as path_definitions
import pandas as pd
import os
import datetime
import sys


engine = create_engine("postgresql://postgres:postgres@localhost:5432/next")

# Load Final Data ______________________________________________________________

CONTRIBUTIONS = os.path.join(path_definitions.DATA_FINAL, "contributions.pkl")
MISCELLANEOUS = os.path.join(path_definitions.DATA_FINAL, "miscellaneous.pkl")
SPOKEN_CONTENT = os.path.join(path_definitions.DATA_FINAL, "spoken_content.pkl")
FACTIONS = os.path.join(path_definitions.DATA_FINAL, "factions.pkl")
PEOPLE = os.path.join(path_definitions.DATA_FINAL, "people.csv")
TEXT_POSITION_X_TEXT = os.path.join(
    path_definitions.TEXT_POSITION_X_TEXT, "text_position_x_text.pkl"
)
TEXT_POSITION_X_TEXT_WP19 = os.path.join(
    path_definitions.TEXT_POSITION_X_TEXT, "text_position_x_text_wp_19.pkl"
)
ELECTION_PERIOD = os.path.join(path_definitions.ELECTION_PERIOD, "election_periods.csv")

# Load data ____________________________________________________________________
election_periods = pd.read_csv(ELECTION_PERIOD)

people = pd.read_csv(PEOPLE)
people = people.drop_duplicates(subset=["ui"], keep="first")
people = people.drop(
    [
        "wp_period",
        "faction_id",
        "institution_type",
        "institution_name",
        "institution_member_from",
        "institution_member_until",
    ],
    axis=1,
)

people.columns = [
    "id",
    "first_name",
    "last_name",
    "birth_place",
    "birth_country",
    "birth_year",
    "death_year",
    "gender",
    "profession",
    "location_information",
    "aristocracy",
    "prefix",
    "academic_title",
    "salutation",
    "vita_short",
    "disclosure_requirement",
    "electoral_district_number",
    "electoral_district_name",
    "electoral_district_region",
    "electoral_list",
    "type_of_mandate",
    "mdb_from",
    "mdb_until",
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
    "location_information": None,
    "aristocracy": None,
    "prefix": None,
    "academic_title": None,
    "salutation": None,
    "vita_short": None,
    "disclosure_requirement": None,
    "electoral_district_number": None,
    "electoral_district_name": None,
    "electoral_list": None,
    "mdb_from": None,
    "mdb_until": None,
    "history_from": None,
    "history_until": None,
    "function_long": None,
    "function_from": None,
    "function_until": None,
}

people = people.append(pd.Series(series), ignore_index=True)


def convert_date(date):
    # try:
    date = datetime.datetime.strptime(date, "%d.%m.%Y")
    date = date.strftime("%Y-%m-%d %H:%M:%S")
    return date
    # except:
    #     return None


def check_people(row):
    speaker_id = row.people_id

    people_ids = people.id.tolist()
    if speaker_id not in people_ids:
        speaker_id = -1
    return speaker_id


if "election_periods" in sys.argv or "all" in sys.argv:
    print("starting election_periods..")
    election_periods.to_sql(
        "election_periods", engine, if_exists="append", schema="app_public", index=False
    )


if "people" in sys.argv or "all" in sys.argv:
    print("starting people..")

    people = people.where((pd.notnull(people)), None)

    people.birth_year = people.birth_year.apply(convert_date)
    people.death_year = people.death_year.apply(convert_date)
    people.mdb_from = people.mdb_from.apply(convert_date)
    people.mdb_until = people.mdb_until.apply(convert_date)
    people.history_from = people.history_from.apply(convert_date)
    people.history_until = people.history_until.apply(convert_date)
    people.function_from = people.function_from.apply(convert_date)
    people.function_until = people.function_until.apply(convert_date)

    people.to_sql(
        "people", engine, if_exists="append", schema="app_public", index=False
    )

if "factions" in sys.argv or "all" in sys.argv:
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
                "CDU/SCU",
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
        "factions", engine, if_exists="append", schema="app_public", index=False
    )

if "spoken" in sys.argv or "all" in sys.argv:
    print("starting speeches..")

    speeches = pd.read_pickle(SPOKEN_CONTENT)

    speeches = speeches.where((pd.notnull(speeches)), None)
    speeches.people_id = speeches.apply(check_people, axis=1)

    speeches.to_sql(
        "speeches", engine, if_exists="append", schema="app_public", index=False
    )


if "contributions" in sys.argv or "all" in sys.argv:
    print("starting contributions..")

    contributions = pd.read_pickle(CONTRIBUTIONS)

    contributions = contributions.where((pd.notnull(contributions)), None)

    contributions.to_sql(
        "contributions", engine, if_exists="append", schema="app_public", index=False
    )

if "miscellaneous" in sys.argv or "all" in sys.argv:
    print("starting miscellaneous..")

    miscellaneous = pd.read_pickle(MISCELLANEOUS)

    miscellaneous = miscellaneous.where((pd.notnull(miscellaneous)), None)

    miscellaneous.to_sql(
        "miscellaneous", engine, if_exists="append", schema="app_public", index=False
    )

if "text_position_x_text" in sys.argv or "all" in sys.argv:
    print("starting text_position_x_text..")

    text_position_x_text = pd.read_pickle(TEXT_POSITION_X_TEXT)

    text_position_x_text_wp_19 = pd.read_pickle(TEXT_POSITION_X_TEXT_WP19)

    text_position_x_text = pd.concat(
        [text_position_x_text, text_position_x_text_wp_19], sort=False
    )

    text_position_x_text = text_position_x_text.where(
        (pd.notnull(text_position_x_text)), None
    )

    text_position_x_text["id"] = range(len(text_position_x_text.deleted_text))

    text_position_x_text.to_sql(
        "text_position_x_text",
        engine,
        if_exists="append",
        schema="app_public",
        index=False,
    )

print("finished")
