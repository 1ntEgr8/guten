import sys
import argparse
import toml
import asyncio

from pathlib import Path

from .config import Config, DEFAULT_CONFIG_PATH
from .press import Press


async def main():
    parser = argparse.ArgumentParser(description="guten - compile rss/atom feeds into a combined feed")
    parser.add_argument("--config-file", type=str, help="Path to config file", default=str(DEFAULT_CONFIG_PATH))
    parser.add_argument("--output-dir", type=str, help="Path to output directory", default=str(Path(".")))
    parser.add_argument("--backend", type=str, help="Backend to use", default="html")

    args = parser.parse_args()

    config = Config.from_file(args.config_file)
    press = Press(config)
    output_file = await press.run(
        backend_key=args.backend,
        output_dir=args.output_dir
    )
    print(output_file)

if __name__ == "__main__":
    asyncio.run(main())
