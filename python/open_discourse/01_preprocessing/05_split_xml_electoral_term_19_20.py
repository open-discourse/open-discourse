import xml.etree.ElementTree as et

import regex

import open_discourse.definitions.path_definitions as path_definitions
from open_discourse.helper_functions.progressbar import progressbar

# input directory
ELECTORAL_TERM_19_20_INPUT = path_definitions.ELECTORAL_TERM_19_20_STAGE_01

# output directory
ELECTORAL_TERM_19_20_OUTPUT = path_definitions.ELECTORAL_TERM_19_20_STAGE_02

for folder_path in sorted(ELECTORAL_TERM_19_20_INPUT.iterdir()):
    # Skip e.g. the .DS_Store file.
    if not folder_path.is_dir():
        continue

    term_number = regex.search(r"(?<=electoral_term_)\d{2}", folder_path.stem)
    if term_number is None:
        continue
    term_number = int(term_number.group(0))

    for xml_file_path in progressbar(
        folder_path.iterdir(), f"Parsing term {term_number:>2}..."
    ):
        # read data
        tree = et.parse(xml_file_path)
        root = tree.getroot()

        toc = et.ElementTree(root.find("vorspann"))
        session_content = et.ElementTree(root.find("sitzungsverlauf"))
        appendix = et.ElementTree(root.find("anlagen"))
        meta_data = et.ElementTree(root.find("rednerliste"))

        save_path = (
            ELECTORAL_TERM_19_20_OUTPUT
            / folder_path.stem
            / regex.search(r"\d+", xml_file_path.stem).group()
        )
        save_path.mkdir(parents=True, exist_ok=True)
        # save to xmls
        toc.write(save_path / "toc.xml", encoding="UTF-8", xml_declaration=True)
        session_content.write(
            save_path / "session_content.xml",
            encoding="UTF-8",
            xml_declaration=True,
        )
        appendix.write(
            save_path / "appendix.xml",
            encoding="UTF-8",
            xml_declaration=True,
        )
        meta_data.write(
            save_path / "meta_data.xml",
            encoding="UTF-8",
            xml_declaration=True,
        )
