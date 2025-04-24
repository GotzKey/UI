import sys
import datetime
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from testui import Ui_MainWindow
from video_widget import VideoWidget
from radian_angle_picker import RadianAnglePicker
from full_circle_angle_picker import FullCircleAnglePicker
from border_frame import BorderFrame

class MainWindow:
    """Lớp cửa sổ chính cho giao diện camera 10 inch."""
    def __init__(self):
        self.main_win = QMainWindow()
        self.uic = Ui_MainWindow()
        try:
            self.uic.setupUi(self.main_win)
        except Exception as e:
            print(f"Lỗi khi thiết lập UI: {str(e)}")
            QMessageBox.critical(None, "Lỗi UI", f"Không thể tải UI: {str(e)}")
            sys.exit(1)

        self.day_mode = self.is_day_time()
        self.video_widget = None
        self.setup_ui()
        self.setup_connections()
        self.setup_timers()
        self.initialize_values()
        self.update_colors()

    def setup_ui(self):
        """Thiết lập vị trí và widget giao diện."""
        try:
            # Thiết lập vị trí các thành phần
            self.uic.frame_video.setGeometry(10, 10, 1900, 900)
            self.uic.label_distance.setGeometry(844, 940, 101, 40)
            self.uic.label_EA.setGeometry(844, 990, 101, 40)
            self.uic.label_AA.setGeometry(844, 1040, 101, 40)
            self.uic.textEditDis.setGeometry(955, 940, 120, 40)
            self.uic.textEditEA.setGeometry(955, 990, 120, 40)
            self.uic.textEditAA.setGeometry(955, 1040, 120, 40)

            # Khởi tạo widget
            self.border_frame = BorderFrame(self.uic.centralwidget, self.day_mode)
            self.border_frame.setGeometry(824, 920, 271, 160)
            self.border_frame.lower()

            self.radian_picker = RadianAnglePicker(self.uic.centralwidget, self.day_mode)
            self.radian_picker.setGeometry(150, 930, 124, 124)
            self.label_elevation = QLabel("Góc Tầm", self.uic.centralwidget)
            self.label_elevation.setGeometry(150, 1080, 124, 40)
            self.label_elevation.setAlignment(Qt.AlignCenter)

            self.circle_picker = FullCircleAnglePicker(self.uic.centralwidget, self.day_mode)
            self.circle_picker.setGeometry(1646, 930, 124, 124)
            self.label_azimuth = QLabel("Góc Hướng", self.uic.centralwidget)
            self.label_azimuth.setGeometry(1646, 1080, 124, 40)
            self.label_azimuth.setAlignment(Qt.AlignCenter)

            self.uic.label_distance.setVisible(True)
            self.uic.label_EA.setVisible(True)
            self.uic.label_AA.setVisible(True)

            self.setup_video_player()
        except Exception as e:
            print(f"Lỗi khi thiết lập UI: {str(e)}")
            QMessageBox.critical(self.main_win, "Lỗi Widget", 
                               f"Không thể thiết lập widget: {str(e)}")
            sys.exit(1)

    def setup_video_player(self):
        """Thiết lập widget video."""
        # camera_url = "rtsp://192.168.100.24:554/stream1"  # Thay bằng URL thực tế
        try:
            self.video_widget = VideoWidget(self.uic.frame_video, video_source=0, #camera_url
                                         day_mode=self.day_mode)
            self.video_widget.setGeometry(4, 4, 1892, 892)
            self.video_widget.show()
        except Exception as e:
            print(f"Lỗi khi thiết lập video: {str(e)}")
            self.video_widget = None
            error_label = QLabel(f"Lỗi Video: {str(e)}")
            error_label.setStyleSheet("color: red; font-size: 20px;")
            error_label.setGeometry(10, 10, 1900, 900)
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setParent(self.uic.frame_video)
            error_label.show()

    def setup_connections(self):
        """Thiết lập kết nối tín hiệu-sự kiện."""
        try:
            self.uic.textEditEA.textChanged.connect(self.update_elevation_angle)
            self.uic.textEditAA.textChanged.connect(self.update_azimuth_angle)
            self.uic.textEditDis.textChanged.connect(self.update_distance)
        except Exception as e:
            print(f"Lỗi khi kết nối tín hiệu textChanged: {str(e)}")

    def setup_timers(self):
        """Thiết lập bộ đếm thời gian cho cập nhật thông số và chế độ ngày/đêm."""
        self.data_timer = QTimer(self.main_win)
        self.data_timer.timeout.connect(self.update_parameters)
        self.data_timer.start(100)

        self.time_check_timer = QTimer(self.main_win)
        self.time_check_timer.timeout.connect(self.check_day_mode)
        self.time_check_timer.start(60000)

    def is_day_time(self):
        """Kiểm tra thời gian hiện tại là ban ngày (6h-18h)."""
        try:
            current_hour = datetime.datetime.now().hour
            return 6 <= current_hour < 18
        except Exception as e:
            print(f"Lỗi khi kiểm tra thời gian: {str(e)}")
            return True

    def check_day_mode(self):
        """Cập nhật chế độ ngày/đêm dựa trên thời gian."""
        try:
            new_day_mode = self.is_day_time()
            if new_day_mode != self.day_mode:
                print(f"Chuyển chế độ ngày/đêm sang: {new_day_mode} "
                      f"(thời gian: {datetime.datetime.now().strftime('%H:%M')})")
                self.day_mode = new_day_mode
                self.update_colors()
        except Exception as e:
            print(f"Lỗi khi kiểm tra chế độ ngày/đêm: {str(e)}")

    def update_colors(self):
        """Cập nhật màu sắc giao diện theo chế độ ngày/đêm."""
        try:
            bg_color = "black" if self.day_mode else "white"
            text_color = "yellow"
            border_color = "white" if self.day_mode else "black"
            font_size = 20

            self.uic.centralwidget.setStyleSheet(f"background-color: {bg_color};")
            self.uic.frame_video.setStyleSheet(
                f"QFrame#frame_video {{ border: 4px solid orange; background-color: {bg_color}; }}")

            # Cập nhật kiểu cho ô nhập
            for text_edit in [self.uic.textEditDis, self.uic.textEditEA, self.uic.textEditAA]:
                text_edit.setStyleSheet(
                    f"background-color: {bg_color}; color: {text_color}; "
                    f"font-size: {font_size}px; font-weight: bold; "
                    f"border: 2px solid {border_color};")
                text_edit.setAlignment(Qt.AlignCenter)

            # Cập nhật kiểu cho nhãn
            for label in [self.uic.label_distance, self.uic.label_EA, self.uic.label_AA]:
                label.setStyleSheet(
                    f"background-color: red; color: white; "
                    f"font-size: {font_size}px; font-weight: bold; "
                    f"border: 2px solid {border_color};")

            # Cập nhật kiểu cho nhãn tùy chỉnh
            for label in [self.label_elevation, self.label_azimuth]:
                label.setStyleSheet(
                    f"background-color: {bg_color}; color: {text_color}; "
                    f"font-size: {font_size}px; font-weight: bold; "
                    f"border: 2px solid {border_color};")

            # Cập nhật chế độ ngày/đêm cho widget
            if self.video_widget:
                self.video_widget.set_day_mode(self.day_mode)
            self.radian_picker.set_day_mode(self.day_mode)
            self.circle_picker.set_day_mode(self.day_mode)
            self.border_frame.set_day_mode(self.day_mode)
        except Exception as e:
            print(f"Lỗi khi cập nhật màu sắc: {str(e)}")

    def initialize_values(self):
        """Khởi tạo giá trị mặc định cho giao diện."""
        try:
            self.uic.textEditDis.setPlainText("50")
            self.uic.textEditEA.setPlainText("45")
            self.uic.textEditAA.setPlainText("39")
            self.radian_picker.set_angle(45)
            self.circle_picker.set_angle(39)
        except Exception as e:
            print(f"Lỗi khi khởi tạo giá trị: {str(e)}")

    def get_data_from_device(self):
        """Mô phỏng dữ liệu từ thiết bị."""
        try:
            return {
                "distance": random.uniform(10, 100),
                "elevation_angle": random.uniform(0, 90),
                "azimuth_angle": random.uniform(0, 360),
                "bounding_box": {
                    "x": random.randint(200, 1700),
                    "y": random.randint(100, 800),
                    "w": random.randint(100, 400),
                    "h": random.randint(100, 400)
                }
            }
        except Exception as e:
            print(f"Lỗi khi lấy dữ liệu từ thiết bị: {str(e)}")
            return {
                "distance": 50.0,
                "elevation_angle": 45.0,
                "azimuth_angle": 39.0,
                "bounding_box": None
            }

    def update_parameters(self):
        """Cập nhật giao diện với dữ liệu từ thiết bị."""
        try:
            data = self.get_data_from_device()
            self.uic.textEditDis.setPlainText(str(round(data["distance"], 2)))
            self.uic.textEditEA.setPlainText(str(round(data["elevation_angle"], 2)))
            self.uic.textEditAA.setPlainText(str(round(data["azimuth_angle"], 2)))
            self.radian_picker.set_angle(data["elevation_angle"])
            self.circle_picker.set_angle(data["azimuth_angle"])
            if self.video_widget:
                self.video_widget.set_bounding_box(data.get("bounding_box"))
        except Exception as e:
            print(f"Lỗi khi cập nhật thông số: {str(e)}")
            error_label = QLabel(f"Lỗi: {str(e)}")
            error_label.setStyleSheet("color: red; font-size: 20px;")
            error_label.setGeometry(844, 900, 271, 40)
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setParent(self.uic.centralwidget)
            error_label.show()
            QTimer.singleShot(2000, error_label.deleteLater)

    def update_elevation_angle(self):
        """Cập nhật hiển thị góc tầm."""
        try:
            angle = float(self.uic.textEditEA.toPlainText())
            self.radian_picker.set_angle(angle)
        except (ValueError, TypeError):
            print("Đầu vào góc tầm không hợp lệ")

    def update_azimuth_angle(self):
        """Cập nhật hiển thị góc hướng."""
        try:
            angle = float(self.uic.textEditAA.toPlainText())
            self.circle_picker.set_angle(angle)
        except (ValueError, TypeError):
            print("Đầu vào góc hướng không hợp lệ")

    def update_distance(self):
        """Dự phòng cho cập nhật khoảng cách."""
        pass

    def show(self):
        """Hiển thị cửa sổ chính."""
        try:
            self.main_win.show()
            # Để dùng toàn màn hình: self.main_win.showFullScreen()
        except Exception as e:
            print(f"Lỗi khi hiển thị cửa sổ: {str(e)}")
            QMessageBox.critical(self.main_win, "Lỗi Hiển Thị", 
                               f"Không thể hiển thị cửa sổ: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        QApplication.setAttribute(Qt.AA_DisableHighDpiScaling, True)
        main_win = MainWindow()
        main_win.main_win.resize(1920, 1200)
        main_win.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Lỗi chính: {str(e)}")
        QMessageBox.critical(None, "Lỗi Chính", 
                           f"Ứng dụng không thể khởi động: {str(e)}")
        sys.exit(1)