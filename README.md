# Open Source RFID Race Timing System - Raspberry PI

This repository contains the source code of the Python3 program running on each Raspberry PI. Each Raspberry PI represents a checkpoint and has an UHF RFID antenna connected to it.

The job of the Raspberry PI is to detect the runners with the help of the antenna, to store their times in memory and finally to send those times to the back-end when an internet connection is available.

# Installation

First, you need to ensure that Python3 is installed. On a Raspberry PI model 3, it should be installed by default. However, check if it is really the case by typing one of the following command:

```
$ python -V
$ python3 -V
```
One of those commands should display "Python 3.x.x".

The next step is to install the two dependencies of this projet, which are

* [Pyserial](https://pythonhosted.org/pyserial/)
* [Flask](https://github.com/pallets/flask)
* [Requests](http://docs.python-requests.org/en/master/)

Those dependencies are installed thanks to the Python package manager, aka pip.
Type the following commands to install both dependencies:

```
$ pip install pyserial
$ pip install flask
$ pip install requests
```

# Launch

Once the dependencies are installed, it is time to launch the application. To do so, simply type the following command:

```
python program.py
```
Note that it might be `python3` instead, depending on which command has output Python 3 in the installation.

Multiple options can be given to program.py:
 * `-f n` launches the program with the fake reader (simulates the real reader with random data). It fakes scanning `n` runners (n is therefore a number).
 * `-o` launches the program in offline mode (no online\_status and no sender).
 * `-b` deletes the previous backup file *times.data*.
 * `-s` launches the program in silent mode. That means that it deactivates the textual output.
 * `-c` launches the program with the configuration web server.

 # Additional remarks

 * Our Raspberry PI have two small leds to indicate that it is connected to the internet and that it is sending data.

 # License
[MIT](https://github.com/osrts/osrts-backend/blob/master/LICENSE)

# Authors

* Guillaume Deconinck
* Wojciech Grynczel
