from pathlib import Path
from typing import List

import pytest
from pydantic import ValidationError

from open_discourse.steps.doit_config import DoitTaskConfig


def dummy_action():
    return True


def dummy_uptodate():
    return True


def test_doit_task_config_minimal():
    """Test creation with minimal required fields."""
    config = DoitTaskConfig(
        name="test_task",
        actions=[dummy_action],
        targets=["/path/to/target"],
    )

    assert config.name == "test_task"
    assert len(config.actions) == 1
    assert config.actions[0] == dummy_action
    assert config.targets == ["/path/to/target"]
    assert config.task_dep == []
    assert config.file_dep == []
    assert config.uptodate == []


def test_doit_task_config_full():
    """Test creation with all fields."""
    config = DoitTaskConfig(
        name="full_task",
        actions=[dummy_action, "echo 'hello'"],
        targets=[Path("target1.txt"), "target2.txt"],
        task_dep=["task1", "task2"],
        file_dep=[Path("dep1.txt"), "dep2.txt"],
        uptodate=[dummy_uptodate],
    )

    assert config.name == "full_task"
    assert len(config.actions) == 2
    assert isinstance(config.targets[0], Path)
    assert isinstance(config.targets[1], str)
    assert config.task_dep == ["task1", "task2"]
    assert isinstance(config.file_dep[0], Path)
    assert isinstance(config.file_dep[1], str)
    assert len(config.uptodate) == 1


def test_doit_task_config_validation():
    """Test validation errors."""
    with pytest.raises(ValidationError):
        # Missing required field 'actions'
        DoitTaskConfig(
            name="invalid_task",
            targets=["/path/to/target"],
        )

    with pytest.raises(ValidationError):
        # Missing required field 'targets'
        DoitTaskConfig(
            name="invalid_task",
            actions=[dummy_action],
        )

    with pytest.raises(ValidationError):
        # Missing required field 'name'
        DoitTaskConfig(
            actions=[dummy_action],
            targets=["/path/to/target"],
        )


def test_doit_task_config_empty_lists():
    """Test that empty lists are handled correctly for optional fields."""
    config = DoitTaskConfig(
        name="empty_lists",
        actions=[dummy_action],
        targets=["target.txt"],
        task_dep=[],
        file_dep=[],
        uptodate=[],
    )

    assert isinstance(config.task_dep, List)
    assert len(config.task_dep) == 0
    assert isinstance(config.file_dep, List)
    assert len(config.file_dep) == 0
    assert isinstance(config.uptodate, List)
    assert len(config.uptodate) == 0
