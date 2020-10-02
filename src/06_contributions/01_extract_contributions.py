import pandas as pd
import numpy as np
import sys
import os
import regex

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))
from src.helper_functions.extract_contributions import extract
import path_definitions

# input directory ______________________________________________________________
SPOKEN_CONTENT_INPUT = path_definitions.SPOKEN_CONTENT_STAGE_04

# output directory _____________________________________________________________
SPOKEN_CONTENT_OUTPUT = path_definitions.SPOKEN_CONTENT_STAGE_05
CONTRIBUTIONS_OUTPUT = path_definitions.CONTRIBUTIONS_STAGE_01
CONTRIBUTIONS_MISCELLANEOUS_STAGE_01 = path_definitions.CONTRIBUTIONS_MISCELLANEOUS_STAGE_01
TEXT_POSITION_X_TEXT = path_definitions.TEXT_POSITION_X_TEXT


class Incrementor(object):
    """Incrementor class for iterative regex deletion"""

    def __init__(self):
        self.count = -1

    def increment(self, matchObject):
        self.count += 1
        return "{->" + str(self.count) + "}"


speech_id = 0

if not os.path.exists(TEXT_POSITION_X_TEXT):
    os.makedirs(TEXT_POSITION_X_TEXT)

text_position_x_text = pd.DataFrame({"text_position": [], "deleted_text": [], "speech_id": []})

# Go through all wp folders
for wp_folder in sorted(os.listdir(SPOKEN_CONTENT_INPUT)):
    if "wp" not in wp_folder:
        continue
    if len(sys.argv) > 1:
        if str(int(regex.sub("wp_", "", wp_folder))) not in sys.argv:
            continue
    wp_folder_path = os.path.join(SPOKEN_CONTENT_INPUT, wp_folder)

    print(wp_folder)

    if not os.path.exists(os.path.join(SPOKEN_CONTENT_OUTPUT, wp_folder)):
        os.makedirs(os.path.join(SPOKEN_CONTENT_OUTPUT, wp_folder))

    if not os.path.exists(os.path.join(CONTRIBUTIONS_OUTPUT, wp_folder)):
        os.makedirs(os.path.join(CONTRIBUTIONS_OUTPUT, wp_folder))

    if not os.path.exists(os.path.join(CONTRIBUTIONS_MISCELLANEOUS_STAGE_01, wp_folder)):
        os.makedirs(os.path.join(CONTRIBUTIONS_MISCELLANEOUS_STAGE_01, wp_folder))

    # iterate over every spoken_content file
    for spoken_content_file in sorted(os.listdir(wp_folder_path)):
        print(spoken_content_file)

        # checks if the file is a csv file
        if ".pkl" not in spoken_content_file:
            continue
        filepath = os.path.join(wp_folder_path, spoken_content_file)

        # read the spoken content csv
        spoken_content = pd.read_pickle(filepath)

        frame = {
            "id": [],
            "type": [],
            "name": [],
            "party": [],
            "location_information": [],
            "content": [],
            "text_position": [],
        }
        miscellaneous_frame = {
            "id": [],
            "type": [],
            "name": [],
            "party": [],
            "location_information": [],
            "content": [],
            "text_position": [],
        }
        contributions = pd.DataFrame(frame)
        miscellaneous = pd.DataFrame(miscellaneous_frame)

        spoken_content.insert(0, "speech_id", 0)

        # iterate over every speech
        for counter, speech in zip(spoken_content.index, spoken_content.speech_content):
            # call the extract method which returns the cleaned speech and a
            # dataframe with all contributions in that particular speech

            (
                contribution,
                miscellaneous_frame,
                speech_text,
                text_position_x_text_frame,
                _,
            ) = extract(speech, int(spoken_content_file.replace(".pkl", "")), speech_id,)

            spoken_content.at[counter, "speech_content"] = speech_text

            spoken_content.at[counter, "speech_id"] = speech_id
            speech_id += 1

            # combine the dataframes
            contributions = pd.concat([contributions, contribution], sort=False)
            miscellaneous = pd.concat([miscellaneous, miscellaneous_frame], sort=False)
            text_position_x_text = pd.concat(
                [text_position_x_text, text_position_x_text_frame], sort=False
            )

        # save the contributions to pickle
        contributions.to_pickle(os.path.join(CONTRIBUTIONS_OUTPUT, wp_folder, spoken_content_file))

        # save the miscellaneous contributions to pickle
        miscellaneous.to_pickle(
            os.path.join(CONTRIBUTIONS_MISCELLANEOUS_STAGE_01, wp_folder, spoken_content_file)
        )

        # save the spoken_conten to pickle
        spoken_content.to_pickle(
            os.path.join(SPOKEN_CONTENT_OUTPUT, wp_folder, spoken_content_file)
        )

text_position_x_text.to_pickle(os.path.join(TEXT_POSITION_X_TEXT, "text_position_x_text.pkl"))
