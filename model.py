from collections import deque
from threading import Condition
import configparser


class Model:
    # Internal class that is a singleton
    class __OnlyOneModel:
        def __init__(self):
            self.map = {}
            # The queue containing the data to be sent
            self.map['data_queue'] = deque()
            # The lock to avoid conflict on the queue
            self.map['condition'] = Condition()
            # The configuration
            self.map['config'] = configparser.ConfigParser()
            self.map['config'].read('config.ini')
            # Is connected or
            self.map['is_connected'] = False
            # For display errors
            self.map['errors'] = set()

    # The instance
    instance = None

    def __init__(self):
        if not Model.instance:
            Model.instance = Model.__OnlyOneModel()
    
    def get_value(self, key):
        return self.instance.map[key]

    def set_value(self, key, value):
        Model.instance.map[key] = value

    