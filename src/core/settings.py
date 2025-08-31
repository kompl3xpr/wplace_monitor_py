import tomllib
import tomli_w
from src.core.fs import path_manager

class Settings:
    def __init__(self):
        with open(path_manager.get("data/settings.toml"), "rb") as f:
            settings = tomllib.load(f)
        self.__dict__["_inner"] = settings

    def __getattr__(self, name):
        if name in self.__dict__["_inner"]:
            return self.__dict__["_inner"][name]
        else:
            raise AttributeError('There is no `{name}` option in the settings')


    def __setattr__(self, name, value):
        if name in self.__dict__["_inner"]:
            self.__dict__["_inner"][name] = value
        else:
            raise AttributeError('There is no `{name}` option in the settings')
        
    def save(self):
        with open(path_manager.get("data/settings.toml"), "wb") as f:
            f.write(tomli_w.dumps(self.__dict__["_inner"]).encode("utf-8"))
        
settings = Settings()