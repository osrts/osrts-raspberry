#!/usr/bin/env python

# Program launched by program.py

from datetime import datetime, date
import serial
from threading import Thread,Condition
import re, time
import platform
from time import sleep
import pickle


# Errors
ERROR_CREATING_SERIAL = 'Error creating the serial'
ERROR_WITH_SERIAL = 'Error with the serial'



########################
###### Producer ########
########################

class TagReader(Thread):
    """                         """

    def init_data(self,  model):
        self.setName("TagReader")
        print("Init TagReader")
        self.model = model
        self.serial = None
        self.check_serial()
        self.scanned_tags = set()
        self.backup_dir = None;

    def run(self):
        buffer = ''
        #print("Initializing data read ...")
        while True:
            if 'Checkpoint' not in self.model.get_value('config'):
                #print("No checkpoint in the config")
                continue
            self.model.get_value('condition').acquire()
            try:
                self.model.get_value('condition').wait_for(self.check_serial)
                data = self.serial.readline()
                if len(data) > 0:
                    tags = self.split(list(data), 20)
                    if len(list(tags)) > 0:
                        for tag in tags:
                            # Retrieve the tag number
                            tag_id = str(tag[9]) + "_" + str(tag[10]) + "" + str(tag[11]) + "" + str(tag[12]) + "" + str(tag[13])
                            if self.check_tag(tag, tag_id):
                                tag_num = self.tag_type(tag_id)[0]
                                tag_color = self.tag_type(tag_id)[1]
                                print("Scanned tag :  "+str(tag_num) + " (" + tag_color + ")")
                                time = {'timestamp': datetime.now().isoformat(), 'checkpoint_id': self.model.get_value('config')['Checkpoint']['num'], 'tag': { 'num': tag_num, 'color': tag_color }}
                                self.model.get_value('data_queue').append(time)
                                # Save the queue to file
                                pickle.dump( self.model.get_value('data_queue'), open( "times.data", "wb" ) )
                                # Backup scanned time in a file
                                csv = str(self.model.get_value('config')['Checkpoint']['num'])+","+str(tag_num)+","+str(tag_color)+","+str(datetime.now().isoformat())+"\n"
                                # Raspberry backup
                                with open(date.today().strftime("%d-%m-%Y")+'_backup.csv','a+') as f:
                                    f.write(csv)
                                try:
                                    # Save scanned tag to backup file on usb key
                                    with open(self.backup_dir+""+date.today().strftime("%d-%m-%Y")+'_backup.csv','a+') as f:
                                        f.write(csv)
                                except IOError as e:
                                    self.model.get_value('errors').add('USB KEY is not connected!')
                            else:
                                self.model.get_value('errors').add('Error during the check of the tag')
            except Exception as e:
                self.model.get_value('errors').add(ERROR_WITH_SERIAL)
                self.serial = None
            self.model.get_value('condition').notify()
            self.model.get_value('condition').release()
            # time.sleep(1)
            sleep(0.01)
        self.serial.close()

    def check_tag(self, tag, tag_id):
        """Check if the tag is valid and if it was already scanned
        Valid tag : AB CD 0x 0x 0x 0x DC BA where x is a decimal number
        """
        if tag[7] == 171 and tag[8] == 205 and tag[14] == 220 and tag[15] == 186:
            if tag_id not in self.scanned_tags:
                self.scanned_tags.add(tag_id)
                return True
            else:
                print("Tag " + str(tag_id) + " already scanned")
        else:
            return False

    def tag_type(self, tag_id):
        if tag_id[0] is '1':
            return (tag_id[2:], 'Bleu')
        elif tag_id[0] is '2':
            return (tag_id[2:], 'Orange')
        else:
            return 'invalid'

    def split(self, arr, size):
         arrs = []
         while len(arr) > size:
             pice = arr[:size]
             arrs.append(pice)
             arr   = arr[size:]
         arrs.append(arr)
         return arrs

    def split_list(self, alist, wanted_parts=1):
        length = len(alist)
        return [ alist[i*length // wanted_parts: (i+1)*length // wanted_parts]
                 for i in range(wanted_parts) ]

    def create_serial(self):
        #print("Create serial")
        try:
            if platform.system() == 'Windows':
                if not self.backup_dir:
                    self.backup_dir = "c:/"
                    print("Windows dir : c:")
                self.serial = serial.Serial(
                    port='COM5',
                    baudrate=9600,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS,
                    timeout=1
                )
            elif platform.system() == 'Darwin':
                if not self.backup_dir:
                    self.backup_dir = "/mnt/usb/"
                    print("Mac dir : /mnt/usb/:")
                self.serial = serial.Serial(
                    port='/dev/tty.usbserial',
                    baudrate=9600,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS,
                    timeout=1
                )
            else:
                if not self.backup_dir:
                    self.backup_dir = "/mnt/usb/"
                    print("Linux dir : /mnt/usb/:")
                self.serial = serial.Serial(
                    port='/dev/ttyUSB0',
                    baudrate=9600,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS,
                    timeout=1
                )
        except Exception as e:
            self.model.get_value('errors').add(ERROR_CREATING_SERIAL)

    def check_serial(self):
        if self.serial is None:
            self.create_serial()
            return True
        else:
            return True
