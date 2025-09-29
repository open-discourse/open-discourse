import open_discourse.steps.factions._dodo as factions_task
import open_discourse.steps.politicians._dodo as politicians_task
import open_discourse.steps.preprocessing._dodo as preprocessing_task
import open_discourse.steps.speech_content.clean as step2
import open_discourse.steps.speech_content.extract as step1
import open_discourse.steps.speech_content.match_names as step3
from open_discourse.definitions import path
from open_discourse.steps.task_factory import TaskFactory

# Define targets
TARGET_TASK1 = path.SPEECH_CONTENT_STAGE_01 / "05_01.done"
TARGET_TASK2 = path.SPEECH_CONTENT_STAGE_02 / "05_02.done"
TARGET_TASK3 = path.SPEECH_CONTENT_STAGE_03 / "05_03.done"

# Create task factory
factory = TaskFactory(
    task_group="05_speech_content",
    task_description="Extracts and processes speech content by cleaning the text and matching speaker names.",
)

# Define tasks using factory
TASK_DEFINITION = {
    "step1": factory.create_task(
        step_module=step1,
        target_paths=[TARGET_TASK1],
        task_deps=[
            "02_preprocessing:split_xml_electoral_term_1_and_2",
            "02_preprocessing:split_xml",
        ],
        file_deps=[preprocessing_task.TARGET_TASK1, preprocessing_task.TARGET_TASK2],
    ),
    "step2": factory.create_task(
        step_module=step2,
        target_paths=[TARGET_TASK2],
        task_deps=[
            "03_factions:add_abbreviations_and_ids",
            "05_speech_content:extract",
        ],
        file_deps=[factions_task.TARGET_TASK2, TARGET_TASK1],
    ),
    "step3": factory.create_task(
        step_module=step3,
        target_paths=[TARGET_TASK3],
        task_deps=["04_politicians:merge", "05_speech_content:clean"],
        file_deps=[politicians_task.TARGET_TASK3, TARGET_TASK2],
    ),
}

# Create task function
task_05_speech_content = factory.create_task_function(TASK_DEFINITION)
