from PyQt6.QtWidgets import *
from PyQt6.QtGui import QAction, QPixmap
from PyQt6.QtCore import Qt, pyqtSignal
from PIL.ImageQt import ImageQt
from src.core.utils import name_of_color

from src.gui.qt_image_viewer import QtImageViewer
from src.gui.area_edit_dialog import AreaEditDialog
from src.core import area_manager, Diff
from src.gui.threads import CheckThread

class AreaDetailDialog(QDialog):
    checked = pyqtSignal(dict)

    def __init__(self, area_name: str, result: dict):
        super().__init__()
        self.area_name = area_name
        self.result = result
        self.diff_qimg = None
        self.original_qimg = None
        self.current_qimg = None

        self.process_images()
        self.init_ui()

    def process_images(self):
        if self.result is None:
            return

        base_img = self.result['current_image'].copy()
        diff_img = self.result['diff_image']
        base_img.paste(diff_img, (0, 0), diff_img)
        self.diff_qimg = QPixmap.fromImage(ImageQt(base_img))
        self.original_qimg = QPixmap.fromImage(ImageQt(self.result['original_image']))
        self.current_qimg = QPixmap.fromImage(ImageQt(self.result['current_image']))


    def reset_sidebar(self):
        self.list_widget.clear()
        if self.result is None:
            self.diff_label.setText(f"待检查")
            return
        
        msg = f"找到 {len(self.result["diffs"])} 个异常像素"
        for i, diff in enumerate(self.result["diffs"]):
            if i >= 100:
                msg += "(仅显示100个)"
                break
            x, y, orig, curr = diff

            item_widget = QLabel(self.list_widget)
            item_widget.setStyleSheet('QLabel { font-size: 20px }')
            item_widget.setText(f"({x}, {y}): \n{name_of_color(orig)} -> {name_of_color(curr)}\n")
            list_item = QListWidgetItem(self.list_widget)
            list_item.setData(Qt.ItemDataRole.UserRole, diff)

            list_item.setSizeHint(item_widget.sizeHint())
            self.list_widget.addItem(list_item)
            self.list_widget.setItemWidget(list_item, item_widget)

        self.diff_label.setText(msg)

    def init_ui(self):
        self.setWindowTitle(f"区域详情: {self.area_name}")
        self.setGeometry(200, 200, 1200, 900)
        layout = QVBoxLayout()

        toolbar = QToolBar(self)

        self.check_action = QAction("检查", self)
        self.check_action.triggered.connect(self.check_area)
        toolbar.addAction(self.check_action)

        edit_action = QAction("编辑", self)
        edit_action.triggered.connect(self.open_edit_dialog)
        toolbar.addAction(edit_action)

        self.image_viewer = QtImageViewer(self)

        self.show_diff_radio = QRadioButton("显示异常", self)
        self.show_original_radio = QRadioButton("显示参考图", self)
        self.show_current_radio = QRadioButton("显示当前", self)
        self.show_diff_radio.click()
        self.radio_group = QButtonGroup(self)
        self.radio_group.addButton(self.show_diff_radio)
        self.radio_group.addButton(self.show_original_radio)
        self.radio_group.addButton(self.show_current_radio)
        toolbar.addWidget(self.show_diff_radio)
        toolbar.addWidget(self.show_original_radio)
        toolbar.addWidget(self.show_current_radio)
        self.radio_group.buttonClicked.connect(self.on_radio_button_clicked) 
        self.open_image(self.diff_qimg)

        layout.addWidget(toolbar)
        h_layout = QHBoxLayout()

        self.diff_label = QLabel(self)
        self.list_widget = QListWidget(self)
        self.list_widget.setMinimumSize(200, 200)
        self.list_widget.itemClicked.connect(self.on_diff_item_clicked)

        diff_info_sidebar = QVBoxLayout()
        diff_info_sidebar.addWidget(self.diff_label)
        diff_info_sidebar.addWidget(self.list_widget)
        h_layout.addLayout(diff_info_sidebar)
        self.reset_sidebar()

        h_layout.addWidget(self.image_viewer)
        layout.addLayout(h_layout)
        self.setLayout(layout)

    def open_image(self, qimg):
        if self.result is not None:
            self.image_viewer.clearImage()
            self.image_viewer.setImage(qimg)

    def open_edit_dialog(self):
        dialog = AreaEditDialog(self, area_manager.area(self.area_name), self.result)
        dialog.exec()

    def on_area_name_changed(self, name):
        self.area_name = name
        self.setWindowTitle(f"区域详情: {self.area_name}")

    def check_area(self):
        self.thread = CheckThread([area_manager.area(self.area_name)])
        self.thread.finished.connect(self.on_check_thread_finished)

        self.check_action.setEnabled(False)
        self.thread.start()
        self.progress = QProgressDialog( "正在检查中，请稍等...", None, 0, 0, self)
        self.progress.setWindowFlags(
            self.progress.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint
        )
        self.progress.setWindowModality(Qt.WindowModality.WindowModal)
        
        self.progress.setWindowTitle("检查中")
        self.progress.setCancelButton(None)
        self.progress.show()

    def on_check_thread_finished(self, results):
        if self.area_name in results:
            self.result = results[self.area_name]
            self.process_images()
            self.open_image(self.diff_qimg)
            self.reset_sidebar()
            self.checked.emit(self.result)
        else:
            QMessageBox.warning(self, "检查失败", "网络异常或该区域被设置为无视")
            
        self.progress.close()
        self.check_action.setEnabled(True)


    def on_diff_item_clicked(self, item: QListWidgetItem):
        diff: Diff = item.data(Qt.ItemDataRole.UserRole)
        if diff:
            self.image_viewer.move(diff.x, diff.y)

    def on_radio_button_clicked(self, button):
        if button == self.show_diff_radio:
            self.open_image(self.diff_qimg)
        elif button == self.show_original_radio:
            self.open_image(self.original_qimg)
        elif button == self.show_current_radio:
            self.open_image(self.current_qimg)