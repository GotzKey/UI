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
    """Main application window for the camera interface."""
    def __init__(self):
        self.main_win = QMainWindow()
        self.uic = Ui_MainWindow()
        self.uic.setupUi(self.main_win)
        self.day_mode = self.is_day_time()

        # Setup UI components
        self.setup_ui_geometry()
        self.setup_widgets()
        self.setup_connections()
        self.setup_timers()
        self.initialize_values()
        self.update_colors()

    def setup_ui_geometry(self):
        """Set geometry for UI elements."""
        self.uic.frame_video.setGeometry(10, 10, 780, 300)
        self.uic.label_distance.setGeometry(320, 335, 70, 30)
        self.uic.label_EA.setGeometry(320, 365, 70, 30)
        self.uic.label_AA.setGeometry(320, 395, 70, 30)
        self.uic.textEditDis.setGeometry(400, 335, 70, 30)
        self.uic.textEditEA.setGeometry(400, 365, 70, 30)
        self.uic.textEditAA.setGeometry(400, 395, 70, 30)

    def setup_widgets(self):
        """Initialize and setup UI widgets."""
        self.border_frame = BorderFrame(self.uic.centralwidget, self.day_mode)
        self.border_frame.setGeometry(310, 330, 180, 100)
        self.border_frame.lower()

        self.radian_picker = RadianAnglePicker(self.uic.centralwidget, self.day_mode)
        self.radian_picker.setGeometry(50, 340, 80, 80)
        self.label_elevation = QLabel("Góc Tầm", self.uic.centralwidget)
        self.label_elevation.setGeometry(50, 425, 80, 25)
        self.label_elevation.setAlignment(Qt.AlignCenter)

        self.circle_picker = FullCircleAnglePicker(self.uic.centralwidget, self.day_mode)
        self.circle_picker.setGeometry(670, 340, 80, 80)
        self.label_azimuth = QLabel("Góc Hướng", self.uic.centralwidget)
        self.label_azimuth.setGeometry(670, 425, 80, 25)
        self.label_azimuth.setAlignment(Qt.AlignCenter)

        self.uic.label_distance.setVisible(True)
        self.uic.label_EA.setVisible(True)
        self.uic.label_AA.setVisible(True)

        self.setup_video_player()

    def setup_video_player(self):
        """Setup the video player widget."""
        try:
            self.video_widget = VideoWidget(self.uic.frame_video, video_source=0, day_mode=self.day_mode)
            self.video_widget.setGeometry(4, 4, 772, 292)
            self.video_widget.show()
        except Exception as e:
            QMessageBox.critical(self.main_win, "Error", f"Failed to load video: {str(e)}")

    def setup_connections(self):
        """Setup signal-slot connections."""
        self.uic.textEditEA.textChanged.connect(self.update_elevation_angle)
        self.uic.textEditAA.textChanged.connect(self.update_azimuth_angle)
        self.uic.textEditDis.textChanged.connect(self.update_distance)

    def setup_timers(self):
        """Setup timers for updating parameters and checking day mode."""
        self.data_timer = QTimer(self.main_win)
        self.data_timer.timeout.connect(self.update_parameters)
        self.data_timer.start(100)

        self.time_check_timer = QTimer(self.main_win)
        self.time_check_timer.timeout.connect(self.check_day_mode)
        self.time_check_timer.start(60000)

    def is_day_time(self):
        """Check if current time is daytime (6 AM to 6 PM)."""
        current_hour = datetime.datetime.now().hour
        return 6 <= current_hour < 18

    def check_day_mode(self):
        """Update day mode based on current time."""
        new_day_mode = self.is_day_time()
        if new_day_mode != self.day_mode:
            self.day_mode = new_day_mode
            self.update_colors()

    def update_colors(self):
        """Update UI colors based on day/night mode."""
        bg_color = "black" if self.day_mode else "white"
        text_color = "yellow"
        border_color = "white" if self.day_mode else "black"
        font_size = 16

        self.uic.centralwidget.setStyleSheet(f"background-color: {bg_color};")
        self.uic.frame_video.setStyleSheet(
            f"QFrame#frame_video {{ border: 3px solid orange; background-color: {bg_color}; }}")
        for text_edit in [self.uic.textEditDis, self.uic.textEditEA, self.uic.textEditAA]:
            text_edit.setStyleSheet(
                f"background-color: {bg_color}; color: {text_color}; font-size: {font_size}px; "
                f"font-weight: bold; border: 1px solid {border_color};")
            text_edit.setAlignment(Qt.AlignCenter)
        for label in [self.uic.label_distance, self.uic.label_EA, self.uic.label_AA]:
            label.setStyleSheet(
                f"background-color: red; color: white; font-size: {font_size}px; "
                f"font-weight: bold; border: 1px solid {border_color};")
        for label in [self.label_elevation, self.label_azimuth]:
            label.setStyleSheet(
                f"background-color: {bg_color}; color: {text_color}; font-size: {font_size}px; "
                f"font-weight: bold; border: 1px solid {border_color};")

        self.video_widget.set_day_mode(self.day_mode)
        self.radian_picker.set_day_mode(self.day_mode)
        self.circle_picker.set_day_mode(self.day_mode)
        self.border_frame.set_day_mode(self.day_mode)

    def initialize_values(self):
        """Initialize default values for UI elements."""
        self.uic.textEditDis.setPlainText("50")
        self.uic.textEditEA.setPlainText("45")
        self.uic.textEditAA.setPlainText("39")
        self.radian_picker.set_angle(45)
        self.circle_picker.set_angle(39)

    def get_data_from_device(self):
        """Simulate data retrieval from a device."""
        return {
            "distance": random.uniform(10, 100),
            "elevation_angle": random.uniform(0, 90),
            "azimuth_angle": random.uniform(0, 360),
            "bounding_box": {
                "x": random.randint(100, 600),
                "y": random.randint(50, 250),
                "w": random.randint(50, 200),
                "h": random.randint(50, 200)
            }
        }

    def update_parameters(self):
        """Update UI with data from device."""
        try:
            data = self.get_data_from_device()
            self.uic.textEditDis.setPlainText(str(round(data["distance"], 2)))
            self.uic.textEditEA.setPlainText(str(round(data["elevation_angle"], 2)))
            self.uic.textEditAA.setPlainText(str(round(data["azimuth_angle"], 2)))
            self.radian_picker.set_angle(data["elevation_angle"])
            self.circle_picker.set_angle(data["azimuth_angle"])
            self.video_widget.set_bounding_box(data.get("bounding_box"))
        except Exception as e:
            error_label = QLabel(f"Error: {str(e)}")
            error_label.setStyleSheet("color: red; font-size: 16px;")
            error_label.setGeometry(310, 310, 180, 20)
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setParent(self.uic.centralwidget)
            error_label.show()
            QTimer.singleShot(2000, error_label.deleteLater)

    def update_elevation_angle(self):
        """Update elevation angle display."""
        try:
            angle = float(self.uic.textEditEA.toPlainText())
            self.radian_picker.set_angle(angle)
        except ValueError:
            pass

    def update_azimuth_angle(self):
        """Update azimuth angle display."""
        try:
            angle = float(self.uic.textEditAA.toPlainText())
            self.circle_picker.set_angle(angle)
        except ValueError:
            pass

    def update_distance(self):
        """Placeholder for distance update."""
        pass

    def show(self):
        """Show the main window."""
        self.main_win.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        QApplication.setAttribute(Qt.AA_DisableHighDpiScaling, True)
        main_win = MainWindow()
        main_win.main_win.resize(800, 480)
        main_win.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Error in main: {str(e)}")