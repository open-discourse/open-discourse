import od_lib.definitions.path_definitions as path_definitions
import pandas as pd
import numpy as np
import os

# input directory ______________________________________________________________
POLITICIANS_STAGE_01 = path_definitions.POLITICIANS_STAGE_01

# output directory _____________________________________________________________
FACTIONS_STAGE_01 = path_definitions.FACTIONS_STAGE_01
save_path_factions = os.path.join(FACTIONS_STAGE_01, "factions.pkl")

if not os.path.exists(FACTIONS_STAGE_01):
    os.makedirs(FACTIONS_STAGE_01)

# read data.
politicians = pd.read_pickle(os.path.join(POLITICIANS_STAGE_01, "mdbs.pkl"))

factions = politicians.institution_name.loc[
    (politicians.institution_type == "Fraktion/Gruppe")
]

unique_factions = np.unique(factions)
unique_factions = np.append(
    unique_factions,
    ["Südschleswigscher Wählerverband", "Gast", "Gruppe Nationale Rechte"],
)

unique_factions = pd.DataFrame(unique_factions, columns=["faction_name"])


unique_factions.to_pickle(save_path_factions)
