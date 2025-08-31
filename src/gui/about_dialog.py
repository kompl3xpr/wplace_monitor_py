from PyQt6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QProgressDialog
from PyQt6.QtCore import Qt
import requests
from packaging import version
from src import __version__
from src.core import logger, path_manager
import os
from src.gui.threads import GithubApiThread, UpdaterThread

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        # 设置对话框标题和固定大小
        self.setWindowTitle("关于")
        self.setFixedSize(400, 250)

        # 创建主布局
        main_layout = QVBoxLayout(self)

        # 应用程序名称和版本
        app_name_label = QLabel("Wplace Monitor")
        app_name_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        version_label = QLabel(f"当前版本: {__version__}")

        # 作者信息
        author_label = QLabel("作者: LEN612(kompl3xpr)")
        email_label = QLabel("邮箱: kompl3xpr@proton.me")
        license_label = QLabel("协议: ANCAP License")

        # 增加一些弹性空间，让内容在垂直方向上居中
        main_layout.addStretch()

        # 添加所有标签到布局中
        main_layout.addWidget(app_name_label)
        main_layout.addWidget(version_label)
        main_layout.addSpacing(15)  # 添加一些垂直间隔
        main_layout.addWidget(author_label)
        main_layout.addWidget(email_label)
        main_layout.addWidget(license_label)

        # 增加更多弹性空间
        main_layout.addStretch()
        
        # 创建一个水平布局用于放置更新和关闭按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()  # 将按钮推到右侧

        # 更新按钮
        update_button = QPushButton("检查更新")
        # 连接更新按钮的点击事件到槽函数
        update_button.clicked.connect(lambda: self.check_for_updates(False))
        
        # 关闭按钮
        close_button = QPushButton("关闭")
        # 连接关闭按钮的点击事件到 accept 槽，该槽会关闭对话框
        close_button.clicked.connect(self.accept)

        button_layout.addWidget(update_button)
        button_layout.addWidget(close_button)
        
        # 将按钮布局添加到主布局的底部
        main_layout.addLayout(button_layout)

    def check_for_updates(self, hide_other_msg=True):
        self.api_thread = GithubApiThread()
        self.api_thread.finished.connect(lambda r: self.handle_github_api_response(hide_other_msg, r))
        self.api_thread.start()

    def handle_github_api_response(self, hide_other_msg, resp_or_exception: dict):
        try:
            resp = None
            if "resp" in resp_or_exception:
                resp = resp_or_exception["resp"]
            else:
                raise resp_or_exception["exception"]

            # 如果请求成功
            if resp.status_code == 200:
                data = resp.json()
                    
                # 获取最新版本号，通常是 'tag_name'
                latest_version_str = data.get('tag_name')
                
                # 使用 packaging.version 库进行版本比较，更健壮
                current_version = version.parse(__version__)
                latest_version = version.parse(latest_version_str)
                    
                if latest_version > current_version:
                    # 有新版本可用
                    reply = QMessageBox.information(
                        self,
                        "发现新版本",
                        f"有新版本 {latest_version} 可用！\n是否安装？",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                        
                    if reply == QMessageBox.StandardButton.Yes:
                        self.exec_updater()
                elif not hide_other_msg:
                    # 已经是最新版本
                    QMessageBox.information(
                        self,
                        "版本信息",
                        f"您正在使用最新版本 {__version__}。",
                        QMessageBox.StandardButton.Ok
                    )
            elif not hide_other_msg:
                # API 请求失败，返回非 200 状态码
                QMessageBox.warning(
                    self,
                    "检查更新失败",
                    "无法连接到更新服务器，请稍后重试。",
                    QMessageBox.StandardButton.Ok
                )
                
        except requests.exceptions.Timeout:
            if not hide_other_msg:
                # 请求超时
                QMessageBox.warning(
                    self,
                    "检查更新失败",
                    "网络请求超时，请检查您的网络连接。",
                    QMessageBox.StandardButton.Ok
                )
        except requests.exceptions.RequestException as e:
            if not hide_other_msg:
                # 其他请求错误（如网络连接问题）
                QMessageBox.warning(
                    self,
                    "检查更新失败",
                    f"发生网络错误：{e}",
                    QMessageBox.StandardButton.Ok
                )
        except Exception as e:
            if not hide_other_msg:
                # 其他未知错误
                QMessageBox.warning(
                    self,
                    "检查更新失败",
                    f"发生未知错误：{e}",
                    QMessageBox.StandardButton.Ok
                )


    def exec_updater(self):
        logger.info("正在执行安装程序...")
        self.updater_thread = UpdaterThread()
        self.updater_thread.finished.connect(self._exec_updater)
        self.updater_thread.start()

        self.progress = QProgressDialog( "正在更新程序，请稍等...", None, 0, 0, self)
        self.progress.setWindowFlags(
            self.progress.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint
        )
        self.progress.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress.setWindowTitle("更新中")
        self.progress.setCancelButton(None)
        self.progress.show()
        

    def _exec_updater(self, exception_or_none: dict):
        temp_dir = path_manager.get('updater_temp')

        try:
            if 'exception' in exception_or_none:
                raise exception_or_none['exception']

            # 创建更新批处理脚本
            self.progress.close()
            self.create_update_script(temp_dir)
            self.parent().quit_app()  # 假设你的主窗口有一个 quit_app 方法
            
        except requests.exceptions.RequestException as e:
            logger.error(f"下载更新文件失败: {e}")
            QMessageBox.critical(self, "更新失败", f"下载更新文件失败。\n错误信息: {e}")
            
        except Exception as e:
            logger.error(f"更新过程中发生错误: {e}")
            QMessageBox.critical(self, "更新失败", f"更新过程中发生未知错误。\n错误信息: {e}")
        finally:
            self.progress.close()

    # 修改后的 create_update_script 方法
    def create_update_script(self, temp_dir):
        current_dir = os.getcwd()
        script_path = os.path.join(current_dir, 'update.bat')

        script_content = f"""
@echo off
echo Wplace Monitor is updating...

REM waiting for quit
ping 127.0.0.1 -n 6 > nul

REM delete old files
echo Deleting old files...
rd /s /q "{current_dir}\\_internal"
del /q "{current_dir}\\*.exe"

REM copy new files
echo Copying new files...
xcopy "{temp_dir}\\wplace_monitor.exe" "{current_dir}\\" /y > nul
xcopy "{temp_dir}\\_internal" "{current_dir}\\_internal" /e /i /h /y > nul

REM clear temp files
echo clearing temp files...
rd /s /q "{temp_dir}"

echo finished update, rebooting...

REM waiting for rebooting
ping 127.0.0.1 -n 5 > nul
start "" "{current_dir}\\wplace_monitor.exe"

REM remove this script
del "{script_path}"
pause
"""
        with open(script_path, 'w') as f:
            f.write(script_content)

        # 启动批处理脚本
        os.startfile(script_path)