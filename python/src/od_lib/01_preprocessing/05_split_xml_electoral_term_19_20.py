import od_lib.definitions.path_definitions as path_definitions
import xml.etree.ElementTree as et
import os
import regex
import lxml
import lxml.etree


# input directory
ELECTORAL_TERM_19_20_INPUT = path_definitions.ELECTORAL_TERM_19_20_STAGE_01

# output directory
ELECTORAL_TERM_19_20_OUTPUT = path_definitions.ELECTORAL_TERM_19_20_STAGE_02

HAUSHALTSGESETZ_OUTPUT = path_definitions.FINAL

haushaltsgesetz_dates = []
haushaltsgesetz_docnum = []

for electoral_term_folder in sorted(os.listdir(ELECTORAL_TERM_19_20_INPUT)):
    electoral_term_folder_path = os.path.join(
        ELECTORAL_TERM_19_20_INPUT, electoral_term_folder
    )

    # Skip e.g. the .DS_Store file.
    if not os.path.isdir(electoral_term_folder_path):
        continue

    for xml_file in sorted(os.listdir(electoral_term_folder_path)):

        print(xml_file)

        save_path = os.path.join(
            ELECTORAL_TERM_19_20_OUTPUT,
            electoral_term_folder,
            regex.search(r"\d+", xml_file).group(),
        )

        #19031.xml
        # read data
        tree = et.parse(os.path.join(electoral_term_folder_path, xml_file))
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
            os.path.join(save_path, "appendix.xml"),
            encoding="UTF-8",
            xml_declaration=True,
        )
        meta_data.write(
            os.path.join(save_path, "meta_data.xml"),
            encoding="UTF-8",
            xml_declaration=True,
        )



        tree = lxml.etree.parse(os.path.join(electoral_term_folder_path, xml_file))
        text = " ".join(tree.xpath("//ivz-eintrag-inhalt/text()"))
        date = tree.xpath("//@sitzung-datum")[0]

        if 'Haushaltsgesetz' in text:
                haushaltsgesetz_dates.append(date)
                haushaltsgesetz_docnum.append(xml_file)

with open(os.path.join(HAUSHALTSGESETZ_OUTPUT, "haushaltsgesetz_dates_19_20.txt"), "w") as text_file:
    text_file.write("\n".join(haushaltsgesetz_dates))

with open(os.path.join(HAUSHALTSGESETZ_OUTPUT, "haushaltsgesetz_docnum_19_20.txt"), "w") as text_file:
    text_file.write("\n".join(haushaltsgesetz_docnum))

