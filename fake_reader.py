# Guillaume Deconinck & Grynczel Wojciech

# Program launched by program.py

import pytz
from datetime import datetime, date
import serial
from threading import Thread,Condition
import random
import uuid
from time import sleep
from random import randint
import re, time
import pickle

############################
###### FakeProducer ########
############################

class FakeTagReader(Thread):
    """                         """

    def init_data(self,  model, iterations):
        self.setName("FakeTagReader")
        print("Init FakeTagReader")
        self.model = model
        self.iterations = iterations
        self.counter = 0
        self.scanned_tags = set()

    def run(self):
        while True:
            time.sleep(random.uniform(0, 5))
            if 'Checkpoint' not in self.model.get_value('config'):
                print("No checkpoint in the config")
                continue
            self.model.get_value('condition').acquire()
            data={
                'timestamp': datetime.now(pytz.timezone('Europe/Brussels')).isoformat(),
                'checkpoint_id': self.model.get_value('config')['Checkpoint']['num'],
                'tag':{
                    'num': random.randint(1,12),
                    'color': random.choice(['Orange', 'Bleu'])
                }
            }
            self.model.get_value('data_queue').append(data)
            #print("Scan "+str(data['tag']['num']) + "(" + data['tag']['color'] +")     (" + str(self.counter + 1)+ "/"+ str(self.iterations)+ ")")
            # Save the queue to file
            pickle.dump( self.model.get_value('data_queue'), open( "times.data", "wb" ) )
            # Save scanned tag to backup file on raspberry pi
            csv = str(data['checkpoint_id'])+","+str(data['tag']['num'])+","+str(data['tag']['color'])+","+str(data['timestamp'])+"\n"
            with open(date.today().strftime("%d-%m-%Y")+'_backup.csv','a+') as f:
                f.write(csv)
            try:
                # Save scanned tag to backup file on usb key
                with open('/mnt/usb/'+date.today().strftime("%d-%m-%Y")+'_backup.csv','a+') as f:
                    f.write(csv)
            except IOError:
                self.model.get_value('errors').add('USB KEY is not connected!')
            self.model.get_value('condition').notify()
            self.model.get_value('condition').release()
            self.counter = self.counter + 1
            if int(self.counter) == int(self.iterations):
                return
