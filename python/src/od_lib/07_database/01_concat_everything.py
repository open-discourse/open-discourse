import od_lib.definitions.path_definitions as path_definitions
import xml.etree.ElementTree as et
import pandas as pd
import os
import regex
import time
import datetime
import sys

# input directory
RAW_XML = path_definitions.RAW_XML
SPEECH_CONTENT_INPUT = path_definitions.SPEECH_CONTENT_STAGE_04
SPEECH_CONTENT_INPUT_2 = path_definitions.ELECTORAL_TERM_19_STAGE_03
CONTRIBUTIONS_INPUT = path_definitions.CONTRIBUTIONS_STAGE_03

# output directory
SPEECH_CONTENT_OUTPUT = path_definitions.FINAL
CONTRIBUTIONS_OUTPUT = path_definitions.FINAL

if not os.path.exists(SPEECH_CONTENT_OUTPUT):
    os.makedirs(SPEECH_CONTENT_OUTPUT)

if not os.path.exists(CONTRIBUTIONS_OUTPUT):
    os.makedirs(CONTRIBUTIONS_OUTPUT)

# spoken content

# Placeholder for concating speeches DF of all sessions.
speech_content_01_18 = pd.DataFrame()


# Walk over all legislature periods.
for electoral_term_folder in sorted(os.listdir(SPEECH_CONTENT_INPUT)):
    electoral_term_folder_path = os.path.join(
        SPEECH_CONTENT_INPUT, electoral_term_folder
    )

    if not os.path.isdir(electoral_term_folder_path):
        continue
    elif electoral_term_folder == ".DS_Store":
        continue

    for speech_content_file in sorted(os.listdir(electoral_term_folder_path)):
        if ".pkl" not in speech_content_file:
            continue

        print(speech_content_file)

        speech_content = pd.read_pickle(
            os.path.join(electoral_term_folder_path, speech_content_file)
        )

        speech_content_01_18 = pd.concat(
            [speech_content_01_18, speech_content], sort=False
        )


speech_content_01_18 = speech_content_01_18.loc[
    :,
    [
        "speech_id",
        "session",
        "first_name",
        "last_name",
        "faction_id",
        "position_short",
        "position_long",
        "politician_id",
        "speech_content",
    ],
]

speech_content_01_18 = speech_content_01_18.rename(columns={"speech_id": "id"})


speech_content_01_18["first_name"] = speech_content_01_18["first_name"].apply(" ".join)

speech_content_01_18["id"] = list(range(len(speech_content_01_18)))

speech_content_01_18["session"] = speech_content_01_18["session"].str.replace(
    r"\.pkl", ""
)


meta_data = {}

# Open every xml plenar file in every legislature period.
for electoral_term_folder in sorted(os.listdir(RAW_XML)):
    electoral_term_folder_path = os.path.join(RAW_XML, electoral_term_folder)
    # Skip e.g. the .DS_Store file.
    if not os.path.isdir(electoral_term_folder_path):
        continue

    if len(sys.argv) > 1:
        if (
            str(int(regex.sub("electoral_term_", "", electoral_term_folder)))
            not in sys.argv
        ):
            continue

    print(electoral_term_folder)
    for xml_plenar_file in sorted(os.listdir(electoral_term_folder_path)):
        if ".xml" in xml_plenar_file:
            print(xml_plenar_file)
            path = os.path.join(electoral_term_folder_path, xml_plenar_file)
            tree = et.parse(path)
            # Get the document number, the date of the session and the content.
            # meta_data["document_number"].append(tree.find("NR").text)
            # meta_data["date"].append(tree.find("DATUM").text)
            # document_number = tree.find("NR").text
            date = time.mktime(
                datetime.datetime.strptime(
                    tree.find("DATUM").text, "%d.%m.%Y"
                ).timetuple()
            )
            document_number = xml_plenar_file.replace(".xml", "")
            document_number = int(document_number)
            meta_data[document_number] = date

speech_content_01_18.insert(1, "electoral_term", -1)
speech_content_01_18.insert(4, "document_url", "")
speech_content_01_18["electoral_term"] = speech_content_01_18["session"].apply(
    lambda x: str(x)[:2]
)
speech_content_01_18["session"] = speech_content_01_18["session"].astype("int32")
speech_content_01_18["date"] = speech_content_01_18["session"].apply(meta_data.get)
speech_content_01_18["session"] = speech_content_01_18["session"].apply(
    lambda x: str(x)[-3:]
)

speech_content_01_18["document_url"] = speech_content_01_18.apply(
    lambda row: "https://dip21.bundestag.de/dip21/btp/{0}/{0}{1}.pdf".format(
        row["electoral_term"], row["session"]
    ),
    axis=1,
)

speech_content_01_18["session"] = speech_content_01_18["session"].astype("int32")
speech_content_01_18["electoral_term"] = speech_content_01_18["electoral_term"].astype(
    "int32"
)

speech_content_19 = pd.read_pickle(
    os.path.join(SPEECH_CONTENT_INPUT_2, "speech_content", "speech_content.pkl")
)

speech_content_19 = speech_content_19.loc[
    :,
    [
        "id",
        "session",
        "first_name",
        "last_name",
        "faction_id",
        "position_short",
        "position_long",
        "politician_id",
        "speech_content",
        "date",
    ],
]


speech_content_19.insert(1, "electoral_term", -1)
speech_content.insert(2, "document_url", "")

speech_content_19["electoral_term"] = speech_content_19["session"].apply(
    lambda x: str(x)[:2]
)
speech_content_19["session"] = speech_content_19["session"].apply(lambda x: str(x)[-3:])

speech_content_19["document_url"] = speech_content_19.apply(
    lambda row: "https://dip21.bundestag.de/dip21/btp/{0}/{0}{1}.pdf".format(
        row["electoral_term"], row["session"]
    ),
    axis=1,
)

speech_content_19["electoral_term"] = speech_content_19["electoral_term"].astype(
    "int32"
)
speech_content_19["session"] = speech_content_19["session"].astype("int32")

speech_content = pd.concat([speech_content_01_18, speech_content_19])

# save data.

speech_content.to_pickle(os.path.join(SPEECH_CONTENT_OUTPUT, "speech_content.pkl"))

# Placeholder for concating contributions DF of all sessions.
concat_contributions_df = pd.DataFrame()

# Walk over all legislature periods.
for electoral_term_folder in sorted(os.listdir(CONTRIBUTIONS_INPUT)):
    electoral_term_folder_path = os.path.join(
        CONTRIBUTIONS_INPUT, electoral_term_folder
    )

    if not os.path.isdir(electoral_term_folder_path):
        continue
    elif electoral_term_folder == ".DS_Store":
        continue

    for contributions_file in sorted(os.listdir(electoral_term_folder_path)):
        if ".pkl" not in contributions_file:
            continue

        print(contributions_file)

        contributions = pd.read_pickle(
            os.path.join(electoral_term_folder_path, contributions_file)
        )

        concat_contributions_df = pd.concat(
            [concat_contributions_df, contributions], sort=False
        )


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
    columns={"id": "speech_id", "politician_id": "politician_id"}
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
        "politician_id": "int32",
        "content": "object",
    }
)

concat_contributions_df.to_pickle(
    os.path.join(CONTRIBUTIONS_OUTPUT, "contributions.pkl")
)
