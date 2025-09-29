from pathlib import Path
from typing import Callable, List

from pydantic import BaseModel


class DoitTaskConfig(BaseModel):
    name: str
    actions: List[Callable | str]
    targets: List[str]
    task_dep: List[str] = []
    file_dep: List[Path] = []
    uptodate: List[Callable] = []
