import pandas as pd
import sys
import os
import regex

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))
import path_definitions
from src.helper_functions.clean_text import clean_name_headers

# Disabling pandas warnings.
pd.options.mode.chained_assignment = None

# input directory ______________________________________________________________
CONTRIBUTIONS_INPUT = path_definitions.CONTRIBUTIONS_STAGE_01
FACTIONS = path_definitions.DATA_FINAL

# output directory _____________________________________________________________
CONTRIBUTIONS_OUTPUT = path_definitions.CONTRIBUTIONS_STAGE_02

factions = pd.read_pickle(os.path.join(FACTIONS, "factions.pkl"))


parties_patterns = {
    "Bündnis 90/Die Grünen": r"(?:BÜNDNIS\s*(?:90)?/?(?:\s*D[1I]E)?|Bündnis\s*90/(?:\s*D[1I]E)?)?\s*[GC]R[UÜ].?\s*[ÑN]EN?(?:/Bündnis 90)?",
    "CDU/CSU": r"(?:Gast|-)?(?:\s*C\s*[DSMU]\s*S?[DU]\s*(?:\s*[/,':!.-]?)*\s*(?:\s*C+\s*[DSs]?\s*[UÙ]?\s*)?)(?:-?Hosp\.|-Gast|1)?",
    "BP": r"^\[?BP\]?",
    "DA": r"^\[?DA\]?",
    "DP": r"^\[?DP\]?",
    "DIE LINKE.": r"DIE ?LINKE|LINKEN|\[DIE ?LINKE.\]",
    "DPB": r"^\[?DPB\]?",
    "DRP": r"\[?DRP(\-Hosp\.)?\]?|^\[?SRP\]?|^\[?DBP\]?",
    "FDP": "\s*F\.?\s*[PDO][.']?[DP]\.?",
    "Fraktionslos": r"(?:fraktionslos|Parteilos)",
    "FU": r"^\[?FU\]?",
    "FVP": r"^\[?FVP\]?",
    "Gast": r"\[?Gast\]?",
    "GB/BHE": r"\[?(?:GB[/-]\s*)?BHE(?:-DG)?\]?",
    "KPD": r"^\[?KPD\]?",
    "NR": r"^\[?NR\]?",
    "PDS": r"(?:Gruppe\s*der\s*)?PDS(?:/(?:LL|Linke Liste))?",
    "SPD": "\s*'?S(?:PD|DP)(?:\.|-Gast)?",
    "SSW": r"^\[?SSW\]?",
    "SRP": r"^\[?SRP\]?",
    "WAV": r"^\[?WAV\]?",
    "Z": r"^\[?Z\]?$",
    "AfD": r"^\[?AfD\]?$",
    "DBP": r"^\[?DBP\]?$",
    "NR": r"^\[?NR\]?$",
}


def get_faction_abbrev(party, parties_patterns):
    """matches the given party and returns an id"""

    for party_abbrev, party_pattern in parties_patterns.items():
        if regex.search(party_pattern, party):
            # if party_abbrev == "DIE LINKE.":
            #     print("stop")
            return party_abbrev
    return None


# iterate over all wp_folders
for wp_folder in sorted(os.listdir(CONTRIBUTIONS_INPUT)):

    if "wp" not in wp_folder:
        continue
    if len(sys.argv) > 1:
        if str(int(regex.sub("wp_", "", wp_folder))) not in sys.argv:
            continue
    wp_folder_path = os.path.join(CONTRIBUTIONS_INPUT, wp_folder)

    print(wp_folder)

    save_path = os.path.join(CONTRIBUTIONS_OUTPUT, wp_folder)
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # iterate over every contributions file
    for contributions_file in sorted(os.listdir(wp_folder_path)):
        # checks if the file is a .pkl file
        if ".pkl" not in contributions_file:
            continue

        print(contributions_file)

        filepath = os.path.join(wp_folder_path, contributions_file)

        # read the spoken content csv
        contributions = pd.read_pickle(filepath)

        # Insert title column and extract plain name and titles.
        # ADD DOCUMENTATION HERE
        contributions.insert(3, "faction_id", -1)
        contributions.insert(5, "last_name", "")
        contributions.insert(6, "first_name", "")
        contributions.insert(7, "title", "")

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
        names = contributions.name.to_list()
        contributions.content = contributions.content.apply(clean_name_headers, args=(names, True,))

        contributions.reset_index(inplace=True, drop=True)

        # Delete all not alphabetical chars, keep "-" as it occurs often in
        # names.
        # Question: Is any other character deleted, which could be in a name?
        # Answer: I don't think so.
        contributions.name = contributions.name.astype(str)
        contributions.name = contributions.name.str.replace("[^a-zA-ZÖÄÜäöüß\-]", " ", regex=True)

        # Replace more than two whitespaces with one.
        contributions.name = contributions.name.str.replace(r"  +", " ", regex=True)

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
        first_last_titles = contributions.name.apply(str.split)

        # Extract title, if it is in the titles list.
        contributions.title = [
            [title for title in title_list if title in titles] for title_list in first_last_titles
        ]

        # Remove titles from the first_last_name list.
        for politician_titles in first_last_titles:
            for title in politician_titles[:]:
                if title in titles:
                    politician_titles.remove(title)

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

        # look for parties in the party column and replace them with a
        # standardized party name
        for index, party in zip(contributions.index, contributions.party):
            if party:
                faction_abbrev = get_faction_abbrev(str(party), parties_patterns=parties_patterns)

                if faction_abbrev:
                    contributions.party.at[index] = faction_abbrev
                    try:
                        # .iloc[0] is important right now, as some faction entries
                        # in factions df share same faction_id, so always the first
                        # one is chosen right now.
                        contributions.faction_id.at[index] = int(
                            factions.id.loc[factions.abbreviation == faction_abbrev].iloc[0]
                        )
                    except:
                        contributions.faction_id.at[index] = -1

        contributions.to_pickle(os.path.join(save_path, contributions_file))
