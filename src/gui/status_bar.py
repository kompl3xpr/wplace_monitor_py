from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt

remaining_table = [
    (100e2, '十秒内'),
    (300e2, '三十秒内'),
    (600e2, '一分钟内'),
    (120e3, '两分钟内'),
    (180e3, '三分钟内'),
    (300e3, '五分钟内'),
    (600e3, '十分钟内'),
    (900e3, '十五分钟内'),
    (180e4, '半小时内'),
    (360e4, '一小时内'),
    (720e4, '二小时内'),
    (144e5, '四小时内'),
    (288e5, '八小时内'),
    (-1, '超过八小时'),
]

class AppStatusBar(QStatusBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet('QLabel { font-size: 14px }')
        self.next_update_label = QLabel("下次检查: N/A")
        self.logging_info_label = QLabel("")

        self.addPermanentWidget(self.next_update_label)
        self.addWidget(self.logging_info_label)


    def set_next_update(self, remaining_msec: int):
        text = 'N/A'
        for msec, t in remaining_table:
            if remaining_msec == -2:
                text = '未启用自动检查'
                break
            if remaining_msec == -3:
                text = '正在进行'
                break
            if msec == -1 or remaining_msec < msec:
                text = t
                break

        self.next_update_label.setText(f"下次检查: {text}")

    def set_logging_info(self, text):
        self.logging_info_label.setText(f"{text}")