import xml.etree.ElementTree as et

import dicttoxml
import regex

import open_discourse.definitions.path_definitions as path_definitions
from open_discourse.helper_functions.clean_text import clean
from open_discourse.helper_functions.progressbar import progressbar

# input directory
RAW_XML = path_definitions.RAW_XML

# output directory
RAW_TXT = path_definitions.RAW_TXT
RAW_TXT.mkdir(parents=True, exist_ok=True)

# Open every xml plenar file in every electoral term.
for folder_path in sorted(RAW_XML.iterdir()):
    # Skip e.g. the .DS_Store file.
    if not folder_path.is_dir():
        continue

    term_number = regex.search(r"(?<=electoral_term_)\d{2}", folder_path.stem)
    if term_number is None:
        continue
    term_number = int(term_number.group(0))

    if term_number > 2:
        continue

    begin_pattern = regex.compile(
        r"Die.*?Sitzung.*?wird.*?\d{1,2}.*?Uhr.*?(durch.*?den.*?)?eröffnet"
    )
    appendix_pattern = regex.compile(r"\(Schluß.*?Sitzung.*?Uhr.*?\)")

    for xml_file_path in progressbar(
        folder_path.iterdir(), f"Parsing term {term_number:>2}..."
    ):
        if xml_file_path.suffix == ".xml":
            tree = et.parse(xml_file_path)

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
            find_endings = list(regex.finditer(appendix_pattern, text_corpus))

            # Append "END OF FILE" to document text, otherwise pattern is
            # not found, when appearing at the end of the file.
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

            save_path = RAW_TXT / folder_path.stem / xml_file_path.stem
            save_path.mkdir(parents=True, exist_ok=True)
            # Save table of content, spoken content and appendix
            # in separate folders.
            with open(save_path / "session_content.txt", "w") as text_file:
                text_file.write(session_content)

            with open(save_path / "meta_data.xml", "wb") as result_file:
                result_file.write(dicttoxml.dicttoxml(meta_data))
