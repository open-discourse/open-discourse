import open_discourse.steps.contributions.clean as step2
import open_discourse.steps.contributions.extract as step1
import open_discourse.steps.contributions.match as step3
import open_discourse.steps.factions._dodo as factions_task
import open_discourse.steps.politicians._dodo as politicians_task
import open_discourse.steps.speech_content._dodo as speech_content_task
from open_discourse.definitions import path
from open_discourse.steps.task_factory import TaskFactory

# Define targets
TARGET_TASK1 = [
    path.SPEECH_CONTENT_STAGE_04 / "07_01.done",
    path.CONTRIBUTIONS_EXTENDED_STAGE_01 / "07_01.done",
    path.FINAL / "07_01.done",
]
TARGET_TASK2 = path.CONTRIBUTIONS_EXTENDED_STAGE_02 / "07_02.done"
TARGET_TASK3 = path.CONTRIBUTIONS_EXTENDED_STAGE_03 / "07_03.done"

# Create task factory
factory = TaskFactory(
    task_group="07_contributions",
    task_description="Extracts and processes contributions like comments and interjections from speech content.",
)

# Define tasks using factory
TASK_DEFINITION = {
    "step1": factory.create_task(
        step_module=step1,
        target_paths=TARGET_TASK1,
        task_deps=[
            "03_factions:add_abbreviations_and_ids",
            "05_speech_content:match_names",
        ],
        file_deps=[factions_task.TARGET_TASK2, speech_content_task.TARGET_TASK3],
    ),
    "step2": factory.create_task(
        step_module=step2,
        target_paths=[TARGET_TASK2],
        task_deps=[
            "03_factions:add_abbreviations_and_ids",
            "07_contributions:extract",
        ],
        file_deps=[factions_task.TARGET_TASK2] + TARGET_TASK1,
    ),
    "step3": factory.create_task(
        step_module=step3,
        target_paths=[TARGET_TASK3],
        task_deps=[
            "03_factions:add_abbreviations_and_ids",
            "04_politicians:merge",
            "07_contributions:clean",
        ],
        file_deps=[
            factions_task.TARGET_TASK2,
            politicians_task.TARGET_TASK3,
            TARGET_TASK2,
        ],
    ),
}

# Create task function
task_07_contributions = factory.create_task_function(TASK_DEFINITION)
