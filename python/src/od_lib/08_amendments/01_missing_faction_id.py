# Create the history of politicians party affiliations and fill in missing faction_id
# So far we have missing faction_id for the members of parliament who also hold special position
# i.e. Bundesminister, President, Vicepresident etc.
# Faction affiliation is determined based on xml files with transcripts
# Now I will determine party affiliation based on MDB_STAMMDATEN.XML

import od_lib.definitions.path_definitions as path_definitions
import pandas as pd
import os
import numpy as np
import datetime

# Input
PEOPLE = os.path.join(path_definitions.DATA_FINAL, "politicians.csv")
politicians = pd.read_csv(PEOPLE)

FACTIONS = path_definitions.DATA_FINAL
factions = pd.read_pickle(os.path.join(FACTIONS, "factions.pkl"))

speeches = pd.read_csv(os.path.join(path_definitions.DATABASE, "speeches.csv"))


# Output direcory

save_path = path_definitions.DATABASE

politicians = politicians[politicians.institution_type == 'Fraktion/Gruppe']
politicians = politicians.merge(factions,
                                how='left',
                                left_on='institution_name',
                                right_on='faction_name')

politicians['institution_start_dt'] = pd.to_datetime(politicians['institution_start_dt'], format='%d.%m.%Y')
politicians['institution_end_dt'] = pd.to_datetime(politicians['institution_end_dt'], format='%d.%m.%Y')

end = pd.to_datetime('2200-12-31')
start = pd.to_datetime('1900-01-01')

politicians['institution_start_dt'] = politicians['institution_start_dt'].fillna(start)

politicians = politicians.sort_values(by=['ui', 'electoral_term', 'institution_start_dt', 'institution_end_dt'],
                                      ascending=[True, True, True, True])

politicians = politicians.groupby(['ui', 'electoral_term', 'institution_start_dt']).nth(0).reset_index()

politicians['next_institution_start_dt'] = politicians.groupby(['ui', 'electoral_term']).shift(-1)[
    'institution_start_dt']

# If the current insitution end dt is missing, but the next institution start dt is not missing,
# then overwrite the current institution end dt with the next institution start dt less 1 day

condition = (~politicians.next_institution_start_dt.isnull()) & (politicians.institution_end_dt.isnull())
politicians.institution_end_dt = np.where(condition,
                                          politicians.next_institution_start_dt-pd.Timedelta(days=1),
                                          politicians.institution_end_dt)

print("Number of changes made:", np.sum(condition))

# If the current institution end dt is greater than or equal the next institution start date,
# then overwrite the current institution end dt with the next institution start dt less 1 day

condition = politicians.institution_end_dt >= politicians.next_institution_start_dt
politicians.institution_end_dt = np.where(condition,
                                          politicians.next_institution_start_dt-pd.Timedelta(days=1),
                                          politicians.institution_end_dt)

print("Number of changes made:", np.sum(condition))


# If the next institution start dt is grater than the current institution end dt by more than one day,
# then overwrite the current institution end dt with the next institution start dt less 1 day

condition = politicians.next_institution_start_dt > politicians.institution_end_dt + pd.Timedelta(days=1)
politicians.institution_end_dt = np.where(condition,
                                          politicians.next_institution_start_dt-pd.Timedelta(days=1),
                                          politicians.institution_end_dt)

print("Number of changes made:", np.sum(condition))


politicians['institution_end_dt'] = politicians['institution_end_dt'].fillna(end)
politicians['history_start_dt'] = politicians.groupby(['ui', 'electoral_term'])['institution_start_dt'].transform('min')
politicians['history_end_dt'] = politicians.groupby(['ui', 'electoral_term'])['institution_end_dt'].transform('max')

politicians.to_csv(os.path.join(save_path, 'politicians_history.csv'), index = False)

# Merge with speeches

politicians.rename(columns = {"id" : "faction_id_hist"}, inplace = True)

dt = speeches.merge(politicians[['ui', 'electoral_term', 'faction_id_hist',
                                 'institution_start_dt', 'institution_end_dt',
                                 'history_start_dt', 'history_end_dt']],
               how = 'left',
               left_on = ['politician_id', 'electoral_term'],
               right_on = ['ui', 'electoral_term'])

dt['institution_start_dt'] = dt['institution_start_dt'].fillna(start)
dt['institution_end_dt'] = dt['institution_end_dt'].fillna(end)
dt['history_start_dt'] = dt['history_start_dt'].fillna(start)
dt['history_end_dt'] = dt['history_end_dt'].fillna(end)

dt['date'] = pd.to_datetime(dt['date'], format='%Y-%m-%d')

dt['missing_prev_history'] = np.where((dt.history_start_dt> dt.date) & (dt.history_start_dt==dt.institution_start_dt), True, False)
dt['missing_subs_history'] = np.where((dt.history_end_dt < dt.date) & (dt.history_end_dt==dt.institution_end_dt), True, False)

dt.loc[dt['missing_subs_history'] == True , 'institution_end_dt'] = end
dt.loc[dt['missing_prev_history'] == True , 'institution_start_dt'] = start

dt['keep_rows'] = ((dt.date <= dt.institution_end_dt) & (dt.date >= dt.institution_start_dt)) #| (dt.history_start_dt> dt.date) | (dt.history_end_dt< dt.date)
dt = dt[dt.keep_rows == True]

print(dt.shape)
print(speeches.shape)


dt[dt.faction_id != dt.faction_id_hist].groupby(['faction_id', 'faction_id_hist'])['politician_id'].count()

dt['faction_id'] = np.where(dt['faction_id_hist'].isnull(), dt['faction_id'], dt['faction_id_hist'])

dt['speech_content'] = dt['speech_content'].astype(str)
dt['length'] = dt['speech_content'].str.split().apply(len)

dt = dt.drop([
    'faction_id_hist',
    'institution_start_dt',
    'institution_end_dt',
    'ui',
    'history_start_dt',
    'history_end_dt',
    'missing_prev_history',
    'missing_subs_history',
    'keep_rows'
], axis = 1)

dt.date = pd.to_datetime(dt.date)
dt.date = dt.date.dt.date
dt.speech_content.fillna(" ", inplace=True)


dt.to_csv(os.path.join(path_definitions.DATABASE, "speeches_revised.csv"), index = False)

#dt = pd.read_csv(os.path.join(path_definitions.DATABASE, "speeches_revised.csv"))
