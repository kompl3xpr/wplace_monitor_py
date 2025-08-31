import sys
import os
from pathlib import Path

class AppPath:
    def __init__(self):
        workspace = Path(__file__).resolve().parent.parent.parent
        if getattr(sys, 'frozen', False):
            self.base_path = Path(sys.executable).parent
        else:
            self.base_path = workspace

    def get(self, relative_path: str):
        relative_path = relative_path.split('/')
        return str(self.base_path.joinpath(*relative_path))
    
    def get_original_image(self, area_name: str):
        return self.get(f"data/originals/{area_name}.png")

    def get_mask_image(self, area_name: str):
        return self.get(f"data/masks/{area_name}.png")

_app_path = AppPath()

def app_path() -> AppPath:
    return _app_path