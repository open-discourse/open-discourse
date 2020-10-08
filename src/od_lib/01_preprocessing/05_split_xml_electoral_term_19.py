import od_lib.definitions.path_definitions as path_definitions
import xml.etree.ElementTree as et
import os
import regex

# input directory
ELECTORAL_TERM_19_INPUT = path_definitions.ELECTORAL_TERM_19_STAGE_01

# output directory
ELECTORAL_TERM_19_OUTPUT = path_definitions.ELECTORAL_TERM_19_STAGE_02


for xml_file in sorted(os.listdir(ELECTORAL_TERM_19_INPUT)):

    print(xml_file)

    save_path = os.path.join(
        ELECTORAL_TERM_19_OUTPUT, regex.search(r"\d+", xml_file).group()
    )

    # read data
    tree = et.parse(os.path.join(ELECTORAL_TERM_19_INPUT, xml_file))
    root = tree.getroot()

    toc = et.ElementTree(root.find("vorspann"))
    session_content = et.ElementTree(root.find("sitzungsverlauf"))
    appendix = et.ElementTree(root.find("anlagen"))
    meta_data = et.ElementTree(root.find("rednerliste"))

    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # save to xmls
    toc.write(
        os.path.join(save_path, "toc.xml"), encoding="UTF-8", xml_declaration=True
    )
    session_content.write(
        os.path.join(save_path, "session_content.xml"),
        encoding="UTF-8",
        xml_declaration=True,
    )
    appendix.write(
        os.path.join(save_path, "appendix.xml"), encoding="UTF-8", xml_declaration=True
    )
    meta_data.write(
        os.path.join(save_path, "meta_data.xml"),
        encoding="UTF-8",
        xml_declaration=True,
    )
