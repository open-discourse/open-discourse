import sys

import pandas as pd
import regex

import open_discourse.definitions.path_definitions as path_definitions
from open_discourse.helper_functions.extract_contributions import extract
from open_discourse.helper_functions.progressbar import progressbar

# input directory
SPEECH_CONTENT_INPUT = path_definitions.SPEECH_CONTENT_STAGE_03

# output directory
SPEECH_CONTENT_OUTPUT = path_definitions.SPEECH_CONTENT_STAGE_04
CONTRIBUTIONS_EXTENDED_OUTPUT = path_definitions.CONTRIBUTIONS_EXTENDED_STAGE_01
CONTRIBUTIONS_SIMPLIFIED = path_definitions.CONTRIBUTIONS_SIMPLIFIED
CONTRIBUTIONS_SIMPLIFIED.mkdir(parents=True, exist_ok=True)

speech_id = 0

simplified_list = []

# Go through all electoral_term folders
for folder_path in sorted(SPEECH_CONTENT_INPUT.iterdir()):
    if not folder_path.is_dir():
        continue

    term_number = regex.search(r"(?<=electoral_term_)\d{2}", folder_path.stem)
    if term_number is None:
        continue
    term_number = int(term_number.group(0))

    if len(sys.argv) > 1:
        if str(term_number) not in sys.argv:
            continue

    speech_output = SPEECH_CONTENT_OUTPUT / folder_path.stem
    extended_output = CONTRIBUTIONS_EXTENDED_OUTPUT / folder_path.stem

    speech_output.mkdir(parents=True, exist_ok=True)
    extended_output.mkdir(parents=True, exist_ok=True)

    # iterate over every speech_content file
    for speech_content_file_path in progressbar(
        folder_path.glob("*.pkl"),
        f"Extract contributions (term {term_number:>2})...",
    ):
        # read the spoken content csv
        speech_content = pd.read_pickle(speech_content_file_path)

        frame = {
            "id": [],
            "type": [],
            "name_raw": [],
            "faction": [],
            "constituency": [],
            "content": [],
            "text_position": [],
        }

        speech_content.insert(0, "speech_id", 0)

        extended_list = []
        # iterate over every speech
        for counter, speech in zip(
            speech_content.index, speech_content["speech_content"]
        ):
            # call the extract method which returns the cleaned speech and a
            # dataframe with all contributions in that particular speech

            (
                contribution_extended,
                speech_text,
                contribution_simple,
                _,
            ) = extract(
                speech,
                int(speech_content_file_path.stem),
                speech_id,
            )
            simplified_list.append(contribution_simple)
            extended_list.append(contribution_extended)
            speech_content.at[counter, "speech_content"] = speech_text
            speech_content.at[counter, "speech_id"] = speech_id
            speech_id += 1

        contributions_extended = pd.concat(extended_list, sort=False)
        # save the contributions_extended to pickle
        contributions_extended.to_pickle(
            extended_output / speech_content_file_path.name
        )
        # save the spoken_conten to pickle
        speech_content.to_pickle(speech_output / speech_content_file_path.name)

contributions_simplified = pd.concat(simplified_list, sort=False)
contributions_simplified.to_pickle(
    CONTRIBUTIONS_SIMPLIFIED / "contributions_simplified.pkl"
)
