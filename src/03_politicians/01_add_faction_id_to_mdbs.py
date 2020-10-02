import pandas as pd
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))
import path_definitions

# input ________________________________________________________________________
POLITICIANS_INPUT = path_definitions.POLITICIANS_STAGE_01
FACTIONS_INPUT = path_definitions.DATA_FINAL

# output _______________________________________________________________________
POLITICIANS_OUTPUT = path_definitions.POLITICIANS_STAGE_02

if not os.path.exists(POLITICIANS_OUTPUT):
    os.makedirs(POLITICIANS_OUTPUT)


factions = pd.read_pickle(os.path.join(FACTIONS_INPUT, "factions.pkl"))
politicians = pd.read_pickle(os.path.join(POLITICIANS_INPUT, "mdbs.pkl"))

politicians.insert(2, "faction_id", -1)

for faction_name, faction_id in zip(factions.faction_name, factions.id):
    politicians.faction_id.loc[
        politicians.institution_name == faction_name
    ] = faction_id

politicians.to_pickle(os.path.join(POLITICIANS_OUTPUT, "mdbs.pkl"))
