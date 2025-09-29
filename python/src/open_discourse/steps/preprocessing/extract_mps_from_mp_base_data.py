import logging
import xml.etree.ElementTree as Et
from datetime import datetime

import pandas as pd

from open_discourse.definitions import path
from open_discourse.helper.logging_config import setup_and_get_logger


def is_valid_date(date_string: str, date_format: str = "%d.%m.%Y") -> bool:
    """
    Check if date_string is a valid date acc. to given format

    Args:
        date_string (str): date to check
        date_format (str): format for date check

    Returns:
        bool: True, if date_string is valid, otherwise False.
    """
    try:
        datetime.strptime(date_string, date_format)
        return True
    except ValueError:
        return False


def process_single_mdb(xml_mdb: Et.Element) -> dict:
    """
    Process xml-data of one Member of Parliament (MdB)
    and return dict with the desired subset of data.

    Args:
        xml_mdb (Et.Element):   xml-data of one MP (MdB)

    Returns:
        mps (dict):         dict with data of one MP (MdB)

    """

    mps = {
        "ui": [],
        "electoral_term": [],  # WP
        "first_name": [],  # VORNAME,
        "last_name": [],  # NACHNAME,
        "birth_place": [],  # GEBURTSORT
        "birth_country": [],  # GEBURTSLAND
        "birth_date": [],  # GEBURTSDATUM
        "death_date": [],  # STERBEDATUM
        "gender": [],  # GESCHLECHT
        "profession": [],  # BERUF
        "constituency": [],  # ORTSZUSATZ,
        "aristocracy": [],  # ADEL,
        "academic_title": [],  # AKAD_TITEL,
        "institution_type": [],  # INSART_LANG
        "institution_name": [],  # INS_LANG
    }

    ui = xml_mdb.findtext("ID")
    # These entries exist only once for every politician.

    # Two clauses in if:
    # result is None-> default value is used, result == "" -> Thruthy is False
    birth_date = xml_mdb.findtext("BIOGRAFISCHE_ANGABEN/GEBURTSDATUM", -1) or -1
    if birth_date == -1:
        msg = f"birth_date missing for id {ui}"
        logging.error(msg)
    else:
        birth_date = str(birth_date)
        if not is_valid_date(birth_date):
            logging.error(f"Invalid birth_date {birth_date} for {ui}.")

    birth_place = xml_mdb.findtext("BIOGRAFISCHE_ANGABEN/GEBURTSORT")
    birth_country = (
        xml_mdb.findtext("BIOGRAFISCHE_ANGABEN/GEBURTSLAND", "Deutschland")
        or "Deutschland"
    )

    death_date = xml_mdb.findtext("BIOGRAFISCHE_ANGABEN/STERBEDATUM", -1) or -1
    if not death_date == -1:
        death_date = str(death_date)
        if not is_valid_date(death_date):
            logging.error(f"Invalid death_date {death_date} for {ui}.")

    gender = xml_mdb.findtext("BIOGRAFISCHE_ANGABEN/GESCHLECHT")
    profession = xml_mdb.findtext("BIOGRAFISCHE_ANGABEN/BERUF")

    # Iterate over all name entries for the politician_id, e.g. necessary if
    # name has changed due to a marriage or losing/gaining of titles like "Dr."
    # or if in another period the location information
    # changed "" -> "Bremerhaven"
    for name in xml_mdb.findall("./NAMEN/NAME"):
        first_name = name.findtext("VORNAME")
        last_name = name.findtext("NACHNAME")
        constituency = name.findtext("ORTSZUSATZ")
        aristocracy = name.findtext("ADEL")
        academic_title = name.findtext("AKAD_TITEL")

        # Hardcode Schmidt (Weilburg). Note: This makes 4 entries for Frank Schmidt!
        if "(Weilburg)" in last_name:
            last_name = last_name.replace(" (Weilburg)", "")
            constituency = "(Weilburg)"

        # Iterate over parliament periods the politician was member
        # of the Bundestag.
        for electoral_term in xml_mdb.findall("./WAHLPERIODEN/WAHLPERIODE"):
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

    return mps


# ------------------------------
# processing block
# ------------------------------
def main(task):
    """
    Iterate through every entry in Member of Parliament master data (MDB_STAMMDATEN.XML)
    Create pd.DataFrame with necessary information about every Member of Parliament.
    """
    logger = setup_and_get_logger(__file__, logging.DEBUG)
    logger.info("Script 02_04 start: Process mps...")

    # input directory
    MP_BASE_DATA = path.MP_BASE_DATA
    # output directory
    POLITICIANS_STAGE_01 = path.POLITICIANS_STAGE_01
    POLITICIANS_STAGE_01.mkdir(parents=True, exist_ok=True)
    save_path = POLITICIANS_STAGE_01 / "mps.pkl"

    # read data
    tree = Et.parse(MP_BASE_DATA / "MDB_STAMMDATEN.XML")
    # root = tree.getroot()

    # Iterate over all MDBs (Mitglieder des Bundestages) in XML File.
    df = pd.DataFrame()
    for mdb in tree.iter("MDB"):
        mp_data = process_single_mdb(mdb)
        df_tmp = pd.DataFrame(mp_data)
        df = pd.concat([df, df_tmp], ignore_index=True)

    df["constituency"] = df["constituency"].str.replace("[)(]", "", regex=True)
    df = df.astype(dtype={"ui": "int64", "birth_date": "str", "death_date": "str"})

    df.to_pickle(save_path)

    logger.info("Script 02_04 done.")

    return True


if __name__ == "__main__":
    main("Run 02_04")
