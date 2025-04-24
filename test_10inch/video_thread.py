import cv2
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage

class VideoThread(QThread):
    """Lớp luồng để xử lý và truyền dữ liệu video từ camera."""
    frame_updated = pyqtSignal(QPixmap)  # Tín hiệu gửi frame video mới
    error_occurred = pyqtSignal(str)    # Tín hiệu gửi thông báo lỗi

    def __init__(self, video_source=0):
        super().__init__()
        self.video_source = video_source  # Nguồn video (0: camera mặc định)
        self.cap = None                   # Đối tượng camera
        self.running = True               # Cờ kiểm soát vòng lặp

    def run(self):
        """Chụp và gửi frame video dưới dạng QPixmap."""
        try:
            self.cap = cv2.VideoCapture(self.video_source)
            if not self.cap.isOpened():
                self.error_occurred.emit("Không tìm thấy hoặc không mở được camera")
                self.frame_updated.emit(QPixmap())
                return
            while self.running:
                ret, frame = self.cap.read()
                if not ret or frame is None:
                    self.error_occurred.emit("Không đọc được frame video")
                    self.frame_updated.emit(QPixmap())
                    continue
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                image = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(image)
                self.frame_updated.emit(pixmap)
                self.msleep(30)  # Nghỉ 30ms (~33 FPS)
        except Exception as e:
            self.error_occurred.emit(f"Lỗi luồng video: {str(e)}")
            self.frame_updated.emit(QPixmap())
        finally:
            if self.cap:
                self.cap.release()
                self.cap = None

    def stop(self):
        """Dừng luồng và giải phóng camera."""
        self.running = False
        if self.cap:
            self.cap.release()
            self.cap = None