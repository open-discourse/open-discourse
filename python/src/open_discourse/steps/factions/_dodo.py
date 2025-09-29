import open_discourse.steps.factions.add_abbreviations_and_ids as step2
import open_discourse.steps.factions.create as step1
import open_discourse.steps.preprocessing._dodo as preprocessing_task
from open_discourse.definitions import path
from open_discourse.steps.task_factory import TaskFactory

# Define targets
TARGET_TASK1 = path.FACTIONS_STAGE_01 / "03_01.done"
TARGET_TASK2 = path.FINAL / "03_02.done"

# Create task factory
factory = TaskFactory(
    task_group="03_factions",
    task_description="Creates and processes faction data by adding abbreviations and IDs to match with speeches.",
)

# Define tasks using factory
TASK_DEFINITION = {
    "step1": factory.create_task(
        step_module=step1,
        target_paths=[TARGET_TASK1],
        task_deps=["02_preprocessing:extract_mps_from_mp_base_data"],
        file_deps=[preprocessing_task.TARGET_TASK4],
    ),
    "step2": factory.create_task(
        step_module=step2,
        target_paths=[TARGET_TASK2],
        task_deps=["03_factions:create"],
        file_deps=[TARGET_TASK1],
    ),
}

# Create task function
task_03_factions = factory.create_task_function(TASK_DEFINITION)
