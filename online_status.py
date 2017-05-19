#!/usr/bin/env python
# Program launched by program.py

import time
import datetime
import socket
import requests
from collections import deque
from threading import Thread, Condition, Timer
from requests.auth import HTTPBasicAuth
from led_controller import LedController

# Errors
ERROR_ONLINE_STATUS = 'Error - online status'

class OnlineStatus(Thread):
    """                         """
    def init_data(self, model):
        self.model = model
        print("Init OnlineStatus")
        self.setName("OnlineStatus")

    def run(self):
        while True:
            if check_connection():
                try:
                    self.model.set_value("is_connected", True)
                    if 'Database' in self.model.get_value('config'):
                        if 'id' in self.model.get_value('config')['Checkpoint']:
                            # Update checkpoint status
                            response = requests.patch(self.model.get_value('config')['Database']['url']+"/checkpoints/"+self.model.get_value('config')['Checkpoint']['id'],
                            {
                                "online": True,
                                "last_connection": int(time.time()),
                                "email":self.model.get_value('config')['Database']['email'],
                                "password":self.model.get_value('config')['Database']['password'],
                                "strategy":"local"
                            })
                        else:
                            response = requests.get(self.model.get_value('config')['Database']['url']+"/checkpoints"+
                                "?num="+self.model.get_value('config')['Checkpoint']['num'])
                            json = response.json()
                            self.model.get_value('config')['Checkpoint']['id'] = json['data'][0]['_id']
                except Exception as inst:
                    self.model.get_value('errors').add(ERROR_ONLINE_STATUS)
                time.sleep(2)
            else:
                self.model.set_value("is_connected", False)
                time.sleep(3)


########################
###     Functions    ###
########################

def check_connection(host="8.8.8.8", port=53, timeout=3):
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        mysocket.connect((host, port))
        mysocket.close()
        LedController().blink(23)
        return True
    except Exception as e:
        pass
    return False
