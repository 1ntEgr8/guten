import toml

from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass

from .source import Source, SourceGroup


SOURCES_KEY = "sources"
SETTINGS_KEY = "settings"

NOGROUP_NAME = "<nogroup>"


class ConfigParseException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


def default_config_dir():
    path = Path("~/.config/guten").expanduser()
    if not path.exists():
        path.mkdir(parents=True)
    return path


DEFAULT_CONFIG_DIR = default_config_dir()
DEFAULT_CONFIG_FILE_NAME = "config.toml"
DEFAULT_CONFIG_PATH = DEFAULT_CONFIG_DIR / DEFAULT_CONFIG_FILE_NAME
DEFAULT_BACKENDS_DIR = DEFAULT_CONFIG_DIR


@dataclass
class Settings:
    backends_dir: Path


def default_settings():
    return Settings(
        backends_dir=Path(DEFAULT_BACKENDS_DIR)
    )


@dataclass
class Config:
    settings: Settings
    source_groups: List[SourceGroup]


    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]):
        # Parse settings
        if SETTINGS_KEY not in config_dict:
            settings = default_settings()
        else:
            # TODO more robust implementation
            settings_dict = config_dict["settings"]
            settings = Settings(
                backends_dir=Path(settings_dict["backends_dir"]).expanduser()
            )

        # Parse source groups
        if SOURCES_KEY not in config_dict:
            raise ConfigParseException(f"Missing '{SOURCES_KEY}' key in config")

        sources_dict = config_dict["sources"]

        nogroup = SourceGroup(NOGROUP_NAME, [])

        # invariant: nogroup is always at the head
        source_groups = [nogroup]

        for (groupname, sources) in sources_dict.items():
            if isinstance(sources, str):
                name = groupname
                url = sources
                nogroup.sources.append(Source(name, url))
            elif isinstance(sources, dict):
                group = SourceGroup(groupname, [])
                for (name, url) in sources.items():
                    if not isinstance(url, str):
                        raise ConfigParseException("Multi-level nesting of source groups is not permitted", None)
                    group.sources.append(Source(name, url))
                source_groups.append(group)
            else:
                raise ConfigParseException(f"Failed to parse '{SOURCES_KEY}' config", None)

        return cls(source_groups=source_groups, settings=settings)


    @classmethod
    def from_str(cls, config_str: str):
        try:
            config_dict = toml.loads(config_str)
            return Config.from_dict(config_dict)
        except ConfigParseException as e:
            raise e
        except Exception as e:
            raise ConfigParseException("Failed to parse config string. It should be a valid TOML string", e)


    @classmethod
    def from_file(cls, path: Path):
        try:
            config_dict = toml.load(path)
            return Config.from_dict(config_dict)
        except ConfigParseException as e:
            raise e
        except Exception as e:
            raise ConfigParseException(f"Failed to parse config file '{str(path)}'. It should be a valid TOML file", e)
