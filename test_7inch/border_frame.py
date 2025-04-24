from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor

class BorderFrame(QWidget):
    """Widget to draw a rounded border frame."""
    def __init__(self, parent=None, day_mode=True):
        super().__init__(parent)
        self.day_mode = day_mode
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

    def set_day_mode(self, day_mode):
        """Set day or night mode for display."""
        self.day_mode = day_mode
        self.update()

    def paintEvent(self, event):
        """Paint the rounded border frame."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        border_color = Qt.white if self.day_mode else Qt.black
        bg_color = Qt.black if self.day_mode else Qt.white
        painter.setPen(QPen(border_color, 2))
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(2, 2, self.width() - 4, self.height() - 4, 10, 10)