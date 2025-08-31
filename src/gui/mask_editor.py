import sys
from PyQt6.QtWidgets import (QButtonGroup, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QRadioButton, 
                             QSlider, QLabel, QMessageBox, QSizePolicy, QScrollArea)
from PyQt6.QtGui import QPixmap, QImage, QPainter, QColor, QPen, QPalette
from PyQt6.QtCore import Qt, QPoint

# 假设 area_manager 和 app_path 已经存在并正确导入
from src.core import app_path

class MaskEditor(QMainWindow):
    def __init__(self, parent, area_name: str):
        super().__init__(parent)
        self.setWindowTitle("Mask Editor")
        self.setGeometry(100, 100, 1200, 800)

        self.image_size = (1000, 1000)
        self.current_image = QImage(self.image_size[0], self.image_size[1], QImage.Format.Format_ARGB32_Premultiplied)
        self.current_image.fill(Qt.GlobalColor.white) # Initialize with a white background

        self.brush_size = 1
        self.tool_mode = "brush"
        self.brush_color = Qt.GlobalColor.black
        self.last_point = QPoint()

        self.background_image = None  # Add a new attribute for the background image
        self.editor_opacity = 0.8
        
        # New attributes for scaling
        self.scale_factor = 1.0
        self.min_scale = 0.1
        self.max_scale = 5.0
        self.scale_step = 0.1
        
        self.area_name = area_name
        self._setup_ui()
        self.open_background_image()
        self.open_image()
        
    def _setup_ui(self):
        """
        Setup the user interface elements.
        """
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Left panel for controls
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        control_panel.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        control_panel.setFixedWidth(200)

        # Save button
        self.save_btn = QPushButton("保存遮罩")
        self.save_btn.clicked.connect(self.save_image)

        # Tool selection group
        self.tool_group = QButtonGroup(self)
        tool_label = QLabel("工具选择:")
        self.brush_radio = QRadioButton("画笔")
        self.fill_radio = QRadioButton("油漆桶")
        self.tool_group.addButton(self.brush_radio)
        self.tool_group.addButton(self.fill_radio)
        self.brush_radio.setChecked(True)
        self.tool_group.buttonToggled.connect(self.toggle_tool)
        
        # Color selection group
        self.color_group = QButtonGroup(self)
        color_label = QLabel("画笔/填充颜色:")
        self.black_radio = QRadioButton("黑色")
        self.white_radio = QRadioButton("白色")
        self.color_group.addButton(self.black_radio)
        self.color_group.addButton(self.white_radio)
        self.black_radio.setChecked(True)
        self.color_group.buttonToggled.connect(self.set_color)

        # Brush size control
        size_label = QLabel("画笔大小:")
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setMinimum(1)
        self.size_slider.setMaximum(100)
        self.size_slider.setValue(self.brush_size)
        self.size_slider.valueChanged.connect(self.set_brush_size)
        self.size_value_label = QLabel(str(self.brush_size))
        
        # New: Scale control
        scale_label = QLabel("缩放比例:")
        self.scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.scale_slider.setMinimum(50)
        self.scale_slider.setMaximum(1000)
        self.scale_slider.setValue(100)
        self.scale_slider.valueChanged.connect(self.set_scale_factor)
        self.scale_value_label = QLabel("100%")

        control_layout.addWidget(self.save_btn)
        control_layout.addWidget(tool_label)
        control_layout.addWidget(self.brush_radio)
        control_layout.addWidget(self.fill_radio)
        control_layout.addWidget(color_label)
        control_layout.addWidget(self.black_radio)
        control_layout.addWidget(self.white_radio)
        control_layout.addWidget(size_label)
        size_layout = QHBoxLayout()
        size_layout.addWidget(self.size_slider)
        size_layout.addWidget(self.size_value_label)
        control_layout.addLayout(size_layout)
        
        # Add scale controls to layout
        control_layout.addWidget(scale_label)
        scale_layout = QHBoxLayout()
        scale_layout.addWidget(self.scale_slider)
        scale_layout.addWidget(self.scale_value_label)
        control_layout.addLayout(scale_layout)
        
        control_layout.addStretch()

        # Canvas for drawing
        self.canvas_label = QLabel()
        self.canvas_label.setScaledContents(False)
        self.canvas_label.mousePressEvent = self.mouse_press
        self.canvas_label.mouseMoveEvent = self.mouse_move
        self.canvas_label.mouseReleaseEvent = self.mouse_release

        # Wrap the canvas in a QScrollArea
        self.scroll_area = QScrollArea()
        self.scroll_area.setBackgroundRole(QPalette.ColorRole.Dark)
        self.scroll_area.setWidget(self.canvas_label)
        self.scroll_area.setWidgetResizable(False) # Important: we manage scaling manually
        
        self.update_canvas()

        main_layout.addWidget(control_panel)
        main_layout.addWidget(self.scroll_area) # Add scroll area to main layout
    
    def update_canvas(self):
        """
        Draws the background and the translucent foreground, then scales and updates the canvas label.
        """
        # Create a blank image to draw on
        display_image = QImage(self.image_size[0], self.image_size[1], QImage.Format.Format_ARGB32)
        painter = QPainter(display_image)

        # 1. Draw the background image
        if self.background_image and not self.background_image.isNull():
            painter.setOpacity(1.0)
            painter.drawImage(0, 0, self.background_image)
        else:
            painter.fillRect(display_image.rect(), QColor(Qt.GlobalColor.white))

        # 2. Draw the editable foreground image with transparency
        painter.setOpacity(self.editor_opacity)
        painter.drawImage(0, 0, self.current_image)
        
        painter.end()

        # Scale the combined image for display
        pixmap = QPixmap.fromImage(display_image)
        scaled_pixmap = pixmap.scaled(
            int(self.image_size[0] * self.scale_factor),
            int(self.image_size[1] * self.scale_factor),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.FastTransformation
        )
        
        # Update canvas label size and pixmap
        self.canvas_label.setFixedSize(scaled_pixmap.size())
        self.canvas_label.setPixmap(scaled_pixmap)

    def set_scale_factor(self, value):
        """
        Set the scale factor based on the slider value and zoom to the center.
        """
        # Save the old scale factor to calculate the ratio
        old_scale_factor = self.scale_factor

        self.scale_factor = value / 100.0
        self.scale_value_label.setText(f"{value}%")

        # Get the current scroll bar positions
        old_h_scroll = self.scroll_area.horizontalScrollBar().value()
        old_v_scroll = self.scroll_area.verticalScrollBar().value()
        
        # Get the current scroll area viewport size
        viewport_width = self.scroll_area.viewport().width()
        viewport_height = self.scroll_area.viewport().height()

        # Calculate the center point in the old image coordinates
        old_center_x = (old_h_scroll + viewport_width / 2) / old_scale_factor
        old_center_y = (old_v_scroll + viewport_height / 2) / old_scale_factor

        # Update the canvas to reflect the new scale factor
        self.update_canvas()

        # Calculate the new scroll bar positions to keep the center point
        new_h_scroll = old_center_x * self.scale_factor - viewport_width / 2
        new_v_scroll = old_center_y * self.scale_factor - viewport_height / 2

        # Set the new scroll bar positions
        self.scroll_area.horizontalScrollBar().setValue(int(new_h_scroll))
        self.scroll_area.verticalScrollBar().setValue(int(new_v_scroll))

    def open_background_image(self):
        file_name = app_path().get_original_image(self.area_name)
        image = QImage(file_name)
        self.background_image = image.convertToFormat(QImage.Format.Format_ARGB32)
        self.update_canvas()

    def open_image(self):
        file_name = app_path().get_mask_image(self.area_name)
        image = QImage(file_name)   
        self.current_image = image.convertToFormat(QImage.Format.Format_ARGB32_Premultiplied)
        self.update_canvas()

    def save_image(self):
        file_name = app_path().get_mask_image(self.area_name)
        self.current_image.save(file_name)
        QMessageBox.information(self, "修改成功", "遮罩图片已保存。")

    def toggle_tool(self):
        if self.brush_radio.isChecked():
            self.tool_mode = "brush"
            self.size_slider.setEnabled(True)
            self.size_value_label.setEnabled(True)
        elif self.fill_radio.isChecked():
            self.tool_mode = "fill"
            self.size_slider.setEnabled(False)
            self.size_value_label.setEnabled(False)

    def set_color(self):
        if self.black_radio.isChecked():
            self.brush_color = Qt.GlobalColor.black
        elif self.white_radio.isChecked():
            self.brush_color = Qt.GlobalColor.white

    def set_brush_size(self, size):
        self.brush_size = size
        self.size_value_label.setText(str(size))
        
    def mouse_press(self, event):
        """
        Handle mouse press event on the scaled image.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            # Convert mouse position from scaled coordinates to original image coordinates
            pos_on_image = QPoint(
                int(event.pos().x() / self.scale_factor),
                int(event.pos().y() / self.scale_factor)
            )
            
            if self.tool_mode == "brush":
                self.last_point = pos_on_image
                self.draw_point(pos_on_image)
            elif self.tool_mode == "fill":
                self.fill_area(pos_on_image)

    def mouse_move(self, event):
        """
        Handle mouse move events for drawing on the scaled image.
        """
        if event.buttons() & Qt.MouseButton.LeftButton and self.tool_mode == "brush":
            pos_on_image = QPoint(
                int(event.pos().x() / self.scale_factor),
                int(event.pos().y() / self.scale_factor)
            )
            self.draw_line(self.last_point, pos_on_image)
            self.last_point = pos_on_image

    def mouse_release(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.last_point = QPoint()

    def draw_point(self, pos):
        """
        Draw a single point on the original image.
        """
        painter = QPainter(self.current_image)
        pen = QPen(self.brush_color, self.brush_size, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.MiterJoin)
        painter.setPen(pen)
        painter.drawPoint(pos)
        self.update_canvas()

    def draw_line(self, start_pos, end_pos):
        """
        Draw a non-antialiased line on the original image.
        """
        painter = QPainter(self.current_image)
        pen = QPen(self.brush_color, self.brush_size, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.MiterJoin)
        painter.setPen(pen)
        painter.drawLine(start_pos, end_pos)
        self.update_canvas()

    def fill_area(self, pos):
        """
        Flood fill an area with the selected color on the original image.
        """
        if not self.current_image.rect().contains(pos):
            return

        target_color = self.current_image.pixelColor(pos)
        fill_color = QColor(self.brush_color)

        if target_color == fill_color:
            return

        w, h = self.image_size
        stack = [(pos.x(), pos.y())]
        
        temp_image = self.current_image
        
        while stack:
            x, y = stack.pop()
            
            if not (0 <= x < w and 0 <= y < h):
                continue

            if temp_image.pixelColor(x, y) == target_color:
                temp_image.setPixelColor(x, y, fill_color)
                stack.append((x + 1, y))
                stack.append((x - 1, y))
                stack.append((x, y + 1))
                stack.append((x, y - 1))
        
        self.current_image = temp_image
        self.update_canvas()