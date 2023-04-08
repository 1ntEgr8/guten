from typing import List
from pathlib import Path
from datetime import datetime, timedelta, timezone
from dateutil.parser import parse as date_parse

from guten.backend import Backend
from guten.press import FetchedSourceGroup
from guten.utils import eprint


METADATA_FILE = ".metadata"

def begin_document():
    return "<html>"

def end_document():
    return "</html>"

def preamble():
    return """
    <head>
        <style>
            html {
                margin: 20px 60px;
            }

            body {
                font-size: 16px;
                font-family: sans-serif;
            }

            h1 {
                border: 10px double black;
                text-align: center;
                padding: 10px;
            }

            details {
                margin: 5px 0px;
                padding: 5px 15px;
                border-radius: 4px;
            }

            details:hover {
                /* background: #ffffd0; */
            }

            a {
                margin-left: 10px;
            }
        </style>
    </head>
    """

def begin_body():
    return "<body>"

def end_body():
    return "</body>"

def h1(s):
    return f"<h1>{s}</h1>"

def h2(s):
    return f"<h2>{s}</h2>"

def h3(s):
    return f"<h3>{s}</h3>"

def small(s):
    return f"<small>{s}</small>"

def begin_list():
    return "<ul>"

def end_list():
    return "</ul>"

def source_item(data):
    return f"""
        <details>
            <summary><a href='{data['link']}'>{data['title']}</a></summary>
            {data['summary']}
        </details>
    """

def DEFAULT_HIST(today):
    return today - timedelta(days=5)


def parse_metadata(data, today):
    dates = [date_parse(d.strip()) for d in data.split(";")]

    if len(dates) == 0:
        return DEFAULT_HIST(today), DEFAULT_HIST(today)
    elif len(dates) == 1:
        return dates[0], DEFAULT_HIST(today)
    else:
        return dates[0], dates[1]
    

class HTMLBackend(Backend):
    async def run(self, groups: List[FetchedSourceGroup], output_dir: Path) -> Path:
        today = datetime.now(timezone.utc)
        output_file = output_dir / f"{today.year}-{today.month}-{today.day}.html"
        metadata_file = output_dir / METADATA_FILE

        hist0, hist1 = None, None
        if metadata_file.exists():
            with open(metadata_file, "r") as f:
                data = f.read()
                hist0, hist1 = parse_metadata(data, today)
        else:
            hist0, hist1 = DEFAULT_HIST(today), DEFAULT_HIST(today)

        # Now, hist0 and hist1 have been set

        # If guten is run more than once, we use hist1 as the previous run
        # date. This approximates a fresh re-run of guten for that day.
        if hist0.date() == today.date():
            previous_run_date = hist1

        eprint(f"Showing entries published after {previous_run_date}")

        with open(output_file, "w") as f:
            f.write(begin_document())
            f.write(preamble())

            f.write(begin_body())

            localdate = datetime.now()
            f.write(h1(f"{localdate.year}/{localdate.month}/{localdate.day}"))

            def process_source(item):
                source, df = item
                if df.empty:
                    return source, []
                data = df
                if "published" in df:
                    df["date"] = df["published"].apply(lambda x: date_parse(x))
                    data = df[df["date"] > previous_run_date]
                data = data[["title", "link", "summary"]]
                data = data.apply(lambda x: source_item(x), axis=1)
                data = list(data)
                return source, data


            for (group, sources) in groups:
                sources = [process_source(source) for source in sources]
                sources = [(source, data) for (source, data) in sources if len(data) > 0]
                if len(sources) == 0:
                    continue

                f.write(h2(group.name.title()))
                for source, data in sources:
                    f.write(h3(source.name))
                    # f.write(begin_list())
                    f.write("".join(data))
                    # f.write(end_list())

            f.write(small(f"Generated at: {today.isoformat()}"))

            f.write(end_body())
            f.write(end_document())

        with open(metadata_file, "w") as f:
            # If hist0.date() == today.date(), set metadate file to:
            # <hist0>;<hist1>
            # Otherwise, set metadata file to:
            # <today>;<hist0>
            if hist0.date() == today.date():
                f.write(hist0.isoformat())
                f.write(";")
                f.write(hist1.isoformat())
            else:
                f.write(today.isoformat())
                f.write(";")
                f.write(hist0.isoformat())

        return output_file



__backend__ = HTMLBackend
