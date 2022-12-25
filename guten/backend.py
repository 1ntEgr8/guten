import importlib
import os.path
import pandas as pd

from dataclasses import dataclass
from pathlib import Path
from abc import ABC, abstractmethod
from typing import List

from .utils import prepend_path
from .source import SourceGroup


class LoaderException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class Backend(ABC):
    @abstractmethod
    async def run(self, groups: List[SourceGroup], output_dir: Path) -> Path:
        pass


class Loader:
    backends_dir: Path

    def __init__(self, backends_dir: Path):
        if not backends_dir.exists():
            raise LoaderException(f"Backends dir '{backends_dir}' does not exist")
        self.backends_dir = os.path.realpath(backends_dir)

    def load(self, key: str):
        with prepend_path(self.backends_dir):
            module = importlib.import_module(f'backends.{key}')

        if not hasattr(module, '__backend__'):
            raise LoaderException(f'Module {module} is missing a __backend__ attr')

        return getattr(module, '__backend__')
