import logging
import xml.etree.ElementTree as Et
from pathlib import Path
from xml.etree.ElementTree import ParseError

import dicttoxml
import regex
from tqdm import tqdm

from open_discourse.definitions import path
from open_discourse.helper.clean_text import clean
from open_discourse.helper.create_electoral_terms import create_electoral_terms
from open_discourse.helper.logging_config import setup_and_get_logger
from open_discourse.helper.session_file_iterator import session_file_iterator


def split_single_session_xml_data(xml_file_path: Path) -> tuple:
    """
    Open a session protocol xml-file and split content into metadata and text corpus.
    Raise ParseError resp. ValueError when xml-content cannot be processed properly
    or expected tags are missing.

    Args:
        xml_file_path (Path): Path to single session protocol xml-file

    Returns:
        meta_data (dict):   Metadata of current xml-file
        text_corpus (str):  Content of tag <TEXT> of current xml-file
    """

    # Cancel if not xml file, this case should not occur
    if (not xml_file_path.is_file()) or xml_file_path.suffix != ".xml":
        msg = f"xml file expected {xml_file_path}"
        logging.error(msg)
        raise FileNotFoundError(msg)

    meta_data = {}
    text_corpus = None

    try:
        tree = Et.parse(xml_file_path)
    except ParseError:
        msg = "xml ParseError" + str(xml_file_path)
        logging.error(msg)
        raise

    try:
        meta_data["term"] = tree.find("WAHLPERIODE").text
        meta_data["document_type"] = tree.find("DOKUMENTART").text
        # Get the document number, the date of the session and the content.
        meta_data["document_number"] = tree.find("NR").text
        meta_data["date"] = tree.find("DATUM").text
        text_corpus = tree.find("TEXT").text
    except AttributeError:
        msg = "xml AttributeError" + str(xml_file_path)
        logging.error(msg)
        raise

    # Are filename and meta_data consistent?
    if (
        xml_file_path.stem != f"{int(meta_data['term']):02d}"
        f"{int(meta_data['document_number'].split('/')[1]):03d}"
    ):
        msg = (
            f"meta_data / filepath not consistent: {str(xml_file_path)} "
            f"{meta_data['document_number']}"
        )
        logging.warning(msg)

    return meta_data, text_corpus


def define_single_session_regex_pattern(meta_data: dict) -> tuple:
    """
    Define regex pattern for finding begin of speech_content respectively appendix
    of a session protocol.
    Based on a standard case, various exceptions from
    individual protocols (based on meta_data["document_number"]) are taken into account.

    Args:
        meta_data (dict):   Metadata of current xml-file

    Returns:
        begin_pattern (compiled regex):     regex pattern for begin of speech content
        appendix_pattern (compiled regex):  regex pattern for appendix

    """
    begin_pattern_electoral_term = r"Beginn?:?\s?(\d){1,2}(\s?[.,]\s?(\d){1,2})?\s?Uhr"
    appendix_pattern_electoral_term = (
        r"\(Schlu(ß|ss)\s?:?(.*?)\d{1,2}\D+(\d{1,"
        r"2})?(.*?)\)?|\(Ende der Sitzung: \d{1,"
        r"2}\D+(\d{1,2}) Uhr\.?\)"
    )

    begin_pattern = begin_pattern_electoral_term
    appendix_pattern = appendix_pattern_electoral_term

    # Some files have issues which have to be handled manually
    # like a duplicated text corpus or two sessions in one file.
    # change begin_pattern / appendix_patern only when different to default
    if meta_data["document_number"] == "03/16":
        appendix_pattern = r"\(Schluß der Sitzung: 16\.58 Uhr\.\)"
    elif meta_data["document_number"] == "04/69":
        begin_pattern = r"Beginn: 9\.01"
    elif meta_data["document_number"] == "04/176":
        begin_pattern = r"Beginn: 16\.02 Uhr"
    elif meta_data["document_number"] == "04/196":
        appendix_pattern = r"Beifall.*?Schluß der Sitzung: 14\.54 Uhr\.\)"
    elif meta_data["document_number"] == "05/76":
        begin_pattern = r"\(Beginn: 14\.32 Uhr\)"
    elif meta_data["document_number"] == "05/162":
        begin_pattern = r"\(Beginn: 21\.13 Uhr\.\)"
    elif meta_data["document_number"] == "05/235":
        appendix_pattern = r"\(Schluß der Sitzung: 16\.09 Uhr\.\)"
    elif meta_data["document_number"] == "07/243":
        begin_pattern = r"Beginn: 9\.00 Uhr(?=\nPräsident)"
    elif meta_data["document_number"] == "08/7":
        begin_pattern = r"Beginn: 9\.00 Uhr(?=\nPräsident)"
    elif meta_data["document_number"] == "08/146":
        begin_pattern = r"Beginn: 8\.00 Uhr"
    elif meta_data["document_number"] == "11/68":
        appendix_pattern = r"\(Schluß der Sitzung: 21\. 07 Uhr\)"
    elif meta_data["document_number"] == "11/155":
        begin_pattern = r"Beginn: 9\.00 Uhr(?=\nVize)"
    elif meta_data["document_number"] == "14/17":
        begin_pattern = "Beginn: 9.00 Uhr"
        appendix_pattern = (
            r"Schluß: 12.06 Uhr\)\n\nDruck: Bonner Universitäts-Buchdruckerei, 53113 "
            r"Bonn\n 53003 Bonn, Telefon: 02 28/3 82 08 40, Telefax: 02 28/3 82 08 "
            r"44\n\n20\n\nBundespräsident Dr. Roman Herzog\n\nDeutscher"
        )
    elif meta_data["document_number"] == "14/21":
        appendix_pattern = r"\(Schluß: 22.18 Uhr\)\n\nAdelheid Tröscher\n\n1594"
    elif meta_data["document_number"] == "14/192":
        appendix_pattern = r"Vizepräsidentin Petra Bläss: Ich schließe die "
        appendix_pattern += r"Aus-\nsprache\.(?=\n\nInter)"
    elif meta_data["document_number"] == "16/222":
        appendix_pattern = r"\(Schluss: 18\.54 Uhr\)"
    elif meta_data["document_number"] == "17/250":
        begin_pattern = r"Beginn: 9.02 Uhr(?=\nPräsident)"
        appendix_pattern = r"\(Schluss: 0.52 Uhr\)\n\nIch"
    elif meta_data["document_number"] == "18/142":
        appendix_pattern = r"\(Schluss: 16 \.36 Uhr\)"
    elif meta_data["document_number"] == "18/237":
        begin_pattern = r"Beginn: 9 \.02 Uhr"

    # return compiled regex
    begin_pattern = regex.compile(begin_pattern)
    appendix_pattern = regex.compile(appendix_pattern)

    return begin_pattern, appendix_pattern


def single_session_special_text_split(meta_data: dict, text_corpus: str) -> str:
    """
    Change the content of text_corpus for some special cases (e.g. duplicated text
    corpus or two sessions in one protocol),
    dependent from meta_data["document_number"].
    In the standard case, text_corpus is returned unchanged.

    Args:
        meta_data (dict):   Metadata of current xml-file
        text_corpus (str):  Content of tag <TEXT> of current xml-file

    Returns:
        text_corpus (str):  Improved content of tag <TEXT> of current xml-file

    """
    # Some files have issues which have to be handled manually
    # like a duplicated text corpus or two sessions in one file.
    if meta_data["document_number"] == "07/145":
        # In this file the whole text is duplicated.
        find_bundestag = list(regex.finditer("Deutscher Bundestag\n", text_corpus))
        text_corpus = text_corpus[: find_bundestag[1].span()[0]]
    elif meta_data["document_number"] in [
        "03/97",
        "04/66",
        "04/87",
        "04/112",
        "05/47",
        "05/232",
    ]:
        # In these documents there are two sessions right after each
        # other, and the following document is identical.
        find_second = regex.search(
            "(?<=\n)"
            + str(int(meta_data["document_number"][3:]) + 1)
            + r"\. Sitzung(?=\nBonn)",
            text_corpus,
        )
        text_corpus = text_corpus[: find_second.span()[0]]
    elif meta_data["document_number"] in [
        "03/98",
        "04/67",
        "04/88",
        "04/113",
        "05/48",
        "05/233",
    ]:
        find_second = regex.search(
            "(?<=\n)" + meta_data["document_number"][3:] + r"\. Sitzung(?=\nBonn)",
            text_corpus,
        )
        text_corpus = text_corpus[find_second.span()[0] :]

    return text_corpus


def main(task):
    logger = setup_and_get_logger(__file__, logging.DEBUG)
    logger.info("Script 02_01 starts")

    # input directory
    RAW_XML = path.RAW_XML

    # output directory
    RAW_TXT = path.RAW_TXT
    RAW_TXT.mkdir(parents=True, exist_ok=True)

    # iterate through entire data or select term or session
    # by default the iterator process from electoral term 3 until the last completed
    # electoral term
    electoral_terms = create_electoral_terms()
    max_term = max(electoral_terms)
    while electoral_terms[max_term]["number_of_sessions"] is None:
        max_term -= 1
        if max_term < 1:
            msg = "No valid completed electoral term found. Check SESSIONS_PER_TERM."
            raise ValueError(msg)
    # change here for testing with single terms or sessions
    # for input_file_path in tqdm(session_file_iterator(RAW_XML,4, 19)):
    logger.debug("Processing electoral terms from 3 to %s.", max_term)
    for input_file_path in tqdm(session_file_iterator(RAW_XML, (3, max_term))):
        # ========================================
        # 1 split xml
        # ========================================
        try:
            meta_data, text_corpus = split_single_session_xml_data(input_file_path)
        except ParseError:
            continue  # logs are written in func
        # ========================================
        # 2 define regex patterns
        # ========================================
        begin_pattern, appendix_pattern = define_single_session_regex_pattern(meta_data)
        # ========================================
        # 3 special cases with text split
        # ========================================
        text_corpus = single_session_special_text_split(meta_data, text_corpus)
        # ========================================
        # 4 clean text corpus.
        # ========================================
        text_corpus = clean(text_corpus)
        # ========================================
        # 5 Find the beginning pattern in session protocol
        # ========================================
        find_beginnings = list(regex.finditer(begin_pattern, text_corpus))

        # If found more than once or none, handle depending on period.
        if len(find_beginnings) != 1:
            msg = (
                f"found {len(find_beginnings)} beginnings, 1 is expected in "
                f"{input_file_path.name}. No files written."
            )
            logging.warning(msg)
            continue

        beginning_of_session = find_beginnings[0].span()[1]

        toc = text_corpus[:beginning_of_session]
        session_content = text_corpus[beginning_of_session:]
        # At this point the document has a unique beginning. The spoken
        # content begins after the matched phrase.

        # ========================================
        # 6 Find the ending pattern in session protocol
        # ========================================
        # Append "END OF FILE" to document text, otherwise pattern is
        # not found, when appearing at the end of the file.
        session_content += "\n\nEND OF FILE"

        find_endings = list(regex.finditer(appendix_pattern, session_content))

        if len(find_endings) != 1:
            msg = (
                f"found {len(find_endings)} endings, 1 is expected in "
                f"{input_file_path.name}. No files written."
            )
            logging.warning(msg)
            continue

        # Appendix begins before the matched phrase.
        end_of_session = find_endings[0].span()[0]

        appendix = session_content[end_of_session:]
        session_content = session_content[:end_of_session]

        # ========================================
        # 7 write files
        # ========================================
        output_dir_path = RAW_TXT / input_file_path.parent.stem / input_file_path.stem
        output_dir_path.mkdir(parents=True, exist_ok=True)

        # Save table of content, spoken content and appendix in separate files
        with open(output_dir_path / "toc.txt", "w", encoding="utf-8") as text_file:
            text_file.write(toc)

        with open(
            output_dir_path / "session_content.txt", "w", encoding="utf-8"
        ) as text_file:
            text_file.write(session_content)

        with open(output_dir_path / "appendix.txt", "w", encoding="utf-8") as text_file:
            text_file.write(appendix)

        # Dictionary Comprehension to reduce meta_data
        keys_to_keep = ["document_number", "date"]
        meta_data_short = {k: meta_data[k] for k in keys_to_keep if k in meta_data}

        # other loglevel for dicttoxml!
        logging.getLogger("dicttoxml").setLevel(logging.WARNING)
        with open(output_dir_path / "meta_data.xml", "wb") as result_file:
            result_file.write(dicttoxml.dicttoxml(meta_data_short))

        # above writes successful?
        for file_name in [
            "toc.txt",
            "session_content.txt",
            "appendix.txt",
            "meta_data.xml",
        ]:
            file_path = Path(output_dir_path / file_name)
            if not file_path.exists():
                msg = f"pp{input_file_path.stem}: File {file_name} not written."
                logging.error(msg)

    logging.info("Script 02_01 ends")


if __name__ == "__main__":
    main(None)
