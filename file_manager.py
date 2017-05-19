#!/usr/bin/env python

# Program launched by program.py

import pickle
import os

FILE_NAME = 'times.data'

class FileManager:

    def __init__(self, model):
        self.model = model
        print("Init FileManager")

    def read_file(self):
        try:
            with open("times.data", "rb") as file:
                data = pickle.load(file)
                for d in data:
                    print("Import " + str(d) + " from times.data")
                    self.model.get_value('data_queue').append(d)
        except:
            pass
