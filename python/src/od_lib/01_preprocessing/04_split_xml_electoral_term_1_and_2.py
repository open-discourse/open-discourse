from od_lib.helper_functions.clean_text import clean
import od_lib.definitions.path_definitions as path_definitions
import xml.etree.ElementTree as et
import os
import regex
import dicttoxml

# input directory
RAW_XML = path_definitions.RAW_XML

# output directory
RAW_TXT = path_definitions.RAW_TXT

HAUSHALTSGESETZ_OUTPUT = path_definitions.FINAL

haushaltsgesetz_dates = []
haushaltsgesetz_docnum = []

if not os.path.exists(RAW_TXT):
    os.makedirs(RAW_TXT)

# Open every xml plenar file in every electoral term.
for electoral_term_folder in sorted(os.listdir(RAW_XML)):
    electoral_term_folder_path = os.path.join(RAW_XML, electoral_term_folder)

    # Skip e.g. the .DS_Store file.
    if not os.path.isdir(electoral_term_folder_path):
        continue

    if electoral_term_folder not in ["electoral_term_01", "electoral_term_02"]:
        continue

    # JK: this pattern do not capture sentences like this: 02078.xml '4332\nDie Sitzung wird um 9 Uhr durch den Präsidenten\nD. Dr. Gerstenmaier eröffnet'
    begin_pattern = regex.compile(
        r"Die.*?Sitzung.*?wird.*?\d{1,2}.*?Uhr.*?(durch.*?den.*?)?eröffnet"
    )

    alternative_begin_pattern = regex.compile(
        r"Die[^\.]*?Sitzung[^\.]*?wird[^\.]*?\d{1,2}[^\.]*?Uhr[^\.]*?(durch[^\.]*?den.*?)?(eröffnet|eingeleitet)[^\.]*?[.]",
        regex.V0 | regex.DOTALL
    )

    appendix_pattern = regex.compile(r"\(Schluß.*?Sitzung.*?Uhr.*?\)")

    print(electoral_term_folder)
    for xml_file in sorted(os.listdir(electoral_term_folder_path)):
        if ".xml" in xml_file:
            print(xml_file)
            path = os.path.join(electoral_term_folder_path, xml_file)
            tree = et.parse(path)

            meta_data = {}

            # Get the document number, the date of the session and the content.
            meta_data["document_number"] = tree.find("NR").text
            meta_data["date"] = tree.find("DATUM").text
            text_corpus = tree.find("TEXT").text

            # Clean text corpus.
            text_corpus = clean(text_corpus)

            # Find the beginnings and endings of the spoken contents in the
            # pattern plenar files.

            find_beginnings = list(regex.finditer(begin_pattern, text_corpus))

            if len(find_beginnings) == 0:
                print("applying different pattern beginnings")
                find_beginnings = list(regex.finditer(alternative_begin_pattern, text_corpus))
                print(find_beginnings[0])

            find_endings = list(regex.finditer(appendix_pattern, text_corpus))

            beginning_of_session = find_beginnings[0].span()[1]

            toc = text_corpus[:beginning_of_session]
            # Append "END OF FILE" to document text, otherwise pattern is
            # not found, when appearing at the end of the file.


            if 'Haushaltsgesetz' in toc:
                print("Found budget discussion")
                haushaltsgesetz_dates.append(meta_data["date"])
                haushaltsgesetz_docnum.append(meta_data["document_number"])

            text_corpus += "\n\nEND OF FILE"

            session_content = ""

            # Just extract spoken parts between the matching of the
            # beginning and the ending pattern. TOC and APPENDIX is
            # disregarded. For example: If a session is interrupted and
            # continued on the next day, there is again a whole table of content
            # section with the names of all the speakers, which should not be
            # included in the usual spoken content.
            if len(find_beginnings) == 0:
                continue
            elif len(find_beginnings) > len(find_endings) and len(find_endings) == 1:
                session_content = text_corpus[
                    find_beginnings[0].span()[1] : find_endings[0].span()[0]
                ]
            elif len(find_beginnings) == len(find_endings):
                for begin, end in zip(find_beginnings, find_endings):
                    session_content += text_corpus[begin.span()[1] : end.span()[0]]
            else:
                continue

            save_path = os.path.join(
                RAW_TXT, electoral_term_folder, xml_file.replace(".xml", "")
            )

            # Save table of content, spoken content and appendix
            # in separate folders.
            if not os.path.exists(save_path):
                os.makedirs(save_path)

            with open(os.path.join(save_path, "session_content.txt"), "w") as text_file:
                text_file.write(session_content)

            with open(os.path.join(save_path, "meta_data.xml"), "wb") as result_file:
                result_file.write(dicttoxml.dicttoxml(meta_data))


with open(os.path.join(HAUSHALTSGESETZ_OUTPUT, "haushaltsgesetz_dates_1_2.txt"), "w") as text_file:
    text_file.write("\n".join(haushaltsgesetz_dates))

with open(os.path.join(HAUSHALTSGESETZ_OUTPUT, "haushaltsgesetz_docnum_1_2.txt"), "w") as text_file:
    text_file.write("\n".join(haushaltsgesetz_docnum))
