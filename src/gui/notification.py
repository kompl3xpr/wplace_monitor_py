import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QUrl
from PyQt6.QtGui import QFont, QColor, QGuiApplication
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from src.core import path_manager, Settings

class NotificationWindow(QWidget):
    def __init__(self, title, message):
        super().__init__()

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                            Qt.WindowType.Tool | 
                            Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        layout = QVBoxLayout(self)
        
        title_label = QLabel(f"<b>{title}</b>")
        layout.addWidget(title_label)
        
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        layout.addWidget(message_label)

        self.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 200);
                border-radius: 10px;
                padding: 10px;
                color: black;
            }
        """)

        self.adjustSize()
        self.move_to_bottom_right()
        
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        self.fade_out_timer = QTimer(self)
        self.fade_out_timer.setSingleShot(True)
        self.fade_out_timer.timeout.connect(self.start_fade_out)
        
        self.show()
        self.fade_in()

    def move_to_bottom_right(self):
        """
        计算并设置窗口在屏幕右下角的位置。
        """
        # 获取主屏幕的几何信息
        screen_geo = QGuiApplication.primaryScreen().availableGeometry()
        screen_width = screen_geo.width()
        screen_height = screen_geo.height()
        
        # 获取窗口自身的尺寸
        window_width = self.width()
        window_height = self.height()
        
        # 计算新位置（留出一些边距，比如10像素）
        new_x = screen_width - window_width - 10
        new_y = screen_height - window_height - 10
        
        # 移动窗口
        self.move(new_x, new_y)

    def fade_in(self):
        self.setWindowOpacity(0.0)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.start()
        self.animation.finished.connect(lambda: self.fade_out_timer.start(5000)) # 5秒后开始渐出
        
    def start_fade_out(self):
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.start()
        self.animation.finished.connect(self.close)

    # def mousePressEvent(self, event):
    #     self.close()

def show_notification(title, message):
    global notification_win
    notification_win = NotificationWindow(title, message)
    play_notification_sound()

player_ref = None
audio_output_ref = None

def play_notification_sound():
    global player_ref, audio_output_ref
    player_ref = QMediaPlayer()
    audio_output_ref = QAudioOutput()
    player_ref.setAudioOutput(audio_output_ref)
    player_ref.setSource(QUrl.fromLocalFile(path_manager.get('assets/notification.mp3')))
    audio_output_ref.setVolume(Settings().notification_volume / 100)
    player_ref.play()