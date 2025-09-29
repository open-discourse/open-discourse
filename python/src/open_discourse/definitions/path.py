from pathlib import Path

# ROOT DIR _____________________________________________________________________________
ROOT_DIR = (Path(__file__) / "../../../..").resolve()

# LOGS DIR _____________________________________________________________________________
LOGS_DIR = ROOT_DIR / "logs"

# DATA _________________________________________________________________________________
DATA = ROOT_DIR / "data"
DATA_RAW = DATA / "01_raw"
DATA_CACHE = DATA / "02_cached"
DATA_FINAL = DATA / "03_final"
FINAL = DATA / "03_final"

# MP_BASE_DATA _________________________________________________________________________
MP_BASE_DATA = DATA_RAW / "MP_BASE_DATA"

# RAW __________________________________________________________________________________
RAW_ZIP = DATA_RAW / "zip"
RAW_XML = DATA_RAW / "xml"
RAW_TXT = DATA_RAW / "txt"

# SPEECH CONTENT _______________________________________________________________________
SPEECH_CONTENT = DATA_CACHE / "speech_content"
SPEECH_CONTENT_STAGE_01 = SPEECH_CONTENT / "stage_01"
SPEECH_CONTENT_STAGE_02 = SPEECH_CONTENT / "stage_02"
SPEECH_CONTENT_STAGE_03 = SPEECH_CONTENT / "stage_03"
SPEECH_CONTENT_STAGE_04 = SPEECH_CONTENT / "stage_04"
SPEECH_CONTENT_FINAL = SPEECH_CONTENT / "final"

# CONTRIBUTIONS_EXTENDED _______________________________________________________________
CONTRIBUTIONS_EXTENDED = DATA_CACHE / "contributions_extended"
CONTRIBUTIONS_EXTENDED_STAGE_01 = CONTRIBUTIONS_EXTENDED / "stage_01"
CONTRIBUTIONS_EXTENDED_STAGE_02 = CONTRIBUTIONS_EXTENDED / "stage_02"
CONTRIBUTIONS_EXTENDED_STAGE_03 = CONTRIBUTIONS_EXTENDED / "stage_03"
CONTRIBUTIONS_EXTENDED_STAGE_04 = CONTRIBUTIONS_EXTENDED / "stage_04"

CONTRIBUTIONS_EXTENDED_FINAL = CONTRIBUTIONS_EXTENDED / "final"

# POLITICIANS __________________________________________________________________________
POLITICIANS = DATA_CACHE / "politicians"
POLITICIANS_STAGE_01 = POLITICIANS / "stage_01"
POLITICIANS_STAGE_02 = POLITICIANS / "stage_02"
POLITICIANS_FINAL = POLITICIANS / "final"

# FACTIONS _____________________________________________________________________________
FACTIONS = DATA_CACHE / "factions"
FACTIONS_STAGE_01 = FACTIONS / "stage_01"
FACTIONS = FACTIONS / "stage_02"

FACTIONS_FINAL = FACTIONS / "final"

# CONTRIBUTIONS_SIMPLIFIED _____________________________________________________________
CONTRIBUTIONS_SIMPLIFIED = FINAL

# ELECTORAL_TERMS ______________________________________________________________________
ELECTORAL_TERMS = FINAL

# TOPIC_MODELLING ______________________________________________________________________
TOPIC_MODELLING = DATA_CACHE / "topic_modelling"
