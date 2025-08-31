import tomllib
import tomli_w
import cattrs
import sys
from src.core.logging import logger
from src.core.fs import app_path
from dataclasses import dataclass, asdict, field



@dataclass
class CheckerSettings:
    interval_ms: int = 600000
    wait_req_ms: int = 5000
    at_startup: bool = True
    auto: bool = True

@dataclass
class NotificationSettings:
    volume: int = 50

@dataclass
class Settings:
    checker: CheckerSettings = field(default_factory=CheckerSettings)
    notification: NotificationSettings = field(default_factory=NotificationSettings)

    @classmethod
    def load(cls) -> 'Settings':
        try:
            with open(app_path().get("data/settings.toml"), "rb") as f:
                settings_dict = asdict(Settings())
                settings_dict.update(tomllib.load(f))
                return cattrs.structure(settings_dict, cls)

        except Exception as e:
            logger().error(f"无法加载设置：{e}")
            sys.exit(-1)

    def save(self):
        with open(app_path().get("data/settings.toml"), "wb") as f:
            f.write(tomli_w.dumps(asdict(self)).encode("utf-8"))


_settings = None

def init_settings():
    global _settings
    _settings = Settings.load()

def settings() -> Settings:
    return _settings