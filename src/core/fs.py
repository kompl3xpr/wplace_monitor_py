import sys
import os
from pathlib import Path

class PathManager:
    def __init__(self):
        workspace = Path(__file__).resolve().parent.parent.parent
        if getattr(sys, 'frozen', False):
            self.base_path = Path(sys.executable).parent
        else:
            self.base_path = workspace

    def get(self, relative_path: str):
            relative_path = relative_path.split('/')
            return str(self.base_path.joinpath(*relative_path))

path_manager = PathManager()