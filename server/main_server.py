import socket
import time
import threading
from threading import Thread

from PyQt5.QtWidgets import QApplication

from core.constant import Constant
from core.face_recognition_model import train_face
from core.socket_util import SocketUtil
from core.face_recognition_model import FaceRecognitionModel
from server.camera_model import CameraModel


class FaceRecognitionServer:
    def __init__(self):
        self.cameras = []
        train_face()
        self.check_socket()

    def check_socket(self):
        constant = Constant.get_instance()
        s = SocketUtil()
        s.set_up_server(constant.PORT_SOCKET_1)
        while True:
            try:
                # create connection
                s.create_connection()

                # receive data from client
                data = s.receive_data_from_client()
                print(data)

                # send back data to client
                s.send_data_to_client(data)

                # close connection
                s.close_connection()

                data = data.decode("utf-8")

                # if data is start or end recognition message, then stop all recognition thread  before
                # else add new recognition thread
                face_recognition_model = FaceRecognitionModel.get_instance()
                if data == constant.START_FACE_RECOGNITION_MESSAGE:
                    face_recognition_model.is_face_recognition = True
                elif data == constant.END_FACE_RECOGNITION_MESSAGE:
                    self.stop_all_camera()
                    self.cameras = []
                    face_recognition_model.is_face_recognition = False
                elif data == constant.TRAIN_NEW_FACE_MESSAGE:
                    train_face()
                elif data != b'':
                    self.cameras.append(CameraModel(data))
                    print(f"thread number: {threading.active_count()}")
            except Exception as ex:
                print(__file__)
                print(ex)
                continue

    def stop_all_camera(self):
        for camera in self.cameras:
            camera.stop_camera()


if __name__ == '__main__':
    try:
        FaceRecognitionServer()
    except Exception as ex:
        print(ex)
