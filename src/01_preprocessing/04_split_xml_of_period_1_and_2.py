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

i = 0
# Open every xml plenar file in every legislature period.
for wp_folder in sorted(os.listdir(RAW_XML)):
    wp_folder_path = os.path.join(RAW_XML, wp_folder)

    # Skip e.g. the .DS_Store file.  ___________________________________________
    if not os.path.isdir(wp_folder_path):
        continue

    if wp_folder not in ["wp_01", "wp_02"]:
        continue

    begin_pattern = regex.compile(
        "Die.*?Sitzung.*?wird.*?\d{1,2}.*?Uhr.*?(durch.*?den.*?)?eröffnet"
    )
    appendix_pattern = regex.compile("\(Schluß.*?Sitzung.*?Uhr.*?\)")

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

            # Clean text corpus. _______________________________________________
            text_corpus = clean(text_corpus)

            # Find the beginnings and endings of the spoken contents in the ____
            # pattern plenar files. ____________________________________________
            find_beginnings = list(regex.finditer(begin_pattern, text_corpus))
            find_endings = list(regex.finditer(appendix_pattern, text_corpus))

            # For the first and second period a duplicate beginning pattern
            # means in all cases an interruption and restarting of the
            # sitting, possibly on another day.
            # print(find_beginnings)
            # print(find_endings)

            # Append "END OF FILE" to document text, otherwise pattern is
            # not found, when appearing at the end of the file.
            text_corpus += "\n\nEND OF FILE"

            spoken_content = ""

            # Just extract spoken parts between the matching of the
            # beginning and the ending pattern. TOC and APPENDIX is
            # disregarded. For example: If a sitting is interrupted and
            # continued on the next day, there is again a whole table of content
            # section with the names of all the speakers, which should not be
            # included in the usual spoken content.
            if len(find_beginnings) == 0:
                beginning_pattern_not_found.append(xml_plenar_file)
                continue
            elif len(find_beginnings) > len(find_endings) and len(find_endings) == 1:
                spoken_content = text_corpus[
                    find_beginnings[0].span()[1] : find_endings[0].span()[0]
                ]
            elif len(find_beginnings) == len(find_endings):
                for begin, end in zip(find_beginnings, find_endings):
                    spoken_content += text_corpus[begin.span()[1] : end.span()[0]]
            else:
                print(
                    "What can be else?, e.g. len(beginnings) > len(endings) && len(endings) != 1"
                )
                print(find_beginnings)
                print(find_endings)
                other_cases.append(xml_plenar_file)
                continue

            save_path = os.path.join(
                RAW_TXT, wp_folder, xml_plenar_file.replace(".xml", "")
            )

            # Save table of content, spoken content and appendix
            # in separate folders.
            if not os.path.exists(save_path):
                os.makedirs(save_path)

            with open(os.path.join(save_path, "spoken_content.txt"), "w") as text_file:
                text_file.write(spoken_content)

            with open(os.path.join(save_path, "meta_data.xml"), "wb") as result_file:
                result_file.write(dicttoxml.dicttoxml(meta_data))


print("____ Beginning Not Found ____", *beginning_pattern_not_found, sep="\n")
print("____ Beginning Too Often ____", *beginning_pattern_too_often, sep="\n")
print("____ End Not Found ____", *appendix_pattern_not_found, sep="\n")
print("____ End Too Often ____", *appendix_pattern_too_often, sep="\n")
print("____ Other cases ____", *other_cases, sep="\n")
