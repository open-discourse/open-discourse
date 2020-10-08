import od_lib.definitions.path_definitions as path_definitions
import pandas as pd
import xml.etree.ElementTree as et
import os
import regex

# input directory
MP_BASE_DATA = path_definitions.MP_BASE_DATA

# output directory
POLITICIANS_STAGE_01 = path_definitions.POLITICIANS_STAGE_01
save_path = os.path.join(POLITICIANS_STAGE_01, "mps.pkl")

if not os.path.exists(POLITICIANS_STAGE_01):
    os.makedirs(POLITICIANS_STAGE_01)

# read data
tree = et.parse(MP_BASE_DATA)
root = tree.getroot()

# placeholder for final dataframe
mps = {
    "ui": [],
    "electoral_term": [],
    "first_name": [],
    "last_name": [],
    "birth_place": [],
    "birth_country": [],
    "birth_year": [],
    "death_year": [],
    "gender": [],
    "profession": [],
    "constituency": [],
    "aristocracy": [],
    "prefix": [],
    "academic_title": [],
    "salutation": [],
    "vita_short": [],
    "disclosure_requirement": [],
    "constituency_number": [],
    "constituency_name": [],
    "constituency_region": [],
    "electoral_list": [],
    "type_of_mandate": [],
    "mp_from": [],
    "mp_until": [],
    "history_from": [],
    "history_until": [],
    "institution_type": [],
    "institution_name": [],
    "institution_member_from": [],
    "institution_member_until": [],
    "function_long": [],
    "function_from": [],
    "function_until": [],
}

last_names_to_revisit = []
i = 0
# Iterate over all MDBs (Mitglieder des Bundestages) in XML File.
for mdb in tree.iter("MDB"):
    ui = mdb.findtext("ID")

    print(ui)

    # This entries exist only once for every politician.
    if mdb.findtext("BIOGRAFISCHE_ANGABEN/GEBURTSDATUM") == "":
        raise ValueError("Politician has to be born at some point.")
    else:
        birth_year = str(mdb.findtext("BIOGRAFISCHE_ANGABEN/GEBURTSDATUM"))

    birth_place = mdb.findtext("BIOGRAFISCHE_ANGABEN/GEBURTSORT")
    birth_country = mdb.findtext("BIOGRAFISCHE_ANGABEN/GEBURTSLAND")
    if birth_country == "":
        birth_country = "Deutschland"

    if mdb.findtext("BIOGRAFISCHE_ANGABEN/STERBEDATUM") == "":
        death_year = -1
    else:
        death_year = str(mdb.findtext("BIOGRAFISCHE_ANGABEN/STERBEDATUM"))

    gender = mdb.findtext("BIOGRAFISCHE_ANGABEN/GESCHLECHT")
    profession = mdb.findtext("BIOGRAFISCHE_ANGABEN/BERUF")
    vita_short = mdb.findtext("BIOGRAFISCHE_ANGABEN/VITA_KURZ")
    disclosure_requirement = mdb.findtext(
        "BIOGRAFISCHE_ANGABEN/VEROEFFENTLICHUNGSPFLICHTIGES"
    )

    # Iterate over all name entries for the poltiician_id, e.g. necessary if
    # name has changed due to a marriage or losing/gaining of titles like "Dr."
    # Or if in another period the location information
    # changed "" -> "Bremerhaven"
    for name in mdb.findall("./NAMEN/NAME"):
        first_name = name.findtext("VORNAME")
        last_name = name.findtext("NACHNAME")
        constituency = name.findtext("ORTSZUSATZ")
        aristocracy = name.findtext("ADEL")
        prefix = name.findtext("PRAEFIX")
        academic_title = name.findtext("AKAD_TITEL")
        salutation = name.findtext("ANREDE_TITEL")
        history_from = name.findtext("HISTORIE_VON")
        history_until = name.findtext("HISTORIE_BIS")

        # Hardcode Schmidt (Weilburg). Note: This makes 4 entries for
        # Frank Schmidt!!
        if regex.search(r"\(Weilburg\)", last_name):
            last_name = last_name.replace(" (Weilburg)", "")
            constituency = "(Weilburg)"

        # Iterate over parliament periods the politician was member
        # of the Bundestag.
        for electoral_term in mdb.findall("./WAHLPERIODEN/WAHLPERIODE"):
            electoral_term_number = electoral_term.findtext("WP")
            mp_from = electoral_term.findtext("MDBWP_VON")
            mp_until = electoral_term.findtext("MDBWP_BIS")
            constituency_number = electoral_term.findtext("WKR_NUMMER")
            constituency_name = electoral_term.findtext("WKR_NAME")
            constituency_region = electoral_term.findtext("WKR_LAND")
            electoral_list = electoral_term.findtext("LISTE")
            type_of_mandate = electoral_term.findtext("MANDATSART")

            # Iterate over faction membership in each parliament period, e.g.
            # multiple entries exist if faction was changed within period.
            for institution in electoral_term.findall("./INSTITUTIONEN/INSTITUTION"):
                institution_name = institution.findtext("INS_LANG")
                institution_type = institution.findtext("INSART_LANG")
                institution_member_from = institution.findtext("MDBINS_VON")
                institution_member_until = institution.findtext("MDBINS_BIS")
                function_long = institution.findtext("FKT_LANG")
                function_from = institution.findtext("FKTINS_VON")
                function_until = institution.findtext("FKTINS_BIS")

                mps["ui"].append(ui)
                mps["electoral_term"].append(electoral_term_number)
                mps["first_name"].append(first_name)
                mps["last_name"].append(last_name)
                mps["birth_place"].append(birth_place)
                mps["birth_country"].append(birth_country)
                mps["birth_year"].append(birth_year)
                mps["death_year"].append(death_year)
                mps["gender"].append(gender)
                mps["profession"].append(profession)
                mps["constituency"].append(constituency)
                mps["aristocracy"].append(aristocracy)
                mps["prefix"].append(prefix)
                mps["academic_title"].append(academic_title)
                mps["salutation"].append(salutation)
                mps["vita_short"].append(vita_short)
                mps["disclosure_requirement"].append(disclosure_requirement)
                mps["history_from"].append(history_from)
                mps["history_until"].append(history_until)
                mps["constituency_number"].append(constituency_number)
                mps["constituency_name"].append(constituency_name)
                mps["constituency_region"].append(constituency_region)
                mps["electoral_list"].append(electoral_list)
                mps["type_of_mandate"].append(type_of_mandate)
                mps["mp_from"].append(mp_from)
                mps["mp_until"].append(mp_until)

                mps["institution_type"].append(institution_type)
                mps["institution_name"].append(institution_name)
                mps["institution_member_from"].append(institution_member_from)
                mps["institution_member_until"].append(institution_member_until)

                mps["function_long"].append(function_long)
                mps["function_from"].append(function_from)
                mps["function_until"].append(function_until)


mps = pd.DataFrame(mps)
mps.constituency = mps.constituency.str.replace("[)(]", "")
mps = mps.astype(dtype={"ui": "int64", "birth_year": "str", "death_year": "str"})

# Convert to date stamp
mps.history_from = pd.to_datetime(mps.history_from).dt.date
mps.history_until = pd.to_datetime(mps.history_until).dt.date
mps.mp_from = pd.to_datetime(mps.mp_from).dt.date
mps.mp_until = pd.to_datetime(mps.mp_until).dt.date
mps.function_from = pd.to_datetime(mps.function_from).dt.date
mps.function_until = pd.to_datetime(mps.function_until).dt.date
mps.institution_member_from = pd.to_datetime(mps.institution_member_from).dt.date
mps.institution_member_until = pd.to_datetime(mps.institution_member_until).dt.date

mps.to_pickle(save_path)
