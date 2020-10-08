import os

src_path = os.path.join("src/od_lib")

preprocessing_path = os.path.join(src_path, "01_preprocessing")
factions_path = os.path.join(src_path, "02_factions")
politicians_path = os.path.join(src_path, "03_politicians")
speech_content_path = os.path.join(src_path, "04_speech_content")
election_period_19 = os.path.join(src_path, "05_election_period_19")
contributions_path = os.path.join(src_path, "06_contributions")
database = os.path.join(src_path, "07_database")

if not os.path.exists("./logs/"):
    os.makedirs("./logs/")

scripts = {
    # Preprocessing
    "01_download_raw_data": os.path.join(preprocessing_path, "01_download_raw_data.py"),
    "02_download_raw_data_electoral_term_19": os.path.join(
        preprocessing_path, "02_download_raw_data_electoral_term_19.py"
    ),
    "03_split_xml": os.path.join(preprocessing_path, "03_split_xml.py"),
    "04_split_xml_of_period_1_and_2": os.path.join(
        preprocessing_path, "04_split_xml_of_period_1_and_2.py"
    ),
    "05_split_xml_of_period_19": os.path.join(
        preprocessing_path, "05_split_xml_of_period_19.py"
    ),
    "06_extract_mdbs_from_STAMMDATEN_XML": os.path.join(
        preprocessing_path, "06_extract_mdbs_from_STAMMDATEN_XML.py"
    ),
    "07_create_electoral_terms": os.path.join(
        preprocessing_path, "07_create_electoral_terms.py"
    ),
    # Factions
    "01_create_factions": os.path.join(factions_path, "01_create_factions.py"),
    "02_add_abbreviations_and_ids": os.path.join(
        factions_path, "02_add_abbreviations_and_ids.py"
    ),
    # Politicians
    "01_add_faction_id_to_mdbs": os.path.join(
        politicians_path, "01_add_faction_id_to_mdbs.py"
    ),
    "02_scrape_government_members": os.path.join(
        politicians_path, "02_scrape_government_members.py"
    ),
    "03_merge_politicians": os.path.join(politicians_path, "03_merge_politicians.py"),
    # Spoken Content
    "01_split_at_tops": os.path.join(speech_content_path, "01_split_at_tops.py"),
    "02_extract_speech_parts": os.path.join(
        speech_content_path, "02_extract_speech_parts.py"
    ),
    "03_clean_speeches": os.path.join(speech_content_path, "03_clean_speeches.py"),
    "04_match_names_speech_content": os.path.join(
        speech_content_path, "04_match_names_speech_content.py"
    ),
    # Election Period 19
    "01_extract_speeches_and_contributions_period_19": os.path.join(
        election_period_19, "01_extract_speeches_and_contributions_period_19.py"
    ),
    # Contributions
    "01_extract_contributions": os.path.join(
        contributions_path, "01_extract_contributions.py"
    ),
    "02_clean_contributions": os.path.join(
        contributions_path, "02_clean_contributions.py"
    ),
    "03_match_contributions": os.path.join(
        contributions_path, "03_match_contributions.py"
    ),
    # Concat Everything
    "01_concat_everything": os.path.join(database, "01_concat_everything.py"),
    # Upload Data to the Database
    "02_upload_data_to_database.py": os.path.join(
        database, "02_upload_data_to_database.py all"
    ),
}


for key in scripts.keys():
    print("Executing: ", key, "______________________________________")
    os.system("docker-compose up -d database")
    os.system(
        "cd database && yarn run db:update:local && cd .. && docker-compose up -d graphql"
    )
    command = " ".join(
        [
            "python",
            scripts[key],
            "2>&1 | tee ",
            "".join(["./logs/", scripts[key].split("/")[-1], "_log.log"]),
        ]
    )
    print(command)
    os.system(command)
