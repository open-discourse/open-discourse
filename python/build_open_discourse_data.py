import os
import time

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
    "04_split_xml_electoral_term_1_and_2": os.path.join(
        preprocessing_path, "04_split_xml_electoral_term_1_and_2.py"
    ),
    "05_split_xml_electoral_term_19": os.path.join(
        preprocessing_path, "05_split_xml_electoral_term_19.py"
    ),
    "06_extract_mps_from_mp_base_data": os.path.join(
        preprocessing_path, "06_extract_mps_from_mp_base_data.py"
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
    "01_add_faction_id_to_mps": os.path.join(
        politicians_path, "01_add_faction_id_to_mps.py"
    ),
    "02_scrape_mgs": os.path.join(
        politicians_path, "02_scrape_mgs.py"
    ),
    "03_merge_politicians": os.path.join(politicians_path, "03_merge_politicians.py"),
    # Spoken Content
    "01_extract_speeches": os.path.join(
        speech_content_path, "01_extract_speeches.py"
    ),
    "02_clean_speeches": os.path.join(speech_content_path, "02_clean_speeches.py"),
    "03_match_names_speeches": os.path.join(
        speech_content_path, "03_match_names_speeches.py"
    ),
    # Electoral Term 19
    "01_extract_speeches_and_contributions_electoral_term_19": os.path.join(
        election_period_19, "01_extract_speeches_and_contributions_electoral_term_19.py"
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
        database, "02_upload_data_to_database.py"
    ),
}

os.system("docker-compose down")
time.sleep(5)
os.system("docker-compose up -d database")
time.sleep(20)
os.system(
    "cd ../database && yarn run db:update:local && cd .. && docker-compose up -d graphql"
)

for key in scripts.keys():
    print("Executing: ", key, "______________________________________")
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
