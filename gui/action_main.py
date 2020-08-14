import json
import socket
import threading
from threading import Thread
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QPixmap

from core.camera_widget import CameraWidget
from core.constant import Constant
from core.face_recognition_model import FaceRecognitionModel
from core.socket_util import SocketUtil

constant = Constant.get_instance()
face_recognition_model = FaceRecognitionModel.get_instance()

global camera_widgets
camera_widgets = []


def btn_face_recognition():
    """
    enable face recognition
    :return: None
    """
    face_recognition_model.is_face_recognition = not face_recognition_model.is_face_recognition
    if face_recognition_model.is_face_recognition:
        send_data_socket(constant.START_FACE_RECOGNITION_MESSAGE)
    else:
        send_data_socket(constant.END_FACE_RECOGNITION_MESSAGE)


def btn_show(all_link_cameras, grid, tree):
    """
    show camera
    :param all_link_cameras: list ip/rtsp camera
    :param grid: grid layout content camera
    :param tree: tree view select camera
    :return: None
    """
    link_cameras = []

    def recurse(parent_item):
        for i in range(parent_item.childCount()):
            child = parent_item.child(i)
            grand_children = child.childCount()
            if grand_children > 0:
                recurse(child)
            elif child.checkState(0) == Qt.Checked:
                link_cameras.append(all_link_cameras[int(child.text(0)[-1]) - 1])

    recurse(tree.invisibleRootItem())
    setup_camera(link_cameras, grid)
    send_data_socket(constant.END_FACE_RECOGNITION_MESSAGE)
    face_recognition_model.is_face_recognition = False
    print(f"thread number: {threading.active_count()}")


def setup_camera(links, grid_layout):
    """
    set camera to grid layout
    :param links:
    :param grid_layout:
    :return:
    """
    global camera_widgets
    clear_layout(grid_layout)
    # Dynamically determine screen width/height
    screen_width = constant.CAMERA_LAYOUT_WIDTH
    screen_height = constant.CAMERA_LAYOUT_HIGHT
    print(screen_width,screen_height)

    camera_widgets = []
    split_number = len(links)
    for st_link in links:
        camera = CameraWidget((screen_width // (split_number*100))*100, screen_height // split_number, st_link)
        grid_layout.addWidget(camera.get_video_frame())
        camera_widgets.append(camera)


def clear_layout(grid_layout):
    """
    delete item in grid layout
    :param grid_layout:
    :return:
    """
    for i in reversed(range(grid_layout.count())):
        grid_layout.itemAt(i).widget().setParent(None)

    for camera in camera_widgets:
        camera.stop_all_thread()


def get_face_detect(my_list_widget):
    """
    get face detect in camera
    :param my_list_widget: list widget content camera
    :return: None
    """

    def check_have_new_face():
        while True:
            try:
                s = SocketUtil()
                s.set_up_client(constant.PORT_SOCKET_2)
                data = json.loads(s.receive_data_from_server())
                if data != b'':
                    show_face(my_list_widget, data)
            except:
                continue

    thread = Thread(target=check_have_new_face, args=())
    thread.daemon = True
    thread.start()


def show_face(my_list_widget, face_oj):
    """
    show face detect
    :param my_list_widget: list widget content camera
    :param face_oj: face object
    :return: None
    """
    print(face_oj)
    my_list_widget.add_item(face_oj)


def send_data_socket(_data):
    data = _data
    if isinstance(data, str):
        data = data.encode()

    try:
        s = SocketUtil()
        s.set_up_client(constant.PORT_SOCKET_1)

        # send data from client to server
        print(f"send data: {data}")
        s.send_data_to_server(data)

        # receive data from client
        recv_data = s.receive_data_from_server()

        # close socket
        s.close_socket()
        if recv_data != data:
            send_data_socket(data)
    except Exception as e:
        print(__file__)
        print(e)

