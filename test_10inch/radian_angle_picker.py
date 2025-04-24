import math
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont

class RadianAnglePicker(QWidget):
    """Lớp hiển thị đồng hồ góc tầm (0-90 độ)."""
    def __init__(self, parent=None, day_mode=True):
        super().__init__(parent)
        self.setMinimumSize(124, 124)  # Kích thước tối thiểu
        self.indicator_angle = 45      # Góc ban đầu
        self.day_mode = day_mode       # Chế độ ngày/đêm

    def set_day_mode(self, day_mode):
        """Cập nhật chế độ ngày/đêm."""
        self.day_mode = day_mode
        self.update()

    def set_angle(self, angle):
        """Cập nhật góc tầm (0-90 độ)."""
        try:
            self.indicator_angle = max(0, min(90, float(angle)))
            self.update()
        except (ValueError, TypeError):
            print(f"Góc không hợp lệ cho RadianAnglePicker: {angle}")

    def paintEvent(self, event):
        """Vẽ đồng hồ góc tầm với cung 90 độ và kim chỉ báo."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        try:
            width, height = self.width(), self.height()
            margin = 2
            radius = min(width, height) - margin * 2
            center_x = width - margin - radius
            center_y = height - margin

            border_color = Qt.white if self.day_mode else Qt.black
            bg_color = Qt.black if self.day_mode else Qt.white
            indicator_color = Qt.red

            # Vẽ khung và nền
            painter.setPen(QPen(border_color, 2))
            painter.drawRect(0, 0, width - 1, height - 1)
            painter.setBrush(QBrush(bg_color))
            painter.drawArc(QRectF(center_x - radius, center_y - radius, 
                                 radius * 2, radius * 2), 0 * 16, 90 * 16)

            # Vẽ trục
            painter.setPen(QPen(border_color, 2))
            painter.drawLine(center_x, center_y, center_x + radius, center_y)
            painter.drawLine(center_x, center_y, center_x, center_y - radius)

            # Vẽ mốc góc
            mark_length = radius // 6
            painter.setFont(QFont('Arial', min(10, radius // 8)))
            for angle in range(0, 91, 15):
                rad_angle = math.radians(angle)
                outer_x = center_x + radius * math.cos(rad_angle)
                outer_y = center_y - radius * math.sin(rad_angle)
                inner_x = center_x + (radius - mark_length) * math.cos(rad_angle)
                inner_y = center_y - (radius - mark_length) * math.sin(rad_angle)
                painter.setPen(QPen(border_color, 1))
                painter.drawLine(int(outer_x), int(outer_y), int(inner_x), int(inner_y))

            # Vẽ kim chỉ báo
            rad_angle = math.radians(self.indicator_angle)
            pointer_x = center_x + radius * 0.8 * math.cos(rad_angle)
            pointer_y = center_y - radius * 0.8 * math.sin(rad_angle)
            painter.setPen(QPen(indicator_color, 2))
            painter.drawLine(center_x, center_y, int(pointer_x), int(pointer_y))
        except Exception as e:
            print(f"Lỗi trong paintEvent của RadianAnglePicker: {str(e)}")