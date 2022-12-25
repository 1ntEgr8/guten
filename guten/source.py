from dataclasses import dataclass
from typing import List


@dataclass
class Source:
    name: str
    url: str


@dataclass
class SourceGroup:
    name: str
    sources: List[Source]
