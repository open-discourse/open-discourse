import open_discourse.steps.contributions._dodo as contributions_task
import open_discourse.steps.data._dodo as download_task
import open_discourse.steps.database.concat as step1
import open_discourse.steps.database.upload as step2
import open_discourse.steps.electoral_term_20._dodo as electoral_term_20_task
from open_discourse.definitions import path
from open_discourse.steps.task_factory import TaskFactory

# Define targets
TARGET_TASK1 = path.FINAL / "08_01.done"
TARGET_TASK2 = path.FINAL / "08_02.done"

# Create task factory
factory = TaskFactory(
    task_group="08_upload",
    task_description="Concatenates all processed data and uploads it to the database.",
)

# Define tasks using factory
TASK_DEFINITION = {
    "step1": factory.create_task(
        step_module=step1,
        target_paths=[TARGET_TASK1],
        task_deps=[
            "01_download:download_previous_periods",
            "06_electoral_term_20",
            "07_contributions:extract",
            "07_contributions:match",
        ],
        file_deps=[
            download_task.TARGET_TASK1,
            electoral_term_20_task.TARGET_TASK1[0],
            contributions_task.TARGET_TASK1[0],
            contributions_task.TARGET_TASK3,
        ],
    ),
    "step2": factory.create_task(
        step_module=step2,
        target_paths=[TARGET_TASK2],
        task_deps=["08_upload:concat"],
        file_deps=[TARGET_TASK1],
    ),
}

# Create task function
task_08_upload = factory.create_task_function(TASK_DEFINITION)
