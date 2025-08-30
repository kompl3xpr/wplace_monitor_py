import tomllib
import tomli_w
from src.core.fs import path_manager

class Settings:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            # 只在第一次实例化时执行
            with open(path_manager.get("data/settings.toml"), "rb") as f:
                settings = tomllib.load(f)
            self.__dict__["_settings"] = settings
            Settings._initialized = True

    def __getattr__(self, name):
        if name in self.__dict__["_settings"]:
            return self.__dict__["_settings"][name]
        else:
            raise AttributeError('There is no `{name}` option in the settings')


    def __setattr__(self, name, value):
        if name in self.__dict__["_settings"]:
            self.__dict__["_settings"][name] = value
        else:
            raise AttributeError('There is no `{name}` option in the settings')
        
    def save(self):
        with open(path_manager.get("data/settings.toml"), "wb") as f:
            f.write(tomli_w.dumps(self.__dict__["_settings"]).encode("utf-8"))
        