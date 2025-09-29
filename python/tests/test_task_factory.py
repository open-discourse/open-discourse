from pathlib import Path
from typing import Dict

import pytest

from open_discourse.steps.task_factory import TaskFactory


@pytest.fixture
def task_factory():
    return TaskFactory("test_group", "Test description")


@pytest.fixture
def mock_module():
    class MockModule:
        __name__ = "open_discourse.steps.mock_step"

        @staticmethod
        def main(task):
            return True

    return MockModule()


def test_task_factory_init(task_factory):
    assert task_factory.task_group == "test_group"
    assert task_factory.task_description == "Test description"


def test_create_task(task_factory, mock_module):
    target_paths = [Path("test/path1.txt"), Path("test/path2.txt")]
    task_deps = ["task1", "task2"]
    file_deps = ["file1.txt", "file2.txt"]
    uptodate = [lambda: True]

    task = task_factory.create_task(
        mock_module,
        target_paths,
        task_deps,
        file_deps,
        uptodate,
    )

    assert isinstance(task, Dict)
    assert task["name"] == "mock_step"
    assert len(task["actions"]) == 3  # main action + 2 touch commands
    assert task["targets"] == [str(path) for path in target_paths]
    assert task["task_dep"] == task_deps
    assert task["file_dep"] == file_deps
    assert task["uptodate"] == uptodate


def test_create_task_with_defaults(task_factory, mock_module):
    target_paths = [Path("test/path.txt")]

    task = task_factory.create_task(mock_module, target_paths)

    assert task["task_dep"] == []
    assert task["file_dep"] == []
    assert task["uptodate"] == []


def test_create_task_function(task_factory):
    task_definitions = {
        "task1": {"name": "task1", "actions": ["action1"]},
        "task2": {"name": "task2", "actions": ["action2"]},
    }

    task_function = task_factory.create_task_function(task_definitions)

    assert task_function.__name__ == "task_test_group"
    assert task_function.__doc__ == "Test description"

    # Convert generator to list to test its contents
    tasks = list(task_function())
    assert len(tasks) == 2
    assert tasks[0]["name"] == "task1"
    assert tasks[1]["name"] == "task2"
    assert tasks[0]["actions"] == ["action1"]
    assert tasks[1]["actions"] == ["action2"]
