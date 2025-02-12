import Levenshtein
import numpy as np
import pandas as pd
import regex

# Note: This matching script is a total mess, I know. But it works quite fine and has
# some optimization logic already included. Would still be nice to clean this up
# a little together with the preceeding scripts.


def get_fuzzy_names(df, name_to_check, fuzzy_threshold=0.7):
    return df.loc[
        df["last_name"].apply(Levenshtein.ratio, args=[name_to_check])
        >= fuzzy_threshold
    ]


def get_possible_matches(df, **columns):
    """Returns possible matches in df with respect to specified columns."""

    for col_name, col_value in columns.items():
        df = df.loc[df[col_name] == col_value]

    return df


def check_unique(possible_matches, col="ui"):
    return len(np.unique(possible_matches[col])) == 1


def set_id(df, index, possible_matches, col_set, col_check):
    """Sets the ID in column "col_set" of "df" at "index" to the value in
    "col_check" in possible_matches. Expects a unique col_check value in
    possible_matches.
    """
    df[col_set].at[index] = int(possible_matches[col_check].iloc[0])


def set_value(df, index, col, value):
    """Sets the value of col in df based on given value."""
    df[col].at[index] = value


def check_last_name(df, index, possible_matches, last_name):
    # Get possible matches according to last name.
    possible_matches = get_possible_matches(possible_matches, last_name=last_name)

    if check_unique(possible_matches):
        set_id(df, index, possible_matches, col_set="politician_id", col_check="ui")
        return True, possible_matches
    else:
        return False, possible_matches


def check_first_name(df, index, possible_matches, first_name):
    first_name_set = set(first_name)

    possible_matches = possible_matches.loc[
        ~possible_matches["first_name"].apply(
            lambda x: set(x).isdisjoint(first_name_set)
        )
    ]

    if check_unique(possible_matches):
        set_id(df, index, possible_matches, col_set="politician_id", col_check="ui")
        return True, possible_matches
    else:
        return False, possible_matches


def check_faction_id(df, index, possible_matches, faction_id):
    # Get possible matches according to faction_id.
    possible_matches = get_possible_matches(possible_matches, faction_id=faction_id)

    # Check if IDs unique.
    if check_unique(possible_matches):
        set_id(df, index, possible_matches, col_set="politician_id", col_check="ui")
        return True, possible_matches
    else:
        return False, possible_matches


def check_location_info(df, index, possible_matches, constituency, fuzzy_threshold=0.7):
    possible_matches = possible_matches.loc[
        possible_matches["constituency"].apply(Levenshtein.ratio, args=[constituency])
        > fuzzy_threshold
    ]

    if len(np.unique(possible_matches["ui"])) == 1:
        set_id(df, index, possible_matches, col_set="politician_id", col_check="ui")
        return True, possible_matches
    else:
        return False, possible_matches


def check_name_and_profession(
    df, index, last_name, profession_regex, politicians_df, fuzzy_threshold=75
):
    possible_matches = get_possible_matches(politicians_df, last_name=last_name)

    if len(possible_matches) == 0:
        possible_matches = get_fuzzy_names(
            politicians_df, name_to_check=last_name, fuzzy_threshold=fuzzy_threshold
        )

    if check_unique(possible_matches):
        set_id(df, index, possible_matches, col_set="politician_id", col_check="ui")
        return True, possible_matches
    else:
        boolean_indexer = possible_matches["profession"].str.contains(
            profession_regex, regex=True, na=False
        )
        possible_matches = possible_matches[boolean_indexer]

        if check_unique(possible_matches):
            set_id(df, index, possible_matches, col_set="politician_id", col_check="ui")
            return True, possible_matches
        else:
            return False, possible_matches


def check_government(df, index, last_name, mgs_electoral_term, fuzzy_threshold=80):
    possible_matches = get_possible_matches(mgs_electoral_term, last_name=last_name)

    if len(possible_matches) == 0:
        possible_matches = get_fuzzy_names(
            mgs_electoral_term, name_to_check=last_name, fuzzy_threshold=fuzzy_threshold
        )

    if check_unique(possible_matches):
        set_id(df, index, possible_matches, col_set="politician_id", col_check="ui")
        return True, possible_matches
    else:
        return False, possible_matches


def check_member_of_parliament(
    df,
    index,
    first_name,
    last_name,
    politicians,
    faction_id,
    constituency,
    acad_title,
    fuzzy_threshold=80,
):
    # Check Last Name.
    found, possible_matches = check_last_name(df, index, politicians, last_name)
    if found:
        return True, possible_matches

    # Fuzzy search, if last_name can't be found.
    if len(possible_matches) == 0:
        possible_matches = get_fuzzy_names(politicians, name_to_check=last_name)

    if len(possible_matches) == 0:
        return False, possible_matches

    # Check Faction ID.
    if faction_id >= 0:
        found, possible_matches = check_faction_id(
            df, index, possible_matches, faction_id
        )
        if found:
            return found, possible_matches

    # Check First Name.
    if first_name:
        found, possible_matches = check_first_name(
            df, index, possible_matches, first_name
        )
        if found:
            return found, possible_matches

    # Match with location info.
    if constituency:
        found, possible_matches = check_location_info(
            df, index, possible_matches, constituency
        )
        if found:
            return found, possible_matches
    elif constituency == "":
        # Probably someone joined during the period, e.g. there
        # is an entry in STAMMDATEN for the correct person
        # without the location info, as there was only one
        # person with the last name before.
        possible_matches = get_possible_matches(possible_matches, constituency="")
        if check_unique(possible_matches, col="ui"):
            set_id(df, index, possible_matches, col_set="politician_id", col_check="ui")
            return True, possible_matches

    # Check Gender.
    found, possible_matches = check_woman(df, index, acad_title, possible_matches)
    if found:
        return True, possible_matches
    else:
        return False, possible_matches


def check_woman(df, index, acad_title, possible_matches):
    if "Frau" in acad_title:
        possible_matches = possible_matches.loc[
            possible_matches["gender"] == "weiblich"
        ]

        if check_unique(possible_matches):
            set_id(df, index, possible_matches, col_set="politician_id", col_check="ui")
            return True, possible_matches
    return False, possible_matches


def insert_politician_id_into_speech_content(
    df, politicians_electoral_term, mgs_electoral_term, politicians
):
    "Appends a politician id column with matched IDs"

    df = df.fillna("")

    last_name_copy = df["last_name"].copy()
    first_name_copy = df["first_name"].copy()

    problem_df = []

    # Lower case to ease up matching. Note: first_name is a list of strings.
    df["first_name"] = df["first_name"].apply(
        lambda first: [str.lower(string) for string in first]
    )

    df["constituency"] = df["constituency"].fillna("")
    df["constituency"] = df["constituency"].str.lower()
    df["last_name"] = df["last_name"].str.lower()
    df["last_name"] = df["last_name"].str.replace("ß", "ss", regex=False)
    df.insert(4, "politician_id", -1)
    df["position_long"] = df["position_long"].str.lower()

    for index, row in df.iterrows():
        # ##################################################################
        # ######## Start Matching ##########################################
        # ##################################################################

        if row["position_short"] == "Presidium of Parliament":
            if row["position_long"] in [
                "präsident",
                "präsidentin",
                "vizepräsident",
                "vizepräsidentin",
            ]:
                if row["last_name"] == "jäger":
                    # The president of the Bundestag is saves as "jaeger" in the "politicians" data
                    # Maybe manually changing last name as below would work. But must be checked
                    # if this does maybe change also other politicians which should not be changed.
                    # row["last_name"] = "jaeger"
                    pass
                elif row["last_name"] == "bläss":
                    row["last_name"] = "bläss-rafajlovski"

                profession_pattern = "präsident dbt|präsidentin dbt|vizepräsident dbt|vizepräsidentin dbt|vizeprä. dbt"
                found, possible_matches = check_name_and_profession(
                    df,
                    index,
                    row["last_name"],
                    profession_pattern,
                    politicians_electoral_term,
                )

                if found:
                    continue
                else:
                    found, possible_matches = check_member_of_parliament(
                        df,
                        index,
                        row["first_name"],
                        row["last_name"],
                        politicians_electoral_term,
                        row["faction_id"],
                        row["constituency"],
                        row["acad_title"],
                        fuzzy_threshold=80,
                    )

                    if found:
                        continue
                    else:
                        problem_df.append(row)

            elif regex.search("schriftführer", row["position_long"]):
                profession_pattern = "schriftführer"
                found, possible_matches = check_name_and_profession(
                    df,
                    index,
                    row["last_name"],
                    profession_pattern,
                    politicians_electoral_term,
                )

                if found:
                    continue
                else:
                    found, possible_matches = check_member_of_parliament(
                        df,
                        index,
                        row["first_name"],
                        row["last_name"],
                        politicians_electoral_term,
                        row["faction_id"],
                        row["constituency"],
                        row["acad_title"],
                        fuzzy_threshold=80,
                    )

                    if found:
                        continue
                    else:
                        problem_df.append(row)

            else:
                found, possible_matches = check_member_of_parliament(
                    df,
                    index,
                    row["first_name"],
                    row["last_name"],
                    politicians_electoral_term,
                    row["faction_id"],
                    row["constituency"],
                    row["acad_title"],
                    fuzzy_threshold=80,
                )

                if found:
                    continue
                else:
                    problem_df.append(row)

        elif row["position_short"] == "Minister":
            found, possible_matches = check_government(
                df, index, row["last_name"], mgs_electoral_term, fuzzy_threshold=75
            )

            if found:
                continue
            else:
                found, possible_matches = check_member_of_parliament(
                    df,
                    index,
                    row["first_name"],
                    row["last_name"],
                    politicians_electoral_term,
                    row["faction_id"],
                    row["constituency"],
                    row["acad_title"],
                    fuzzy_threshold=80,
                )

                if found:
                    continue
                else:
                    problem_df.append(row)

        elif row["position_short"] == "Chancellor":
            found, possible_matches = check_government(
                df, index, row["last_name"], mgs_electoral_term
            )

            if found:
                continue
            else:
                problem_df.append(row)

        elif row["position_short"] == "Secretary of State":
            # Look for "Parlamentarische Staatsekretäre"
            if regex.search("parl", row["position_long"]):
                profession_pattern = (
                    "Parl. Staatssekretär|Parlamentarischer Staatssekretär"
                )

                found, possible_matches = check_name_and_profession(
                    df,
                    index,
                    row["last_name"],
                    profession_pattern,
                    politicians_electoral_term,
                )

                if found:
                    continue
                else:
                    found, possible_matches = check_member_of_parliament(
                        df,
                        index,
                        row["first_name"],
                        row["last_name"],
                        politicians_electoral_term,
                        row["faction_id"],
                        row["constituency"],
                        row["acad_title"],
                        fuzzy_threshold=80,
                    )

                    if found:
                        continue
                    else:
                        problem_df.append(row)

            # "Beamtete Staatsekretäre" are not included in "politicians" data.
            elif regex.search("staatssekretär", row["position_long"]):
                problem_df.append(row)
                continue

            else:
                problem_df.append(row)
                continue

        elif row["position_short"] == "Member of Parliament":
            found, possible_matches = check_member_of_parliament(
                df,
                index,
                row["first_name"],
                row["last_name"],
                politicians_electoral_term,
                row["faction_id"],
                row["constituency"],
                row["acad_title"],
                fuzzy_threshold=80,
            )

            if found:
                continue
            else:
                problem_df.append(row)

        else:
            # Some other notes
            # Example: Meyer in 01033. Have the same last name and
            # are in the same faction at same period. In this
            # particular case the location information in the toc
            # "Westhagen", does not match with the two possible
            # location informations "Hagen", "Bremen"
            # probably "Hagen" == "Westfalen" is meant.
            # Other things: "Cornelia <Nachname>" ist in dem spoken content
            # mit "Conny <Nachname>" abgespeichert. Findet Vornamen natürlich
            # nicht.

            problem_df.append(row)

        df["first_name"] = first_name_copy
        df["last_name"] = last_name_copy

    problem_df = pd.DataFrame(problem_df)

    return df, problem_df


def insert_politician_id_into_contributions_extended(
    df, politicians_electoral_term, mgs_electoral_term
):
    "Appends a politician id column with matched IDs"

    assert {
        "last_name",
        "first_name",
        "faction_id",
        "acad_title",
        "constituency",
    }.issubset(df.columns)

    if len(df) == 0:
        return df, pd.DataFrame()

    last_name_copy = df["last_name"].copy()
    first_name_copy = df["first_name"].copy()

    problem_df = []

    # Lower case to ease up matching
    df["first_name"] = df["first_name"].apply(
        lambda first: [str.lower(string) for string in first]
    )
    df["constituency"] = df["constituency"].fillna("")
    df["constituency"] = df["constituency"].str.lower()
    df["last_name"] = df["last_name"].str.lower()
    df["last_name"] = df["last_name"].str.replace("ß", "ss", regex=False)
    df.insert(4, "politician_id", -1)

    for index, row in df.iterrows():
        # Start Matching

        # E.g. Präsident, Bundeskanzler, Staatssekretär etc.
        if not row["last_name"]:
            problem_df.append(row)
            continue
        else:
            found, possible_matches = check_last_name(
                df, index, politicians_electoral_term, row["last_name"]
            )
            if found:
                if check_unique(possible_matches, col="faction_id"):
                    set_id(
                        df,
                        index,
                        possible_matches,
                        col_set="faction_id",
                        col_check="faction_id",
                    )
                    continue
                else:
                    continue

        # Fuzzy search, if last_name can't be found.
        if len(possible_matches) == 0:
            possible_matches = get_fuzzy_names(
                politicians_electoral_term, row["last_name"]
            )

        if len(possible_matches) == 0:
            problem_df.append(row)
            continue

        # Check Faction ID.
        if row["faction_id"] >= 0:
            found, possible_matches = check_faction_id(
                df, index, possible_matches, row["faction_id"]
            )
            if found:
                if check_unique(possible_matches, col="faction_id"):
                    df["faction_id"].at[index] = int(
                        possible_matches["faction_id"].iloc[0]
                    )
                    continue
                else:
                    continue

        # Check First Name.
        if row["first_name"]:
            found, possible_matches = check_first_name(
                df, index, possible_matches, row["first_name"]
            )
            if found:
                continue

        # Match with location info.
        if row["constituency"]:
            found, possible_matches = check_location_info(
                df, index, possible_matches, row["constituency"]
            )
            if found:
                continue
        elif row["constituency"] == "":
            # Probably someone joined during the period, e.g. there
            # is an entry in STAMMDATEN for the correct person
            # without the location info, as there was only one
            # person with the last name before.
            possible_matches = get_possible_matches(possible_matches, constituency="")

            if check_unique(possible_matches):
                set_id(
                    df, index, possible_matches, col_set="politician_id", col_check="ui"
                )
                continue

        # Check Gender.
        found, possible_matches = check_woman(
            df, index, row["acad_title"], possible_matches
        )
        if found:
            continue

        # Example: Meyer in 01033. Have the same last name and
        # are in the same faction at same period. In this
        # particular case the location information in the toc
        # "Westhagen", does not match with the two possible
        # location informations "Hagen", "Bremen"
        # probably "Hagen" == "Westfalen" is meant.
        # Other things: Cornelia Irgendwas, ist in dem spoken content
        # mit "Conny Irgendwas abgespeichert. Findet Vornamen natürlich
        # nicht.
        problem_df.append(row)

        df["first_name"] = first_name_copy
        df["last_name"] = last_name_copy

    problem_df = pd.DataFrame(problem_df)
    return df, problem_df
