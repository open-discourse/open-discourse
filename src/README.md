# Python Scripts Information

## General Information

The folders and the files are mostly sorted in the order of execution.

For the correct order of execution, please use our execution graph:

![Execution Graph](./ExecutionGraph.png "Execution Graph")

The Input and Output paths start at the project root

## 01_preprocessing

### 1. [Download Raw Data](./01_preprocessing/01_download_raw_data.py)

- Function:

  - Downloads Zip folders that include XML files for plenary sessions in the electoral periods 1 to 18
  - Downloads XML file with the personal details for all Members of the Bundestag from the 1st to the 19th electoral period

- Attributes:
  - Input: `None`
  - Output: `./data/01_raw/xml/*`

### 2. [Download Raw Data WP 19](./01_preprocessing/02_download_raw_data_electoral_term_19.py)

- Function:

  - Downloads XML files for plenary sessions in the 19th electoral period
  - New sessions have to be added manually

- Attributes:
  - Input: `None`
  - Output: `./data/02_cached/electoral_term_10/stage_01/*`

### 3. [Split XML](./01_preprocessing/03_split_xml.py)

- Function:

  - A cleaning function checks the text corpus. It deletes things like the titles that were left from the pdf files, the XML files were generated from. The cleaning function can be found in [helper_functions/clean_text.py](./helper_functions/clean_text.py)
  - Splits the XML files of the 3rd to 18th electoral period into the table of content, speech_content and appendix

- Attributes:
  - Input: `./data/01_raw/xml/*`
  - Output: `./data/01_raw/txt/*`

### 4. [Split XML of period 1 and 2](./01_preprocessing/04_split_xml_of_period_1_and_2.py)

- Function:

  - A cleaning function checks the text corpus. It deletes things like the titles that were left from the pdf files, the XML files were generated from. The cleaning function can be found in [helper_functions/clean_text.py](./helper_functions/clean_text.py)
  - Because of the "interesting" structure of the first two election periods, we use a different approach to split the XML files into the table of content, speech_content and appendix

- Attributes:
  - Input: `./data/01_raw/xml/*`
  - Output: `./data/01_raw/txt/*`

### 5. [Split XML of period 19](./01_preprocessing/05_split_xml_of_period_19.py)

- Function:

  - Splits the XML file into table of content, speech_content and appendix based on the XML tags

- Attributes:
  - Input: `./data/02_cached/electoral_term_19/stage_01/*`
  - Output: `./data/02_cached/electoral_term_19/stage_02/*`

### 6. [Extract MDBs from personal details](./01_preprocessing/06_extract_mdbs_from_STAMMDATEN_XML.py)

- Function:

  - Parses the personal details into a Dataframe

- Attributes:
  - Input: `./data/01_raw/mdb_stammdaten/MDB_STAMMDATEN.XML`
  - Output: `./data/02_cached/politicians/stage_01/mdbs.pkl`

### 7. [Create Election Periods](./01_preprocessing/07_create_electoral_terms.py)

- Function:

  - Creates the Election Period Dataframe

- Attributes:
  - Input: `None`
  - Output: `./data/03_final/electoral_terms.csv`

## Factions

### 1. [Create Factions](./02_factions/01_create_factions.py)

- Function:

  - Uses the `mdbs` Dataframe to extract unique factions and manually adds factions that show up in the speeches but not in the Dataframe

- Attributes:
  - Input: `./data/02_cached/politicians/stage_01/mdbs.pkl`
  - Output: `./data/02_cached/factions/stage_01/factions.pkl`

### 2. [Add Abbreviations](./02_factions/02_add_abbreviations_and_ids.py)

- Function:

  - Add Abbreviations to the factions Dataframe

- Attributes:
  - Input: `./data/02_cached/factions/stage_01/factions.pkl`
  - Output: `./data/03_final/factions.pkl`

## Politicians

### 1. [Add Faction IDs to MDBs](./03_politicians/01_add_faction_id_to_mdbs.py)

- Function:

  - Assigns the according faction id to every politician

- Attributes:
  - Input:
    - `./data/02_cached/politicians/stage_01/mdbs.pkl`
    - `./data/03_final/factions.pkl`
  - Output: `./data/02_cached/politicians/stage_02/mdbs.pkl`

### 2. [Scrape the Government Members](./03_politicians/02_scrape_government_members.py)

- Function:

  - Scrapes every Government Member off of Wikipedia

- Attributes:
  - Input: `None`
  - Output: `./data/02_cached/politicians/stage_01/government_members.pkl`

### 3. [Merge People](./03_politicians/03_merge_politicians.py)

- Function:

  - Merges the `mdbs.pkl`and `government_members.pkl` Dataframe

- Attributes:
  - Input:
    - `./data/02_cached/politicians/stage_02/mdbs.pkl`
    - `./data/02_cached/politicians/stage_01/government_members.pkl`
    - `./data/03_final/factions.pkl`
  - Output: `./data/03_final/politicians.csv`

## Spoken Content

### 1. [Split Corpus at every Agenda Item](./04_speech_content/01_split_at_tops.py)

- Function:

  - Searches for Patterns in the Text that imply the beginning of a new Agenda Item

- Attributes:
  - Input: `./data/01_raw/txt/*`
  - Output: `./data/02_cached/speech_content/stage_01/*`
  - File Format:
    - speech_content:
      | top | additional_tops | content |
      | --- | --- | --- |
      | intro | | Peter Schmidt (CDU/CSU): Sehr geehrter (Hans Müller [AfD]: Fisch! - Beifall bei der SPD - Links)... |
      | ... | ... | ... |

### 2. [Extract Speech Parts](./04_speech_content/02_extract_speech_parts.py)

- Function:

  - Searches for Speaches in the Corpus using Regex Patterns.

- Attributes:
  - Input: `./data/02_cached/speech_content/stage_01/*`
  - Output: `./data/02_cached/speech_content/stage_02/*`
  - File Format:
    - speech_content:
      | session | top | additional_tops | name | position | speech_content | span_begin | span_end |
      | --- | --- | --- | --- | --- | --- | --- | --- |
      | 18245.pkl | intro | | Peter Schmidt | CDU/CSU | Sehr geehrter (Hans Müller [AfD]: Fisch! - Beifall bei der SPD - Links)... | 0.0 | 255.0 |
      | ... | ... | ... | ... | ... | ... | ... | ... |

### 3. [Clean Speeches](./04_speech_content/03_clean_speeches.py)

- Function:

  - Splits the Full Name into First- and Last-Name
  - Assigns a Faction ID
  - Parses the Position into `position_long` and `position_short`

- Attributes:
  - Input:
    - `./data/02_cached/speech_content/stage_02/*`
    - `./data/03_final/factions.pkl`
  - Output: `./data/02_cached/speech_content/stage_03/*`
  - File Format:
    - speech_content:
      | session | top | additional_tops | faction_id | name | last_name | first_name | title | position_short | position_long | speech_content | span_begin | span_end |
      | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
      | 18245.pkl | intro | | 4 | Peter Schmidt | Schmidt | ['Peter'] | [] | | Member of Parliament | Sehr geehrter (Hans Müller [AfD]: Fisch! - Beifall bei der SPD - Links)... | 0.0 | 255.0 |
      | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

### 4. [Match Names](./04_speech_content/04_match_names_speech_content.py)

- Function:

  - Assigns a People ID to every Speaker

- Attributes:
  - Input:
    - `./data/02_cached/speech_content/stage_03/*`
    - `./data/03_final/politicians.csv`
  - Output: `./data/02_cached/speech_content/stage_04/*`
  - File Format:
    - speech_content:
      | session | top | additional_tops | faction_id | politician_id |name | last_name | first_name | title | position_short | position_long | speech_content | span_begin | span_end |
      | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
      | 18245.pkl | intro | | 4 | 1109312 | Peter Schmidt | Schmidt | ['Peter'] | [] | | Member of Parliament | Sehr geehrter (Hans Müller [AfD]: Fisch! - Beifall bei der SPD - Links)... | 0.0 | 255.0 |
      | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

## Election Period 19

### 1. [Extract Speeches and Contributions Period 19](./06_election_period_19/01_extract_speeches_and_contributions_period_19.py)

- Function:

  - Speeches are extracted from the XML Structure
  - Searches for Contributions in the Speeches using Regex Pattern
  - Text in Braces that can't be assigned to a Contribution, are saved as Miscellaneous
  - The Script replaces Contributions in the speech_content with an Identifier
  - The extract_contribution funciton can be found in [helper_functions/extract_contributions.py](./helper_functions/extract_contributions.py)

- Attributes:

  - Input: `./data/02_cached/electoral_term_19/stage_02/*`
  - Output:
    - `./data/02_cached/electoral_term_19/stage_03/speech_content/speech_content.pkl`
    - `./data/02_cached/contributions/stage_01/*`
    - `./data/02_cached/miscellaneous/stage_01/*`
    - `./data/03_final/contributions_lookup.pkl`
  - File Format:
    - speech_content:
      | id | session | first_name | last_name | faction_id | position_short | position_long | politician_id | speech_content | date |
      | --- | --- | ---| --- | --- | --- | --- | --- | --- | --- |
      | 25000 | 19171 | Stefan | Müller | 23 | | Member of Parliament | 1122402 | Sehr geehrte Damen und Herren ({0}) | 1508803200.0 |
      | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |
    - contributions:
      | id |  type | name | faction | constituency | content | text_position |
      | --- | --- | --- | --- | --- | --- | --- |
      | 0 | Beifall | | SPD | | | 0 |
      | 1 | Personen-Einruf | Hans Müller | AfD | | Fisch! | 0 |
      | ... | ... | ... | ... | ... | ... | ... |
    - miscellaneous:
      | id | name | faction | content | position |
      | --- | --- | --- | --- | --- |
      | 0 | | | Links | 0 |
      | ... | ... | ... | ... | ... |

## Contributions

### 1. [Extract Contributions](./05_contributions/01_extract_contributions.py)

- Function:

  - Searches for Contributions in the Speeches using Regex Pattern
  - Text in Braces that can't be assigned to a Contribution, are saved as Miscellaneous
  - The Script replaces Contributions in the speech_content with an Identifier
  - The extract_contribution funciton can be found in [helper_functions/extract_contributions.py](./helper_functions/extract_contributions.py)

- Attributes:

  - Input: `./data/02_cached/speech_content/stage_05/*`
  - Output:
    - `./data/02_cached/speech_content/stage_06/*`
    - `./data/02_cached/contributions/stage_01/*`
    - `./data/02_cached/miscellaneous/stage_01/*`
    - `./data/03_final/contributions_lookup.pkl`
  - File Format:
    - speech_content:
      | speech_id | session | top | additional_tops | faction_id | politician_id |name | last_name | first_name | title | position_short | position_long | speech_content | span_begin | span_end |
      | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
      | 0 | 18245.pkl | intro | | 4 | 1109312 | Peter Schmidt | Schmidt | ['Peter'] | [] | | Member of Parliament | Sehr geehrter ({0})... | 0.0 | 255.0 |
      | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |
    - contributions:
      | id |  type | name | faction | constituency | content | text_position |
      | --- | --- | --- | --- | --- | --- | --- |
      | 0 | Beifall | | SPD | | | 0 |
      | 1 | Personen-Einruf | Hans Müller | AfD | | Fisch! | 0 |
      | ... | ... | ... | ... | ... | ... | ... |
    - miscellaneous:
      | id | name | faction | content | position |
      | --- | --- | --- | --- | --- |
      | 0 | | | Links | 0 |
      | ... | ... | ... | ... | ... |

### 2. [Clean Contributions](./05_contributions/02_clean_contributions.py)

- Function:

  - Splits the Full Name into First- and Last-Name
  - Cleans the Party name and assigns a Faction ID

- Attributes:
  - Input:
    - `./data/02_cached/contributions/stage_01/*`
    - `./data/03_final/politicians.csv`
  - Output: `./data/02_cached/contributions/stage_02/*`
  - File Format:
    - contributions:
      | id | type | name | faction_id | faction | last_name | first_name | title | constituency | content | text_position |
      | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
      | 0 | Beifall | | 23 | SPD | | [] | [] | | 0 |
      | 1 | Personen-Einruf | Hans Müller | 0 | AfD | Müller | ['Hans'] | [] | | Fisch! | 0 |
      | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

### 3. [Match Contributions](./05_contributions/03_match_contributions.py)

- Function:

  - Assigns a People ID to every Contribution

- Attributes:
  - Input:
    - `./data/02_cached/contributions/stage_01/*`
    - `./data/03_final/politicians.csv`
  - Output: `./data/02_cached/contributions/stage_02/*`
  - File Format:
    - contributions:
      | id | type | name | faction_id | politician_id | faction | last_name | first_name | title | constituency | content | text_position |
      | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
      | 0 | Beifall | | 23 | -1 | SPD | | [] | [] | | | 0 |
      | 1 | Personen-Einruf | Hans Müller | 0 | 1109373 | AfD | Müller | ['Hans'] | [] | | Fisch! | 0 |
      | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

## Database

### 1. [Concat Everything](./07_database/01_concat_everything.py)

- Function:

  - Concats every speech_content DataFrame into one single DataFrame. Does this as well for contributions and miscellaneous

- Attributes:

  - Input:
    - `./data/01_raw/xml/*`
    - `./data/02_cached/speech_content/stage_06/*`
    - `./data/02_cached/electoral_term_19/stage_03/speech_content/speech_content.pkl`
    - `./data/02_cached/contributions/stage_03/*`
    - `./data/02_cached/miscellaneous/stage_01/*`
  - Output:
    - `./data/03_final/speech_content.pkl`
    - `./data/03_final/contributions.pkl`
    - `./data/03_final/miscellaneous.pkl`

### 2. [Upload Data to Database](./07_database/02_upload_data_to_database.py)

- Function:

  - Uploads every Dataframe in `./data/03_final` to the Database
