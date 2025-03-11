import sys

import pandas as pd
import regex
from tqdm import tqdm

from open_discourse.definitions import path
from open_discourse.helper.match_names import (
    insert_politician_id_into_contributions_extended,
)

# input directory
CONTRIBUTIONS_EXTENDED_INPUT = path.CONTRIBUTIONS_EXTENDED_STAGE_02
DATA_FINAL = path.DATA_FINAL

# output directory
CONTRIBUTIONS_EXTENDED_OUTPUT = path.CONTRIBUTIONS_EXTENDED_STAGE_03

# MDBS
politicians = pd.read_csv(DATA_FINAL / "politicians.csv")
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
politicians["constituency"] = politicians["constituency"].fillna("")

politicians["first_name"] = politicians["first_name"].str.lower()
politicians["last_name"] = politicians["last_name"].str.lower()
politicians["constituency"] = politicians["constituency"].str.lower()

politicians["first_name"] = politicians["first_name"].str.replace("ß", "ss", regex=False)
politicians["last_name"] = politicians["last_name"].str.replace("ß", "ss", regex=False)

politicians["first_name"] = politicians["first_name"].apply(str.split)

# iterate over all electoral_term_folders __________________________________________________
for folder_path in sorted(CONTRIBUTIONS_EXTENDED_INPUT.iterdir()):
    if not folder_path.is_dir():
        continue

    term_number = regex.search(r"(?<=electoral_term_pp)\d{2}", folder_path.stem)
    if term_number is None:
        continue
    term_number = int(term_number.group(0))

    if len(sys.argv) > 1:
        if str(term_number) not in sys.argv:
            continue

    save_path = CONTRIBUTIONS_EXTENDED_OUTPUT / folder_path.stem
    save_path.mkdir(parents=True, exist_ok=True)

    # Only select politicians of the election period.
    politicians_electoral_term = politicians.loc[politicians["electoral_term"] == term_number]
    gov_members_electoral_term = politicians_electoral_term.loc[
        politicians_electoral_term["institution_type"] == "Regierungsmitglied"
    ]

    working = []
    # iterate over every contributions_extended file
    for contrib_ext_file_path in tqdm(
        folder_path.glob("*.pkl"),
        desc=f"Match contributions (term {term_number:>2})...",
    ):
        # read the contributions_extended pickle file
        contributions_extended = pd.read_pickle(contrib_ext_file_path)

        (
            contributions_extended_matched,
            problems,
        ) = insert_politician_id_into_contributions_extended(
            contributions_extended,
            politicians_electoral_term,
            gov_members_electoral_term,
        )

        contributions_extended.to_pickle(save_path / contrib_ext_file_path.name)

assert len(list(CONTRIBUTIONS_EXTENDED_INPUT.glob("*_pp*"))) == len(list(CONTRIBUTIONS_EXTENDED_OUTPUT.glob("*_pp*")))
print("Script 07_03 done.")
