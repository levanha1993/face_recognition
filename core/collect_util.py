from collections import deque


class CollectionUtil:
    """
    store data deque
    """
    __instance = None
    __deque = deque(maxlen=1)
    __is_change = False

    @staticmethod
    def get_instance():
        """ Static access method. """
        if CollectionUtil.__instance is None:
            CollectionUtil()
        return CollectionUtil.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if CollectionUtil.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            CollectionUtil.__instance = self

    @property
    def is_change(self):
        return self.__is_change

    @property
    def pop(self):
        self.__is_change = False
        return self.__deque.pop()

    def append(self, item):
        self.__deque.append(item)
        self.__is_change = True
