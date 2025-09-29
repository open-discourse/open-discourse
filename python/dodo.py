"""
Main doit task file that imports and exposes all task functions.
Tasks are executed in the order defined by their dependencies.
"""

from open_discourse.steps.contributions._dodo import task_07_contributions
from open_discourse.steps.data._dodo import task_01_download
from open_discourse.steps.database._dodo import task_08_upload
from open_discourse.steps.electoral_term_20._dodo import task_06_electoral_term_20
from open_discourse.steps.factions._dodo import task_03_factions
from open_discourse.steps.politicians._dodo import task_04_politicians
from open_discourse.steps.preprocessing._dodo import task_02_preprocessing
from open_discourse.steps.speech_content._dodo import task_05_speech_content

# Order here doesn't matter as dependencies control execution order
TASKS = [
    task_01_download,
    task_02_preprocessing,
    task_03_factions,
    task_04_politicians,
    task_05_speech_content,
    task_06_electoral_term_20,
    task_07_contributions,
    task_08_upload,
]

# Make tasks available to doit
globals().update({task.__name__: task for task in TASKS})
