from pathlib import Path

# ROOT DIR _________________________________________________________________________________________
ROOT_DIR = (Path(__file__) / "../../../..").resolve()

# DATA _____________________________________________________________________________________________
DATA = ROOT_DIR / "data"
DATA_RAW = DATA / "01_raw"
DATA_CACHE = DATA / "02_cached"
DATA_FINAL = DATA / "03_final"
FINAL = DATA / "03_final"

# MP_BASE_DATA ___________________________________________________________________________________
MP_BASE_DATA = DATA_RAW / "MP_BASE_DATA" / "MDB_STAMMDATEN.XML"

# RAW ______________________________________________________________________________________________
RAW_ZIP = DATA_RAW / "zip"
RAW_XML = DATA_RAW / "xml"
RAW_TXT = DATA_RAW / "txt"

# SPEECH CONTENT ___________________________________________________________________________________
SPEECH_CONTENT = DATA_CACHE / "speech_content"
SPEECH_CONTENT_STAGE_01 = SPEECH_CONTENT / "stage_01"
SPEECH_CONTENT_STAGE_02 = SPEECH_CONTENT / "stage_02"
SPEECH_CONTENT_STAGE_03 = SPEECH_CONTENT / "stage_03"
SPEECH_CONTENT_STAGE_04 = SPEECH_CONTENT / "stage_04"
SPEECH_CONTENT_FINAL = SPEECH_CONTENT / "final"

# CONTRIBUTIONS_EXTENDED ___________________________________________________________________________
CONTRIBUTIONS_EXTENDED = DATA_CACHE / "contributions_extended"
CONTRIBUTIONS_EXTENDED_STAGE_01 = CONTRIBUTIONS_EXTENDED / "stage_01"
CONTRIBUTIONS_EXTENDED_STAGE_02 = CONTRIBUTIONS_EXTENDED / "stage_02"
CONTRIBUTIONS_EXTENDED_STAGE_03 = CONTRIBUTIONS_EXTENDED / "stage_03"
CONTRIBUTIONS_EXTENDED_STAGE_04 = CONTRIBUTIONS_EXTENDED / "stage_04"

CONTRIBUTIONS_EXTENDED_FINAL = CONTRIBUTIONS_EXTENDED / "final"


# POLITICIANS ______________________________________________________________________________________
POLITICIANS = DATA_CACHE / "politicians"
POLITICIANS_STAGE_01 = POLITICIANS / "stage_01"
POLITICIANS_STAGE_02 = POLITICIANS / "stage_02"
POLITICIANS_FINAL = POLITICIANS / "final"

# FACTIONS _________________________________________________________________________________________
FACTIONS = DATA_CACHE / "factions"
FACTIONS_STAGE_01 = FACTIONS / "stage_01"
FACTIONS = FACTIONS / "stage_02"

FACTIONS_FINAL = FACTIONS / "final"

# CONTRIBUTIONS_SIMPLIFIED _________________________________________________________________________
CONTRIBUTIONS_SIMPLIFIED = FINAL

# ELECTORAL_TERMS __________________________________________________________________________________
ELECTORAL_TERMS = FINAL

# ELECTORAL_TERM_19_20 _____________________________________________________________________________
ELECTORAL_TERM_19_20 = DATA_CACHE / "electoral_term_19_20"
ELECTORAL_TERM_19_20_STAGE_01 = ELECTORAL_TERM_19_20 / "stage_01"
ELECTORAL_TERM_19_20_STAGE_02 = ELECTORAL_TERM_19_20 / "stage_02"
ELECTORAL_TERM_19_20_STAGE_03 = ELECTORAL_TERM_19_20 / "stage_03"

# TOPIC_MODELLING __________________________________________________________________________________
TOPIC_MODELLING = DATA_CACHE / "topic_modelling"
