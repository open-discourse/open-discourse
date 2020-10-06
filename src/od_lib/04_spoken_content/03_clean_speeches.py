from od_lib.helper_functions.clean_text import clean_name_headers
import od_lib.definitions.path_definitions as path_definitions
import pandas as pd
import sys
import os
import regex

# Disabling pandas warnings.
pd.options.mode.chained_assignment = None

# input directory ______________________________________________________________
SPOKEN_CONTENT_INPUT = path_definitions.SPOKEN_CONTENT_STAGE_02
FACTIONS = path_definitions.DATA_FINAL

# output directory _____________________________________________________________
SPOKEN_CONTENT_OUTPUT = path_definitions.SPOKEN_CONTENT_STAGE_03

factions = pd.read_pickle(os.path.join(FACTIONS, "factions.pkl"))

parties_patterns = {
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


def get_faction_abbrev(party, parties_patterns):
    """matches the given party and returns an id"""

    for party_abbrev, party_pattern in parties_patterns.items():
        if regex.search(party_pattern, party):
            return party_abbrev
    return None


def get_position_short_and_long(position):
    """matches the given position and returns the long and short version"""
    if position in parties_patterns.keys() or regex.match(
        r"^[Bb]erichterstatter(in)?(\s|$|,|.)", position
    ):
        return (
            "Member of Parliament",
            None if position in parties_patterns.keys() else position,
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


# iterate over all wp_folders
for wp_folder in sorted(os.listdir(SPOKEN_CONTENT_INPUT)):

    if wp_folder == ".DS_Store":
        continue
    if len(sys.argv) > 1:
        if str(int(regex.sub("wp_", "", wp_folder))) not in sys.argv:
            continue
    wp_folder_path = os.path.join(SPOKEN_CONTENT_INPUT, wp_folder)

    print(wp_folder)

    save_path = os.path.join(SPOKEN_CONTENT_OUTPUT, wp_folder)
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # iterate over every spoken_content file
    for spoken_content_file in sorted(os.listdir(wp_folder_path)):
        print(spoken_content_file)

        # checks if the file is a .pkl file
        if ".pkl" not in spoken_content_file:
            continue
        filepath = os.path.join(wp_folder_path, spoken_content_file)

        # read the spoken content csv
        spoken_content = pd.read_pickle(filepath)

        # Insert title column and extract plain name and titles.
        # ADD DOCUMENTATION HERE
        spoken_content.insert(3, "faction_id", -1)
        spoken_content.insert(3, "position_short", "")
        spoken_content.insert(5, "last_name", "")
        spoken_content.insert(6, "first_name", "")
        spoken_content.insert(7, "title", "")

        # Current workaround, because some speeches seem to not be matched
        # correctly. If second stage works without mistakes (extracting the
        # speech parts), this should not be necessary anymore.
        spoken_content = spoken_content.fillna("")

        # Clean all the names still remaining from PDF Header.
        # KEEP IN MIND THIS ALSO DELETES NAMES IN VOTING LISTS!!!
        # And I think not all names are cleaned because of their position, e.g.
        # "Max Mustermann, Bundeskanzler"
        # THIS PART IS IMPORTANT AND SHOULD WORK PROPERLY, AS REOCCURING NAMES
        # CAN INTRODUCE A LARGE BIAS IN TEXT ANALYSIS
        names = spoken_content.name.to_list()
        spoken_content.speech_content = spoken_content.speech_content.apply(
            clean_name_headers, args=(names,)
        )

        spoken_content.reset_index(inplace=True, drop=True)

        # Delete all not alphabetical chars, keep "-" as it occurs often in
        # names.
        # Question: Is any other character deleted, which could be in a name?
        # Answer: I don't think so.
        spoken_content.name = spoken_content.name.str.replace(
            r"[^a-zA-ZÖÄÜäöüß\-]", " ", regex=True
        )

        # Replace more than two whitespaces with one.
        spoken_content.name = spoken_content.name.str.replace(r"  +", " ", regex=True)

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
        first_last_titles = spoken_content.name.apply(str.split)

        # Extract title, if it is in the titles list.
        spoken_content.title = [
            [title for title in title_list if title in titles]
            for title_list in first_last_titles
        ]

        # Remove titles from the first_last_name list.
        for politician_titles in first_last_titles:
            for title in politician_titles[:]:
                if title in titles:
                    politician_titles.remove(title)

        # Get the first and last name based on the amount of elements.
        for index, first_last in zip(range(len(first_last_titles)), first_last_titles):
            if len(first_last) == 1:
                spoken_content.first_name.iloc[index] = ""
                spoken_content.last_name.iloc[index] = first_last[0]
            # elif len(first_last) == 2:
            elif len(first_last) >= 2:
                spoken_content.first_name.iloc[index] = first_last[:-1]
                spoken_content.last_name.iloc[index] = first_last[-1]
            else:
                spoken_content.first_name.iloc[index] = "ERROR"
                spoken_content.last_name.iloc[index] = "ERROR"

        # look for parties in the party column and replace them with a
        # standardized party name
        for index, position in zip(spoken_content.index, spoken_content.position_long):
            # if str(party) in ["DBP", "SSW",
            faction_abbrev = get_faction_abbrev(
                str(position), parties_patterns=parties_patterns
            )
            (
                spoken_content.position_short.at[index],
                spoken_content.position_long.at[index],
            ) = get_position_short_and_long(
                faction_abbrev if faction_abbrev else regex.sub("\n+", " ", position)
            )
            if faction_abbrev:
                try:
                    spoken_content.faction_id.at[index] = int(
                        factions.id.loc[factions.abbreviation == faction_abbrev].iloc[0]
                    )
                except IndexError:
                    spoken_content.faction_id.at[index] = -1

        spoken_content.to_pickle(os.path.join(save_path, spoken_content_file))
