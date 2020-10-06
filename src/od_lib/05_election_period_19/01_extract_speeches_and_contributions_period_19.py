import pandas as pd
import numpy as np
import xml.etree.ElementTree as et
import regex
import os
import sys
import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))
from src.helper_functions.extract_contributions import extract
import path_definitions


# input directory ______________________________________________________________
WP_19_INPUT = path_definitions.WP_19_STAGE_02
FACTIONS = path_definitions.DATA_FINAL
PEOPLE = path_definitions.DATA_FINAL

# output directory _____________________________________________________________
WP_19_OUTPUT = path_definitions.WP_19_STAGE_03
CONTRIBUTIONS_OUTPUT = os.path.join(path_definitions.CONTRIBUTIONS_STAGE_01, "wp_19")
WP_19_SPOKEN_CONTENT = os.path.join(WP_19_OUTPUT, "spoken_content")
MISCELLANEOUS_OUTPUT = os.path.join(
    path_definitions.CONTRIBUTIONS_MISCELLANEOUS_STAGE_01, "wp_19"
)
TEXT_POSITION_X_TEXT = path_definitions.TEXT_POSITION_X_TEXT

if not os.path.exists(WP_19_OUTPUT):
    os.makedirs(WP_19_SPOKEN_CONTENT)

# Contributions are saved to the normale contributions folder not the seperate wp_19 folders
if not os.path.exists(CONTRIBUTIONS_OUTPUT):
    os.makedirs(CONTRIBUTIONS_OUTPUT)

if not os.path.exists(MISCELLANEOUS_OUTPUT):
    os.makedirs(MISCELLANEOUS_OUTPUT)

if not os.path.exists(TEXT_POSITION_X_TEXT):
    os.makedirs(TEXT_POSITION_X_TEXT)

text_position_x_text = pd.DataFrame(
    {"text_position": [], "deleted_text": [], "speech_id": []}
)

parties_patterns = {
    "Bündnis 90/Die Grünen": r"(?:BÜNDNIS\s*(?:90)?/?(?:\s*D[1I]E)?|Bündnis\s*90/(?:\s*D[1I]E)?)?\s*[GC]R[UÜ].?\s*[ÑN]EN?(?:/Bündnis 90)?",
    "CDU/CSU": r"(?:Gast|-)?(?:\s*C\s*[DSMU]\s*S?[DU]\s*(?:\s*[/,':!.-]?)*\s*(?:\s*C+\s*[DSs]?\s*[UÙ]?\s*)?)(?:-?Hosp\.|-Gast|1)?",
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
    "NR": r"^NR",
    "PDS": r"(?:Gruppe\s*der\s*)?PDS(?:/(?:LL|Linke Liste))?",
    "SPD": "\s*'?S(?:PD|DP)(?:\.|-Gast)?",
    "SSW": r"^SSW",
    "SRP": r"^SRP",
    "WAV": r"^WAV",
    "Z": r"^Z$",
    "AfD": r"^AfD$",
    "DBP": r"^DBP$",
    "NR": r"^NR$",
}


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


def get_faction_abbrev(party, parties_patterns):
    """matches the given party and returns an id"""

    for party_abbrev, party_pattern in parties_patterns.items():
        if regex.search(party_pattern, party):
            return party_abbrev
    return None


spoken_content_id = 1000000

spoken_content = pd.DataFrame(
    {
        "id": [],
        "sitting": [],
        "first_name": [],
        "last_name": [],
        "faction_id": [],
        "position_short": [],
        "position_long": [],
        "people_id": [],
        "speech_content": [],
        "date": [],
    }
)

factions = pd.read_pickle(os.path.join(FACTIONS, "factions.pkl"))

people = pd.read_csv(os.path.join(PEOPLE, "people.csv"))
people = people.loc[people.wp_period == 19]
people.last_name = people.last_name.str.lower()
people.last_name = people.last_name.str.replace("ß", "ss", regex=False)
people.first_name = people.first_name.str.lower()
people.first_name = people.first_name.str.replace("ß", "ss", regex=False)
people.first_name = people.first_name.apply(str.split)

for sitting in sorted(os.listdir(WP_19_INPUT)):

    if sitting == ".DS_Store":
        continue

    contributions = pd.DataFrame(
        {"id": [], "type": [], "name": [], "party": [], "content": [], "position": []}
    )

    miscellaneous = pd.DataFrame(
        {"id": [], "type": [], "name": [], "party": [], "content": [], "position": []}
    )

    print(sitting)

    sitzungsverlauf = et.parse(
        os.path.join(WP_19_INPUT, sitting, "sitzungsverlauf.xml")
    )

    rednerliste = et.parse(os.path.join(WP_19_INPUT, sitting, "rednerliste.xml"))

    date = rednerliste.getroot().get("sitzung-datum")
    # Wrong date in xml file. Fixing manually
    if sitting == "19158":
        date = "07.05.2020"
    date = (
        datetime.datetime.strptime(date, "%d.%m.%Y") - datetime.datetime(1970, 1, 1)
    ).total_seconds()

    root = sitzungsverlauf.getroot()

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
                position = name.find("fraktion").text
            except (ValueError, AttributeError):
                position = name.find("rolle").find("rolle_lang").text
            faction_abbrev = get_faction_abbrev(
                str(position), parties_patterns=parties_patterns
            )
            position_short, position_long = get_position_short_and_long(
                faction_abbrev if faction_abbrev else regex.sub("\n+", " ", position)
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

            for speech_content in speech[1:]:
                text_position = 0
                tag = speech_content.tag
                if tag == "name":
                    speech_series = pd.Series(
                        {
                            "id": spoken_content_id,
                            "sitting": sitting,
                            "first_name": first_name,
                            "last_name": last_name,
                            "faction_id": faction_id,
                            "position_short": position_short,
                            "position_long": position_long,
                            "people_id": speaker_id,
                            "speech_content": speech_text,
                            "date": date,
                        }
                    )
                    spoken_content = spoken_content.append(
                        speech_series, ignore_index=True
                    )
                    spoken_content_id += 1
                    faction_id = -1
                    speaker_id = -1
                    name = regex.sub(":", "", speech_content.text).split()
                    first_name, last_name = get_first_last(" ".join(name[1:]))
                    position_short, position_long = get_position_short_and_long(name[0])
                    possible_matches = people.loc[people.last_name == last_name.lower()]
                    length = len(np.unique(possible_matches["ui"]))
                    if length == 1:
                        speaker_id = int(possible_matches["ui"].iloc[0])
                    elif length > 1:
                        first_name_set = set([x.lower() for x in first_name.split()])
                        possible_matches = possible_matches.loc[
                            ~possible_matches.first_name.apply(
                                lambda x: set(x).isdisjoint(first_name_set)
                            )
                        ]
                        length = len(np.unique(possible_matches["ui"]))
                        if length == 1:
                            speaker_id = int(possible_matches["ui"].iloc[0])
                    speech_text = ""
                elif tag == "p" and speech_content.get("klasse") == "redner":
                    speech_series = pd.Series(
                        {
                            "id": spoken_content_id,
                            "sitting": sitting,
                            "first_name": first_name,
                            "last_name": last_name,
                            "faction_id": faction_id,
                            "position_short": position_short,
                            "position_long": position_long,
                            "people_id": speaker_id,
                            "speech_content": speech_text,
                            "date": date,
                        }
                    )
                    spoken_content = spoken_content.append(
                        speech_series, ignore_index=True
                    )
                    spoken_content_id += 1
                    speech_text = ""
                    speaker = speech_content.find("redner")
                    speaker_id = int(speaker.get("id"))
                    possible_matches = people.loc[people.ui == speaker_id]
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
                        position = name.find("fraktion").text
                    except (ValueError, AttributeError):
                        position = name.find("rolle").find("rolle_lang").text
                    faction_abbrev = get_faction_abbrev(
                        str(position), parties_patterns=parties_patterns
                    )

                    faction_id = -1
                    position_short, position_long = get_position_short_and_long(
                        faction_abbrev
                        if faction_abbrev
                        else regex.sub("\n+", " ", position)
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
                        speech_text += speech_content.text
                    except TypeError:
                        pass
                elif tag == "kommentar":
                    (
                        contribtuions_frame,
                        miscellaneous_frame,
                        speech_replaced,
                        text_position_x_text_frame,
                        text_position,
                    ) = extract(
                        speech_content.text,
                        int(sitting),
                        spoken_content_id,
                        text_position,
                    )
                    speech_text += speech_replaced
                    contributions = pd.concat([contributions, contribtuions_frame], sort=False)
                    miscellaneous = pd.concat([miscellaneous, miscellaneous_frame], sort=False)
                    text_position_x_text = pd.concat(
                        [text_position_x_text, text_position_x_text_frame], sort=False
                    )

            speech_series = pd.Series(
                {
                    "id": spoken_content_id,
                    "sitting": sitting,
                    "first_name": first_name,
                    "last_name": last_name,
                    "faction_id": faction_id,
                    "position_short": position_short,
                    "position_long": position_long,
                    "people_id": speaker_id,
                    "speech_content": speech_text,
                    "date": date,
                }
            )
            spoken_content = spoken_content.append(speech_series, ignore_index=True)
            spoken_content_id += 1

    contributions.to_pickle(os.path.join(CONTRIBUTIONS_OUTPUT, sitting + ".pkl"))

    miscellaneous.to_pickle(os.path.join(MISCELLANEOUS_OUTPUT, sitting + ".pkl"))

spoken_content.to_pickle(os.path.join(WP_19_SPOKEN_CONTENT, "spoken_content.pkl"))

text_position_x_text.to_pickle(
    os.path.join(TEXT_POSITION_X_TEXT, "text_position_x_text_wp_19.pkl")
)
