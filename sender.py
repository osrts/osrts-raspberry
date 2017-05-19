#!/usr/bin/env python

# Program launched by program.py

import time
import datetime
import socket
import requests
from collections import deque
from threading import Thread,Condition
import pickle
from led_controller import LedController

########################
####### Consumer #######
########################

class DataSender(Thread):
    """                         """

    def init_data(self, model):
        print("Init DataSender")
        self.model = model
        self.setName("DataSender")

    # The main loop of the sender
    def run(self):
        while(True):
            self.model.get_value('condition').acquire()
            self.model.get_value('condition').wait_for(self.not_empty)
            if self.model.get_value("is_connected"):
                data = self.model.get_value('data_queue').popleft()
                self.model.get_value('condition').release()
                succeed = self.send_data(data)
                if not succeed:
                    self.model.set_value("is_connected", False)
            else:
                self.model.get_value('condition').release()

            if self.model.get_value("is_connected"):
                time.sleep(0.1)
            else:
                time.sleep(1)

    # Method that check if the queue is empty or not
    def not_empty(self):
        return len(self.model.get_value('data_queue')) != 0

    # Method that sends the data to the server
    def send_data(self, data):
        try:
            # Normal case, connection is working
            data['email'] = self.model.get_value('config')['Database']['email']
            data['password'] = self.model.get_value('config')['Database']['password']
            data['strategy'] = "local"
            # The POST request and its response
            response = requests.post(self.model.get_value('config')['Database']['url']+"/times", json=data, timeout=3)
            if response.status_code == 201:
                # Data successfully send to the server
                pickle.dump( self.model.get_value('data_queue'), open( "times.data", "wb" ) )
                LedController().fast_blink(18)
            elif response.status_code == 409 or response.status_code == 404 or response.status_code == 406:
                LedController().fast_blink(18)
                LedController().fast_blink(18)
                self.model.get_value('errors').add(str(response.text))
            else:
                # If we get some kind of failure that did not raise an exception
                self.model.get_value('errors').add(str(response.text))
                self.reappend_data(data)
                return False
            return True
        # If the connection fails, we re-append the data (otherwise it's lost !)
        except requests.exceptions.RequestException as e:
            self.model.get_value('errors').add('Network error in sender')
            self.reappend_data(data)
            return False
        # In other types of failure
        except Exception as e:
            self.model.get_value('errors').add('Error in sender')
            self.reappend_data(data)
            return False

    # Utility method that re-appends the data to the queue
    def reappend_data(self, data):
        self.model.get_value('condition').acquire()
        self.model.get_value('data_queue').append(data)
        self.model.get_value('condition').release()
