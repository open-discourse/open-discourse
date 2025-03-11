import pandas as pd
import regex
from tqdm import tqdm

from open_discourse.definitions import path
from open_discourse.helper.match_names import (
    insert_politician_id_into_speech_content,
)

# input directory
SPEECH_CONTENT_INPUT = path.SPEECH_CONTENT_STAGE_02
DATA_FINAL = path.DATA_FINAL

# output directory
SPEECH_CONTENT_OUTPUT = path.SPEECH_CONTENT_STAGE_03
SPEECH_CONTENT_OUTPUT.mkdir(parents=True, exist_ok=True)

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
        "profession",
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

politicians["profession"] = politicians["profession"].str.lower()

# iterate over all electoral_term_folders __________________________________________________
for folder_path in sorted(SPEECH_CONTENT_INPUT.iterdir()):
    if not folder_path.is_dir():
        continue

    term_number = regex.search(r"(?<=electoral_term_pp)\d{2}", folder_path.stem)
    if term_number is None:
        continue
    term_number = int(term_number.group(0))

    save_path = SPEECH_CONTENT_OUTPUT / folder_path.stem
    save_path.mkdir(parents=True, exist_ok=True)

    # Only select politicians of the election period.
    politicians_electoral_term = politicians.loc[politicians["electoral_term"] == term_number]
    mgs_electoral_term = politicians_electoral_term.loc[
        politicians_electoral_term["institution_type"] == "Regierungsmitglied"
    ]

    # iterate over every speech_content file
    for speech_content_file in tqdm(
        folder_path.glob("*.pkl"),
        desc=f"Match speaker names (term {term_number:>2})...",
    ):
        # read the spoken content pickle file
        speech_content = pd.read_pickle(speech_content_file)

        speech_content_matched, _ = insert_politician_id_into_speech_content(
            speech_content, politicians_electoral_term, mgs_electoral_term, politicians
        )

        speech_content_matched.to_pickle(save_path / speech_content_file.name)

assert len(list(SPEECH_CONTENT_INPUT.glob("*_pp*"))) == len(list(SPEECH_CONTENT_OUTPUT.glob("*_pp*")))
print("Script 05_03 done.")
