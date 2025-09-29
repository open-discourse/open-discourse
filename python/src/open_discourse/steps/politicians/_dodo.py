from doit.tools import run_once

import open_discourse.steps.factions._dodo as factions_task
import open_discourse.steps.politicians.add_faction_id_to_mps as step1
import open_discourse.steps.politicians.merge as step3
import open_discourse.steps.politicians.scrape_mgs as step2
import open_discourse.steps.preprocessing._dodo as preprocessing_task
from open_discourse.definitions import path
from open_discourse.steps.task_factory import TaskFactory

# Define targets
TARGET_TASK1 = path.POLITICIANS_STAGE_02 / "04_01.done"
TARGET_TASK2 = path.POLITICIANS_STAGE_01 / "04_02.done"
TARGET_TASK3 = path.FINAL / "04_03.done"

# Create task factory
factory = TaskFactory(
    task_group="04_politicians",
    task_description="Processes politician data by merging MP information with faction IDs and scraped data.",
)

# Define tasks using factory
TASK_DEFINITION = {
    "step1": factory.create_task(
        step_module=step1,
        target_paths=[TARGET_TASK1],
        task_deps=[
            "02_preprocessing:extract_mps_from_mp_base_data",
            "03_factions:add_abbreviations_and_ids",
        ],
        file_deps=[preprocessing_task.TARGET_TASK4, factions_task.TARGET_TASK2],
    ),
    "step2": factory.create_task(
        step_module=step2,
        target_paths=[TARGET_TASK2],
        uptodate=[run_once],
    ),
    "step3": factory.create_task(
        step_module=step3,
        target_paths=[TARGET_TASK3],
        task_deps=[
            "03_factions:add_abbreviations_and_ids",
            "04_politicians:add_faction_id_to_mps",
            "04_politicians:scrape_mgs",
        ],
        file_deps=[factions_task.TARGET_TASK2, TARGET_TASK1, TARGET_TASK2],
    ),
}

# Create task function
task_04_politicians = factory.create_task_function(TASK_DEFINITION)
