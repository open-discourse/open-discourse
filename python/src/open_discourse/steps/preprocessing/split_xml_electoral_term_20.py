import xml.etree.ElementTree as et

import regex
from tqdm import tqdm

from open_discourse.definitions import path

# input directory
INPUT_PATH = path.DATA_CACHE / "electoral_term_pp20" / "stage_01"

# output directory
OUTPUT_PATH = path.DATA_CACHE / "electoral_term_pp20" / "stage_02"


def main(task):
    for xml_file_path in tqdm(
        sorted(INPUT_PATH.glob("*.xml")), desc="Parsing term 20..."
    ):
        # read data
        tree = et.parse(xml_file_path)
        root = tree.getroot()

        toc = et.ElementTree(root.find("vorspann"))
        session_content = et.ElementTree(root.find("sitzungsverlauf"))
        appendix = et.ElementTree(root.find("anlagen"))
        meta_data = et.ElementTree(root.find("rednerliste"))

        save_path = OUTPUT_PATH / regex.search(r"\d+", xml_file_path.stem).group()
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

    return True


if __name__ == "__main__":
    main(None)
