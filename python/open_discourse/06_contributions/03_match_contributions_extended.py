import os
import sys

import pandas as pd
import regex

import open_discourse.definitions.path_definitions as path_definitions
from open_discourse.helper_functions.match_names import (
    insert_politician_id_into_contributions_extended,
)

# input directory
CONTRIBUTIONS_EXTENDED_INPUT = path_definitions.CONTRIBUTIONS_EXTENDED_STAGE_02
DATA_FINAL = path_definitions.DATA_FINAL

# output directory
CONTRIBUTIONS_EXTENDED_OUTPUT = path_definitions.CONTRIBUTIONS_EXTENDED_STAGE_03

# MDBS
politicians = pd.read_csv(os.path.join(DATA_FINAL, "politicians.csv"))
politicians = politicians.loc[
    :,
    [
        "ui",
        "electoral_term",
        "faction_id",
        "first_name",
        "last_name",
        "gender",
        "constituency",
        "institution_type",
    ],
].copy()

politicians = politicians.astype(dtype={"ui": "int64"})

# Some cleaning to make matching easier.
politicians.constituency = politicians.constituency.fillna("")

politicians.first_name = politicians.first_name.str.lower()
politicians.last_name = politicians.last_name.str.lower()
politicians.constituency = politicians.constituency.str.lower()

politicians.first_name = politicians.first_name.str.replace("ß", "ss", regex=False)
politicians.last_name = politicians.last_name.str.replace("ß", "ss", regex=False)

politicians.first_name = politicians.first_name.apply(str.split)

problem_df = pd.DataFrame()

# iterate over all electoral_term_folders __________________________________________________
for electoral_term_folder in sorted(os.listdir(CONTRIBUTIONS_EXTENDED_INPUT)):
    working = []
    if "electoral_term" not in electoral_term_folder:
        continue
    if len(sys.argv) > 1:
        if (
            str(int(regex.sub("electoral_term_", "", electoral_term_folder)))
            not in sys.argv
        ):
            continue
    electoral_term_folder_path = os.path.join(
        CONTRIBUTIONS_EXTENDED_INPUT, electoral_term_folder
    )

    print(electoral_term_folder)

    save_path = os.path.join(CONTRIBUTIONS_EXTENDED_OUTPUT, electoral_term_folder)
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    electoral_term = int(regex.sub("electoral_term_0?", "", electoral_term_folder))

    # Only select politicians of the election period.
    politicians_electoral_term = politicians.loc[
        politicians.electoral_term == electoral_term
    ]
    gov_members_electoral_term = politicians_electoral_term.loc[
        politicians_electoral_term.institution_type == "Regierungsmitglied"
    ]

    # iterate over every contributions_extended file
    for contributions_extended_file in sorted(os.listdir(electoral_term_folder_path)):
        print(contributions_extended_file)

        # check if session file is a pickle file
        if ".pkl" not in contributions_extended_file:
            continue
        filepath = os.path.join(electoral_term_folder_path, contributions_extended_file)

        # read the contributions_extended pickle file
        contributions_extended = pd.read_pickle(filepath)

        (
            contributions_extended_matched,
            problems,
        ) = insert_politician_id_into_contributions_extended(
            contributions_extended,
            politicians_electoral_term,
            gov_members_electoral_term,
        )

        problem_df = problem_df.append(problems, ignore_index=True, sort=True)

        contributions_extended.to_pickle(
            os.path.join(save_path, contributions_extended_file)
        )
