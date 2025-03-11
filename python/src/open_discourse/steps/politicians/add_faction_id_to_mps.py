import pandas as pd

from open_discourse.definitions import path

# input directory
POLITICIANS_INPUT = path.POLITICIANS_STAGE_01
FACTIONS_INPUT = path.DATA_FINAL

# output directory
POLITICIANS_OUTPUT = path.POLITICIANS_STAGE_02
POLITICIANS_OUTPUT.mkdir(parents=True, exist_ok=True)

factions = pd.read_pickle(FACTIONS_INPUT / "factions.pkl")
mps = pd.read_pickle(POLITICIANS_INPUT / "mps.pkl")

mps.insert(2, "faction_id", -1)

for faction_name, faction_id in zip(factions["faction_name"], factions["id"]):
    mps.loc[mps["institution_name"] == faction_name, "faction_id"] = faction_id

mps.to_pickle(POLITICIANS_OUTPUT / "mps.pkl")

print("Script 04_01 done.")
