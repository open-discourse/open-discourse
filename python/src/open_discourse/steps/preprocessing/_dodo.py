import open_discourse.steps.data._dodo as download_task
import open_discourse.steps.preprocessing.create_electoral_terms as step5
import open_discourse.steps.preprocessing.extract_mps_from_mp_base_data as step4
import open_discourse.steps.preprocessing.split_xml as step2
import open_discourse.steps.preprocessing.split_xml_electoral_term_1_and_2 as step1
import open_discourse.steps.preprocessing.split_xml_electoral_term_20 as step3
from open_discourse.definitions import path
from open_discourse.steps.task_factory import TaskFactory

# Define targets
TARGET_TASK1 = path.RAW_TXT / "02_01.done"
TARGET_TASK2 = path.RAW_TXT / "02_02.done"
TARGET_TASK3 = step3.OUTPUT_PATH / "02_03.done"
TARGET_TASK4 = path.POLITICIANS_STAGE_01 / "02_04.done"
TARGET_TASK5 = path.FINAL / "02_05.done"

# Create task factory
factory = TaskFactory(
    task_group="02_preprocessing",
    task_description="Preprocesses raw XML files by splitting them into manageable chunks and extracting MP data.",
)

# Define tasks using factory
TASK_DEFINITION = {
    "step1": factory.create_task(
        step_module=step1,
        target_paths=[TARGET_TASK1],
        task_deps=["01_download:download_previous_periods"],
        file_deps=[download_task.TARGET_TASK1],
    ),
    "step2": factory.create_task(
        step_module=step2,
        target_paths=[TARGET_TASK2],
        task_deps=["01_download:download_previous_periods"],
        file_deps=[download_task.TARGET_TASK1],
    ),
    "step3": factory.create_task(
        step_module=step3,
        target_paths=[TARGET_TASK3],
        task_deps=["01_download:download_current_period"],
        file_deps=[download_task.TARGET_TASK2],
    ),
    "step4": factory.create_task(
        step_module=step4,
        target_paths=[TARGET_TASK4],
        task_deps=["01_download:download_MdB_data"],
        file_deps=[download_task.TARGET_TASK3],
    ),
    "step5": factory.create_task(
        step_module=step5,
        target_paths=[TARGET_TASK5],
        task_deps=["02_preprocessing:extract_mps_from_mp_base_data"],
        file_deps=[TARGET_TASK4],
    ),
}

# Create task function
task_02_preprocessing = factory.create_task_function(TASK_DEFINITION)
