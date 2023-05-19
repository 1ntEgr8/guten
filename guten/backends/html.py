from typing import List
from pathlib import Path
from datetime import datetime

from guten.backend import Backend
from guten.press import FetchedSourceGroup
from guten.utils import eprint
from guten.filters import DefaultFilter
from guten.metadata import L10MetadataScheme


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


class HTMLBackend(Backend):
    async def run(self, groups: List[FetchedSourceGroup], output_dir: Path) -> Path:
        with L10MetadataScheme(output_dir) as metadata:
            today = metadata.today
            output_file = output_dir / f"{today.year}-{today.month}-{today.day}.html"
            previous_run_date = metadata.previous_run_date
            groups = DefaultFilter().apply(groups, previous_run_date)

            eprint(f"Showing entries published after {previous_run_date}")

            with open(output_file, "w") as f:
                f.write(begin_document())
                f.write(preamble())

                f.write(begin_body())

                localdate = datetime.now()
                f.write(h1(f"{localdate.year}/{localdate.month}/{localdate.day}"))

                for (group, sources) in groups:
                    f.write(h2(group.name.title()))
                    for source, data in sources:
                        data = data.apply(lambda x: source_item(x), axis=1)
                        data = list(data)

                        f.write(h3(source.name))
                        # f.write(begin_list())
                        f.write("".join(data))
                        # f.write(end_list())

                f.write(small(f"Generated at: {today.isoformat()}"))

                f.write(end_body())
                f.write(end_document())

        return output_file


__backend__ = HTMLBackend
