import numpy as np
import pandas as pd

from open_discourse.definitions import path

# input directory
FACTIONS_STAGE_01 = path.FACTIONS_STAGE_01

# output directory
DATA_FINAL = path.DATA_FINAL
DATA_FINAL.mkdir(parents=True, exist_ok=True)

factions = pd.read_pickle(FACTIONS_STAGE_01 / "factions.pkl")

abbreviations_dict = {
    "Alternative für Deutschland": "AfD",
    "Deutsche Soziale Union": "DSU",
    "Fraktion Alternative für Deutschland": "AfD",
    "Fraktion Bayernpartei": "BP",
    "Fraktion Bündnis 90/Die Grünen": "Bündnis 90/Die Grünen",
    "Fraktion DIE LINKE.": "DIE LINKE.",
    "Fraktion DP/DPB (Gast)": "DP/DPB",
    "Fraktion DRP (Gast)": "DRP",
    "Fraktion Demokratische Arbeitsgemeinschaft": "DA",
    "Fraktion Deutsche Partei": "DP",
    "Fraktion Deutsche Partei Bayern": "DPB",
    "Fraktion Deutsche Partei/Deutsche Partei Bayern": "DP/DPB",
    "Fraktion Deutsche Partei/Freie Volkspartei": "DP/FVP",
    "Fraktion Deutsche Reichspartei": "DRP",
    "Fraktion Deutsche Reichspartei/Nationale Rechte": "DRP/NR",
    "Fraktion Deutsche Zentrums-Partei": "Z",
    "Fraktion Deutscher Gemeinschaftsblock der Heimatvertriebenen und Entrechteten": "BHE",
    "Fraktion Die Grünen": "Bündnis 90/Die Grünen",
    "Fraktion Die Grünen/Bündnis 90": "Bündnis 90/Die Grünen",
    "Fraktion BÜNDNIS 90/DIE GRÜNEN": "Bündnis 90/Die Grünen",
    "Fraktion Freie Volkspartei": "FVP",
    "Fraktion Föderalistische Union": "FU",
    "Fraktion Gesamtdeutscher Block / Block der Heimatvertriebenen und Entrechteten": "GB/BHE",
    "Fraktion WAV (Gast)": "WAV",
    "Fraktion Wirtschaftliche Aufbauvereinigung": "WAV",
    "Fraktion der CDU/CSU (Gast)": "CDU/CSU",
    "Fraktion der Christlich Demokratischen Union/Christlich - Sozialen Union": "CDU/CSU",
    "Fraktion der FDP (Gast)": "FDP",
    "Fraktion der Freien Demokratischen Partei": "FDP",
    "Fraktion der Kommunistischen Partei Deutschlands": "KPD",
    "Fraktion der Partei des Demokratischen Sozialismus": "PDS",
    "Fraktion der SPD (Gast)": "SPD",
    "Fraktion der Sozialdemokratischen Partei Deutschlands": "SPD",
    "Fraktionslos": "Fraktionslos",
    "Gruppe Bündnis 90/Die Grünen": "Bündnis 90/Die Grünen",
    "Gruppe BSW - Bündnis Sahra Wagenknecht - Vernunft und Gerechtigkeit": "BSW",
    "Gruppe Deutsche Partei": "DP",
    "Gruppe Die Linke": "DIE LINKE.",
    "Gruppe Kraft/Oberländer": "KO",
    "Gruppe der Partei des Demokratischen Sozialismus": "PDS",
    "Gruppe der Partei des Demokratischen Sozialismus/Linke Liste": "PDS",
    "Südschleswigscher Wählerverband": "SSW",
    "Gast": "Gast",
    "Gruppe Nationale Rechte": "NR",
}

factions.insert(0, "abbreviation", "")
factions["abbreviation"] = factions["faction_name"].apply(lambda x: abbreviations_dict[x])

unique_abbreviations = np.unique(factions["abbreviation"])
faction_ids = list(range(len(unique_abbreviations)))

factions.insert(0, "id", -1)

for abbrev, id in zip(unique_abbreviations, faction_ids):
    factions.loc[factions["abbreviation"] == abbrev, "id"] = id

# save the dataframe
factions.to_pickle(DATA_FINAL / "factions.pkl")

print("Script 03_02 done.")
