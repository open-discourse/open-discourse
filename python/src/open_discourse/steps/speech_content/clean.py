import sys

import numpy as np
import pandas as pd
import regex
from tqdm import tqdm

from open_discourse.definitions import path
from open_discourse.helper.clean_text import clean_name_headers

# input directory
SPEECH_CONTENT_INPUT = path.SPEECH_CONTENT_STAGE_01
FACTIONS = path.DATA_FINAL

# output directory
SPEECH_CONTENT_OUTPUT = path.SPEECH_CONTENT_STAGE_02

factions = pd.read_pickle(FACTIONS / "factions.pkl")

faction_patterns = {
    "Bündnis 90/Die Grünen": regex.compile(
        "(?:BÜNDNIS\s*(?:90)?/?(?:\s*D[1I]E)?|Bündnis\s*90/(?:\s*D[1I]E)?)?\s*[GC]R[UÜ].?\s*[ÑN]EN?(?:/Bündnis 90)?|Bündnis 90/Die Grünen"
    ),
    "CDU/CSU": regex.compile(
        "(?:Gast|-)?(?:\s*C\s*[DSMU]\s*S?[DU]\s*(?:\s*[/,':!.-]?)*\s*(?:\s*C+\s*[DSs]?\s*[UÙ]?\s*)?)(?:-?Hosp\.|-Gast|1)?"
    ),
    "BP": regex.compile("^BP"),
    "DA": regex.compile("^DA"),
    "DP": regex.compile("^DP"),
    "DIE LINKE.": regex.compile("DIE LINKE"),
    "DPB": regex.compile("(?:^DPB)"),
    "DRP": regex.compile("DRP(\-Hosp\.)?|SRP"),
    "FDP": regex.compile("\s*F\.?\s*[PDO][.']?[DP]\.?"),
    "Fraktionslos": regex.compile("(?:fraktionslos|Parteilos|parteilos)"),
    "FU": regex.compile("^FU"),
    "FVP": regex.compile("^FVP"),
    "Gast": regex.compile("Gast"),
    "GB/BHE": regex.compile("(?:GB[/-]\s*)?BHE(?:-DG)?"),
    "KPD": regex.compile("^KPD"),
    "PDS": regex.compile("(?:Gruppe\s*der\s*)?PDS(?:/(?:LL|Linke Liste))?"),
    "SPD": regex.compile("\s*'?S(?:PD|DP)(?:\.|-Gast)?"),
    "SSW": regex.compile("^SSW"),
    "SRP": regex.compile("^SRP"),
    "WAV": regex.compile("^WAV"),
    "Z": regex.compile("^Z$"),
    "DBP": regex.compile("^DBP$"),
    "NR": regex.compile("^NR$"),
}


def get_faction_abbrev(faction, faction_patterns: dict[str, regex.Pattern]):
    """matches the given faction and returns an id"""

    for faction_abbrev, faction_pattern in faction_patterns.items():
        if faction_pattern.search(faction):
            return faction_abbrev
    return None


def get_position_short_and_long(position):
    """matches the given position and returns the long and short version"""
    if position in faction_patterns.keys() or regex.match(r"^[Bb]erichterstatter(in)?(\s|$|,|.)", position):
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
for folder_path in sorted(SPEECH_CONTENT_INPUT.iterdir()):
    if not folder_path.is_dir():
        continue

    term_number = regex.search(r"(?<=electoral_term_pp)\d{2}", folder_path.stem)
    if term_number is None:
        continue
    term_number = int(term_number.group(0))

    if len(sys.argv) > 1:
        if str(term_number) not in sys.argv:
            continue

    save_path = SPEECH_CONTENT_OUTPUT / folder_path.stem
    save_path.mkdir(parents=True, exist_ok=True)

    # iterate over every speech_content file
    for speech_content_file in tqdm(
        folder_path.glob("*.pkl"),
        desc=f"Clean speeches (term {term_number:>2})...",
    ):
        # read the spoken content csv
        speech_content = pd.read_pickle(speech_content_file)

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
        names = speech_content["name_raw"].to_list()
        speech_content["speech_content"] = speech_content["speech_content"].apply(
            clean_name_headers, args=(np.unique(names),)
        )

        speech_content.reset_index(inplace=True, drop=True)

        # Delete all not alphabetical chars, keep "-" as it occurs often in
        # names.
        # Question: Is any other character deleted, which could be in a name?
        # Answer: I don't think so.
        speech_content["name_raw"] = speech_content["name_raw"].str.replace(r"[^a-zA-ZÖÄÜäöüß\-]", " ", regex=True)

        # Replace more than two whitespaces with one.
        speech_content["name_raw"] = speech_content["name_raw"].str.replace(r"  +", " ", regex=True)

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
        first_last_titles = speech_content["name_raw"].apply(str.split)

        # Extract acad_title, if it is in the titles list.
        speech_content["acad_title"] = [
            [acad_title for acad_title in title_list if acad_title in titles] for title_list in first_last_titles
        ]

        # Remove titles from the first_last_name list.
        for politician_titles in first_last_titles:
            for acad_title in politician_titles[:]:
                if acad_title in titles:
                    politician_titles.remove(acad_title)

        # Get the first and last name based on the amount of elements.
        for index, first_last in first_last_titles.items():
            if len(first_last) == 1:
                speech_content.at[index, "first_name"] = ""
                speech_content.at[index, "last_name"] = first_last[0]
            elif len(first_last) >= 2:
                speech_content.at[index, "first_name"] = first_last[:-1]
                speech_content.at[index, "last_name"] = first_last[-1]
            else:
                speech_content.at[index, "first_name"] = "ERROR"
                speech_content.at[index, "last_name"] = "ERROR"

        # look for factions in the faction column and replace them with a
        # standardized faction name
        for index, position_raw in speech_content["position_raw"].items():
            faction_abbrev = get_faction_abbrev(str(position_raw), faction_patterns)
            (
                speech_content.at[index, "position_short"],
                speech_content.at[index, "position_long"],
            ) = get_position_short_and_long(faction_abbrev if faction_abbrev else regex.sub("\n+", " ", position_raw))
            if faction_abbrev:
                try:
                    speech_content.at[index, "faction_id"] = int(
                        factions.loc[factions["abbreviation"] == faction_abbrev, "id"].iloc[0]
                    )
                except IndexError:
                    speech_content.at[index, "faction_id"] = -1

        speech_content = speech_content.drop(columns=["position_raw", "name_raw"])
        speech_content.to_pickle(save_path / speech_content_file.name)

assert len(list(SPEECH_CONTENT_INPUT.glob("*_pp*"))) == len(list(SPEECH_CONTENT_OUTPUT.glob("*_pp*")))

print("Script 05_02 done.")
