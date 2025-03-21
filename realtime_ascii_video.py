import os.path
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, \
    QComboBox
import numpy as np
from image_to_ascii import *
import multiprocessing
import queue

######################################################

# main app class
class VideoASCII(QWidget):

    def __init__(self):
        super().__init__()
        self.frame_height = None
        self.frame_width = None
        self.cam = None
        self.camera_running = False
        self.setWindowTitle("ASCII to video")
        self.window_base_width = None

        self.resize(400, 200)

        self.master_layout = QVBoxLayout()

        self.converter = None
        self.font_paths = self.load_fonts()
        self.selected_font = "DejaVuSansMono.ttf" # set the font to the first font in the combobox
        self.font_paths.insert(0, "DejaVuSansMono.ttf")
        # ui
        self.init_ui()
        self.event_handler()
        self.move(1400, 500)

        self.worker_process = None

        self.input_queue = multiprocessing.Queue(maxsize=1)
        self.output_queue = multiprocessing.Queue(maxsize=1)

        self.timer = QTimer(self)  # Use QTimer instead of while loop
        self.timer.timeout.connect(self.process_frame)


    def init_ui(self):
        self.video_layout = QHBoxLayout()
        self.start_video_button = QPushButton("Start Video")
        self.stop_video_button = QPushButton("Stop Video")
        self.fonts_combo_box = QComboBox()

        # get fonts from the list

        for font_path in self.font_paths:
            font_name = os.path.basename(font_path)  # extract just the font name
            self.fonts_combo_box.addItem(font_name, font_path)  # store full path as user data



        self.video_layout.addWidget(self.start_video_button)
        self.video_layout.addWidget(self.stop_video_button)
        self.video_layout.addWidget(self.fonts_combo_box)

        self.master_layout.addLayout(self.video_layout)
        self.master_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # add master layout to the window
        self.setLayout(self.master_layout)



    def event_handler(self):
        self.fonts_combo_box.currentIndexChanged.connect(self.font_selected)
        self.start_video_button.clicked.connect(self.camera_run)
        self.stop_video_button.clicked.connect(self.change_run_state)


    def font_selected(self, index):
        selected_font_path = self.fonts_combo_box.itemData(index)  # Retrieve stored font path
        # print(f"Selected Font Path: {selected_font_path}")
        self.selected_font = selected_font_path

        # Send font update to worker
        if self.worker_process is not None:
            self.input_queue.put(("FONT_UPDATE", self.selected_font))


    def open_camera(self):
        # Open the default camera
        self.cam = cv2.VideoCapture(0)

        # Get the default frame width and height
        self.frame_width = int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.camera_running = True

    def start_worker(self):
        """Start the worker process if not already running."""
        if self.worker_process is None or not self.worker_process.is_alive():
            self.worker_process = multiprocessing.Process(
                target=ascii_worker,
                args=(self.input_queue, self.output_queue, self.selected_font),
                daemon=True
            )
            self.worker_process.start()
            print(f"Worker process started: {self.worker_process.pid}")

    def camera_run(self):
        self.open_camera()
        self.start_worker()
        self.timer.start(15)  # Process a frame every 15ms

    def process_frame(self):
        if not self.camera_running:
            self.timer.stop()
            return

        ret, frame = self.cam.read()
        if not ret:
            self.stop_camera()
            return

        try:
            if self.input_queue.empty():
                self.input_queue.put_nowait(frame)
        except queue.Full:
            pass  # Skip if full

        try:
            ascii_img_cv = self.output_queue.get_nowait()
            cv2.imshow('Camera', ascii_img_cv)
        except queue.Empty:
            pass  # No frame available

    def stop_camera(self):
        self.camera_running = False
        self.timer.stop()
        self.stop_worker()
        if self.cam:
            self.cam.release()
        cv2.destroyAllWindows()

    def stop_worker(self):
        print("Stopping worker process...")
        if self.worker_process is not None:
            self.input_queue.put(None)  # Signal the process to stop
            self.worker_process.join()  # Wait for it to exit
            self.worker_process = None


    @staticmethod
    def load_fonts():
        fonts_files = "fonts"
        font_files = [i for i in os.listdir(fonts_files)]
        font_paths = []
        for path in font_files:
            font_paths.append(os.path.abspath(os.path.join(fonts_files, path)))

        return font_paths

    def change_run_state(self):
        self.camera_running = False

    def closeEvent(self, event):
        self.camera_running = False
        event.accept()

# process
def ascii_worker(input_queue, output_queue, font):
    """Worker process function for converting frames to ASCII."""
    converter_proc = ImageToAsciiConverter()

    while True:
        try:
            data = input_queue.get()
            if data is None:
                break  # Stop signal

            if isinstance(data, tuple) and data[0] == "FONT_UPDATE":
                font = data[1]  # Update the font
                converter_proc = ImageToAsciiConverter(width=150)  # Recreate converter if needed
                continue  # Don't process a frame, just update the font

            frame = data  # If it's not a font update, treat it as a frame
            ascii_image = converter_proc.convert(frame, font=font)
            ascii_img_cv = cv2.cvtColor(np.array(ascii_image), cv2.COLOR_RGB2BGR)

            output_queue.put(ascii_img_cv)

        except queue.Empty:
            continue



if __name__ == "__main__":
    import sys
    multiprocessing.freeze_support()  # Required for Windows multiprocessing
    app = QApplication([])
    video_app = VideoASCII()
    video_app.show()
    sys.exit(app.exec())


