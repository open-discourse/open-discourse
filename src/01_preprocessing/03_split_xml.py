import xml.etree.ElementTree as et
import os
import regex
import dicttoxml
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))
from src.helper_functions.clean_text import clean
import path_definitions

# input directory ______________________________________________________________
RAW_XML = path_definitions.RAW_XML

# output directory _____________________________________________________________
RAW_TXT = path_definitions.RAW_TXT

if not os.path.exists(RAW_TXT):
    os.makedirs(RAW_TXT)

beginning_pattern_not_found = []
beginning_pattern_too_often = []
appendix_pattern_not_found = []
appendix_pattern_too_often = []
other_cases = []

# Open every xml plenar file in every legislature period.
for wp_folder in sorted(os.listdir(RAW_XML)):
    wp_folder_path = os.path.join(RAW_XML, wp_folder)

    # Skip e.g. the .DS_Store file.  ___________________________________________
    if not os.path.isdir(wp_folder_path):
        continue

    if wp_folder in ["wp_01", "wp_02"]:
        continue

    elif wp_folder in [
        "wp_03",
        "wp_04",
        "wp_05",
        "wp_06",
        "wp_07",
        "wp_08",
        "wp_09",
        "wp_10",
        "wp_11",
        "wp_12",
        "wp_13",
        "wp_14",
        "wp_15",
        "wp_16",
        "wp_17",
        "wp_18",
    ]:
        begin_pattern_wp = regex.compile(
            r"Beginn?:?\s?(\d){1,2}(\s?[.,]\s?(\d){1,2})?\s?Uhr"
        )

        appendix_pattern_wp = regex.compile(
            r"\(Schlu(ß|ss)\s?:?(.*?)\d{1,2}\D+(\d{1,2})?(.*?)\)?|\(Ende der Sitzung: \d{1,2}\D+(\d{1,2}) Uhr\.?\)"
        )

    else:
        raise ValueError("How did I come here?")

    if len(sys.argv) > 1:
        if str(int(regex.sub("wp_", "", wp_folder))) not in sys.argv:
            continue

    print(wp_folder)

    for xml_plenar_file in sorted(os.listdir(wp_folder_path)):
        if ".xml" in xml_plenar_file:
            print(xml_plenar_file)
            path = os.path.join(wp_folder_path, xml_plenar_file)
            tree = et.parse(path)

            meta_data = {}

            # Get the document number, the date of the sitting and the content.
            meta_data["document_number"] = tree.find("NR").text
            meta_data["date"] = tree.find("DATUM").text
            text_corpus = tree.find("TEXT").text

            # __________________________________________________________________
            # Some files have issues which have to be handled mannualy
            # like a duplicated text corpus or two sittings in one file.
            if meta_data["document_number"] == "03/16":
                begin_pattern = begin_pattern_wp
                appendix_pattern = regex.compile(
                    r"\(Schluß der Sitzung: 16\.58 Uhr\.\)"
                )
            elif meta_data["document_number"] == "04/69":
                begin_pattern = regex.compile(r"Beginn: 9\.01")
                appendix_pattern = appendix_pattern_wp
            elif meta_data["document_number"] == "04/176":
                begin_pattern = regex.compile(r"Beginn: 16\.02 Uhr")
                appendix_pattern = appendix_pattern_wp
            elif meta_data["document_number"] == "04/196":
                begin_pattern = begin_pattern_wp
                appendix_pattern = regex.compile(
                    r"Beifall.*?Schluß der Sitzung: 14\.54 Uhr\.\)"
                )
            elif meta_data["document_number"] == "05/76":
                begin_pattern = regex.compile(r"\(Beginn: 14\.32 Uhr\)")
                appendix_pattern = appendix_pattern_wp
            elif meta_data["document_number"] == "05/162":
                begin_pattern = regex.compile(r"\(Beginn: 21\.13 Uhr\.\)")
                appendix_pattern = appendix_pattern_wp
            elif meta_data["document_number"] == "05/235":
                begin_pattern = begin_pattern_wp
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
                appendix_pattern = appendix_pattern_wp
            elif meta_data["document_number"] == "08/7":
                begin_pattern = regex.compile(r"Beginn: 9\.00 Uhr(?=\nPräsident)")
                appendix_pattern = appendix_pattern_wp
            elif meta_data["document_number"] == "08/146":
                begin_pattern = regex.compile(r"Beginn: 8\.00 Uhr")
                appendix_pattern = appendix_pattern_wp
            elif meta_data["document_number"] == "11/68":
                other_cases.append(
                    (
                        meta_data["document_number"],
                        "The ending line is deleted in the cleaning part.",
                    )
                )
                begin_pattern = begin_pattern_wp
                appendix_pattern = regex.compile(r"\(Schluß der Sitzung: 21\. 07 Uhr\)")
            elif meta_data["document_number"] == "11/155":
                begin_pattern = regex.compile(r"Beginn: 9\.00 Uhr(?=\nVize)")
                appendix_pattern = appendix_pattern_wp
            elif meta_data["document_number"] == "14/17":
                other_cases.append(
                    (
                        meta_data["document_number"],
                        "14/17: This sitting has a 'Gedenkstunde'",
                    )
                )
                begin_pattern = "Beginn: 9.00 Uhr"
                appendix_pattern = (
                    "Schluß: 12.06 Uhr\)\n\nDruck: Bonner Universitäts-Buchdruckerei, 53113 Bonn\n "
                    "53003 Bonn, Telefon: 02 28/3 82 08 40, Telefax: 02 28/3 82 08 44\n\n20\n\nBun"
                    "despräsident Dr. Roman Herzog\n\nDeutscher"
                )
            elif meta_data["document_number"] == "14/21":
                begin_pattern = begin_pattern_wp
                appendix_pattern = "\(Schluß: 22.18 Uhr\)\n\nAdelheid Tröscher\n\n1594"
            # find_dupl_text = list(regex.finditer("den DM\. Jetzt wollen Sie nur noch 2\,289 Milliarden DM\nansetzen\. Das ist nicht zu akzeptieren\.\n"))
            # delete_begin = find_dupl_text[0].span()[0]
            # delete_end = find_dupl_text[1].span()[0]
            # text_corpus = text_corpus[:delete_begin] + text_corpus[delete_end:]
            # elif meta_data["document_number"] == "14/169":
            #     other_cases.append((meta_data["document_number"], "file 14/169 is broken"))
            #     continue
            elif meta_data["document_number"] == "14/192":
                begin_pattern = begin_pattern_wp
                appendix_pattern = regex.compile(
                    r"Vizepräsidentin Petra Bläss: Ich schließe die Aus-\nsprache\.(?=\n\nInter)"
                )
            elif meta_data["document_number"] == "16/222":
                begin_pattern = begin_pattern_wp
                appendix_pattern = regex.compile(r"\(Schluss: 18\.54 Uhr\)")
            elif meta_data["document_number"] == "17/250":
                begin_pattern = regex.compile(r"Beginn: 9.02 Uhr(?=\nPräsident)")
                appendix_pattern = "\(Schluss: 0.52 Uhr\)\n\nIch"
            elif meta_data["document_number"] == "18/142":
                begin_pattern = begin_pattern_wp
                appendix_pattern = regex.compile(r"\(Schluss: 16 \.36 Uhr\)")
            elif meta_data["document_number"] == "18/237":
                begin_pattern = regex.compile(r"Beginn: 9 \.02 Uhr")
                appendix_pattern = appendix_pattern_wp
            elif meta_data["document_number"] in [
                "03/97",
                "04/66",
                "04/87",
                "04/112",
                "05/47",
                "05/232",
            ]:
                # In these documents there are two sittings right after each
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
                begin_pattern = begin_pattern_wp
                appendix_pattern = appendix_pattern_wp

            # Clean text corpus. _______________________________________________
            text_corpus = clean(text_corpus)

            # Find the beginning pattern in plenar file. _______________________
            find_beginnings = list(regex.finditer(begin_pattern, text_corpus))

            # If found more than once, handle depending on period.
            if len(find_beginnings) > 1:
                beginning_pattern_too_often.append(meta_data["document_number"])
                continue

            elif len(find_beginnings) == 0:
                beginning_pattern_not_found.append(meta_data["document_number"])
                continue

            begin_of_sitting = find_beginnings[0].span()[1]

            toc = text_corpus[:begin_of_sitting]
            spoken_content = text_corpus[begin_of_sitting:]

            # ___________________________________________________________________
            # At this point the document has a unique beginning. The spoken
            # content begins after the matched phrase.

            # Append "END OF FILE" to document text, otherwise pattern is
            # not found, when appearing at the end of the file.
            spoken_content += "\n\nEND OF FILE"

            find_endings = list(regex.finditer(appendix_pattern, spoken_content))

            if len(find_endings) > 1:
                appendix_pattern_too_often.append(meta_data["document_number"])
                continue
            elif len(find_endings) == 0:
                appendix_pattern_not_found.append(meta_data["document_number"])
                continue

            # Appendix begins before the matched phrase.
            end_of_sitting = find_endings[0].span()[0]

            appendix = spoken_content[end_of_sitting:]
            spoken_content = spoken_content[:end_of_sitting]

            save_path = os.path.join(
                RAW_TXT, wp_folder, xml_plenar_file.replace(".xml", "")
            )

            # Save table of content, spoken content and appendix
            # in separate folders.
            if not os.path.exists(save_path):
                os.makedirs(save_path)

            with open(os.path.join(save_path, "toc.txt"), "w") as text_file:
                text_file.write(toc)

            with open(os.path.join(save_path, "spoken_content.txt"), "w") as text_file:
                text_file.write(spoken_content)

            with open(os.path.join(save_path, "appendix.txt"), "w") as text_file:
                text_file.write(appendix)

            with open(os.path.join(save_path, "meta_data.xml"), "wb") as result_file:
                result_file.write(dicttoxml.dicttoxml(meta_data))


print("____ Beginning Not Found ____", *beginning_pattern_not_found, sep="\n")
print("____ Beginning Too Often ____", *beginning_pattern_too_often, sep="\n")
print("____ End Not Found ____", *appendix_pattern_not_found, sep="\n")
print("____ End Too Often ____", *appendix_pattern_too_often, sep="\n")
print("____ Other cases ____", *other_cases, sep="\n")
