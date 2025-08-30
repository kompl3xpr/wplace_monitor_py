from PyQt6.QtWidgets import *
from src.gui.area_detail_dialog import AreaDetailDialog
from src.core.utils import format_relative_time
from src.core import AreaManager


class AreaInfoListItemWidget(QFrame):
    def __init__(self, app, area_name: str, result: dict):
        super().__init__()
        self.area_name = area_name
        self.result = result
        self.init_ui()
        self.updater = app.update_list_with_new_results

    def setup_info_label(self):
        area = AreaManager().area(self.area_name)
        common_info = f'上次检查: {format_relative_time(area["last_check_date"]) if "last_check_date" in area else '无'}'
        if self.result is not None:
            self.info_label.setText(f"{common_info} | 异常像素: {len(self.result['diffs'])}")
            if self.result['diffs']:
                self.area_label.setStyleSheet("color: red;")
                self.info_label.setStyleSheet("color: red;")
        else:
            self.info_label.setText(f"{common_info} | 等待检查")

    def init_ui(self):
        layout = QVBoxLayout()
        self.area_label = QLabel(f"区域: {self.area_name}")
        self.info_label = QLabel()
        self.setup_info_label()

        layout.addWidget(self.area_label)
        layout.addWidget(self.info_label)
        self.setStyleSheet("AreaInfoListItemWidget { margin: 5px 0px 5px 0px; border: 1px solid #888; border-radius: 4px; background: transparent; }")
        self.setLayout(layout)

        # click to open detail dialog
        self.mousePressEvent = self.open_detail_dialog

    
    def open_detail_dialog(self, event):
        def _slot(result):
            self.result = result
            self.updater({self.area_name: result})

        dialog = AreaDetailDialog(self.area_name, self.result)
        dialog.checked.connect(_slot)
        dialog.exec()
        self.updater({})