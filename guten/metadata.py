from pathlib import Path
from datetime import datetime, timedelta, timezone
from dateutil.parser import parse as date_parse


class L10MetadataScheme:
    today: datetime
    previous_run_date: datetime
    hist0: datetime
    hist1: datetime
    output_dir: Path

    METADATA_FILE = ".metadata"

    def default_hist(self, today):
        return today - timedelta(days=5)

    def parse_metadata(self, data, today):
        dates = [date_parse(d.strip()) for d in data.split(";")]

        if len(dates) == 0:
            return self.default_hist(today), self.default_hist(today)
        elif len(dates) == 1:
            return dates[0], self.default_hist(today)
        else:
            return dates[0], dates[1]

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir

    def __enter__(self):
        today = datetime.now(timezone.utc)
        metadata_file = self.output_dir / self.METADATA_FILE
        hist0, hist1 = None, None
        if metadata_file.exists():
            with open(metadata_file, "r") as f:
                data = f.read()
                hist0, hist1 = self.parse_metadata(data, today)
        else:
            hist0, hist1 = self.default_hist(today), self.default_hist(today)
        # Now, hist0 and hist1 have been set

        # If guten is run more than once, we use hist1 as the previous run
        # date. This approximates a fresh re-run of guten for that day.
        if hist0.date() == today.date():
            previous_run_date = hist1
        else:
            previous_run_date = hist0

        self.hist0 = hist0
        self.hist1 = hist1
        self.previous_run_date = previous_run_date
        self.today = today

        return self


    def __exit__(self, exc_type, exc_val, exc_tb):
        metadata_file = self.output_dir / self.METADATA_FILE
        with open(metadata_file, "w") as f:
            # If self.hist0.date() == self.today.date(), set metadata file to:
            # <hist0>;<hist1>
            # Otherwise, set metadata file to:
            # <today>;<hist0>
            if self.hist0.date() == self.today.date():
                f.write(self.hist0.isoformat())
                f.write(";")
                f.write(self.hist1.isoformat())
            else:
                f.write(self.today.isoformat())
                f.write(";")
                f.write(self.hist0.isoformat())
