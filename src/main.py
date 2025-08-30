from PyQt6.QtWidgets import *
from PyQt6.QtGui import QFont, QFontDatabase, QIcon
from src.gui import App
from src.core import Settings, logger, path_manager
import sys

def should_hide():
    return "-hide" in sys.argv


if __name__ == "__main__":
    app = QApplication([])
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

    if Settings().check_area_when_boot:
        window.check_areas()
    
    logger().info('欢迎使用 Wplace Monitor')
    app.exec()