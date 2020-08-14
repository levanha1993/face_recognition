import json
import sys
import time
from datetime import datetime

import cv2
import face_recognition
import numpy as np

from core.constant import Constant
from core.face_recognition_model import FaceRecognitionModel
from core.socket_util import SocketUtil

face_recognition_model = FaceRecognitionModel.get_instance()
constant = Constant.get_instance()


def recognition_face(frame):
    try:
        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Only process every other frame of video to save time

        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(face_recognition_model.known_face_encodings, face_encoding)
            name = "Unknown"

            # Or instead, use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(face_recognition_model.known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            print(f"{face_distances[best_match_index]} - {face_distances[np.argmax(face_distances)]}")
            if matches[best_match_index] and face_distances[best_match_index] < 0.4:
                name = face_recognition_model.known_face_names[best_match_index]
            print(name)
            face_names.append(name)

        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # # Draw a box around the face
            # cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            #
            # # Draw a label with a name below the face
            # # cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            # font = cv2.FONT_HERSHEY_COMPLEX
            # cv2.putText(frame, name, (left + 6, bottom + 35), font, 1.0, (255, 0, 0), 2)

            # crop face from frame
            face_image = frame[top:bottom, left:right].copy()
            cv2.resize(face_image, (300, 400))

            # save face
            print(f"save face: {name}")
            save_face(face_image, name)
    except Exception as ex:
        print(__file__)
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(ex)


def save_face(face_image, name_face):
    """
    save face is caught is show
    :param face_image: face is caught
    :param name_face: name of face
    :return:
    """
    model = {
        "time": datetime.now().__str__(),
        # "face_image": face_image,
        "name": name_face
    }

    exist = False
    for index, obj in enumerate(face_recognition_model.faces_caught):
        if obj["name"] == name_face:
            exist = True
            time_now = time.time()
            old_time = float(obj["time"])
            if time_now - old_time > constant.TIME_CAUGHT_FACE:
                # update object time
                obj["time"] = time_now.__str__()
                face_recognition_model.faces_caught[index] = obj

                # send new face info to client
                print(f"send socket info face: {name_face}")
                send_face_info_to_client(model)
            break

    if not exist:
        obj = {
            "time": time.time(),
            "name": name_face
        }
        face_recognition_model.faces_caught.append(obj)
        # send new face info to client
        print(f"send socket info face: {name_face}")
        send_face_info_to_client(model)


def send_face_info_to_client(model):
    socket = SocketUtil()
    socket.set_up_server(constant.PORT_SOCKET_2)
    data = json.dumps(model)
    socket.create_connection()
    socket.send_data_to_client(data.encode())
