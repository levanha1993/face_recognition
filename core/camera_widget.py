import threading
import time
from core.constant import Constant
from collections import deque
from threading import Thread

import cv2
import imutils
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QWidget, QLabel, QApplication

from core.face_recognition_model import FaceRecognitionModel
from core.socket_util import SocketUtil
from recognition.face import recognition_face


def recog_face(frame):
    """
    recognition face in frame
    :param frame: frame of video stream
    :return: frame
    """
    recognition_face(frame)


def spin(seconds):
    """Pause for set amount of seconds, replaces time.sleep so program doesnt stall"""

    time_end = time.time() + seconds
    while time.time() < time_end:
        QApplication.processEvents()


def send_data_socket(data):
    constant = Constant.get_instance()
    if isinstance(data, str):
        data = data.encode()
    s = SocketUtil()
    s.set_up_client(constant.PORT_SOCKET_1)

    # send data to server
    s.send_data_to_server(data)

    # receive back data from server
    recv_data = s.receive_data_from_server()
    if recv_data != data:
        send_data_socket(data)


class CameraWidget(QWidget):
    """Independent camera feed
    Uses threading to grab IP camera frames in the background

    @param width - Width of the video frame
    @param height - Height of the video frame
    @param stream_link - IP/RTSP/Webcam link
    @param aspect_ratio - Whether to maintain frame aspect ratio or force into fraame
    """

    def __init__(self, width, height, stream_link=0, aspect_ratio=False, parent=None, deque_size=1):
        super(CameraWidget, self).__init__(parent)
        # Flag send link to server
        self.send_link_to_server = False

        # Initialize deque used to store frames read from the stream
        self.deque = deque(maxlen=deque_size)

        # Slight offset is needed since PyQt layouts have a built in padding
        # So add offset to counter the padding
        self.offset = 16
        self.screen_width = width - self.offset
        self.screen_height = height - self.offset
        self.maintain_aspect_ratio = aspect_ratio

        self.camera_stream_link = stream_link
        self.face_recognition_model = FaceRecognitionModel.get_instance()

        # Flag to check if camera is valid/working
        self.online = False
        self.capture = None
        self.video_frame = QLabel()

        self.load_network_stream()

        # stop thread
        self.stop_thread = False

        # Start background frame grabbing
        self.get_frame_thread = Thread(target=self.get_frame, args=())
        self.get_frame_thread.daemon = True
        self.get_frame_thread.start()

        # Periodically set video frame to display
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.set_frame)
        self.timer.start(1)

        print('Started camera: {}'.format(self.camera_stream_link))
        print(threading.activeCount())

    def load_network_stream(self):
        """Verifies stream link and open new stream if valid"""

        def verify_network_stream(link):
            """Attempts to receive a frame from given link"""
            cap = cv2.VideoCapture(link)
            if not cap.isOpened():
                return False
            cap.release()
            return True

        def load_network_stream_thread():
            if verify_network_stream(self.camera_stream_link):
                self.capture = cv2.VideoCapture(self.camera_stream_link)
                self.online = True

        self.load_stream_thread = Thread(target=load_network_stream_thread, args=())
        self.load_stream_thread.daemon = True
        self.load_stream_thread.start()

    def get_frame(self):
        """Reads frame, resizes, and converts image to pixmap"""
        while True:
            if self.stop_thread:
                break
            try:
                if self.capture.isOpened() and self.online:
                    # Read next frame from stream and insert into deque
                    status, frame = self.capture.read()
                    if status:
                        self.deque.append(frame)
                    else:
                        self.capture.release()
                        self.online = False
                else:
                    # Attempt to reconnect
                    print('attempting to reconnect', self.camera_stream_link)
                    self.load_network_stream()
                    spin(5)
                spin(.001)
            except AttributeError:
                pass

    def set_frame(self):
        """Sets pixmap image to video frame"""

        if not self.online:
            spin(1)
            return

        if self.deque and self.online:
            # Grab latest frame
            frame = self.deque[-1]
            if self.face_recognition_model.is_face_recognition and not self.send_link_to_server:
                send_data_socket(self.camera_stream_link)
                self.send_link_to_server = True
            elif not self.face_recognition_model.is_face_recognition:
                self.send_link_to_server = False

            # Keep frame aspect ratio
            if self.maintain_aspect_ratio:
                self.frame = imutils.resize(frame, width=self.screen_width)
            # Force resize
            else:
                self.frame = cv2.resize(frame, (self.screen_width, self.screen_height))

            # Convert to pixmap and set to video frame
            self.img = QtGui.QImage(self.frame, self.frame.shape[1], self.frame.shape[0],
                                    QtGui.QImage.Format_RGB888).rgbSwapped()
            self.pix = QtGui.QPixmap.fromImage(self.img)
            self.video_frame.setPixmap(self.pix)

    def get_video_frame(self):
        """
        Get frame to show
        :return: frame
        """
        return self.video_frame

    def stop_all_thread(self):
        self.stop_thread = True
