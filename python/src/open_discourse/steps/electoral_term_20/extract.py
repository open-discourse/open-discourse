import datetime
import xml.etree.ElementTree as et

import numpy as np
import pandas as pd
import regex
from tqdm import tqdm

from open_discourse.definitions import path, pattern
from open_discourse.helper.extract_contributions import extract

# input directory
ELECTORAL_TERM_20_INPUT = path.DATA_CACHE / "electoral_term_pp20" / "stage_02"
FACTIONS = path.DATA_FINAL
POLITICIANS = path.DATA_FINAL

# output directory
ELECTORAL_TERM_20_OUTPUT = path.DATA_CACHE / "electoral_term_pp20" / "stage_03"
CONTRIBUTIONS_SIMPLIFIED = path.CONTRIBUTIONS_SIMPLIFIED
CONTRIBUTIONS_EXTENDED = path.CONTRIBUTIONS_EXTENDED_STAGE_01

ELECTORAL_TERM_20_OUTPUT.mkdir(parents=True, exist_ok=True)
CONTRIBUTIONS_SIMPLIFIED.mkdir(parents=True, exist_ok=True)
CONTRIBUTIONS_EXTENDED.mkdir(parents=True, exist_ok=True)


def main(task):
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

    factions = pd.read_pickle(FACTIONS / "factions.pkl")

    politicians = pd.read_csv(POLITICIANS / "politicians.csv")
    politicians["last_name"] = politicians["last_name"].str.lower()
    politicians["last_name"] = politicians["last_name"].str.replace(
        "ß", "ss", regex=False
    )
    politicians["first_name"] = politicians["first_name"].str.lower()
    politicians["first_name"] = politicians["first_name"].str.replace(
        "ß", "ss", regex=False
    )
    politicians["first_name"] = politicians["first_name"].apply(str.split)

    term_spoken_content = ELECTORAL_TERM_20_OUTPUT / "speech_content"
    contributions_extended_output = CONTRIBUTIONS_EXTENDED / "electoral_term_pp20"
    contributions_simplified_output = CONTRIBUTIONS_SIMPLIFIED / "electoral_term_pp20"

    contributions_extended_output.mkdir(parents=True, exist_ok=True)
    term_spoken_content.mkdir(parents=True, exist_ok=True)
    contributions_simplified_output.mkdir(parents=True, exist_ok=True)

    speech_records = []

    contributions_simplified = []

    politicians_electoral_term = politicians.loc[politicians["electoral_term"] == "20"]

    for session_path in tqdm(
        ELECTORAL_TERM_20_INPUT.iterdir(),
        desc="Extract speeches (term 20)...",
    ):
        if not session_path.is_dir():
            continue

        contributions_extended = []

        session_content = et.parse(session_path / "session_content.xml")
        meta_data = et.parse(session_path / "meta_data.xml")

        date = meta_data.getroot().get("sitzung-datum")
        # Wrong date in xml file. Fixing manually
        if session_path.stem == "19158":
            date = "07.05.2020"
        date = (
            datetime.datetime.strptime(date, "%d.%m.%Y") - datetime.datetime(1970, 1, 1)
        ).total_seconds()

        root = session_content.getroot()

        tops = root.findall("tagesordnungspunkt")

        for top in tops:
            speeches = top.findall("rede")
            for speech in speeches:
                speaker = speech[0].find("redner")
                if speaker is None:
                    continue
                try:
                    speaker_id = int(speaker.get("id"))
                except (ValueError, AttributeError):
                    speaker_id = -1
                name = speaker.find("name")
                first_name = find_with_default(name, "vorname", "")
                last_name = find_with_default(name, "nachname", "")

                position_raw = name.find("fraktion")
                if position_raw is None:
                    position_raw = name.find("rolle")
                    if position_raw is not None:
                        position_raw = find_with_default(position_raw, "rolle_lang", "")
                    else:
                        position_raw = ""
                else:
                    position_raw = ""

                faction_abbrev = get_faction_abbrev(str(position_raw))
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
                        factions.loc[
                            factions["abbreviation"] == faction_abbrev, "id"
                        ].iloc[0]
                    )

                speech_text = ""
                text_position = 0
                for content in speech[1:]:
                    tag = content.tag
                    if tag == "name":
                        speech_records.append(
                            {
                                "id": speech_content_id,
                                "session": session_path.stem,
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
                            politicians_electoral_term["last_name"] == last_name.lower()
                        ]
                        length = len(np.unique(possible_matches["ui"]))
                        if length == 1:
                            speaker_id = int(possible_matches["ui"].iloc[0])
                        elif length > 1:
                            first_name_set = set(
                                [x.lower() for x in first_name.split()]
                            )
                            possible_matches = possible_matches.loc[
                                ~possible_matches["first_name"].apply(
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
                                "session": session_path.stem,
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
                            politicians_electoral_term["ui"] == speaker_id
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
                        faction_abbrev = get_faction_abbrev(str(position_raw))

                        faction_id = -1
                        position_short, position_long = get_position_short_and_long(
                            faction_abbrev
                            if faction_abbrev
                            else regex.sub("\n+", " ", position_raw)
                        )
                        if faction_abbrev:
                            # .iloc[0] is important right now, as some faction entries
                            # in factions df share same faction_id, so always the first
                            # one is chosen right now.
                            faction_id = int(
                                factions.loc[
                                    factions["abbreviation"] == faction_abbrev, "id"
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
                            int(session_path.stem),
                            speech_content_id,
                            text_position,
                            False,
                        )
                        speech_text += "\n\n" + speech_replaced
                        contributions_extended.append(contributions_extended_frame)
                        contributions_simplified.append(contributions_simplified_frame)

                speech_records.append(
                    {
                        "id": speech_content_id,
                        "session": session_path.stem,
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

        contributions_extended = pd.concat(contributions_extended, sort=False)
        contributions_extended.to_pickle(
            contributions_extended_output / (session_path.stem + ".pkl")
        )

    speech_content = pd.DataFrame.from_records(speech_records)

    speech_content.to_pickle(term_spoken_content / "speech_content.pkl")

    contributions_simplified = pd.concat(contributions_simplified, sort=False)
    contributions_simplified.to_pickle(
        contributions_simplified_output / "contributions_simplified.pkl"
    )

    return True


def get_position_short_and_long(position_raw):
    """matches the given position_raw and returns the long and short version"""
    if position_raw in pattern.FACTIONS.keys() or regex.match(
        r"^[Bb]erichterstatter(in)?(\s|$|,|.)", position_raw
    ):
        return (
            "Member of Parliament",
            None if position_raw in pattern.FACTIONS.keys() else position_raw,
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


def find_with_default(node, key, default):
    result = node.find(key)
    return default if result is None else result.text


def get_faction_abbrev(faction):
    """matches the given faction and returns an id"""

    for faction_abbrev, faction_pattern in pattern.FACTIONS.items():
        if regex.search(faction_pattern, faction):
            return faction_abbrev
    return None


if __name__ == "__main__":
    main(None)
