import pandas as pd
import regex
from tqdm import tqdm

from open_discourse.definitions import path

# input directory
MGS_PATH = path.POLITICIANS_STAGE_01
MPS_PATH = path.POLITICIANS_STAGE_02
FACTIONS_PATH = path.DATA_FINAL


def main(task):
    mps = pd.read_pickle(MPS_PATH / "mps.pkl")
    mgs = pd.read_pickle(MGS_PATH / "mgs.pkl")
    factions = pd.read_pickle(FACTIONS_PATH / "factions.pkl")

    # helper functions
    electoral_terms_dict = {
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

    faction_patterns = {
        "Bündnis 90/Die Grünen": r"(?:BÜNDNIS\s*(?:90)?/?(?:\s*D[1I]E)?|Bündnis\s*90/(?:\s*D[1I]E)?)?\s*[GC]R[UÜ].?\s*[ÑN]EN?(?:/Bündnis 90)?|Bündnis 90/Die Grünen",
        "CDU/CSU": r"(?:Gast|-)?(?:\s*C\s*[DSMU]\s*S?[DU]\s*(?:\s*[/,':!.-]?)*\s*(?:\s*C+\s*[DSs]?\s*[UÙ]?\s*)?)(?:-?Hosp\.|-Gast|1)?",
        "BP": r"^BP",
        "DA": r"^DA",
        "DP": r"^DP",
        "DIE LINKE.": r"DIE LINKE",
        "DPB": r"(?:^DPB)",
        "DRP": r"DRP(\-Hosp\.)?|SRP",
        "DSU": r"^DSU",
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

    def get_electoral_term(from_year=None, to_year=None):
        if not from_year and not to_year:
            raise AttributeError()
        elif not from_year:
            if to_year in electoral_terms_dict["until"]:
                return electoral_terms_dict["until"].index(to_year) + 1
            else:
                if to_year > 2017:
                    return 19
                for counter, year in enumerate(electoral_terms_dict["until"]):
                    if year > to_year:
                        return counter + 1
                raise ValueError()
        elif not to_year:
            if from_year in electoral_terms_dict["from"]:
                return electoral_terms_dict["from"].index(from_year) + 1
            else:
                if from_year > 2017:
                    return 19
                for counter, year in enumerate(electoral_terms_dict["from"]):
                    if year > from_year:
                        return counter
                raise ValueError()
        else:
            from_year = get_electoral_term(from_year=from_year, to_year=None)
            to_year = get_electoral_term(from_year=None, to_year=to_year)
            if from_year != to_year:
                return list(range(from_year, to_year + 1))
            else:
                return [from_year]

    politicians = mps.copy()
    politicians["first_name"] = politicians["first_name"].str.replace(
        "-", " ", regex=False
    )

    # merging for mgs
    for (
        last_name,
        first_name,
        birth_date,
        death_date,
        position,
        position_from,
        position_until,
        faction,
    ) in tqdm(
        zip(
            mgs["last_name"],
            mgs["first_name"],
            mgs["birth_date"],
            mgs["death_date"],
            mgs["position"],
            mgs["position_from"],
            mgs["position_until"],
            mgs["faction"],
        ),
        desc="Merging mp-data...",
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
            faction = "FDP"

        faction_abbrev = get_faction_abbrev(faction, faction_patterns)

        if faction_abbrev:
            faction_match = int(
                factions.loc[factions["abbreviation"] == faction_abbrev, "id"].iloc[0]
            )
        else:
            faction_match = -1

        first_name = [regex.sub("-", " ", name) for name in first_name]

        electoral_terms = get_electoral_term(
            from_year=int(position_from), to_year=int(position_until)
        )
        possible_matches = politicians.loc[
            (politicians["last_name"] == last_name)
            & (politicians["first_name"].str.contains(first_name[0]))
            & (politicians["birth_date"].str.contains(str(birth_date)))
        ]

        possible_matches = possible_matches.drop_duplicates(subset="ui", keep="first")

        if len(possible_matches) == 1:
            for electoral_term in electoral_terms:
                series = {
                    "ui": possible_matches["ui"].iloc[0],
                    "electoral_term": electoral_term,
                    "faction_id": faction_match,
                    "first_name": possible_matches["first_name"].iloc[0],
                    "last_name": possible_matches["last_name"].iloc[0],
                    "birth_place": possible_matches["birth_place"].iloc[0],
                    "birth_country": possible_matches["birth_country"].iloc[0],
                    "birth_date": possible_matches["birth_date"].iloc[0],
                    "death_date": possible_matches["death_date"].iloc[0],
                    "gender": possible_matches["gender"].iloc[0],
                    "profession": possible_matches["profession"].iloc[0],
                    "constituency": possible_matches["constituency"].iloc[0],
                    "aristocracy": possible_matches["aristocracy"].iloc[0],
                    "academic_title": possible_matches["academic_title"].iloc[0],
                    "institution_type": "Regierungsmitglied",
                    "institution_name": position,
                }
                series = pd.DataFrame(series, index=[politicians.index[-1]])
                politicians = pd.concat([politicians, series], ignore_index=True)
                # success_counter += 1
        elif len(possible_matches) > 1:
            # This doesn't get reached
            raise RuntimeError("What happened?")
        else:
            if len(first_name) > 1:
                possible_matches = politicians.loc[
                    (politicians["last_name"] == last_name)
                    & (
                        politicians["first_name"]
                        == (" ".join([first_name[0], first_name[1]]))
                    )
                    & (politicians["birth_date"].str.contains(str(birth_date)))
                ]

                possible_matches = possible_matches.drop_duplicates(
                    subset="ui", keep="first"
                )

            if len(possible_matches) == 1:
                for electoral_term in electoral_terms:
                    series = {
                        "ui": possible_matches["ui"].iloc[0],
                        "electoral_term": electoral_term,
                        "faction_id": faction_match,
                        "first_name": possible_matches["first_name"].iloc[0],
                        "last_name": possible_matches["last_name"].iloc[0],
                        "birth_place": possible_matches["birth_place"].iloc[0],
                        "birth_country": possible_matches["birth_country"].iloc[0],
                        "birth_date": possible_matches["birth_date"].iloc[0],
                        "death_date": possible_matches["death_date"].iloc[0],
                        "gender": possible_matches["gender"].iloc[0],
                        "profession": possible_matches["profession"].iloc[0],
                        "constituency": possible_matches["constituency"].iloc[0],
                        "aristocracy": possible_matches["aristocracy"].iloc[0],
                        "academic_title": possible_matches["academic_title"].iloc[0],
                        "institution_type": "Regierungsmitglied",
                        "institution_name": position,
                    }
                    series = pd.DataFrame(series, index=[politicians.index[-1]])
                    politicians = pd.concat([politicians, series], ignore_index=True)
            elif len(possible_matches) > 1:
                # This doesn't get reached
                raise RuntimeError("What happened?")
            else:
                ui_temp = max(politicians["ui"].tolist()) + 1
                for electoral_term in electoral_terms:
                    series = {
                        "ui": ui_temp,
                        "electoral_term": electoral_term,
                        "faction_id": faction_match,
                        "first_name": " ".join(first_name),
                        "last_name": last_name,
                        "birth_place": "",
                        "birth_country": "",
                        "birth_date": str(birth_date),
                        "death_date": str(death_date),
                        "gender": "",
                        "profession": "",
                        "constituency": "",
                        "aristocracy": "",
                        "academic_title": "",
                        "institution_type": "Regierungsmitglied",
                        "institution_name": position,
                    }
                    series = pd.DataFrame(series, index=[politicians.index[-1]])
                    politicians = pd.concat([politicians, series], ignore_index=True)

    politicians.to_csv(FACTIONS_PATH / "politicians.csv", index=False)

    return True


if __name__ == "__main__":
    main(None)
