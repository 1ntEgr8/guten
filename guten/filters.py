from abc import ABC, abstractmethod
from typing import List
from dateutil.parser import parse as date_parse

from .source import SourceGroup


class Filter(ABC):
    @abstractmethod
    def apply(self, groups: List[SourceGroup]) -> List[SourceGroup]:
        pass


class DefaultFilter(Filter):
    def apply(self, groups: List[SourceGroup], previous_run_date) -> List[SourceGroup]:
        def process_source(item):
            source, df = item
            if df.empty:
                return source, []
            data = df
            if "published" in df:
                df["date"] = df["published"].apply(lambda x: date_parse(x))
                data = df[df["date"] > previous_run_date]
            data = data[["title", "link", "summary"]]
            return source, data

        new_groups = []
        for (group, sources) in groups:
            sources = [process_source(source) for source in sources]
            sources = [(source, data) for (source, data) in sources if len(data) > 0]
            if len(sources) == 0:
                continue
            new_groups.append((group, sources))
        return new_groups

             



    
