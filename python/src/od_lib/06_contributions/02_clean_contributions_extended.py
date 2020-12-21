from od_lib.helper_functions.clean_text import clean_name_headers
import od_lib.definitions.path_definitions as path_definitions
import pandas as pd
import sys
import os
import regex

# Disabling pandas warnings.
pd.options.mode.chained_assignment = None

# input directory
CONTRIBUTIONS_EXTENDED_INPUT = path_definitions.CONTRIBUTIONS_EXTENDED_STAGE_01
FACTIONS = path_definitions.DATA_FINAL

# output directory
CONTRIBUTIONS_EXTENDED_OUTPUT = path_definitions.CONTRIBUTIONS_EXTENDED_STAGE_02

factions = pd.read_pickle(os.path.join(FACTIONS, "factions.pkl"))


faction_patterns = {
    "Bündnis 90/Die Grünen": r"(?:BÜNDNIS\s*(?:90)?/?(?:\s*D[1I]E)?|Bündnis\s*90/(?:\s*D[1I]E)?)?\s*[GC]R[UÜ].?\s*[ÑN]EN?(?:/Bündnis 90)?",  # noqa: E501
    "CDU/CSU": r"(?:Gast|-)?(?:\s*C\s*[DSMU]\s*S?[DU]\s*(?:\s*[/,':!.-]?)*\s*(?:\s*C+\s*[DSs]?\s*[UÙ]?\s*)?)(?:-?Hosp\.|-Gast|1)?",  # noqa: E501
    "BP": r"^\[?BP\]?",
    "DA": r"^\[?DA\]?",
    "DP": r"^\[?DP\]?",
    "DIE LINKE.": r"DIE ?LINKE|LINKEN|\[DIE ?LINKE.\]",
    "DPB": r"^\[?DPB\]?",
    "DRP": r"\[?DRP(\-Hosp\.)?\]?|^\[?SRP\]?|^\[?DBP\]?",
    "FDP": r"\s*F\.?\s*[PDO][.']?[DP]\.?",
    "Fraktionslos": r"(?:fraktionslos|Parteilos)",
    "FU": r"^\[?FU\]?",
    "FVP": r"^\[?FVP\]?",
    "Gast": r"\[?Gast\]?",
    "GB/BHE": r"\[?(?:GB[/-]\s*)?BHE(?:-DG)?\]?",
    "KPD": r"^\[?KPD\]?",
    "NR": r"^\[?NR\]?$",
    "PDS": r"(?:Gruppe\s*der\s*)?PDS(?:/(?:LL|Linke Liste))?",
    "SPD": r"\s*'?S(?:PD|DP)(?:\.|-Gast)?",
    "SSW": r"^\[?SSW\]?",
    "SRP": r"^\[?SRP\]?",
    "WAV": r"^\[?WAV\]?",
    "Z": r"^\[?Z\]?$",
    "AfD": r"^\[?AfD\]?$",
    "DBP": r"^\[?DBP\]?$",
}


def get_faction_abbrev(faction, faction_patterns):
    """matches the given faction and returns an id"""

    for faction_abbrev, faction_pattern in faction_patterns.items():
        if regex.search(faction_pattern, faction):
            return faction_abbrev
    return None


# iterate over all electoral_term_folders
for electoral_term_folder in sorted(os.listdir(CONTRIBUTIONS_EXTENDED_INPUT)):

    if "electoral_term" not in electoral_term_folder:
        continue
    if len(sys.argv) > 1:
        if (
            str(int(regex.sub("electoral_term_", "", electoral_term_folder)))
            not in sys.argv
        ):
            continue
    electoral_term_folder_path = os.path.join(
        CONTRIBUTIONS_EXTENDED_INPUT, electoral_term_folder
    )

    print(electoral_term_folder)

    save_path = os.path.join(CONTRIBUTIONS_EXTENDED_OUTPUT, electoral_term_folder)
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # iterate over every contributions_extended file
    for contributions_extended_file in sorted(os.listdir(electoral_term_folder_path)):
        # checks if the file is a .pkl file
        if ".pkl" not in contributions_extended_file:
            continue

        print(contributions_extended_file)

        filepath = os.path.join(electoral_term_folder_path, contributions_extended_file)

        # read the spoken content csv
        contributions_extended = pd.read_pickle(filepath)

        # Insert acad_title column and extract plain name and titles.
        # ADD DOCUMENTATION HERE
        contributions_extended.insert(3, "faction_id", -1)
        contributions_extended.insert(5, "last_name", "")
        contributions_extended.insert(6, "first_name", "")
        contributions_extended.insert(7, "acad_title", "")

        # Current workaround, because some speeches seem to not be matched
        # correctly. If second stage works without mistakes, this should not be
        # necessary anymoregex.
        contributions_extended = contributions_extended.fillna("")

        # Clean all the names still remaining from PDF Header.
        # KEEP IN MIND THIS ALSO DELETES NAMES IN VOTING LISTS!!!
        # And I think not all names are cleaned because of their position, e.g.
        # "Max Mustermann, Bundeskanzler"
        # THIS PART IS IMPORTANT AND SHOULD WORK PROPERLY, AS REOCCURING NAMES
        # CAN INTRODUCE A LARGE BIAS IN TEXT ANALYSIS
        names = contributions_extended.name_raw.to_list()
        contributions_extended.content = contributions_extended.content.apply(
            clean_name_headers, args=(names, True,)
        )

        contributions_extended.reset_index(inplace=True, drop=True)

        # Delete all not alphabetical chars, keep "-" as it occurs often in
        # names.
        # Question: Is any other character deleted, which could be in a name?
        # Answer: I don't think so.
        contributions_extended.name_raw = contributions_extended.name_raw.astype(str)
        contributions_extended.name_raw = contributions_extended.name_raw.str.replace(
            r"[^a-zA-ZÖÄÜäöüß\-]", " ", regex=True
        )

        # Replace more than two whitespaces with one.
        contributions_extended.name_raw = contributions_extended.name_raw.str.replace(
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

        # Split the name_raw column into it's components at space character.
        first_last_titles = contributions_extended.name_raw.apply(str.split)

        # Extract acad_title, if it is in the titles list.
        contributions_extended.acad_title = [
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
                contributions_extended.first_name.iloc[index] = []
                contributions_extended.last_name.iloc[index] = first_last[0]
            # elif len(first_last) == 2:
            elif len(first_last) >= 2:
                contributions_extended.first_name.iloc[index] = first_last[:-1]
                contributions_extended.last_name.iloc[index] = first_last[-1]
            else:
                contributions_extended.first_name.iloc[index] = []
                contributions_extended.last_name.iloc[index] = ""

        # look for parties in the faction column and replace them with a
        # standardized faction name
        for index, faction in zip(
            contributions_extended.index, contributions_extended.faction
        ):
            if faction:
                faction_abbrev = get_faction_abbrev(
                    str(faction), faction_patterns=faction_patterns
                )

                if faction_abbrev:
                    contributions_extended.faction.at[index] = faction_abbrev
                    try:
                        contributions_extended.faction_id.at[index] = int(
                            factions.id.loc[
                                factions.abbreviation == faction_abbrev
                            ].iloc[0]
                        )
                    except IndexError:
                        contributions_extended.faction_id.at[index] = -1

        contributions_extended.drop(columns=["name_raw"])
        contributions_extended.to_pickle(
            os.path.join(save_path, contributions_extended_file)
        )
