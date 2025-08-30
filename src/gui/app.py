from PyQt6.QtWidgets import *
from PyQt6.QtCore import QTimer, QTime
from PyQt6.QtGui import QAction, QIcon

from src.core import AreaManager, init_logger, logger, Settings, path_manager
from src.gui.area_info_list import AreaInfoListItemWidget
from src.gui.status_bar import AppStatusBar
from src.gui.settings_dialog import SettingsDialog
from src.gui.threads import CheckThread
from src.gui.notification import show_notification
from src.gui.new_area_dialog import NewAreaDialog

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WPlace Monitor")
        self.setGeometry(100, 100, 900, 600)
        self.results = dict([(area['name'], None) for area in AreaManager().areas])
        self.init_ui()

    def init_ui(self):
        # Tray Icon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(path_manager.get("assets/icon.ico")))
        tray_menu = QMenu()
        show_action = QAction("显示窗口", self)
        quit_action = QAction("退出", self)
        show_action.triggered.connect(self.show_window)
        quit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.show()

        # Toolbar
        toolbar = self.addToolBar("主工具栏")

        refresh_action = QAction("刷新", self)
        refresh_action.triggered.connect(self.update_list)
        toolbar.addAction(refresh_action)

        self.check_action = QAction("检查全部", self)
        self.check_action.triggered.connect(self.check_areas)
        toolbar.addAction(self.check_action)

        self.set_checking(False)
        self.auto_check_enabled = Settings().auto_check_enabled
        text = "关闭自动检查" if self.auto_check_enabled else "开启自动检查"
        self.auto_check_action = QAction(text, self)
        self.auto_check_action.triggered.connect(self.toggle_auto_check)
        toolbar.addAction(self.auto_check_action)

        add_area_action = QAction("添加", self)
        add_area_action.triggered.connect(self.add_area)
        toolbar.addAction(add_area_action)

        import_action = QAction("设置", self)
        import_action.triggered.connect(self.open_settings)
        toolbar.addAction(import_action)

        self.app_sbar = AppStatusBar(self)
        self.setStatusBar(self.app_sbar)
        init_logger(self.app_sbar)

        self.area_list_widget = QListWidget()
        self.setCentralWidget(self.area_list_widget)

        # add timer to check areas
        self.check_timer = QTimer(self)
        self.check_timer.timeout.connect(self.check_areas)
        if self.auto_check_enabled:
            self._start_auto_check_timer()

        timer = QTimer(self)
        timer.timeout.connect(self.set_next_update)
        timer.start(2000)

        self.update_list()

    def set_checking(self, is_checking: bool):
        self.is_checking = is_checking
        self.setEnabled(not is_checking)

    def _start_auto_check_timer(self):
        self.start_check_time = QTime.currentTime()
        self.check_timer.start(Settings().check_interval_ms)

    def toggle_auto_check(self):
        if self.auto_check_enabled:
            self.check_timer.stop()
            self.auto_check_enabled = False
            self.auto_check_action.setText('开启自动检查')
        else:
            self._start_auto_check_timer()
            self.auto_check_enabled = True
            self.auto_check_action.setText('关闭自动检查')
        self.set_next_update()

    def set_next_update(self):
        if self.is_checking:
            self.app_sbar.set_next_update(-3)
        elif self.auto_check_enabled:
            elapsed = self.start_check_time.msecsTo(QTime.currentTime())
            remaining = self.check_timer.interval() - elapsed
            self.app_sbar.set_next_update(remaining)
        else:
            self.app_sbar.set_next_update(-2)
        

    def add_area(self):
        dialog = NewAreaDialog(self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            name = dialog.get_name()
            x = dialog.get_x()
            y = dialog.get_y()
            if not name or not (0 <= x < 2048) or not (0 <= y < 2048):
                QMessageBox.warning(self, '输入错误', '输入无效，请检查名字和坐标范围。')
                return

            AreaManager().add_area(name, x, y)
            self.update_list_with_new_results({name: None})


    def open_settings(self):
        setting_dialog = SettingsDialog(self)
        setting_dialog.exec()

    def check_areas(self):
        logger().info('正在检查所有区域...')

        def _slot(results):
            self.check_timer.stop()
            self.update_list_with_new_results(results)
            if self.auto_check_enabled:
                self._start_auto_check_timer()
            self.set_checking(False)
            logger().info('所有区域已检查完毕')
            self.send_notification()

        self.check_area_thread = CheckThread(AreaManager().areas)
        self.check_area_thread.finished.connect(_slot)
        self.set_checking(True)
        self.check_area_thread.start()

    def send_notification(self):
        messages = []
        for area_name, result in self.results.items():
            if result is None:
                continue
            diffs = len(result['diffs'])
            if diffs > 0:
                messages.append(f'`{area_name}` 有 {diffs} 个异常像素')

        if len(messages) > 0:
            show_notification('检查出异常像素', '\n'.join(messages))


    def update_list_with_new_results(self, results):
        self.results.update(results)
        self.update_list()

    def update_list(self):
        self.area_list_widget.clear()
        self.clear_removed_results()
        sorted_results = sorted(self.results.items(), key=lambda item: -1 if item[1] is None else len(item[1]['diffs']), reverse=True)

        for area_name, result in sorted_results:
            item_widget = AreaInfoListItemWidget(self, area_name, result)
            list_item = QListWidgetItem(self.area_list_widget)
            list_item.setSizeHint(item_widget.sizeHint())
            self.area_list_widget.addItem(list_item)
            self.area_list_widget.setItemWidget(list_item, item_widget)

    def clear_removed_results(self):
        to_deleted = []

        for area_name in self.results.keys():
            if not AreaManager().has(area_name):
                to_deleted.append(area_name)

        for name in to_deleted:
            self.results.pop(name)

    def closeEvent(self, event):
        QMessageBox.warning(self, "注意", "点击关闭按钮会使应用最小化到托盘。")
        event.ignore()
        self.hide()

    def show_window(self):
        self.show()

    def quit_app(self):
        QApplication.quit()

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show_window()