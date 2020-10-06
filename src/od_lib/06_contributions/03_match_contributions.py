from od_lib.helper_functions.match_names import insert_people_id_into_contributions
import od_lib.definitions.path_definitions as path_definitions
import pandas as pd
import regex
import os
import sys


# from src.helper_functions.matching_functions import levenshtein_ratio_and_distance

DEBUG_MODE = False

# input directory ______________________________________________________________
CONTRIBUTIONS_INPUT = path_definitions.CONTRIBUTIONS_STAGE_02
DATA_FINAL = path_definitions.DATA_FINAL

# output directory _____________________________________________________________
CONTRIBUTIONS_OUTPUT = path_definitions.CONTRIBUTIONS_STAGE_03

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

problem_df = pd.DataFrame()

# iterate over all wp_folders __________________________________________________
for wp_folder in sorted(os.listdir(CONTRIBUTIONS_INPUT)):
    working = []
    if "wp" not in wp_folder:
        continue
    if len(sys.argv) > 1:
        if str(int(regex.sub("wp_", "", wp_folder))) not in sys.argv:
            continue
    wp_folder_path = os.path.join(CONTRIBUTIONS_INPUT, wp_folder)

    print(wp_folder)

    save_path = os.path.join(CONTRIBUTIONS_OUTPUT, wp_folder)
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    wp = int(regex.sub("wp_0?", "", wp_folder))

    # Only select politicians of the election period.
    people_wp = people.loc[people.wp_period == wp]
    gov_members_wp = people_wp.loc[people_wp.institution_type == "Regierungsmitglied"]

    # iterate over every contributions file
    for contributions_file in sorted(os.listdir(wp_folder_path)):
        print(contributions_file)

        # check if sitting file is a pickle file
        if ".pkl" not in contributions_file:
            continue
        filepath = os.path.join(wp_folder_path, contributions_file)

        # read the contributions pickle file
        contributions = pd.read_pickle(filepath)

        contributions_matched, problems = insert_people_id_into_contributions(
            contributions, people_wp, gov_members_wp
        )

        problem_df = problem_df.append(problems, ignore_index=True, sort=True)

        contributions.to_pickle(os.path.join(save_path, contributions_file))
