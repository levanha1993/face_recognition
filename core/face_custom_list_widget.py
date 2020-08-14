from PyQt5.QtWidgets import QListWidget, QListWidgetItem

from core.face_custom_widget import FaceWidget


class FaceList(QListWidget):
    def __init__(self):
        QListWidget.__init__(self)

    def add_item(self, face_object):
        # create face widget
        # my_face_widget = FaceWidget()
        # my_face_widget.set_text_name(face_object["name"])
        # my_face_widget.set_text_time(face_object["time"])
        # my_face_widget.set_face(face_object["face_image"])

        # Create QListWidgetItem
        item = f"""        
        Time: {face_object["time"]}
        Name: {face_object["name"]}
        """
        my_list_widget_item = QListWidgetItem(item)

        # Set size hint
        # my_list_widget_item.setSizeHint(my_face_widget.sizeHint())

        # Add QListWidgetItem into QListWidget
        self.insertItem(0, my_list_widget_item)
        # self.setItemWidget(my_list_widget_item, my_face_widget)
