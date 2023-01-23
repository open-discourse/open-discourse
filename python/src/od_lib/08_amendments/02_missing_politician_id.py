
import od_lib.definitions.path_definitions as path_definitions
import pandas as pd
import os

# Input
PEOPLE = os.path.join(path_definitions.DATA_FINAL, "politicians.csv")
politicians = pd.read_csv(PEOPLE)

FACTIONS = path_definitions.DATA_FINAL
factions = pd.read_pickle(os.path.join(FACTIONS, "factions.pkl"))

speeches = pd.read_csv(os.path.join(path_definitions.DATABASE, "speeches.csv"))


# Output direcory

save_path = path_definitions.DATABASE

dt_noid = speeches[ speeches.politician_id == -1].drop_duplicates(subset = ['first_name', 'last_name', 'electoral_term'])
dt_names = politicians.drop_duplicates(subset = ['first_name', 'last_name', 'electoral_term'])
dt_noid['first_name'] = dt_noid.first_name.str.lower()
dt_noid['last_name'] = dt_noid.last_name.str.lower()

dt_names['first_name_lower'] = politicians['first_name'].str.lower()
dt_names['last_name_lower'] = politicians['last_name'].str.lower()

dt_noid = dt_noid.merge(dt_names.drop_duplicates(subset = ['first_name','last_name_lower', 'electoral_term']), how = 'left', left_on = ['last_name', 'electoral_term'], right_on = ['last_name_lower', 'electoral_term'])
matched = dt_noid[~dt_noid.first_name_lower.isnull()]
matched['dupl'] = matched.duplicated(subset = ['electoral_term','first_name_x', 'last_name_x'], keep = False)
matched = matched[matched.dupl == False]

matched[(matched.first_name_x.isnull() | ( matched.first_name_lower == matched.first_name_x))].groupby('position_short').count()
tab = matched[(matched.first_name_x.isnull() | ( matched.first_name_lower == matched.first_name_x))]

tab.groupby('position_short').count()

test = pd.read_pickle(os.path.join(path_definitions.DATA_FINAL, "speech_content.pkl"))
test[test.last_name=='Nordt'] # tu jes politician_id: 999990107
speeches[speeches.last_name=='Nordt'] # tu nie ma
