import os
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QDialog, QGridLayout, QGroupBox, QLabel, QPushButton, QVBoxLayout,
                             QHBoxLayout, QTreeWidget, QTreeWidgetItem, QFileDialog, QLineEdit, QFrame)
from PyQt5.QtGui import QPixmap

from shutil import copyfile
from pathlib import Path

from core.face_custom_list_widget import FaceList
from core.constant import Constant

from gui.action_main import send_data_socket
from gui.action_main import btn_show, btn_face_recognition, get_face_detect

all_link_camera = []
# Create Camera Widgets
username = 'admin'
password = 'CongNghe'

# Stream links
camera0 = 'rtsp://{}:{}@192.168.1.126/1'.format(username, password)
camera1 = 'rtsp://{}:{}@192.168.1.128/1'.format(username, password)

all_link_camera.append(camera0)
all_link_camera.append(camera1)

# constant
constant = Constant.get_instance()


class WidgetGallery(QDialog):
    def __init__(self, parent=None):
        super(WidgetGallery, self).__init__(parent)

        self.originalPalette = QApplication.palette()

        right_layout = self.create_right_layout()
        self.create_top_left_group_box()
        self.create_bottom_left_group_box()
        self.create_center_group_box()

        mainLayout = QGridLayout()
        mainLayout.addLayout(right_layout, 0, 2, 0, 1)
        mainLayout.addLayout(self.top_left_group_box, 0, 0)
        mainLayout.addWidget(self.bottom_left_group_box, 1, 0)
        mainLayout.addWidget(self.center_group_box, 1, 1)

        self.setLayout(mainLayout)

        self.setWindowTitle("Styles")

    def create_right_layout(self):
        # create list view
        self.my_list_widget = FaceList()
        self.my_list_widget.setFixedWidth(constant.RIGHT_LAYOUT_WIDTH)
        get_face_detect(self.my_list_widget)

        # create label
        label = QLabel()
        label.setText("Face Recognition")

        # create button
        add_face_button = QPushButton()
        add_face_button.setText("Add Face")
        add_face_button.clicked.connect(self.add_face_dialog)

        right_layout = QVBoxLayout()
        right_layout.addWidget(label)
        # right_layout.addStretch()
        right_layout.addWidget(self.my_list_widget)
        right_layout.addWidget(add_face_button)

        return right_layout

    def create_top_left_group_box(self):
        self.top_left_group_box = QGridLayout()
        face_recognition = QPushButton()
        face_recognition.setText("Face Recognition")
        face_recognition.clicked.connect(lambda: btn_face_recognition())

        self.top_left_group_box.addWidget(face_recognition)

    def create_bottom_left_group_box(self):
        self.bottom_left_group_box = QGroupBox("control")
        self.bottom_left_group_box.setFixedWidth(constant.LEFT_LAYOUT_WIDTH)

        tree = QTreeWidget()
        recorders = 1
        cams = 2
        for i in range(recorders):
            parent = QTreeWidgetItem(tree)
            parent.setText(0, "Recorder {}".format(i + 1))
            parent.setFlags(parent.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
            for x in range(cams):
                child = QTreeWidgetItem(parent)
                child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                child.setText(0, "Cam {}".format(x + 1))
                child.setCheckState(0, Qt.Unchecked)

        show = QPushButton()
        show.setText("Show")
        show.clicked.connect(lambda: btn_show(all_link_camera, self.grid_layout, tree))

        # TODO
        layout = QVBoxLayout()
        layout.addWidget(show)
        layout.addWidget(tree)
        self.bottom_left_group_box.setLayout(layout)

    def create_center_group_box(self):
        self.center_group_box = QGroupBox("Show")
        self.center_group_box.setMinimumWidth(300)

        # TODO
        self.grid_layout = QGridLayout()
        self.center_group_box.setLayout(self.grid_layout)

    def add_face_dialog(self):
        self.image = QLabel()

        # button Browse face file
        browse_button = QPushButton()
        browse_button.setText("Browse File")
        browse_button.clicked.connect(self.browse_image)

        # text box input name
        name = QLabel()
        name.setText("Name")
        self.name_input = QLineEdit()

        hbox = QHBoxLayout()
        hbox.addWidget(name)
        hbox.addWidget(self.name_input)

        save = QPushButton()
        save.setText("Save")
        save.clicked.connect(self.save_image)

        vbox_sub = QVBoxLayout()
        vbox_sub.addLayout(hbox)
        vbox_sub.addWidget(save)

        self.frame = QFrame()
        self.frame.setLayout(vbox_sub)
        self.frame.setHidden(True)

        vbox_main = QVBoxLayout()
        vbox_main.addWidget(browse_button)
        vbox_main.addWidget(self.image)
        vbox_main.addWidget(self.frame)

        d = QDialog()
        d.setGeometry(0, 0, 300, 400)
        d.setLayout(vbox_main)
        d.setWindowTitle("Dialog")
        d.setWindowModality(Qt.ApplicationModal)
        d.exec_()

    def browse_image(self):
        file_dialog = QFileDialog()
        file_dialog.setNameFilters(["Text files (*.txt)", "Images (*.png *.jpg)"])
        file_dialog.selectNameFilter("Images (*.png *.jpg)")

        filename = file_dialog.getOpenFileName()
        self.src_image = filename[0]
        pixmap = QPixmap(self.src_image).scaledToWidth(300)
        self.image.setPixmap(pixmap)
        self.frame.setHidden(False)

    def save_image(self):
        name = self.name_input.text()
        print({Path(__file__).parent.parent})
        path = f"{Path(__file__).parent.parent}/core/dataset/new_face/{name}"
        if not os.path.exists(path):
            os.mkdir(path)
        count = len([name for name in os.listdir('.') if os.path.isfile(name)])
        copyfile(self.src_image, f"{path}/{os.path.basename(self.src_image)}")
        send_data_socket(constant.TRAIN_NEW_FACE_MESSAGE)


if __name__ == '__main__':
    import sys

    try:
        app = QApplication(sys.argv)
        gallery = WidgetGallery()
        gallery.setFixedSize(constant.MAIN_WIDTH, constant.MAIN_HIGHT)
        gallery.show()
        sys.exit(app.exec_())
    except Exception as ex:
        print(ex)
