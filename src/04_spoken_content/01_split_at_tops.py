import pandas as pd
import os
import regex
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))
import path_definitions

# input directory ______________________________________________________________
RAW_TXT = path_definitions.RAW_TXT

# output directory _____________________________________________________________
SPOKEN_CONTENT_STAGE_01 = path_definitions.SPOKEN_CONTENT_STAGE_01

# Walk over every period _______________________________________________________
for wp_folder in sorted(os.listdir(RAW_TXT)):
    wp_folder_path = os.path.join(RAW_TXT, wp_folder)
    save_path = os.path.join(SPOKEN_CONTENT_STAGE_01, wp_folder)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    if not os.path.isdir(wp_folder_path):
        continue
    elif wp_folder == ".DS_Store":
        continue
    if len(sys.argv) > 1:
        if str(int(regex.sub("wp_", "", wp_folder))) not in sys.argv:
            continue

    top_pattern = r"(?<=\n).*?(rufe|komme).{,50}?\s(?P<top>(?:Zusatz)?\w{,20}punkt.{,5}?(\d{1,2}|I{1,3}|V|X))(?P<additional_tops>.*?):"
    top_pattern = regex.compile(top_pattern)

    # Walk over every sitting in the wp.
    for sitting in sorted(os.listdir(wp_folder_path)):
        if sitting == ".DS_Store":
            continue
        print(sitting)
        # Create a df which holds the corresponding "Tagesordnungspunkte",
        # additional_top information which could not be extracted,
        # and the content of the top
        top_df = {
            "top": [],
            "additional_tops": [],
            "content": [],
        }

        # Open spoken content.
        with open(os.path.join(wp_folder_path, sitting, "spoken_content.txt")) as file:
            spoken_content = file.read()

        # TOPs script broken at the moment, so skipping
        if wp_folder in ["nothing"]:
            # Try to find all the TOPs.
            tops = list(regex.finditer(top_pattern, spoken_content))
            # Name of the TOP.
            top_description = [elem.group("top") for elem in tops]
            top_description.insert(0, "intro")
            # Not extracted information after the TOP.
            additional_tops = [elem.group("additional_tops") for elem in tops]
            additional_tops.insert(0, "")
            # Character positions of the TOPs.
            spans_begin = [elem.span()[1] for elem in tops]
            spans_begin.insert(0, 0)
            spans_end = [elem.span()[0] for elem in tops]
            spans_end.append(len(spoken_content))

            # Split the spoken_content at the TOPs.
            for top, additional, begin, end in zip(
                top_description, additional_tops, spans_begin, spans_end
            ):
                top_df["top"].append(top)
                top_df["additional_tops"].append(additional)
                top_df["content"].append(spoken_content[begin:end])
        else:
            top_df["top"].append("to_be_added")
            top_df["additional_tops"].append("to_be_added")
            top_df["content"].append(spoken_content)

        top_df = pd.DataFrame(top_df)
        top_df.to_pickle(os.path.join(save_path, sitting + ".pkl"))
