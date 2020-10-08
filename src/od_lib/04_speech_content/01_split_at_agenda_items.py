import od_lib.definitions.path_definitions as path_definitions
import pandas as pd
import os
import regex
import sys

# input directory ______________________________________________________________
RAW_TXT = path_definitions.RAW_TXT

# output directory _____________________________________________________________
SPEECH_CONTENT_STAGE_01 = path_definitions.SPEECH_CONTENT_STAGE_01

# Walk over every period _______________________________________________________
for electoral_term_folder in sorted(os.listdir(RAW_TXT)):
    electoral_term_folder_path = os.path.join(RAW_TXT, electoral_term_folder)
    save_path = os.path.join(SPEECH_CONTENT_STAGE_01, electoral_term_folder)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    if not os.path.isdir(electoral_term_folder_path):
        continue
    elif electoral_term_folder == ".DS_Store":
        continue
    if len(sys.argv) > 1:
        if (
            str(int(regex.sub("electoral_term_", "", electoral_term_folder)))
            not in sys.argv
        ):
            continue

    agenda_item_pattern = r"(?<=\n).*?(rufe|komme).{,50}?\s(?P<agenda_item>(?:Zusatz)?\w{,20}punkt.{,5}?(\d{1,2}|I{1,3}|V|X))(?P<additional_agenda_items>.*?):"  # noqa: E501
    agenda_item_pattern = regex.compile(agenda_item_pattern)

    # Walk over every session in the electoral_term.
    for session in sorted(os.listdir(electoral_term_folder_path)):
        if session == ".DS_Store":
            continue
        print(session)
        # Create a df which holds the corresponding "Tagesordnungspunkte",
        # additional_agenda_item information which could not be extracted,
        # and the agenda_item_content of the agenda_item
        agenda_item_df = {
            "agenda_item": [],
            "additional_agenda_items": [],
            "agenda_item_content": [],
        }

        # Open spoken agenda_item_content.
        with open(
            os.path.join(electoral_term_folder_path, session, "session_content.txt")
        ) as file:
            session_content = file.read()

        # TOPs script broken at the moment, so skipping
        if electoral_term_folder in ["nothing"]:
            # Try to find all the TOPs.
            agenda_items = list(regex.finditer(agenda_item_pattern, session_content))
            # Name of the TOP.
            agenda_item_description = [
                elem.group("agenda_item") for elem in agenda_items
            ]
            agenda_item_description.insert(0, "intro")
            # Not extracted information after the TOP.
            additional_agenda_items = [
                elem.group("additional_agenda_items") for elem in agenda_items
            ]
            additional_agenda_items.insert(0, "")
            # Character positions of the TOPs.
            spans_begin = [elem.span()[1] for elem in agenda_items]
            spans_begin.insert(0, 0)
            spans_end = [elem.span()[0] for elem in agenda_items]
            spans_end.append(len(session_content))

            # Split the speech_content at the TOPs.
            for agenda_item, additional, begin, end in zip(
                agenda_item_description, additional_agenda_items, spans_begin, spans_end
            ):
                agenda_item_df["agenda_item"].append(agenda_item)
                agenda_item_df["additional_agenda_items"].append(additional)
                agenda_item_df["agenda_item_content"].append(session_content[begin:end])
        else:
            agenda_item_df["agenda_item"].append("to_be_added")
            agenda_item_df["additional_agenda_items"].append("to_be_added")
            agenda_item_df["agenda_item_content"].append(session_content)

        agenda_item_df = pd.DataFrame(agenda_item_df)
        agenda_item_df.to_pickle(os.path.join(save_path, session + ".pkl"))
