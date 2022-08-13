import os

# ROOT DIR _________________________________________________________________________________________
ROOT_DIR = os.path.abspath(os.path.join(__file__, "../../../.."))

# DATA _____________________________________________________________________________________________
DATA = os.path.join(ROOT_DIR, "data")
DATA_RAW = os.path.join(DATA, "01_raw")
DATA_CACHE = os.path.join(DATA, "02_cached")
DATA_FINAL = os.path.join(DATA, "03_final")
FINAL = os.path.join(DATA, "03_final")
DATABASE = os.path.join(DATA, "04_database")

# MP_BASE_DATA ___________________________________________________________________________________
MP_BASE_DATA = os.path.join(DATA_RAW, "MP_BASE_DATA", "MDB_STAMMDATEN.XML")

# RAW ______________________________________________________________________________________________
RAW_ZIP = os.path.join(DATA_RAW, "zip")
RAW_XML = os.path.join(DATA_RAW, "xml")
RAW_TXT = os.path.join(DATA_RAW, "txt")

# SPEECH CONTENT ___________________________________________________________________________________
SPEECH_CONTENT = os.path.join(DATA_CACHE, "speech_content")
SPEECH_CONTENT_STAGE_01 = os.path.join(SPEECH_CONTENT, "stage_01")
SPEECH_CONTENT_STAGE_02 = os.path.join(SPEECH_CONTENT, "stage_02")
SPEECH_CONTENT_STAGE_03 = os.path.join(SPEECH_CONTENT, "stage_03")
SPEECH_CONTENT_STAGE_04 = os.path.join(SPEECH_CONTENT, "stage_04")
SPEECH_CONTENT_FINAL = os.path.join(SPEECH_CONTENT, "final")

# CONTRIBUTIONS_EXTENDED ___________________________________________________________________________
CONTRIBUTIONS_EXTENDED = os.path.join(DATA_CACHE, "contributions_extended")
CONTRIBUTIONS_EXTENDED_STAGE_01 = os.path.join(CONTRIBUTIONS_EXTENDED, "stage_01")
CONTRIBUTIONS_EXTENDED_STAGE_02 = os.path.join(CONTRIBUTIONS_EXTENDED, "stage_02")
CONTRIBUTIONS_EXTENDED_STAGE_03 = os.path.join(CONTRIBUTIONS_EXTENDED, "stage_03")
CONTRIBUTIONS_EXTENDED_STAGE_04 = os.path.join(CONTRIBUTIONS_EXTENDED, "stage_04")

CONTRIBUTIONS_EXTENDED_FINAL = os.path.join(CONTRIBUTIONS_EXTENDED, "final")


# POLITICIANS ______________________________________________________________________________________
POLITICIANS = os.path.join(DATA_CACHE, "politicians")
POLITICIANS_STAGE_01 = os.path.join(POLITICIANS, "stage_01")
POLITICIANS_STAGE_02 = os.path.join(POLITICIANS, "stage_02")
POLITICIANS_FINAL = os.path.join(POLITICIANS, "final")

# FACTIONS _________________________________________________________________________________________
FACTIONS = os.path.join(DATA_CACHE, "factions")
FACTIONS_STAGE_01 = os.path.join(FACTIONS, "stage_01")
FACTIONS = os.path.join(FACTIONS, "stage_02")

FACTIONS_FINAL = os.path.join(FACTIONS, "final")

# CONTRIBUTIONS_SIMPLIFIED _________________________________________________________________________
CONTRIBUTIONS_SIMPLIFIED = os.path.join(FINAL)

# ELECTORAL_TERMS __________________________________________________________________________________
ELECTORAL_TERMS = os.path.join(FINAL)

# ELECTORAL_TERM_19_20 _____________________________________________________________________________
ELECTORAL_TERM_19_20 = os.path.join(DATA_CACHE, "electoral_term_19_20")
ELECTORAL_TERM_19_20_STAGE_01 = os.path.join(ELECTORAL_TERM_19_20, "stage_01")
ELECTORAL_TERM_19_20_STAGE_02 = os.path.join(ELECTORAL_TERM_19_20, "stage_02")
ELECTORAL_TERM_19_20_STAGE_03 = os.path.join(ELECTORAL_TERM_19_20, "stage_03")

# TOPIC_MODELLING __________________________________________________________________________________
TOPIC_MODELLING = os.path.join(DATA_CACHE, "topic_modelling")
