import pandas as pd
import xml.etree.ElementTree as et
import os
import sys
import regex

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))
import path_definitions

# input directory ______________________________________________________________
STAMMDATEN_XML = path_definitions.STAMMDATEN_XML

# output directory _____________________________________________________________
POLITICIANS_STAGE_01 = path_definitions.POLITICIANS_STAGE_01
save_path = os.path.join(POLITICIANS_STAGE_01, "mdbs.pkl")

if not os.path.exists(POLITICIANS_STAGE_01):
    os.makedirs(POLITICIANS_STAGE_01)

# read data ____________________________________________________________________
tree = et.parse(STAMMDATEN_XML)
root = tree.getroot()

# placeholder for final dataframe ______________________________________________
politicians = {
    "ui": [],
    "wp_period": [],
    "first_name": [],
    "last_name": [],
    "birth_place": [],
    "birth_country": [],
    "birth_year": [],
    "death_year": [],
    "gender": [],
    "profession": [],
    "location_information": [],
    "aristocracy": [],
    "prefix": [],
    "academic_title": [],
    "salutation": [],
    "vita_short": [],
    "disclosure_requirement": [],
    "electoral_district_number": [],
    "electoral_district_name": [],
    "electoral_district_region": [],
    "electoral_list": [],
    "type_of_mandate": [],
    "mdb_from": [],
    "mdb_until": [],
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
# Iterate over all MDBs (Mitglieder des Bundestages) in XML File. ______________
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
    # last_party_membership = mdb.findtext("BIOGRAFISCHE_ANGABEN/PARTEI_KURZ")
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
        location_information = name.findtext("ORTSZUSATZ")
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
            location_information = "(Weilburg)"

        # Iterate over parliament periods the politician was member
        # of the Bundestag.
        for wp in mdb.findall("./WAHLPERIODEN/WAHLPERIODE"):
            wp_number = wp.findtext("WP")
            mdb_from = wp.findtext("MDBWP_VON")
            mdb_until = wp.findtext("MDBWP_BIS")
            electoral_district_number = wp.findtext("WKR_NUMMER")
            electoral_district_name = wp.findtext("WKR_NAME")
            electoral_district_region = wp.findtext("WKR_LAND")
            electoral_list = wp.findtext("LISTE")
            type_of_mandate = wp.findtext("MANDATSART")

            # Iterate over faction membership in each parliament period, e.g.
            # multiple entries exist if faction was changed within period.
            for institution in wp.findall("./INSTITUTIONEN/INSTITUTION"):
                institution_name = institution.findtext("INS_LANG")
                institution_type = institution.findtext("INSART_LANG")
                institution_member_from = institution.findtext("MDBINS_VON")
                institution_member_until = institution.findtext("MDBINS_BIS")
                function_long = institution.findtext("FKT_LANG")
                function_from = institution.findtext("FKTINS_VON")
                function_until = institution.findtext("FKTINS_BIS")

                politicians["ui"].append(ui)
                politicians["wp_period"].append(wp_number)
                politicians["first_name"].append(first_name)
                politicians["last_name"].append(last_name)
                politicians["birth_place"].append(birth_place)
                politicians["birth_country"].append(birth_country)
                politicians["birth_year"].append(birth_year)
                politicians["death_year"].append(death_year)
                politicians["gender"].append(gender)
                politicians["profession"].append(profession)
                politicians["location_information"].append(location_information)
                politicians["aristocracy"].append(aristocracy)
                politicians["prefix"].append(prefix)
                politicians["academic_title"].append(academic_title)
                politicians["salutation"].append(salutation)
                politicians["vita_short"].append(vita_short)
                politicians["disclosure_requirement"].append(disclosure_requirement)
                politicians["history_from"].append(history_from)
                politicians["history_until"].append(history_until)
                politicians["electoral_district_number"].append(
                    electoral_district_number
                )
                politicians["electoral_district_name"].append(electoral_district_name)
                politicians["electoral_district_region"].append(
                    electoral_district_region
                )
                politicians["electoral_list"].append(electoral_list)
                politicians["type_of_mandate"].append(type_of_mandate)
                politicians["mdb_from"].append(mdb_from)
                politicians["mdb_until"].append(mdb_until)

                politicians["institution_type"].append(institution_type)
                politicians["institution_name"].append(institution_name)
                politicians["institution_member_from"].append(institution_member_from)
                politicians["institution_member_until"].append(institution_member_until)

                politicians["function_long"].append(function_long)
                politicians["function_from"].append(function_from)
                politicians["function_until"].append(function_until)


politicians = pd.DataFrame(politicians)
politicians.location_information = politicians.location_information.str.replace(
    "[)(]", ""
)
politicians = politicians.astype(
    dtype={"ui": "int64", "birth_year": "str", "death_year": "str"}
)

# Convert to date stamp
politicians.history_from = pd.to_datetime(politicians.history_from).dt.date
politicians.history_until = pd.to_datetime(politicians.history_until).dt.date
politicians.mdb_from = pd.to_datetime(politicians.mdb_from).dt.date
politicians.mdb_until = pd.to_datetime(politicians.mdb_until).dt.date
politicians.function_from = pd.to_datetime(politicians.function_from).dt.date
politicians.function_until = pd.to_datetime(politicians.function_until).dt.date
politicians.institution_member_from = pd.to_datetime(
    politicians.institution_member_from
).dt.date
politicians.institution_member_until = pd.to_datetime(
    politicians.institution_member_until
).dt.date

politicians.to_pickle(save_path)
