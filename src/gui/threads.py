from PyQt6.QtCore import QThread, pyqtSignal
from src.core import AreaManager, monitor_all
import asyncio

class CheckThread(QThread):
    finished = pyqtSignal(dict)

    def __init__(self, areas):
        super().__init__()
        self._areas = areas

    def run(self):
        results = asyncio.run(monitor_all(self._areas))
        self.finished.emit(results)