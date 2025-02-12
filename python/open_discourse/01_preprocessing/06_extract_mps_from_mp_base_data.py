import xml.etree.ElementTree as et

import pandas as pd
import regex

import open_discourse.definitions.path_definitions as path_definitions

# input directory
MP_BASE_DATA = path_definitions.MP_BASE_DATA

# output directory
POLITICIANS_STAGE_01 = path_definitions.POLITICIANS_STAGE_01
POLITICIANS_STAGE_01.mkdir(parents=True, exist_ok=True)
save_path = POLITICIANS_STAGE_01 / "mps.pkl"

print("Process mps...", end="", flush=True)
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
    "birth_date": [],
    "death_date": [],
    "gender": [],
    "profession": [],
    "constituency": [],
    "aristocracy": [],
    "academic_title": [],
    "institution_type": [],
    "institution_name": [],
}

last_names_to_revisit = []
i = 0
# Iterate over all MDBs (Mitglieder des Bundestages) in XML File.
for mdb in tree.iter("MDB"):
    ui = mdb.findtext("ID")

    # This entries exist only once for every politician.
    if mdb.findtext("BIOGRAFISCHE_ANGABEN/GEBURTSDATUM") == "":
        raise ValueError("Politician has to be born at some point.")
    else:
        birth_date = str(mdb.findtext("BIOGRAFISCHE_ANGABEN/GEBURTSDATUM"))

    birth_place = mdb.findtext("BIOGRAFISCHE_ANGABEN/GEBURTSORT")
    birth_country = mdb.findtext("BIOGRAFISCHE_ANGABEN/GEBURTSLAND")
    if birth_country == "":
        birth_country = "Deutschland"

    if mdb.findtext("BIOGRAFISCHE_ANGABEN/STERBEDATUM") == "":
        death_date = -1
    else:
        death_date = str(mdb.findtext("BIOGRAFISCHE_ANGABEN/STERBEDATUM"))

    gender = mdb.findtext("BIOGRAFISCHE_ANGABEN/GESCHLECHT")
    profession = mdb.findtext("BIOGRAFISCHE_ANGABEN/BERUF")

    # Iterate over all name entries for the poltiician_id, e.g. necessary if
    # name has changed due to a marriage or losing/gaining of titles like "Dr."
    # Or if in another period the location information
    # changed "" -> "Bremerhaven"
    for name in mdb.findall("./NAMEN/NAME"):
        first_name = name.findtext("VORNAME")
        last_name = name.findtext("NACHNAME")
        constituency = name.findtext("ORTSZUSATZ")
        aristocracy = name.findtext("ADEL")
        academic_title = name.findtext("AKAD_TITEL")

        # Hardcode Schmidt (Weilburg). Note: This makes 4 entries for
        # Frank Schmidt!!
        if regex.search(r"\(Weilburg\)", last_name):
            last_name = last_name.replace(" (Weilburg)", "")
            constituency = "(Weilburg)"

        # Iterate over parliament periods the politician was member
        # of the Bundestag.
        for electoral_term in mdb.findall("./WAHLPERIODEN/WAHLPERIODE"):
            electoral_term_number = electoral_term.findtext("WP")

            # Iterate over faction membership in each parliament period, e.g.
            # multiple entries exist if faction was changed within period.
            for institution in electoral_term.findall("./INSTITUTIONEN/INSTITUTION"):
                institution_name = institution.findtext("INS_LANG")
                institution_type = institution.findtext("INSART_LANG")

                mps["ui"].append(ui)
                mps["electoral_term"].append(electoral_term_number)
                mps["first_name"].append(first_name)
                mps["last_name"].append(last_name)
                mps["birth_place"].append(birth_place)
                mps["birth_country"].append(birth_country)
                mps["birth_date"].append(birth_date)
                mps["death_date"].append(death_date)
                mps["gender"].append(gender)
                mps["profession"].append(profession)
                mps["constituency"].append(constituency)
                mps["aristocracy"].append(aristocracy)
                mps["academic_title"].append(academic_title)

                mps["institution_type"].append(institution_type)
                mps["institution_name"].append(institution_name)


mps = pd.DataFrame(mps)
mps["constituency"] = mps["constituency"].str.replace("[)(]", "", regex=True)
mps = mps.astype(dtype={"ui": "int64", "birth_date": "str", "death_date": "str"})

mps.to_pickle(save_path)
print("Done.")
