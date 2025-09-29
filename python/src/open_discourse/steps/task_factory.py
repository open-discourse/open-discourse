from functools import partial
from pathlib import Path
from typing import Callable

from open_discourse.steps.doit_config import DoitTaskConfig


class TaskFactory:
    def __init__(self, task_group: str, task_description: str = ""):
        self.task_group = task_group
        self.task_description = task_description

    def create_task(
        self,
        step_module: object,
        target_paths: list[Path],
        task_deps: list[str] | None = None,
        file_deps: list[Path] | None = None,
        uptodate: list[Callable] | None = None,
    ) -> dict:
        """Create a standardized doit task configuration."""
        touch_commands = list(map(_create_task_output_action, target_paths))

        return DoitTaskConfig(
            name=step_module.__name__.split(".")[-1],
            actions=[step_module.main] + touch_commands,
            targets=[str(path) for path in target_paths],
            task_dep=task_deps or [],
            file_dep=file_deps or [],
            uptodate=uptodate or [],
        ).model_dump()

    def create_task_function(self, task_definitions: dict) -> Callable:
        """Create the task function that yields all task definitions."""

        def task_function():
            for _, task_definition in task_definitions.items():
                yield task_definition

        task_function.__name__ = f"task_{self.task_group}"
        task_function.__doc__ = self.task_description

        return task_function


def _create_task_output_action(path: Path) -> Callable[[Path], bool]:
    def action(task, path) -> bool:
        if path.exists():
            path.unlink()
        path.touch()
        return True

    return partial(action, path=path)
