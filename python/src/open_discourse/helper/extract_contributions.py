import copy

import pandas as pd
import regex

# Party Patterns:
parties = {
    "AfD": r"Alternative für Deutschland|AfD",
    "CDU/CSU": r"(?:Gast|-)?(?:\s*C\s*[DSMU]\s*S?[DU]\s*(?:\s*[/,':!.-]?)*\s*(?:\s*C+\s*[DSs]?\s*[UÙ]?\s*)?)(?:-?Hosp\.|-Gast|1)?",
    "SPD": r"\s*'?S(?:PD|DP)(?:\.|-Gast)?",
    "FDP": r"\s*F\.?\s*[PDO][.']?[DP]\.?",
    "BÜNDNIS 90/DIE GRÜNEN": r"(?:BÜNDNIS\s*(?:90)?/?(?:\s*D[1I]E)?|Bündnis\s*90/(?:\s*D[1I]E)?)?\s*[GC]R[UÜ].?\s*[ÑN]EN?(?:/Bündnis 90)?|BÜNDNISSES 90/DIE GRÜNEN|Grünen|BÜNDNISSES 90/ DIE GRÜNEN|BÜNDNIS 90/DIE GRÜNEN",
    "DIE LINKE": r"DIE LIN\s?KEN?|LIN\s?KEN",
    "PDS/Linke Liste": r"(?:Gruppe\s*der\s*)?PDS(?:/(?:LL|Linke Liste))?",
    "fraktionslos": r"(fraktionslos|Parteilos)",
    "GB/BHE": r"(?:GB[/-]\s*)?BHE(?:-DG)?",
    "DP": "DP",
    "KPD": "KPD",
    "Z": r"Z\s|Zentrum",
    "BP": "BP|Bayernpartei",
    "FU": "FU",
    "WAV": "WAV",
    "DRP": r"DRP(\-Hosp\.)?",
    "FVP": "FVP",
    "SSW": "SSW",
    "SRP": "SRP",
    "DA": "DA",
    "Gast": "Gast",
    "DBP": "DBP",
    "NR": "NR",
}
left_right_Pattern = r"([Rr]echts|[Ll]inks|[Mm]itte)"


# Other Patterns:
prefix_Pattern = r"\b(?:\s*bei\s+der|\s*im|\s*bei\s+Abgeordneten|\s*bei\s+Abgeordneten\s+der|\s*beim|\s*des|)\b"
suffix_Pattern = r"\s*?(?!der)(?![-––])(?P<initiator>(?:(?!\s[-––]\s)[^:])*)\s*"
text_Pattern = (
    r"[^––:(){{}}[\]\n{}]"  # Basic Text Pattern that can be extended if needed
)

# Bracket Patterns (can also be extended modularly):
start_contributions_opening_bracket_Pattern = (
    r"(?:(?<=\()|(?<=[-––]\s)|(?<=[––])|(?<=[-––]\.\s)|(?<=\s[-––]){})"
)
start_contributions_closing_bracket_Pattern = (
    r"(?=\)|–[^\)\(]+\)|{{|—[^\)\(]+\)|\)|-[^\)\(]+\){})"
)

opening_bracket_Pattern = r"[({\[]"
closing_bracket_Pattern = r"[)}\]]"

# Base Patterns:
base_applause_Pattern = (
    r"(?P<delete>(?:(?:[Ll]ang)?[Aa]nhaltender\s(?:[Ll]ebhafter\s)?|[Ll]ebhafter\s|[Ee]rneuter\s|[Dd]emonstrativer|[Aa]llseitiger)?Beifall"
    + prefix_Pattern
    + suffix_Pattern
    + r")"
)
base_person_interjection_Pattern = (
    r"(?P<delete>(?!Beifall){}:\s(?P<content>[^-)—–{{}}]*))"
)
base_shout_Pattern = (
    r"(?P<delete>(und\s?|[Ee]rneute\s|[Aa]nhaltende\s|[Ee]rregte\s|[Vv]ielfache)?(Zurufe?|Gegenrufe?|Rufe?)(?:(?::|"
    + prefix_Pattern
    + r"{0}:)\s*(?P<content>{1}*)|"
    + prefix_Pattern
    + suffix_Pattern
    + r"))"
)
base_cheerfulness_Pattern = (
    r"(?P<delete>(Große)?Heiterkeit" + prefix_Pattern + suffix_Pattern + r")"
)
base_objection_Pattern = (
    r"(?P<delete>Widerspruch" + prefix_Pattern + suffix_Pattern + r")"
)
base_laughter_Pattern = r"(?P<delete>Lachen" + prefix_Pattern + suffix_Pattern + r")"
base_approval_Pattern = (
    r"(?<delete>(Sehr\srichtig[.!]?|Zustimmung|Lebhafte\sZustimmung|Sehr\swahr[.!]?|Bravo[-—\s]?[Rr]ufe[.!]?|Bravo[.!]?|Sehr\sgut[.!]?)"
    + prefix_Pattern
    + suffix_Pattern
    + r")"
)
base_interruption_Pattern = r"Unterbrechung[^)]*"
base_disturbance_Pattern = (
    r"(?P<delete>[Uu]nruhe" + prefix_Pattern + suffix_Pattern + r")"
)

# Modular Patterns:
name_Pattern = {
    0: r"(?P<name_raw>(?:(?!\sund\s)(?!sowie\sdes)"
    # Formatting has to be done this way because of python formatting errors
    + text_Pattern.format("").replace(
        "{}", "{{}}"
    )  # Text Pattern can be extended if needed
    + r")+)(\s*{0}(?P<constituency>"
    + text_Pattern.format("").replace(
        "{}", "{{}}"
    )  # Text Pattern can be extended if needed
    + r"+){1})*\s*{0}(?P<faction>"
    + text_Pattern.format("").replace(
        "{}", "{{}}"
    )  # Text Pattern can be extended if needed
    + r"*){1}(\s*{0}(?P<constituency>"
    + text_Pattern.format("").replace(
        "{}", "{{}}"
    )  # Text Pattern can be extended if needed
    + r"+){1})*",
    1: r"(?P<name_raw>(?:(?!\sund\s)(?!sowie\sdes)"
    + text_Pattern.format("").replace(
        "{}", "{{}}"
    )  # Text Pattern can be extended if needed
    + r")+)(?P<constituency>{0}"
    + text_Pattern.format("").replace(
        "{}", "{{}}"
    )  # Text Pattern can be extended if needed
    + r"+{1})*",
}


def get_government_factions(electoral_term):
    """Get the government factions for the given electoral_term"""
    government_electoral_term = {
        1: ["CDU/CSU", "FDP", "DP"],
        2: ["CDU/CSU", "FDP", "DP"],
        3: ["CDU/CSU", "DP"],
        4: ["CDU/CSU", "FDP"],
        5: ["CDU/CSU", "SPD"],
        6: ["SPD", "FDP"],
        7: ["SPD", "FDP"],
        8: ["SPD", "FDP"],
        9: ["SPD", "FDP"],
        10: ["CDU/CSU", "FDP"],
        11: ["CDU/CSU", "FDP"],
        12: ["CDU/CSU", "FDP"],
        13: ["CDU/CSU", "FDP"],
        14: ["SPD", "BÜNDNIS 90/DIE GRÜNEN"],
        15: ["SPD", "BÜNDNIS 90/DIE GRÜNEN"],
        16: ["CDU/CSU", "SPD"],
        17: ["CDU/CSU", "FDP"],
        18: ["CDU/CSU", "SPD"],
        19: ["CDU/CSU", "SPD"],
        20: ["SPD", "BÜNDNIS 90/DIE GRÜNEN", "FDP"],
    }

    return government_electoral_term[electoral_term]


def convert_to_string(string):
    return "" if string is None else str(string)


def clean_person_name(name_raw):
    """cleans the person name_raw"""
    # Remove any newlines from the name_raw
    name_raw = regex.sub(r"\n", " ", convert_to_string(name_raw))
    # Remove any Additional stuff
    name_raw = regex.sub(
        r"(Gegenrufe?\sdes\s|Gegenrufe?\sder\s|Zurufe?\sdes\s|Zurufe?\sder\s)(Abg\s?\.\s)*",
        "",
        name_raw,
    )
    name_raw = regex.sub(r"(Abg\s?\.\s?|Abgeordneten\s)", "", name_raw)
    # Remove any Pronouns
    name_raw = regex.sub(r"(^\s?der\s?|^\s?die\s?|^\s?das\s?|^\s?von\s?)", "", name_raw)
    # Remove whitespaces at the beginning and at the end
    name_raw = name_raw.lstrip(" ").rstrip(" ")

    # Return the name_raw
    return name_raw


def add_entry(frame, id, type, name_raw, faction, constituency, content, text_position):
    """adds an entry for every Contribution into the given frame"""
    # Append the corresponding variables to the dictionary
    frame["id"].append(id)
    frame["type"].append(type)
    frame["name_raw"].append(clean_person_name(name_raw))
    frame["faction"].append(convert_to_string(faction))
    frame["constituency"].append(convert_to_string(constituency))
    frame["content"].append(convert_to_string(content))
    frame["text_position"].append(int(text_position))

    # Return the frame
    return frame


def extract_initiators(
    initiators, electoral_term, session, identity, text_position, frame, type
):
    """extracts the initators and creates and entry in the frame (for each initiator)
    Tries extracting politicians (twice - different methods); parties by themselves;
    'links', 'rechts', 'mitte' and government parties"""

    initiators_not_removed = copy.copy(initiators)
    # Remove wrongly placed contributions from initiators and pass them recursively
    other_contributions = regex.search(
        r"(?P<type>[Bb]eifall|[Zz]uruf|[Gg]egenruf|[Rr]uf|[Hh]eiterkeit|[Ww]iderspruch|[Ll]achen|[Zz]ustimmung|[Uu]nterbrechung|[Uu]nruhe)(?P<initiators>(?:(?!\s[-––]\s).)*)\s*",
        initiators,
    )
    if other_contributions:
        frame, _ = methods[other_contributions.group("type").lower()](
            "(" + other_contributions.group() + ")",
            electoral_term,
            session,
            identity,
            text_position,
            frame,
        )
        initiators = initiators.replace(other_contributions.group(), "")

    if session < 7115:
        # Set name pattern to the second name pattern (second row in name_Pattern)
        name_Pattern_id = 1
    else:
        # Set name pattern to the first name pattern (first row in name_Pattern)
        name_Pattern_id = 0

    # Create the first_person_search_Pattern (looking for key Abg.)
    first_person_search_Pattern = r"Abg\s?\.\s?{}(?:(?<=!:)|(?!:))".format(
        name_Pattern[name_Pattern_id].format(
            opening_bracket_Pattern,
            closing_bracket_Pattern,
        )
    )
    # Find match
    first_person_match = regex.search(
        first_person_search_Pattern,
        initiators,
    )
    if first_person_match:
        # Remove name_raw from the search text
        initiators = initiators.replace(first_person_match.group(), "")
        # Check if the person was just asking a "Zwischenfrage"
        if not regex.search("[Zz]wischenfrage", initiators):
            # Get the persons name_raw
            name_raw = first_person_match.group("name_raw")
            # Try to get the persons faction
            try:
                faction = first_person_match.group("faction")
            except IndexError:
                faction = ""
            # Try to get the persons location information
            try:
                constituency = first_person_match.group("constituency")
            except IndexError:
                constituency = ""
            # Add an entry to the frame
            frame = add_entry(
                frame,
                identity,
                type,
                name_raw,
                faction,
                constituency,
                "",
                text_position,
            )

    # Create the first_person_search_Pattern (looking for key und)
    second_person_search_Pattern = (
        r"(?:\sund|sowie\sdes)\s+(?:des|der)?{}(?:(?<=!:)|(?!:))".format(
            name_Pattern[name_Pattern_id].format(
                opening_bracket_Pattern,
                closing_bracket_Pattern,
            )
        )
    )

    # Find match
    second_person_match = regex.search(
        second_person_search_Pattern,
        initiators,
    )
    if second_person_match:
        # Remove the person name_raw from the search text
        initiators = initiators.replace(second_person_match.group(), "")
        # Check if the person was just asking a "Zwischenfrage"
        if not regex.search("[Zz]wischenfrage", initiators):
            # Get the persons name_raw
            name_raw = second_person_match.group("name_raw")
            # Try to get the persons faction
            try:
                faction = second_person_match.group("faction")
            except IndexError:
                faction = ""
            # Try to get the persons location information
            try:
                constituency = second_person_match.group("constituency")
            except IndexError:
                constituency = ""
            # Add an entry to the frame
            frame = add_entry(
                frame,
                identity,
                type,
                name_raw,
                faction,
                constituency,
                "",
                text_position,
            )

    # Iterate over all parties
    for faction in parties:
        # Create the faction_search_Pattern
        faction_search_Pattern = r"(?<!\[)(" + parties[faction] + r")(?![^[\s]*\])"
        # Find match for faction
        faction_match = regex.search(faction_search_Pattern, initiators)
        # Check if there is a match
        if faction_match:
            # Remove the faction from the search text
            initiators = initiators.replace(faction_match.group(), "")
            # Add an entry to the frame
            frame = add_entry(frame, identity, type, "", faction, "", "", text_position)

    # Create the left_right_search_Pattern
    left_right_search_Pattern = left_right_Pattern
    # Find matches
    left_right_matches = list(regex.finditer(left_right_search_Pattern, initiators))
    for direction in left_right_matches:
        # Remove the direction from the search text
        initiators = initiators.replace(direction.group(), "")
        # Add an entry to the frame
        frame = add_entry(
            frame, identity, type, "", "", "", direction.group(), text_position
        )

    # Search for Regierungsparteien in the initiators
    government_matches = regex.search(r"[Rr]egierungspar[^\s]+", initiators)
    if government_matches:
        initiators = initiators.replace(government_matches.group(), "")
        # iterate over every faction get_government_factions returns
        for faction in get_government_factions(electoral_term):
            # Add and entry to the frame for every faction in the government
            frame = add_entry(frame, identity, type, "", faction, "", "", text_position)

    search_stuff = [
        ": Das haben Sie 16 Jahre lang versäumt!",
    ]
    for stuff in search_stuff:
        if (
            stuff == initiators
            # or stuff in initiators
            # or stuff == initiators_not_removed
            # or stuff in initiators_not_removed
        ):
            print(
                initiators_not_removed,
                session,
                first_person_search_Pattern,
            )
    # Return the frame
    return frame, initiators


def extract_applause(text, electoral_term, session, identity, text_position, frame):
    """Extracts applause from the given text"""

    # creates the Pattern modularly
    applause_Pattern = (
        start_contributions_opening_bracket_Pattern.format(
            ""  # Nothing to extend, so .format("")
        )
        + base_applause_Pattern
        + start_contributions_closing_bracket_Pattern.format(
            ""  # Nothing to extend, so .format("")
        )
    )

    matches = list(
        regex.finditer(
            applause_Pattern,
            text,
        )
    )

    for match in matches:
        # replace everything except the delimeters
        text = text.replace(match.group("delete"), " ")
        # Extract the initiators and create entries to the dataframe
        frame, returned = extract_initiators(
            match.group("initiator"),
            electoral_term,
            session,
            identity,
            text_position,
            frame,
            "Beifall",
        )

    # Return the frame
    return frame, text


def extract_person_interjection(
    text, electoral_term, session, identity, text_position, frame
):
    """Extracts person interjections from the given text"""

    # Check if session is under 7115
    if session < 7115:
        # Set name pattern to the second name pattern (second row in name_Pattern)
        name_Pattern_id = 1
        extra_Pattern = r"(?:Abg\s?\.\s?)"
    else:
        # Set name pattern to the first name pattern (first row in name_Pattern)
        name_Pattern_id = 0
        extra_Pattern = ""

    # creates the Pattern "very" modularly
    person_interjection_Pattern = (
        start_contributions_opening_bracket_Pattern.format("")
        + base_person_interjection_Pattern.format(
            extra_Pattern
            + name_Pattern[name_Pattern_id].format(
                opening_bracket_Pattern,
                closing_bracket_Pattern,
            )
        )
        + start_contributions_closing_bracket_Pattern.format("")
    )

    # Match person interjections
    matches = list(regex.finditer(person_interjection_Pattern, text))

    # Iterate over matches
    for match in matches:
        # replace everything except the delimeters
        text = text.replace(match.group("delete"), " ")
        name_raw = match.group("name_raw")
        content = match.group("content")

        try:
            faction = match.group("faction")
        except IndexError:
            faction = ""

        try:
            constituency = match.group("constituency")
        except IndexError:
            constituency = ""

        # Add entry to the frame
        frame = add_entry(
            frame,
            identity,
            "Personen-Einruf",
            name_raw,
            faction,
            constituency,
            content,
            text_position,
        )

    return frame, text


def extract_shout(text, electoral_term, session, identity, text_position, frame):
    """Extracts shouts from the given text"""

    # Check if session is under 7115
    if session < 7115:
        # Set name pattern to the second name pattern (second row in name_Pattern)
        name_Pattern_id = 1
    else:
        # Set name pattern to the first name pattern (first row in name_Pattern)
        name_Pattern_id = 0

    # creates the Pattern modularly
    shout_Pattern = (
        start_contributions_opening_bracket_Pattern.format(
            r"|(?<=[Hh]eiterkeit\s)|(?<=[Ll]achen\s)|(?<=[Ww]eiterer\s)|(?<=[Ww]eitere\s)|(?<=[Ee]rneuter\s)|(?<=[Ee]rneute\s)|(?<=[Ff]ortgesetzte\s)|(?<=[Ll]ebhafte\s)|(?<=[Ww]eitere\s[Ll]ebhafte\s|(?<=Andauernde\s)|(?<=Fortdauernde\s))"  # Extending the opening_bracket_Pattern
        )
        + base_shout_Pattern.format(
            r"\s*Abg\s?\.\s?{}".format(
                name_Pattern[name_Pattern_id].format(
                    opening_bracket_Pattern,
                    closing_bracket_Pattern,
                )
            ),
            text_Pattern.format("").replace("{}", "{{}}"),
        )
        + start_contributions_closing_bracket_Pattern.format(
            ""  # Nothing to extend, so .format("")
        )
    )

    matches = list(
        regex.finditer(
            shout_Pattern,
            text,
        )
    )
    for match in matches:
        if match.group("initiator"):
            # replace everything except the delimeters
            text = text.replace(match.group("delete"), " ")
            # Extract the initiators and create entries to the dataframe
            frame, _ = extract_initiators(
                match.group("initiator"),
                electoral_term,
                session,
                identity,
                text_position,
                frame,
                "Zuruf",
            )
        else:
            # replace everything except the delimeters
            text = text.replace(match.group("delete"), " ")

            try:
                name_raw = match.group("name_raw")
            except IndexError:
                name_raw = ""
            content = match.group("content")

            try:
                faction = match.group("faction")
            except IndexError:
                faction = ""

            try:
                constituency = match.group("constituency")
            except IndexError:
                constituency = ""

            # Add an entry to the frame
            frame = add_entry(
                frame,
                identity,
                "Zuruf",
                name_raw,
                faction,
                constituency,
                content,
                text_position,
            )

    # Extract faction shouts
    # creates the Pattern modularly
    faction_shout_Pattern = (
        start_contributions_opening_bracket_Pattern.format(
            r"|(?<=[Hh]eiterkeit\s)|(?<=[Ll]achen\s)|(?<=[Ww]eiterer\s)|(?<=[Ww]eitere\s)|(?<=[Ee]rneuter\s)|(?<=[Ee]rneute\s)|(?<=[Ff]ortgesetzte\s)|(?<=[Ll]ebhafte\s)|(?<=[Ww]eitere\s[Ll]ebhafte\s|(?<=Andauernde\s)|(?<=Fortdauernde\s))"  # Extending the opening_bracket_Pattern
        )
        + r"(?P<delete>(?P<initiator>"
        + text_Pattern.format("").replace("{}", "{{}}")
        + r"+):\s*(?P<content>"
        + text_Pattern
        + r"+))"
        + start_contributions_closing_bracket_Pattern.format(
            ""  # Nothing to extend, so .format("")
        )
    )

    matches = list(
        regex.finditer(
            faction_shout_Pattern,
            text,
        )
    )
    for match in matches:
        # replace everything except the delimeters
        text = text.replace(match.group("delete"), " ")
        content = match.group("content")
        initiators = match.group("initiator")

        # Iterate over all parties
        for faction in parties:
            # Create the faction_search_Pattern
            faction_search_Pattern = r"(?<!\[)(" + parties[faction] + r")(?![^[\s]*\])"
            # Find match for faction
            faction_match = regex.search(faction_search_Pattern, initiators)
            # Check if there is a match
            if faction_match:
                # Remove the faction from the search text
                initiators = initiators.replace(faction_match.group(), "")
                # Add an entry to the frame
                frame = add_entry(
                    frame, identity, "Zuruf", "", faction, "", content, text_position
                )

    # Return the frame
    return frame, text


def extract_cheerfulness(text, electoral_term, session, identity, text_position, frame):
    """Extracts cheerfulness from the given text"""

    # creates the Pattern modularly
    cheerfulness_Pattern = (
        start_contributions_opening_bracket_Pattern.format(
            ""  # Nothing to extend, so .format("")
        )
        + base_cheerfulness_Pattern
        + start_contributions_closing_bracket_Pattern.format(
            ""  # Nothing to extend, so .format("")
        )
    )

    matches = list(
        regex.finditer(
            cheerfulness_Pattern,
            text,
        )
    )
    for match in matches:
        # replace everything except the delimeters
        text = text.replace(match.group("delete"), " ")
        # Extract the initiators and create entries to the dataframe
        frame, _ = extract_initiators(
            match.group("initiator"),
            electoral_term,
            session,
            identity,
            text_position,
            frame,
            "Heiterkeit",
        )

    # Return the frame
    return frame, text


def extract_objection(text, electoral_term, session, identity, text_position, frame):
    """Extracts objection from the given text"""

    # creates the Pattern modularly
    objection_Pattern = (
        start_contributions_opening_bracket_Pattern.format(
            ""  # Nothing to extend, so .format("")
        )
        + base_objection_Pattern
        + start_contributions_closing_bracket_Pattern.format(
            ""  # Nothing to extend, so .format("")
        )
    )

    matches = list(
        regex.finditer(
            objection_Pattern,
            text,
        )
    )
    for match in matches:
        # replace everything except the delimeters
        text = text.replace(match.group("delete"), " ")
        # Extract the initiators and create entries to the dataframe
        frame, _ = extract_initiators(
            match.group("initiator"),
            electoral_term,
            session,
            identity,
            text_position,
            frame,
            "Widerspruch",
        )

    # Return the frame
    return frame, text


def extract_laughter(text, electoral_term, session, identity, text_position, frame):
    """Extracts laughter from the given text"""

    # creates the Pattern modularly
    laughter_Pattern = (
        start_contributions_opening_bracket_Pattern.format(
            ""  # Nothing to extend, so .format("")
        )
        + base_laughter_Pattern
        + start_contributions_closing_bracket_Pattern.format(
            r"|\sund\sZurufe\)"  # Extending the closing_bracket_Pattern
        )
    )

    matches = list(
        regex.finditer(
            laughter_Pattern,
            text,
        )
    )
    for match in matches:
        # replace everything except the delimeters
        text = text.replace(match.group("delete"), " ")
        # Extract the initiators and create entries to the dataframe
        frame, _ = extract_initiators(
            match.group("initiator"),
            electoral_term,
            session,
            identity,
            text_position,
            frame,
            "Lachen",
        )

    # Return the frame
    return frame, text


def extract_approval(text, electoral_term, session, identity, text_position, frame):
    """Extracts approval from the given text"""

    # creates the Pattern modularly
    approval_Pattern = (
        start_contributions_opening_bracket_Pattern.format(
            ""  # Nothing to extend, so .format("")
        )
        + base_approval_Pattern
        + start_contributions_closing_bracket_Pattern.format(
            ""  # Nothing to extend, so .format("")
        )
    )

    matches = list(
        regex.finditer(
            approval_Pattern,
            text,
        )
    )
    for match in matches:
        # replace everything except the delimeters
        text = text.replace(match.group("delete"), " ")
        # Extract the initiators and create entries to the dataframe
        frame, _ = extract_initiators(
            match.group("initiator"),
            electoral_term,
            session,
            identity,
            text_position,
            frame,
            "Zustimmung",
        )

    # Return the frame
    return frame, ""


def extract_interruption(text, electoral_term, session, identity, text_position, frame):
    """Extracts interruptions from the given text"""

    # Creates the Pattern modularly
    interruption_Pattern = (
        start_contributions_opening_bracket_Pattern.format(
            ""  # Nothing to extend, so .format("")
        )
        + base_interruption_Pattern
        + start_contributions_closing_bracket_Pattern.format(
            ""  # Nothing to extend, so .format("")
        )
    )

    # Find matches
    matches = list(regex.finditer(interruption_Pattern, text))

    # Iterate over matches
    for match in matches:
        # replace everything except the delimeters
        text = text.replace(match.group("delete"), " ")
        # Add entry to the frame
        frame = add_entry(
            frame,
            identity,
            "Unterbrechung",
            "",
            "",
            "",
            match.group("delete"),
            text_position,
        )

    return frame, text


def extract_disturbance(text, electoral_term, session, identity, text_position, frame):
    """Extracts disturbance from the given text"""

    # creates the Pattern modularly
    disturbance_Pattern = (
        start_contributions_opening_bracket_Pattern.format(
            ""  # Nothing to extend, so .format("")
        )
        + base_disturbance_Pattern
        + start_contributions_closing_bracket_Pattern.format(
            ""  # Nothing to extend, so .format("")
        )
    )

    matches = list(
        regex.finditer(
            disturbance_Pattern,
            text,
        )
    )

    for match in matches:
        # replace everything except the delimeters
        text = text.replace(match.group("delete"), " ")
        # Extract the initiators and create entries to the dataframe
        frame, _ = extract_initiators(
            match.group("initiator"),
            electoral_term,
            session,
            identity,
            text_position,
            frame,
            "Unruhe",
        )

    # Return the frame
    return frame, text


def extract(
    speech_text, session, identity, text_position=0, text_position_reversed=True
):
    electoral_term = session // 1000

    # Match all brackets
    brackets = list(
        regex.finditer(r"\(([^(\)]*(\(([^(\)]*)\))*[^(\)]*)\)", speech_text)
    )

    # Create an empty frame for the normal contributions
    frame = {
        "id": [],
        "type": [],
        "name_raw": [],
        "faction": [],
        "constituency": [],
        "content": [],
        "text_position": [],
    }

    contributions_simplified = {"text_position": [], "content": [], "speech_id": []}

    # Iterate over all brackets
    for bracket in reversed(brackets):
        # calculate reversed text_position
        reversed_text_position = len(brackets) - 1 - text_position
        # Make sure to remove all newlines
        speech_text_no_newline = regex.sub(r"\n+", " ", bracket.group())
        speech_text_no_newline = regex.sub(r"\s+", " ", speech_text_no_newline)
        # Save the bracket text
        bracket_text = bracket.group()
        # Save deleted text to DataFrame
        contributions_simplified["text_position"].append(
            reversed_text_position if text_position_reversed else text_position
        )
        contributions_simplified["content"].append(bracket_text)
        contributions_simplified["speech_id"].append(identity)

        deletion_span = bracket.span(1)

        # Remove the bracket text from the speech_text and replace it with the text_position
        speech_text = (
            speech_text[: deletion_span[0]]
            + "{"
            + str(reversed_text_position if text_position_reversed else text_position)
            + "}"
            + speech_text[deletion_span[1] :]
        )

        contribution_methods = [
            extract_applause,
            extract_person_interjection,
            extract_shout,
            extract_cheerfulness,
            extract_objection,
            extract_laughter,
            extract_approval,
            extract_interruption,
            extract_disturbance,
        ]

        for method in contribution_methods:
            frame, speech_text_no_newline = method(
                speech_text_no_newline,
                electoral_term,
                session,
                identity,
                reversed_text_position if text_position_reversed else text_position,
                frame,
            )

        text_position += 1

    return (
        pd.DataFrame(frame),
        speech_text,
        pd.DataFrame(contributions_simplified),
        text_position,
    )


# Method Dictionary:
# Keep in mind to lower the keys
methods = {
    "beifall": extract_applause,
    "zuruf": extract_shout,
    "gegenruf": extract_shout,
    "ruf": extract_shout,
    "heiterkeit": extract_cheerfulness,
    "widerspruch": extract_objection,
    "lachen": extract_laughter,
    "zustimmung": extract_approval,
    "unterbrechung": extract_interruption,
    "unruhe": extract_disturbance,
}
