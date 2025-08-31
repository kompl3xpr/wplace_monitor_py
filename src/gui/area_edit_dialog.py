from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from src.core import area_manager
from src.gui.mask_editor import MaskEditor

class AreaEditDialog(QDialog):
    def __init__(self, parent, area: dict, result: dict):
        super().__init__(parent)
        self.result = result
        self.area = area
        self.init_ui()
        self.new_original = None
        self.new_mask = None

    def init_ui(self):
        self.setWindowTitle(f"编辑区域: {self.area['name']}")
        self.setGeometry(150, 150, 150, 300)
        layout = QVBoxLayout()

        self.name_label = QLabel("区域名称:")
        self.name_input = QLineEdit(self.area['name'])
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)

        self.position_label = QLabel("位置 (x, y):")
        self.position_x_input = QSpinBox(self)
        self.position_x_input.setRange(0, 10000)
        self.position_x_input.setValue(self.area['position']['x'])
        self.position_y_input = QSpinBox(self)
        self.position_y_input.setRange(0, 10000)
        self.position_y_input.setValue(self.area['position']['y'])
        pos_layout = QHBoxLayout()
        pos_layout.addWidget(self.position_x_input)
        pos_layout.addWidget(QLabel(","))
        pos_layout.addWidget(self.position_y_input)
        layout.addWidget(self.position_label)
        layout.addLayout(pos_layout)

        self.ignored_checkbox = QCheckBox("忽略对该区域的检查")
        self.ignored_checkbox.setChecked(self.area['ignored'])

        layout.addWidget(self.ignored_checkbox)

        self.set_original_from_current_button = QPushButton("把当前状态设置为参考图")
        self.set_original_from_current_button.clicked.connect(self.set_original_from_current)
        layout.addWidget(self.set_original_from_current_button)

        self.import_original_button = QPushButton("导入参考图")
        self.import_original_button.clicked.connect(self.import_original_image)
        layout.addWidget(self.import_original_button)

        self.edit_mask_button = QPushButton("编辑遮罩")
        self.edit_mask_button.clicked.connect(self.edit_mask)
        layout.addWidget(self.edit_mask_button)

        self.import_mask_button = QPushButton("导入遮罩")
        self.import_mask_button.clicked.connect(self.import_mask)
        layout.addWidget(self.import_mask_button)

        self.remove_area_button = QPushButton("删除区域")
        self.remove_area_button.clicked.connect(self.remove_area)
        layout.addWidget(self.remove_area_button)

        #save button
        self.save_button = QPushButton("保存")
        self.save_button.clicked.connect(self.save_area)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def edit_mask(self):
        editor = MaskEditor(self, self.area['name'])
        editor.setWindowModality(Qt.WindowModality.WindowModal)
        editor.show()

    def import_mask(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "选择遮罩图片", "", "图片文件 (*.png)")
        if file_path:
            self.new_mask = file_path

    def import_original_image(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "选择参考图", "", "图片文件 (*.png)")
        if file_path:
            self.new_original = file_path

    def set_original_from_current(self):
        if self.result is None:
            QMessageBox.warning(self, "无法获取当前图片", "请先检查一遍，以获取当前图片。")
            return

        self.new_original = self.result['current_image']

    def remove_area(self):
        reply = QMessageBox.question(
                self,
                '确认删除',
                '您确定要删除这个区域吗？该操作不可撤销。',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
        if reply == QMessageBox.StandardButton.Yes:
            area_manager().remove(self.area['name'])
            self.accept()
            detail_dialog: QWidget = self.parent()
            detail_dialog.close()

    def save_area(self):
        reply = QMessageBox.question(
            self,
            '确认保存',
            '您确定要保存该区域所有配置吗？该操作不可撤销。',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            mng = area_manager()
            old_name = self.area['name']
            new_name = self.name_input.text()

            mng.set_ignored(self.area, self.ignored_checkbox.isChecked())
            mng.set_position(self.area, self.position_x_input.value(), self.position_y_input.value())
            mng.update_mask(old_name, self.new_mask)
            mng.update_original(old_name, self.new_original)
            if old_name != new_name:
                mng.rename_area(self.area, new_name)
                self.parent().on_area_name_changed(new_name)

            mng.save()
            self.accept()