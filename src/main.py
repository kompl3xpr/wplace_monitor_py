from PyQt6.QtWidgets import *
from PyQt6.QtCore import QSharedMemory
from PyQt6.QtGui import QFont, QFontDatabase, QIcon
from src.gui import App
from src.core import Settings, logger, path_manager
import sys

def should_hide():
    return "-hide" in sys.argv


SHARED_MEMORY_KEY = "wplace_monitor_app_instance_key"

class SingleApplication(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.shared_memory = QSharedMemory(SHARED_MEMORY_KEY)
        self.is_running = not self.shared_memory.create(1, QSharedMemory.AccessMode.ReadWrite)

    def is_already_running(self):
        return self.is_running


if __name__ == "__main__":
    app = SingleApplication(sys.argv)
        
    if app.is_already_running():
        print("应用程序已经在运行。")
        sys.exit(-1)

    app.setWindowIcon(QIcon(path_manager.get('assets/icon.ico'))) 
    app.setQuitOnLastWindowClosed(False)

    font_id = QFontDatabase.addApplicationFont(path_manager.get("assets/font.ttf"))
    font_families = QFontDatabase.applicationFontFamilies(font_id)
    if font_families:
        font = QFont(font_families[0], 14)
        app.setFont(font)

    window = App()
    if not should_hide():
        window.show()

    logger().info('欢迎使用 Wplace Monitor')
    window.check_for_updates()
    if Settings().check_area_when_boot:
        window.check_areas()
    
    app.exec()