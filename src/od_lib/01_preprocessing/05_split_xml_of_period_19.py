import od_lib.definitions.path_definitions as path_definitions
import xml.etree.ElementTree as et
import os
import regex

# input directory ______________________________________________________________
WP_19_INPUT = path_definitions.WP_19_STAGE_01

# output directory _____________________________________________________________
WP_19_OUTPUT = path_definitions.WP_19_STAGE_02


for xml_file in os.listdir(WP_19_INPUT):

    print(xml_file)

    save_path = os.path.join(WP_19_OUTPUT, regex.search(r"\d+", xml_file).group())

    # read data ________________________________________________________________
    tree = et.parse(os.path.join(WP_19_INPUT, xml_file))
    root = tree.getroot()

    vorspann = et.ElementTree(root.find("vorspann"))
    sitzungsverlauf = et.ElementTree(root.find("sitzungsverlauf"))
    anlagen = et.ElementTree(root.find("anlagen"))
    rednerliste = et.ElementTree(root.find("rednerliste"))

    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # save to xmls _____________________________________________________________
    vorspann.write(
        os.path.join(save_path, "vorspann.xml"), encoding="UTF-8", xml_declaration=True
    )
    sitzungsverlauf.write(
        os.path.join(save_path, "sitzungsverlauf.xml"),
        encoding="UTF-8",
        xml_declaration=True,
    )
    anlagen.write(
        os.path.join(save_path, "anlagen.xml"), encoding="UTF-8", xml_declaration=True
    )
    rednerliste.write(
        os.path.join(save_path, "rednerliste.xml"),
        encoding="UTF-8",
        xml_declaration=True,
    )
