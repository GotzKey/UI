from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QColor, QFont, QPixmap
from video_thread import VideoThread
import cv2

class VideoWidget(QWidget):
    """Lớp hiển thị video với dấu cộng đỏ, mốc mil và khung giới hạn."""
    def __init__(self, parent=None, video_source=0, day_mode=True):
        super().__init__(parent)
        self.day_mode = day_mode         # Chế độ ngày (True) hoặc đêm (False)
        self.pixmap = None               # Frame video hiện tại
        self.bounding_box = None         # Khung giới hạn từ AI
        self.error_message = ""          # Thông báo lỗi
        # Kiểm tra camera trước khi khởi động
        cap = cv2.VideoCapture(video_source)
        if not cap.isOpened():
            self.error_message = "Camera không khả dụng"
            cap.release()
            self.video_thread = None
        else:
            cap.release()
            self.video_thread = VideoThread(video_source)
            self.video_thread.frame_updated.connect(self.set_pixmap)
            self.video_thread.error_occurred.connect(self.set_error_message)
            self.video_thread.start()

    def set_day_mode(self, day_mode):
        """Cập nhật chế độ ngày/đêm."""
        self.day_mode = day_mode
        self.update()

    def set_error_message(self, message):
        """Hiển thị thông báo lỗi khi video gặp sự cố."""
        self.error_message = message
        self.pixmap = None
        self.update()

    def set_bounding_box(self, bounding_box):
        """Cập nhật tọa độ khung giới hạn."""
        try:
            if bounding_box:
                x, y, w, h = (bounding_box["x"], bounding_box["y"], 
                             bounding_box["w"], bounding_box["h"])
                if (x >= 0 and y >= 0 and w > 0 and h > 0 and 
                    (self.pixmap is None or (x + w <= self.pixmap.width() and 
                                             y + h <= self.pixmap.height()))):
                    self.bounding_box = (x, y, w, h)
                else:
                    self.bounding_box = None
            else:
                self.bounding_box = None
            self.update()
        except Exception as e:
            print(f"Lỗi khi đặt khung giới hạn: {str(e)}")
            self.bounding_box = None
            self.update()

    def set_pixmap(self, pixmap):
        """Cập nhật frame video mới, thu phóng theo kích thước widget."""
        try:
            self.pixmap = None if pixmap.isNull() else pixmap.scaled(
                self.size(), Qt.KeepAspectRatio)
            self.error_message = ""
            self.update()
        except Exception as e:
            print(f"Lỗi khi đặt pixmap: {str(e)}")
            self.error_message = f"Lỗi pixmap: {str(e)}"
            self.update()

    def paintEvent(self, event):
        """Vẽ frame video, dấu cộng đỏ và mốc mil."""
        painter = QPainter(self)
        widget_size = self.size()

        try:
            if self.pixmap and not self.error_message:
                pixmap_rect = self.pixmap.rect()
                pixmap_rect.moveCenter(self.rect().center())
                painter.drawPixmap(pixmap_rect, self.pixmap)
            else:
                painter.fillRect(0, 0, widget_size.width(), widget_size.height(), 
                               QColor(0, 0, 0))
                if self.error_message:
                    painter.setPen(QPen(Qt.red, 2))
                    painter.setFont(QFont('Arial', 20))
                    painter.drawText(self.rect(), Qt.AlignCenter, self.error_message)

            center_x = widget_size.width() // 2
            center_y = widget_size.height() // 2
            cross_length = 30

            if self.bounding_box:
                x, y, w, h = self.bounding_box
                center_x = x + w // 2
                center_y = y + h // 2
                scale_x = widget_size.width() / self.pixmap.width() if self.pixmap else 1
                scale_y = widget_size.height() / self.pixmap.height() if self.pixmap else 1
                center_x = int(center_x * scale_x)
                center_y = int(center_y * scale_y)
                cross_length = max(15, min(45, (w + h) // 4))

            # Vẽ dấu cộng đỏ
            painter.setPen(QPen(Qt.red, 3))
            painter.drawLine(center_x - cross_length // 2, center_y, 
                           center_x + cross_length // 2, center_y)
            painter.drawLine(center_x, center_y - cross_length // 2, 
                           center_x, center_y + cross_length // 2)

            # Vẽ mốc mil
            painter.setPen(QPen(Qt.red, 1))
            painter.setFont(QFont('Arial', 8))
            width = self.width()
            fov_mil = 349
            pixel_per_mil = width / fov_mil
            major_tick_mil, minor_tick_mil = 10, 1
            label_mil = 50
            major_tick_length, minor_tick_length = 10, 5
            for mil in range(-200, 201, minor_tick_mil):
                x = int(center_x + mil * pixel_per_mil)
                if x < 0 or x > width:
                    continue
                if mil % major_tick_mil == 0:
                    painter.drawLine(x, 0, x, major_tick_length)
                    if mil % label_mil == 0:
                        painter.drawText(x - 15, major_tick_length + 15, str(mil))
                else:
                    painter.drawLine(x, 0, x, minor_tick_length)
        except Exception as e:
            print(f"Lỗi trong paintEvent: {str(e)}")

    def closeEvent(self, event):
        """Dừng luồng video khi đóng widget."""
        if self.video_thread:
            self.video_thread.stop()
        super().closeEvent(event)