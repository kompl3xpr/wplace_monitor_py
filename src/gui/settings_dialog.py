from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from src.core import settings

class SettingsDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("设置")
        self.setGeometry(150, 150, 500, 200) # 调整窗口大小以容纳更多控件
        
        main_layout = QVBoxLayout()

        # check_interval_ms
        check_layout = QHBoxLayout()
        check_label = QLabel("总刷新间隔 (毫秒):")
        self.check_interval_edit = QLineEdit()
        self.check_interval_edit.setPlaceholderText("例如: 300000")
        check_layout.addWidget(check_label)
        check_layout.addWidget(self.check_interval_edit)
        
        # wait_for_next_area_ms
        wait_layout = QHBoxLayout()
        wait_label = QLabel("网络请求间隔 (毫秒, 过小会 ban IP):")
        self.wait_for_next_area_edit = QLineEdit()
        self.wait_for_next_area_edit.setPlaceholderText("例如: 5000")
        wait_layout.addWidget(wait_label)
        wait_layout.addWidget(self.wait_for_next_area_edit)

        # check_area_when_boot
        self.check_on_boot_checkbox = QCheckBox("启动时立即检查")
        self.auto_check_enabled_checkbox = QCheckBox("默认开启自动检查")

        notification_volume = QHBoxLayout()
        notification_volume_label = QLabel("通知音量:")
        self.notification_volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.notification_volume_slider.setMinimum(0)
        self.notification_volume_slider.setMaximum(100)
        self.notification_volume_slider.valueChanged.connect(self.set_notification_volume)
        self.notification_volume_value_label = QLabel("100%")

        notification_volume.addWidget(notification_volume_label)
        notification_volume.addWidget(self.notification_volume_slider)
        notification_volume.addWidget(self.notification_volume_value_label)

        # 保存和取消按钮
        button_layout = QHBoxLayout()
        save_button = QPushButton("保存")
        cancel_button = QPushButton("取消")
        save_button.clicked.connect(self.save)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)

        # 加载初始值
        self.check_interval_edit.setText(str(settings.check_interval_ms))
        self.wait_for_next_area_edit.setText(str(settings.wait_for_next_area_ms))
        self.check_on_boot_checkbox.setChecked(settings.check_area_when_boot)
        self.auto_check_enabled_checkbox.setChecked(settings.auto_check_enabled)
        self.notification_volume_slider.setValue(settings.notification_volume)

        main_layout.addLayout(check_layout)
        main_layout.addLayout(wait_layout)
        main_layout.addLayout(notification_volume)
        main_layout.addWidget(self.check_on_boot_checkbox)
        main_layout.addWidget(self.auto_check_enabled_checkbox)
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)

    def save(self):
        reply = QMessageBox.question(
            self,
            '确认保存',
            '您确定要保存所有设置吗（部分设置需要重启程序才能应用）？',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # 从UI控件中获取值并保存
            try:
                settings.check_interval_ms = int(self.check_interval_edit.text())
                settings.wait_for_next_area_ms = int(self.wait_for_next_area_edit.text())
                settings.check_area_when_boot = self.check_on_boot_checkbox.isChecked()
                settings.auto_check_enabled = self.auto_check_enabled_checkbox.isChecked()
                settings.notification_volume = self.notification_volume_slider.value()

                settings.save()
                self.accept()
            except ValueError:
                QMessageBox.warning(self, "输入错误", "请输入有效的数字！")

    def set_notification_volume(self, value):
        self.notification_volume_value_label.setText(f"{value}%")