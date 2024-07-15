import datetime
import os
import xml.etree.ElementTree as et

import numpy as np
import pandas as pd
import regex

import open_discourse.definitions.path_definitions as path_definitions
from open_discourse.helper_functions.extract_contributions import extract

# input directory
ELECTORAL_TERM_19_20_INPUT = path_definitions.ELECTORAL_TERM_19_20_STAGE_02
FACTIONS = path_definitions.DATA_FINAL
politicians = path_definitions.DATA_FINAL

# output directory
ELECTORAL_TERM_19_20_OUTPUT = path_definitions.ELECTORAL_TERM_19_20_STAGE_03
CONTRIBUTIONS_SIMPLIFIED = path_definitions.CONTRIBUTIONS_SIMPLIFIED

if not os.path.exists(ELECTORAL_TERM_19_20_OUTPUT):
    os.makedirs(ELECTORAL_TERM_19_20_OUTPUT)


if not os.path.exists(CONTRIBUTIONS_SIMPLIFIED):
    os.makedirs(CONTRIBUTIONS_SIMPLIFIED)

faction_patterns = {
    "Bündnis 90/Die Grünen": r"(?:BÜNDNIS\s*(?:90)?/?(?:\s*D[1I]E)?|Bündnis\s*90/(?:\s*D[1I]E)?)?\s*[GC]R[UÜ].?\s*[ÑN]EN?(?:/Bündnis 90)?",  # noqa: E501
    "CDU/CSU": r"(?:Gast|-)?(?:\s*C\s*[DSMU]\s*S?[DU]\s*(?:\s*[/,':!.-]?)*\s*(?:\s*C+\s*[DSs]?\s*[UÙ]?\s*)?)(?:-?Hosp\.|-Gast|1)?",  # noqa: E501
    "BP": r"^BP",
    "DA": r"^DA",
    "DP": r"^DP",
    "DIE LINKE.": r"DIE LINKE",
    "DPB": r"^DPB",
    "DRP": r"DRP(\-Hosp\.)?|^SRP|^DBP",
    "FDP": r"\s*F\.?\s*[PDO][.']?[DP]\.?",
    "Fraktionslos": r"(?:fraktionslos|Parteilos)",
    "FU": r"^FU",
    "FVP": r"^FVP",
    "Gast": r"Gast",
    "GB/BHE": r"(?:GB[/-]\s*)?BHE(?:-DG)?",
    "KPD": r"^KPD",
    "NR": r"^NR$",
    "PDS": r"(?:Gruppe\s*der\s*)?PDS(?:/(?:LL|Linke Liste))?",
    "SPD": r"\s*'?S(?:PD|DP)(?:\.|-Gast)?",
    "SSW": r"^SSW",
    "SRP": r"^SRP",
    "WAV": r"^WAV",
    "Z": r"^Z$",
    "AfD": r"^AfD$",
    "DBP": r"^DBP$",
}


def get_position_short_and_long(position_raw):
    """matches the given position_raw and returns the long and short version"""
    if position_raw in faction_patterns.keys() or regex.match(
        r"^[Bb]erichterstatter(in)?(\s|$|,|.)", position_raw
    ):
        return (
            "Member of Parliament",
            None if position_raw in faction_patterns.keys() else position_raw,
        )
    elif (
        regex.match(r"^[Bb]undestagspräsident(in)?(\s|$|,|.)", position_raw)
        or regex.match(r"^[Aa]lterspräsident(in)?(\s|$|,|.)", position_raw)
        or regex.match(r"^[Vv]izebundestagspräsident(in)?(\s|$|,|.)", position_raw)
        or regex.match(r"^[Ss]chriftführer(in)?(\s|$|,|.)", position_raw)
        or position_raw.lower()
        in [
            "präsidentin",
            "präsident",
            "präsident des deutschen bundestages",
            "präsidentin des deutschen bundestages",
            "vizepräsidentin",
            "vizepräsident",
        ]
    ):
        return "Presidium of Parliament", position_raw
    elif (
        regex.match(r"^[Bb]undespräsident(in)?(\s|$|,|.)", position_raw)
        or regex.match(r"^[Mm]inisterpräsident(in)?(\s|$|,|.)", position_raw)
        or regex.match(r"^[Ss]taatsminister(in)?(\s|$|,|.)", position_raw)
        or regex.match(r"^[Ss]enator(in)?(\s|$|,|.)", position_raw)
        or regex.match(r"^[Pp]räsident(in)?(\s|$|,|.)", position_raw)
        or regex.match(r"^[Gg]ast", position_raw)
    ):
        return "Guest", position_raw
    elif regex.match(r"^[Bb]undeskanzler(in)?(\s|$|,|.)", position_raw):
        return "Chancellor", None
    elif regex.match(r"^(Bundes)?[Mm]inister(in)?(\s|$|,|.)", position_raw):
        return "Minister", position_raw
    elif regex.match(
        r"^([Pp]arl\s*\.\s+)?[Ss]taatssekretär(in)?(\s|$|,|.)", position_raw
    ):
        return "Secretary of State", position_raw
    else:
        return "Not found", None


class Incrementor(object):
    """Incrementor class for iterative regex deletion"""

    def __init__(self):
        self.count = -1

    def increment(self, matchObject):
        self.count += 1
        return "{->" + str(self.count) + "}"


def get_first_last(name):
    first_last = name.split()
    if len(first_last) == 1:
        first_name = ""
        last_name = first_last[0]
    elif len(first_last) >= 2:
        first_name = first_last[:-1]
        last_name = first_last[-1]
    else:
        first_name = "ERROR"
        last_name = "ERROR"
    return " ".join(first_name), last_name


def get_faction_abbrev(faction, faction_patterns):
    """matches the given faction and returns an id"""

    for faction_abbrev, faction_pattern in faction_patterns.items():
        if regex.search(faction_pattern, faction):
            return faction_abbrev
    return None


speech_content_id = 1000000

speech_content = pd.DataFrame(
    {
        "id": [],
        "session": [],
        "first_name": [],
        "last_name": [],
        "faction_id": [],
        "position_short": [],
        "position_long": [],
        "politician_id": [],
        "speech_content": [],
        "date": [],
    }
)

factions = pd.read_pickle(os.path.join(FACTIONS, "factions.pkl"))

politicians = pd.read_csv(os.path.join(politicians, "politicians.csv"))
politicians.last_name = politicians.last_name.str.lower()
politicians.last_name = politicians.last_name.str.replace("ß", "ss", regex=False)
politicians.first_name = politicians.first_name.str.lower()
politicians.first_name = politicians.first_name.str.replace("ß", "ss", regex=False)
politicians.first_name = politicians.first_name.apply(str.split)

for electoral_term_folder in sorted(os.listdir(ELECTORAL_TERM_19_20_INPUT)):
    electoral_term_folder_path = os.path.join(
        ELECTORAL_TERM_19_20_INPUT, electoral_term_folder
    )

    if not os.path.isdir(electoral_term_folder_path):
        continue

    CONTRIBUTIONS_EXTENDED_OUTPUT = os.path.join(
        path_definitions.CONTRIBUTIONS_EXTENDED_STAGE_01, electoral_term_folder
    )

    ELECTORAL_TERM_SPOKEN_CONTENT = os.path.join(
        ELECTORAL_TERM_19_20_OUTPUT, electoral_term_folder, "speech_content"
    )

    CONTRIBUTIONS_SIMPLIFIED_OUTPUT = os.path.join(
        CONTRIBUTIONS_SIMPLIFIED, electoral_term_folder
    )

    if not os.path.exists(CONTRIBUTIONS_EXTENDED_OUTPUT):
        os.makedirs(CONTRIBUTIONS_EXTENDED_OUTPUT)

    if not os.path.exists(ELECTORAL_TERM_SPOKEN_CONTENT):
        os.makedirs(ELECTORAL_TERM_SPOKEN_CONTENT)

    if not os.path.exists(CONTRIBUTIONS_SIMPLIFIED_OUTPUT):
        os.makedirs(CONTRIBUTIONS_SIMPLIFIED_OUTPUT)

    speech_records = []

    contributions_simplified = pd.DataFrame(
        {"text_position": [], "content": [], "speech_id": []}
    )

    politicians_electoral_term = politicians.loc[
        politicians.electoral_term == int(electoral_term_folder[-2:])
    ]

    for session in sorted(os.listdir(electoral_term_folder_path)):
        if session == ".DS_Store":
            continue

        contributions_extended = pd.DataFrame(
            {
                "id": [],
                "type": [],
                "name": [],
                "faction": [],
                "constituency": [],
                "content": [],
                "text_position": [],
            }
        )

        print(session)

        session_content = et.parse(
            os.path.join(electoral_term_folder_path, session, "session_content.xml")
        )

        meta_data = et.parse(
            os.path.join(electoral_term_folder_path, session, "meta_data.xml")
        )

        date = meta_data.getroot().get("sitzung-datum")
        # Wrong date in xml file. Fixing manually
        if session == "19158":
            date = "07.05.2020"
        date = (
            datetime.datetime.strptime(date, "%d.%m.%Y") - datetime.datetime(1970, 1, 1)
        ).total_seconds()

        root = session_content.getroot()

        tops = root.findall("tagesordnungspunkt")

        c = Incrementor()
        id_Counter = 0

        for top in tops:
            speeches = top.findall("rede")
            for speech in speeches:
                speaker = speech[0].find("redner")
                try:
                    speaker_id = int(speaker.get("id"))
                except (ValueError, AttributeError):
                    speaker_id = -1

                try:
                    name = speaker.find("name")
                except AttributeError:
                    continue

                try:
                    first_name = name.find("vorname").text
                except AttributeError:
                    first_name = ""

                try:
                    last_name = name.find("nachname").text
                except AttributeError:
                    last_name = ""

                try:
                    position_raw = name.find("fraktion").text
                except (ValueError, AttributeError):
                    position_raw = name.find("rolle").find("rolle_lang").text
                faction_abbrev = get_faction_abbrev(
                    str(position_raw), faction_patterns=faction_patterns
                )
                position_short, position_long = get_position_short_and_long(
                    faction_abbrev
                    if faction_abbrev
                    else regex.sub("\n+", " ", position_raw)
                )
                faction_id = -1
                if faction_abbrev:
                    # .iloc[0] is important right now, as some faction entries
                    # in factions df share same faction_id, so always the first
                    # one is chosen right now.
                    faction_id = int(
                        factions.id.loc[factions.abbreviation == faction_abbrev].iloc[0]
                    )

                speech_text = ""
                text_position = 0
                for content in speech[1:]:
                    tag = content.tag
                    if tag == "name":
                        speech_records.append(
                            {
                                "id": speech_content_id,
                                "session": session,
                                "first_name": first_name,
                                "last_name": last_name,
                                "faction_id": faction_id,
                                "position_short": position_short,
                                "position_long": position_long,
                                "politician_id": speaker_id,
                                "speech_content": speech_text,
                                "date": date,
                            }
                        )
                        speech_content_id += 1
                        faction_id = -1
                        speaker_id = -1
                        name = regex.sub(":", "", content.text).split()
                        first_name, last_name = get_first_last(" ".join(name[1:]))
                        position_short, position_long = get_position_short_and_long(
                            name[0]
                        )
                        possible_matches = politicians_electoral_term.loc[
                            politicians_electoral_term.last_name == last_name.lower()
                        ]
                        length = len(np.unique(possible_matches["ui"]))
                        if length == 1:
                            speaker_id = int(possible_matches["ui"].iloc[0])
                        elif length > 1:
                            first_name_set = set(
                                [x.lower() for x in first_name.split()]
                            )
                            possible_matches = possible_matches.loc[
                                ~possible_matches.first_name.apply(
                                    lambda x: set(x).isdisjoint(first_name_set)
                                )
                            ]
                            length = len(np.unique(possible_matches["ui"]))
                            if length == 1:
                                speaker_id = int(possible_matches["ui"].iloc[0])
                        speech_text = ""
                        text_position = 0
                    elif tag == "p" and content.get("klasse") == "redner":
                        speech_records.append(
                            {
                                "id": speech_content_id,
                                "session": session,
                                "first_name": first_name,
                                "last_name": last_name,
                                "faction_id": faction_id,
                                "position_short": position_short,
                                "position_long": position_long,
                                "politician_id": speaker_id,
                                "speech_content": speech_text,
                                "date": date,
                            }
                        )

                        speech_content_id += 1
                        speech_text = ""
                        text_position = 0
                        speaker = content.find("redner")
                        speaker_id = int(speaker.get("id"))
                        possible_matches = politicians_electoral_term.loc[
                            politicians_electoral_term.ui == speaker_id
                        ]
                        if len(possible_matches) == 0:
                            speaker_id = -1
                        name = speaker.find("name")
                        try:
                            first_name = name.find("vorname").text
                            last_name = name.find("nachname").text
                        except AttributeError:
                            try:
                                first_name, last_name = get_first_last(speech[0].text)
                            except AttributeError:
                                first_name = "ERROR"
                                last_name = "ERROR"
                        try:
                            position_raw = name.find("fraktion").text
                        except (ValueError, AttributeError):
                            position_raw = name.find("rolle").find("rolle_lang").text
                        faction_abbrev = get_faction_abbrev(
                            str(position_raw), faction_patterns=faction_patterns
                        )

                        faction_id = -1
                        position_short, position_long = get_position_short_and_long(
                            faction_abbrev
                            if faction_abbrev
                            else regex.sub("\n+", " ", position_raw)
                        )
                        if faction_abbrev:
                            faction = faction_abbrev
                            # .iloc[0] is important right now, as some faction entries
                            # in factions df share same faction_id, so always the first
                            # one is chosen right now.
                            faction_id = int(
                                factions.id.loc[
                                    factions.abbreviation == faction_abbrev
                                ].iloc[0]
                            )
                    elif tag == "p":
                        try:
                            speech_text += "\n\n" + content.text
                        except TypeError:
                            pass
                    elif tag == "kommentar":
                        (
                            contributions_extended_frame,
                            speech_replaced,
                            contributions_simplified_frame,
                            text_position,
                        ) = extract(
                            content.text,
                            int(session),
                            speech_content_id,
                            text_position,
                            False,
                        )
                        speech_text += "\n\n" + speech_replaced
                        contributions_extended = pd.concat(
                            [contributions_extended, contributions_extended_frame],
                            sort=False,
                        )
                        contributions_simplified = pd.concat(
                            [contributions_simplified, contributions_simplified_frame],
                            sort=False,
                        )

                speech_records.append(
                    {
                        "id": speech_content_id,
                        "session": session,
                        "first_name": first_name,
                        "last_name": last_name,
                        "faction_id": faction_id,
                        "position_short": position_short,
                        "position_long": position_long,
                        "politician_id": speaker_id,
                        "speech_content": speech_text,
                        "date": date,
                    }
                )
                speech_content_id += 1

        contributions_extended.to_pickle(
            os.path.join(CONTRIBUTIONS_EXTENDED_OUTPUT, session + ".pkl")
        )

    speech_content = pd.DataFrame.from_records(speech_records)

    speech_content.to_pickle(
        os.path.join(ELECTORAL_TERM_SPOKEN_CONTENT, "speech_content.pkl")
    )

    contributions_simplified.to_pickle(
        os.path.join(
            CONTRIBUTIONS_SIMPLIFIED_OUTPUT,
            "contributions_simplified.pkl",
        )
    )
