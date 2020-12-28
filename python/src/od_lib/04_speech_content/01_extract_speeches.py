import od_lib.definitions.path_definitions as path_definitions
import pandas as pd
import os
import regex
import sys

# input directory
RAW_TXT = path_definitions.RAW_TXT

# output directory
SPEECH_CONTENT_OUTPUT = path_definitions.SPEECH_CONTENT_STAGE_01

if not os.path.exists(SPEECH_CONTENT_OUTPUT):
    os.makedirs(SPEECH_CONTENT_OUTPUT)

president_pattern_str = r"(?P<position_raw>Präsident(?:in)?|Vizepräsident(?:in)?|Alterspräsident(?:in)?|Bundespräsident(?:in)?|Bundeskanzler(?:in)?)\s+(?P<name_raw>[A-ZÄÖÜß](?:[^:([}{\]\)\s]+\s?){1,5})\s?:\s?"

faction_speaker_pattern_str = r"{3}(?P<name_raw>[A-ZÄÖÜß][^:([{{}}\]\)\n]+?)(\s*{0}(?P<constituency>[^:(){{}}[\]\n]+){1})*\s*{0}(?P<position_raw>{2}){1}(\s*{0}(?P<constituency>[^:(){{}}[\]\n]+){1})*\s?:\s?"

minister_pattern_str = r"{0}(?P<name_raw>[A-ZÄÖÜß](?:[^:([{{}}\]\)\s]+\s?){{1,5}}?),\s?(?P<position_raw>(?P<short_position>Bundesminister(?:in)?|Staatsminister(?:in)?|(?:Parl\s?\.\s)?Staatssekretär(?:in)?|Präsident(?:in)?|Bundeskanzler(?:in)?|Schriftführer(?:in)?|Senator(?:in)?\s?(?:{1}(?P<constituency>[^:([{{}}\]\)\s]+){2})?|Berichterstatter(?:in)?)\s?([^:([\]{{}}\)\n]{{0,76}}?\n?){{1,2}})\s?:\s?"

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
for electoral_term_folder in sorted(os.listdir(RAW_TXT)):
    electoral_term_folder_path = os.path.join(RAW_TXT, electoral_term_folder)

    if not os.path.isdir(electoral_term_folder_path):
        continue
    elif electoral_term_folder == ".DS_Store":
        continue
    elif electoral_term_folder in [
        "electoral_term_01",
        "electoral_term_02",
        "electoral_term_03",
        "electoral_term_04",
        "electoral_term_05",
        "electoral_term_06",
        "electoral_term_07",
        "electoral_term_08",
        "electoral_term_09",
        "electoral_term_10",
    ]:
        open_brackets = r"[({\[]"
        close_brackets = r"[)}\]]"
        prefix = r"(?<=\n)"
    elif electoral_term_folder in [
        "electoral_term_11",
        "electoral_term_12",
        "electoral_term_13",
        "electoral_term_14",
        "electoral_term_15",
        "electoral_term_16",
        "electoral_term_17",
        "electoral_term_18",
    ]:
        open_brackets = r"[(]"
        close_brackets = r"[)]"
        prefix = r"(?<=\n)"
    else:
        raise ValueError("You should not land heregex.")

    if len(sys.argv) > 1:
        if (
            str(int(regex.sub("electoral_term_", "", electoral_term_folder)))
            not in sys.argv
        ):
            continue

    faction_speaker_pattern = regex.compile(
        faction_speaker_pattern_str.format(
            open_brackets, close_brackets, "|".join(parties), prefix
        )
    )
    president_pattern = regex.compile(president_pattern_str)
    minister_pattern = regex.compile(
        minister_pattern_str.format(prefix, open_brackets, close_brackets)
    )

    patterns = [president_pattern, faction_speaker_pattern, minister_pattern]

    save_path = os.path.join(SPEECH_CONTENT_OUTPUT, electoral_term_folder)
    if not os.path.isdir(save_path):
        os.makedirs(save_path)

    # Walk over every session in the period.
    for session in sorted(os.listdir(electoral_term_folder_path)):
        # Skip e.g. the .DS_Store file.
        if not os.path.isdir(os.path.join(electoral_term_folder_path, session)):
            continue

        print(session)

        session_df = pd.DataFrame(
            {
                "session": [],
                "name_raw": [],
                "position_raw": [],
                "constituency": [],
                "speech_content": [],
                "span_begin": [],
                "span_end": [],
            }
        )

        # Open the session content
        with open(
            os.path.join(electoral_term_folder_path, session, "session_content.txt")
        ) as file:
            session_content = file.read()

        # Placeholders for the information of a speaker.
        session_list = []
        speaker_name = []
        speaker_position = []  # faction like "SPD" or also "Präsident"
        speaker_constituency = []
        speaker_span_begin = []  # Character position beginning of match
        speaker_span_end = []  # Character position ending of match
        speech_content = []

        # Search all parts where one of the patterns is matching.
        for pattern in patterns:
            for match in regex.finditer(pattern, session_content):
                session_list.append(session)
                speaker_name.append(match.group("name_raw"))
                speaker_position.append(match.group("position_raw"))
                try:
                    speaker_constituency.append(match.group("constituency"))
                except IndexError:
                    speaker_constituency.append(None)
                spans = match.span()
                speaker_span_begin.append(spans[0])
                speaker_span_end.append(spans[1])

        # Sort the speeches in the text.
        session_df["session"] = session_list
        session_df["name_raw"] = speaker_name
        session_df["position_raw"] = speaker_position
        session_df["constituency"] = speaker_constituency
        session_df["span_begin"] = speaker_span_begin
        session_df["span_end"] = speaker_span_end

        session_df = session_df.sort_values(by="span_begin")

        # Cut out the speech_contents between the matched patterns.
        speech_beginnings = session_df.span_end.to_list()
        speech_endings = session_df.span_begin.to_list()[1:]
        speech_endings.append(len(session_content))

        for begin, end in zip(speech_beginnings, speech_endings):
            speech_content.append(session_content[begin:end])

        session_df["speech_content"] = speech_content

        session_df.to_pickle(os.path.join(save_path, session + ".pkl"))
