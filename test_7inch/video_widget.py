from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QColor, QFont, QPixmap
from video_thread import VideoThread

class VideoWidget(QWidget):
    """Widget to display video stream with a red crosshair and optional bounding box."""
    def __init__(self, parent=None, video_source=0, day_mode=True):
        super().__init__(parent)
        self.day_mode = day_mode
        self.pixmap = None
        self.bounding_box = None
        self.error_message = ""
        self.video_thread = VideoThread(video_source)
        self.video_thread.frame_updated.connect(self.set_pixmap)
        self.video_thread.error_occurred.connect(self.set_error_message)
        self.video_thread.start()

    def set_day_mode(self, day_mode):
        """Set day or night mode for display."""
        self.day_mode = day_mode
        self.update()

    def set_error_message(self, message):
        """Set error message to display when video fails."""
        self.error_message = message
        self.pixmap = None
        self.update()

    def set_bounding_box(self, bounding_box):
        """Set bounding box coordinates for display."""
        if bounding_box:
            self.bounding_box = (
                bounding_box["x"],
                bounding_box["y"],
                bounding_box["w"],
                bounding_box["h"]
            )
        else:
            self.bounding_box = None
        self.update()

    def set_pixmap(self, pixmap):
        """Set the pixmap to display, scaled to widget size."""
        if pixmap.isNull():
            self.pixmap = None
        else:
            self.pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatio)
        self.error_message = ""
        self.update()

    def paintEvent(self, event):
        """Paint the video frame, crosshair, and mil markers."""
        painter = QPainter(self)
        widget_size = self.size()

        try:
            if self.pixmap and not self.error_message:
                pixmap_rect = self.pixmap.rect()
                pixmap_rect.moveCenter(self.rect().center())
                painter.drawPixmap(pixmap_rect, self.pixmap)
            else:
                painter.fillRect(0, 0, widget_size.width(), widget_size.height(), QColor(0, 0, 0))
                if self.error_message:
                    painter.setPen(QPen(Qt.red, 2))
                    painter.setFont(QFont('Arial', 16))
                    painter.drawText(self.rect(), Qt.AlignCenter, self.error_message)

            center_x = widget_size.width() // 2
            center_y = widget_size.height() // 2
            cross_length = 20

            if self.bounding_box:
                x, y, w, h = self.bounding_box
                center_x = x + w // 2
                center_y = y + h // 2
                scale_x = widget_size.width() / self.pixmap.width() if self.pixmap else 1
                scale_y = widget_size.height() / self.pixmap.height() if self.pixmap else 1
                center_x = int(center_x * scale_x)
                center_y = int(center_y * scale_y)
                cross_length = max(10, min(30, (w + h) // 4))

            # Draw red crosshair
            painter.setPen(QPen(Qt.red, 3))
            painter.drawLine(center_x - cross_length // 2, center_y, center_x + cross_length // 2, center_y)
            painter.drawLine(center_x, center_y - cross_length // 2, center_x, center_y + cross_length // 2)

            # Draw mil markers
            text_color = Qt.red
            painter.setPen(QPen(text_color, 1))
            painter.setFont(QFont('Arial', 8))
            width = self.width()
            fov_mil = 349
            pixel_per_mil = width / fov_mil
            major_tick_mil = 10
            minor_tick_mil = 1
            label_mil = 50
            major_tick_length = 8
            minor_tick_length = 4
            for mil in range(-200, 201, minor_tick_mil):
                x = int(center_x + mil * pixel_per_mil)
                if x < 0 or x > width:
                    continue
                if mil % major_tick_mil == 0:
                    painter.drawLine(x, 0, x, major_tick_length)
                    if mil % label_mil == 0:
                        painter.drawText(x - 12, major_tick_length + 12, str(mil))
                else:
                    painter.drawLine(x, 0, x, minor_tick_length)

        except Exception as e:
            print(f"Error in paintEvent: {str(e)}")

    def closeEvent(self, event):
        """Stop the video thread when closing."""
        self.video_thread.stop()
        super().closeEvent(event)