import pandas as pd

import open_discourse.definitions.path_definitions as path_definitions

# input directory
POLITICIANS_INPUT = path_definitions.POLITICIANS_STAGE_01
FACTIONS_INPUT = path_definitions.DATA_FINAL
# output directory
POLITICIANS_OUTPUT = path_definitions.POLITICIANS_STAGE_02
POLITICIANS_OUTPUT.mkdir(parents=True, exist_ok=True)

factions = pd.read_pickle(FACTIONS_INPUT / "factions.pkl")
mps = pd.read_pickle(POLITICIANS_INPUT / "mps.pkl")

mps.insert(2, "faction_id", -1)

for faction_name, faction_id in zip(factions["faction_name"], factions["id"]):
    mps.loc[mps["institution_name"] == faction_name, "faction_id"] = faction_id

mps.to_pickle(POLITICIANS_OUTPUT / "mps.pkl")
