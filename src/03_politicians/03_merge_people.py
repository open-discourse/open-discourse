import pandas as pd
import regex
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))
import path_definitions

print("Start merging people...")

# input ________________________________________________________________________
GOV_MEMBERS = path_definitions.POLITICIANS_STAGE_01
MDBS = path_definitions.POLITICIANS_STAGE_02
FACTIONS = path_definitions.DATA_FINAL

mdbs = pd.read_pickle(os.path.join(MDBS, "mdbs.pkl"))
gov_members = pd.read_pickle(os.path.join(GOV_MEMBERS, "government_members.pkl"))
factions = pd.read_pickle(os.path.join(FACTIONS, "factions.pkl"))

# output _______________________________________________________________________
DATA_FINAL = path_definitions.DATA_FINAL
if not os.path.exists(DATA_FINAL):
    os.makedirs(DATA_FINAL)

# helper functions _____________________________________________________________
wps_dict = {
    "from": [
        1949,
        1953,
        1957,
        1961,
        1965,
        1969,
        1972,
        1976,
        1980,
        1983,
        1987,
        1990,
        1994,
        1998,
        2002,
        2005,
        2009,
        2013,
        2017,
    ],
    "until": [
        1953,
        1957,
        1961,
        1965,
        1969,
        1972,
        1976,
        1980,
        1983,
        1987,
        1990,
        1994,
        1998,
        2002,
        2005,
        2009,
        2013,
        2017,
        -1,
    ],
}

parties_patterns = {
    "Bündnis 90/Die Grünen": r"(?:BÜNDNIS\s*(?:90)?/?(?:\s*D[1I]E)?|Bündnis\s*90/(?:\s*D[1I]E)?)?\s*[GC]R[UÜ].?\s*[ÑN]EN?(?:/Bündnis 90)?|Bündnis 90/Die Grünen",
    "CDU/CSU": r"(?:Gast|-)?(?:\s*C\s*[DSMU]\s*S?[DU]\s*(?:\s*[/,':!.-]?)*\s*(?:\s*C+\s*[DSs]?\s*[UÙ]?\s*)?)(?:-?Hosp\.|-Gast|1)?",
    "BP": r"^BP",
    "DA": r"^DA",
    "DP": r"^DP",
    "DIE LINKE.": r"DIE LINKE",
    "DPB": r"(?:^DPB)",
    "DRP": r"DRP(\-Hosp\.)?|SRP",
    "FDP": "\s*F\.?\s*[PDO][.']?[DP]\.?",
    "Fraktionslos": r"(?:fraktionslos|Parteilos|parteilos)",
    "FU": r"^FU",
    "FVP": r"^FVP",
    "Gast": r"Gast",
    "GB/BHE": r"(?:GB[/-]\s*)?BHE(?:-DG)?",
    "KPD": r"^KPD",
    "PDS": r"(?:Gruppe\s*der\s*)?PDS(?:/(?:LL|Linke Liste))?",
    "SPD": "\s*'?S(?:PD|DP)(?:\.|-Gast)?",
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


def get_wp(from_year=None, to_year=None):
    if not from_year and not to_year:
        raise AttributeError()
    elif not from_year:
        if to_year in wps_dict["until"]:
            return wps_dict["until"].index(to_year) + 1
        else:
            if to_year > 2017:
                return 19
            for counter, year in enumerate(wps_dict["until"]):
                if year > to_year:
                    return counter + 1
            raise ValueError()
    elif not to_year:
        if from_year in wps_dict["from"]:
            return wps_dict["from"].index(from_year) + 1
        else:
            if from_year > 2017:
                return 19
            for counter, year in enumerate(wps_dict["from"]):
                if year > from_year:
                    return counter
            raise ValueError()
    else:
        from_year = get_wp(from_year=from_year, to_year=None)
        to_year = get_wp(from_year=None, to_year=to_year)
        if from_year != to_year:
            return list(range(from_year, to_year + 1))
        else:
            return [from_year]


i = 0
failure_counter = 0
people = mdbs.copy()
people.first_name = people.first_name.str.replace("-", " ", regex=False)

print("Started merging...")

# merging for gov_members
for (
    last_name,
    first_name,
    birth_year,
    death_year,
    position,
    position_from,
    position_until,
    party,
) in zip(
    gov_members.last_name,
    gov_members.first_name,
    gov_members.birth_year,
    gov_members.death_year,
    gov_members.position,
    gov_members.position_from,
    gov_members.position_until,
    gov_members.party,
):

    # Hardcode special cases
    if last_name == "Fischer" and first_name[0] == "Joschka":
        first_name = ["Joseph"]
    elif last_name == "Waigel" and first_name[0] == "Theo":
        first_name = ["Theodor"]
    elif last_name == "Baum" and first_name[0] == "Gerhart":
        first_name = ["Gerhart Rudolf"]
    elif last_name == "Heinemann" and first_name[0] == "Gustav":
        first_name = ["Gustav W."]
    elif last_name == "Lehr" and first_name[0] == "Ursula":
        first_name = ["Ursula Maria"]
    elif last_name == "Möllemann" and first_name[0] == "Jürgen":
        first_name = ["Jürgen W."]
    elif last_name == "Kinkel" and first_name[0] == "Klaus":
        party = "FDP"

    faction_abbrev = get_faction_abbrev(party, parties_patterns)

    if faction_abbrev:
        party_match = int(
            factions.id.loc[factions.abbreviation == faction_abbrev].iloc[0]
        )
    else:
        party_match = -1

    first_name = [regex.sub("-", " ", name) for name in first_name]

    wp_to_be_changed = -1
    wps = get_wp(from_year=int(position_from), to_year=int(position_until))
    try:
        possible_matches = people.loc[
            (people.last_name == last_name)
            & (people.first_name.str.contains(first_name[0]))
            & (people.birth_year.str.contains(str(birth_year)))
        ]
    except:
        pass

    possible_matches = possible_matches.drop_duplicates(subset="ui", keep="first")

    if len(possible_matches) == 1:
        for wp in wps:
            series = {
                "ui": possible_matches.ui.iloc[0],
                "wp_period": wp,
                "faction_id": party_match,
                "first_name": possible_matches.first_name.iloc[0],
                "last_name": possible_matches.last_name.iloc[0],
                "birth_place": possible_matches.birth_place.iloc[0],
                "birth_country": possible_matches.birth_country.iloc[0],
                "birth_year": possible_matches.birth_year.iloc[0],
                "death_year": possible_matches.death_year.iloc[0],
                "gender": possible_matches.gender.iloc[0],
                "profession": possible_matches.profession.iloc[0],
                "location_information": possible_matches.location_information.iloc[0],
                "aristocracy": possible_matches.aristocracy.iloc[0],
                "prefix": possible_matches.prefix.iloc[0],
                "academic_title": possible_matches.academic_title.iloc[0],
                "salutation": possible_matches.salutation.iloc[0],
                "vita_short": possible_matches.vita_short.iloc[0],
                "disclosure_requirement": possible_matches.disclosure_requirement.iloc[
                    0
                ],
                "electoral_district_number": possible_matches.electoral_district_number.iloc[
                    0
                ],
                "electoral_district_name": possible_matches.electoral_district_name.iloc[
                    0
                ],
                "electoral_list": possible_matches.electoral_list.iloc[0],
                "mdb_from": possible_matches.mdb_from.iloc[0],
                "mdb_until": possible_matches.mdb_until.iloc[0],
                "history_from": possible_matches.history_from.iloc[0],
                "history_until": possible_matches.history_until.iloc[0],
                "institution_type": "Regierungsmitglied",
                "institution_name": position,
                "institution_member_from": position_from,
                "institution_member_until": position_until,
                "function_long": position,
                "function_from": "",
                "function_until": "",
            }
            people = people.append(pd.Series(series), ignore_index=True)
            # success_counter += 1
    elif len(possible_matches) > 1:
        # This doesn't get reached
        failure_counter += 0
    else:
        if len(first_name) > 1:
            possible_matches = people.loc[
                (people.last_name == last_name)
                & (people.first_name == (" ".join([first_name[0], first_name[1]])))
                & (people.birth_year.str.contains(str(birth_year)))
            ]

            possible_matches = possible_matches.drop_duplicates(
                subset="ui", keep="first"
            )

        if len(possible_matches) == 1:
            for wp in wps:
                series = {
                    "ui": possible_matches.ui.iloc[0],
                    "wp_period": wp,
                    "faction_id": party_match,
                    "first_name": possible_matches.first_name.iloc[0],
                    "last_name": possible_matches.last_name.iloc[0],
                    "birth_place": possible_matches.birth_place.iloc[0],
                    "birth_country": possible_matches.birth_country.iloc[0],
                    "birth_year": possible_matches.birth_year.iloc[0],
                    "death_year": possible_matches.death_year.iloc[0],
                    "gender": possible_matches.gender.iloc[0],
                    "profession": possible_matches.profession.iloc[0],
                    "location_information": possible_matches.location_information.iloc[
                        0
                    ],
                    "aristocracy": possible_matches.aristocracy.iloc[0],
                    "prefix": possible_matches.prefix.iloc[0],
                    "academic_title": possible_matches.academic_title.iloc[0],
                    "salutation": possible_matches.salutation.iloc[0],
                    "vita_short": possible_matches.vita_short.iloc[0],
                    "disclosure_requirement": possible_matches.disclosure_requirement.iloc[
                        0
                    ],
                    "electoral_district_number": possible_matches.electoral_district_number.iloc[
                        0
                    ],
                    "electoral_district_name": possible_matches.electoral_district_name.iloc[
                        0
                    ],
                    "electoral_list": possible_matches.electoral_list.iloc[0],
                    "mdb_from": possible_matches.mdb_from.iloc[0],
                    "mdb_until": possible_matches.mdb_until.iloc[0],
                    "history_from": possible_matches.history_from.iloc[0],
                    "history_until": possible_matches.history_until.iloc[0],
                    "institution_type": "Regierungsmitglied",
                    "institution_name": position,
                    "institution_member_from": position_from,
                    "institution_member_until": position_until,
                    "function_long": position,
                    "function_from": "",
                    "function_until": "",
                }
                people = people.append(pd.Series(series), ignore_index=True)
        elif len(possible_matches) > 1:
            # This doesn't get reached
            failure_counter += 1
        else:
            ui_temp = max(people.ui.tolist()) + 1
            for wp in wps:
                series = {
                    "ui": ui_temp,
                    "wp_period": wp,
                    "faction_id": party_match,
                    "first_name": " ".join(first_name),
                    "last_name": last_name,
                    "birth_place": "",
                    "birth_country": "",
                    "birth_year": str(birth_year),
                    "death_year": str(death_year),
                    "gender": "",
                    "profession": "",
                    "location_information": "",
                    "aristocracy": "",
                    "prefix": "",
                    "academic_title": "",
                    "salutation": "",
                    "vita_short": "",
                    "disclosure_requirement": "",
                    "electoral_district_number": "",
                    "electoral_district_name": "",
                    "electoral_list": "",
                    "mdb_from": "",
                    "mdb_until": "",
                    "history_from": "",
                    "history_until": "",
                    "institution_type": "Regierungsmitglied",
                    "institution_name": position,
                    "institution_member_from": position_from,
                    "institution_member_until": position_until,
                    "function_long": position,
                    "function_from": "",
                    "function_until": "",
                }
                people = people.append(pd.Series(series), ignore_index=True)
    i += 1

people.to_csv(os.path.join(DATA_FINAL, "people.csv"), index=False)
