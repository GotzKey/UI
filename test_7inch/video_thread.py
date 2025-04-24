import cv2
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage

class VideoThread(QThread):
    """Thread to capture and process video frames from a camera."""
    frame_updated = pyqtSignal(QPixmap)
    error_occurred = pyqtSignal(str)

    def __init__(self, video_source=0):
        super().__init__()
        self.cap = cv2.VideoCapture(video_source)
        self.running = True

    def run(self):
        """Capture video frames and emit them as QPixmap."""
        while self.running:
            if not self.cap or not self.cap.isOpened():
                self.error_occurred.emit("Camera disconnected")
                self.frame_updated.emit(QPixmap())
                break
            ret, frame = self.cap.read()
            if not ret or frame is None:
                self.error_occurred.emit("Failed to read frame")
                self.frame_updated.emit(QPixmap())
                continue
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            image = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(image)
            self.frame_updated.emit(pixmap)
            self.msleep(30) # điều chỉnh frame

    def stop(self):
        """Stop the video thread and release the camera."""
        self.running = False
        if self.cap:
            self.cap.release()