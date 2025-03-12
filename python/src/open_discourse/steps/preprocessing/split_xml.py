import sys
import xml.etree.ElementTree as et

import dicttoxml
import regex
from tqdm import tqdm

from open_discourse.definitions import path
from open_discourse.helper.clean_text import clean
from open_discourse.helper.utils import get_term_from_path

# input directory
RAW_XML = path.RAW_XML

# output directory
RAW_TXT = path.RAW_TXT
RAW_TXT.mkdir(parents=True, exist_ok=True)

# Open every xml plenar file in every legislature period.
for folder_path in sorted(RAW_XML.iterdir()):
    # Skip e.g. the .DS_Store file.
    if not folder_path.is_dir():
        continue

    term_number = get_term_from_path(folder_path)
    if term_number is None:
        print(f"No term number found in {folder_path.stem}.")
        continue

    if not (3 <= term_number <= 19):
        print(
            f"Term number {term_number} is not in range [3, 19]. Skipping for this script"
        )
        continue

    begin_pattern_electoral_term = regex.compile(
        r"Beginn?:?\s?(\d){1,2}(\s?[.,]\s?(\d){1,2})?\s?Uhr"
    )
    appendix_pattern_electoral_term = regex.compile(
        r"\(Schlu(ß|ss)\s?:?(.*?)\d{1,2}\D+(\d{1,2})?(.*?)\)?|\(Ende der Sitzung: \d{1,2}\D+(\d{1,2}) Uhr\.?\)"
    )

    if len(sys.argv) > 1:
        if str(term_number) not in sys.argv:
            continue

    for xml_file_path in tqdm(
        list(folder_path.iterdir()), desc=f"Parsing term {term_number:>2}..."
    ):
        if xml_file_path.suffix == ".xml":
            tree = et.parse(xml_file_path)

            meta_data = {}

            # Get the document number, the date of the session and the content.
            meta_data["document_number"] = tree.find("NR").text
            meta_data["date"] = tree.find("DATUM").text
            text_corpus = tree.find("TEXT").text

            # Some files have issues which have to be handled mannualy
            # like a duplicated text corpus or two sessions in one file.
            if meta_data["document_number"] == "03/16":
                begin_pattern = begin_pattern_electoral_term
                appendix_pattern = regex.compile(
                    r"\(Schluß der Sitzung: 16\.58 Uhr\.\)"
                )
            elif meta_data["document_number"] == "04/69":
                begin_pattern = regex.compile(r"Beginn: 9\.01")
                appendix_pattern = appendix_pattern_electoral_term
            elif meta_data["document_number"] == "04/176":
                begin_pattern = regex.compile(r"Beginn: 16\.02 Uhr")
                appendix_pattern = appendix_pattern_electoral_term
            elif meta_data["document_number"] == "04/196":
                begin_pattern = begin_pattern_electoral_term
                appendix_pattern = regex.compile(
                    r"Beifall.*?Schluß der Sitzung: 14\.54 Uhr\.\)"
                )
            elif meta_data["document_number"] == "05/76":
                begin_pattern = regex.compile(r"\(Beginn: 14\.32 Uhr\)")
                appendix_pattern = appendix_pattern_electoral_term
            elif meta_data["document_number"] == "05/162":
                begin_pattern = regex.compile(r"\(Beginn: 21\.13 Uhr\.\)")
                appendix_pattern = appendix_pattern_electoral_term
            elif meta_data["document_number"] == "05/235":
                begin_pattern = begin_pattern_electoral_term
                appendix_pattern = regex.compile(
                    r"\(Schluß der Sitzung: 16\.09 Uhr\.\)"
                )
            elif meta_data["document_number"] == "07/145":
                # In this file the whole text is duplicated.
                find_bundestag = list(
                    regex.finditer("Deutscher Bundestag\n", text_corpus)
                )
                text_corpus = text_corpus[: find_bundestag[1].span()[0]]
            elif meta_data["document_number"] == "07/243":
                begin_pattern = regex.compile(r"Beginn: 9\.00 Uhr(?=\nPräsident)")
                appendix_pattern = appendix_pattern_electoral_term
            elif meta_data["document_number"] == "08/7":
                begin_pattern = regex.compile(r"Beginn: 9\.00 Uhr(?=\nPräsident)")
                appendix_pattern = appendix_pattern_electoral_term
            elif meta_data["document_number"] == "08/146":
                begin_pattern = regex.compile(r"Beginn: 8\.00 Uhr")
                appendix_pattern = appendix_pattern_electoral_term
            elif meta_data["document_number"] == "11/68":
                begin_pattern = begin_pattern_electoral_term
                appendix_pattern = regex.compile(r"\(Schluß der Sitzung: 21\. 07 Uhr\)")
            elif meta_data["document_number"] == "11/155":
                begin_pattern = regex.compile(r"Beginn: 9\.00 Uhr(?=\nVize)")
                appendix_pattern = appendix_pattern_electoral_term
            elif meta_data["document_number"] == "14/17":
                begin_pattern = "Beginn: 9.00 Uhr"
                appendix_pattern = (
                    r"Schluß: 12.06 Uhr\)\n\nDruck: Bonner Universitäts-Buchdruckerei, 53113 Bonn\n "
                    r"53003 Bonn, Telefon: 02 28/3 82 08 40, Telefax: 02 28/3 82 08 44\n\n20\n\nBun"
                    r"despräsident Dr. Roman Herzog\n\nDeutscher"
                )
            elif meta_data["document_number"] == "14/21":
                begin_pattern = begin_pattern_electoral_term
                appendix_pattern = r"\(Schluß: 22.18 Uhr\)\n\nAdelheid Tröscher\n\n1594"
            elif meta_data["document_number"] == "14/192":
                begin_pattern = begin_pattern_electoral_term
                appendix_pattern = regex.compile(
                    r"Vizepräsidentin Petra Bläss: Ich schließe die Aus-\nsprache\.(?=\n\nInter)"
                )
            elif meta_data["document_number"] == "16/222":
                begin_pattern = begin_pattern_electoral_term
                appendix_pattern = regex.compile(r"\(Schluss: 18\.54 Uhr\)")
            elif meta_data["document_number"] == "17/250":
                begin_pattern = regex.compile(r"Beginn: 9.02 Uhr(?=\nPräsident)")
                appendix_pattern = r"\(Schluss: 0.52 Uhr\)\n\nIch"
            elif meta_data["document_number"] == "18/142":
                begin_pattern = begin_pattern_electoral_term
                appendix_pattern = regex.compile(r"\(Schluss: 16 \.36 Uhr\)")
            elif meta_data["document_number"] == "18/237":
                begin_pattern = regex.compile(r"Beginn: 9 \.02 Uhr")
                appendix_pattern = appendix_pattern_electoral_term
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
                    "(?<=\n)"
                    + meta_data["document_number"][3:]
                    + r"\. Sitzung(?=\nBonn)",
                    text_corpus,
                )
                text_corpus = text_corpus[find_second.span()[0] :]
            else:
                begin_pattern = begin_pattern_electoral_term
                appendix_pattern = appendix_pattern_electoral_term

            # Clean text corpus.
            text_corpus = clean(text_corpus)

            # Find the beginning pattern in plenar file.
            find_beginnings = list(regex.finditer(begin_pattern, text_corpus))

            # If found more than once or none, handle depending on period.
            if len(find_beginnings) != 1:
                continue

            beginning_of_session = find_beginnings[0].span()[1]

            toc = text_corpus[:beginning_of_session]
            session_content = text_corpus[beginning_of_session:]

            # At this point the document has a unique beginning. The spoken
            # content begins after the matched phrase.

            # Append "END OF FILE" to document text, otherwise pattern is
            # not found, when appearing at the end of the file.
            session_content += "\n\nEND OF FILE"

            find_endings = list(regex.finditer(appendix_pattern, session_content))

            if len(find_endings) != 1:
                continue

            # Appendix begins before the matched phrase.
            end_of_session = find_endings[0].span()[0]

            appendix = session_content[end_of_session:]
            session_content = session_content[:end_of_session]

            save_path = RAW_TXT / folder_path.stem / xml_file_path.stem
            save_path.mkdir(parents=True, exist_ok=True)
            # Save table of content, spoken content and appendix
            # in separate files.
            with open(save_path / "toc.txt", "w") as text_file:
                text_file.write(toc)

            with open(save_path / "session_content.txt", "w") as text_file:
                text_file.write(session_content)

            with open(save_path / "appendix.txt", "w") as text_file:
                text_file.write(appendix)

            with open(save_path / "meta_data.xml", "wb") as result_file:
                result_file.write(dicttoxml.dicttoxml(meta_data))

assert RAW_TXT.exists(), f"Output directory {RAW_TXT}does not exist."

print("Script 02_01 done.")
