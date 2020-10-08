from od_lib.helper_functions.extract_contributions import extract
import od_lib.definitions.path_definitions as path_definitions
import pandas as pd
import sys
import os
import regex

# input directory
SPEECH_CONTENT_INPUT = path_definitions.SPEECH_CONTENT_STAGE_03

# output directory
SPEECH_CONTENT_OUTPUT = path_definitions.SPEECH_CONTENT_STAGE_04
CONTRIBUTIONS_OUTPUT = path_definitions.CONTRIBUTIONS_STAGE_01
CONTRIBUTIONS_MISCELLANEOUS_STAGE_01 = (
    path_definitions.CONTRIBUTIONS_MISCELLANEOUS_STAGE_01
)
CONTRIBUTIONS_LOOKUP = path_definitions.CONTRIBUTIONS_LOOKUP


class Incrementor(object):
    """Incrementor class for iterative regex deletion"""

    def __init__(self):
        self.count = -1

    def increment(self, matchObject):
        self.count += 1
        return "{->" + str(self.count) + "}"


speech_id = 0

if not os.path.exists(CONTRIBUTIONS_LOOKUP):
    os.makedirs(CONTRIBUTIONS_LOOKUP)

contributions_lookup = pd.DataFrame(
    {"text_position": [], "deleted_text": [], "speech_id": []}
)

# Go through all electoral_term folders
for electoral_term_folder in sorted(os.listdir(SPEECH_CONTENT_INPUT)):
    if "electoral_term" not in electoral_term_folder:
        continue
    if len(sys.argv) > 1:
        if (
            str(int(regex.sub("electoral_term_", "", electoral_term_folder)))
            not in sys.argv
        ):
            continue
    electoral_term_folder_path = os.path.join(
        SPEECH_CONTENT_INPUT, electoral_term_folder
    )

    print(electoral_term_folder)

    if not os.path.exists(os.path.join(SPEECH_CONTENT_OUTPUT, electoral_term_folder)):
        os.makedirs(os.path.join(SPEECH_CONTENT_OUTPUT, electoral_term_folder))

    if not os.path.exists(os.path.join(CONTRIBUTIONS_OUTPUT, electoral_term_folder)):
        os.makedirs(os.path.join(CONTRIBUTIONS_OUTPUT, electoral_term_folder))

    if not os.path.exists(
        os.path.join(CONTRIBUTIONS_MISCELLANEOUS_STAGE_01, electoral_term_folder)
    ):
        os.makedirs(
            os.path.join(CONTRIBUTIONS_MISCELLANEOUS_STAGE_01, electoral_term_folder)
        )

    # iterate over every speech_content file
    for speech_content_file in sorted(os.listdir(electoral_term_folder_path)):
        print(speech_content_file)

        # checks if the file is a csv file
        if ".pkl" not in speech_content_file:
            continue
        filepath = os.path.join(electoral_term_folder_path, speech_content_file)

        # read the spoken content csv
        speech_content = pd.read_pickle(filepath)

        frame = {
            "id": [],
            "type": [],
            "name_raw": [],
            "faction": [],
            "constituency": [],
            "content": [],
            "text_position": [],
        }

        miscellaneous_frame = {
            "id": [],
            "type": [],
            "name_raw": [],
            "faction": [],
            "constituency": [],
            "content": [],
            "text_position": [],
        }

        contributions = pd.DataFrame(frame)
        miscellaneous = pd.DataFrame(miscellaneous_frame)

        speech_content.insert(0, "speech_id", 0)

        # iterate over every speech
        for counter, speech in zip(speech_content.index, speech_content.speech_content):
            # call the extract method which returns the cleaned speech and a
            # dataframe with all contributions in that particular speech

            (
                contribution,
                miscellaneous_frame,
                speech_text,
                contributions_lookup_frame,
                _,
            ) = extract(
                speech, int(speech_content_file.replace(".pkl", "")), speech_id,
            )

            speech_content.at[counter, "speech_content"] = speech_text

            speech_content.at[counter, "speech_id"] = speech_id
            speech_id += 1

            # combine the dataframes
            contributions = pd.concat([contributions, contribution], sort=False)
            miscellaneous = pd.concat([miscellaneous, miscellaneous_frame], sort=False)
            contributions_lookup = pd.concat(
                [contributions_lookup, contributions_lookup_frame], sort=False
            )

        # save the contributions to pickle
        contributions.to_pickle(
            os.path.join(
                CONTRIBUTIONS_OUTPUT, electoral_term_folder, speech_content_file
            )
        )

        # save the miscellaneous contributions to pickle
        miscellaneous.to_pickle(
            os.path.join(
                CONTRIBUTIONS_MISCELLANEOUS_STAGE_01,
                electoral_term_folder,
                speech_content_file,
            )
        )

        # save the spoken_conten to pickle
        speech_content.to_pickle(
            os.path.join(
                SPEECH_CONTENT_OUTPUT, electoral_term_folder, speech_content_file
            )
        )

contributions_lookup.to_pickle(
    os.path.join(CONTRIBUTIONS_LOOKUP, "contributions_lookup.pkl")
)
