import threading
from MyMyo import Listener
from Commons.CSVHandler import CSVHandler
from OnlineFatigue import OnlineFatigue
import keyboard
import os
import datetime
import time


import queue
import numpy as np

import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from PlotFeatures import *

window_size = 20
feature_num = 2
feature_window = window_size
feature_queues = [queue.Queue(maxsize=window_size) for _ in range(feature_num)]
fig, axs = plt.subplots(feature_num, 1, figsize=(10, 8))
lines_feature = [ax.plot([0] * window_size)[0] for ax in axs]
for ax in axs:
    ax.set_ylim(0, 80)  # Adjust RMS y-limits as needed


def get_emg_data_from_queue(q):
    data = []
    while not q.empty():
        data.append(q.get())
    return data

def update_feature(frame):
    for i, line in enumerate(lines_feature):
        new_data = get_emg_data_from_queue(feature_queues[i])
        if new_data:
            print(f"Updating feature plot for channel {i} with data: {new_data[-1:]}")  # Last 5 data points for checking
        else:
            print(f"No new feature data for channel {i}")
        
        current_data = line.get_ydata()
        updated_data = list(current_data[len(new_data):]) + new_data
        line.set_ydata(updated_data)
        
    return lines_feature

def update_feature_queues(features:list):
    for i in range(len(features)):
        if not feature_queues[i].full():
            feature_queues[i].put(features[i])
        else:
            feature_queues[i].get()
            feature_queues[i].put(features[i])


if __name__ == '__main__':
    # init parameter
    sdkpath = 'C:\\Users\\zcha621\\Documents\\PhD\Myo\\PythonProject\\myo-sdk-win-0.9.0\\'
    address = "tcp://127.0.0.1:5689"
    csv_filename = "zhuang" + "_"+ datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    # + datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')

    csvfirstrow = ['C1','C2','C3','C4','C5','C6','C7','C8','Marker']
    listener = Listener(sdkpath, address)
    
    # # csv handler
    csvHandler = CSVHandler(csv_filename)
    csvHandler.write_first_row(csvfirstrow)
    listener.register_observer(csvHandler.write_row)
    
    
    
    fatigue = OnlineFatigue(fs=200, num_channel=8,window_size=5,feature_window_size=3,step=3)
    # listener.register_observer(fatigue.fatigue_indicator)
    listener.register_observer(fatigue.cal_fatigue_features)
    # csv handler for feature, store the detected feature
    feature_csv_filename = csv_filename+"_feature"
    feature_csvHandler = CSVHandler(feature_csv_filename)
    feature_csvfirstrow = ["RMS", "Median_Freq"]
    feature_csvHandler.write_first_row(feature_csvfirstrow)
    fatigue.register_observer(feature_csvHandler.write_row)


    # plot 
    fatigue.register_observer(update_feature_queues)

    
    # start fetching the emg data
    thread = threading.Thread(target=listener.fetch_emg)
    thread.start()
    print("t")
    # Animation
    # time.sleep(3)

    ani = animation.FuncAnimation(fig, update_feature, interval=1000, blit=True)
    plt.show()
