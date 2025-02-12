import numpy as np
import pandas as pd

import open_discourse.definitions.path_definitions as path_definitions

# input directory
POLITICIANS_STAGE_01 = path_definitions.POLITICIANS_STAGE_01
# output directory
FACTIONS_STAGE_01 = path_definitions.FACTIONS_STAGE_01
FACTIONS_STAGE_01.mkdir(parents=True, exist_ok=True)

# read data.
mps = pd.read_pickle(POLITICIANS_STAGE_01 / "mps.pkl")

factions = mps.loc[mps["institution_type"] == "Fraktion/Gruppe", "institution_name"]

unique_factions = np.unique(factions)
unique_factions = np.append(
    unique_factions,
    [
        "Südschleswigscher Wählerverband",
        "Gast",
        "Gruppe Nationale Rechte",
        "Deutsche Soziale Union",
    ],
)

unique_factions = pd.DataFrame(unique_factions, columns=["faction_name"])

save_path_factions = FACTIONS_STAGE_01 / "factions.pkl"
unique_factions.to_pickle(save_path_factions)
