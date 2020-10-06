import xml.etree.ElementTree as et
import pandas as pd
import os
import regex
import time
import datetime
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))
import path_definitions

# input directory ______________________________________________________________
RAW_XML = path_definitions.RAW_XML
SPOKEN_CONTENT_INPUT = path_definitions.SPOKEN_CONTENT_STAGE_05
SPOKEN_CONTENT_INPUT_2 = path_definitions.WP_19_STAGE_03
CONTRIBUTIONS_INPUT = path_definitions.CONTRIBUTIONS_STAGE_03
MISCELLANEOUS_INPUT = path_definitions.MISCELLANEOUS_STAGE_01

# output directory _____________________________________________________________
SPOKEN_CONTENT_OUTPUT = path_definitions.FINAL
CONTRIBUTIONS_OUTPUT = path_definitions.FINAL
MISCELLANEOUS_OUTPUT = path_definitions.FINAL

if not os.path.exists(SPOKEN_CONTENT_OUTPUT):
    os.makedirs(SPOKEN_CONTENT_OUTPUT)

if not os.path.exists(CONTRIBUTIONS_OUTPUT):
    os.makedirs(CONTRIBUTIONS_OUTPUT)

if not os.path.exists(MISCELLANEOUS_OUTPUT):
    os.makedirs(MISCELLANEOUS_OUTPUT)

# spoken content _______________________________________________________________

# Placeholder for concating speeches DF of all sittings.
spoken_content_01_18 = pd.DataFrame()


# Walk over all legislature periods. ___________________________________________
for wp_folder in sorted(os.listdir(SPOKEN_CONTENT_INPUT)):
    wp_folder_path = os.path.join(SPOKEN_CONTENT_INPUT, wp_folder)

    if not os.path.isdir(wp_folder_path):
        continue
    elif wp_folder == ".DS_Store":
        continue

    for spoken_content_file in sorted(os.listdir(wp_folder_path)):
        if ".pkl" not in spoken_content_file:
            continue

        print(spoken_content_file)

        spoken_content = pd.read_pickle(os.path.join(wp_folder_path, spoken_content_file))

        spoken_content_01_18 = pd.concat([spoken_content_01_18, spoken_content], sort=False)


spoken_content_01_18 = spoken_content_01_18.loc[
    :,
    [
        "speech_id",
        "sitting",
        "first_name",
        "last_name",
        "faction_id",
        "position_short",
        "position_long",
        "politician_id",
        "speech_content",
    ],
]

spoken_content_01_18 = spoken_content_01_18.rename(
    columns={"speech_id": "id", "politician_id": "people_id"}
)


spoken_content_01_18.first_name = spoken_content_01_18.first_name.apply(" ".join)

spoken_content_01_18.id = list(range(len(spoken_content_01_18)))

spoken_content_01_18.sitting = spoken_content_01_18.sitting.str.replace(r"\.pkl", "")


meta_data = {}

# Open every xml plenar file in every legislature period.
for wp_folder in sorted(os.listdir(RAW_XML)):
    wp_folder_path = os.path.join(RAW_XML, wp_folder)
    # Skip e.g. the .DS_Store file.  ___________________________________________
    if not os.path.isdir(wp_folder_path):
        continue

    if len(sys.argv) > 1:
        if str(int(regex.sub("wp_", "", wp_folder))) not in sys.argv:
            continue

    print(wp_folder)
    for xml_plenar_file in sorted(os.listdir(wp_folder_path)):
        if ".xml" in xml_plenar_file:
            print(xml_plenar_file)
            path = os.path.join(wp_folder_path, xml_plenar_file)
            tree = et.parse(path)
            # Get the document number, the date of the sitting and the content.
            # meta_data["document_number"].append(tree.find("NR").text)
            # meta_data["date"].append(tree.find("DATUM").text)
            # document_number = tree.find("NR").text
            date = time.mktime(
                datetime.datetime.strptime(tree.find("DATUM").text, "%d.%m.%Y").timetuple()
            )
            document_number = xml_plenar_file.replace(".xml", "")
            document_number = int(document_number)
            meta_data[document_number] = date

spoken_content_01_18.insert(1, "wp", -1)
spoken_content_01_18["wp"] = spoken_content_01_18.sitting.apply(lambda x: int(str(x)[:2]))
spoken_content_01_18.sitting = spoken_content_01_18.sitting.astype("int32")
spoken_content_01_18["date"] = spoken_content_01_18.sitting.apply(meta_data.get)
spoken_content_01_18["sitting"] = spoken_content_01_18.sitting.apply(lambda x: int(str(x)[-3:]))
spoken_content_01_18.sitting = spoken_content_01_18.sitting.astype("int32")
spoken_content_01_18.wp = spoken_content_01_18.wp.astype("int32")

spoken_content_19 = pd.read_pickle(
    os.path.join(SPOKEN_CONTENT_INPUT_2, "spoken_content", "spoken_content.pkl")
)

spoken_content_19 = spoken_content_19.loc[
    :,
    [
        "id",
        "sitting",
        "first_name",
        "last_name",
        "faction_id",
        "position_short",
        "position_long",
        "people_id",
        "speech_content",
        "date",
    ],
]


spoken_content_19.insert(1, "wp", -1)
spoken_content_19["wp"] = spoken_content_19.sitting.apply(lambda x: int(str(x)[:2]))
spoken_content_19["sitting"] = spoken_content_19.sitting.apply(lambda x: int(str(x)[-3:]))
spoken_content_19.wp = spoken_content_19.wp.astype("int32")
spoken_content_19.sitting = spoken_content_19.sitting.astype("int32")

spoken_content = pd.concat([spoken_content_01_18, spoken_content_19])


# save data. ___________________________________________________________________

spoken_content.to_pickle(os.path.join(SPOKEN_CONTENT_OUTPUT, "spoken_content.pkl"))

# Placeholder for concating contributions DF of all sittings.
concat_contributions_df = pd.DataFrame()

# Walk over all legislature periods. ___________________________________________
for wp_folder in sorted(os.listdir(CONTRIBUTIONS_INPUT)):
    wp_folder_path = os.path.join(CONTRIBUTIONS_INPUT, wp_folder)

    if not os.path.isdir(wp_folder_path):
        continue
    elif wp_folder == ".DS_Store":
        continue

    for contributions_file in sorted(os.listdir(wp_folder_path)):
        if ".pkl" not in contributions_file:
            continue

        print(contributions_file)

        contributions = pd.read_pickle(os.path.join(wp_folder_path, contributions_file))

        concat_contributions_df = pd.concat([concat_contributions_df, contributions], sort=False)


concat_contributions_df = concat_contributions_df.loc[
    :,
    [
        "type",
        "first_name",
        "last_name",
        "faction_id",
        "id",
        "text_position",
        "politician_id",
        "content",
    ],
]

concat_contributions_df = concat_contributions_df.rename(
    columns={"id": "speech_id", "politician_id": "people_id"}
)

concat_contributions_df.insert(0, "id", list(range(len(concat_contributions_df))))

concat_contributions_df.first_name = concat_contributions_df.first_name.apply(" ".join)

concat_contributions_df = concat_contributions_df.astype(
    {
        "id": "int64",
        "type": "object",
        "first_name": "object",
        "last_name": "object",
        "faction_id": "int32",
        "speech_id": "int32",
        "text_position": "int32",
        "people_id": "int32",
        "content": "object",
    }
)

concat_contributions_df.to_pickle(os.path.join(CONTRIBUTIONS_OUTPUT, "contributions.pkl"))

# Placeholder for concating contributions DF of all sittings.
concat_miscellaneous_df = pd.DataFrame()

# Walk over all legislature periods. ___________________________________________
for wp_folder in sorted(os.listdir(MISCELLANEOUS_INPUT)):
    wp_folder_path = os.path.join(MISCELLANEOUS_INPUT, wp_folder)

    if not os.path.isdir(wp_folder_path):
        continue
    elif wp_folder == ".DS_Store":
        continue

    for contributions_file in sorted(os.listdir(wp_folder_path)):
        if ".pkl" not in contributions_file:
            continue

        print(contributions_file)

        contributions = pd.read_pickle(os.path.join(wp_folder_path, contributions_file))

        concat_miscellaneous_df = pd.concat([concat_miscellaneous_df, contributions])


concat_miscellaneous_df = concat_miscellaneous_df.loc[
    :, ["id", "text_position", "content"],
]

concat_miscellaneous_df = concat_miscellaneous_df.rename(columns={"id": "speech_id"})

concat_miscellaneous_df.insert(0, "id", list(range(len(concat_miscellaneous_df))))

concat_miscellaneous_df = concat_miscellaneous_df.astype(
    {"id": "int64", "speech_id": "int32", "text_position": "int32", "content": "object",}
)

concat_miscellaneous_df.to_pickle(os.path.join(MISCELLANEOUS_OUTPUT, "miscellaneous.pkl"))

