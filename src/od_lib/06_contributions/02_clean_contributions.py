from od_lib.helper_functions.clean_text import clean_name_headers
import od_lib.definitions.path_definitions as path_definitions
import pandas as pd
import sys
import os
import regex

# Disabling pandas warnings.
pd.options.mode.chained_assignment = None

# input directory
CONTRIBUTIONS_INPUT = path_definitions.CONTRIBUTIONS_STAGE_01
FACTIONS = path_definitions.DATA_FINAL

# output directory
CONTRIBUTIONS_OUTPUT = path_definitions.CONTRIBUTIONS_STAGE_02

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
for electoral_term_folder in sorted(os.listdir(CONTRIBUTIONS_INPUT)):

    if "electoral_term" not in electoral_term_folder:
        continue
    if len(sys.argv) > 1:
        if (
            str(int(regex.sub("electoral_term_", "", electoral_term_folder)))
            not in sys.argv
        ):
            continue
    electoral_term_folder_path = os.path.join(
        CONTRIBUTIONS_INPUT, electoral_term_folder
    )

    print(electoral_term_folder)

    save_path = os.path.join(CONTRIBUTIONS_OUTPUT, electoral_term_folder)
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # iterate over every contributions file
    for contributions_file in sorted(os.listdir(electoral_term_folder_path)):
        # checks if the file is a .pkl file
        if ".pkl" not in contributions_file:
            continue

        print(contributions_file)

        filepath = os.path.join(electoral_term_folder_path, contributions_file)

        # read the spoken content csv
        contributions = pd.read_pickle(filepath)

        # Insert acad_title column and extract plain name and titles.
        # ADD DOCUMENTATION HERE
        contributions.insert(3, "faction_id", -1)
        contributions.insert(5, "last_name", "")
        contributions.insert(6, "first_name", "")
        contributions.insert(7, "acad_title", "")

        # Current workaround, because some speeches seem to not be matched
        # correctly. If second stage works without mistakes, this should not be
        # necessary anymoregex.
        contributions = contributions.fillna("")

        # Clean all the names still remaining from PDF Header.
        # KEEP IN MIND THIS ALSO DELETES NAMES IN VOTING LISTS!!!
        # And I think not all names are cleaned because of their position, e.g.
        # "Max Mustermann, Bundeskanzler"
        # THIS PART IS IMPORTANT AND SHOULD WORK PROPERLY, AS REOCCURING NAMES
        # CAN INTRODUCE A LARGE BIAS IN TEXT ANALYSIS
        names = contributions.name_raw.to_list()
        contributions.content = contributions.content.apply(
            clean_name_headers, args=(names, True,)
        )

        contributions.reset_index(inplace=True, drop=True)

        # Delete all not alphabetical chars, keep "-" as it occurs often in
        # names.
        # Question: Is any other character deleted, which could be in a name?
        # Answer: I don't think so.
        contributions.name_raw = contributions.name_raw.astype(str)
        contributions.name_raw = contributions.name_raw.str.replace(
            r"[^a-zA-ZÖÄÜäöüß\-]", " ", regex=True
        )

        # Replace more than two whitespaces with one.
        contributions.name_raw = contributions.name_raw.str.replace(r"  +", " ", regex=True)

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
        first_last_titles = contributions.name_raw.apply(str.split)

        # Extract acad_title, if it is in the titles list.
        contributions.acad_title = [
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
                contributions.first_name.iloc[index] = []
                contributions.last_name.iloc[index] = first_last[0]
            # elif len(first_last) == 2:
            elif len(first_last) >= 2:
                contributions.first_name.iloc[index] = first_last[:-1]
                contributions.last_name.iloc[index] = first_last[-1]
            else:
                contributions.first_name.iloc[index] = []
                contributions.last_name.iloc[index] = ""

        # look for parties in the faction column and replace them with a
        # standardized faction name
        for index, faction in zip(contributions.index, contributions.faction):
            if faction:
                faction_abbrev = get_faction_abbrev(
                    str(faction), faction_patterns=faction_patterns
                )

                if faction_abbrev:
                    contributions.faction.at[index] = faction_abbrev
                    try:
                        contributions.faction_id.at[index] = int(
                            factions.id.loc[
                                factions.abbreviation == faction_abbrev
                            ].iloc[0]
                        )
                    except IndexError:
                        contributions.faction_id.at[index] = -1

        contributions.drop(columns=["name_raw"])
        contributions.to_pickle(os.path.join(save_path, contributions_file))
