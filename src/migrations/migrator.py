from abc import ABC, abstractmethod
import tomllib
import tomli_w
import os
from src.core import app_path, logger
from packaging import version
from src import __version__

class Migrator(ABC):
    @abstractmethod
    def should_migrate(self) -> bool:
        pass

    @abstractmethod
    def migrate(self) -> bool:
        pass


class Migrator_0_2_3(Migrator):
    def should_migrate(self, from_version: str) -> bool:
        return version.parse(from_version) < version.parse("0.2.3")
    
    def migrate(self):
        # update settings
        try:
            settings = None
            with open(app_path().get("data/settings.toml"), "rb") as f:
                settings =tomllib.load(f)
            
            settings['notification'] = {
                'volume': settings['notification_volume'],
            }

            settings['checker'] = {
                'interval_ms': settings['check_interval_ms'],
                'wait_req_ms':settings['wait_for_next_area_ms'],
                'at_startup': settings['check_area_when_boot'],
                'auto': settings['auto_check_enabled'],
            }

            settings.pop('notification_volume')
            settings.pop('check_interval_ms')
            settings.pop('wait_for_next_area_ms')
            settings.pop('check_area_when_boot')
            settings.pop('auto_check_enabled')

            with open(app_path().get("data/settings.toml"), "wb") as f:
                f.write(tomli_w.dumps(settings).encode("utf-8"))

        except Exception as e:
            logger().error(f"无法更新设置文件: {e}")