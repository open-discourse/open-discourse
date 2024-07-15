import os
import sys

import pandas as pd
import regex

import open_discourse.definitions.path_definitions as path_definitions
from open_discourse.helper_functions.clean_text import clean_name_headers

# Disabling pandas warnings.
pd.options.mode.chained_assignment = None

# input directory
SPEECH_CONTENT_INPUT = path_definitions.SPEECH_CONTENT_STAGE_01
FACTIONS = path_definitions.DATA_FINAL

# output directory
SPEECH_CONTENT_OUTPUT = path_definitions.SPEECH_CONTENT_STAGE_02

factions = pd.read_pickle(os.path.join(FACTIONS, "factions.pkl"))

faction_patterns = {
    "Bündnis 90/Die Grünen": r"(?:BÜNDNIS\s*(?:90)?/?(?:\s*D[1I]E)?|Bündnis\s*90/(?:\s*D[1I]E)?)?\s*[GC]R[UÜ].?\s*[ÑN]EN?(?:/Bündnis 90)?|Bündnis 90/Die Grünen",  # noqa: E501
    "CDU/CSU": r"(?:Gast|-)?(?:\s*C\s*[DSMU]\s*S?[DU]\s*(?:\s*[/,':!.-]?)*\s*(?:\s*C+\s*[DSs]?\s*[UÙ]?\s*)?)(?:-?Hosp\.|-Gast|1)?",  # noqa: E501
    "BP": r"^BP",
    "DA": r"^DA",
    "DP": r"^DP",
    "DIE LINKE.": r"DIE LINKE",
    "DPB": r"(?:^DPB)",
    "DRP": r"DRP(\-Hosp\.)?|SRP",
    "FDP": r"\s*F\.?\s*[PDO][.']?[DP]\.?",
    "Fraktionslos": r"(?:fraktionslos|Parteilos|parteilos)",
    "FU": r"^FU",
    "FVP": r"^FVP",
    "Gast": r"Gast",
    "GB/BHE": r"(?:GB[/-]\s*)?BHE(?:-DG)?",
    "KPD": r"^KPD",
    "PDS": r"(?:Gruppe\s*der\s*)?PDS(?:/(?:LL|Linke Liste))?",
    "SPD": r"\s*'?S(?:PD|DP)(?:\.|-Gast)?",
    "SSW": r"^SSW",
    "SRP": r"^SRP",
    "WAV": r"^WAV",
    "Z": r"^Z$",
    "DBP": r"^DBP$",
    "NR": r"^NR$",
}


def get_faction_abbrev(faction, faction_patterns):
    """matches the given faction and returns an id"""

    for faction_abbrev, faction_pattern in faction_patterns.items():
        if regex.search(faction_pattern, faction):
            return faction_abbrev
    return None


def get_position_short_and_long(position):
    """matches the given position and returns the long and short version"""
    if position in faction_patterns.keys() or regex.match(
        r"^[Bb]erichterstatter(in)?(\s|$|,|.)", position
    ):
        return (
            "Member of Parliament",
            None if position in faction_patterns.keys() else position,
        )
    elif (
        regex.match(r"^[Bb]undestagspräsident(in)?(\s|$|,|.)", position)
        or regex.match(r"^[Aa]lterspräsident(in)?(\s|$|,|.)", position)
        or regex.match(r"^[Vv]izebundestagspräsident(in)?(\s|$|,|.)", position)
        or regex.match(r"^[Ss]chriftführer(in)?(\s|$|,|.)", position)
        or position.lower()
        in [
            "präsidentin",
            "präsident",
            "präsident des deutschen bundestages",
            "präsidentin des deutschen bundestages",
            "vizepräsidentin",
            "vizepräsident",
        ]
    ):
        return "Presidium of Parliament", position
    elif (
        regex.match(r"^[Bb]undespräsident(in)?(\s|$|,|.)", position)
        or regex.match(r"^[Ss]taatsminister(in)?(\s|$|,|.)", position)
        or regex.match(r"^[Ss]enator(in)?(\s|$|,|.)", position)
        or regex.match(r"^[Pp]räsident(in)?(\s|$|,|.)", position)
        or regex.match(r"^[Gg]ast", position)
    ):
        return "Guest", position
    elif regex.match(r"^[Bb]undeskanzler(in)?(\s|$|,|.)", position):
        return "Chancellor", None
    elif regex.match(r"^(Bundes)?[Mm]inister(in)?(\s|$|,|.)", position):
        return "Minister", position
    elif regex.match(r"^([Pp]arl\s*\.\s+)?[Ss]taatssekretär(in)?(\s|$|,|.)", position):
        return "Secretary of State", position
    else:
        return "Not found", None


# iterate over all electoral_term_folders
for electoral_term_folder in sorted(os.listdir(SPEECH_CONTENT_INPUT)):
    if electoral_term_folder == ".DS_Store":
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

    save_path = os.path.join(SPEECH_CONTENT_OUTPUT, electoral_term_folder)
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # iterate over every speech_content file
    for speech_content_file in sorted(os.listdir(electoral_term_folder_path)):
        print(speech_content_file)

        # checks if the file is a .pkl file
        if ".pkl" not in speech_content_file:
            continue
        filepath = os.path.join(electoral_term_folder_path, speech_content_file)

        # read the spoken content csv
        speech_content = pd.read_pickle(filepath)

        # Insert acad_title column and extract plain name and titles.
        # ADD DOCUMENTATION HERE
        speech_content.insert(3, "faction_id", -1)
        speech_content.insert(3, "position_short", "")
        speech_content.insert(4, "position_long", "")
        speech_content.insert(5, "last_name", "")
        speech_content.insert(6, "first_name", "")
        speech_content.insert(7, "acad_title", "")

        # Current workaround, because some speeches seem to not be matched
        # correctly. If second stage works without mistakes (extracting the
        # speech parts), this should not be necessary anymore.
        speech_content = speech_content.fillna("")

        # Clean all the names still remaining from PDF Header.
        # KEEP IN MIND THIS ALSO DELETES NAMES IN VOTING LISTS!!!
        # And I think not all names are cleaned because of their position, e.g.
        # "Max Mustermann, Bundeskanzler"
        # THIS PART IS IMPORTANT AND SHOULD WORK PROPERLY, AS REOCCURING NAMES
        # CAN INTRODUCE A LARGE BIAS IN TEXT ANALYSIS
        names = speech_content.name_raw.to_list()
        speech_content.speech_content = speech_content.speech_content.apply(
            clean_name_headers, args=(names,)
        )

        speech_content.reset_index(inplace=True, drop=True)

        # Delete all not alphabetical chars, keep "-" as it occurs often in
        # names.
        # Question: Is any other character deleted, which could be in a name?
        # Answer: I don't think so.
        speech_content.name_raw = speech_content.name_raw.str.replace(
            r"[^a-zA-ZÖÄÜäöüß\-]", " ", regex=True
        )

        # Replace more than two whitespaces with one.
        speech_content.name_raw = speech_content.name_raw.str.replace(
            r"  +", " ", regex=True
        )

        # Graf has to be checked again, as this is also a last_name.
        # Titles have to be added: Like e.c. or when mistakes occur like b.c.
        # Deleted "Graf" for now.
        titles = [
            "Dr",
            "Frau",
            "D",
            "-Ing",
            "von",
            "und",
            "zu",
            "van",
            "de",
            "Baron",
            "Freiherr",
            "Prinz",
            "h",
            "c",
        ]

        # Split the name column into it's components at space character.
        first_last_titles = speech_content.name_raw.apply(str.split)

        # Extract acad_title, if it is in the titles list.
        speech_content.acad_title = [
            [acad_title for acad_title in title_list if acad_title in titles]
            for title_list in first_last_titles
        ]

        # Remove titles from the first_last_name list.
        for politician_titles in first_last_titles:
            for acad_title in politician_titles[:]:
                if acad_title in titles:
                    politician_titles.remove(acad_title)

        # Get the first and last name based on the amount of elements.
        for index, first_last in zip(range(len(first_last_titles)), first_last_titles):
            if len(first_last) == 1:
                speech_content.first_name.iloc[index] = ""
                speech_content.last_name.iloc[index] = first_last[0]
            elif len(first_last) >= 2:
                speech_content.first_name.iloc[index] = first_last[:-1]
                speech_content.last_name.iloc[index] = first_last[-1]
            else:
                speech_content.first_name.iloc[index] = "ERROR"
                speech_content.last_name.iloc[index] = "ERROR"

        # look for factions in the faction column and replace them with a
        # standardized faction name
        for index, position_raw in zip(
            speech_content.index, speech_content.position_raw
        ):
            faction_abbrev = get_faction_abbrev(
                str(position_raw), faction_patterns=faction_patterns
            )
            (
                speech_content.position_short.at[index],
                speech_content.position_long.at[index],
            ) = get_position_short_and_long(
                faction_abbrev
                if faction_abbrev
                else regex.sub("\n+", " ", position_raw)
            )
            if faction_abbrev:
                try:
                    speech_content.faction_id.at[index] = int(
                        factions.id.loc[factions.abbreviation == faction_abbrev].iloc[0]
                    )
                except IndexError:
                    speech_content.faction_id.at[index] = -1

        speech_content = speech_content.drop(columns=["position_raw", "name_raw"])
        speech_content.to_pickle(os.path.join(save_path, speech_content_file))
