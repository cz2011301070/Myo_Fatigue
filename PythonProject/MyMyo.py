import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import random  # Only for generating dummy data
import myo
import time

import queue
import numpy as np
from Zmq_Router import ZmqRouter
import csv

class Listener(myo.DeviceListener):
    def __init__(self, sdkpath, address):
        super().__init__()
        myo.init(sdk_path= sdkpath)
        self.hub = myo.Hub()
        self.observers = []
        self.zmqRouter = ZmqRouter(address)
    def fetch_emg(self):
        while self.hub.run(self.on_event,10000):
            pass
    def register_observer(self, observer):
        self.observers.append(observer)
    def notify(self, data):
        for observer in self.observers:
            observer(data)
    
    def on_paired(self, event):
        print("Hello, {}!".format(event.device_name))
        event.device.vibrate(myo.VibrationType.short)
        event.device.stream_emg(myo.StreamEmg.enabled)
    def on_unpaired(self, event):
        return False  # Stop the hub
    def on_orientation(self, event):
        orientation = event.orientation
        acceleration = event.acceleration
        gyroscope = event.gyroscope
    # ... do something with that

    def on_emg(self, event):
        try:
            emg = []
            emg = event.emg
            marker = self.zmqRouter.PollData()
            if len(emg) == 8:
                emg.append(marker)
        except AttributeError:
            pass
        else:
            # handle the emg data
            self.notify(emg)
            print(emg)
    def on_connected(self, event):
        print("connected!")
    def on_disconnected(self, event):
        print("Disconnected!")
    

    