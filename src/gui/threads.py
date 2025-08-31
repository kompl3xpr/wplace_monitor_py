from PyQt6.QtCore import QThread, pyqtSignal
from src.core import monitor_all, app_path, logger
import asyncio
import requests
import os
import zipfile

class CheckThread(QThread):
    finished = pyqtSignal(dict)

    def __init__(self, areas):
        super().__init__()
        self._areas = areas

    def run(self):
        results = asyncio.run(monitor_all(self._areas))
        self.finished.emit(results)


class GithubApiThread(QThread):
    finished = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

    def run(self):
        api_url = 'https://api.github.com/repos/kompl3xpr/wplace_monitor_py/releases/latest'
        try:
            response = requests.get(api_url, timeout=10)
            self.finished.emit({"resp": response})
        except Exception as e:
            self.finished.emit({"exception" : e})

class UpdaterThread(QThread):
    finished = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

    def run(self):
        # 定义下载 URL
        url = 'https://github.com/kompl3xpr/wplace_monitor_py/releases/latest/download/wplace_monitor_gui_windows_x64.zip'
        
        # 定义临时下载路径
        temp_dir = app_path().get('updater_temp')
        zip_path = os.path.join(temp_dir, 'wplace_monitor_gui_windows_x64.zip')

        try:
            # 确保临时目录存在
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)

            # 下载压缩包
            logger().info(f"正在下载更新文件...")
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()  # 检查 HTTP 错误
            
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            logger().info("下载完成。")

            # 解压压缩包
            logger().info("正在解压更新文件...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            logger().info("解压完成。")

            self.finished.emit({})

        except Exception as e:
            self.finished.emit({'exception': e})