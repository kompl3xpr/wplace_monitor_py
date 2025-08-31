from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from src.core import settings

class SettingsDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.init_ui()

    def add_group_label(self, layout, text):
        label = QLabel(f"【{text}】")
        label.setStyleSheet('QLabel { font-size: 25px; font-weight: bold;}')
        layout.addWidget(label)

    def add_group_end(self, layout):
        line = QFrame(self)
        line.setFrameShape(QFrame.Shape.HLine)
        line.setLineWidth(2)
        layout.addWidget(line)

    def init_ui(self):
        self.setWindowTitle("设置")
        self.setBaseSize(100, 100)

        main_layout = QVBoxLayout()
        self.add_application_options(main_layout)
        self.add_checker_options(main_layout)
        self.add_notification_options(main_layout)
        self.add_buttons(main_layout)
        self.setLayout(main_layout)


    def add_application_options(self, layout):
        self.add_group_label(layout, "应用")

        self.auto_check_for_updates_checkbox = QCheckBox("启动时自动检查版本更新")
        self.auto_check_for_updates_checkbox.setChecked(settings().application.auto_check_for_updates)
        layout.addWidget(self.auto_check_for_updates_checkbox)

        self.add_group_end(layout)


    def add_checker_options(self, layout):
        self.add_group_label(layout, "检查")

        check_layout = QHBoxLayout()
        check_label1 = QLabel("每隔")
        self.check_interval_spinbox = QSpinBox()
        self.check_interval_spinbox.setRange(60000, 86400000)
        check_label2 = QLabel("毫秒自动检查所有区域")
        check_layout.addWidget(check_label1)
        check_layout.addWidget(self.check_interval_spinbox)
        check_layout.addWidget(check_label2)
        self.check_interval_spinbox.setValue(settings().checker.interval_ms)
        layout.addLayout(check_layout)
        
        wait_layout = QHBoxLayout()
        wait_label1 = QLabel("每隔")
        self.wait_for_next_area_spinbox = QSpinBox()
        self.wait_for_next_area_spinbox.setRange(3000, 60000)
        wait_label2 = QLabel("毫秒进行一次网络请求")
        wait_layout.addWidget(wait_label1)
        wait_layout.addWidget(self.wait_for_next_area_spinbox)
        wait_layout.addWidget(wait_label2)
        self.wait_for_next_area_spinbox.setValue(settings().checker.wait_req_ms)
        layout.addLayout(wait_layout)

        self.check_on_boot_checkbox = QCheckBox("启动时立即检查")
        self.check_on_boot_checkbox.setChecked(settings().checker.at_startup)
        layout.addWidget(self.check_on_boot_checkbox)

        self.auto_check_enabled_checkbox = QCheckBox("默认开启自动检查")
        self.auto_check_enabled_checkbox.setChecked(settings().checker.auto)
        layout.addWidget(self.auto_check_enabled_checkbox)

        self.add_group_end(layout)


    def add_notification_options(self, layout):
        self.add_group_label(layout, "通知")

        notification_volume = QHBoxLayout()
        notification_volume_label = QLabel("通知音量:")
        self.notification_volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.notification_volume_slider.setMinimum(0)
        self.notification_volume_slider.setMaximum(100)
        self.notification_volume_slider.valueChanged.connect(
            lambda v: self.notification_volume_value_label.setText(f"{v}%")
        )
        self.notification_volume_value_label = QLabel("100%")

        notification_volume.addWidget(notification_volume_label)
        notification_volume.addWidget(self.notification_volume_slider)
        notification_volume.addWidget(self.notification_volume_value_label)
        self.notification_volume_slider.setValue(settings().notification.volume)


        notiwin_duration = QHBoxLayout()
        notiwin_duration_label1 = QLabel("通知弹窗消失时间:")
        self.notiwin_duration_spinbox = QSpinBox(self)
        self.notiwin_duration_spinbox.setRange(0, 86400000)
        self.notiwin_duration_spinbox.setValue(settings().notification.window_duration_ms)
        notiwin_duration_label2 = QLabel("毫秒")
        notiwin_duration.addWidget(notiwin_duration_label1)
        notiwin_duration.addWidget(self.notiwin_duration_spinbox)
        notiwin_duration.addWidget(notiwin_duration_label2)

        layout.addLayout(notification_volume)
        layout.addLayout(notiwin_duration)

        self.add_group_end(layout)


    def add_buttons(self, layout):
        button_layout = QHBoxLayout()
        save_button = QPushButton("保存")
        cancel_button = QPushButton("取消")
        save_button.clicked.connect(self.save)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)


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
                settings().application.auto_check_for_updates = self.auto_check_for_updates_checkbox.isChecked()

                settings().checker.interval_ms = self.check_interval_spinbox.value()
                settings().checker.wait_req_ms = self.wait_for_next_area_spinbox.value()
                settings().checker.at_startup = self.check_on_boot_checkbox.isChecked()
                settings().checker.auto = self.auto_check_enabled_checkbox.isChecked()

                settings().notification.volume = self.notification_volume_slider.value()
                settings().notification.window_duration_ms = self.notiwin_duration_spinbox.value()

                settings().save()
                self.accept()
            except ValueError:
                QMessageBox.warning(self, "输入错误", "请输入有效的数字！")