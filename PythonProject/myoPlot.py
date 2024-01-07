import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import random  # Only for generating dummy data
import myo
import time
import threading
import queue
import numpy as np
from Zmq_Router import ZmqRouter
import csv

class Listener(myo.DeviceListener):
    def __init__(self, address, filename):
        super().__init__()
        self.zmqRouter = ZmqRouter(address)
         # Optional: write a header row
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
            emg = event.emg
        except AttributeError:
            pass
        else:
            for i in range(num_channels):
                if not emg_data_queues[i].full():
                    emg_data_queues[i].put(emg[i])
                else:
                    emg_data_queues[i].get()
                    emg_data_queues[i].put(emg[i])

            # Compute RMS and update RMS queue
                # Check if enough data for RMS

                if emg_data_queues[i].qsize() >= rms_window:
                    rms = compute_rms(list(emg_data_queues[i].queue)[-rms_window:])
                    print(f"Computed RMS for channel {i}: {rms}")  # Debugging line
                    if not rms_data_queues[i].full():
                        rms_data_queues[i].put(rms)
                    else:
                        rms_data_queues[i].get()
                        rms_data_queues[i].put(rms)
                else:
                    print(f"Not enough data for RMS calculation for channel {i}. Data points available: {emg_data_queues[i].qsize()}")
            
            # print(marker)
            # print(emg)


    def on_connected(self, event):
        print("connected!")
    def on_disconnected(self, event):
        print("Disconnected!")
    

def FetchEmg():
    myo.init(sdk_path='C:\\Users\\zcha621\\Documents\\PhD\Myo\\PythonProject\\myo-sdk-win-0.9.0\\')
    hub = myo.Hub()
    listener = Listener("tcp://127.0.0.1:5689","output")
    while hub.run(listener.on_event,10000):
        pass


    # Sampling rate and desired window size for the plot
sampling_rate = 200  # 200 Hz
window_size = 5  # window size in seconds
num_channels = 8
rms_window = 50  # Number of samples over which to compute RMS
maxlen = sampling_rate * window_size


emg_data_queues = [queue.Queue(maxsize=maxlen) for _ in range(num_channels)]
rms_data_queues = [queue.Queue(maxsize=maxlen) for _ in range(num_channels)]
# Create the figure and axis for plotting
fig, axs = plt.subplots(num_channels, 1, figsize=(12, 10))
# Lines for each channel
lines = [ax.plot([0] * maxlen)[0] for ax in axs]
for ax in axs:
    ax.set_ylim(-180, 180)  # Adjust as per your EMG data's range


def update(frame):
    for i, line in enumerate(lines):
        new_data = get_emg_data_from_queue(emg_data_queues[i])
        current_data = line.get_ydata()
        updated_data = list(current_data[len(new_data):]) + new_data
        line.set_ydata(updated_data)
    return lines
    
def get_emg_data_from_queue(q):
    data = []
    while not q.empty():
        data.append(q.get())
    return data


fig_rms, axs_rms = plt.subplots(num_channels, 1, figsize=(10, 8))
lines_rms = [ax.plot([0] * maxlen)[0] for ax in axs_rms]
for ax in axs_rms:
    ax.set_ylim(0, 80)  # Adjust RMS y-limits as needed


def compute_rms(data):
    return np.sqrt(np.mean(np.square(data)))
# def update_rms(frame):
#     for i, line in enumerate(lines_rms):
#         new_data = get_emg_data_from_queue(rms_data_queues[i])
#         current_data = line.get_ydata()
#         updated_data = list(current_data[len(new_data):]) + new_data
#         line.set_ydata(updated_data)
#     return lines_rms

def update_rms(frame):
    for i, line in enumerate(lines_rms):
        new_data = get_emg_data_from_queue(rms_data_queues[i])
        if new_data:
            print(f"Updating RMS plot for channel {i} with data: {new_data[-5:]}")  # Last 5 data points for checking
        else:
            print(f"No new RMS data for channel {i}")
        
        current_data = line.get_ydata()
        updated_data = list(current_data[len(new_data):]) + new_data
        line.set_ydata(updated_data)
        
    return lines_rms



if __name__ == '__main__':

    # myo.init(sdk_path='.\\myo-sdk-win-0.9.0\\')
    # thread = threading.Thread(target=plotSignal, args=(emg))
    thread = threading.Thread(target=FetchEmg)
    thread.start()
    # Animation
    time.sleep(3)
    ani = animation.FuncAnimation(fig, update, interval=1000 / sampling_rate, blit=True)

    # Animation for RMS
    ani_rms = animation.FuncAnimation(fig_rms, update_rms, interval=1000 / sampling_rate, blit=True)

    plt.tight_layout()
    plt.show()


    