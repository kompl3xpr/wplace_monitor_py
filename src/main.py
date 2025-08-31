from PyQt6.QtWidgets import *
from PyQt6.QtCore import QSharedMemory
from PyQt6.QtGui import QFont, QFontDatabase, QIcon
from src.gui import App
from src.core.utils import parse_sys_args
from src.core import init_settings, settings, init_logger, logger, app_path
from src.migrations import apply_migrations, is_version_too_low
import sys


SYS_ARGS = parse_sys_args()
SHARED_MEMORY_KEY = "wplace_monitor_app_instance_key"

class SingleApplication(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.shared_memory = QSharedMemory(SHARED_MEMORY_KEY)
        self.is_running = not self.shared_memory.create(1, QSharedMemory.AccessMode.ReadWrite)

    def is_already_running(self):
        return self.is_running


def main():
    init_logger()
    logger().info(f"命令行参数: {SYS_ARGS}")

    # 先迁移再加载设置
    if 'migrate-from' in SYS_ARGS:
        apply_migrations(SYS_ARGS['migrate-from'])
    elif is_version_too_low():
        apply_migrations()

    logger().info("正在加载设置...")
    init_settings()
    logger().info(f"当前设置：{settings()}")

    app = SingleApplication(sys.argv)
        
    if app.is_already_running():
        logger().error("应用程序已经在运行。")
        return -1

    app.setWindowIcon(QIcon(app_path().get('assets/icon.ico'))) 
    app.setQuitOnLastWindowClosed(False)

    font_id = QFontDatabase.addApplicationFont(app_path().get("assets/font.ttf"))
    font_families = QFontDatabase.applicationFontFamilies(font_id)
    if font_families:
        font = QFont(font_families[0], 14)
        app.setFont(font)

    window = App()
    if 'hide' not in SYS_ARGS:
        window.show()

    logger().info('欢迎使用 Wplace Monitor')
    window.check_for_updates()
    if settings().checker.at_startup:
        window.check_areas()
    
    exit_code = app.exec()
    logger().info('正在保存设置...')
    settings().save()
    return exit_code


if __name__ == "__main__":
    exit(main())