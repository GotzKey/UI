import math
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont

class RadianAnglePicker(QWidget):
    """Widget to display an elevation angle indicator (0-90 degrees)."""
    def __init__(self, parent=None, day_mode=True):
        super().__init__(parent)
        self.setMinimumSize(80, 80)
        self.indicator_angle = 45
        self.day_mode = day_mode

    def set_day_mode(self, day_mode):
        """Set day or night mode for display."""
        self.day_mode = day_mode
        self.update()

    def set_angle(self, angle):
        """Set the elevation angle (0-90 degrees)."""
        self.indicator_angle = max(0, min(90, angle))
        self.update()

    def paintEvent(self, event):
        """Paint the angle picker with an arc and angle indicator."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        width = self.width()
        height = self.height()
        margin = 2
        radius = min(width, height) - margin * 2
        center_x = width - margin - radius
        center_y = height - margin

        border_color = Qt.white if self.day_mode else Qt.black
        bg_color = Qt.black if self.day_mode else Qt.white
        indicator_color = Qt.red

        # Draw border and background
        painter.setPen(QPen(border_color, 1))
        painter.drawRect(0, 0, width - 1, height - 1)
        painter.setBrush(QBrush(bg_color))
        painter.drawArc(QRectF(center_x - radius, center_y - radius, radius * 2, radius * 2), 0 * 16, 90 * 16)

        # Draw axes
        painter.setPen(QPen(border_color, 1))
        painter.drawLine(center_x, center_y, center_x + radius, center_y)
        painter.drawLine(center_x, center_y, center_x, center_y - radius)

        # Draw angle markers
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

        # Draw angle indicator
        rad_angle = math.radians(self.indicator_angle)
        pointer_x = center_x + radius * 0.8 * math.cos(rad_angle)
        pointer_y = center_y - radius * 0.8 * math.sin(rad_angle)
        painter.setPen(QPen(indicator_color, 1))
        painter.drawLine(center_x, center_y, int(pointer_x), int(pointer_y))