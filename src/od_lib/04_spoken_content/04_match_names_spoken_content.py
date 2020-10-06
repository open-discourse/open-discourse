import pandas as pd
import regex
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))
import path_definitions
from src.helper_functions.match_names import insert_people_id_into_spoken_content

# input directory ______________________________________________________________
SPOKEN_CONTENT_INPUT = path_definitions.SPOKEN_CONTENT_STAGE_03
DATA_FINAL = path_definitions.DATA_FINAL

# output directory _____________________________________________________________
SPOKEN_CONTENT_OUTPUT = path_definitions.SPOKEN_CONTENT_STAGE_04

if not os.path.exists(SPOKEN_CONTENT_OUTPUT):
    os.makedirs(SPOKEN_CONTENT_OUTPUT)

# MDBS
people = pd.read_csv(os.path.join(DATA_FINAL, "people.csv"))
people = people.loc[
    :,
    [
        "ui",
        "wp_period",
        "faction_id",
        "first_name",
        "last_name",
        "gender",
        "profession",
        "location_information",
        "institution_type",
    ],
].copy()

people = people.astype(dtype={"ui": "int64"})

# Some cleaning to make matching easier.
people.location_information = people.location_information.fillna("")

people.first_name = people.first_name.str.lower()
people.last_name = people.last_name.str.lower()
people.location_information = people.location_information.str.lower()

people.first_name = people.first_name.str.replace("ß", "ss", regex=False)
people.last_name = people.last_name.str.replace("ß", "ss", regex=False)

people.first_name = people.first_name.apply(str.split)

people.profession = people.profession.str.lower()

problem_df = pd.DataFrame()

# iterate over all wp_folders __________________________________________________
for wp_folder in sorted(os.listdir(SPOKEN_CONTENT_INPUT)):
    working = []
    if wp_folder == ".DS_Store":
        continue
    wp_folder_path = os.path.join(SPOKEN_CONTENT_INPUT, wp_folder)

    print(wp_folder)

    save_path = os.path.join(SPOKEN_CONTENT_OUTPUT, wp_folder)
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    wp = int(regex.sub("wp_0?", "", wp_folder))

    # Only select politicians of the election period.
    people_wp = people.loc[people.wp_period == wp]
    gov_members_wp = people_wp.loc[people_wp.institution_type == "Regierungsmitglied"]

    # iterate over every spoken_content file
    for spoken_content_file in sorted(os.listdir(wp_folder_path)):

        # check if sitting file is a pickle file
        if ".pkl" not in spoken_content_file:
            continue
        filepath = os.path.join(wp_folder_path, spoken_content_file)

        print(spoken_content_file)

        # read the spoken content pickle file
        spoken_content = pd.read_pickle(filepath)

        spoken_content_matched, problems = insert_people_id_into_spoken_content(
            spoken_content, people_wp, gov_members_wp, people
        )

        problem_df = problem_df.append(problems, ignore_index=True, sort=True)

        spoken_content_matched.to_pickle(os.path.join(save_path, spoken_content_file))

problem_df.to_pickle(os.path.join(SPOKEN_CONTENT_OUTPUT, "problems.pkl"))
