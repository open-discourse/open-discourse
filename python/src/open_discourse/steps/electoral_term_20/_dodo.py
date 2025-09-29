import open_discourse.steps.electoral_term_20.extract as step1
import open_discourse.steps.factions._dodo as factions_task
import open_discourse.steps.preprocessing._dodo as preprocessing_task
from open_discourse.definitions import path
from open_discourse.steps.task_factory import TaskFactory

# Define targets
TARGET_TASK1 = [
    step1.ELECTORAL_TERM_20_OUTPUT / "06_01.done",
    path.FINAL / "06_01.done",
    path.CONTRIBUTIONS_EXTENDED_STAGE_01 / "06_01.done",
]

# Create task factory
factory = TaskFactory(
    task_group="06_electoral_term_20",
    task_description="Processes data specifically for electoral term 20 with special handling requirements.",
)

# Define tasks using factory
TASK_DEFINITION = {
    "step1": factory.create_task(
        step_module=step1,
        target_paths=TARGET_TASK1,
        task_deps=[
            "02_preprocessing:split_xml_electoral_term_20",
            "03_factions:add_abbreviations_and_ids",
        ],
        file_deps=[preprocessing_task.TARGET_TASK3, factions_task.TARGET_TASK2],
    ),
}

# Create task function
task_06_electoral_term_20 = factory.create_task_function(TASK_DEFINITION)
