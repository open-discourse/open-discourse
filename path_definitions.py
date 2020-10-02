import os

# project root folder __________________________________________________________
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# data folder __________________________________________________________________
DATA = os.path.join(ROOT_DIR, "data")
DATA_RAW = os.path.join(DATA, "01_raw")
DATA_CACHE = os.path.join(DATA, "02_cached")
DATA_FINAL = os.path.join(DATA, "03_final")
FINAL = os.path.join(DATA, "03_final")

# ______________________________________________________________________________
STAMMDATEN_XML = os.path.join(DATA_RAW, "mdb_stammdaten", "MDB_STAMMDATEN.XML")

# ______________________________________________________________________________
RAW_ZIP = os.path.join(DATA_RAW, "zip")
RAW_XML = os.path.join(DATA_RAW, "xml")
RAW_TXT = os.path.join(DATA_RAW, "txt")

# ______________________________________________________________________________
TOPS = os.path.join(DATA_CACHE, "top")
TOPS_STAGE_01 = os.path.join(TOPS, "stage_01")

# ______________________________________________________________________________
TOC = os.path.join(DATA_CACHE, "toc")
TOC_STAGE_01 = os.path.join(TOC, "stage_01")
TOC_STAGE_02 = os.path.join(TOC, "stage_02")

# ______________________________________________________________________________
SPOKEN_CONTENT = os.path.join(DATA_CACHE, "spoken_content")
SPOKEN_CONTENT_STAGE_01 = os.path.join(SPOKEN_CONTENT, "stage_01")
SPOKEN_CONTENT_STAGE_02 = os.path.join(SPOKEN_CONTENT, "stage_02")
SPOKEN_CONTENT_STAGE_03 = os.path.join(SPOKEN_CONTENT, "stage_03")
SPOKEN_CONTENT_STAGE_04 = os.path.join(SPOKEN_CONTENT, "stage_04")
SPOKEN_CONTENT_STAGE_05 = os.path.join(SPOKEN_CONTENT, "stage_05")
SPOKEN_CONTENT_FINAL = os.path.join(SPOKEN_CONTENT, "final")

# ______________________________________________________________________________
CONTRIBUTIONS = os.path.join(DATA_CACHE, "contributions")
CONTRIBUTIONS_STAGE_01 = os.path.join(CONTRIBUTIONS, "stage_01")
CONTRIBUTIONS_STAGE_02 = os.path.join(CONTRIBUTIONS, "stage_02")
CONTRIBUTIONS_STAGE_03 = os.path.join(CONTRIBUTIONS, "stage_03")
CONTRIBUTIONS_STAGE_04 = os.path.join(CONTRIBUTIONS, "stage_04")
CONTRIBUTIONS_MISCELLANEOUS_STAGE_01 = os.path.join(DATA_CACHE, "miscellaneous", "stage_01")

CONTRIBUTIONS_FINAL = os.path.join(CONTRIBUTIONS, "final")

# ______________________________________________________________________________
MISCELLANEOUS = os.path.join(DATA_CACHE, "miscellaneous")
MISCELLANEOUS_STAGE_01 = os.path.join(MISCELLANEOUS, "stage_01")

# ______________________________________________________________________________
PARTIES = os.path.join(DATA_CACHE, "parties")

# ______________________________________________________________________________
PERIODS = os.path.join(DATA_CACHE, "periods")

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
TEXT_POSITION_X_TEXT = os.path.join(FINAL)

# _____________________________________________________________________________
ELECTION_PERIOD = os.path.join(FINAL)

########################### WP_19 Seperate directory ###########################

# WP_19 data directories________________________________________________________
WP_19 = os.path.join(DATA_CACHE, "wp_19")
WP_19_STAGE_01 = os.path.join(WP_19, "stage_01")
WP_19_STAGE_02 = os.path.join(WP_19, "stage_02")
WP_19_STAGE_03 = os.path.join(WP_19, "stage_03")
