#!/usr/bin/env python

# Guillaume Deconinck & Grynczel Wojciech

##########################################################
### This file is the point of entry of the application ###
##########################################################

import sys
import getopt
import time
import pickle
import os

from pathlib import Path
import shutil
from threading import Thread

# Our files
from model import Model
from file_manager import FileManager
from reader import TagReader
from fake_reader import FakeTagReader
from sender import DataSender
from online_status import OnlineStatus
import config_server
from led_controller import LedController

########################
### Start of program ###
########################

# Import config from usb key
config_file = Path("/mnt/usb/config.ini")
if config_file.is_file():
    print("Copy new config")
    shutil.copy2('/mnt/usb/config.ini', 'config.ini')
    LedController().importConfig()
else:
    LedController().start()

server = False
fake_flag = False
fake_numb = 0
online = True
silent = False
# Check arguments
try:
    opts, args = getopt.getopt(sys.argv[1:], 'f:obsc')
    for opt, arg in opts:
        if opt == '-f':
            print("***Option : Fake Reader")
            fake_flag = True
            fake_numb = arg
        elif opt == '-o':
            print("***Option : Offline")
            online = False
        elif opt == '-b':
            print("***Option : Erase times.data")
            try:
                os.remove("times.data")
            except Exception:
                pass
        elif opt == '-s':
            silent = True
        elif opt == '-c':
            server = True
except Exception as e:
    print(e)

# Register the default SIGINT signal
import signal
signal.signal(signal.SIGINT, signal.default_int_handler)

# Create a model (class that contains the data)
MODEL = Model()

# File's manager
FILE_MANAGER = FileManager(MODEL)
FILE_MANAGER.read_file()

if fake_flag:
    # Fake Producer
    TAG_READER = FakeTagReader()
    TAG_READER.daemon = True
    TAG_READER.init_data(MODEL, fake_numb)
    TAG_READER.start()
else:
    # Producer
    TAG_READER = TagReader()
    TAG_READER.daemon = True
    TAG_READER.init_data(MODEL)
    TAG_READER.start()

if online:
    # Launch the online status updater
    ONLINE_STATUS = OnlineStatus()
    ONLINE_STATUS.daemon = True
    ONLINE_STATUS.init_data(MODEL)
    ONLINE_STATUS.start()

    # Sender
    DATA_SENDER = DataSender()
    DATA_SENDER.daemon = True
    DATA_SENDER.init_data(MODEL)
    DATA_SENDER.start()

# Configuration Server
def run_config_server():
    config_server.main()

if server:
    config_thread = Thread(target=run_config_server, args=[])
    config_thread.daemon = True
    config_thread.start()


# Textual output
def show_textual_output():
    # Line 1 (title)
    print('\x1b[6;30;42m'+' '*27+'Checkpoint manager'+' '*27+'\x1b[0m')
    # Line 2 (empty)
    print('')
    # Line 3 (headers of configuration and status)
    print('\x1b[1;37;41m Configuration: \x1b[0m', end='')
    print(' '*30, end='')
    print('\x1b[1;37;41m Status: \x1b[0m')
    # Line 4 (Serial + Num of checkpoint)
    num_str = str(MODEL.get_value('config')['Checkpoint']['num'])
    print('Num: '+num_str, end='')
    print(' '*(41-len(num_str)), end='')
    print('Serial  : ', end='')
    if fake_flag:
        print('\x1b[1;32;40m'+'Fake'+'\x1b[0m')
    elif TAG_READER.serial:
        print('\x1b[1;32;40m'+u'\u2713'+'\x1b[0m')
    else:
        print('\x1b[1;31;40m'+u'\u2717'+'\x1b[0m')
    # Line 5 (Serial + Num of checkpoint)
    url = MODEL.get_value('config')['Database']['url']
    print('URL: '+url, end='')
    print(' '*(41-len(url)), end='')
    print('Internet: ', end='')
    if MODEL.get_value("is_connected"):
        print('\x1b[1;32;40m'+u'\u2713'+'\x1b[0m')
    else:
        print('\x1b[1;31;40m'+u'\u2717'+'\x1b[0m')
    # Line 6 and line 7
    print('\n')
    # line 8
    print(' '*20, end='')
    print('Number of tags in queue = '+str(len(MODEL.get_value('data_queue'))))
    # Line 9 & 10
    print('\n')
    # Line 11
    print('\033[K\x1b[1;37;41mErrors:\x1b[0m ', end='')
    for error in MODEL.get_value('errors'):
        print(str(error)+' | ', end='')
    MODEL.get_value('errors').clear()
    print('')
    # Line 12
    print('')
    # Line 13 (last)
    print('\x1b[0;37;44m EXIT: CTRL+C'+' '*59+'\x1b[0m')


def clear_cursor_position():
    print('\033[13A', end='')



# Infinite loop needed in both cases, otherwise the main thread stops
# Which would mean that the daemon threads would stop too !
if not silent:
    time.sleep(2)
    print()
    while True:
        try:
            show_textual_output()
            time.sleep(1)
            clear_cursor_position()
        except KeyboardInterrupt:
            sys.exit()
else:
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            sys.exit()
