import od_lib.definitions.path_definitions as path_definitions
import pandas as pd
import numpy as np
import os

# input directory
POLITICIANS_STAGE_01 = path_definitions.POLITICIANS_STAGE_01

# output directory
FACTIONS_STAGE_01 = path_definitions.FACTIONS_STAGE_01
save_path_factions = os.path.join(FACTIONS_STAGE_01, "factions.pkl")

if not os.path.exists(FACTIONS_STAGE_01):
    os.makedirs(FACTIONS_STAGE_01)

# read data.
mps = pd.read_pickle(os.path.join(POLITICIANS_STAGE_01, "mps.pkl"))

factions = mps.institution_name.loc[(mps.institution_type == "Fraktion/Gruppe")]

unique_factions = np.unique(factions)
unique_factions = np.append(
    unique_factions,
    ["Südschleswigscher Wählerverband", "Gast", "Gruppe Nationale Rechte"],
)

unique_factions = pd.DataFrame(unique_factions, columns=["faction_name"])


unique_factions.to_pickle(save_path_factions)
