import od_lib.definitions.path_definitions as path_definitions
import pandas as pd
import os

SPOKEN_CONTENT = path_definitions.FINAL
CONTRIBUTIONS = path_definitions.FINAL
POLITICIANS = path_definitions.FINAL

speeches = pd.read_pickle(os.path.join(SPOKEN_CONTENT, "spoken_content.pkl"))
contributions = pd.read_pickle(os.path.join(CONTRIBUTIONS, "contributions.pkl"))
people = pd.read_csv(os.path.join(POLITICIANS, "people.csv"))

people = people.drop_duplicates(subset=["ui"], keep="first")

print("Anzahl an Speeches:", str(len(speeches)))
print("Anzahl an Contributions:", str(len(contributions)))
print("Anzahl an Politikern:", str(len(people)))
