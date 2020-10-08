import os

# project root folder __________________________________________________________
ROOT_DIR = os.path.abspath(os.path.join(__file__, "../../../.."))

# data folder __________________________________________________________________
DATA = os.path.join(ROOT_DIR, "data")
DATA_RAW = os.path.join(DATA, "01_raw")
DATA_CACHE = os.path.join(DATA, "02_cached")
DATA_FINAL = os.path.join(DATA, "03_final")
FINAL = os.path.join(DATA, "03_final")

# ______________________________________________________________________________
MP_MASTER_DATA = os.path.join(DATA_RAW, "mp_master_data", "MDB_STAMMDATEN.XML")

# ______________________________________________________________________________
RAW_ZIP = os.path.join(DATA_RAW, "zip")
RAW_XML = os.path.join(DATA_RAW, "xml")
RAW_TXT = os.path.join(DATA_RAW, "txt")

# ______________________________________________________________________________
SPEECH_CONTENT = os.path.join(DATA_CACHE, "speech_content")
SPEECH_CONTENT_STAGE_01 = os.path.join(SPEECH_CONTENT, "stage_01")
SPEECH_CONTENT_STAGE_02 = os.path.join(SPEECH_CONTENT, "stage_02")
SPEECH_CONTENT_STAGE_03 = os.path.join(SPEECH_CONTENT, "stage_03")
SPEECH_CONTENT_STAGE_04 = os.path.join(SPEECH_CONTENT, "stage_04")
SPEECH_CONTENT_STAGE_05 = os.path.join(SPEECH_CONTENT, "stage_05")
SPEECH_CONTENT_FINAL = os.path.join(SPEECH_CONTENT, "final")

# ______________________________________________________________________________
CONTRIBUTIONS = os.path.join(DATA_CACHE, "contributions")
CONTRIBUTIONS_STAGE_01 = os.path.join(CONTRIBUTIONS, "stage_01")
CONTRIBUTIONS_STAGE_02 = os.path.join(CONTRIBUTIONS, "stage_02")
CONTRIBUTIONS_STAGE_03 = os.path.join(CONTRIBUTIONS, "stage_03")
CONTRIBUTIONS_STAGE_04 = os.path.join(CONTRIBUTIONS, "stage_04")
CONTRIBUTIONS_MISCELLANEOUS_STAGE_01 = os.path.join(
    DATA_CACHE, "miscellaneous", "stage_01"
)

CONTRIBUTIONS_FINAL = os.path.join(CONTRIBUTIONS, "final")

# ______________________________________________________________________________
MISCELLANEOUS = os.path.join(DATA_CACHE, "miscellaneous")
MISCELLANEOUS_STAGE_01 = os.path.join(MISCELLANEOUS, "stage_01")

# ______________________________________________________________________________
POLITICIANS = os.path.join(DATA_CACHE, "politicians")
POLITICIANS_STAGE_01 = os.path.join(POLITICIANS, "stage_01")
POLITICIANS_STAGE_02 = os.path.join(POLITICIANS, "stage_02")
POLITICIANS_FINAL = os.path.join(POLITICIANS, "final")

# ______________________________________________________________________________
FACTIONS = os.path.join(DATA_CACHE, "factions")
FACTIONS_STAGE_01 = os.path.join(FACTIONS, "stage_01")
FACTIONS = os.path.join(FACTIONS, "stage_02")

FACTIONS_FINAL = os.path.join(FACTIONS, "final")

# ______________________________________________________________________________
CONTRIBUTIONS_LOOKUP = os.path.join(FINAL)

# ______________________________________________________________________________
ELECTORAL_TERMS = os.path.join(FINAL)

# _________________________ WP_19 Seperate directory ___________________________

# WP_19 data directories________________________________________________________
WP_19 = os.path.join(DATA_CACHE, "electoral_term_19")
WP_19_STAGE_01 = os.path.join(WP_19, "stage_01")
WP_19_STAGE_02 = os.path.join(WP_19, "stage_02")
WP_19_STAGE_03 = os.path.join(WP_19, "stage_03")
