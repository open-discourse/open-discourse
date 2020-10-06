import od_lib.definitions.path_definitions as path_definitions
import pandas as pd
import os
import regex
import sys

# input directory ______________________________________________________________
SPOKEN_CONTENT_INPUT = path_definitions.SPOKEN_CONTENT_STAGE_01

# output directory _____________________________________________________________
SPOKEN_CONTENT_OUTPUT = path_definitions.SPOKEN_CONTENT_STAGE_02

if not os.path.exists(SPOKEN_CONTENT_OUTPUT):
    os.makedirs(SPOKEN_CONTENT_OUTPUT)

# ______________________________________________________________________________
# I think we should not include the positive look behind of the newline
# character, because it happens quite often, that President parts starts
# within a line.
president_pattern_str = r"(?P<position>Präsident(?:in)?|Vizepräsident(?:in)?|Alterspräsident(?:in)?|Bundespräsident(?:in)?|Bundeskanzler(?:in)?)\s+(?P<name>[A-ZÄÖÜß](?:[^:([}{\]\)\s]+\s?){1,5})\s?:\s?"

faction_speaker_pattern_str = r"{3}(?P<name>[A-ZÄÖÜß][^:([{{}}\]\)\n]+?)(\s*{0}(?P<location_information>[^:(){{}}[\]\n]+){1})*\s*{0}(?P<position>{2}){1}(\s*{0}(?P<location_information>[^:(){{}}[\]\n]+){1})*\s?:\s?"

minister_pattern_str = r"{0}(?P<name>[A-ZÄÖÜß](?:[^:([{{}}\]\)\s]+\s?){{1,5}}?),\s?(?P<position>(?P<short_position>Bundesminister(?:in)?|Staatsminister(?:in)?|(?:Parl\s?\.\s)?Staatssekretär(?:in)?|Präsident(?:in)?|Bundeskanzler(?:in)?|Schriftführer(?:in)?|Senator(?:in)?\s?(?:{1}(?P<location_information>[^:([{{}}\]\)\s]+){2})?|Berichterstatter(?:in)?)\s?([^:([\]{{}}\)\n]{{0,76}}?\n?){{1,2}})\s?:\s?"

parties = [
    r"(?:Gast|-)?(?:\s*C\s*[DSMU]\s*S?[DU]\s*(?:\s*[/,':!.-]?)*\s*(?:\s*C+\s*[DSs]?\s*[UÙ]?\s*)?)(?:-?Hosp\.|-Gast|1)?",
    r"\s*'?S(?:PD|DP)(?:\.|-Gast)?",
    r"\s*F\.?\s*[PDO][.']?[DP]\.?",
    r"(?:BÜNDNIS\s*(?:90)?/?(?:\s*D[1I]E)?|Bündnis\s*90/(?:\s*D[1I]E)?)?\s*[GC]R[UÜ].?\s*[ÑN]EN?(?:/Bündnis 90)?",
    r"DIE LINKE",
    r"(?:Gruppe\s*der\s*)?PDS(?:/(?:LL|Linke Liste))?",
    r"(fraktionslos|Parteilos)",
    r"(?:GB[/-]\s*)?BHE(?:-DG)?",
    "DP",
    "KPD",
    "Z",
    "BP",
    "FU",
    "WAV",
    r"DRP(\-Hosp\.)",
    "FVP",
    "SSW",
    "SRP",
    "DA",
    "Gast",
    "DBP",
    "NR",
]

print("Starting..")

# Walk over all legislature periods. ___________________________________________
for wp_folder in sorted(os.listdir(SPOKEN_CONTENT_INPUT)):
    wp_folder_path = os.path.join(SPOKEN_CONTENT_INPUT, wp_folder)

    # if wp_folder in ["wp_01", "wp_02", "wp_03", "wp_04", "wp_05", "wp_06",
    #                  "wp_07", "wp_08", "wp_09", "wp_10", "wp_11", "wp_12", "wp_13"]:
    #     continue

    if not os.path.isdir(wp_folder_path):
        continue
    elif wp_folder == ".DS_Store":
        continue
    elif wp_folder in [
        "wp_01",
        "wp_02",
        "wp_03",
        "wp_04",
        "wp_05",
        "wp_06",
        "wp_07",
        "wp_08",
        "wp_09",
        "wp_10",
    ]:
        open_brackets = r"[({\[]"
        close_brackets = r"[)}\]]"
        # prefix = r"(?:(?<=\-\s)|(?<=\n))"
        prefix = r"(?<=\n)"
    elif wp_folder in [
        "wp_11",
        "wp_12",
        "wp_13",
        "wp_14",
        "wp_15",
        "wp_16",
        "wp_17",
        "wp_18",
    ]:
        open_brackets = r"[(]"
        close_brackets = r"[)]"
        prefix = r"(?<=\n)"
    else:
        raise ValueError("You should not land heregex.")

    if len(sys.argv) > 1:
        if str(int(regex.sub("wp_", "", wp_folder))) not in sys.argv:
            continue

    faction_speaker_pattern = regex.compile(
        faction_speaker_pattern_str.format(
            open_brackets, close_brackets, "|".join(parties), prefix
        )
    )
    # faction_speaker_pattern = regex.compile(faction_speaker_pattern_str.format(open_brackets, close_brackets, "[^(){{}}[\]\n]{1,25}"))
    president_pattern = regex.compile(president_pattern_str)
    minister_pattern = regex.compile(
        minister_pattern_str.format(prefix, open_brackets, close_brackets)
    )

    patterns = [president_pattern, faction_speaker_pattern, minister_pattern]

    save_path = os.path.join(SPOKEN_CONTENT_OUTPUT, wp_folder)
    if not os.path.isdir(save_path):
        os.makedirs(save_path)

    # Walk over every sitting in the period.
    for spoken_content_file in sorted(os.listdir(wp_folder_path)):
        if ".pkl" not in spoken_content_file:
            continue

        print(spoken_content_file)
        if spoken_content_file == "03004.pkl":
            print("hallo")

        sitting_df = pd.DataFrame(
            {
                "sitting": [],
                "wp": [],
                "top": [],
                "additional_tops": [],
                "name": [],
                "position": [],
                "location_information": [],
                "speech_content": [],
                "span_begin": [],
                "span_end": [],
            }
        )

        spoken_content = pd.read_pickle(
            os.path.join(wp_folder_path, spoken_content_file)
        )

        # Walk over every TOP, which was extracted for the first_stage.
        for top, additional, content in zip(
            spoken_content.top.to_list(),
            spoken_content.additional_tops.to_list(),
            spoken_content.content.to_list(),
        ):

            sorting_df = pd.DataFrame(
                {
                    "sitting": [],
                    "wp": [],
                    "top": [],
                    "additional_tops": [],
                    "name": [],
                    "position": [],
                    "location_information": [],
                    "speech_content": [],
                    "span_begin": [],
                    "span_end": [],
                }
            )

            # Placeholders for the information of a speaker. ___________________
            sitting_list = []
            top_list = []
            additional_tops_list = []
            speaker_name = []
            speaker_position = []  # faction like "SPD" or also "Präsident"
            speaker_location_information = []
            speaker_span_begin = []  # Character position beginning of match
            speaker_span_end = []  # Character position ending of match
            speech_content = []

            # Search all parts where one of the patterns is matching. __________
            for pattern in patterns:
                for match in regex.finditer(pattern, content):
                    sitting_list.append(spoken_content_file)
                    top_list.append(top)
                    additional_tops_list.append(additional)
                    speaker_name.append(match.group("name"))
                    speaker_position.append(match.group("position"))
                    try:
                        speaker_location_information.append(
                            match.group("location_information")
                        )
                    except IndexError:
                        speaker_location_information.append(None)

                    spans = match.span()
                    speaker_span_begin.append(spans[0])
                    speaker_span_end.append(spans[1])

            # Sort the speeches in the text. ___________________________________
            sorting_df["sitting"] = sitting_list
            sorting_df["top"] = top_list
            sorting_df["additional_tops"] = additional_tops_list
            sorting_df["name"] = speaker_name
            sorting_df["position_long"] = speaker_position
            sorting_df["location_information"] = speaker_location_information
            sorting_df["span_begin"] = speaker_span_begin
            sorting_df["span_end"] = speaker_span_end

            sorting_df = sorting_df.sort_values(by="span_begin")

            # Cut out the speeches content between the matched patterns. _______
            speech_beginnings = sorting_df.span_end.to_list()
            speech_endings = sorting_df.span_begin.to_list()[1:]
            speech_endings.append(len(content))

            for begin, end in zip(speech_beginnings, speech_endings):
                speech_content.append(content[begin:end])

            sorting_df["speech_content"] = speech_content

            sorting_df.replace()

            # Append df to the preceding parts of the sitting.
            sitting_df = pd.concat([sitting_df, sorting_df], sort=False)

        sitting_df.to_pickle(os.path.join(save_path, spoken_content_file))
