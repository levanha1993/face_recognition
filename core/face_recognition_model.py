import os
import pickle

import face_recognition


def train_face():
    """
    train face to recognition
    :return: None
    """
    face_recognition_model = FaceRecognitionModel.get_instance()

    # load face data is trained
    face_recognition_model.known_face_encodings, face_recognition_model.known_face_names = load_known_faces()

    # Load a sample picture and learn how to recognize it.
    direction = os.path.dirname(__file__)
    data_set_new_path = os.path.join(direction, "dataset/new_face")
    for _, d, _ in os.walk(data_set_new_path):
        for directory in d:
            image_directory_path = os.path.join(data_set_new_path, directory)
            for _, _, f in os.walk(image_directory_path):
                for file in f:
                    if '.jpg' in file:
                        file_path = os.path.join(image_directory_path, file)
                        print(file_path)
                        image = face_recognition.load_image_file(file_path)
                        image_encoding = face_recognition.face_encodings(image)
                        if image_encoding:
                            face_recognition_model.known_face_encodings.append(image_encoding[0])
                            face_recognition_model.known_face_names.append(directory)

                            # move face is trained to old face
                            move_file(file_path, file_path.replace("new_face", "old_face"))
                        else:
                            print(f"{file_path} don't detect face")

                            # move face can't train to trash face
                            move_file(file_path, file_path.replace("new_face", "trash_face"))

    # save face data is trained
    save_known_faces(face_recognition_model.known_face_encodings, face_recognition_model.known_face_names)


def move_file(source_path, destination_path):
    """
    Move file from source path to destination path
    :param source_path: The directory containing the file
    :param destination_path: The directory which file go to
    :return: None
    """
    direction = os.path.dirname(destination_path)
    if not os.path.exists(direction):
        os.makedirs(direction)
    os.replace(source_path, destination_path)


def save_known_faces(known_face_encodings, known_face_name):
    """
    save face data is trained
    :param known_face_encodings: list face encode
    :param known_face_name: list name of face
    :return:None
    """
    direction = os.path.dirname(__file__)
    data_file_path = os.path.join(direction, "dataset/known_faces.dat")
    with open(data_file_path, "wb") as face_data_file:
        face_data = [known_face_encodings, known_face_name]
        pickle.dump(face_data, face_data_file)
        print("Known faces backed up to disk.")


def load_known_faces():
    """
    load face data is training
    :return: list face encode, list name of face
    """
    try:
        direction = os.path.dirname(__file__)
        data_file_path = os.path.join(direction, "dataset/known_faces.dat")
        with open(data_file_path, "rb") as face_data_file:
            known_face_encodings, known_face_name = pickle.load(face_data_file)
            print("Known faces loaded from disk.")
            return known_face_encodings, known_face_name
    except FileNotFoundError:
        print("No previous face data found - starting with a blank known face list.")
        return [], []


class FaceRecognitionModel:
    """
    use content info of program
    """
    __instance = None
    __is_face_recognition = False
    __known_face_encodings = []
    __known_face_names = []
    __faces_caught = []

    @staticmethod
    def get_instance():
        """ Static access method. """
        if FaceRecognitionModel.__instance is None:
            FaceRecognitionModel()
        return FaceRecognitionModel.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if FaceRecognitionModel.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            FaceRecognitionModel.__instance = self

    @property
    def is_face_recognition(self):
        return self.__is_face_recognition

    @is_face_recognition.setter
    def is_face_recognition(self, is_face_recognition):
        self.__is_face_recognition = is_face_recognition

    @property
    def known_face_encodings(self):
        return self.__known_face_encodings

    @known_face_encodings.setter
    def known_face_encodings(self, known_face_encodings):
        self.__known_face_encodings = known_face_encodings

    @property
    def known_face_names(self):
        return self.__known_face_names

    @known_face_names.setter
    def known_face_names(self, known_face_names):
        self.__known_face_names = known_face_names

    @property
    def faces_caught(self):
        return self.__faces_caught

    @faces_caught.setter
    def faces_caught(self, faces_caught):
        self.__faces_caught = faces_caught
