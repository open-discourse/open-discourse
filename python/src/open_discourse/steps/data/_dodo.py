from doit.tools import run_once

import open_discourse.steps.data.download_current_period as step2
import open_discourse.steps.data.download_MdB_data as step3
import open_discourse.steps.data.download_previous_periods as step1
from open_discourse.definitions import path
from open_discourse.steps.task_factory import TaskFactory

# Define targets
TARGET_TASK1 = path.RAW_XML / "01_01.done"
TARGET_TASK2 = step2.OUTPUT_PATH / "01_02.done"
TARGET_TASK3 = path.MP_BASE_DATA / "01_03.done"

# Create task factory
factory = TaskFactory(
    task_group="01_download", task_description="Downloads raw XML files from the Bundestag server and MdB data."
)

# Define tasks using factory
TASK_DEFINITION = {
    "step1": factory.create_task(
        step_module=step1,
        target_paths=[TARGET_TASK1],
        uptodate=[run_once],
    ),
    "step2": factory.create_task(
        step_module=step2,
        target_paths=[TARGET_TASK2],
        uptodate=[run_once],
    ),
    "step3": factory.create_task(
        step_module=step3,
        target_paths=[TARGET_TASK3],
        uptodate=[run_once],
    ),
}

# Create task function
task_01_download = factory.create_task_function(TASK_DEFINITION)
