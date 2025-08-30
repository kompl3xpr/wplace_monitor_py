from PyQt6.QtWidgets import *
from PyQt6.QtGui import QRegularExpressionValidator as QRegExpValidator
from PyQt6.QtCore import QRegularExpression as QRegExp

class NewAreaDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('添加新的受保护区域')
        self.setFixedSize(500, 200)

        # 布局
        main_layout = QVBoxLayout(self)

        # 名字输入
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel('区域名称:'))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("请输入名称 (字母、数字、下划线)")
        self.name_input.setValidator(self.get_name_validator())
        name_layout.addWidget(self.name_input)
        main_layout.addLayout(name_layout)

        # 坐标输入
        coord_layout = QHBoxLayout()
        coord_layout.addWidget(QLabel('区域坐标 X:'))
        self.x_spinbox = QSpinBox()
        self.x_spinbox.setRange(0, 2047)
        coord_layout.addWidget(self.x_spinbox)
        
        coord_layout.addWidget(QLabel('Y:'))
        self.y_spinbox = QSpinBox()
        self.y_spinbox.setRange(0, 2047)
        coord_layout.addWidget(self.y_spinbox)
        main_layout.addLayout(coord_layout)

        main_layout.addWidget(QLabel('注：参考图将会被设置为当前状态。'))

        # 按钮
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

    def get_name_validator(self):
        return QRegExpValidator(QRegExp("^[a-zA-Z0-9_]+$"), self)

    def get_name(self):
        return self.name_input.text()

    def get_x(self):
        return self.x_spinbox.value()

    def get_y(self):
        return self.y_spinbox.value()