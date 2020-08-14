from collections import deque
from threading import Thread

import cv2
import time

from recognition.face import recognition_face
from core.face_recognition_model import FaceRecognitionModel
from PyQt5.QtWidgets import QApplication


def spin(seconds):
    """Pause for set amount of seconds, replaces time.sleep so program doesnt stall"""
    time_end = time.time() + seconds
    while time.time() < time_end:
        QApplication.processEvents()


class CameraModel:
    def __init__(self, _link):
        self.link = _link
        self.cap = None
        self.deque = deque(maxlen=1)
        self.stop_thread = False

        # recognition face
        self.face_recognition()

    def face_recognition(self):
        self.cap = cv2.VideoCapture(self.link)
        face_recognition_model = FaceRecognitionModel.get_instance()

        def put_frame():
            while True:
                if self.stop_thread:
                    break
                ret, frame = self.cap.read()
                if ret:
                    self.deque.append(frame)

        def recognition_frame():
            while True:
                if self.stop_thread:
                    break
                if self.deque and face_recognition_model.is_face_recognition:
                    frame = self.deque[0]
                    recognition_face(frame)
                    spin(1)

        self.put_frame_thread = Thread(target=put_frame, args=())
        self.put_frame_thread.daemon = True
        self.put_frame_thread.start()

        self.face_recognition_thread = Thread(target=recognition_frame, args=())
        self.face_recognition_thread.daemon = True
        self.face_recognition_thread.start()

    def stop_camera(self):
        # stop thread
        self.stop_thread = True
