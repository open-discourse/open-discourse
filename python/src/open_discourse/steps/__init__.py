from .contributions._dodo import task_07_contributions
from .data._dodo import task_01_download
from .database._dodo import task_08_upload
from .electoral_term_20._dodo import task_06_electoral_term_20
from .factions._dodo import task_03_factions
from .politicians._dodo import task_04_politicians
from .preprocessing._dodo import task_02_preprocessing
from .speech_content._dodo import task_05_speech_content

__all__ = [
    "task_01_download",
    "task_02_preprocessing",
    "task_03_factions",
    "task_04_politicians",
    "task_05_speech_content",
    "task_06_electoral_term_20",
    "task_07_contributions",
    "task_08_upload",
]
